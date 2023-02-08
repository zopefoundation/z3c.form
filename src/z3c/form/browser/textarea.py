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
"""Text Area Widget Implementation

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


@zope.interface.implementer_only(interfaces.ITextAreaWidget)
class TextAreaWidget(widget.HTMLTextAreaWidget, Widget):
    """Textarea widget implementation."""

    klass = 'textarea-widget'
    css = 'textarea'
    value = ''

    def update(self):
        super().update()
        widget.addFieldClass(self)

    def json_data(self):
        data = super().json_data()
        data['type'] = 'textarea'
        return data


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def TextAreaFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, TextAreaWidget(request))
