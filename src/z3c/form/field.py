##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Field Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.location
import zope.schema.interfaces

from z3c.form import interfaces
from z3c.form import util
from z3c.form.error import MultipleErrors
from z3c.form.widget import AfterWidgetUpdateEvent


def _initkw(keepReadOnly=(), omitReadOnly=False, **defaults):
    return keepReadOnly, omitReadOnly, defaults


class WidgetFactories(dict):

    def __init__(self):
        super().__init__()
        self.default = None

    def __getitem__(self, key):
        if key not in self and self.default:
            return self.default
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key not in self and self.default:
            return self.default
        return super().get(key, default)


class WidgetFactoryProperty:

    def __get__(self, inst, klass):
        if not hasattr(inst, '_widgetFactories'):
            inst._widgetFactories = WidgetFactories()
        return inst._widgetFactories

    def __set__(self, inst, value):
        if not hasattr(inst, '_widgetFactories'):
            inst._widgetFactories = WidgetFactories()
        inst._widgetFactories.default = value


@zope.interface.implementer(interfaces.IField)
class Field:
    """Field implementation."""

    widgetFactory = WidgetFactoryProperty()

    def __init__(self, field, name=None, prefix='', mode=None, interface=None,
                 ignoreContext=None, showDefault=None):
        self.field = field
        if name is None:
            name = field.__name__
        assert name
        self.__name__ = util.expandPrefix(prefix) + name
        self.prefix = prefix
        self.mode = mode
        if interface is None:
            interface = field.interface
        self.interface = interface
        self.ignoreContext = ignoreContext
        self.showDefault = showDefault

    def __repr__(self):
        return '<{} {!r}>'.format(self.__class__.__name__, self.__name__)


@zope.interface.implementer(interfaces.IFields)
class Fields(util.SelectionManager):
    """Field manager."""
    managerInterface = interfaces.IFields

    def __init__(self, *args, **kw):
        keepReadOnly, omitReadOnly, defaults = _initkw(**kw)

        fields = []
        for arg in args:
            if isinstance(arg, zope.interface.interface.InterfaceClass):
                for name, field in zope.schema.getFieldsInOrder(arg):
                    fields.append((name, field, arg))

            elif zope.schema.interfaces.IField.providedBy(arg):
                name = arg.__name__
                if not name:
                    raise ValueError("Field has no name")
                fields.append((name, arg, arg.interface))

            elif self.managerInterface.providedBy(arg):
                for form_field in arg.values():
                    fields.append(
                        (form_field.__name__, form_field,
                         form_field.interface))

            elif isinstance(arg, Field):
                fields.append((arg.__name__, arg, arg.interface))

            else:
                raise TypeError("Unrecognized argument type", arg)

        super().__init__()
        for name, field, iface in fields:
            if isinstance(field, Field):
                form_field = field
            else:
                if field.readonly:
                    if omitReadOnly and (name not in keepReadOnly):
                        continue
                customDefaults = defaults.copy()
                if iface is not None:
                    customDefaults['interface'] = iface
                form_field = Field(field, **customDefaults)
                name = form_field.__name__

            if name in self:
                raise ValueError("Duplicate name", name)

            self[name] = form_field

    def select(self, *names, **kwargs):
        """See interfaces.IFields"""
        prefix = kwargs.pop('prefix', None)
        interface = kwargs.pop('interface', None)
        assert len(kwargs) == 0
        if prefix:
            names = [util.expandPrefix(prefix) + name for name in names]
        mapping = self
        if interface is not None:
            mapping = {field.field.__name__: field
                       for field in self.values()
                       if field.field.interface is interface}
        return self.__class__(*[mapping[name] for name in names])

    def omit(self, *names, **kwargs):
        """See interfaces.IFields"""
        prefix = kwargs.pop('prefix', None)
        interface = kwargs.pop('interface', None)
        assert len(kwargs) == 0
        if prefix:
            names = [util.expandPrefix(prefix) + name for name in names]
        return self.__class__(
            *[field for name, field in self.items()
              if not ((name in names and interface is None) or
                      (field.field.interface is interface and
                       field.field.__name__ in names))])


