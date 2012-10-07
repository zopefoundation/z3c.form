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
from zope.interface.common import mapping
from zope.security.interfaces import ForbiddenAttribute
from zope.security.checker import canAccess, canWrite, Proxy

from z3c.form import interfaces

_marker = []

ALLOWED_DATA_CLASSES = [dict]
try:
    import persistent.mapping
    import persistent.dict
    ALLOWED_DATA_CLASSES.append(persistent.mapping.PersistentMapping)
    ALLOWED_DATA_CLASSES.append(persistent.dict.PersistentDict)
except ImportError:
    pass


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

    @property
    def adapted_context(self):
        # get the right adapter or context
        context = self.context
        # NOTE: zope.schema fields defined in inherited interfaces will point
        # to the inherited interface. This could end in adapting the wrong item.
        # This is very bad because the widget field offers an explicit interface
        # argument which doesn't get used in Widget setup during IDataManager
        # lookup. We should find a concept which allows to adapt the
        # IDataManager use the widget field interface instead of the zope.schema
        # field.interface, ri
        if self.field.interface is not None:
            context = self.field.interface(context)
        return context

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        return getattr(self.adapted_context, self.field.__name__)

    def query(self, default=interfaces.NO_VALUE):
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
        setattr(self.adapted_context, self.field.__name__, value)

    def canAccess(self):
        """See z3c.form.interfaces.IDataManager"""
        context = self.adapted_context
        if isinstance(context, Proxy):
            return canAccess(context, self.field.__name__)
        return True

    def canWrite(self):
        """See z3c.form.interfaces.IDataManager"""
        context = self.adapted_context
        if isinstance(context, Proxy):
            return canWrite(context, self.field.__name__)
        return True

class DictionaryField(DataManager):
    """Dictionary field.

    NOTE: Even though, this data manager allows nearly all kinds of
    mappings, by default it is only registered for dict, because it
    would otherwise get picked up in undesired scenarios. If you want
    to it use for another mapping, register the appropriate adapter in
    your application.

    """

    zope.component.adapts(
        dict, zope.schema.interfaces.IField)

    _allowed_data_classes = tuple(ALLOWED_DATA_CLASSES)

    def __init__(self, data, field):
        if (not isinstance(data, self._allowed_data_classes) and
            not mapping.IMapping.providedBy(data)):
            raise ValueError("Data are not a dictionary: %s" %type(data))
        self.data = data
        self.field = field

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        value = self.data.get(self.field.__name__, _marker)
        if value is _marker:
            raise AttributeError
        return value

    def query(self, default=interfaces.NO_VALUE):
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

