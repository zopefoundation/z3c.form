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
import os

from setuptools import find_packages
from setuptools import setup


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        text = f.read()
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    return text.encode('ascii', 'xmlcharrefreplace').decode()


setup(
    name='z3c.form',
    version='5.2',
    author="Stephan Richter, Roger Ineichen and the Zope Community",
    author_email="zope-dev@zope.dev",
    description="An advanced form and widget framework for Zope 3",
    long_description=(
        read('README.rst')
        + '\n\n' +
        '.. contents:: \n\n'
        + '\n\n'
        + read('CHANGES.rst')),
    license="ZPL-2.1",
    keywords="zope3 form widget",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope :: 3',
    ],
    url='https://github.com/zopefoundation/z3c.form',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    python_requires='>=3.9',
    extras_require=dict(
        extra=[
            'z3c.pt >= 2.1',
            'z3c.ptcompat>=1.0',
            'zope.pagetemplate >= 3.6.2',
        ],
        test=[
            'lxml >= 5.3',
            'persistent',
            'z3c.template >= 1.3',
            'zc.sourcefactory',
            'zope.container',
            'zope.password',
            'zope.testing',
        ],
        adding=['zope.app.container >= 3.7'],
        docs=[
            'Sphinx',
            'repoze.sphinx.autointerface',
        ],
    ),
    install_requires=[
        'setuptools',
        'zope.browser',
        'zope.browserpage',
        'zope.browserresource',
        'zope.component',
        'zope.configuration >= 4.3',
        'zope.contentprovider',
        'zope.event',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.location',
        'zope.pagetemplate',  # >= 3.6.2 if z3c.pt is used
        'zope.publisher',
        'zope.schema >= 4.7',
        'zope.security',
        'zope.site',
        'zope.traversing',
    ],
    zip_safe=False,
)
