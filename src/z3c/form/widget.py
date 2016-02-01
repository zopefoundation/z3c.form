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
"""Widget Framework Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import json

import zope.interface
import zope.component
import zope.location
import zope.schema.interfaces
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
from zope.pagetemplate.interfaces import IPageTemplate
from zope.schema.fieldproperty import FieldProperty

from z3c.form import interfaces, util, value

PLACEHOLDER = object()

StaticWidgetAttribute = value.StaticValueCreator(
    discriminators=('context', 'request', 'view', 'field', 'widget')
    )
ComputedWidgetAttribute = value.ComputedValueCreator(
    discriminators=('context', 'request', 'view', 'field', 'widget')
    )


@zope.interface.implementer(interfaces.IWidget)
class Widget(zope.location.Location):
    """Widget base class."""

    # widget specific attributes
    name = FieldProperty(interfaces.IWidget['name'])
    label = FieldProperty(interfaces.IWidget['label'])
    mode = FieldProperty(interfaces.IWidget['mode'])
    required = FieldProperty(interfaces.IWidget['required'])
    error = FieldProperty(interfaces.IWidget['error'])
    value = FieldProperty(interfaces.IWidget['value'])
    template = None
    layout = None
    ignoreRequest = FieldProperty(interfaces.IWidget['ignoreRequest'])
    ignoreRequiredOnValidation = FieldProperty(
        interfaces.IWidget['ignoreRequiredOnValidation'])
    setErrors = FieldProperty(interfaces.IWidget['setErrors'])
    showDefault = FieldProperty(interfaces.IWidget['showDefault'])

    # The following attributes are for convenience. They are declared in
    # extensions to the simple widget.

    # See ``interfaces.IContextAware``
    context = None
    ignoreContext = False
    # See ``interfaces.IFormAware``
    form = None
    # See ``interfaces.IFieldWidget``
    field = None

    # Internal attributes
    _adapterValueAttributes = ('label', 'name', 'required', 'title')

    def __init__(self, request):
        self.request = request

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Step 1: Determine the value.
        value = interfaces.NO_VALUE
        lookForDefault = False
        # Step 1.1: If possible, get a value from the request
        if not self.ignoreRequest:
            #at this turn we do not need errors to be set on widgets
            #errors will be set when extract gets called from form.extractData
            self.setErrors = False
            widget_value = self.extract()
            if widget_value is not interfaces.NO_VALUE:
                # Once we found the value in the request, it takes precendence
                # over everything and nothing else has to be done.
                self.value = widget_value
                value = PLACEHOLDER
        # Step 1.2: If we have a widget with a field and we have no value yet,
        #           we have some more possible locations to get the value
        if (interfaces.IFieldWidget.providedBy(self) and
            value is interfaces.NO_VALUE and
            value is not PLACEHOLDER):
            # Step 1.2.1: If the widget knows about its context and the
            #              context is to be used to extract a value, get
            #              it now via a data manager.
            if (interfaces.IContextAware.providedBy(self) and
                not self.ignoreContext):
                value = zope.component.getMultiAdapter(
                    (self.context, self.field),
                    interfaces.IDataManager).query()
            # Step 1.2.2: If we still do not have a value, we can always use
            #             the default value of the field, if set
            # NOTE: It should check field.default is not missing_value, but
            # that requires fixing zope.schema first
            # We get a clone of the field with the context binded
            field = self.field.bind(self.context)

            if value is field.missing_value or value is interfaces.NO_VALUE:
                default_value = field.default
                if default_value is not None and self.showDefault:
                    value = field.default
                    lookForDefault = True

        # Step 1.3: If we still have not found a value, then we try to get it
        #           from an attribute value
        if ((value is interfaces.NO_VALUE or lookForDefault)
            and self.showDefault):
            adapter = zope.component.queryMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.IValue, name='default')
            if adapter:
                value = adapter.get()
        # Step 1.4: Convert the value to one that the widget can understand
        if value not in (interfaces.NO_VALUE, PLACEHOLDER):
            converter = interfaces.IDataConverter(self)
            self.value = converter.toWidgetValue(value)
        # Step 2: Update selected attributes
        for attrName in self._adapterValueAttributes:
            # only allow to set values for known attributes
            if hasattr(self, attrName):
                value = zope.component.queryMultiAdapter(
                    (self.context, self.request, self.form, self.field, self),
                    interfaces.IValue, name=attrName)
                if value is not None:
                    setattr(self, attrName, value.get())

    def extract(self, default=interfaces.NO_VALUE):
        """See z3c.form.interfaces.IWidget."""
        return self.request.get(self.name, default)

    def render(self):
        """Render the plain widget without additional layout"""
        template = self.template
        if template is None:
            template = zope.component.getMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                IPageTemplate, name=self.mode)
        return template(self)

    def json_data(self):
        return {
            'mode': self.mode,
            'error': self.error.message if self.error else '',
            'value': self.value,
            'required': self.required,
            'name': self.name,
            'id': getattr(self, 'id', ''),
            'type': 'text',
            'label': self.label or ''
        }

    def __call__(self):
        """Get and return layout template which is calling widget/render"""
        layout = self.layout
        if layout is None:
            layout = zope.component.getMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.IWidgetLayoutTemplate, name=self.mode)
        return layout(self)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


@zope.interface.implementer(interfaces.ISequenceWidget)
class SequenceWidget(Widget):
    """Term based sequence widget base.

    The sequence widget is used for select items from a sequence. Don't get
    confused, this widget does support to choose one or more values from a
    sequence. The word sequence is not used for the schema field, it's used
    for the values where this widget can choose from.

    This widget base class is used for build single or sequence values based
    on a sequence which is in most use case a collection. e.g.
    IList of IChoice for sequence values or IChoice for single values.

    See also the MultiWidget for build sequence values based on none collection
    based values. e.g. IList of ITextLine
    """

    value = ()
    terms = None

    noValueToken = '--NOVALUE--'

    @property
    def displayValue(self):
        value = []
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.noValueToken:
                continue
            try:
                term = self.terms.getTermByToken(token)
            except LookupError:
                # silently ignore missing tokens, because INPUT_MODE and
                # HIDDEN_MODE does that too
                continue
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                value.append(translate(
                    term.title, context=self.request, default=term.title))
            else:
                value.append(term.value)
        return value

    def updateTerms(self):
        if self.terms is None:
            self.terms = zope.component.getMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.ITerms)
        return self.terms

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Create terms first, since we need them for the generic update.
        self.updateTerms()
        super(SequenceWidget, self).update()

    def extract(self, default=interfaces.NO_VALUE):
        """See z3c.form.interfaces.IWidget."""
        if (self.name not in self.request and
            self.name + '-empty-marker' in self.request):
            return []
        value = self.request.get(self.name, default)
        if value != default:
            if not isinstance(value, (tuple, list)):
                value = (value,)
            # do some kind of validation, at least only use existing values
            for token in value:
                if token == self.noValueToken:
                    continue
                try:
                    self.terms.getTermByToken(token)
                except LookupError:
                    return default
        return value

    def json_data(self):
        data = super(SequenceWidget, self).json_data()
        data['type'] = 'sequence'
        return data


@zope.interface.implementer(interfaces.IMultiWidget)
class MultiWidget(Widget):
    """None Term based sequence widget base.

    The multi widget is used for ITuple, IList or IDict if no other widget is
    defined.

    Some IList, ITuple or IDict are using another specialized widget if they can
    choose from a collection. e.g. a IList of IChoice. The base class of such
    widget is the ISequenceWidget.

    This widget can handle none collection based sequences and offers add or
    remove values to or from the sequence. Each sequence value get rendered by
    it's own relevant widget. e.g. IList of ITextLine or ITuple of IInt

    Each widget get rendered within a sequence value. This means each internal
    widget will represent one value from the multi widget value. Based on the
    nature of this (sub) widget setup the internal widget do not have a real
    context and can't get bound to it. This makes it impossible to use a
    sequence of collection where the collection needs a context. But that
    should not be a problem since sequence of collection will use the
    SequenceWidget as base.
    """

    allowAdding = True
    allowRemoving = True

    widgets = None
    key_widgets = None
    _value = None
    _widgets_updated = False

    _mode = FieldProperty(interfaces.IWidget['mode'])

    def __init__(self, request):
        super(MultiWidget, self).__init__(request)
        self.widgets = []
        self.key_widgets = []
        self._value = []

    @property
    def is_dict(self):
        return getattr(self.field, 'key_type', None) is not None

    @property
    def counterName(self):
        return '%s.count' % self.name

    @property
    def counterMarker(self):
        # this get called in render from the template and contains always the
        # right amount of widgets we use.
        return '<input type="hidden" name="%s" value="%d" />' % (
            self.counterName, len(self.widgets))

    @property
    def mode(self):
        """This sets the subwidgets modes."""
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode
        # ensure that we apply the new mode to the widgets
        for w in self.widgets:
            w.mode = mode
        for w in self.key_widgets:
            if w is not None:
                w.mode = mode

    def getWidget(self, idx, prefix=None, type_field="value_type"):
        """Setup widget based on index id with or without value."""
        valueType = getattr(self.field, type_field)
        widget = zope.component.getMultiAdapter(
            (valueType, self.request), interfaces.IFieldWidget)
        self.setName(widget, idx, prefix)
        widget.mode = self.mode
        #set widget.form (objectwidget needs this)
        if interfaces.IFormAware.providedBy(self):
            widget.form = self.form
            zope.interface.alsoProvides(
                widget, interfaces.IFormAware)
        widget.update()
        return widget

    def setName(self, widget, idx, prefix=None):
        names = lambda id: [str(n) for n in [id]+[prefix, idx] if n is not None]
        widget.name = '.'.join([str(self.name)]+names(None))
        widget.id = '-'.join([str(self.id)]+names(None))

    def appendAddingWidget(self):
        """Simply append a new empty widget with correct (counter) name."""
        # since we start with idx 0 (zero) we can use the len as next idx
        idx = len(self.widgets)
        widget = self.getWidget(idx)
        self.widgets.append(widget)
        if self.is_dict:
            widget = self.getWidget(idx, "key", "key_type")
            self.key_widgets.append(widget)
        else:
            self.key_widgets.append(None)

    def removeWidgets(self, names):
        """
        :param names: list of widget.name to remove from the value
        :return: None
        """
        zipped = list(zip(self.key_widgets, self.widgets))
        self.key_widgets = [k for k, v in zipped if v.name not in names]
        self.widgets = [v for k, v in zipped if v.name not in names]
        if self.is_dict:
            self.value = [(k.value, v.value)
                          for k, v in zip(self.key_widgets, self.widgets)]
        else:
            self.value = [widget.value for widget in self.widgets]

    def applyValue(self, widget, value=interfaces.NO_VALUE):
        """Validate and apply value to given widget.

        This method gets called on any multi widget value change and is
        responsible for validating the given value and setup an error message.

        This is internal apply value and validation process is needed because
        nothing outside this multi widget does know something about our
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
                # convert field value to widget value
                widget.value = converter.toWidgetValue(fvalue)
            except (zope.schema.ValidationError, ValueError) as error:
                # on exception, setup the widget error message
                view = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     self.form, self.context), interfaces.IErrorViewSnippet)
                view.update()
                widget.error = view
                # set the wrong value as value
                widget.value = value

    def updateWidgets(self):
        """Setup internal widgets based on the value_type for each value item.
        """
        oldLen = len(self.widgets)
        # Ensure at least min_length widgets are shown
        if (zope.schema.interfaces.IMinMaxLen.providedBy(self.field) and
            self.mode == interfaces.INPUT_MODE and self.allowAdding and
            oldLen < self.field.min_length):
            oldLen = self.field.min_length
        self.widgets = []
        self.key_widgets = []
        keys = set()
        idx = 0
        if self.value:
            if self.is_dict:
                # mainly sorting for testing reasons
                items = self.value
            else:
                items = zip([None]*len(self.value), self.value)
            for key, v in items:
                widget = self.getWidget(idx)
                self.applyValue(widget, v)
                self.widgets.append(widget)

                if self.is_dict:
                    # This is needed, since sequence widgets (such as for
                    # choices) return lists of values.
                    hash_key = key if not isinstance(key, list) else tuple(key)
                    widget = self.getWidget(idx, "key", "key_type")
                    self.applyValue(widget, key)
                    if hash_key in keys and widget.error is None:
                        error = zope.interface.Invalid(u'Duplicate key')
                        view = zope.component.getMultiAdapter(
                            (error, self.request, widget, widget.field,
                             self.form, self.context),
                            interfaces.IErrorViewSnippet)
                        view.update()
                        widget.error = view
                    self.key_widgets.append(widget)
                    keys.add(hash_key)
                else:
                    #makes the template easier to have this the same length
                    self.key_widgets.append(None)
                idx += 1
        missing = oldLen - len(self.widgets)
        if missing > 0:
            # add previous existing new added widgtes
            for i in range(missing):
                widget = self.getWidget(idx)
                self.widgets.append(widget)
                if self.is_dict:
                    widget = self.getWidget(idx, "key", "key_type")
                    self.key_widgets.append(widget)
                else:
                    self.key_widgets.append(None)
                idx += 1
        self._widgets_updated = True

    def updateAllowAddRemove(self):
        """Update the allowAdding/allowRemoving attributes
        basing on field constraints and current number of widgets
        """
        if not zope.schema.interfaces.IMinMaxLen.providedBy(self.field):
            return
        max_length = self.field.max_length
        min_length = self.field.min_length
        num_items = len(self.widgets)
        self.allowAdding = bool((not max_length) or (num_items < max_length))
        self.allowRemoving = bool(num_items and (num_items > min_length))

    @property
    def value(self):
        """This invokes updateWidgets on any value change e.g. update/extract."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        # ensure that we apply our new values to the widgets
        self.updateWidgets()

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Ensure that updateWidgets is called.
        super(MultiWidget, self).update()
        if not self._widgets_updated:
            self.updateWidgets()

    def extract(self, default=interfaces.NO_VALUE):
        # This method is responsible to get the widgets value based on the
        # request and nothing else.
        # We have to setup the widgets for extract their values, because we
        # don't know how to do this for every field without the right widgets.
        # Later we will setup the widgets based on this values. This is needed
        # because we probably set a new value in the form for our multi widget
        # which would generate a different set of widgets.
        if self.request.get(self.counterName) is None:
            # counter marker not found
            return interfaces.NO_VALUE
        counter = int(self.request.get(self.counterName, 0))
        # extract value for existing widgets
        values = []
        append = values.append
        # extract value for existing widgets
        for idx in range(counter):
            widget = self.getWidget(idx)
            if self.is_dict:
                key_widget = self.getWidget(idx, "key", "key_type")
                append((key_widget.value, widget.value))
            else:
                append(widget.value)
        return values

    def json_data(self):
        data = super(MultiWidget, self).json_data()
        data['widgets'] = [widget.json_data() for widget in self.widgets]
        data['type'] = 'multi'
        return data

def FieldWidget(field, widget):
    """Set the field for the widget."""
    widget.field = field
    if not interfaces.IFieldWidget.providedBy(widget):
        zope.interface.alsoProvides(widget, interfaces.IFieldWidget)
    # Initial values are set. They can be overridden while updating the widget
    # itself later on.
    widget.name = field.__name__
    widget.id = field.__name__.replace('.', '-')
    widget.label = field.title
    widget.required = field.required
    return widget


class WidgetTemplateFactory(object):
    """Widget template factory."""

    def __init__(self, filename, contentType='text/html',
                 context=None, request=None, view=None,
                 field=None, widget=None):
        self.template = ViewPageTemplateFile(filename, content_type=contentType)
        zope.component.adapter(
            util.getSpecification(context),
            util.getSpecification(request),
            util.getSpecification(view),
            util.getSpecification(field),
            util.getSpecification(widget))(self)
        zope.interface.implementer(IPageTemplate)(self)

    def __call__(self, context, request, view, field, widget):
        return self.template


class WidgetLayoutFactory(object):
    """Widget layout template factory."""

    def __init__(self, filename, contentType='text/html',
                 context=None, request=None, view=None,
                 field=None, widget=None):
        self.template = ViewPageTemplateFile(filename, content_type=contentType)
        zope.component.adapter(
            util.getSpecification(context),
            util.getSpecification(request),
            util.getSpecification(view),
            util.getSpecification(field),
            util.getSpecification(widget))(self)
        zope.interface.implementer(interfaces.IWidgetLayoutTemplate)(self)

    def __call__(self, context, request, view, field, widget):
        return self.template


@zope.interface.implementer(interfaces.IWidgetEvent)
class WidgetEvent(object):

    def __init__(self, widget):
        self.widget = widget

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.widget)


@zope.interface.implementer_only(interfaces.IAfterWidgetUpdateEvent)
class AfterWidgetUpdateEvent(WidgetEvent):
    pass
