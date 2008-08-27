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
"""Utilities helpful to the package.

$Id$
"""
__docformat__ = "reStructuredText"
import re
import types
import string
import zope.interface
import zope.contenttype

from z3c.form import interfaces
from z3c.form.i18n import MessageFactory as _


_identifier = re.compile('[A-Za-z][a-zA-Z0-9_]*$')

def createId(name):
    if _identifier.match(name):
        return str(name).lower()
    return name.encode('utf-8').encode('hex')

_acceptableChars = string.letters + string.digits + '_-'
def createCSSId(name):
    return str(''.join([((char in _acceptableChars and char) or
                         char.encode('utf-8').encode('hex'))
                        for char in name]))

classTypes = type, types.ClassType

def getSpecification(spec, force=False):
    """Get the specification of the given object.

    If the given object is already a specification acceptable to the component
    architecture, it is simply returned. This is true for classes
    and specification objects (which includes interfaces).

    In case of instances, an interface is generated on the fly and tagged onto
    the object. Then the interface is returned as the specification.
    """
    # If the specification is an instance, then we do some magic.
    if (force or
        (spec is not None and
         not zope.interface.interfaces.ISpecification.providedBy(spec)
         and not isinstance(spec, classTypes)) ):
        # Step 1: Create an interface
        iface = zope.interface.interface.InterfaceClass(
            'IGeneratedForObject_%i' %hash(spec))
        # Step 2: Directly-provide the interface on the specification
        zope.interface.alsoProvides(spec, iface)
        # Step 3: Make the new interface the specification for this instance
        spec = iface
    return spec


def expandPrefix(prefix):
    """Expand prefix string by adding a trailing period if needed.

    expandPrefix(p) should be used instead of p+'.' in most contexts.
    """
    if prefix and not prefix.endswith('.'):
        return prefix + '.'
    return prefix


def getWidgetById(form, id):
    """Get a widget by it's rendered DOM element id."""
    # convert the id to a name
    name = id.replace('-', '.')
    prefix = form.prefix + form.widgets.prefix
    if not name.startswith(prefix):
        raise ValueError("Name %r must start with prefix %r" %(name, prefix))
    shortName = name[len(prefix):]
    return form.widgets.get(shortName, None)


def extractContentType(form, id):
    """Extract the content type of the widget with the given id."""
    widget = getWidgetById(form, id)
    return zope.contenttype.guess_content_type(widget.filename)[0]


def extractFileName(form, id, cleanup=True, allowEmtpyPostFix=False):
    """Extract the filename of the widget with the given id.

    Uploads from win/IE need some cleanup because the filename includes also
    the path. The option ``cleanup=True`` will do this for you. The option
    ``allowEmtpyPostFix`` allows to have a filename without extensions. By
    default this option is set to ``False`` and will raise a ``ValueError`` if
    a filename doesn't contain a extension.
    """
    widget = getWidgetById(form, id)
    if not allowEmtpyPostFix or cleanup:
        # We need to strip out the path section even if we do not reomve them
        # later, because we just need to check the filename extension.
        cleanFileName = widget.filename.split('\\')[-1]
        cleanFileName = cleanFileName.split('/')[-1]
        dottedParts = cleanFileName.split('.')
    if not allowEmtpyPostFix:
        if len(dottedParts) <= 1:
            raise ValueError(_('Missing filename extension.'))
    if cleanup:
        return cleanFileName
    return widget.filename


class Manager(object):
    """Non-persistent IManager implementation."""
    zope.interface.implements(interfaces.IManager)

    def __init__(self, *args, **kw):
        self._data_keys = []
        self._data_values = []
        self._data = {}

    def __len__(self):
        return len(self._data_values)

    def __iter__(self):
        return iter(self._data_keys)

    def __getitem__(self, name):
        return self._data[name]

    def __delitem__(self, name):
        if name not in self._data_keys:
            raise KeyError(name)

        del self._data_keys[self._data_keys.index(name)]
        value = self._data[name]
        del self._data_values[self._data_values.index(value)]
        del self._data[name]

    def get(self, name, default=None):
        return self._data.get(name, default)

    def keys(self):
        return self._data_keys

    def values(self):
        return self._data_values

    def items(self):
        return [(i, self._data[i]) for i in self._data_keys]

    def __contains__(self, name):
        return bool(self.get(name))


class SelectionManager(Manager):
    """Non-persisents ISelectionManager implementation."""
    zope.interface.implements(interfaces.ISelectionManager)

    managerInterface = None

    def __add__(self, other):
        if not self.managerInterface.providedBy(other):
            return NotImplemented
        return self.__class__(self, other)

    def select(self, *names):
        """See interfaces.ISelectionManager"""
        return self.__class__(*[self[name] for name in names])

    def omit(self, *names):
        """See interfaces.ISelectionManager"""
        return self.__class__(
            *[item for item in self.values()
              if item.__name__ not in names])

    def copy(self):
        """See interfaces.ISelectionManager"""
        return self.__class__(*self.values())
