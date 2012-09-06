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
"""Text Widget Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from zope.i18n import translate

from z3c.form import interfaces
from z3c.form.i18n import MessageFactory as _
from z3c.form.widget import SequenceWidget, FieldWidget
from z3c.form.browser import widget


class SelectWidget(widget.HTMLSelectWidget, SequenceWidget):
    """Select widget implementation."""
    zope.interface.implementsOnly(interfaces.ISelectWidget)

    klass = u'select-widget'
    css = u'select'
    prompt = False

    noValueMessage = _('no value')
    promptMessage = _('select a value ...')

    # Internal attributes
    _adapterValueAttributes = SequenceWidget._adapterValueAttributes + \
        ('noValueMessage', 'promptMessage', 'prompt')

    def isSelected(self, term):
        return term.token in self.value

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(SelectWidget, self).update()
        widget.addFieldClass(self)

    @property
    def items(self):
        if self.terms is None:  # update() has not been called yet
            return ()
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })

        ignored = set(self.value)

        def addItem(idx, term, prefix=''):
            selected = self.isSelected(term)
            if selected:
                ignored.remove(term.token)
            id = '%s-%s%i' % (self.id, prefix, idx)
            content = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                content = translate(
                    term.title, context=self.request, default=term.title)
            items.append(
                {'id': id, 'value': term.token, 'content': content,
                 'selected': selected})

        for idx, term in enumerate(self.terms):
            addItem(idx, term)

        if ignored:
            # some values are not displayed, probably they went away from the vocabulary
            for idx, token in enumerate(sorted(ignored)):
                try:
                    term = self.terms.getTermByToken(token)
                except LookupError:
                    # just in case the term really went away
                    continue

                addItem(idx, term, prefix='missing-')
        return items


@zope.component.adapter(zope.schema.interfaces.IChoice, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def ChoiceWidgetDispatcher(field, request):
    """Dispatch widget for IChoice based also on its source."""
    return zope.component.getMultiAdapter((field, field.vocabulary, request),
                                          interfaces.IFieldWidget)


@zope.component.adapter(zope.schema.interfaces.IChoice,
                        zope.interface.Interface,
                        interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def SelectFieldWidget(field, source, request=None):
    """IFieldWidget factory for SelectWidget."""
    # BBB: emulate our pre-2.0 signature (field, request)
    if request is None:
        real_request = source
    else:
        real_request = request
    return FieldWidget(field, SelectWidget(real_request))


@zope.component.adapter(
    zope.schema.interfaces.IUnorderedCollection, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def CollectionSelectFieldWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    widget = zope.component.getMultiAdapter((field, field.value_type, request),
        interfaces.IFieldWidget)
    widget.size = 5
    widget.multiple = 'multiple'
    return widget


@zope.component.adapter(
    zope.schema.interfaces.IUnorderedCollection,
    zope.schema.interfaces.IChoice, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def CollectionChoiceSelectFieldWidget(field, value_type, request):
    """IFieldWidget factory for SelectWidget."""
    return SelectFieldWidget(field, None, request)
