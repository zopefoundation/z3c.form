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
"""ObjectWidget related classes

$Id$
"""
__docformat__ = "reStructuredText"
import zope.i18n.format
import zope.interface
import zope.component
import zope.schema

from z3c.form.converter import BaseDataConverter

from z3c.form import form, interfaces
from z3c.form.field import Fields
from z3c.form.error import MultipleErrors
from z3c.form.i18n import MessageFactory as _

class ObjectSubForm(form.BaseForm):
    zope.interface.implements(interfaces.ISubForm)

    def __init__(self, context, parentWidget):
        self.context = context
        self.request = parentWidget.request
        self.parentWidget = parentWidget
        self.parentForm = self.__parent__ = parentWidget.form

    def _validate(self):
        for widget in self.widgets.values():
            try:
                # convert widget value to field value
                converter = interfaces.IDataConverter(widget)
                value = converter.toFieldValue(widget.value)
                # validate field value
                zope.component.getMultiAdapter(
                    (self.context,
                     self.request,
                     self.parentWidget.form,
                     getattr(widget, 'field', None),
                     widget),
                    interfaces.IValidator).validate(value)
            except (zope.schema.ValidationError, ValueError), error:
                # on exception, setup the widget error message
                view = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     self.parentWidget.form, self.context),
                    interfaces.IErrorViewSnippet)
                view.update()
                widget.error = view

    def update(self):
        self.fields = Fields(self.parentWidget.field.schema)

        self.mode = self.parentWidget.mode
        self.ignoreContext = self.parentWidget.ignoreContext
        self.ignoreRequest = self.parentWidget.ignoreRequest
        self.prefix = self.parentWidget.field.__name__

        if interfaces.IFormAware.providedBy(self.parentWidget):
            self.ignoreReadonly = self.parentWidget.form.ignoreReadonly

        super(ObjectSubForm, self).update()

        self._validate()


class ObjectConverter(BaseDataConverter):
    """Data converter for IObjectWidget."""

    zope.component.adapts(
        zope.schema.interfaces.IObject, interfaces.IObjectWidget)

    factory = None

    def _fields(self):
        x = zope.schema.getFields(self.field.schema)
        return x

    def toWidgetValue(self, value):
        """Just dispatch it."""
        if value is self.field.missing_value:
            return None

        return value

    def createObject(self, value):
        #keep value passed, maybe some subclasses want it

        if self.factory is None:
            name = self.field.schema.__module__+'.'+self.field.schema.__name__
            adapter = zope.component.queryMultiAdapter(
                (self.widget.context, self.widget.request,
                 self.widget.form, self.widget),
                interfaces.IObjectFactory,
                name=name)
            if adapter:
                obj = adapter.get(value)
            else:
                raise ValueError("No IObjectFactory adapter registered for %s" %
                                 name)
        else:
            #this is creepy, do we need this?
            #there seems to be no way to dispatch???
            obj = self.factory()

        return obj

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value is interfaces.NOVALUE:
            return self.field.missing_value

        if value[1]:
            raise MultipleErrors(value[1])

        obj = self.createObject(value)

        for name, f in self._fields().items():
            setattr(obj, name, value[0][name])
        return obj

class FactoryAdapter(object):
    """Most basic-default factory adapter"""

    zope.interface.implements(interfaces.IObjectFactory)
    zope.component.adapts(zope.interface.Interface, interfaces.IFormLayer,
        interfaces.IForm, interfaces.IWidget)

    factory = None

    def __init__(self, context, request, form, widget):
        self.context = context
        self.request = request
        self.form = form
        self.widget = widget

    def get(self, value):
        return self.factory()

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)

def registerFactoryAdapter(for_, klass):
    """register the basic FactoryAdapter for a given interface and class"""
    name = for_.__module__+'.'+for_.__name__
    class temp(FactoryAdapter):
        factory = klass
    zope.component.provideAdapter(temp, name=name)