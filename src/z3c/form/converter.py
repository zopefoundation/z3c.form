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
"""Data Converters

$Id$
"""
__docformat__ = "reStructuredText"
import datetime
import zope.interface
import zope.component
import zope.schema
import zope.publisher.browser

from z3c.form.i18n import MessageFactory as _
from z3c.form import interfaces


class FieldDataConverter(object):
    """A data converter using the field's ``fromUnicode()`` method."""
    zope.component.adapts(
        zope.schema.interfaces.IFromUnicode, interfaces.IWidget)
    zope.interface.implements(interfaces.IDataConverter)

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return u''
        return unicode(value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        return self.field.fromUnicode(value)

    def __repr__(self):
        return '<DataConverter from %s to %s>' %(
            self.field.__class__.__name__, self.widget.__class__.__name__)


@zope.component.adapter(interfaces.IFieldWidget)
@zope.interface.implementer(interfaces.IDataConverter)
def FieldWidgetDataConverter(widget):
    """Provide a data converter based on a field widget."""
    return zope.component.queryMultiAdapter(
        (widget.field, widget), interfaces.IDataConverter)


class DateDataConverter(FieldDataConverter):
    """A special data converter for dates."""
    zope.component.adapts(
        zope.schema.interfaces.IDate, interfaces.IWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        return datetime.date(*[int(part) for part in value.split('-')])


class TimeDataConverter(FieldDataConverter):
    """A special data converter for times."""
    zope.component.adapts(
        zope.schema.interfaces.ITime, interfaces.IWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        return datetime.time(*[int(part) for part in value.split(':')])


class DatetimeDataConverter(FieldDataConverter):
    """A special data converter for datetimes."""
    zope.component.adapts(
        zope.schema.interfaces.IDatetime, interfaces.IWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        dateString, timeString = value.split(' ')
        dt = [int(part) for part in dateString.split('-')]
        dt += [int(part) for part in timeString.split(':')]
        return datetime.datetime(*dt)


class TimedeltaDataConverter(FieldDataConverter):
    """A special data converter for timedeltas."""
    zope.component.adapts(
        zope.schema.interfaces.ITimedelta, interfaces.IWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        daysString, crap, timeString = value.split(' ')
        days = int(daysString)
        seconds = [int(part)*60**(2-n)
                   for n, part in enumerate(timeString.split(':'))]
        return datetime.timedelta(days, sum(seconds))


class BytesDataConverter(FieldDataConverter):
    """A special data converter for bytes, supporting also FileUpload.

    Since IBytes represents a file upload too, this converter can handle
    zope.publisher.browser.FileUpload object as given value.
    """
    zope.component.adapts(
        zope.schema.interfaces.IBytes, interfaces.IWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value is None or value == '':
            return self.context.missing_value

        if isinstance(value, zope.publisher.browser.FileUpload):
            # By default a IBytes field is used for get a file upload widget.
            # But interfaces extending IBytes do not use file upload widgets.
            # Any way if we get a FileUpload object, we'll convert it.
            # We also store the additional FileUpload values on the widget
            # before we loose them.
            self.widget.headers = value.headers
            self.widget.filename = value.filename
            try:
                seek = value.seek
                read = value.read
            except AttributeError, e:
                raise ValueError(_('Bytes data is not a file object'), e)
            else:
                seek(0)
                data = read()
                if data or getattr(value, 'filename', ''):
                    return data
                else:
                    return self.context.missing_value
        else:
            return unicode(value)


class SequenceDataConverter(FieldDataConverter):
    """Basic data converter for ISequenceWidget."""

    zope.component.adapts(
        zope.schema.interfaces.IField, interfaces.ISequenceWidget)

    def toWidgetValue(self, value):
        """Convert from Python bool to HTML representation."""
        widget = self.widget
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return []
        # Look up the term in the terms
        terms = zope.component.getMultiAdapter(
            (widget.context, widget.request, widget.form, self.field, widget),
             interfaces.ITerms)
        return [terms.getTerm(value).token]

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if not len(value) or value[0] == widget.noValueToken:
            return self.field.missing_value
        terms = zope.component.getMultiAdapter(
            (widget.context, widget.request, widget.form, self.field, widget),
             interfaces.ITerms)
        return terms.getValue(value[0])


class CollectionSequenceDataConverter(FieldDataConverter):
    """A special converter between collections and sequence widgets."""

    zope.component.adapts(
        zope.schema.interfaces.ICollection, interfaces.ISequenceWidget)

    def toWidgetValue(self, value):
        """Convert from Python bool to HTML representation."""
        widget = self.widget
        terms = zope.component.getMultiAdapter(
            (widget.context, widget.request, widget.form, self.field, widget),
             interfaces.ITerms)
        return [terms.getTerm(entry).token for entry in value]

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        terms = zope.component.getMultiAdapter(
            (widget.context, widget.request, widget.form, self.field, widget),
             interfaces.ITerms)
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        return collectionType([terms.getValue(token) for token in value])
