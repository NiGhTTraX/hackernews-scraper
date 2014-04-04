import httpretty
from mock import patch

from hackernews_scraper.endpoints import AlgoliaEndpoint
from hackernews_scraper.hnscraper import Scraper, StoryScraper
from .factories import StoryFactory
from .utils import BaseTest


class TestStoryScraper(BaseTest):
    SCRAPER_SCRAPE_PATH = "hackernews_scraper.hnscraper.Scraper.scrape"

    @httpretty.activate
    def test_correct_tag(self):
        with patch(self.SCRAPER_SCRAPE_PATH) as scraper_scrape_mock:
            httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(hits=[]),
                               content_type="application/json")

            list(StoryScraper().getStories(since=42))
            self.assertEquals(scraper_scrape_mock.call_args[0][0], "story",
                              "Correct tag was used")

    @httpretty.activate
    def test_get_stories(self):
        hits = [StoryFactory(), StoryFactory()]

        httpretty.register_uri(httpretty.GET, AlgoliaEndpoint.URL,
                               responses=self._createPages(hits=hits),
                               content_type="application/json")

        resp = list(StoryScraper().getStories(since=42))
        expected = Scraper._translateFields({"hits": hits},
                StoryScraper.FIELDS)
        self.assertListEqual(resp, expected)

