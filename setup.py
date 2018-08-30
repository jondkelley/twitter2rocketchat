#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
import sys

base_path = '%s/etc/' % os.getenv('VIRTUAL_ENV', '')
data_files = dict()
data_files[base_path] = ['twitter_rocketchat_bot.conf']

console_scripts = ['twitter_rocketchat_bot=twitter_rocketchat_bot.main:loop']
install_requires = ['helper>=2.2.2', 'rocket-python>=1.2.5', 'twitter-scraper>=0.3.0']
tests_require = []
extras_require = {'rocketchat': ['rocket-python'],
                  'twitter': ['twitter-scraper']}

setup(name='twitter_rocketchat_bot',
      version='1.0.0',
      description='Bot to send twitter stream to rockechat',
      url='https://github.com/jondkelley/twitter_rocketchat_bot/',
      packages=find_packages(),
      author='Jon Kelley',
      author_email='jonkelley@gmail.com',
      license='BSD',
      entry_points={'console_scripts': console_scripts},
      data_files=[(key, data_files[key]) for key in data_files.keys()],
      install_requires=install_requires,
      extras_require=extras_require,
      tests_require=tests_require,
      classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: System :: Monitoring'])
