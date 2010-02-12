import zope.component
import zope.interface
import zope.location
import zope.schema.interfaces

from z3c.form.field import FieldWidgets
from z3c.form import interfaces, util
from z3c.form.widget import AfterWidgetUpdateEvent


class ContentProviders(dict):

    def __getitem__(self, key):
        factory = super(ContentProviders, self).__getitem__(key)
        return ContentProviderFactory(name=key, factory=factory)


class ContentProviderFactory(object):

    def __init__(self, factory, *args, **kwargs):
        self.factory = factory
        self.args = args
        self.kwargs = kwargs

    def __call__(self, manager):
        contentProvider = self.factory(manager.form, manager.request, manager.form)
        return contentProvider


class FieldWidgetsAndProviders(FieldWidgets):
    zope.component.adapts(
        interfaces.IWidgetsForm, interfaces.IFormLayer, zope.interface.Interface)
    zope.interface.implementsOnly(interfaces.IWidgets)

    def update(self):
        super(FieldWidgetsAndProviders, self).update()
        prefix = util.expandPrefix(self.form.prefix)
        prefix += util.expandPrefix(self.prefix)

        uniqueOrderedKeys = self._data_keys
        for name in self.form.contentProviders:
            factory = self.form.contentProviders[name]
            contentProvider = factory(self)
            newWidget = True
            ignoreContext = True
            # Step 1: Determine the mode of the contentProvider.
            mode = self.mode
            # Step 2: Get the widget for the given field.
            shortName = name
            #widget.name = prefix + shortName
            contentProvider.id = (prefix + shortName).replace('.', '-')
            # Step 4: Set the context
            contentProvider.context = self.content
            # Step 5: Set the form
            contentProvider.form = self.form
            # Optimization: Set both interfaces here, rather in step 4 and 5:
            # ``alsoProvides`` is quite slow
            zope.interface.alsoProvides(
                contentProvider, interfaces.IContextAware, interfaces.IFormAware)
            # Step 6: Set some variables
            contentProvider.ignoreContext = ignoreContext
            contentProvider.ignoreRequest = self.ignoreRequest
            # Step 7: Set the mode of the widget
            contentProvider.mode = mode
            # Step 8: Update the widget
            contentProvider.update()
            zope.event.notify(AfterWidgetUpdateEvent(contentProvider))
            # Step 9: Add the widget to the manager
            uniqueOrderedKeys.append(shortName)
            if newWidget:
                self._data_values.append(contentProvider)
                self._data[shortName] = contentProvider
                zope.location.locate(contentProvider, self, shortName)
            # allways ensure that we add all keys and keep the order given from
            # button items
            self._data_keys = uniqueOrderedKeys
