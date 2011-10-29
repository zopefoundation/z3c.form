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
"""Error Views Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import os
import zope.component
import zope.interface
import zope.schema
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.pagetemplate.interfaces import IPageTemplate

import z3c.form
from z3c.form import interfaces, util, value
from z3c.form.i18n import MessageFactory as _

ErrorViewMessage = value.StaticValueCreator(
    discriminators = ('error', 'request', 'widget', 'field', 'form', 'content')
    )

ComputedErrorViewMessage = value.ComputedValueCreator(
    discriminators = ('error', 'request', 'widget', 'field', 'form', 'content')
    )


def ErrorViewDiscriminators(
    errorView,
    error=None, request=None, widget=None, field=None, form=None, content=None):
    zope.component.adapter(
        util.getSpecification(error),
        util.getSpecification(request),
        util.getSpecification(widget),
        util.getSpecification(field),
        util.getSpecification(form),
        util.getSpecification(content))(errorView)


class ErrorViewSnippet(object):
    """Error view snippet."""
    zope.component.adapts(
        zope.schema.ValidationError, None, None, None, None, None)
    zope.interface.implements(interfaces.IErrorViewSnippet)

    def __init__(self, error, request, widget, field, form, content):
        self.error = self.context = error
        self.request = request
        self.widget = widget
        self.field = field
        self.form = form
        self.content = content

    def createMessage(self):
        return self.error.doc()

    def update(self):
        value = zope.component.queryMultiAdapter(
            (self.context, self.request, self.widget,
             self.field, self.form, self.content),
            interfaces.IValue, name='message')
        if value is not None:
            self.message = value.get()
        else:
            self.message = self.createMessage()

    def render(self):
        template = zope.component.getMultiAdapter(
            (self, self.request), IPageTemplate)
        return template(self)

    def __repr__(self):
        return '<%s for %s>' %(
            self.__class__.__name__, self.error.__class__.__name__)


class ValueErrorViewSnippet(ErrorViewSnippet):
    """An error view for ValueError."""
    zope.component.adapts(
        ValueError, None, None, None, None, None)

    defaultMessage = _('The system could not process the given value.')

    def createMessage(self):
        return self.defaultMessage


class InvalidErrorViewSnippet(ErrorViewSnippet):
    """Error view snippet."""
    zope.component.adapts(
        zope.interface.Invalid, None, None, None, None, None)

    def createMessage(self):
        return self.error.args[0]


class MultipleErrorViewSnippet(ErrorViewSnippet):
    """Error view snippet for multiple errors."""
    zope.component.adapts(
        interfaces.IMultipleErrors, None, None, None, None, None)

    def update(self):
        pass

    def render(self):
        return ''.join([view.render() for view in self.error.errors])


class MultipleErrors(Exception):
    """An error that contains many errors"""
    zope.interface.implements(interfaces.IMultipleErrors)

    def __init__(self, errors):
        self.errors = errors


class ErrorViewTemplateFactory(object):
    """Error view template factory."""

    template = None

    def __init__(self, filename, contentType='text/html'):
        self.template = ViewPageTemplateFile(filename, content_type=contentType)

    def __call__(self, errorView, request):
        return self.template

# Create the standard error view template
StandardErrorViewTemplate = ErrorViewTemplateFactory(
    os.path.join(os.path.dirname(z3c.form.__file__), 'error.pt'), 'text/html')
zope.component.adapter(
    interfaces.IErrorViewSnippet, None)(StandardErrorViewTemplate)
zope.interface.implementer(IPageTemplate)(StandardErrorViewTemplate)
