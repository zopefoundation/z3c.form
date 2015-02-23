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
from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser import widget


@zope.interface.implementer_only(interfaces.ITextAreaWidget)
class TextAreaWidget(widget.HTMLTextAreaWidget, Widget):
    """Textarea widget implementation."""

    klass = u'textarea-widget'
    css = u'textarea'
    value = u''

    def update(self):
        super(TextAreaWidget, self).update()
        widget.addFieldClass(self)

    def json_data(self):
        data = super(TextAreaWidget, self).json_data()
        data['type'] = 'textarea'
        return data


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def TextAreaFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, TextAreaWidget(request))
