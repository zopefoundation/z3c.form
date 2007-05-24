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
"""Form Framework Action Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.component

from z3c.form import interfaces, util


class Action(object):
    """Action class."""

    zope.interface.implements(interfaces.IAction)

    __name__ = __parent__ = None

    def __init__(self, request, title, name=None):
        self.request = request
        self.title = title
        if name is None:
            name = util.createId(title)
        self.name = name

    def isExecuted(self):
        return self.name in self.request

    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, self.name, self.title)


class Actions(util.Manager):
    """Action manager class."""
    zope.interface.implementsOnly(interfaces.IActions)

    __name__ = __parent__ = None

    def __init__(self, form, request, content):
        super(Actions, self).__init__()
        self.form = form
        self.request = request
        self.content = content

    @property
    def executedActions(self):
        return [action for action in self.values()
                if action.isExecuted()]

    def update(self):
        """See z3c.form.interfaces.IActions."""
        pass

    def execute(self):
        """See z3c.form.interfaces.IActions."""
        adapter = None
        for action in self.executedActions:
            adapter = zope.component.queryMultiAdapter(
                (self.form, self.request, self.content, action),
                interface=interfaces.IActionHandler)
            if adapter is not None:
                return adapter()

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class ActionHandlerBase(object):
    """Action handler base adapter."""

    zope.interface.implements(interfaces.IActionHandler)

    def __init__(self, form, request, content, action):
        self.form = form
        self.request = request
        self.content = content
        self.action = action
