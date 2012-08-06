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
"""ObjectWidget browser related classes

$Id$
"""

__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form import interfaces, object
from z3c.form.widget import FieldWidget
from z3c.form.browser import widget

class ObjectWidget(widget.HTMLFormElement, object.ObjectWidget):
    zope.interface.implements(interfaces.IObjectWidget)

    klass = u'object-widget'
    css = u'object'

@zope.component.adapter(zope.schema.interfaces.IObject, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def ObjectFieldWidget(field, request):
    """IFieldWidget factory for IObjectWidget."""
    return FieldWidget(field, ObjectWidget(request))
