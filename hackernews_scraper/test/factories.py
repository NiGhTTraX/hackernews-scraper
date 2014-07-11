import factory


class ItemFactory(factory.Factory):
    FACTORY_FOR = dict

    objectID = 21
    created_at_i = 42
    title = "Test item"


class CommentFactory(factory.Factory):
    FACTORY_FOR = dict

    created_at = "2014-04-03T10:17:28.000Z"
    title = "Test comment"
    url = "www.google.com"
    comment_text = "Fuzzy wuzzy was a bear"
    story_id = 42
    story_title = "Bear kills man"
    story_url = "www.bing.com"
    author = "yourmom"
    points = 42
    created_at_i = 42
    objectID = 42
    parent_id = 42


class StoryFactory(factory.Factory):
    FACTORY_FOR = dict

    created_at = "2014-04-03T10:17:28.000Z"
    created_at_i = 42
    title = "Test story"
    url = "www.google.com"
    author = "yourdad"
    points = 42
    story_text = "Fuzzy wuzzy had no hair"
    story_id = 42


class ResponseFactory(factory.Factory):
    FACTORY_FOR = dict

    nbPages = 1
    hits = [ItemFactory(), ItemFactory()]
    nbHits = factory.LazyAttribute(lambda x: x.nbPages * len(x.hits))
    hitsPerPage = factory.LazyAttribute(lambda x: len(x.hits))

