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
"""Data Converters

$Id$
"""
__docformat__ = "reStructuredText"
import zope.i18n.format
import zope.interface
import zope.component
import zope.schema

from z3c.form.converter import BaseDataConverter

from z3c.form.dummy import MySubObject
from z3c.form import form, interfaces
from z3c.form.field import Fields
from z3c.form.error import MultipleErrors
from z3c.form.i18n import MessageFactory as _

class IObjectFactory(zope.interface.Interface):
    """Factory that will instatiate our objects for ObjectWidget
    """

    def get(value):
        """return a default object created to be populated
        """

class ObjectSubForm(form.BaseForm):
    zope.interface.implements(interfaces.ISubForm)

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

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

    #factory = MySubObject
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
            adapter = zope.component.queryMultiAdapter(
                (self.widget.context, self.widget.request,
                 self.widget.form, self.widget),
                IObjectFactory,
                name=self.field.schema.__name__)
            if adapter:
                obj = adapter.get(value)
        else:
            #this is creepy, do we need this?
            #there seems to be no way to dispatch???
            obj = self.factory()

        return obj

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if not value:
            from pub.dbgpclient import brk; brk('192.168.32.1')

        if value[1]:
            #lame, we must be able to show all errors
            #if len(value[1])>1:
            #    from pub.dbgpclient import brk; brk('192.168.32.1')

            raise MultipleErrors(value[1])

        obj = self.createObject(value)

        for name, f in self._fields().items():
            try:
                setattr(obj, name, value[0][name])
            except KeyError:
                #smells like an input error?
                pass
        return obj
