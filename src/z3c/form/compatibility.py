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

import sys
import types

def addHooks():
    import zope.component
    try:
        from zope.component import hooks
        return # yay, we have modern software
    except ImportError:
        pass
    try:
        from zope.site import hooks
        zope.component.hooks = hooks
        return
    except AttributeError:
        #this is a crappy situation
        import zope.location.interfaces
        import zope.traversing.interfaces
        zope.location.interfaces.IRoot = zope.traversing.interfaces.IContainmentRoot
        import zope.site
        import zope.app.component.hooks
        zope.component.hooks = zope.app.component.hooks
    except ImportError:
        import zope.app.component.hooks
        zope.component.hooks = zope.app.component.hooks

def addBTree():
    try:
        import zope.container.btree
        return
    except ImportError:
        try:
            import zope.app.container.btree
            container = types.ModuleType('container')
            container.btree = zope.app.container.btree
            sys.modules['zope.container'] = container
        except ImportError:
            pass # only for tests

def apply():
    addHooks()
    addBTree()
