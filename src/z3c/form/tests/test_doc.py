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
"""z3c.form Test Module

$Id$
"""
__docformat__ = "reStructuredText"
import unittest
import itertools
import re

from zope.testing import doctest, renormalizing
from zope.app.testing import placelesssetup

from z3c.form import testing

def test_suite():
    checker = testing.OutputChecker()

    tests = ((
        doctest.DocFileSuite(
            '../action.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../datamanager.txt',
            setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../field.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../value.txt',
            setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../validator.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../term.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../error.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../widget.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../button.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../zcml.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../converter.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=renormalizing.RENormalizing([
                 (re.compile(
                  r"(invalid literal for int\(\)) with base 10: '(.*)'"),
                  r'\1: \2'),
                 ])
            ),
        doctest.DocFileSuite(
            '../form.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../group.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../subform.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../util.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ),
        doctest.DocFileSuite(
            '../adding.txt',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker,
            ))
        for setUp in (testing.setUpZPT, testing.setUpZ3CPT))

    return unittest.TestSuite(itertools.chain(*tests))
