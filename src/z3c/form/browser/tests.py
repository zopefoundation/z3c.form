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

from doctest import DocFileSuite
import doctest
import itertools
import re
import unittest

from z3c.form import testing

Z3CPT_AVAILABLE = False
try:
    import z3c.pt
    import z3c.ptcompat
except ImportError:
    Z3CPT_AVAILABLE = False

def test_suite():
    flags = \
        doctest.NORMALIZE_WHITESPACE | \
        doctest.ELLIPSIS | \
        doctest.IGNORE_EXCEPTION_DETAIL

    # This package will setup z3c.pt support for testing by default.
    # The Z3CPT_AVAILABLE option allows to run z3c.form test from a
    # custom setup which doesn't use z3c.pt. But do we really need this?
    # I guess not or is there a reason to support this?
    if Z3CPT_AVAILABLE:
        setups = (testing.setUpZPT, testing.setUpZ3CPT)
    else:
        setups = (testing.setUpZPT, )

    tests = ((
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('button.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('checkbox.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('file.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('file-testing.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('image.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('orderedselect.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('password.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('radio.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('select.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('select-missing-terms.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('select-source.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('submit.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('text.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('textarea.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('textlines.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('object.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('objectmulti.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('multi.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ))
             for setUp in setups)

    integtests = (
        DocFileSuite('object_single_integration.txt',
                     setUp=testing.setUpIntegration, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('object_multi_dict_integration.txt',
                     setUp=testing.setUpIntegration, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('object_multi_list_integration.txt',
                     setUp=testing.setUpIntegration, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('multi_dict_integration.txt',
                     setUp=testing.setUpIntegration, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        DocFileSuite('multi_list_integration.txt',
                     setUp=testing.setUpIntegration, tearDown=testing.tearDown,
                     optionflags=flags, checker=testing.outputChecker,
                     ),
        )

    return unittest.TestSuite(tuple(itertools.chain(*tests)) + integtests)
