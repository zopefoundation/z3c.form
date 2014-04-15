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
"""Widget Group Implementation

$Id$
"""
__docformat__ = "reStructuredText"

from z3c.form import form, interfaces
from zope.interface import implementer
from z3c.form.events import DataExtractedEvent

import zope.component
import zope.event


@implementer(interfaces.IGroup)
class Group(form.BaseForm):

    groups = ()

    def __init__(self, context, request, parentForm):
        self.context = context
        self.request = request
        self.parentForm = self.__parent__ = parentForm

    def updateWidgets(self, prefix=None):
        '''See interfaces.IForm'''
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), interfaces.IWidgets)
        for attrName in ('mode', 'ignoreRequest', 'ignoreContext',
                         'ignoreReadonly'):
            value = getattr(self.parentForm.widgets, attrName)
            setattr(self.widgets, attrName, value)
        if prefix is not None:
            self.widgets.prefix = prefix
        self.widgets.update()

    def update(self):
        '''See interfaces.IForm'''
        self.updateWidgets()
        groups = []
        for groupClass in self.groups:
            # only instantiate the groupClass if it hasn't already
            # been instantiated
            if interfaces.IGroup.providedBy(groupClass):
                group = groupClass
            else:
                group = groupClass(self.context, self.request, self)
            group.update()
            groups.append(group)
        self.groups = tuple(groups)

    def extractData(self, setErrors=True):
        '''See interfaces.IForm'''
        data, errors = super(Group, self).extractData(setErrors=setErrors)
        for group in self.groups:
            groupData, groupErrors = group.extractData(setErrors=setErrors)
            data.update(groupData)
            if groupErrors:
                if errors:
                    errors += groupErrors
                else:
                    errors = groupErrors
        zope.event.notify(DataExtractedEvent(data, errors, self))
        return data, errors

    def applyChanges(self, data):
        '''See interfaces.IEditForm'''
        content = self.getContent()
        changed = form.applyChanges(self, content, data)
        for group in self.groups:
            groupChanged = group.applyChanges(data)
            for interface, names in groupChanged.items():
                changed[interface] = changed.get(interface, []) + names
        return changed


@implementer(interfaces.IGroupForm)
class GroupForm(object):
    """A mix-in class for add and edit forms to support groups."""

    groups = ()

    def extractData(self, setErrors=True):
        '''See interfaces.IForm'''
        data, errors = super(GroupForm, self).extractData(setErrors=setErrors)
        for group in self.groups:
            groupData, groupErrors = group.extractData(setErrors=setErrors)
            data.update(groupData)
            if groupErrors:
                if errors:
                    errors += groupErrors
                else:
                    errors = groupErrors
        zope.event.notify(DataExtractedEvent(data, errors, self))
        return data, errors

    def applyChanges(self, data):
        '''See interfaces.IEditForm'''
        descriptions = []
        content = self.getContent()
        changed = form.applyChanges(self, content, data)
        for group in self.groups:
            groupChanged = group.applyChanges(data)
            for interface, names in groupChanged.items():
                changed[interface] = changed.get(interface, []) + names
        if changed:
            for interface, names in changed.items():
                descriptions.append(
                    zope.lifecycleevent.Attributes(interface, *names))
            # Send out a detailed object-modified event
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(
                    content, *descriptions))

        return changed

    def update(self):
        '''See interfaces.IForm'''
        self.updateWidgets()
        groups = []
        for groupClass in self.groups:
            # only instantiate the groupClass if it hasn't already
            # been instantiated
            if interfaces.IGroup.providedBy(groupClass):
                group = groupClass
            else:
                group = groupClass(self.context, self.request, self)
            group.update()
            groups.append(group)
        self.groups = tuple(groups)
        self.updateActions()
        self.actions.execute()
