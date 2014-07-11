from setuptools import setup, find_packages

setup(name='hackernews_scraper',
      description='Python library for retrieving comments and stories from HackerNews',
      packages=find_packages(),
      version="1.0.1",
      install_requires=['requests'],
      url='https://github.com/NiGhTTraX/hackernews-scraper',
      license='MIT',
      platforms='any',
      tests_require=['nose', 'factory_boy', 'httpretty'],
      )
