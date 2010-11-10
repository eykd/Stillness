# -*- coding: utf-8 -*-
"""pavement.py -- pavement for stillness, the static asset management tool for stressed webmasters.

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

options(
    install_requires = [
        ],
    setup_requires = [
        'Paver',
        'Paved',
        ],
    tests_require = [
        'nose',
        ],
    )

setup(
    name = "Stillness",
    version = "0.1",
    url = "http://pypi.python.org/pypi/Stillness/",
    author = "David Eyk",
    author_email = "eykd@eykd.net",
    license = 'BSD',

    description = 'A static asset management framework for stressed webmasters with deadlines.',
    long_description = open('README.rst').read(),

    packages = ['stillness'],
    include_package_data = True,

    install_requires = options.install_requires,
    setup_requires = options.setup_requires,
    tests_require = options.tests_require,

    test_suite = "nose.collector",
    )
