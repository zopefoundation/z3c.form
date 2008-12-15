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

$Id: select.py 78513 2007-07-31 23:03:47Z srichter $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from zope.i18n import translate

from z3c.form.i18n import MessageFactory as _
from z3c.form import interfaces
from z3c.form import widget
from z3c.form import button
from z3c.form.browser.widget import HTMLSelectWidget


class FormMixin(object):
    zope.interface.implements(interfaces.IButtonForm, interfaces.IHandlerForm)


class MultiWidget(HTMLSelectWidget, widget.MultiWidget, FormMixin):
    """Multi widget implementation."""
    zope.interface.implements(interfaces.IMultiWidget)

    buttons = button.Buttons()

    prefix = 'widget'
    klass = u'multi-widget'
    items = ()

    def updateActions(self):
        if self.name is not None:
            self.prefix = self.name
        self.actions = zope.component.getMultiAdapter(
            (self, self.request, self), interfaces.IActions)
        self.actions.update()

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        self.updateActions()
        super(MultiWidget, self).update()
        self.actions.execute()

    @button.buttonAndHandler(_('Add'), name='add')
    def handleAdd(self, action):
        self.appendAddingWidget()

    @button.buttonAndHandler(_('Remove'), name='remove')
    def handleRemove(self, action):
        self.widgets = [widget for widget in self.widgets
                        if ('%s.remove' % (widget.name)) not in self.request]
        self.value = [widget.value for widget in self.widgets]

@zope.interface.implementer(interfaces.IFieldWidget)
def multiFieldWidgetFactory(field, request):
    """IFieldWidget factory for TextLinesWidget."""
    return widget.FieldWidget(field, MultiWidget(request))


@zope.interface.implementer(interfaces.IFieldWidget)
def MultiFieldWidget(field, value_type, request):
    """IFieldWidget factory for TextLinesWidget."""
    return multiFieldWidgetFactory(field, request)
