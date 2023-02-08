import zope.interface

from z3c.form.interfaces import IDataExtractedEvent


@zope.interface.implementer(IDataExtractedEvent)
class DataExtractedEvent:

    def __init__(self, data, errors, form):
        self.data = data
        self.errors = errors
        self.form = form
