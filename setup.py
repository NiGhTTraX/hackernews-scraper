from setuptools import setup, find_packages

from hackernews_scraper import __version__

setup(name='hackernews_scraper',
      description='Python library for retrieving comments and stories from HackerNews',
      packages=find_packages(),
      version=__version__,
      install_requires=['requests'],
      url='https://github.com/NiGhTTraX/hackernews-scraper',
      license='MIT',
      platforms='any',
      tests_require=['nose', 'factory_boy', 'httpretty'],
      )
