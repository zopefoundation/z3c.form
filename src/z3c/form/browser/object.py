__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form import action, button, form, interfaces
from z3c.form.i18n import MessageFactory as _
from z3c.form import interfaces
from z3c.form.widget import Widget, FieldWidget
from z3c.form.field import FieldWidgets, Fields
from z3c.form.browser import widget
from z3c.form.subform import EditSubForm

class ObjectSubForm(form.BaseForm):
    zope.interface.implements(interfaces.ISubForm)

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    def __init__(self, context, parentWidget):
        self.context = context
        self.request = parentWidget.request
        self.parentWidget = parentWidget
        self.parentForm = self.__parent__ = parentWidget.form

    def _validate(self):
        for widget in self.widgets.values():
            try:
                # convert widget value to field value
                converter = interfaces.IDataConverter(widget)
                value = converter.toFieldValue(widget.value)
                # validate field value
                zope.component.getMultiAdapter(
                    (self.context,
                     self.request,
                     self.parentWidget.form,
                     getattr(widget, 'field', None),
                     widget),
                    interfaces.IValidator).validate(value)
            except (zope.schema.ValidationError, ValueError), error:
                # on exception, setup the widget error message
                view = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     self.parentWidget.form, self.context),
                    interfaces.IErrorViewSnippet)
                view.update()
                widget.error = view

    def update(self):
        self.fields = Fields(self.parentWidget.field.schema)

        self.mode = self.parentWidget.mode
        self.ignoreContext = self.parentWidget.ignoreContext
        self.ignoreRequest = self.parentWidget.ignoreRequest
        self.prefix = self.parentWidget.field.__name__

        if interfaces.IFormAware.providedBy(self.parentWidget):
            self.ignoreReadonly = self.parentWidget.form.ignoreReadonly

        super(ObjectSubForm, self).update()

        self._validate()


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
