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
"""Title hint adapter implementation

$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.schema.interfaces

from z3c.form import interfaces


class FieldDescriptionAsHint(object):
    """Schema field description as widget ``title`` IValue adapter."""

    zope.interface.implements(interfaces.IValue)
    zope.component.adapts(zope.interface.Interface, interfaces.IFormLayer,
        interfaces.IForm, zope.schema.interfaces.IField, interfaces.IWidget)

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

    def get(self):
        if self.field.description:
            return self.field.description
        # None avoids rendering in templates
        return None
