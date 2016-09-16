==============
CheckBoxWidget
==============

Note: the checkbox widget isn't registered for a field by default. You can use
the ``widgetFactory`` argument of a ``IField`` object if you construct fields
or set the custom widget factory on selected fields later.

The ``CheckBoxWidget`` widget renders a checkbox input type field e.g.  <input
type="checkbox" />

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form import interfaces
  >>> from z3c.form.browser import checkbox

The ``CheckboxWidget`` is a widget:

  >>> verifyClass(interfaces.IWidget, checkbox.CheckBoxWidget)
  True

The widget can render a input field only by adapting a request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = checkbox.CheckBoxWidget(request)

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
  ...     'checkbox_input.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='input')

If we render the widget we only get the empty marker:

  >>> print(widget.render())
  <input name="widget.name-empty-marker" type="hidden" value="1" />

Let's provide some values for this widget. We can do this by defining
a vocabulary providing ``ITerms``. This vocabulary uses descriminators
wich will fit for our setup.

  >>> import zope.schema.interfaces
  >>> from zope.schema.vocabulary import SimpleVocabulary
  >>> import z3c.form.term
  >>> class MyTerms(z3c.form.term.ChoiceTermsVocabulary):
  ...     def __init__(self, context, request, form, field, widget):
  ...         self.terms = SimpleVocabulary.fromValues(['yes', 'no'])
  >>> zope.component.provideAdapter(z3c.form.term.BoolTerms,
  ...     adapts=(zope.interface.Interface,
  ...             interfaces.IFormLayer, zope.interface.Interface,
  ...             zope.interface.Interface, interfaces.ICheckBoxWidget))

Now let's try if we get widget values:

  >>> widget.update()
  >>> print(widget.render())
  <span id="widget-id">
   <span class="option">
    <input type="checkbox" id="widget-id-0" name="widget.name:list"
           class="checkbox-widget" value="true" />
    <label for="widget-id-0">
      <span class="label">yes</span>
    </label>
      </span><span class="option">
    <input type="checkbox" id="widget-id-1" name="widget.name:list"
           class="checkbox-widget" value="false" />
    <label for="widget-id-1">
      <span class="label">no</span>
    </label>
   </span>
  </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

The checkbox json_data representation:
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
                'name': 'widget.name:list',
                'value': 'true'},
               {'checked': False,
                'id': 'widget-id-1',
                'label': 'no',
                'name': 'widget.name:list',
                'value': 'false'}],
   'required': False,
   'type': 'check',
   'value': ()}

If we set the value for the widget to ``yes``, we can se that the checkbox
field get rendered with a checked flag:

  >>> widget.value = 'true'
  >>> widget.update()
  >>> print(widget.render())
  <span id="widget-id">
   <span class="option">
    <input type="checkbox" id="widget-id-0" name="widget.name:list"
           class="checkbox-widget" value="true"
           checked="checked" />
    <label for="widget-id-0">
      <span class="label">yes</span>
    </label>
  </span><span class="option">
    <input type="checkbox" id="widget-id-1" name="widget.name:list"
           class="checkbox-widget" value="false" />
    <label for="widget-id-1">
      <span class="label">no</span>
    </label>
   </span>
  </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

The checkbox json_data representation:
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
                'name': 'widget.name:list',
                'value': 'true'},
               {'checked': False,
                'id': 'widget-id-1',
                'label': 'no',
                'name': 'widget.name:list',
                'value': 'false'}],
   'required': False,
   'type': 'check',
   'value': 'true'}

Check HIDDEN_MODE:

  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'checkbox_hidden.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='hidden')

  >>> widget.value = 'true'
  >>> widget.mode = interfaces.HIDDEN_MODE
  >>> print(widget.render())
  <span class="option">
    <input type="hidden" id="widget-id-0" name="widget.name:list"
           class="checkbox-widget" value="true" />
  </span><span class="option">
    <input type="hidden" id="widget-id-1" name="widget.name:list"
           class="checkbox-widget" value="false" />
  </span>

The checkbox json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'hidden',
   'name': 'widget.name',
   'options': [{'checked': True,
                'id': 'widget-id-0',
                'label': 'yes',
                'name': 'widget.name:list',
                'value': 'true'},
               {'checked': False,
                'id': 'widget-id-1',
                'label': 'no',
                'name': 'widget.name:list',
                'value': 'false'}],
   'required': False,
   'type': 'check',
   'value': 'true'}

