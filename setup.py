from setuptools import setup, find_packages

from hackernews_scraper import __version__

setup(name='hackernews_scraper',
      description='Python library for retrieving comments and stories from HackerNews',
      packages=find_packages(),
      version=__version__)
