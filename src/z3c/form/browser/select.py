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

from z3c.form import interfaces, widget
from z3c.form.i18n import MessageFactory as _


class SelectWidget(widget.SequenceWidget):
    """Select widget implementation."""

    zope.interface.implementsOnly(interfaces.ISelectWidget)

    css = u'selectWidget'
    size = 1
    multiple = None
    items = ()

    noValueMessage = _('no value')

    # Internal attributes
    _adapterValueAttributes = widget.SequenceWidget._adapterValueAttributes + \
        ('noValueMessage',)

    def isSelected(self, term):
        return term.token in self.value

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(SelectWidget, self).update()
        self.items = []
        if not self.required and self.multiple is None:
            self.items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': self.noValueMessage,
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
    return widget.FieldWidget(field, SelectWidget(request))


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
