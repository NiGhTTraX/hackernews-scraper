import requests


class AlgoliaEndpoint(object):
  """Class used to call the Algolia API and parse the response."""

  URL = "http://hn.algolia.com/api/v1/search_by_date"

  @staticmethod
  def get(tag, since, until=None, page=0):
    """Send a GET request to the endpoint.

    Since Algolia only returns JSON, parse it into a dict.

    Params:
      tag: Can be "story" or "comment".
      since: timestamp representing how old the news should be.

    Optional params:
      until: timestamp representing how new the news should be.
      page: The number of the page to get.

    Returns:
      A python dict representing the response.

    Raises:
      requests.exceptions.RequestException.
    """

    numericFilters = ["created_at_i<%d" % since]
    if until is not None:
      numericFilters += ["created_at_i>%d" % until]

    params = {
        "numericFilters": ",".join(numericFilters),
        "tags": tag,
        "page": page
    }

    url = AlgoliaEndpoint.URL
    url += "?" + "&".join(["%s=%s" for k,v in params.items()])
    response = requests.get(url)

    return response.json()

