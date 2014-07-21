from datetime import datetime, timedelta
import factory
from factory.fuzzy import FuzzyText, FuzzyInteger
import time


class ItemFactory(factory.Factory):
    FACTORY_FOR = dict

    objectID = 21
    created_at_i = 42
    title = "Test item"


class CommentFactory(factory.Factory):
    FACTORY_FOR = dict

    @factory.sequence
    def created_at(n):
        return (datetime.now() - timedelta(minutes=n)).isoformat()

    @factory.sequence
    def created_at_i(n):
        return int(time.time()) - n

    title = FuzzyText(length=20)
    url = "www.google.com"
    comment_text = FuzzyText(length=300)
    story_id = 42
    story_title = FuzzyText(length=20)
    story_url = "www.bing.com"
    author = FuzzyText(length=10)
    points = FuzzyInteger(100)
    objectID = FuzzyInteger(100)
    parent_id = FuzzyInteger(100)


class StoryFactory(factory.Factory):
    FACTORY_FOR = dict

    @factory.sequence
    def created_at(n):
        return (datetime.now() - timedelta(minutes=n)).isoformat()

    @factory.sequence
    def created_at_i(n):
        return int(time.time()) - n

    title = FuzzyText(length=20)
    url = "www.google.com"
    author = FuzzyText(length=10)
    points = FuzzyInteger(100)
    story_text = FuzzyText(length=300)
    story_id = FuzzyInteger(100)


class ResponseFactory(factory.Factory):
    FACTORY_FOR = dict

    nbPages = 1
    hits = [ItemFactory(), ItemFactory()]
    nbHits = factory.LazyAttribute(lambda x: x.nbPages * len(x.hits))
    hitsPerPage = factory.LazyAttribute(lambda x: len(x.hits))
