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

def addHooks():
    try:
        from zope.site import hooks
        return
    except AttributeError:
        #this is a crappy situation
        import zope.location.interfaces
        import zope.traversing.interfaces
        zope.location.interfaces.IRoot = zope.traversing.interfaces.IContainmentRoot
        import zope.site
        import zope.app.component.hooks
        zope.site.hooks = zope.app.component.hooks

def apply():
    addHooks()
