from endpoints import AlgoliaEndpoint


class TooManyItemsException(Exception):
  """Exception for when we reach the story fetch limit."""
  pass


class Scraper(object):
  """Generic hacker news scraper."""

  FETCH_LIMIT = 50 * 20

  def __init__(self, endpoint=None):
    if endpoint is None:
      endpoint = AlgoliaEndpoint()

    self.endpoint = endpoint

  def __translate_fields(self, response, fields=None):
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

  def scrape(self, tag, since, until=None, fields=None):
    """Call the endpoint and get the results.

    Params:
      tag: Can be "story" or "comment".
      since: timestamp representing how old the items should be.

    Optional params:
      until: timestamp representing how new the items should be.
      fields: Field translations.

    Yields:
      One item. This is a dict.

    Raises:
      TooManyItemsException if there's more than FETCH_LIMIT items.
    """

    r = self.endpoint.get(tag, since, until)
    hits = self.__translate_fields(r, fields)
    for hit in hits:
      yield hit

    # Let's see if there are any more pages.
    try:
      pages = int(r["nbPages"])
    except ValueError:
      pages = 0

    page = 1
    while page < pages:
      r = self.endpoint.get(tag, since, until, page)
      hits = self.__translate_fields(r, fields)
      for hit in hits:
        yield hit

      page += 1

    # Check to see if there are more stories that we can fetch.
    if r["nbHits"] > self.FETCH_LIMIT:
      raise TooManyItemsException("More than 50 pages of items")


class StoryScraper(object):
  """hacker news story scraper."""

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

