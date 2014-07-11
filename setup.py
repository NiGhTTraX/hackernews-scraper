from setuptools import setup, find_packages

import codecs
import os
import re

def get_version(package_name):
    version_re = re.compile(r"^__version__ = [\"']([\w_.-]+)[\"']$")
    package_components = package_name.split('.')
    init_path = os.path.join(root_dir, *(package_components + ['__init__.py']))
    with codecs.open(init_path, 'r', 'utf-8') as f:
        for line in f:
            match = version_re.match(line[:-1])
            if match:
                return match.groups()[0]
    return '0.1.0'

setup(name='hackernews_scraper',
      description='Python library for retrieving comments and stories from HackerNews',
      packages=find_packages(),
      version=get_version(),
      install_requires=['requests'],
      url='https://github.com/NiGhTTraX/hackernews-scraper',
      license='MIT',
      platforms='any',
      tests_require=['nose', 'factory_boy', 'httpretty'],
      )