@zope.interface.implementer_only(interfaces.IWidgets)
class FieldWidgets(util.Manager):
    """Widget manager for IFieldWidget."""

    zope.component.adapts(
        interfaces.IFieldsForm,
        interfaces.IFormLayer,
        zope.interface.Interface)

    prefix = 'widgets.'
    mode = interfaces.INPUT_MODE
    errors = ()
    hasRequiredFields = False
    ignoreContext = False
    ignoreRequest = False
    ignoreReadonly = False
    ignoreRequiredOnExtract = False
    setErrors = True

    def __init__(self, form, request, content):
        super().__init__()
        self.form = form
        self.request = request
        self.content = content

    def validate(self, data):
        fields = self.form.fields.values()

        # Step 1: Collect the data for the various schemas
        schemaData = {}
        for field in fields:
            schema = field.interface
            if schema is None:
                continue

            fieldData = schemaData.setdefault(schema, {})
            if field.__name__ in data:
                fieldData[field.field.__name__] = data[field.__name__]

        # Step 2: Validate the individual schemas and collect errors
        errors = ()
        content = self.content
        if self.ignoreContext:
            content = None
        for schema, fieldData in schemaData.items():
            validator = zope.component.getMultiAdapter(
                (content, self.request, self.form, schema, self),
                interfaces.IManagerValidator)
            errors += validator.validate(fieldData)

        return errors

    def update(self):
        """See interfaces.IWidgets"""
        # Create a unique prefix.
        prefix = util.expandPrefix(self.form.prefix)
        prefix += util.expandPrefix(self.prefix)
        # Walk through each field, making a widget out of it.
        d = {}
        d.update(self)
        for field in self.form.fields.values():
            # Step 0. Determine whether the context should be ignored.
            ignoreContext = self.ignoreContext
            if field.ignoreContext is not None:
                ignoreContext = field.ignoreContext
            # Step 1: Determine the mode of the widget.
            mode = self.mode
            if field.mode is not None:
                mode = field.mode
            elif field.field.readonly and not self.ignoreReadonly:
                mode = interfaces.DISPLAY_MODE
            elif not ignoreContext:
                # If we do not have enough permissions to write to the
                # attribute, then switch to display mode.
                dm = zope.component.getMultiAdapter(
                    (self.content, field.field), interfaces.IDataManager)
                if not dm.canWrite():
                    mode = interfaces.DISPLAY_MODE
            # Step 2: Get the widget for the given field.
            shortName = field.__name__
            newWidget = True
            if shortName in self:
                # reuse existing widget
                widget = d[shortName]
                newWidget = False
            elif field.widgetFactory.get(mode) is not None:
                factory = field.widgetFactory.get(mode)
                widget = factory(field.field, self.request)
            else:
                widget = zope.component.getMultiAdapter(
                    (field.field, self.request), interfaces.IFieldWidget)
            # Step 3: Set the prefix for the widget
            widget.name = prefix + shortName
            widget.id = (prefix + shortName).replace('.', '-')
            # Step 4: Set the context
            widget.context = self.content
            # Step 5: Set the form
            widget.form = self.form
            # Optimization: Set both interfaces here, rather in step 4 and 5:
            # ``alsoProvides`` is quite slow
            zope.interface.alsoProvides(
                widget, interfaces.IContextAware, interfaces.IFormAware)
            # Step 6: Set some variables
            widget.ignoreContext = ignoreContext
            widget.ignoreRequest = self.ignoreRequest
            if field.showDefault is not None:
                widget.showDefault = field.showDefault
            # Step 7: Set the mode of the widget
            widget.mode = mode
            # Step 8: Update the widget
            widget.update()
            zope.event.notify(AfterWidgetUpdateEvent(widget))
            # Step 9: Add the widget to the manager
            if widget.required:
                self.hasRequiredFields = True
            if newWidget:
                d[shortName] = widget
                zope.location.locate(widget, self, shortName)
        self.create_according_to_list(d, self.form.fields.keys())

    def _extract(self, returnRaw=False):
        data = {}
        errors = ()
        for name, widget in self.items():
            if widget.mode == interfaces.DISPLAY_MODE:
                continue
            value = widget.field.missing_value
            try:
                widget.setErrors = self.setErrors
                raw = widget.extract()
                if raw is not interfaces.NO_VALUE:
                    value = interfaces.IDataConverter(widget).toFieldValue(raw)
                widget.ignoreRequiredOnValidation = (
                    self.ignoreRequiredOnExtract)
                zope.component.getMultiAdapter(
                    (self.content,
                     self.request,
                     self.form,
                     getattr(widget, 'field', None),
                     widget),
                    interfaces.IValidator).validate(value)
            except (zope.interface.Invalid,
                    ValueError, MultipleErrors) as error:
                view = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     self.form, self.content), interfaces.IErrorViewSnippet)
                view.update()
                if self.setErrors:
                    widget.error = view
                errors += (view,)
            else:
                name = widget.__name__
                if returnRaw:
                    data[name] = raw
                else:
                    data[name] = value
        for error in self.validate(data):
            view = zope.component.getMultiAdapter(
                (error, self.request, None, None, self.form, self.content),
                interfaces.IErrorViewSnippet)
            view.update()
            errors += (view,)
        if self.setErrors:
            self.errors = errors
        return data, errors

    def extract(self):
        """See interfaces.IWidgets"""
        return self._extract(returnRaw=False)

    def extractRaw(self):
        """See interfaces.IWidgets"""
        return self._extract(returnRaw=True)

    def copy(self):
        """See interfaces.ISelectionManager"""
        clone = self.__class__(self.form, self.request, self.content)
        super(self.__class__, clone).update(self)
        return clone
