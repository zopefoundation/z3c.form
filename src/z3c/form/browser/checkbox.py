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
from z3c.form.widget import SequenceWidget, FieldWidget
from z3c.form.browser import widget


class CheckBoxWidget(widget.HTMLInputWidget, SequenceWidget):
    """Input type checkbox widget implementation."""
    zope.interface.implementsOnly(interfaces.ICheckBoxWidget)

    klass = u'checkbox-widget'
    items = ()

    def isChecked(self, term):
        return term.token in self.value

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(CheckBoxWidget, self).update()
        widget.addFieldClass(self)
        self.items = []
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = translate(term.title, context=self.request,
                                  default=term.title)
            self.items.append(
                {'id':id, 'name':self.name + ':list', 'value':term.token,
                 'label':label, 'checked':checked})


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def CheckBoxFieldWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    return FieldWidget(field, CheckBoxWidget(request))
