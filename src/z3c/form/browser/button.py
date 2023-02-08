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
"""Button Widget Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface

from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget


@zope.interface.implementer_only(interfaces.IButtonWidget)
class ButtonWidget(widget.HTMLInputWidget, Widget):
    """A simple button of a form."""

    klass = 'button-widget'
    css = 'button'

    def update(self):
        # We do not need to use the widget's update method, because it is
        # mostly about ectracting the value, which we do not need to do.
        widget.addFieldClass(self)


@zope.component.adapter(interfaces.IButton, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def ButtonFieldWidget(field, request):
    button = FieldWidget(field, ButtonWidget(request))
    button.value = field.title
    return button
