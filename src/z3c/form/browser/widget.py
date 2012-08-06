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


class WidgetLayoutSupport(object):
    """Widget layout support"""

    def wrapCSSClass(self, klass, pattern='s(class)%'):
        """Return a list of css class names wrapped with given pattern"""
        if klass is not None and pattern is not None:
            return [pattern % {'class': k} for k in klass.split()]
        else:
            return []

    def getCSSClass(self, klass=None, error=None, required=None,
        classPattern='%(class)s', errorPattern='%(class)s-error',
        requiredPattern='%(class)s-required'):
        """Setup given css class (klass) with error and required postfix
        
        If no klass name is given the widget.wrapper class name/names get used.
        It is also possible if more then one (empty space separated) names 
        are given as klass argument.

        This method can get used from your form or widget template or widget
        layout template without to re-implement the widget itself just because
        you a different CSS class concept. 

        The following sample:
        
        <div tal:attributes="class python:widget.getCSSClass('foo bar')">
          label widget and error
        </div>
        
        will render a div tag if the widget field defines required=True:
        
        <div class="foo-error bar-error foo-required bar-required foo bar">
          label widget and error
        </div>

        And the following sample:
        
        <div tal:attributes="class python:widget.getCSSClass('row')">
          label widget and error
        </div>
        
        will render a div tag if the widget field defines required=True
        and an error occurs:
        
        <div class="row-error row-required row">
          label widget and error
        </div>

        Note; you need to define a globale widget property if you use
        python:widget (in your form template). And you need to use the
        view scope in your widget or layout templates.

        Note, you can set the pattern to None for skip error or required
        rendering. Or you can use a pattern like 'error' or 'required' if
        you like to skip postfixing your default css klass name for error or
        required rendering.

        """
        classes = []
        # setup class names
        if klass is not None:
            kls = klass
        else:
            kls = self.css

        # setup error class names
        if error is not None:
            error = error
        else:
            error = kls

        # setup required class names
        if required is not None:
            required = required
        else:
            required = kls

        # append error class names
        if self.error is not None:
            classes += self.wrapCSSClass(error, errorPattern)
        # append required class names
        if self.required:
            classes += self.wrapCSSClass(required, requiredPattern)
        # append given class names
        classes += self.wrapCSSClass(kls, classPattern)
        # remove duplicated class names but keep order
        unique = []
        [unique.append(kls) for kls in classes if kls not in unique]
        return ' '.join(unique)


class HTMLFormElement(WidgetLayoutSupport):
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

    # layout support
    css = FieldProperty(interfaces.IHTMLFormElement['css'])

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
