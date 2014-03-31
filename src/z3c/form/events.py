from z3c.form.interfaces import IDataExtractedEvent
from zope.interface import implements


class DataExtractedEvent(object):
    implements(IDataExtractedEvent)

    def __init__(self, data, errors, form):
        self.data = data
        self.errors = errors
        self.form = form
