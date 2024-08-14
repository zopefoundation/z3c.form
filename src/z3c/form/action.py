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
import zope.component
import zope.interface

from z3c.form import interfaces
from z3c.form import util


@zope.interface.implementer(interfaces.IActionEvent)
class ActionEvent:

    def __init__(self, action):
        self.action = action

    def __repr__(self):
        return f'<{self.__class__.__name__} for {self.action!r}>'


@zope.interface.implementer(interfaces.IActionErrorEvent)
class ActionErrorOccurred(ActionEvent):
    """An event telling the system that an error occurred during action
    execution."""

    def __init__(self, action, error):
        super().__init__(action)
        self.error = error


class ActionSuccessful(ActionEvent):
    """An event signalizing that an action has been successfully executed."""


@zope.interface.implementer(interfaces.IAction)
class Action:
    """Action class."""

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
        return f'<{self.__class__.__name__} {self.name!r} {self.title!r}>'


@zope.interface.implementer_only(interfaces.IActions)
class Actions(util.Manager):
    """Action manager class."""

    __name__ = __parent__ = None

    def __init__(self, form, request, content):
        super().__init__()
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
        for action in self.executedActions:
            handler = zope.component.queryMultiAdapter(
                (self.form, self.request, self.content, action),
                interface=interfaces.IActionHandler)
            if handler is not None:
                try:
                    result = handler()
                except interfaces.ActionExecutionError as error:
                    zope.event.notify(ActionErrorOccurred(action, error))
                else:
                    zope.event.notify(ActionSuccessful(action))
                    return result

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.__name__!r}>'


@zope.interface.implementer(interfaces.IActionHandler)
class ActionHandlerBase:
    """Action handler base adapter."""

    def __init__(self, form, request, content, action):
        self.form = form
        self.request = request
        self.content = content
        self.action = action
