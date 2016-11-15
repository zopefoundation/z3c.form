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
from zope.schema import vocabulary
from zope.i18n import translate

from z3c.form import interfaces, term, util
from z3c.form.widget import SequenceWidget, FieldWidget
from z3c.form.browser import widget


@zope.interface.implementer_only(interfaces.ICheckBoxWidget)
class CheckBoxWidget(widget.HTMLInputWidget, SequenceWidget):
    """Input type checkbox widget implementation."""

    klass = u'checkbox-widget'
    css = u'checkbox'
    items = ()

    def isChecked(self, term):
        return term.token in self.value

    @property
    def items(self):
        if self.terms is not None and len(self.terms) > 0:
            terms = self.terms
        elif hasattr(self, 'source'):
            terms = [self.source.getTermByToken(token)
                     for token in self.value or []
                     if token != self.noValueToken]
        else:
            terms = []
            for token in self.value:
                if token == self.noValueToken:
                    return []
                try:
                    terms.append(self.terms.getTermByToken(token))
                except LookupError:
                    return []

        items = []
        for count, term in enumerate(terms):
            checked = self.isChecked(term)
            item_id = '%s-%i' % (self.id, count)
            label = self.get_label(term)
            items.append({
                'id': item_id,
                'name': self.name + ':list',
                'value': term.token,
                'label': label,
                'checked': checked})

        return items

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(CheckBoxWidget, self).update()
        widget.addFieldClass(self)

    def json_data(self):
        data = super(CheckBoxWidget, self).json_data()
        data['options'] = list(self.items)
        data['type'] = 'check'
        return data


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def CheckBoxFieldWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    return FieldWidget(field, CheckBoxWidget(request))


@zope.interface.implementer_only(interfaces.ISingleCheckBoxWidget)
class SingleCheckBoxWidget(CheckBoxWidget):
    """Single Input type checkbox widget implementation."""

    klass = u'single-checkbox-widget'

    def updateTerms(self):
        if self.terms is None:
            self.terms = term.Terms()
            self.terms.terms = vocabulary.SimpleVocabulary((
                vocabulary.SimpleTerm('selected', 'selected',
                                      self.label or self.field.title),))
        return self.terms


@zope.component.adapter(zope.schema.interfaces.IBool, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def SingleCheckBoxFieldWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    widget = FieldWidget(field, SingleCheckBoxWidget(request))
    widget.label = u''  # don't show the label twice
    return widget
