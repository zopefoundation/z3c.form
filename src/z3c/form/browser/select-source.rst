=====================================
Customizing widget lookup for IChoice
=====================================

Widgets for fields implementing IChoice are looked up not only according to the
field, but also according to the source used by the field.

  >>> import z3c.form.testing
  >>> import zope.interface
  >>> import zope.component
  >>> from z3c.form import interfaces
  >>> from z3c.form.testing import TestRequest

  >>> z3c.form.testing.setupFormDefaults()
  >>> def setupWidget(field):
  ...     request = TestRequest()
  ...     widget = zope.component.getMultiAdapter((field, request),
  ...         interfaces.IFieldWidget)
  ...     widget.id = 'foo'
  ...     widget.name = 'bar'
  ...     return widget

We define a sample field and source:

  >>> from zope.schema import vocabulary
  >>> terms = [vocabulary.SimpleTerm(*value) for value in
  ...          [(True, 'yes', 'Yes'), (False, 'no', 'No')]]
  >>> vocabulary = vocabulary.SimpleVocabulary(terms)
  >>> field = zope.schema.Choice(default=True, vocabulary=vocabulary)

The default widget is the SelectWidget:

  >>> widget = setupWidget(field)
  >>> type(widget)
  <class 'z3c.form.browser.select.SelectWidget'>

But now we define a marker interface and have our source provide it:

  >>> from z3c.form.widget import FieldWidget
  >>> class ISampleSource(zope.interface.Interface):
  ...     pass
  >>> zope.interface.alsoProvides(vocabulary, ISampleSource)

We can then create and register a special widget for fields using sources with
the ISampleSource marker:

  >>> class SampleSelectWidget(z3c.form.browser.select.SelectWidget):
  ...     pass
  >>> def SampleSelectFieldWidget(field, source, request):
  ...     return FieldWidget(field, SampleSelectWidget(request))
  >>> zope.component.provideAdapter(
  ...   SampleSelectFieldWidget,
  ...   (zope.schema.interfaces.IChoice, ISampleSource, interfaces.IFormLayer),
  ...   interfaces.IFieldWidget)

If we now look up the widget for the field, we get the specialized widget:

  >>> widget = setupWidget(field)
  >>> type(widget)
  <class 'SampleSelectWidget'>

Backwards compatibility
-----------------------

To maintain backwards compatibility, SelectFieldWidget() still can be called
without passing a source:

  >>> import z3c.form.browser.select
  >>> request = TestRequest()
  >>> widget = z3c.form.browser.select.SelectFieldWidget(field, request)
  >>> type(widget)
  <class 'z3c.form.browser.select.SelectWidget'>
