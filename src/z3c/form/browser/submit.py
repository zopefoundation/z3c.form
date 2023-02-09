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

from z3c.form import interfaces
from z3c.form.browser import button
from z3c.form.widget import FieldWidget


@zope.interface.implementer_only(interfaces.ISubmitWidget)
class SubmitWidget(button.ButtonWidget):
    """A submit button of a form."""

    klass = 'submit-widget'
    css = 'submit'

    def json_data(self):
        data = super().json_data()
        data['type'] = 'submit'
        return data


@zope.component.adapter(interfaces.IButton, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def SubmitFieldWidget(field, request):
    submit = FieldWidget(field, SubmitWidget(request))
    submit.value = field.title
    return submit
