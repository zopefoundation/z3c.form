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
import zope.interface
import zope.component
import zope.schema
import zope.event
import zope.lifecycleevent
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.security.proxy import removeSecurityProxy
from zope.pagetemplate.interfaces import IPageTemplate

from z3c.form.converter import BaseDataConverter

from z3c.form import interfaces, util, widget, field
from z3c.form.error import MultipleErrors


def getIfName(iface):
    return iface.__module__ + '.' + iface.__name__


# our own placeholder instead of a simple None
class ObjectWidget_NO_VALUE(object):
    def __repr__(self):
        return '<ObjectWidget_NO_VALUE>'

ObjectWidget_NO_VALUE = ObjectWidget_NO_VALUE()


class ObjectWidgetValue(dict):
    originalValue = ObjectWidget_NO_VALUE  # will store the original object


class ObjectConverter(BaseDataConverter):
    """Data converter for IObjectWidget."""

    zope.component.adapts(
        zope.schema.interfaces.IObject, interfaces.IObjectWidget)

    def toWidgetValue(self, value):
        """Just dispatch it."""
        if value is self.field.missing_value:
            return interfaces.NO_VALUE

        retval = ObjectWidgetValue()
        retval.originalValue = value

        for name, field in zope.schema.getFieldsInOrder(self.field.schema):
            dm = zope.component.getMultiAdapter(
                (value, field), interfaces.IDataManager)
            subv = dm.query()

            if subv is interfaces.NO_VALUE:
                # look up default value
                subv = field.default
                # XXX: too many discriminators
                #adapter = zope.component.queryMultiAdapter(
                #    (context, self.request, self.view, field, widget),
                #    interfaces.IValue, name='default')
                #if adapter:
                #    value = adapter.get()

            widget = zope.component.getMultiAdapter((field, self.widget.request),
                interfaces.IFieldWidget)
            if interfaces.IFormAware.providedBy(self.widget):
                # form property required by objectwidget
                widget.form = self.widget.form
                zope.interface.alsoProvides(widget, interfaces.IFormAware)
            converter = zope.component.getMultiAdapter((field, widget),
                interfaces.IDataConverter)

            retval[name] = converter.toWidgetValue(subv)

        return retval

    def adapted_obj(self, obj):
        return self.field.schema(obj)

    def toFieldValue(self, value):
        """field value is an Object type, that provides field.schema"""
        if value is interfaces.NO_VALUE:
            return self.field.missing_value

        # try to get the original object, or if there's no chance an empty one
        obj = self.widget.getObject(value)
        obj = self.adapted_obj(obj)

        names = []
        for name, field in zope.schema.getFieldsInOrder(self.field.schema):
            if not field.readonly:
                try:
                    newvalRaw = value[name]
                except KeyError:
                    continue

                widget = zope.component.getMultiAdapter(
                    (field, self.widget.request), interfaces.IFieldWidget)
                converter = zope.component.getMultiAdapter(
                    (field, widget), interfaces.IDataConverter)
                newval = converter.toFieldValue(newvalRaw)

                dm = zope.component.getMultiAdapter(
                    (obj, field), interfaces.IDataManager)
                oldval = dm.query()
                if (oldval != newval
                        or zope.schema.interfaces.IObject.providedBy(field)):
                    dm.set(newval)
                    names.append(name)

        if names:
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(obj,
                    zope.lifecycleevent.Attributes(self.field.schema, *names)))

        # Commonly the widget context is security proxied. This method,
        # however, should return a bare object, so let's remove the
        # security proxy now that all fields have been set using the security
        # mechanism.
        return removeSecurityProxy(obj)


