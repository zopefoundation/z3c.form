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

"""
__docformat__ = "reStructuredText"
import binascii
import re
import string
from collections import OrderedDict
from functools import total_ordering

import zope.contenttype
import zope.interface
import zope.schema

from z3c.form import interfaces
from z3c.form.i18n import MessageFactory as _


_identifier = re.compile('[A-Za-z][a-zA-Z0-9_]*$')
classTypes = (type,)
_acceptableChars = string.ascii_letters + string.digits + '_-'


def toUnicode(obj):
    if isinstance(obj, bytes):
        return obj.decode('utf-8', 'ignore')
    return str(obj)


def toBytes(obj):
    if isinstance(obj, bytes):
        return obj
    if isinstance(obj, str):
        return obj.encode('utf-8')
    return str(obj).encode('utf-8')


def createId(name):
    """Returns a *native* string as id of the given name."""
    if _identifier.match(name):
        return str(name).lower()
    id = binascii.hexlify(name.encode('utf-8'))
    return id.decode()


@total_ordering
class MinType:
    def __le__(self, other):
        return True

    def __eq__(self, other):
        return (self is other)


def sortedNone(items):
    Min = MinType()
    return sorted(items, key=lambda x: Min if x is None else x)


def createCSSId(name):
    return str(''.join([
        (char if char in _acceptableChars else
         binascii.hexlify(char.encode('utf-8')).decode())
        for char in name]))


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
         and not isinstance(spec, classTypes))):

        # Step 1: Calculate an interface name
        ifaceName = 'IGeneratedForObject_%i' % id(spec)

        # Step 2: Find out if we already have such an interface
        existingInterfaces = [
            i for i in zope.interface.directlyProvidedBy(spec)
            if i.__name__ == ifaceName
        ]

        # Step 3a: Return an existing interface if there is one
        if len(existingInterfaces) > 0:
            spec = existingInterfaces[0]
        # Step 3b: Create a new interface if not
        else:
            iface = zope.interface.interface.InterfaceClass(ifaceName)
            zope.interface.alsoProvides(spec, iface)
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
        raise ValueError(f"Name {name!r} must start with prefix {prefix!r}")
    shortName = name[len(prefix):]
    return form.widgets.get(shortName, None)


def extractContentType(form, id):
    """Extract the content type of the widget with the given id."""
    widget = getWidgetById(form, id)
    return zope.contenttype.guess_content_type(widget.filename)[0]


def extractFileName(form, id, cleanup=True, allowEmptyPostfix=False):
    """Extract the filename of the widget with the given id.

    Uploads from win/IE need some cleanup because the filename includes also
    the path. The option ``cleanup=True`` will do this for you. The option
    ``allowEmptyPostfix`` allows to have a filename without extensions. By
    default this option is set to ``False`` and will raise a ``ValueError`` if
    a filename doesn't contain a extension.
    """
    widget = getWidgetById(form, id)
    if not allowEmptyPostfix or cleanup:
        # We need to strip out the path section even if we do not reomve them
        # later, because we just need to check the filename extension.
        cleanFileName = widget.filename.split('\\')[-1]
        cleanFileName = cleanFileName.split('/')[-1]
        dottedParts = cleanFileName.split('.')
    if not allowEmptyPostfix:
        if len(dottedParts) <= 1:
            raise ValueError(_('Missing filename extension.'))
    if cleanup:
        return cleanFileName
    return widget.filename


def changedField(field, value, context=None):
    """Figure if a field's value changed

    Comparing the value of the context attribute and the given value"""
    if context is None:
        context = field.context
    if context is None:
        # IObjectWidget madness
        return True
    if zope.schema.interfaces.IObject.providedBy(field):
        return True

    # Get the datamanager and get the original value
    dm = zope.component.getMultiAdapter(
        (context, field), interfaces.IDataManager)
    # now figure value chaged status
    # Or we can not get the original value, in which case we can not check
    # Or it is an Object, in case we'll never know
    if (not dm.canAccess() or dm.query() != value):
        return True
    else:
        return False


def changedWidget(widget, value, field=None, context=None):
    """figure if a widget's value changed

    Comparing the value of the widget context attribute and the given value"""
    if (interfaces.IContextAware.providedBy(widget)
            and not widget.ignoreContext):
        # if the widget is context aware, figure if it's field changed
        if field is None:
            field = widget.field
        if context is None:
            context = widget.context
        return changedField(field, value, context=context)
    # otherwise we cannot, return 'always changed'
    return True


@zope.interface.implementer(interfaces.IManager)
class Manager(OrderedDict):
    """Non-persistent IManager implementation."""

    def create_according_to_list(self, d, l_):
        """Arrange elements of d according to sorting of l_."""
        # TODO: If we are on Python 3 only reimplement on top of `move_to_end`
        self.clear()
        for key in l_:
            if key in d:
                self[key] = d[key]

    def __getitem__(self, key):
        if key not in self:
            try:
                return getattr(self, key)
            except AttributeError:
                # make sure an KeyError is raised later
                pass
        return super().__getitem__(key)


@zope.interface.implementer(interfaces.ISelectionManager)
class SelectionManager(Manager):
    """Non-persisents ISelectionManager implementation."""

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
            *[item for name, item in self.items()
              if name not in names])

    def copy(self):
        """See interfaces.ISelectionManager"""
        return self.__class__(*self.values())
