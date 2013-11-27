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
from zope.pagetemplate.interfaces import IPageTemplate

from z3c.form import interfaces, util
from z3c.form.widget import SequenceWidget, FieldWidget
from z3c.form.browser import widget


@zope.interface.implementer_only(interfaces.IRadioWidget)
class RadioWidget(widget.HTMLInputWidget, SequenceWidget):
    """Input type radio widget implementation."""

    klass = u'radio-widget'
    css = u'radio'
    items = ()

    def isChecked(self, term):
        return term.token in self.value

    def renderForValue(self, value):
        term = self.terms.getTermByToken(value)
        checked = self.isChecked(term)
        id = '%s-%i' % (self.id, list(self.terms).index(term))
        item = {'id': id, 'name': self.name, 'value': term.token,
                'checked': checked}
        template = zope.component.getMultiAdapter(
            (self.context, self.request, self.form, self.field, self),
            IPageTemplate, name=self.mode + '_single')
        return template(self, item)

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(RadioWidget, self).update()
        # XXX: this is to early for setup items. See select widget how this
        # sould be done. Setup the items here doens't allow to override the
        # widget.value in updateWidgets, ri
        widget.addFieldClass(self)
        self.items = []
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = translate(term.title, context=self.request,
                                  default=term.title)
            else:
                label = util.toUnicode(term.value)
            self.items.append(
                {'id':id, 'name':self.name, 'value':term.token,
                 'label':label, 'checked':checked})


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def RadioFieldWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    return FieldWidget(field, RadioWidget(request))
