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
"""Submit Widget Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface

from z3c.form import interfaces, widget
from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser import widget


class SubmitWidget(widget.HTMLInputWidget, Widget):
    """A submit button of a form."""
    zope.interface.implementsOnly(interfaces.ISubmitWidget)

    klass = u'submitWidget'

    def update(self):
        super(SubmitWidget, self).update()
        widget.addFieldClass(self)


@zope.component.adapter(interfaces.IButton, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def SubmitFieldWidget(field, request):
    submit = FieldWidget(field, SubmitWidget(request))
    submit.value = field.title
    return submit
