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
"""File Widget Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form import interfaces, widget
from z3c.form.browser import text


@zope.interface.implementer_only(interfaces.IFileWidget)
class FileWidget(text.TextWidget):
    """Input type text widget implementation."""

    klass = u'file-widget'
    css = u'file'

    # Filename and headers attribute get set by ``IDataConverter`` to the widget
    # provided by the FileUpload object of the form.
    headers = None
    filename = None

    def json_data(self):
        data = super(FileWidget, self).json_data()
        data['type'] = 'file'
        return data


@zope.component.adapter(zope.schema.interfaces.IBytes, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def FileFieldWidget(field, request):
    """IFieldWidget factory for FileWidget."""
    return widget.FieldWidget(field, FileWidget(request))
