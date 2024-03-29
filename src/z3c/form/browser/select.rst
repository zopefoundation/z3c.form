Select Widget
-------------

The select widget allows you to select one or more values from a set of given
options. The "SELECT" and "OPTION" elements are described here:

http://www.w3.org/TR/1999/REC-html401-19991224/interact/forms.html#edef-SELECT

As for all widgets, the select widget must provide the new ``IWidget``
interface:

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form import interfaces
  >>> from z3c.form.browser import select

  >>> verifyClass(interfaces.IWidget, select.SelectWidget)
  True

The widget can be instantiated only using the request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = select.SelectWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

We also need to register the template for at least the widget and request:

  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form.testing import getPath
  >>> from z3c.form.widget import WidgetTemplateFactory

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('select_input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.ISelectWidget),
  ...     IPageTemplate, name=interfaces.INPUT_MODE)

If we render the widget we get an empty widget:

  >>> print(widget.render())
  <select id="widget-id" name="widget.name:list"
          class="select-widget" size="1">
  </select>
  <input name="widget.name-empty-marker" type="hidden"
         value="1" />

Let's provide some values for this widget. We can do this by defining a source
providing ``ITerms``. This source uses descriminators which will fit our setup.

  >>> import zope.schema.interfaces
  >>> from zope.schema.vocabulary import SimpleVocabulary
  >>> import z3c.form.term

  >>> class SelectionTerms(z3c.form.term.Terms):
  ...     def __init__(self, context, request, form, field, widget):
  ...         self.terms = SimpleVocabulary.fromValues(['a', 'b', 'c'])

  >>> zope.component.provideAdapter(SelectionTerms,
  ...     (None, interfaces.IFormLayer, None, None, interfaces.ISelectWidget) )

Now let's try if we get widget values:

  >>> widget.update()
  >>> print(widget.render())
  <select id="widget-id" name="widget.name:list"
          class="select-widget" size="1">
  <option id="widget-id-novalue" selected="selected" value="--NOVALUE--">No value</option>
  <option id="widget-id-0" value="a">a</option>
  <option id="widget-id-1" value="b">b</option>
  <option id="widget-id-2" value="c">c</option>
  </select>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

Select json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'options': [{'content': 'No value',
                'id': 'widget-id-novalue',
                'selected': True,
                'value': '--NOVALUE--'},
               {'content': 'a',
                'id': 'widget-id-0',
                'selected': False,
                'value': 'a'},
               {'content': 'b',
                'id': 'widget-id-1',
                'selected': False,
                'value': 'b'},
               {'content': 'c',
                'id': 'widget-id-2',
                'selected': False,
                'value': 'c'}],
   'required': False,
   'type': 'select',
   'value': ()}

If we select item "b", then it should be selected:

  >>> widget.value = ['b']
  >>> widget.update()
  >>> print(widget.render())
  <select id="widget-id" name="widget.name:list"
          class="select-widget" size="1">
  <option id="widget-id-novalue" value="--NOVALUE--">No value</option>
  <option id="widget-id-0" value="a">a</option>
  <option id="widget-id-1" value="b" selected="selected">b</option>
  <option id="widget-id-2" value="c">c</option>
  </select>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

Select json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'options': [{'content': 'No value',
                'id': 'widget-id-novalue',
                'selected': False,
                'value': '--NOVALUE--'},
               {'content': 'a',
                'id': 'widget-id-0',
                'selected': False,
                'value': 'a'},
               {'content': 'b',
                'id': 'widget-id-1',
                'selected': True,
                'value': 'b'},
               {'content': 'c',
                'id': 'widget-id-2',
                'selected': False,
                'value': 'c'}],
   'required': False,
   'type': 'select',
   'value': ['b']}

Let's see what happens if we have values that are not in the vocabulary:

  >>> widget.value = ['x', 'y']
  >>> widget.update()
  >>> print(widget.render())
  <select id="widget-id" name="widget.name:list"
          class="select-widget" size="1">
  <option id="widget-id-novalue" value="--NOVALUE--">No value</option>
  <option id="widget-id-0" value="a">a</option>
  <option id="widget-id-1" value="b">b</option>
  <option id="widget-id-2" value="c">c</option>
  </select>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

Let's now make sure that we can extract user entered data from a widget:

  >>> widget.request = TestRequest(form={'widget.name': ['c']})
  >>> widget.update()
  >>> widget.extract()
  ('c',)

When "No value" is selected, then no verification against the terms is done:

  >>> widget.request = TestRequest(form={'widget.name': ['--NOVALUE--']})
  >>> widget.update()
  >>> widget.extract(default=1)
  ('--NOVALUE--',)

Unfortunately, when nothing is selected, we do not get an empty list sent into
the request, but simply no entry at all. For this we have the empty marker, so
that:

  >>> widget.request = TestRequest(form={'widget.name-empty-marker': '1'})
  >>> widget.update()
  >>> widget.extract()
  ()

If nothing is found in the request, the default is returned:

  >>> widget.request = TestRequest()
  >>> widget.update()
  >>> widget.extract(default=1)
  1

Let's now make sure that a bogus value causes extract to return the default as
described by the interface:

  >>> widget.request = TestRequest(form={'widget.name': ['x']})
  >>> widget.update()
  >>> widget.extract(default=1)
  1


