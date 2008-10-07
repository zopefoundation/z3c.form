__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form import form, interfaces
from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser import widget

from z3c.form.object import ObjectSubForm

class ObjectWidget(widget.HTMLFormElement, Widget):
    zope.interface.implementsOnly(interfaces.IObjectWidget)

    klass = u'object-widget'
    subform = None

    def _makeSubform(self):
        #if self.subform is None:
        try:
            subobj = getattr(self.context, self.field.__name__)
        except AttributeError:
            if self.value:
                subobj = self.value
            else:
                #lame, mostly for adding
                subobj = self.context
        self.subform = ObjectSubForm(subobj, self)
        #self.subform = ObjectSubForm(self.value, self)

    def update(self):
        super(ObjectWidget, self).update()

        self._makeSubform()
        self.subform.update()

    def extract(self, default=interfaces.NOVALUE):
        if self.name+'-empty-marker' in self.request:
            self._makeSubform()
            self.subform.update()
            rv=self.subform.extractData()
            return rv
        else:
            return default

@zope.component.adapter(zope.schema.interfaces.IObject, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def ObjectFieldWidget(field, request):
    """IFieldWidget factory for IObjectWidget."""
    return FieldWidget(field, ObjectWidget(request))
