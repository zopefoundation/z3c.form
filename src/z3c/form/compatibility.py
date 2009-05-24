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
