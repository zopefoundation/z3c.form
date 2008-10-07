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
"""Widget Framework Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.form.interfaces import IFieldWidget
from z3c.form.browser import interfaces

class HTMLFormElement(object):
    zope.interface.implements(interfaces.IHTMLFormElement)

    id = FieldProperty(interfaces.IHTMLFormElement['id'])
    klass = FieldProperty(interfaces.IHTMLFormElement['klass'])
    style = FieldProperty(interfaces.IHTMLFormElement['style'])
    title = FieldProperty(interfaces.IHTMLFormElement['title'])

    lang = FieldProperty(interfaces.IHTMLFormElement['lang'])

    onclick = FieldProperty(interfaces.IHTMLFormElement['onclick'])
    ondblclick = FieldProperty(interfaces.IHTMLFormElement['ondblclick'])
    onmousedown = FieldProperty(interfaces.IHTMLFormElement['onmousedown'])
    onmouseup = FieldProperty(interfaces.IHTMLFormElement['onmouseup'])
    onmouseover = FieldProperty(interfaces.IHTMLFormElement['onmouseover'])
    onmousemove = FieldProperty(interfaces.IHTMLFormElement['onmousemove'])
    onmouseout = FieldProperty(interfaces.IHTMLFormElement['onmouseout'])
    onkeypress = FieldProperty(interfaces.IHTMLFormElement['onkeypress'])
    onkeydown = FieldProperty(interfaces.IHTMLFormElement['onkeydown'])
    onkeyup = FieldProperty(interfaces.IHTMLFormElement['onkeyup'])

    disabled = FieldProperty(interfaces.IHTMLFormElement['disabled'])
    tabindex = FieldProperty(interfaces.IHTMLFormElement['tabindex'])
    onfocus = FieldProperty(interfaces.IHTMLFormElement['onfocus'])
    onblur = FieldProperty(interfaces.IHTMLFormElement['onblur'])
    onchange = FieldProperty(interfaces.IHTMLFormElement['onchange'])

    def addClass(self, klass):
        """See interfaces.IHTMLFormElement"""
        if not self.klass:
            self.klass = unicode(klass)
        else:
            #make sure items are not repeated
            parts = self.klass.split()+[unicode(klass)]
            seen = {}
            unique = []
            for item in parts:
                if item in seen:
                    continue
                seen[item]=1
                unique.append(item)
            self.klass = u' '.join(unique)

    def update(self):
        """See z3c.form.interfaces.IWidget"""
        super(HTMLFormElement, self).update()
        if self.required:
            self.addClass('required')


class HTMLInputWidget(HTMLFormElement):
    zope.interface.implements(interfaces.IHTMLInputWidget)

    readonly = FieldProperty(interfaces.IHTMLInputWidget['readonly'])
    alt = FieldProperty(interfaces.IHTMLInputWidget['alt'])
    accesskey = FieldProperty(interfaces.IHTMLInputWidget['accesskey'])
    onselect = FieldProperty(interfaces.IHTMLInputWidget['onselect'])


class HTMLTextInputWidget(HTMLInputWidget):
    zope.interface.implements(interfaces.IHTMLTextInputWidget)

    size = FieldProperty(interfaces.IHTMLTextInputWidget['size'])
    maxlength = FieldProperty(interfaces.IHTMLTextInputWidget['maxlength'])


class HTMLTextAreaWidget(HTMLFormElement):
    zope.interface.implements(interfaces.IHTMLTextAreaWidget)

    rows = FieldProperty(interfaces.IHTMLTextAreaWidget['rows'])
    cols = FieldProperty(interfaces.IHTMLTextAreaWidget['cols'])
    readonly = FieldProperty(interfaces.IHTMLTextAreaWidget['readonly'])
    accesskey = FieldProperty(interfaces.IHTMLTextAreaWidget['accesskey'])
    onselect = FieldProperty(interfaces.IHTMLTextAreaWidget['onselect'])


class HTMLSelectWidget(HTMLFormElement):
    zope.interface.implements(interfaces.IHTMLSelectWidget)

    multiple = FieldProperty(interfaces.IHTMLSelectWidget['multiple'])
    size = FieldProperty(interfaces.IHTMLSelectWidget['size'])


def addFieldClass(widget):
    """Add a class to the widget that is based on the field type name.

    If the widget does not have field, then nothing is done.
    """
    if IFieldWidget.providedBy(widget):
        klass = unicode(widget.field.__class__.__name__.lower() + '-field')
        widget.addClass(klass)
