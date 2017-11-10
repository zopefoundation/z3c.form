===========
RadioWidget
===========

The RadioWidget renders a radio input type field e.g. <input type="radio" />

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form import interfaces
  >>> from z3c.form.browser import radio

The RadioWidget is a widget:

 >>> verifyClass(interfaces.IWidget, radio.RadioWidget)
  True

The widget can render a input field only by adapting a request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = radio.RadioWidget(request)

Set a name and id for the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

Such a field provides IWidget:

 >>> interfaces.IWidget.providedBy(widget)
  True

We also need to register the template for at least the widget and request:

  >>> import os.path
  >>> import zope.interface
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> import z3c.form.browser
  >>> import z3c.form.widget
  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'radio_input.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='input')
  >>> template_single = os.path.join(
  ...     os.path.dirname(z3c.form.browser.__file__),
  ...     'radio_input_single.pt')
  >>> zope.component.provideAdapter(
  ...     z3c.form.widget.WidgetTemplateFactory(template_single),
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='input_single')

If we render the widget we only get the empty marker:

  >>> print(widget.render())
  <input name="widget.name-empty-marker" type="hidden" value="1" />

Let's provide some values for this widget. We can do this by defining a source
providing ITerms. This source uses discriminators which will fit for our setup.

  >>> import zope.schema.interfaces
  >>> import z3c.form.term
  >>> from zc.sourcefactory.basic import BasicSourceFactory
  >>> class YesNoSourceFactory(BasicSourceFactory):
  ...     def getValues(self):
  ...         return ['yes', 'no']
  >>> class MyTerms(z3c.form.term.ChoiceTermsSource):
  ...     def __init__(self, context, request, form, field, widget):
  ...         self.terms = YesNoSourceFactory()
  >>> zope.component.provideAdapter(z3c.form.term.BoolTerms,
  ...     adapts=(zope.interface.Interface,
  ...             interfaces.IFormLayer, zope.interface.Interface,
  ...             zope.interface.Interface, interfaces.IRadioWidget))

Now let's try if we get widget values:

  >>> widget.update()
  >>> print(widget.render())
  <span class="option">
    <label for="widget-id-0">
      <input type="radio" id="widget-id-0" name="widget.name"
             class="radio-widget" value="true" />
      <span class="label">yes</span>
    </label>
  </span><span class="option">
    <label for="widget-id-1">
      <input type="radio" id="widget-id-1" name="widget.name"
             class="radio-widget" value="false" />
      <span class="label">no</span>
    </label>
  </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

The radio json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'options': [{'checked': False,
                'id': 'widget-id-0',
                'label': 'yes',
                'name': 'widget.name',
                'value': 'true'},
                {'checked': False,
                'id': 'widget-id-1',
                'label': 'no',
                'name': 'widget.name',
                'value': 'false'}],
   'required': False,
   'type': 'radio',
   'value': ()}

If we set the value for the widget to ``yes``, we can se that the radio field
get rendered with a checked flag:

  >>> widget.value = 'true'
  >>> widget.update()
  >>> print(widget.render())
  <span class="option">
    <label for="widget-id-0">
      <input type="radio" id="widget-id-0" name="widget.name"
             class="radio-widget" value="true" checked="checked" />
      <span class="label">yes</span>
    </label>
  </span><span class="option">
    <label for="widget-id-1">
      <input type="radio" id="widget-id-1" name="widget.name"
             class="radio-widget" value="false" />
      <span class="label">no</span>
    </label>
  </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

The radio json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'options': [{'checked': True,
                'id': 'widget-id-0',
                'label': 'yes',
                'name': 'widget.name',
                'value': 'true'},
                {'checked': False,
                'id': 'widget-id-1',
                'label': 'no',
                'name': 'widget.name',
                'value': 'false'}],
   'required': False,
   'type': 'radio',
   'value': 'true'}

We can also render the input elements for each value separately:

   >>> print(widget.renderForValue('true'))
   <input id="widget-id-0" name="widget.name" class="radio-widget"
          value="true" checked="checked" type="radio" />

   >>> print(widget.renderForValue('false'))
   <input id="widget-id-1" name="widget.name" class="radio-widget"
          value="false" type="radio" />

