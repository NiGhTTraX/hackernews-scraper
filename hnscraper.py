#!/usr/bin/env python
"""
hacker-news story and comment scraper.
"""

from endpoints import JSONEndpoint


class TooManyItemsException(Exception):
  """Exception for when we reach the story fetch limit."""

  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)


class Scraper(object):
  """Generic hacker news scraper."""

  URL = "http://hn.algolia.com/api/v1/search_by_date"
  FETCH_LIMIT = 50 * 20

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
        r[translated_field] = hit[original_field]
      hits.append(r)

    return hits

  def scrape(self, params, fields=None, endpoint=None):
    """Call the endpoint and get the results.

    Params:
      params: Parameters to send to the endpoint.

    Optional params:
      fields: Field translations.
      endpoint: Endpoint to use. Defaults to JSONEndpoint.

    Yields:
      One page of results. This is a list of dicts.

    Raises:
      TooManyItemsException if there's more than FETCH_LIMIT stories.
    """

    if endpoint is None:
      endpoint = JSONEndpoint(Scraper.URL)

    params["page"] = 0

    r = endpoint.get(params)
    yield self.__translate_fields(r, fields)

    # Let's see if there are any more pages.
    try:
      pages = int(r["nbPages"])
    except ValueError:
      pages = 0

    params["page"] += 1
    while params["page"] < pages:
      r = endpoint.get(params)
      yield self.__translate_fields(r, fields)

      params["page"] += 1

    # Check to see if there are more stories that we can fetch.
    if r["nbHits"] > self.FETCH_LIMIT:
      raise TooManyItemsException("More than 50 pages of items")


class StoryScraper(object):
  """hacker news story scraper."""

  @staticmethod
  def getStories(since, until=None, endpoint = None):
    """Scrape stories. The stories are sorted descending by created date.

    Params:
      since: timestamp representing how old the news should be.

    Optional params:
      until: timestamp representing how new the news should be.
      endpoint: endpoint to use. Defaults to JSONEndpoint.

    Yields:
      One page of stories. This is a list of dicts.

    Excepts:
      TooManyItemsException.
    """

    numericFilters = ["created_at_i<%d" % since]
    if until is not None:
      numericFilters += ["created_at_i>%d" % until]

    params = {
        "numericFilters": ",".join(numericFilters),
        "tags": "story"
    }

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

    s = Scraper()
    return s.scrape(params=params, fields=fields, endpoint=endpoint)

