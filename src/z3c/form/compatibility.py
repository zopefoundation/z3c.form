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


def apply():
    addTimeField()
    addDecimalField()