Make sure that we produce a proper label when we have no title for a term and
the value (which is used as a backup label) contains non-ASCII characters:

  >>> terms = SimpleVocabulary.fromValues([b'yes\012', b'no\243'])
  >>> widget.terms = terms
  >>> widget.update()
  >>> pprint(list(widget.items))
  [{'checked': False,
    'id': 'widget-id-0',
    'label': 'yes\n',
    'name': 'widget.name:list',
    'value': 'yes\n'},
   {'checked': False,
    'id': 'widget-id-1',
    'label': 'no',
    'name': 'widget.name:list',
    'value': 'no...'}]

Note: The "\234" character is interpreted differently in Pytohn 2 and 3
here. (This is mostly due to changes int he SimpleVocabulary code.)


Single Checkbox Widget
----------------------

Instead of using the checkbox widget as an UI component to allow multiple
selection from a list of choices, it can be also used by itself to toggle a
selection, effectively making it a binary selector. So in this case it lends
itself well as a boolean UI input component.

The ``SingleCheckboxWidget`` is a widget:

  >>> verifyClass(interfaces.IWidget, checkbox.SingleCheckBoxWidget)
  True

The widget can render a input field only by adapting a request:

  >>> request = TestRequest()
  >>> widget = checkbox.SingleCheckBoxWidget(request)

Set a name and id for the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

Such a widget provides the ``IWidget`` interface:

  >>> interfaces.IWidget.providedBy(widget)
  True

For there to be a sensible output, we need to give the widget a label:

  >>> widget.label = u'Do you want that?'

  >>> widget.update()
  >>> print(widget.render())
  <span class="option" id="widget-id">
    <input type="checkbox" id="widget-id-0"
           name="widget.name:list"
           class="single-checkbox-widget" value="selected" />
    <label for="widget-id-0">
      <span class="label">Do you want that?</span>
    </label>
  </span>
  <input name="widget.name-empty-marker" type="hidden"
         value="1" />

The checkbox json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': 'Do you want that?',
   'mode': 'input',
   'name': 'widget.name',
   'options': [{'checked': False,
                'id': 'widget-id-0',
                'label': 'Do you want that?',
                'name': 'widget.name:list',
                'value': 'selected'}],
   'required': False,
   'type': 'check',
   'value': ()}

Initially, the box is not checked. Changing the widget value to the selection
value, ...

  >>> widget.value = ['selected']

will make the box checked:

  >>> widget.update()
  >>> print(widget.render())
  <span class="option" id="widget-id">
    <input type="checkbox" id="widget-id-0"
           name="widget.name:list"
           class="single-checkbox-widget" value="selected"
           checked="checked" />
    <label for="widget-id-0">
      <span class="label">Do you want that?</span>
    </label>
  </span>
  <input name="widget.name-empty-marker" type="hidden"
         value="1" />

If you do not specify the label on the widget directly, it is taken from the
field

  >>> from zope.schema import Bool
  >>> widget = checkbox.SingleCheckBoxWidget(request)
  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'
  >>> widget.field = Bool(title=u"Do you REALLY want that?")
  >>> widget.update()
  >>> print(widget.render())
  <span class="option" id="widget-id">
    <input type="checkbox" id="widget-id-0"
           name="widget.name:list"
           class="single-checkbox-widget" value="selected" />
    <label for="widget-id-0">
      <span class="label">Do you REALLY want that?</span>
    </label>
  </span>
  <input name="widget.name-empty-marker" type="hidden"
         value="1" />

Check HIDDEN_MODE:

  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'checkbox_hidden.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='hidden')

  >>> widget.value = 'true'
  >>> widget.mode = interfaces.HIDDEN_MODE
  >>> print(widget.render())
  <span class="option">
    <input type="hidden" id="widget-id-0"
           name="widget.name:list"
           class="single-checkbox-widget" value="selected" />
  </span>


Term with non ascii __str__
---------------------------

Check if a term which __str__ returns non ascii string does not crash the update method

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form import interfaces
  >>> from z3c.form.browser import checkbox
  >>> from z3c.form.testing import TestRequest

  >>> request = TestRequest()

  >>> widget = checkbox.CheckBoxWidget(request)
  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

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
  ...             zope.interface.Interface, interfaces.ICheckBoxWidget))
  >>> widget.update()
  >>> print(widget.render())
  <html>
    <body>
      <span id="widget-id">
       <span class="option">
        <input class="checkbox-widget" id="widget-id-0" name="widget.name:list" type="checkbox" value="one">
        <label for="widget-id-0">
          <span class="label">One</span>
        </label>
      </span>
      <span class="option">
        <input class="checkbox-widget" id="widget-id-1" name="widget.name:list" type="checkbox" value="two">
        <label for="widget-id-1">
          <span class="label">Two</span>
        </label>
       </span>
      </span>
      <input name="widget.name-empty-marker" type="hidden" value="1">
    </body>
  </html>
