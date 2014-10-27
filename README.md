hackernews-scraper
==================

Scrape [hacker news](https://news.ycombinator.com) comments and posts
using the [Algolia API](http://hn.algolia.com/api/).


Usage
=====

```python
from hackernews_scraper import CommentScraper

CommentScraper.getComments(since=1394039447)
```

The above will return a generator that will yield one comment at a time.
It will keep on going until there are no more comments to fetch, or until
it reaches the 50 pages limit set by hacker news. In the latter case, a
`TooManyItemsException` will be raised.

If the hacker news API response is missing any required fields, the scraper
will raise `KeyError`.


Response format
===============

Comments:
```
{
 'author': u'dhmholley',
 'comment_id': u'7531026',
 'comment_text': u'Are people still blowing this whistle?...',
 'created_at': u'2014-04-04T12:57:38.000Z',
 'parent_id': 7530853,
 'points': 1,
 'story_id': None,
 'story_title': None,
 'story_url': None,
 'timestamp': 1396616258,
 'title': None,
 'url': None
}
```

Stories:
```
{
 'author': u'sethco',
 'created_at': u'2014-04-04T12:56:23.000Z',
 'objectID': None,
 'points': 1,
 'story_text': 1,
 'timestamp': 1396616183,
 'title': u'Opower IPO today',
 'url': u'http://www.businesswire.com/news/home/20140403006541/en#.Uz4cbq1dVih'
}
```

Testing
=======

You need to have [httpretty](https://github.com/gabrielfalcao/HTTPretty)
and [factory-boy](https://github.com/rbarrois/factory_boy) installed.

Run `nosetests` in the root folder or the `tests` folder.