Custom No Value Messages
########################

Additionally to the standard dynamic attribute values, the select widget also
allows dynamic values for the "No value message". Initially, we have the
default message:

  >>> widget.noValueMessage
  'No value'

Let's now register an attribute value:

  >>> from z3c.form.widget import StaticWidgetAttribute
  >>> NoValueMessage = StaticWidgetAttribute('- nothing -')

  >>> import zope.component
  >>> zope.component.provideAdapter(NoValueMessage, name='noValueMessage')

After updating the widget, the no value message changed to the value provided
by the adapter:

  >>> widget.update()
  >>> widget.noValueMessage
  '- nothing -'

Select json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'options': [{'content': '- nothing -',
                'id': 'widget-id-novalue',
                'selected': True,
                'value': '--NOVALUE--'},
               {'content': 'a',
                'id': 'widget-id-0',
                'selected': False,
                'value': 'a'},
               {'content': 'b',
                'id': 'widget-id-1',
                'selected': False,
                'value': 'b'},
               {'content': 'c',
                'id': 'widget-id-2',
                'selected': False,
                'value': 'c'}],
   'required': False,
   'type': 'select',
   'value': ()}

Explicit Selection Prompt
#########################

In certain scenarios it is desirable to ask the user to select a value and
display it as the first choice, such as "please select a value". In those
cases you just have to set the ``prompt`` attribute to ``True``:

  >>> widget.prompt = True
  >>> widget.update()
  >>> print(widget.render())
  <select id="widget-id" name="widget.name:list"
          class="select-widget" size="1">
  <option id="widget-id-novalue" value="--NOVALUE--"
          selected="selected">Select a value ...</option>
  <option id="widget-id-0" value="a">a</option>
  <option id="widget-id-1" value="b">b</option>
  <option id="widget-id-2" value="c">c</option>
  </select>
  <input name="widget.name-empty-marker" type="hidden"
         value="1" />

As you can see, even though the field is not required, only the explicit
prompt is shown. However, the prompt will also be shown if the field is
required:

  >>> widget.required = True
  >>> widget.update()
  >>> print(widget.render())
  <select id="widget-id" name="widget.name:list"
          class="select-widget required" size="1">
  <option id="widget-id-novalue" value="--NOVALUE--"
          selected="selected">Select a value ...</option>
  <option id="widget-id-0" value="a">a</option>
  <option id="widget-id-1" value="b">b</option>
  <option id="widget-id-2" value="c">c</option>
  </select>
  <input name="widget.name-empty-marker" type="hidden"
         value="1" />

Since the prompy uses the "No value" as the value for the selection, all
behavior is identical to selecting "No value". As for the no-value message,
the prompt message, which is available under

  >>> widget.promptMessage
  'Select a value ...'

can also be changed using an attribute value adapter:

  >>> PromptMessage = StaticWidgetAttribute('Please select a value')
  >>> zope.component.provideAdapter(PromptMessage, name='promptMessage')

So after updating the widget you have the custom value:

  >>> widget.update()
  >>> widget.promptMessage
  'Please select a value'

Additionally, the select widget also allows dynamic value for the ``prompt``
attribute . Initially, value is ``False``:

  >>> widget.prompt = False
  >>> widget.prompt
  False

Let's now register an attribute value:

  >>> from z3c.form.widget import StaticWidgetAttribute
  >>> AllowPrompt = StaticWidgetAttribute(True)

  >>> import zope.component
  >>> zope.component.provideAdapter(AllowPrompt, name='prompt')

After updating the widget, the value for the prompt attribute changed to the
value provided by the adapter:

  >>> widget.update()
  >>> widget.prompt
  True

Display Widget
##############

The select widget comes with a template for ``DISPLAY_MODE``.  Let's
register it first:

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('select_display.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.ISelectWidget),
  ...     IPageTemplate, name=interfaces.DISPLAY_MODE)

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> widget.value = ['b', 'c']
  >>> widget.update()
  >>> print(widget.render())
  <span id="widget-id" class="select-widget required">
    <span class="selected-option">b</span>,
    <span class="selected-option">c</span>
  </span>

Let's see what happens if we have values that are not in the vocabulary:

  >>> widget.value = ['x', 'y']
  >>> widget.update()
  >>> print(widget.render())
  <span id="widget-id" class="select-widget required"></span>

Hidden Widget
#############

The select widget comes with a template for ``HIDDEN_MODE``.  Let's
register it first:

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('select_hidden.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.ISelectWidget),
  ...     IPageTemplate, name=interfaces.HIDDEN_MODE)

We can now set our widget's mode to hidden and render it:

  >>> widget.mode = interfaces.HIDDEN_MODE
  >>> widget.value = ['b']
  >>> widget.update()
  >>> print(widget.render())
  <input type="hidden" name="widget.name:list"
         class="hidden-widget" value="b" id="widget-id-1" />
  <input name="widget.name-empty-marker" type="hidden"
         value="1" />

Let's see what happens if we have values that are not in the vocabulary:

  >>> widget.value = ['x', 'y']
  >>> widget.update()
  >>> print(widget.render())
  <input name="widget.name-empty-marker" type="hidden"
         value="1" />
