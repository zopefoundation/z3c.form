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
    items = ()
    prompt = False

    noValueMessage = _('no value')
    promptMessage = _('select a value ...')

    # Internal attributes
    _adapterValueAttributes = SequenceWidget._adapterValueAttributes + \
        ('noValueMessage', 'promptMessage')

    def isSelected(self, term):
        return term.token in self.value

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(SelectWidget, self).update()
        widget.addFieldClass(self)
        self.items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            self.items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })
        for count, term in enumerate(self.terms):
            selected = self.isSelected(term)
            id = '%s-%i' % (self.id, count)
            content = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                content = translate(
                    term.title, context=self.request, default=term.title)
            self.items.append(
                {'id':id, 'value':term.token, 'content':content,
                 'selected':selected})


@zope.component.adapter(zope.schema.interfaces.IChoice, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def SelectFieldWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return FieldWidget(field, SelectWidget(request))


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
    return SelectFieldWidget(field, request)
