import httpretty
from mock import patch

from hackernews_scraper.endpoints import AlgoliaEndpoint
from hackernews_scraper.hnscraper import Scraper, CommentScraper
from .utils import BaseTest, CommentFactory


class TestCommentScraper(BaseTest):
    ENDPOINT_GET_PATH = "hackernews_scraper.hnscraper.Scraper.scrape"

    @httpretty.activate
    def test_correct_tag(self):
        with patch(self.ENDPOINT_GET_PATH) as endpoint_get_mock:
            httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                                   responses=self._createPages(hits=[]),
                                   content_type="application/json")

            list(CommentScraper().getComments(since=42))
            self.assertEquals(endpoint_get_mock.call_args[0][0], "comment",
                              "Correct tag was used")

    @httpretty.activate
    def test_get_comments(self):
        hits = [CommentFactory(), CommentFactory()]

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(hits=hits),
                               content_type="application/json")

        resp = list(CommentScraper().getComments(since=42))
        expected = Scraper._translateFields({"hits": hits},
                CommentScraper.FIELDS)
        self.assertListEqual(resp, expected)