@zope.interface.implementer(interfaces.IObjectWidget)
class ObjectWidget(widget.Widget):

    _mode = interfaces.INPUT_MODE
    _value = interfaces.NO_VALUE
    _updating = False
    prefix = ''
    widgets = None

    def createObject(self, value):
        # keep value passed, maybe some subclasses want it
        # value here is the raw extracted from the widget's subform
        # in the form of a dict key:fieldname, value:fieldvalue
        name = getIfName(self.field.schema)
        creator = zope.component.queryMultiAdapter(
            (self.context, self.request, self.form, self),
            interfaces.IObjectFactory,
            name=name)
        if creator:
            obj = creator(value)
        else:
            # raise RuntimeError, that won't be swallowed
            raise RuntimeError(
                "No IObjectFactory adapter registered for %s" % name)

        return obj

    def getObject(self, value):
        if value.originalValue is ObjectWidget_NO_VALUE:
            # if the originalValue did not survive the roundtrip
            if self.ignoreContext:
                obj = self.createObject(value)
            else:
                # try to get the original object from the context.field_name
                dm = zope.component.getMultiAdapter(
                    (self.context, self.field), interfaces.IDataManager)
                try:
                    obj = dm.get()
                except KeyError:
                    obj = self.createObject(value)
                except AttributeError:
                    obj = self.createObject(value)
        else:
            # reuse the object that we got in toWidgetValue
            obj = value.originalValue

        if obj is None or obj == self.field.missing_value:
            # if still None, create one, otherwise following will burp
            obj = self.createObject(value)

        return obj

    @property
    def mode(self):
        """This sets the subwidgets modes."""
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode
        # ensure that we apply the new mode to the widgets
        if self.widgets:
            for w in self.widgets.values():
                w.mode = mode

    def setupFields(self):
        self.fields = field.Fields(self.field.schema)

    def setupWidgets(self):
        self.setupFields()

        self.prefix = self.name
        self.widgets = field.FieldWidgets(self, self.request, None)
        self.widgets.mode = self.mode
        # very-very important! otherwise the update() tries to set
        # RAW values as field values
        self.widgets.ignoreContext = True
        self.widgets.ignoreRequest = self.ignoreRequest
        self.widgets.update()

    def updateWidgets(self, setErrors=True):
        if self.field is None:
            raise ValueError("%r .field is None, that's a blocking point" % self)

        self.setupWidgets()

        if self._value is interfaces.NO_VALUE:
            # XXX: maybe readonly fields/widgets should be reset here to
            #      widget.mode = INPUT_MODE
            pass
            for name, widget in self.widgets.items():
                if widget.field.readonly:
                    widget.mode = interfaces.INPUT_MODE
                    widget.update()
        else:
            rawvalue = None

            for name, widget in self.widgets.items():
                if widget.mode == interfaces.DISPLAY_MODE:
                    if rawvalue is None:
                        # lazy evaluation
                        converter = zope.component.getMultiAdapter(
                            (self.field, self),
                            interfaces.IDataConverter)
                        obj = self.getObject(self._value)
                        rawvalue = converter.toWidgetValue(obj)

                    self.applyValue(widget, rawvalue[name])
                else:
                    try:
                        v = self._value[name]
                    except KeyError:
                        pass
                    else:
                        self.applyValue(widget, v)

    def applyValue(self, widget, value):
        """Validate and apply value to given widget.

        This method gets called on any ObjectWidget value change and is
        responsible for validating the given value and setup an error message.

        This is internal apply value and validation process is needed because
        nothing outside this widget does know something about our
        internal sub widgets.
        """
        if value is not interfaces.NO_VALUE:
            try:
                # convert widget value to field value
                converter = interfaces.IDataConverter(widget)
                fvalue = converter.toFieldValue(value)
                # validate field value
                zope.component.getMultiAdapter(
                    (self.context,
                     self.request,
                     self.form,
                     getattr(widget, 'field', None),
                     widget),
                    interfaces.IValidator).validate(fvalue)
                # convert field value back to widget value
                # that will probably format the value too
                widget.value = converter.toWidgetValue(fvalue)
            except (zope.schema.ValidationError, ValueError) as error:
                # on exception, setup the widget error message
                view = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     self.form, self.context), interfaces.IErrorViewSnippet)
                view.update()
                widget.error = view
                # set the wrong value as value despite it's wrong
                # we want to re-show wrong values
                widget.value = value

    def update(self):
        #very-very-nasty: skip raising exceptions in extract while we're updating
        self._updating = True
        try:
            super(ObjectWidget, self).update()
            # create the subwidgets and set their values
            self.updateWidgets(setErrors=False)
        finally:
            self._updating = False

    @property
    def value(self):
        # value (get) cannot raise an exception, then we return insane values
        try:
            self.setErrors = True
            return self.extract()
        except MultipleErrors:
            value = ObjectWidgetValue()
            if self._value is not interfaces.NO_VALUE:
                # send back the original object
                value.originalValue = self._value.originalValue

            for name, widget in self.widgets.items():
                if widget.mode != interfaces.DISPLAY_MODE:
                    value[name] = widget.value
            return value

    @value.setter
    def value(self, value):
        # This invokes updateWidgets on any value change e.g. update/extract.
        if (not isinstance(value, ObjectWidgetValue)
            and value is not interfaces.NO_VALUE):
            value = ObjectWidgetValue(value)
        self._value = value

        # create the subwidgets and set their values
        self.updateWidgets()

    def extractRaw(self, setErrors=True):
        '''See interfaces.IForm'''
        self.widgets.setErrors = setErrors
        #self.widgets.ignoreRequiredOnExtract = self.ignoreRequiredOnExtract
        data, errors = self.widgets.extractRaw()
        value = ObjectWidgetValue()
        if self._value is not interfaces.NO_VALUE:
            # send back the original object
            value.originalValue = self._value.originalValue
        value.update(data)

        return value, errors

    def extract(self, default=interfaces.NO_VALUE):
        if self.name + '-empty-marker' in self.request:
            self.updateWidgets(setErrors=False)

            # important: widget extract MUST return RAW values
            # just an extractData is WRONG here
            value, errors = self.extractRaw(setErrors=self.setErrors)

            if errors:
                # very-very-nasty: skip raising exceptions in extract
                # while we're updating -- that happens when the widget
                # is updated and update calls extract()
                if self._updating:
                    # don't rebind value, send back the original object
                    for name, widget in self.widgets.items():
                        if widget.mode != interfaces.DISPLAY_MODE:
                            value[name] = widget.value
                    return value
                raise MultipleErrors(errors)
            return value
        else:
            return default

    def render(self):
        """See z3c.form.interfaces.IWidget."""
        template = self.template
        if template is None:
            # one more discriminator than in widget.Widget
            template = zope.component.queryMultiAdapter(
                (self.context, self.request, self.form, self.field, self,
                 makeDummyObject(self.field.schema)),
                IPageTemplate, name=self.mode)
            if template is None:
                return super(ObjectWidget, self).render()
        return template(self)


