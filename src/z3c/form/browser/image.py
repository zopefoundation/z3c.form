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
import zope.traversing.api
from zope.schema.fieldproperty import FieldProperty
from zope.component import hooks

from z3c.form import interfaces
from z3c.form.widget import FieldWidget
from z3c.form.browser import button
from z3c.form.browser.interfaces import IHTMLImageWidget


class ImageWidget(button.ButtonWidget):
    """A image button of a form."""
    zope.interface.implementsOnly(interfaces.IImageWidget)

    src = FieldProperty(IHTMLImageWidget['src'])

    klass = u'image-widget'
    css = u'image'

    def extract(self, default=interfaces.NO_VALUE):
        """See z3c.form.interfaces.IWidget."""
        if self.name + '.x' not in self.request:
            return default
        return {
            'x': int(self.request[self.name + '.x']),
            'y': int(self.request[self.name + '.y']),
            'value': self.request[self.name]}


@zope.component.adapter(interfaces.IImageButton, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def ImageFieldWidget(field, request):
    image = FieldWidget(field, ImageWidget(request))
    image.value = field.title
    # Get the full resource URL for the image:
    site = hooks.getSite()
    image.src = unicode(zope.traversing.api.traverse(
        site, '++resource++' + field.image, request=request)())
    return image
