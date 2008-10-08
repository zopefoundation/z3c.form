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
    _value = interfaces.NOVALUE

    #def updateWidgets(self):
    #    #if self.subform is None:
    #    if self._value is not interfaces.NOVALUE:
    #        subobj = self._value
    #    else:
    #        try:
    #            subobj = getattr(self.context, self.field.__name__)
    #        except AttributeError:
    #            #lame, mostly for adding
    #            subobj = self.context
    #    self.subform = ObjectSubForm(subobj, self)
    #    #self.subform = ObjectSubForm(self.value, self)
    #    self.subform.update()
    def updateWidgets(self):
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
        self.subform.update()

    def update(self):
        super(ObjectWidget, self).update()
        self.updateWidgets()

    #@apply
    #def value():
    #    """This invokes updateWidgets on any value change e.g. update/extract."""
    #    def get(self):
    #        return self.extract()
    #    def set(self, value):
    #        if isinstance(value, tuple):
    #            from pub.dbgpclient import brk; brk('192.168.32.1')
    #
    #        self._value = value
    #        # ensure that we apply our new values to the widgets
    #        self.updateWidgets()
    #    return property(get, set)

    def extract(self, default=interfaces.NOVALUE):
        if self.name+'-empty-marker' in self.request:
            self.updateWidgets()
            rv=self.subform.extractData()
            return rv
        else:
            return default

@zope.component.adapter(zope.schema.interfaces.IObject, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def ObjectFieldWidget(field, request):
    """IFieldWidget factory for IObjectWidget."""
    return FieldWidget(field, ObjectWidget(request))