######## make dummy objects providing a given interface to support
######## discriminating on field.schema

def makeDummyObject(iface):
    if iface is not None:
        @zope.interface.implementer(iface)
        class DummyObject(object):
            pass
    else:
        @zope.interface.implementer(zope.interface.Interface)
        class DummyObject(object):
            pass

    dummy = DummyObject()
    return dummy


######## special template factory that takes the field.schema into account
######## used by zcml.py

class ObjectWidgetTemplateFactory(object):
    """Widget template factory."""

    def __init__(self, filename, contentType='text/html',
                 context=None, request=None, view=None,
                 field=None, widget=None, schema=None):
        self.template = ViewPageTemplateFile(filename, content_type=contentType)
        zope.component.adapter(
            util.getSpecification(context),
            util.getSpecification(request),
            util.getSpecification(view),
            util.getSpecification(field),
            util.getSpecification(widget),
            util.getSpecification(schema))(self)
        zope.interface.implementer(IPageTemplate)(self)

    def __call__(self, context, request, view, field, widget, schema):
        return self.template


######## default adapters

@zope.interface.implementer(interfaces.IObjectFactory)
class FactoryAdapter(object):
    """Most basic-default object factory adapter"""
    zope.component.adapts(
        zope.interface.Interface, #context
        interfaces.IFormLayer,    #request
        zope.interface.Interface, #form -- but can become None easily (in tests)
        interfaces.IWidget)       #widget

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


# XXX: Probably we should offer an register factory method which allows to
# use all discriminators e.g. context, request, form, widget as optional
# arguments. But can probably do that later in a ZCML directive
def registerFactoryAdapter(for_, klass):
    """register the basic FactoryAdapter for a given interface and class"""
    name = getIfName(for_)
    class temp(FactoryAdapter):
        factory = klass
    zope.component.provideAdapter(temp, name=name)
