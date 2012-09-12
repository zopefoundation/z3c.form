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
import zope.component

from z3c.form import form, interfaces
from zope.interface import implements


class Group(form.BaseForm):
    implements(interfaces.IGroup)

    groups = ()

    def __init__(self, context, request, parentForm):
        self.context = context
        self.request = request
        self.parentForm = self.__parent__ = parentForm

    def updateWidgets(self):
        '''See interfaces.IForm'''
        for attrName in ('mode', 'ignoreRequest', 'ignoreContext',
                         'ignoreReadonly'):
            value = getattr(self.parentForm.widgets, attrName)
            setattr(self.widgets, attrName, value)
        self.widgets.update()

    def update(self):
        '''See interfaces.IForm'''
        super(Group, self).update()
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
        return changed


class GroupForm(object):
    """A mix-in class for add and edit forms to support groups."""
    implements(interfaces.IGroupForm)

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
                zope.lifecycleevent.ObjectModifiedEvent(content,
                    *descriptions))

        return changed

    def updateWidgets(self):
        '''See interfaces.IForm'''
        super(GroupForm, self).updateWidgets()

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
