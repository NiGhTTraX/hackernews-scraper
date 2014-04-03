import factory
import unittest
import httpretty
import json


class ItemFactory(factory.Factory):
    FACTORY_FOR = dict

    objectID = 21
    created_at_i = 42
    title = "Test item"


class ResponseFactory(factory.Factory):
    FACTORY_FOR = dict

    nbPages = 1
    hits = [ItemFactory(), ItemFactory()]
    nbHits = factory.LazyAttribute(lambda x: x.nbPages * len(x.hits))
    hitsPerPage = factory.LazyAttribute(lambda x: len(x.hits))


class BaseTest(unittest.TestCase):
    def _createPages(self, pages=1, hits=None):
        if hits is None:
          hits = []

        page = ResponseFactory(nbPages=pages, hits=hits)
        resp = [httpretty.Response(body=json.dumps(page))] * pages

        # Last page will have an empty `hits` field, but will have the correct
        # `nbHits`, which is supposed to be just like the previous pages
        lastPage = ResponseFactory(
            hits=[], nbPages=pages,
            hitsPerPage=page["hitsPerPage"], nbHits=page["nbHits"])
        resp.append(httpretty.Response(body=json.dumps(lastPage)))

        return resp
