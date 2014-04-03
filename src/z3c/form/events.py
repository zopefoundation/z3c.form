from z3c.form.interfaces import IDataExtractedEvent
import zope.interface


@zope.interface.implementer(IDataExtractedEvent)
class DataExtractedEvent(object):

    def __init__(self, data, errors, form):
        self.data = data
        self.errors = errors
        self.form = form
