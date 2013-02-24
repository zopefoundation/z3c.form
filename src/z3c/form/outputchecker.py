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
"""Custom Output Checker
"""
import doctest as pythondoctest
import re

import lxml.etree
import lxml.doctestcompare
from lxml.doctestcompare import LHTMLOutputChecker
from zope.testing.renormalizing import RENormalizing


class OutputChecker(LHTMLOutputChecker, RENormalizing):
    """Doctest output checker which is better equippied to identify
    HTML markup than the checker from the ``lxml.doctestcompare``
    module. It also uses the text comparison function from the
    built-in ``doctest`` module to allow the use of ellipsis.

    Also, we need to support RENormalizing.
    """

    _repr_re = re.compile(
        r'^<([A-Z]|[^>]+ (at|object) |[a-z]+ \'[A-Za-z0-9_.]+\'>)')

    def __init__(self, doctest=pythondoctest, patterns=()):
        RENormalizing.__init__(self, patterns)
        self.doctest = doctest

        # make sure these optionflags are registered
        doctest.register_optionflag('PARSE_HTML')
        doctest.register_optionflag('PARSE_XML')
        doctest.register_optionflag('NOPARSE_MARKUP')

    def _looks_like_markup(self, s):
        s = s.replace('<BLANKLINE>', '\n').strip()
        return (s.startswith('<')
                and not self._repr_re.search(s))

    def text_compare(self, want, got, strip):
        if want is None:
            want = ""
        if got is None:
            got = ""
        checker = self.doctest.OutputChecker()
        return checker.check_output(
            want, got, self.doctest.ELLIPSIS|self.doctest.NORMALIZE_WHITESPACE)

    def check_output(self, want, got, optionflags):
        if got == want:
            return True

        for transformer in self.transformers:
            want = transformer(want)
            got = transformer(got)

        return LHTMLOutputChecker.check_output(self, want, got, optionflags)

    def output_difference(self, example, got, optionflags):
        want = example.want
        if not want.strip():
            return LHTMLOutputChecker.output_difference(
                self, example, got, optionflags)

        # Dang, this isn't as easy to override as we might wish
        original = want

        for transformer in self.transformers:
            want = transformer(want)
            got = transformer(got)

        # temporarily hack example with normalized want:
        example.want = want
        result = LHTMLOutputChecker.output_difference(
            self, example, got, optionflags)
        example.want = original

        return result

    def get_parser(self, want, got, optionflags):
        NOPARSE_MARKUP = self.doctest.OPTIONFLAGS_BY_NAME.get(
            "NOPARSE_MARKUP", 0)
        PARSE_HTML = self.doctest.OPTIONFLAGS_BY_NAME.get(
            "PARSE_HTML", 0)
        PARSE_XML = self.doctest.OPTIONFLAGS_BY_NAME.get(
            "PARSE_XML", 0)

        parser = None
        if NOPARSE_MARKUP & optionflags:
            return None
        if PARSE_HTML & optionflags:
            parser = lxml.doctestcompare.html_fromstring
        elif PARSE_XML & optionflags:
            parser = lxml.etree.XML
        elif (want.strip().lower().startswith('<html')
              and got.strip().startswith('<html')):
            parser = lxml.doctestcompare.html_fromstring
        elif (self._looks_like_markup(want)
              and self._looks_like_markup(got)):
            parser = self.get_default_parser()
        return parser
