# coding=utf-8
#---------------------------------------------------------------------------
# Copyright 2011 utahta
#---------------------------------------------------------------------------
import sys
from setuptools import setup
from jsmgui import VERSION

NAME = 'jsm'
LICENSE = 'GPL'
AUTHOR = 'utahta'
AUTHOR_EMAIL = 'labs.ninxit@gmail.com'
DESCRIPTION = 'Get the japanese stock market data'
URL = 'https://github.com/utahta/jsm-gui'

if sys.platform == 'win32':
    # Windows
    import py2exe, innosetup
    
    PY2EXE_OPTIONS = {'compressed': 1,
                      'optimize': 2,
                      'bundle_files': 3,
                      'includes': ["sip", "BeautifulSoup", "html5lib", "jsm"],}
    
    INNOSETUP_OPTIONS = {'inno_script': innosetup.DEFAULT_ISS,
                         'bundle_vcr': True,
                         'zip': False,
                         }
    setup(
        name = NAME,
        version = VERSION,
        license = LICENSE,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        description = DESCRIPTION,
        url = URL,
        scripts = ['jsmgui/main.py'],
        windows=[{"script": "jsmgui/main.py", 
                  'icon_resources': [(1, 'jsm.ico'),]}],
        options = {'py2exe': PY2EXE_OPTIONS,
                   'innosetup': INNOSETUP_OPTIONS},
        zipfile = 'jsm.lib',
    )

elif sys.platform == 'darwin':
    # Mac
    OPTIONS = {
               "argv_emulation": False,
               "includes": ["sip", "BeautifulSoup", "html5lib", "jsm"],
               'iconfile': 'jsm.icns',
               }
    setup(
        name = NAME,
        version = VERSION,
        license = LICENSE,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        description = DESCRIPTION,
        url = URL,
        app = ['jsmgui/main.py'],
        options = {'py2app': OPTIONS},
        setup_requires=["py2app"],
    )
