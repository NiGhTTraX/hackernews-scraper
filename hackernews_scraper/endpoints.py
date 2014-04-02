import requests


class AlgoliaEndpoint(object):
    """Class used to call the Algolia API and parse the response."""

    DEFAULT_TIMEOUT = 30
    URL = "http://hn.algolia.com/api/v1/search_by_date"

    @staticmethod
    def get(tag, since, until, page, timeout):
        """Send a GET request to the endpoint.

        Since Algolia only returns JSON, parse it into a dict.

        See http://hn.algolia.com/api for more details.

        Params:
          tag: Can be "story" or "comment".
          since: timestamp representing how old the news should be.
          until: timestamp representing how new the news should be.
          page: The number of the page to be fetched.
          timeout: socket timeout needed to prevent socket operations
                   from hanging; None switches to a default timeout

        Returns:
          A python dict representing the response.

        Raises:
          requests.exceptions.RequestException.
        """
        if timeout is None:
            timeout = AlgoliaEndpoint.DEFAULT_TIMEOUT

        numericFilters = ["created_at_i>%d" % since]
        if until is not None:
            numericFilters.append("created_at_i<%d" % until)

        params = {
            "numericFilters": ",".join(numericFilters),
            "tags": tag,
            "page": page
        }

        url = AlgoliaEndpoint.URL
        url += "?" + "&".join(["%s=%s" % (k, v) for k, v in params.iteritems()])
        response = requests.get(url, timeout=timeout)

        return response.json()
