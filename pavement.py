# -*- coding: utf-8 -*-
"""pavement.py -- pavement for stillness.

Copyright 2010 David Eyk. All rights reserved.
"""
import site

import warnings
warnings.filterwarnings('ignore', "Parent module 'pavement' not found while handling absolute import")

from paver.easy import *
from paver.setuputils import setup

__path__ = path(__file__).abspath().dirname()
site.addsitedir(__path__)

from paved import *
from paved.dist import *

__path__ = path(__file__).abspath().dirname()
site.addsitedir(__path__)


setup(
    name = "Stillness",
    version = "0.1",
    url = "http://pypi.python.org/pypi/Stillness/",
    author = "David Eyk",
    author_email = "eykd@eykd.net",
    license = 'BSD',

    short_description = 'Manage static assets for your website without breaking a sweat.',
    long_description = open('README.rst').read(),

    packages=['stillness'],
    )
