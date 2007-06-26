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
"""Form Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import sys
import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.publisher import browser
from zope.formlib import form
from zope.pagetemplate.interfaces import IPageTemplate
from zope.schema.fieldproperty import FieldProperty

from z3c.form import button, field, interfaces, util
from z3c.form.i18n import MessageFactory as _


def applyChanges(form, content, data):
    changed = False
    for name, field in form.fields.items():
        # If the field is not in the data, then go on to the next one
        if name not in data:
            continue
        # Get the datamanager and get the original value
        dm = zope.component.getMultiAdapter(
            (content, field.field), interfaces.IDataManager)
        oldValue = dm.get()
        # Only update the data, if it is different
        if dm.get() != data[name]:
            dm.set(data[name])
            changed = True
    return changed


def extends(*args, **kwargs):
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    if not kwargs.get('ignoreFields', False):
        f_locals['fields'] = field.Fields()
        for arg in args:
            f_locals['fields'] += getattr(arg, 'fields', field.Fields())
    if not kwargs.get('ignoreHandlers', False):
        f_locals['buttons'] = button.Buttons()
        for arg in args:
            f_locals['buttons'] += getattr(arg, 'buttons', button.Buttons())
    if not kwargs.get('ignoreHandlers', False):
        f_locals['handlers'] = button.Handlers()
        for arg in args:
            f_locals['handlers'] += getattr(arg, 'handlers', button.Handlers())


class BaseForm(browser.BrowserPage):
    """A base form."""
    zope.interface.implements(interfaces.IForm,
                              interfaces.IFieldsForm)

    fields = field.Fields()

    prefix = 'form.'
    status = ''
    template = None

    def getContent(self):
        '''See interfaces.IForm'''
        return self.context

    def updateWidgets(self):
        '''See interfaces.IForm'''
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), interfaces.IWidgets)
        self.widgets.update()

    def extractData(self):
        '''See interfaces.IForm'''
        return self.widgets.extract()

    def update(self):
        '''See interfaces.IForm'''
        self.updateWidgets()

    def render(self):
        '''See interfaces.IForm'''
        # render content template
        if self.template is None:
            template = zope.component.getMultiAdapter((self, self.request),
                IPageTemplate)
            return template(self)
        return self.template()


class DisplayForm(BaseForm):

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), interfaces.IWidgets)
        self.widgets.mode = interfaces.DISPLAY_MODE
        self.widgets.ignoreRequest = True
        self.widgets.update()


class Form(BaseForm):
    """The Form."""
    zope.interface.implements(
        interfaces.IInputForm, interfaces.IButtonForm, interfaces.IHandlerForm)

    buttons = button.Buttons()

    method = FieldProperty(interfaces.IInputForm['method'])
    enctype = FieldProperty(interfaces.IInputForm['enctype'])
    acceptCharset = FieldProperty(interfaces.IInputForm['acceptCharset'])
    accept = FieldProperty(interfaces.IInputForm['accept'])

    @property
    def action(self):
        """See interfaces.IInputForm"""
        return self.request.getURL()

    @property
    def name(self):
        """See interfaces.IInputForm"""
        return self.prefix.strip('.')

    id = name

    def updateActions(self):
        self.actions = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), interfaces.IActions)
        self.actions.update()

    def update(self):
        super(Form, self).update()
        self.updateActions()
        self.actions.execute()

    def __call__(self):
        self.update()
        return self.render()


class AddForm(Form):
    """A field and button based add form."""
    zope.interface.implements(interfaces.IAddForm)

    _finishedAdd = False
    formErrorsMessage = _('There were some errors.')

    @button.buttonAndHandler(_('Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.create(data)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.add(obj)
        self._finishedAdd = True

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), interfaces.IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.ignoreReadonly = True
        self.widgets.update()

    def create(self, data):
        raise NotImplementedError

    def add(self, object):
        raise NotImplementedError

    def nextURL(self):
        raise NotImplementedError

    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(AddForm, self).render()


class EditForm(Form):
    """A simple edit form with an apply button."""
    zope.interface.implements(interfaces.IEditForm)

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), interfaces.IWidgets)
        self.widgets.update()

    def applyChanges(self, data):
        content = self.getContent()
        changed = applyChanges(self, content, data)
        if changed:
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(content))
        return changed

    @button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changed = self.applyChanges(data)
        if changed:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage


class FormTemplateFactory(object):
    """Form template factory."""

    def __init__(self, filename, contentType='text/html', form=None,
        request=None):
        self.template = ViewPageTemplateFile(filename, content_type=contentType)
        zope.component.adapter(
            util.getSpecification(form),
            util.getSpecification(request))(self)
        zope.interface.implementer(IPageTemplate)(self)

    def __call__(self, form, request):
        return self.template
