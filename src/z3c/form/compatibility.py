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
"""Form and Widget Framework Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import datetime
import decimal
import zope.interface

def addTimeField():
    """Add ITime interface and Time field to zope.schema.

    Target: Zope 3.3
    """
    from zope.schema import interfaces
    if hasattr(interfaces, 'ITime'):
        return

    class ITime(interfaces.IMinMax, interfaces.IField):
        u"""Field containing a time."""
    interfaces.ITime = ITime

    class Time(zope.schema.Orderable, zope.schema.Field):
        __doc__ = ITime.__doc__
        zope.interface.implements(ITime)
        _type = datetime.time
    zope.schema.Time = Time


def addDecimalField():
    """Add IDecimal interface and Decimal field to zope.schema.

    Target: Zope 3.3
    """
    from zope.schema import interfaces
    if hasattr(interfaces, 'IDecimal'):
        return

    class IDecimal(interfaces.IMinMax, interfaces.IField):
        u"""Field containing a Decimal."""
    interfaces.IDecimal = IDecimal

    class Decimal(zope.schema.Orderable, zope.schema.Field):
        __doc__ = IDecimal.__doc__
        zope.interface.implements(IDecimal, interfaces.IFromUnicode)
        _type = decimal.Decimal

        def __init__(self, *args, **kw):
            super(Decimal, self).__init__(*args, **kw)

        def fromUnicode(self, u):
            """
            >>> f = Decimal()
            >>> f.fromUnicode("1.25")
            Decimal("1.25")
            >>> f.fromUnicode("1.25.6")
            Traceback (most recent call last):
            ...
            ValueError: invalid literal for Decimal(): 1.25.6
            """
            try:
                v = decimal.Decimal(u)
            except decimal.InvalidOperation:
                raise ValueError('invalid literal for Decimal(): %s' % u)
            self.validate(v)
            return v
    zope.schema.Decimal = Decimal


def fixNumberFormatter():
    """Switch the number formatter to the latest version:

         * The decimal symbol is optional during parsing.

         * The type of the parsed number can be specified.

    Target: Zope 3.4b1 and older
    """
    from zope.i18n import format
    formatter = format.NumberFormat('#0.#')
    try:
        formatter.parse(u'123')
    except format.NumberParseError:
        pass
    else:
        # The value parsed, so the version we have is good.
        return

    import math
    import re
    from zope.i18n.format import (
        INumberFormat, implements, parseNumberPattern, NumberParseError,
        PADDING1, PADDING2, PADDING3, PADDING4, EXPONENTIAL, SUFFIX, FRACTION,
        INTEGER, EXPONENTIAL, GROUPING, PREFIX)

    class NumberFormat(object):
        __doc__ = INumberFormat.__doc__

        implements(INumberFormat)

        type = None

        def __init__(self, pattern=None, symbols={}):
            # setup default symbols
            self.symbols = {
                u'decimal': u'.',
                u'group': u',',
                u'list':  u';',
                u'percentSign': u'%',
                u'nativeZeroDigit': u'0',
                u'patternDigit': u'#',
                u'plusSign': u'+',
                u'minusSign': u'-',
                u'exponential': u'E',
                u'perMille': u'\xe2\x88\x9e',
                u'infinity': u'\xef\xbf\xbd',
                u'nan': '' }
            self.symbols.update(symbols)
            self._pattern = pattern
            self._bin_pattern = None
            if self._pattern is not None:
                self._bin_pattern = parseNumberPattern(self._pattern)

        def setPattern(self, pattern):
            "See zope.i18n.interfaces.IFormat"
            self._pattern = pattern
            self._bin_pattern = parseNumberPattern(self._pattern)

        def getPattern(self):
            "See zope.i18n.interfaces.IFormat"
            return self._pattern

        def parse(self, text, pattern=None):
            "See zope.i18n.interfaces.IFormat"
            # Make or get binary form of datetime pattern
            if pattern is not None:
                bin_pattern = parseNumberPattern(pattern)
            else:
                bin_pattern = self._bin_pattern
                pattern = self._pattern
            # Determine sign
            num_res = [None, None]
            for sign in (0, 1):
                regex = ''
                if bin_pattern[sign][PADDING1] is not None:
                    regex += '[' + bin_pattern[sign][PADDING1] + ']+'
                if bin_pattern[sign][PREFIX] != '':
                    regex += '[' + bin_pattern[sign][PREFIX] + ']'
                if bin_pattern[sign][PADDING2] is not None:
                    regex += '[' + bin_pattern[sign][PADDING2] + ']+'
                regex += '([0-9'
                min_size = bin_pattern[sign][INTEGER].count('0')
                if bin_pattern[sign][GROUPING]:
                    regex += self.symbols['group']
                    min_size += min_size/3
                regex += ']{%i,100}' %(min_size)
                if bin_pattern[sign][FRACTION]:
                    max_precision = len(bin_pattern[sign][FRACTION])
                    min_precision = bin_pattern[sign][FRACTION].count('0')
                    regex += '['+self.symbols['decimal']+']?'
                    regex += '[0-9]{%i,%i}' %(min_precision, max_precision)
                if bin_pattern[sign][EXPONENTIAL] != '':
                    regex += self.symbols['exponential']
                    min_exp_size = bin_pattern[sign][EXPONENTIAL].count('0')
                    pre_symbols = self.symbols['minusSign']
                    if bin_pattern[sign][EXPONENTIAL][0] == '+':
                        pre_symbols += self.symbols['plusSign']
                    regex += '[%s]?[0-9]{%i,100}' %(pre_symbols, min_exp_size)
                regex +=')'
                if bin_pattern[sign][PADDING3] is not None:
                    regex += '[' + bin_pattern[sign][PADDING3] + ']+'
                if bin_pattern[sign][SUFFIX] != '':
                    regex += '[' + bin_pattern[sign][SUFFIX] + ']'
                if bin_pattern[sign][PADDING4] is not None:
                    regex += '[' + bin_pattern[sign][PADDING4] + ']+'
                num_res[sign] = re.match(regex, text)

            if num_res[0] is not None:
                num_str = num_res[0].groups()[0]
                sign = +1
            elif num_res[1] is not None:
                num_str = num_res[1].groups()[0]
                sign = -1
            else:
                raise NumberParseError('Not a valid number for this pattern %r.'
                                        % pattern)
            # Remove possible grouping separators
            num_str = num_str.replace(self.symbols['group'], '')
            # Extract number
            type = int
            if self.symbols['decimal'] in num_str:
                type = float
                num_str = num_str.replace(self.symbols['decimal'], '.')
            if self.symbols['exponential'] in num_str:
                type = float
                num_str = num_str.replace(self.symbols['exponential'], 'E')
            if self.type:
                type = self.type
            return sign*type(num_str)

        def _format_integer(self, integer, pattern):
            size = len(integer)
            min_size = pattern.count('0')
            if size < min_size:
                integer = self.symbols['nativeZeroDigit']*(min_size-size) + integer
            return integer

        def _format_fraction(self, fraction, pattern):
            max_precision = len(pattern)
            min_precision = pattern.count('0')
            precision = len(fraction)
            roundInt = False
            if precision > max_precision:
                round = int(fraction[max_precision]) >= 5
                fraction = fraction[:max_precision]
                if round:
                    if fraction != '':
                        # add 1 to the fraction, maintaining the decimal
                        # precision; if the result >= 1, need to roundInt
                        fractionLen = len(fraction)
                        rounded = int(fraction) + 1
                        fraction = ('%0' + str(fractionLen) + 'i') % rounded
                        if len(fraction) > fractionLen:	# rounded fraction >= 1
                            roundInt = True
                            fraction = fraction[1:]
                    else:
                        # fraction missing, e.g. 1.5 -> 1. -- need to roundInt
                        roundInt = True

            if precision < min_precision:
                fraction += self.symbols['nativeZeroDigit']*(min_precision -
                                                             precision)
            if fraction != '':
                fraction = self.symbols['decimal'] + fraction
            return fraction, roundInt

        def format(self, obj, pattern=None):
            "See zope.i18n.interfaces.IFormat"
            # Make or get binary form of datetime pattern
            if pattern is not None:
                bin_pattern = parseNumberPattern(pattern)
            else:
                bin_pattern = self._bin_pattern
            # Get positive or negative sub-pattern
            if obj >= 0:
                bin_pattern = bin_pattern[0]
            else:
                bin_pattern = bin_pattern[1]


            if bin_pattern[EXPONENTIAL] != '':
                obj_int_frac = str(obj).split('.')
                # The exponential might have a mandatory sign; remove it from the
                # bin_pattern and remember the setting
                exp_bin_pattern = bin_pattern[EXPONENTIAL]
                plus_sign = u''
                if exp_bin_pattern.startswith('+'):
                    plus_sign = self.symbols['plusSign']
                    exp_bin_pattern = exp_bin_pattern[1:]
                # We have to remove the possible '-' sign
                if obj < 0:
                    obj_int_frac[0] = obj_int_frac[0][1:]
                if obj_int_frac[0] == '0':
                    # abs() of number smaller 1
                    if len(obj_int_frac) > 1:
                        res = re.match('(0*)[0-9]*', obj_int_frac[1]).groups()[0]
                        exponent = self._format_integer(str(len(res)+1),
                                                        exp_bin_pattern)
                        exponent = self.symbols['minusSign']+exponent
                        number = obj_int_frac[1][len(res):]
                    else:
                        # We have exactly 0
                        exponent = self._format_integer('0', exp_bin_pattern)
                        number = self.symbols['nativeZeroDigit']
                else:
                    exponent = self._format_integer(str(len(obj_int_frac[0])-1),
                                                    exp_bin_pattern)
                    number = ''.join(obj_int_frac)

                fraction, roundInt = self._format_fraction(number[1:],
                                                           bin_pattern[FRACTION])
                if roundInt:
                    number = str(int(number[0]) + 1) + fraction
                else:
                    number = number[0] + fraction

                # We might have a plus sign in front of the exponential integer
                if not exponent.startswith('-'):
                    exponent = plus_sign + exponent

                pre_padding = len(bin_pattern[FRACTION]) - len(number) + 2
                post_padding = len(exp_bin_pattern) - len(exponent)
                number += self.symbols['exponential'] + exponent

            else:
                obj_int_frac = str(obj).split('.')
                if len(obj_int_frac) > 1:
                    fraction, roundInt = self._format_fraction(obj_int_frac[1],
                                                     bin_pattern[FRACTION])
                else:
                    fraction = ''
                    roundInt = False
                if roundInt:
                    obj = round(obj)
                integer = self._format_integer(str(int(math.fabs(obj))),
                                               bin_pattern[INTEGER])
                # Adding grouping
                if bin_pattern[GROUPING] == 1:
                    help = ''
                    for pos in range(1, len(integer)+1):
                        if (pos-1)%3 == 0 and pos != 1:
                            help = self.symbols['group'] + help
                        help = integer[-pos] + help
                    integer = help
                pre_padding = len(bin_pattern[INTEGER]) - len(integer)
                post_padding = len(bin_pattern[FRACTION]) - len(fraction)+1
                number = integer + fraction

            # Put it all together
            text = ''
            if bin_pattern[PADDING1] is not None and pre_padding > 0:
                text += bin_pattern[PADDING1]*pre_padding
            text += bin_pattern[PREFIX]
            if bin_pattern[PADDING2] is not None and pre_padding > 0:
                if bin_pattern[PADDING1] is not None:
                    text += bin_pattern[PADDING2]
                else:
                    text += bin_pattern[PADDING2]*pre_padding
            text += number
            if bin_pattern[PADDING3] is not None and post_padding > 0:
                if bin_pattern[PADDING4] is not None:
                    text += bin_pattern[PADDING3]
                else:
                    text += bin_pattern[PADDING3]*post_padding
            text += bin_pattern[SUFFIX]
            if bin_pattern[PADDING4] is not None and post_padding > 0:
                text += bin_pattern[PADDING4]*post_padding

            # TODO: Need to make sure unicode is everywhere
            return unicode(text)

    format.NumberFormat = NumberFormat


def apply():
    addTimeField()
    addDecimalField()
    fixNumberFormatter()
