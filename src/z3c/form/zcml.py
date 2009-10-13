##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

import os

import zope.interface
import zope.component.zcml
import zope.schema
import zope.configuration.fields
from zope.configuration.exceptions import ConfigurationError
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from z3c.form import interfaces
from z3c.form.i18n import MessageFactory as _
from z3c.form.widget import WidgetTemplateFactory
from z3c.form.object import ObjectWidgetTemplateFactory


class IWidgetTemplateDirective(zope.interface.Interface):
    """Parameters for the widget template directive."""

    template = zope.configuration.fields.Path(
        title=_('Layout template.'),
        description=_('Refers to a file containing a page template (should '
                      'end in extension ``.pt`` or ``.html``).'),
        required=True)

    mode = zope.schema.BytesLine(
        title=_('The mode of the template.'),
        description=_('The mode is used to define input and display '
                      'templates'),
        default=interfaces.INPUT_MODE,
        required=False)

    for_ = zope.configuration.fields.GlobalObject(
        title=_('View'),
        description=_('The view for which the template should be available'),
        default=zope.interface.Interface,
        required = False)

    layer = zope.configuration.fields.GlobalObject(
        title=_('Layer'),
        description=_('The layer for which the template should be available'),
        default=IDefaultBrowserLayer,
        required=False)

    view = zope.configuration.fields.GlobalObject(
        title=_('View'),
        description=_('The view for which the template should be available'),
        default=zope.interface.Interface,
        required=False)

    field = zope.configuration.fields.GlobalObject(
        title=_('Field'),
        description=_('The field for which the template should be available'),
        default=zope.schema.interfaces.IField,
        required=False)

    widget = zope.configuration.fields.GlobalObject(
        title=_('View'),
        description=_('The widget for which the template should be available'),
        default=interfaces.IWidget,
        required=False)

    contentType = zope.schema.BytesLine(
        title=_('Content Type'),
        description=_('The content type identifies the type of data.'),
        default='text/html',
        required=False)

class IObjectWidgetTemplateDirective(IWidgetTemplateDirective):
    schema = zope.configuration.fields.GlobalObject(
        title=_('Schema'),
        description=_('The schema of the field for which the template should be available'),
        default=zope.interface.Interface,
        required=False)


def widgetTemplateDirective(
    _context, template, for_=zope.interface.Interface,
    layer=IDefaultBrowserLayer, view=None, field=None, widget=None,
    mode=interfaces.INPUT_MODE, contentType='text/html'):

    # Make sure that the template exists
    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)

    factory = WidgetTemplateFactory(template, contentType)
    zope.interface.directlyProvides(factory, IPageTemplate)

    # register the template
    zope.component.zcml.adapter(_context, (factory,), IPageTemplate,
        (for_, layer, view, field, widget), name=mode)


def objectWidgetTemplateDirective(
    _context, template, for_=zope.interface.Interface,
    layer=IDefaultBrowserLayer, view=None, field=None, widget=None,
    schema=None,
    mode=interfaces.INPUT_MODE, contentType='text/html'):

    # Make sure that the template exists
    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)

    factory = ObjectWidgetTemplateFactory(template, contentType)
    zope.interface.directlyProvides(factory, IPageTemplate)

    # register the template
    zope.component.zcml.adapter(_context, (factory,), IPageTemplate,
        (for_, layer, view, field, widget, schema), name=mode)
