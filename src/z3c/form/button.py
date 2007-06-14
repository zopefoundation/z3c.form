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
"""Button and Button Manager implementation

$Id$
"""
__docformat__ = "reStructuredText"
import sys
import zope.interface
import zope.location
import zope.schema

from zope.interface import adapter
from zope.schema.fieldproperty import FieldProperty
from z3c.form import action, interfaces, util, value
from z3c.form.browser import submit


StaticButtonActionAttribute = value.StaticValueCreator(
    discriminators = ('form', 'request', 'content', 'button', 'manager')
    )
ComputedButtonActionAttribute = value.ComputedValueCreator(
    discriminators = ('form', 'request', 'content', 'button', 'manager')
    )


class Button(zope.schema.Field):
    """A simple button in a form."""
    zope.interface.implements(interfaces.IButton)

    accessKey = FieldProperty(interfaces.IButton['accessKey'])

    def __init__(self, *args, **kwargs):
        # Provide some shortcut ways to specify the name
        if args:
            kwargs['__name__'] = args[0]
            args = args[1:]
        if 'name' in kwargs:
            kwargs['__name__'] = kwargs['name']
            del kwargs['name']
        # Extract button-specific arguments
        self.accessKey = kwargs.pop('accessKey', None)
        self.condition = kwargs.pop('condition', None)
        # Initialize the button
        super(Button, self).__init__(*args, **kwargs)
        # Make sure the button has a name by the time it is initialized.
        if self.__name__ is '':
            self.__name__ = util.createId(self.title)

    def __repr__(self):
        return '<%s %r %r>' %(
            self.__class__.__name__, self.__name__, self.title)

class Buttons(util.SelectionManager):
    """Button manager."""
    zope.interface.implements(interfaces.IButtons)

    managerInterface = interfaces.IButtons
    prefix = 'buttons'

    def __init__(self, *args):
        buttons = []
        for arg in args:
            if zope.interface.interfaces.IInterface.providedBy(arg):
                for name, button in zope.schema.getFieldsInOrder(arg):
                    if interfaces.IButton.providedBy(button):
                        buttons.append((name, button))
            elif self.managerInterface.providedBy(arg):
                buttons += arg.items()
            elif interfaces.IButton.providedBy(arg):
                buttons.append((arg.__name__, arg))
            else:
                raise TypeError("Unrecognized argument type", arg)
        keys = []
        seq = []
        byname = {}
        for name, button in buttons:
            keys.append(name)
            seq.append(button)
            byname[name] = button

        self._data_keys = keys
        self._data_values = seq
        self._data = byname


class Handlers(object):
    """Action Handlers for a Button-based form."""
    zope.interface.implements(interfaces.IButtonHandlers)

    def __init__(self):
        self._registry = adapter.AdapterRegistry()
        self._handlers = ()

    def addHandler(self, button, handler):
        """See interfaces.IButtonHandlers"""
        # Create a specification for the button
        buttonSpec = util.getSpecification(button)
        if isinstance(buttonSpec, util.classTypes):
            buttonSpec = zope.interface.implementedBy(buttonSpec)
        # Register the handler
        self._registry.register(
            (buttonSpec,), interfaces.IButtonHandler, '', handler)
        self._handlers += ((button, handler),)

    def getHandler(self, button):
        """See interfaces.IButtonHandlers"""
        buttonProvided = zope.interface.providedBy(button)
        #if button.__class__.__name__ == 'SpecialButton':
        #    import pdb; pdb.set_trace()
        return self._registry.lookup1(buttonProvided, interfaces.IButtonHandler)

    def copy(self):
        """See interfaces.IButtonHandlers"""
        handlers = Handlers()
        for button, handler in self._handlers:
            handlers.addHandler(button, handler)
        return handlers

    def __add__(self, other):
        """See interfaces.IButtonHandlers"""
        if not isinstance(other, Handlers):
            raise NotImplementedError
        handlers = self.copy()
        for button, handler in other._handlers:
            handlers.addHandler(button, handler)
        return handlers

    def __repr__(self):
        return '<Handlers %r>' %[handler for button, handler in self._handlers]


class Handler(object):
    zope.interface.implements(interfaces.IButtonHandler)

    def __init__(self, button, func):
        self.button = button
        self.func = func

    def __call__(self, form, action):
        return self.func(form, action)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.button)


def handler(button):
    """A decorator for defining a success handler."""
    def createHandler(func):
        handler = Handler(button, func)
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        handlers = f_locals.setdefault('handlers', Handlers())
        handlers.addHandler(button, handler)
        return handler
    return createHandler


def buttonAndHandler(title, **kwargs):
    # Add the title to button constructor keyword arguments
    kwargs['title'] = title
    # Extract directly provided interfaces:
    provides = kwargs.pop('provides', ())
    # Create button and add it to the button manager
    button = Button(**kwargs)
    zope.interface.alsoProvides(button, provides)
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    buttons = f_locals.setdefault('buttons', Buttons())
    f_locals['buttons'] += Buttons(button)
    # Return the handler decorator
    return handler(button)


class ButtonAction(action.Action, submit.SubmitWidget, zope.location.Location):
    zope.interface.implements(interfaces.IFieldWidget)

    def __init__(self, request, field, name):
        action.Action.__init__(self, request, field.title, name)
        submit.SubmitWidget.__init__(self, request)
        self.field = field

    @property
    def accesskey(self):
        return self.field.accessKey

    @property
    def value(self):
        return self.title

    @property
    def id(self):
        return self.name.replace('.', '-')


class ButtonActions(action.Actions):
    zope.component.adapts(
        interfaces.IButtonForm,
        zope.interface.Interface,
        zope.interface.Interface)

    def update(self):
        """See z3c.form.interfaces.IActions."""
        # Create a unique prefix
        prefix = util.expandPrefix(self.form.prefix)
        prefix += util.expandPrefix(self.form.buttons.prefix)
        for name, button in self.form.buttons.items():
            # Only create an action for the button, if the condition is
            # fulfilled
            if button.condition is not None and not button.condition(self.form):
                continue
            fullName = prefix + name
            # Look up a button action factory
            buttonAction = zope.component.queryMultiAdapter(
                (self.request, button, fullName), interfaces.IFieldWidget)
            # if one is not found, use the default
            if buttonAction is None:
                buttonAction = ButtonAction(self.request, button, fullName)
            # Look up a potential custom title for the action.
            title = zope.component.queryMultiAdapter(
                (self.form, self.request, self.content, button, self),
                interfaces.IValue, name='title')
            if title is not None:
                buttonAction.title = title.get()
            self._data_keys.append(name)
            self._data_values.append(buttonAction)
            self._data[name] = buttonAction
            zope.location.locate(buttonAction, self, name)


class ButtonActionHandler(action.ActionHandlerBase):
    zope.component.adapts(
        interfaces.IHandlerForm,
        zope.interface.Interface,
        zope.interface.Interface,
        ButtonAction)

    def __call__(self):
        handler = self.form.handlers.getHandler(self.action.field)
        # If no handler is found, then that's okay too.
        if handler is None:
            return
        return handler(self.form, self.action)
