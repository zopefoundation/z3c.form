from z3c.form.interfaces import IDataExtractedEvent
from zope.interface import implementer


@implementer(IDataExtractedEvent)
class DataExctractedEvent(object):
    def __init__(self, data, errors, form):
        self.data = data
        self.errors = errors
        self.form = form
