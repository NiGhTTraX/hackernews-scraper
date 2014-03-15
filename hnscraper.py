from endpoints import AlgoliaEndpoint


class TooManyItemsException(Exception):
  """Exception for when we reach the story fetch limit."""
  pass


class Scraper(object):
  """Generic hacker news scraper."""

  @staticmethod
  def scrape(tag, since, until=None, fields=None):
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
      { translated_field: original_field }. Only the fields specified in this
      dict will be contained in the response.

    Yields:
      One item. This is a dict. You can specify which fields will be returned
      using the optional fields param.

    Raises:
      TooManyItemsException if there's more items than the endpoint can let us
      fetch.
    """

    page = 0

    while True:
      hits = Scraper._getPage(tag, since, until, page, fields)

      # Was this the last page?
      if hits is None:
        break

      for hit in hits:
        yield hit

      page += 1

  @staticmethod
  def _getPage(tag, since, until, page, fields):
    """Fetch a single plage of items and translate the fields.

    Returns:
      A list of items, each being a dict. If this was the last page, or we've
      reached the fetch limit, return None.
    """
    resp = AlgoliaEndpoint.get(tag, since, until, page)
    hits = Scraper._translateFields(resp, fields)

    if not hits:
      # This might be the last page, or there might be more pages than we can
      # fetch.
      if resp["nbHits"] > resp["nbPages"] * resp["hitsPerPage"]:
        raise TooManyItemsException("More than 50 pages of items")

      return None

    return hits

  @staticmethod
  def _translateFields(response, fields=None):
    """Translate fields of returned objects.

    Params:
      response: Dict containing all the hits.
      fields: A dictionary representing the field translations. Should be in the
      form: translated_field: original_field. If not provided, just returned the
      whole objects.
    """

    if fields is None:
      return response["hits"]

    hits = []
    for hit in response["hits"]:
      r = {}
      for translated_field, original_field in fields.iteritems():
        try:
          r[translated_field] = hit[original_field]
        except KeyError:
          pass

      hits.append(r)

    return hits


class StoryScraper(object):
  """hacker news story scraper.

  Example:
      Story.Scraper.scrape("story", 1394901958) will return all stories since
      15 Mar 2014 16:45:58 GMT.
  """

  @staticmethod
  def getStories(since, until=None):
    """Scrape stories between 2 timestamps.

    Params:
      since: timestamp representing how old the news should be.

    Optional params:
      until: timestamp representing how new the news should be.

    Yields:
      One story. This is a dict.

    Excepts:
      TooManyItemsException.
    """

    fields = {
        "created_at": "created_at",
        "title": "title",
        "url": "url",
        "author": "author",
        "points": "points",
        "story_text": "points",
        "timestamp": "created_at_i",
        "story_id": "objectID"
    }

    return Scraper().scrape("story", since, until, fields)

