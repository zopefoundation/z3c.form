##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

import itertools
import doctest
import unittest

from zope.testing.doctestunit import DocFileSuite

from z3c.form import testing

def test_suite():
    checker = testing.OutputChecker(doctest)

    tests = ((
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('button.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('checkbox.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('file.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('file-testing.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('image.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('orderedselect.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('password.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('radio.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('select.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('select-source.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('submit.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('text.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('textarea.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('textlines.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('object.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('objectmulti.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ),
        DocFileSuite('multi.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     checker=checker,
                     ))
             for setUp in (testing.setUpZPT, testing.setUpZ3CPT))

    return unittest.TestSuite(itertools.chain(*tests))
