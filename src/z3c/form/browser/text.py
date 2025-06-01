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
import zope.schema.interfaces

from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget


@zope.interface.implementer_only(interfaces.ITextWidget)
class TextWidget(widget.HTMLTextInputWidget, Widget):
    """Input type text widget implementation."""

    klass = 'text-widget'
    css = 'text'
    value = ''

    @property
    def step(self):
        if zope.schema.interfaces.IInt.providedBy(self.field):
            return 1
        elif (
            zope.schema.interfaces.IFloat.providedBy(self.field)
            or zope.schema.interfaces.IDecimal.providedBy(self.field)
        ):
            return 'any'

        # Default - if no number type - is to not include the step attribute
        return None

    @property
    def type(self):
        if (
            zope.schema.interfaces.IInt.providedBy(self.field)
            or zope.schema.interfaces.IFloat.providedBy(self.field)
            or zope.schema.interfaces.IDecimal.providedBy(self.field)
        ):
            return 'number'
        else:
            return 'text'

    def update(self):
        super().update()
        widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def TextFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, TextWidget(request))
