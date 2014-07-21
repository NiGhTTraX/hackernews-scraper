import httpretty
from mock import patch

from hackernews_scraper.endpoints import AlgoliaEndpoint
from hackernews_scraper.hnscraper import Scraper, CommentScraper
from .factories import CommentFactory
from .basetestcase import BaseTestCase


class TestCommentScraper(BaseTestCase):
    SCRAPER_SCRAPE_PATH = "hackernews_scraper.hnscraper.Scraper.scrape"

    @httpretty.activate
    def test_correct_tag(self):
        with patch(self.SCRAPER_SCRAPE_PATH) as scraper_scrape_mock:
            httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                                   responses=self._createPages(hits=[]),
                                   content_type="application/json")

            list(CommentScraper().getComments(since=42))
            self.assertEquals(scraper_scrape_mock.call_args[0][0], "comment",
                              "Correct tag was used")

    @httpretty.activate
    def test_get_comments(self):
        hits = [CommentFactory(created_at_i=42) for _ in range(2)]

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(hits=hits),
                               content_type="application/json")

        resp = list(CommentScraper().getComments(since=42))
        expected = Scraper._translateFields({"hits": hits},
                CommentScraper.FIELDS)
        self.assertListEqual(resp, expected)

