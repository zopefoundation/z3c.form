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
import zope.component
import zope.schema
from zope.security.interfaces import ForbiddenAttribute
from zope.security.checker import canAccess, canWrite, Proxy

from z3c.form import interfaces


class DataManager(object):
    """Data manager base class."""
    zope.interface.implements(interfaces.IDataManager)

class AttributeField(DataManager):
    """Attribute field."""
    zope.component.adapts(
        zope.interface.Interface, zope.schema.interfaces.IField)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        # get the right adapter or context
        context = self.context
        if self.field.interface is not None:
            context = self.field.interface(context)
        return getattr(context, self.field.__name__)

    def query(self, default=interfaces.NOVALUE):
        """See z3c.form.interfaces.IDataManager"""
        try:
            return self.get()
        except ForbiddenAttribute, e:
            raise e
        except AttributeError:
            return default

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""
        if self.field.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.field.__name__,
                               self.context.__class__.__module__,
                               self.context.__class__.__name__))
        # get the right adapter or context
        context = self.context
        if self.field.interface is not None:
            context = self.field.interface(context)
        setattr(context, self.field.__name__, value)

    def canAccess(self):
        """See z3c.form.interfaces.IDataManager"""
        context = self.context
        if self.field.interface is not None:
            context = self.field.interface(context)
        if isinstance(context, Proxy):
            return canAccess(context, self.field.__name__)
        return True

    def canWrite(self):
        """See z3c.form.interfaces.IDataManager"""
        context = self.context
        if self.field.interface is not None:
            context = self.field.interface(context)
        if isinstance(context, Proxy):
            return canWrite(context, self.field.__name__)
        return True

class DictionaryField(DataManager):
    """Dictionary field."""
    zope.component.adapts(
        dict, zope.schema.interfaces.IField)

    def __init__(self, data, field):
        if not isinstance(data, dict):
            raise ValueError("Data are not a dictionary: %s" %type(data))
        self.data = data
        self.field = field

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        return self.data[self.field.__name__]

    def query(self, default=interfaces.NOVALUE):
        """See z3c.form.interfaces.IDataManager"""
        return self.data.get(self.field.__name__, default)

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""
        if self.field.readonly:
            raise TypeError("Can't set values on read-only fields name=%s"
                            % self.field.__name__)
        self.data[self.field.__name__] = value

    def canAccess(self):
        """See z3c.form.interfaces.IDataManager"""
        return True

    def canWrite(self):
        """See z3c.form.interfaces.IDataManager"""
        return True

