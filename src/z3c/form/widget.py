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

import zope.interface
import zope.component
import zope.location
import zope.schema.interfaces
from zope.pagetemplate.interfaces import IPageTemplate
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.i18n import translate
from zope.schema.fieldproperty import FieldProperty

from z3c.form import interfaces, util, value

PLACEHOLDER = object()

StaticWidgetAttribute = value.StaticValueCreator(
    discriminators = ('context', 'request', 'view', 'field', 'widget')
    )
ComputedWidgetAttribute = value.ComputedValueCreator(
    discriminators = ('context', 'request', 'view', 'field', 'widget')
    )


class Widget(zope.location.Location):
    """Widget base class."""

    zope.interface.implements(interfaces.IWidget)

    # widget specific attributes
    name = FieldProperty(interfaces.IWidget['name'])
    label = FieldProperty(interfaces.IWidget['label'])
    mode = FieldProperty(interfaces.IWidget['mode'])
    required = FieldProperty(interfaces.IWidget['required'])
    error = FieldProperty(interfaces.IWidget['error'])
    value = FieldProperty(interfaces.IWidget['value'])
    template = None
    ignoreRequest = FieldProperty(interfaces.IWidget['ignoreRequest'])

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
    _adapterValueAttributes = ('label', 'name')

    def __init__(self, request):
        self.request = request

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Step 1: Determine the value.
        value = interfaces.NOVALUE
        lookForDefault = False
        # Step 1.1: If possible, get a value from the request
        if not self.ignoreRequest:
            widget_value = self.extract()
            if widget_value is not interfaces.NOVALUE:
                # Once we found the value in the request, it takes precendence
                # over everything and nothing else has to be done.
                self.value = widget_value
                value = PLACEHOLDER
        # Step 1.2: If we have a widget with a field and we have no value yet,
        #           we have some more possible locations to get the value
        if (interfaces.IFieldWidget.providedBy(self) and
            value is interfaces.NOVALUE and
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
            #             the default value of the field, id set
            # NOTE: It should check field.default is not missing_value, but
            # that requires fixing zope.schema first
            if ((value is self.field.missing_value or
                 value is interfaces.NOVALUE) and
                self.field.default is not None):
                value = self.field.default
                lookForDefault = True
        # Step 1.3: If we still have not found a value, then we try to get it
        #           from an attribute value
        if value is interfaces.NOVALUE or lookForDefault:
            adapter = zope.component.queryMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.IValue, name='default')
            if adapter:
                value = adapter.get()
        # Step 1.4: Convert the value to one that the widget can understand
        if value not in (interfaces.NOVALUE, PLACEHOLDER):
            converter = interfaces.IDataConverter(self)
            self.value = converter.toWidgetValue(value)
        # Step 2: Update selected attributes
        for attrName in self._adapterValueAttributes:
            value = zope.component.queryMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.IValue, name=attrName)
            if value is not None:
                setattr(self, attrName, value.get())

    def render(self):
        """See z3c.form.interfaces.IWidget."""
        template = self.template
        if template is None:
            template = zope.component.getMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                IPageTemplate, name=self.mode)
        return template(self)

    def extract(self, default=interfaces.NOVALUE):
        """See z3c.form.interfaces.IWidget."""
        return self.request.get(self.name, default)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class SequenceWidget(Widget):
    """Sequence widget."""

    zope.interface.implements(interfaces.ISequenceWidget)

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
            term = self.terms.getTermByToken(token)
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

    def extract(self, default=interfaces.NOVALUE):
        """See z3c.form.interfaces.IWidget."""
        if (self.name not in self.request and
            self.name+'-empty-marker' in self.request):
            return []
        value = self.request.get(self.name, default)
        if value != default:
            for token in value:
                if token == self.noValueToken:
                    continue
                try:
                    self.terms.getTermByToken(token)
                except LookupError:
                    return default
        return value


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


class WidgetEvent(object):
    zope.interface.implements(interfaces.IWidgetEvent)

    def __init__(self, widget):
        self.widget = widget

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.widget)

class AfterWidgetUpdateEvent(WidgetEvent):
    zope.interface.implementsOnly(interfaces.IAfterWidgetUpdateEvent)
