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
"""Ordered-Selection Widget Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from zope.i18n import translate

from z3c.form import interfaces, widget
from z3c.form.browser.widget import HTMLSelectWidget


class OrderedSelectWidget(HTMLSelectWidget, widget.SequenceWidget):
    """Ordered-Select widget implementation."""
    zope.interface.implementsOnly(interfaces.IOrderedSelectWidget)

    size = 5
    multiple = u'multiple'
    items = ()
    selectedItems = ()

    def getItem(self, term, count=0):
        id = '%s-%i' % (self.id, count)
        content = term.token
        if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
            content = translate(
                term.title, context=self.request, default=term.title)
        return {'id':id, 'value':term.token, 'content':content}

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(OrderedSelectWidget, self).update()
        self.items = [
            self.getItem(term, count)
            for count, term in enumerate(self.terms)]
        self.selectedItems = [
            self.getItem(self.terms.getTermByToken(token), count)
            for count, token in enumerate(self.value)]


@zope.component.adapter(zope.schema.interfaces.ISequence, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def OrderedSelectFieldWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return widget.FieldWidget(field, OrderedSelectWidget(request))

@zope.component.adapter(
    zope.schema.interfaces.ISequence, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def SequenceSelectFieldWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return zope.component.getMultiAdapter(
        (field, field.value_type, request), interfaces.IFieldWidget)


@zope.component.adapter(zope.schema.interfaces.ISequence,
    zope.schema.interfaces.IChoice, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def SequenceChoiceSelectFieldWidget(field, value_type, request):
    """IFieldWidget factory for SelectWidget."""
    return OrderedSelectFieldWidget(field, request)
