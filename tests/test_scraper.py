import unittest
import httpretty
import factory
import json

from endpoints import AlgoliaEndpoint
from hnscraper import Scraper, TooManyItemsException


class ItemFactory(factory.Factory):
  FACTORY_FOR = dict
  objectID = 21
  created_at_i = 42
  title = "Test item"


class ResponseFactory(factory.Factory):
  FACTORY_FOR = dict

  nbPages = 0

  hits = [ItemFactory(), ItemFactory()]
  nbHits = factory.LazyAttribute(lambda x: x.nbPages * len(x.hits))
  hitsPerPage = factory.LazyAttribute(lambda x: len(x.hits))


class TestScraper(unittest.TestCase):

  @httpretty.activate
  def test_scrape(self):
    hits = [ItemFactory(), ItemFactory()]

    httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                           responses=self._createPages(hits=hits),
                           content_type="application/json")

    resp = list(Scraper().scrape(tag="test", since=42))
    self.assertListEqual(hits, resp)

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
    pages= [httpretty.Response(body=json.dumps(
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
      resp = list(Scraper().scrape(tag="test", since=42))

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

  def _createPages(self, pages=1, hits=None):
    resp = [
        httpretty.Response(body=json.dumps(
            ResponseFactory(pages=pages, hits=hits)
        ))
    ] * pages

    lastPage = ResponseFactory()
    lastPage["nbHits"] = 0
    lastPage["hits"] = []

    resp.append(httpretty.Response(body=json.dumps(lastPage)))

    return resp

