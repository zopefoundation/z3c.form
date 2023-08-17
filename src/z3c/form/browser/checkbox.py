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
from zope.schema import vocabulary

from z3c.form import interfaces
from z3c.form import term
from z3c.form import util
from z3c.form.browser import widget
from z3c.form.widget import FieldWidget
from z3c.form.widget import SequenceWidget


@zope.interface.implementer_only(interfaces.ICheckBoxWidget)
class CheckBoxWidget(widget.HTMLInputWidget, SequenceWidget):
    """Input type checkbox widget implementation."""

    klass = 'checkbox-widget'
    css = 'checkbox'

    def isChecked(self, term):
        return term.token in self.value

    @property
    def items(self):
        if self.terms is None:
            return ()
        items = []
        for count, term_ in enumerate(self.terms):
            checked = self.isChecked(term_)
            id = '%s-%i' % (self.id, count)
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term_):
                label = translate(term_.title, context=self.request,
                                  default=term_.title)
            else:
                label = util.toUnicode(term_.value)
            items.append(
                {'id': id, 'name': self.name + ':list', 'value': term_.token,
                 'label': label, 'checked': checked})
        return items

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super().update()
        widget.addFieldClass(self)

    def json_data(self):
        data = super().json_data()
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

    klass = 'single-checkbox-widget'

    def updateTerms(self):
        if self.terms is None:
            self.terms = term.Terms()
            self.terms.terms = vocabulary.SimpleVocabulary((
                vocabulary.SimpleTerm('selected', 'selected',
                                      self.label or self.field.title), ))
        return self.terms


@zope.component.adapter(zope.schema.interfaces.IBool, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def SingleCheckBoxFieldWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    widget = FieldWidget(field, SingleCheckBoxWidget(request))
    widget.label = ''  # don't show the label twice
    return widget