Additionally we can render the "no value" input element used for non-required fields:

  >>> from z3c.form.widget import SequenceWidget
  >>> print(SequenceWidget.noValueToken)
  --NOVALUE--
  >>> print(widget.renderForValue(SequenceWidget.noValueToken))
  <input id="widget-id-novalue" name="widget.name" class="radio-widget"
          value="--NOVALUE--" type="radio" />

Check HIDDEN_MODE:

  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'radio_hidden.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='hidden')

  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'radio_hidden_single.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='hidden_single')

  >>> widget.value = ['true']
  >>> widget.mode = interfaces.HIDDEN_MODE
  >>> print(widget.render())
  <input id="widget-id-0" name="widget.name" value="true"
         class="hidden-widget" type="hidden" />

And independently:

   >>> print(widget.renderForValue('true'))
   <input id="widget-id-0" name="widget.name" value="true"
          class="hidden-widget" type="hidden" />

The unchecked values do not need a hidden field, hence they are empty:

   >>> print(widget.renderForValue('false'))


Check DISPLAY_MODE:

  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'radio_display.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='display')

  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'radio_display_single.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='display_single')

  >>> widget.value = ['true']
  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="widget-id" class="radio-widget">
    <span class="selected-option">yes</span>
  </span>

And independently:

   >>> print(widget.renderForValue('true'))
   <span id="widget-id" class="radio-widget"><span class="selected-option">yes</span></span>

Again, unchecked values are not displayed:

   >>> print(widget.renderForValue('false'))


Make sure that we produce a proper label when we have no title for a term and
the value (which is used as a backup label) contains non-ASCII characters:

  >>> from zope.schema.vocabulary import SimpleVocabulary
  >>> terms = SimpleVocabulary.fromValues([b'yes\012', b'no\243'])
  >>> widget.terms = terms
  >>> widget.update()
  >>> pprint(list(widget.items))
  [{'checked': False,
    'id': 'widget-id-0',
    'label': 'yes\n',
    'name': 'widget.name',
    'value': 'yes\n'},
   {'checked': False,
    'id': 'widget-id-1',
    'label': 'no',
    'name': 'widget.name',
    'value': 'no...'}]

Note: The "\234" character is interpreted differently in Pytohn 2 and 3
here. (This is mostly due to changes int he SimpleVocabulary code.)

Term with non ascii __str__
---------------------------

Check if a term which __str__ returns non ascii string does not crash the update method

  >>> request = TestRequest()
  >>> widget = radio.RadioWidget(request)
  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'
  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'radio_input.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='input')

  >>> import zope.schema.interfaces
  >>> from zope.schema.vocabulary import SimpleVocabulary,SimpleTerm
  >>> import z3c.form.term
  >>> class ObjWithNonAscii__str__:
  ...     def __str__(self):
  ...         return 'héhé!'
  >>> class MyTerms(z3c.form.term.ChoiceTermsVocabulary):
  ...     def __init__(self, context, request, form, field, widget):
  ...         self.terms = SimpleVocabulary([
  ...             SimpleTerm(ObjWithNonAscii__str__(), 'one', 'One'),
  ...             SimpleTerm(ObjWithNonAscii__str__(), 'two', 'Two'),
  ...         ])
  >>> zope.component.provideAdapter(MyTerms,
  ...     adapts=(zope.interface.Interface,
  ...             interfaces.IFormLayer, zope.interface.Interface,
  ...             zope.interface.Interface, interfaces.IRadioWidget))
  >>> widget.update()
  >>> print(widget.render())
  <html>
    <body>
      <span class="option">
        <label for="widget-id-0">
          <input class="radio-widget" id="widget-id-0" name="widget.name" type="radio" value="one">
          <span class="label">One</span>
        </label>
      </span>
      <span class="option">
        <label for="widget-id-1">
          <input class="radio-widget" id="widget-id-1" name="widget.name" type="radio" value="two">
          <span class="label">Two</span>
        </label>
      </span>
      <input name="widget.name-empty-marker" type="hidden" value="1">
    </body>
  </html>
