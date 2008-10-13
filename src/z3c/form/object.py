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
import zope.event
import zope.lifecycleevent

from z3c.form.converter import BaseDataConverter

from z3c.form import form, interfaces, util, widget
from z3c.form.field import Fields
from z3c.form.error import MultipleErrors
from z3c.form.i18n import MessageFactory as _

class ObjectSubForm(form.BaseForm):
    zope.interface.implements(interfaces.ISubForm)

    def __init__(self, context, parentWidget):
        self.context = context
        self.request = parentWidget.request
        self.__parent__ = parentWidget
        self.parentForm = parentWidget.form

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
                     self.parentForm,
                     getattr(widget, 'field', None),
                     widget),
                    interfaces.IValidator).validate(value)
            except (zope.schema.ValidationError, ValueError), error:
                # on exception, setup the widget error message
                view = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     self.parentForm, self.context),
                    interfaces.IErrorViewSnippet)
                view.update()
                widget.error = view

    def update(self, ignoreContext=None):
        self.fields = Fields(self.__parent__.field.schema)

        #update stuff from parent to be sure
        self.mode = self.__parent__.mode
        if ignoreContext is not None:
            self.ignoreContext = ignoreContext
        else:
            self.ignoreContext = self.__parent__.ignoreContext
        self.ignoreRequest = self.__parent__.ignoreRequest
        if interfaces.IFormAware.providedBy(self.__parent__):
            self.ignoreReadonly = self.parentForm.ignoreReadonly

        prefix = ''
        if self.parentForm:
            prefix = util.expandPrefix(self.parentForm.prefix) + \
                util.expandPrefix(self.parentForm.widgets.prefix)

        self.prefix = prefix+self.__parent__.field.__name__

        super(ObjectSubForm, self).update()

        self._validate()

    def getContent(self):
        return self.__parent__._value

class ObjectConverter(BaseDataConverter):
    """Data converter for IObjectWidget."""

    zope.component.adapts(
        zope.schema.interfaces.IObject, interfaces.IObjectWidget)

    def toWidgetValue(self, value):
        """Just dispatch it."""
        if value is self.field.missing_value:
            return interfaces.NOVALUE

        retval = {}
        for name in zope.schema.getFieldNames(self.field.schema):
            retval[name] = getattr(value, name, interfaces.NOVALUE)

        return retval

    def createObject(self, value):
        #keep value passed, maybe some subclasses want it
        #value here is the raw extracted from the widget's subform
        #in the form of a dict key:fieldname, value:fieldvalue

        name = self.field.schema.__module__+'.'+self.field.schema.__name__
        creator = zope.component.queryMultiAdapter(
            (self.widget.context, self.widget.request,
             self.widget.form, self.widget),
            interfaces.IObjectFactory,
            name=name)
        if creator:
            obj = creator(value)
        else:
            raise ValueError("No IObjectFactory adapter registered for %s" %
                             name)

        return obj

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value is interfaces.NOVALUE:
            return self.field.missing_value

        if self.widget.subform.ignoreContext:
            obj = self.createObject(value)
        else:
            obj = getattr(self.widget.context, self.field.__name__)

        obj = self.field.schema(obj)

        names = []
        for name in zope.schema.getFieldNames(self.field.schema):
            try:
                oldval = getattr(obj, name, interfaces.NOVALUE)
                if (oldval != value[name]
                    or zope.schema.interfaces.IObject.providedBy(
                        self.field.schema[name])
                    ):
                    setattr(obj, name, value[name])
                    names.append(name)
            except KeyError:
                pass

        if names:
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(obj,
                    zope.lifecycleevent.Attributes(self.field.schema, *names)))
        return obj


        return value


class ObjectWidget(widget.Widget):
    zope.interface.implements(interfaces.IObjectWidget)

    subform = None
    _value = interfaces.NOVALUE
    _updating = False

    def updateWidgets(self):
        if self._value is not interfaces.NOVALUE:
            self.subform = ObjectSubForm(self._value, self)
            ignore = None
        else:
            self.subform = ObjectSubForm(None, self)
            ignore = True

        self.subform.update(ignore)

    def update(self):
        #very-very-nasty: skip raising exceptions in extract while we're updating
        self._updating = True
        try:
            super(ObjectWidget, self).update()
            self.updateWidgets()
        finally:
            self._updating = False

    @apply
    def value():
        """This invokes updateWidgets on any value change e.g. update/extract."""
        def get(self):
            return self.extract()
        def set(self, value):
            self._value = value
            # ensure that we apply our new values to the widgets
            self.updateWidgets()
        return property(get, set)


    def extract(self, default=interfaces.NOVALUE):
        if self.name+'-empty-marker' in self.request:
            self.updateWidgets()

            value = self.subform.extractData()
            #value here is (data-dict, (error1, error2))

            if value[1]:
                #very-very-nasty: skip raising exceptions in extract
                #while we're updating
                if self._updating:
                    #very-very-nasty: kill all errors on subwidgets
                    if self.subform.widgets.errors:
                        pass
                        #from pub.dbgpclient import brk; brk('192.168.32.1')

                    self.subform.widgets.errors = ()
                    for w in self.subform.widgets.values():
                        w.error=None

                    return default
                raise MultipleErrors(value[1])

            return value[0]

        else:
            return default

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

    def __call__(self, value):
        #value is the extracted data from the form
        obj = self.factory()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        return obj

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)

# XXX: Probably we should offer an register factrory method which allows to
# use all discriminators e.g. context, request, form, widget as optional
# arguments. But can probably do that later in a ZCML directive
def registerFactoryAdapter(for_, klass):
    """register the basic FactoryAdapter for a given interface and class"""
    name = for_.__module__+'.'+for_.__name__
    class temp(FactoryAdapter):
        factory = klass
    zope.component.provideAdapter(temp, name=name)