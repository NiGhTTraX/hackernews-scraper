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

    nbPages = 0

    hits = [ItemFactory(), ItemFactory()]
    nbHits = factory.LazyAttribute(lambda x: x.nbPages * len(x.hits))
    hitsPerPage = factory.LazyAttribute(lambda x: len(x.hits))


class BaseTest(unittest.TestCase):
    def _createPages(self, pages=1, hits=None):
        resp = [
            httpretty.Response(body=json.dumps(
                ResponseFactory(pages=pages, hits=hits)
            ))
        ] * pages

        lastPage = ResponseFactory()
        lastPage["nbHits"] = 0
        lastPage["hits"] = []

        resp.append(httpretty.Response(body=json.dumps(lastPage)))

        return resp
