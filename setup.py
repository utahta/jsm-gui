# coding=utf-8
#---------------------------------------------------------------------------
# Copyright 2011 utahta
#---------------------------------------------------------------------------
import sys
from setuptools import setup


if sys.platform == 'darwin':
    OPTIONS = {
               "argv_emulation": False,
               "includes": ["sip", "BeautifulSoup", "html5lib"],
               'iconfile': 'jsm.icns',
               }
    setup(
        name = 'jsm',
        app = ['jsmgui/main.py'],
        options = {'py2app': OPTIONS},
        setup_requires=["py2app"],
    )
