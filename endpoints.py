#!/usr/bin/env python
"""
hacker-news endpoints
"""

from requests import Request, Session
import urllib


class Endpoint(object):
  """Base class for defining an API endpoint."""

  def __init__(self, url):
    self.url = url

  def get(self, params):
    """Send a GET request to the endpoint.

    Returns:
      A Request response object.

    Raises:
      requests.exceptions.RequestException.
    """
    request = Request("GET", self.url)
    prepared = request.prepare()

    # Manually prepare the params so we can work around escaping.
    p = urllib.urlencode(params)
    p = p.replace("%3C", "<")
    prepared.url += "?" + p

    session = Session()
    return session.send(prepared)

  def post(self, params):
    pass


class JSONEndpoint(Endpoint):
  """Basic JSON endpoint."""

  def __init__(self, url):
    Endpoint.__init__(self, url)

  def get(self, params):
    """Call the endpoint and return a dict from the parsed JSON.

    Args:
      params: A dict containing parameters that will be sent to the endpoint.

    Returns:
      A dict containing the parsed response.

      If the endpoint returns invalid JSON, this will return None.
    """
    response = Endpoint.get(self, params)

    try:
      return response.json()
    except ValueError:
      return None

