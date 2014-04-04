import httpretty
import json
from mock import patch

from hackernews_scraper.endpoints import AlgoliaEndpoint
from hackernews_scraper.hnscraper import Scraper, TooManyItemsException
from .factories import ItemFactory, ResponseFactory
from .basetestcase import BaseTestCase


class TestScraper(BaseTestCase):
    SOCK_SET_TIMEOUT_PATH = "httpretty.core.fakesock.socket.settimeout"

    @httpretty.activate
    def test_scrape(self):
        hits = [ItemFactory(), ItemFactory()]

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(hits=hits),
                               content_type="application/json")

        resp = list(Scraper().scrape(tag="test", since=42))
        self.assertListEqual(hits, resp)

    @httpretty.activate
    def test_timeout(self):
        with patch(self.SOCK_SET_TIMEOUT_PATH) as set_timeout_mock:
            # The contents of the response and arguments of the method call
            # are irrelevant, the focus is setting the socket timeout
            httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(hits=[]),
                               content_type="application/json")
            timeout = 10
            # Force results retrieval (method is a generator)
            list(Scraper.scrape("comments", 0, 1, 0, timeout))

            self.assertEquals(set_timeout_mock.call_args[0][0], timeout,
                              "Timeout has not been set")

    @httpretty.activate
    def test_scrape_generator(self):
        hits = [ItemFactory(), ItemFactory()]

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(pages=2, hits=hits),
                               content_type="application/json")

        gen = Scraper().scrape(tag="test", since=42)
        resp = gen.next()
        self.assertEqual(resp, hits[0])
        resp = gen.next()
        self.assertEqual(resp, hits[1])

    def test_translate_fields(self):
        dummy_object = {
            "first_field": 42,
            "second_field": 21
        }
        fields = {
            "changed1": "first_field",
            "changed2": "second_field"
        }
        expected = {
            "changed1": 42,
            "changed2": 21
        }
        translated_object = Scraper._translateFields({"hits": [dummy_object]},
            fields=fields)[0]
        self.assertDictEqual(translated_object, expected)

    def test_translate_fields_multiple_objects(self):
        NR_OBJECTS = 2

        dummy_object = {
            "first_field": 42,
            "second_field": 21
        }
        fields = {
            "changed1": "first_field",
            "changed2": "second_field"
        }
        expected = [{
            "changed1": 42,
            "changed2": 21
        }] * NR_OBJECTS
        translated_objects = Scraper._translateFields(
                {"hits": [dummy_object] * NR_OBJECTS}, fields=fields)
        self.assertItemsEqual(translated_objects, expected)

    def test_translate_missing_field(self):
        dummy_object = {
            "first_field": 42,
            "second_field": 21
        }
        fields = {
            "expected_field": "missing_field"
        }

        with self.assertRaises(KeyError):
            Scraper._translateFields({"hits": [dummy_object]}, fields=fields)

    def test_translate_missing_field_multiple_objects(self):
        dummy_object = {
            "valid_field": 42,
            "missing_field": 21
        }
        dummy_object_with_missing_field = {
            "valid_field": 42
        }
        fields = {
            "expected_field": "missing_field"
        }

        with self.assertRaises(KeyError):
            Scraper._translateFields(
                    {"hits": [dummy_object, dummy_object_with_missing_field]},
                    fields=fields)

    def test_translate_fields_no_fields(self):
        dummy_object = {
            "first_field": 42,
            "second_field": 21
        }
        translated_object = Scraper._translateFields({"hits": [dummy_object]},
            fields=None)[0]
        self.assertDictEqual(translated_object, dummy_object)

    @httpretty.activate
    def test_scrape_all_fields_are_returned(self):
        item = ItemFactory()

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(hits=[item]),
                               content_type="application/json")

        resp = list(Scraper().scrape(tag="test", since=42))
        self.assertItemsEqual(resp[0].keys(),
            ["objectID", "created_at_i", "title"])

    @httpretty.activate
    def test_scrape_translate_fields(self):
        item = ItemFactory()

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(hits=[item]),
                               content_type="application/json")

        fields = {
            "test": "created_at_i"
        }

        resp = list(Scraper().scrape(tag="test", since=42, fields=fields))
        self.assertItemsEqual(resp[0].keys(), ["test"])

    @httpretty.activate
    def test_scrape_multiple_pages(self):
        PAGES = 2

        hits = [ItemFactory(), ItemFactory()]

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(PAGES, hits),
                               content_type="application/json")

        resp = list(Scraper().scrape(tag="test", since=42))
        self.assertListEqual(hits * PAGES, resp)

    @httpretty.activate
    def test_scrape_page_limit(self):
        hits = [ItemFactory(), ItemFactory()]
        pages = [httpretty.Response(body=json.dumps(
                ResponseFactory(hits=hits)
            ))
        ]

        lastPage = ResponseFactory()
        # Trick the scraper in thinking it reached the last page but there are more
        # items available.
        lastPage["nbHits"] = 3
        lastPage["hits"] = []  # this needs to be empty

        pages.append(httpretty.Response(body=json.dumps(lastPage)))

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=pages,
                               content_type="application/json")

        with self.assertRaises(TooManyItemsException):
            list(Scraper().scrape(tag="test", since=42))

    @httpretty.activate
    def test_scrape_no_items(self):
        lastPage = ResponseFactory()
        lastPage["nbHits"] = 0
        lastPage["hits"] = []

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               body=json.dumps(lastPage),
                               content_type="application/json")

        resp = list(Scraper().scrape(tag="test", since=42))
        self.assertListEqual(resp, [])

    @httpretty.activate
    def test_scrape_correct_request(self):
        item = ItemFactory()

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(pages=2, hits=[item]),
                               content_type="application/json")

        gen = Scraper().scrape(tag="test", since=42, until=43)

        gen.next()
        self.assertDictEqual(httpretty.last_request().querystring,
            {
              "numericFilters": ["created_at_i>42,created_at_i<43"],
              "tags": ["test"],
              "page": ["0"]
            }
        )

        gen.next()
        self.assertDictEqual(httpretty.last_request().querystring,
            {
              "numericFilters": ["created_at_i>42,created_at_i<43"],
              "tags": ["test"],
              "page": ["1"]
            }
        )

