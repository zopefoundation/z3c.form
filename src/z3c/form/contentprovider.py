import zope.component
import zope.interface
import zope.location
from zope.contentprovider.interfaces import IContentProvider

from z3c.form import interfaces
from z3c.form.error import MultipleErrors
from z3c.form.field import FieldWidgets
from z3c.form.interfaces import IContentProviders


class BaseProvider:
    __slots__ = ('position')


lookup_ = BaseProvider()


@zope.interface.implementer(IContentProviders)
class ContentProviders(dict):

    def __init__(self, names=None):
        super().__init__()
        if names is not None:
            for position, name in enumerate(names):
                self[name] = lookup_

    def __setitem__(self, key, value):
        factory = ContentProviderFactory(factory=value, name=key)
        super().__setitem__(key, factory)


class ContentProviderFactory:

    def __init__(self, factory, name):
        self.factory = factory
        self.name = name
        self.position = getattr(factory, 'position', None)

    def __call__(self, manager):
        if self.factory != lookup_:
            contentProvider = self.factory(
                manager.content, manager.request, manager.form)
        else:
            contentProvider = zope.component.getMultiAdapter(
                (manager.content, manager.request, manager.form),
                IContentProvider, self.name)
        return contentProvider


@zope.interface.implementer_only(interfaces.IWidgets)
class FieldWidgetsAndProviders(FieldWidgets):
    zope.component.adapts(
        interfaces.IFieldsAndContentProvidersForm,
        interfaces.IFormLayer,
        zope.interface.Interface)

    def update(self):
        super().update()
        uniqueOrderedKeys = list(self.keys())
        d = {}
        d.update(self)
        for name in self.form.contentProviders:
            factory = self.form.contentProviders[name]
            if factory.position is None:
                raise ValueError(
                    "Position of the following"
                    " content provider should be an integer: '%s'." %
                    name)
            contentProvider = factory(self)
            shortName = name
            contentProvider.update()
            uniqueOrderedKeys.insert(factory.position, shortName)
            d[shortName] = contentProvider
            zope.location.locate(contentProvider, self, shortName)
        self.create_according_to_list(d, uniqueOrderedKeys)

    def extract(self):
        """See interfaces.IWidgets"""
        data = {}
        errors = ()
        for name, widget in self.items():
            if IContentProvider.providedBy(widget):
                continue
            if widget.mode == interfaces.DISPLAY_MODE:
                continue
            value = widget.field.missing_value
            try:
                widget.setErrors = self.setErrors
                raw = widget.extract()
                if raw is not interfaces.NO_VALUE:
                    value = interfaces.IDataConverter(widget).toFieldValue(raw)
                zope.component.getMultiAdapter(
                    (self.content,
                     self.request,
                     self.form,
                     getattr(widget, 'field', None),
                     widget),
                    interfaces.IValidator).validate(value)
            except (zope.interface.Invalid,
                    ValueError, MultipleErrors) as error:
                view = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     self.form, self.content), interfaces.IErrorViewSnippet)
                view.update()
                if self.setErrors:
                    widget.error = view
                errors += (view,)
            else:
                name = widget.__name__
                data[name] = value
        for error in self.validate(data):
            view = zope.component.getMultiAdapter(
                (error, self.request, None, None, self.form, self.content),
                interfaces.IErrorViewSnippet)
            view.update()
            errors += (view,)
        if self.setErrors:
            self.errors = errors
        return data, errors
