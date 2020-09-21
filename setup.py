##############################################################################
#
# Copyright (c) 2007-2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup
"""
from setuptools import setup, find_packages


def alltests():
    import os
    import sys
    import unittest
    # use the zope.testrunner machinery to find all the
    # test suites we've put under ourselves
    import zope.testrunner.find
    import zope.testrunner.options
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
    args = sys.argv[:]
    defaults = ["--test-path", here]
    options = zope.testrunner.options.get_options(args, defaults)
    suites = list(zope.testrunner.find.find_suites(options))
    return unittest.TestSuite(suites)


setup(
    name='z3c.form',
    version='3.7.1',
    author="Stephan Richter, Roger Ineichen and the Zope Community",
    author_email="zope-dev@zope.org",
    description="An advanced form and widget framework for Zope 3",
    license="ZPL 2.1",
    keywords="zope3 form widget",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3',
    ],
    url='https://github.com/zopefoundation/z3c.form',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    extras_require=dict(
        extra=[
            'z3c.pt >= 2.1',
            'z3c.ptcompat>=1.0',
            'zope.pagetemplate >= 3.6.2',
        ],
        test=[
            'lxml >= 2.1.1',
            'persistent',
            'z3c.template >= 1.3',
            'zc.sourcefactory',
            'zope.container',
            'zope.password',
            'zope.schema >= 4.6.0',
            'zope.testing',
        ],
        adding=['zope.app.container >= 3.7'],
        docs=['z3c.recipe.sphinxdoc'],
    ),
    install_requires=[
        'setuptools',
        'six',
        'zope.browser',
        'zope.browserpage',
        'zope.browserresource',
        'zope.component',
        'zope.configuration',
        'zope.contentprovider',
        'zope.event',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.location',
        'zope.pagetemplate',  # >= 3.6.2 if z3c.pt is used
        'zope.publisher',
        'zope.schema >= 4.6.0',
        'zope.security',
        'zope.site',
        'zope.traversing',
    ],
    tests_require=[
        'lxml >= 2.1.1',
        'persistent',
        'z3c.template >= 1.3',
        'zc.sourcefactory',
        'zope.container',
        'zope.password',
        'zope.schema >= 4.6.0',
        'zope.testing',
        'zope.testrunner',
    ],
    test_suite='__main__.alltests',
    zip_safe=False,
)
