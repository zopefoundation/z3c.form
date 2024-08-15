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
"""z3c.form Test Module"""

import doctest
import itertools
import re
import unittest

from zope.testing import renormalizing

from z3c.form import testing


# This package will allways provide z3c.pt for it's test setup.
# The Z3CPT_AVAILABLE hickup is usefull if someone will run the z3c.form tests
# in his own project and doesn't use z3c.pt.
try:
    import z3c.pt
    import z3c.ptcompat  # noqa: F401 imported but unused
    Z3CPT_AVAILABLE = True
except ModuleNotFoundError:
    Z3CPT_AVAILABLE = False

try:
    import zope.app.container  # noqa: F401 imported but unused
except ModuleNotFoundError:
    ADDING_AVAILABLE = False
else:
    ADDING_AVAILABLE = True


def test_suite():
    flags = \
        doctest.NORMALIZE_WHITESPACE | \
        doctest.ELLIPSIS | \
        doctest.IGNORE_EXCEPTION_DETAIL

    if Z3CPT_AVAILABLE:
        setups = (testing.setUpZPT, testing.setUpZ3CPT)
    else:
        setups = (testing.setUpZPT, )

    tests = ((
        doctest.DocFileSuite(
            '../form.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../action.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../datamanager.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../field.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../contentprovider.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../validator.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../error.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../widget.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../button.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../zcml.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../testing.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../converter.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=renormalizing.RENormalizing([
                (re.compile(
                 r"(invalid literal for int\(\)) with base 10: '(.*)'"),
                 r'\1: \2'),
                (re.compile(
                 r"Decimal\('(.*)'\)"),
                 r'Decimal("\1")'),
            ]) + testing.outputChecker
        ),
        doctest.DocFileSuite(
            '../group.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../subform.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../term.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../util.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../hint.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ),
        doctest.DocFileSuite(
            '../browser/widget.rst',
            setUp=setUp, tearDown=testing.tearDown,
            optionflags=flags, checker=testing.outputChecker,
        ))
        for setUp in setups)

    if ADDING_AVAILABLE:
        tests = itertools.chain(tests, ((
            doctest.DocFileSuite(
                '../adding.rst',
                setUp=setUp, tearDown=testing.tearDown,
                optionflags=flags, checker=testing.outputChecker,
            ),)
            for setUp in setups))

    return unittest.TestSuite(itertools.chain(*tests))
