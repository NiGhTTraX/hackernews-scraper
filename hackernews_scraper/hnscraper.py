from endpoints import AlgoliaEndpoint


class TooManyItemsException(Exception):
    """Exception for when we reach the story fetch limit."""
    pass


class Scraper(object):
    """Generic hacker news scraper."""

    @staticmethod
    def scrape(tag, since, until=None, fields=None, timeout=None):
        """Call the Algolia endpoint and get the results.

        Example:
          Scraper.scrape("story", 1394901958) will return all story items since
          15 Mar 2014 16:45:58 GMT.

        Params:
          tag: Can be "story" or "comment".
          since: timestamp representing how old the items should be.

        Optional params:
          until: timestamp representing how new the items should be.
          fields: Field translations. This is a dict in the form
          { translated_field: original_field }. Only the fields specified in
          this dict will be contained in the response. If this is None, the
          exact API response will be returned.
          timeout: socket timeout

        Yields:
          One item. This is a dict. You can specify which fields will be returned
          using the optional fields param.

        Raises:
          TooManyItemsException if there's more items than the endpoint can let
          us fetch.
        """

        page = 0

        while True:
            hits = Scraper._getPage(tag, since, until, page, fields, timeout)

            # Was this the last page?
            if hits is None:
                break

            for hit in hits:
                yield hit

            page += 1

    @staticmethod
    def _getPage(tag, since, until, page, fields, timeout):
        """Fetch a single page of items and translate the fields.

        Returns:
          A list of items, each being a dict. If this was the last page, or we've
          reached the fetch limit, return None.
        """

        resp = AlgoliaEndpoint.get(tag, since, until, page, timeout)
        hits = Scraper._translateFields(resp, fields)

        if not hits:
            # This might be the last page, or there might be more pages than we
            # can fetch.
            if resp["nbHits"] > resp["nbPages"] * resp["hitsPerPage"]:
                raise TooManyItemsException("More than 50 pages of items")

            return None

        return hits

    @staticmethod
    def _translateFields(response, fields=None):
        """Translate fields of returned objects.

        Params:
          response: Dict containing all the hits.

        Optional params:
          fields: A dictionary representing the field translations. Should be in
          the form: translated_field: original_field. If not provided, just
          return the untouched hits.
        """

        if fields is None:
            return response["hits"]

        hits = []
        for hit in response["hits"]:
            item = {}
            for translated_field, original_field in fields.iteritems():
                try:
                    item[translated_field] = hit[original_field]
                except KeyError:
                    pass

            hits.append(item)

        return hits


class StoryScraper(object):
    """hacker news story scraper.

    Example:
        StoryScraper.getStories("story", 1394901958) will return all
        stories since 15 Mar 2014 16:45:58 GMT.
    """

    FIELDS = {
        "created_at": "created_at",
        "title": "title",
        "url": "url",
        "author": "author",
        "points": "points",
        "story_text": "points",
        "timestamp": "created_at_i",
        "objectID": "story_id"
    }

    @staticmethod
    def getStories(since, until=None, timeout=None):
        """Scrape stories between 2 timestamps.

        Params:
          since: timestamp representing how old the news should be.

        Optional params:
          until: timestamp representing how new the news should be.
          timeout: socket timeout; None switches to a default value

        Yields:
          One story. This is a dict.

        Excepts:
          TooManyItemsException.
        """

        return Scraper().scrape("story", since, until=until,
                                fields=StoryScraper.FIELDS, timeout=timeout)


class CommentScraper(object):
    """hacker news comment scraper.

    Example:
        CommentScraper.getComments("comment", 1394901958) will return all
        comments since 15 Mar 2014 16:45:58 GMT.
    """

    FIELDS = {
        "created_at": "created_at",
        "title": "title",
        "url": "url",
        "comment_text": "comment_text",
        "story_id": "story_id",
        "story_title": "story_title",
        "story_url": "story_url",
        "author": "author",
        "points": "points",
        "timestamp": "created_at_i",
        "comment_id": "objectID",
        "parent_id": "parent_id",
    }

    @staticmethod
    def getComments(since, until=None, timeout=None):
        """Scrape comments between 2 timestamps.

        Params:
          since: timestamp representing how old the comments should be.

        Optional params:
          until: timestamp representing how new the coments should be.
          timeout: socket timeout; None switches to a default value

        Yields:
          One comment. This is a dict.

        Excepts:
          TooManyItemsException.
        """

        return Scraper().scrape("comment", since, until=until,
                                fields=CommentScraper.FIELDS, timeout=timeout)

