=======
Widgets
=======

Widgets are small UI components that accept and process the textual user
input. The only responsibility of a widget is to represent a value to the
user, allow it to be modified and then return a new value. Good examples of
widgets include the Qt widgets and HTML widgets. The widget is not responsible
for converting its value to the desired internal value or validate the
incoming data. These responsibilities are passed data converters and
validators, respectively.

There are several problems that can be identified in the original Zope 3 widget
implementation located at ``zope.app.form``.

(1) Field Dependence -- Widgets are always views of fields. While this might
    be a correct choice for a high-level API, it is fundamentally wrong. It
    disallows us to use widgets without defining fields. This also couples
    certain pieces of information too tightly to the field, especially, value
    retrieval from and storage to the context, validation and raw data
    conversion.

(2) Form Dependence -- While widgets do not have to be located within a form,
    they are usually tightly coupled to it. It is very difficult to use
    widgets outside the context of a form.

(3) Traversability -- Widgets cannot be traversed, which means that they
    cannot interact easily using Javascript. This is not a fundamental
    problem, but simply a lack of the current design to recognize that small
    UI components must also be traversable and thus have a URI.

(4) Customizability -- A consequence of issue (1) is that widgets are not
    customizable enough. Implementing real-world projects has shown that
    widgets often want a very fine-grained ability to customize values. A
    prime example is the label. Because the label of a widget is retrieved
    from the field title, it is impossible to provide an alternative label for
    a widget. While the label could be changed from the form, this would
    require rewriting the entire form to change a label. Instead, we often
    endde up writing cusom schemas.

(5) Flexibility -- Oftentimes it is desired to have one widget, but multiple
    styles of representation. For example, in one scenario the widget uses a
    plain HTML widget and in another a fancy JavaScript widget is used. The
    current implementation makes it very hard to provide alternative styles
    for a widget.


Creating and Using Simple Widgets
---------------------------------

When using the widget API by itself, the simplest way to use it is to just
instantiate it using the request:

  >>> from z3c.form.testing import TestRequest
  >>> from z3c.form import widget
  >>> request = TestRequest()
  >>> age = widget.Widget(request)

In this case we instantiated a generic widget. A full set of simple
browser-based widgets can be found in the ``browser/`` package. Since no
helper components are around to fill the attributes of the widget, we have to
do it by hand:

  >>> age.name = 'age'
  >>> age.label = 'Age'
  >>> age.value = '39'

The most important attributes are the "name" and the "value". The name is used
to identify the widget within the form. The value is either the value to be
manipulated or the default value. The value must be provided in the form the
widget needs it. It is the responsibility of a data converter to convert
between the widget value and the desired internal value.

Before we can render the widget, we have to register a template for the
widget. The first step is to define the template:

  >>> import tempfile
  >>> textWidgetTemplate = tempfile.mktemp('text.pt')
  >>> with open(textWidgetTemplate, 'w') as file:
  ...     _ = file.write('''
  ... <html xmlns="http://www.w3.org/1999/xhtml"
  ...       xmlns:tal="http://xml.zope.org/namespaces/tal"
  ...       tal:omit-tag="">
  ...    <input type="text" name="" value=""
  ...           tal:attributes="name view/name; value view/value;" />
  ... </html>
  ... ''')

Next, we have to create a template factory for the widget:

  >>> from z3c.form.widget import WidgetTemplateFactory
  >>> factory = WidgetTemplateFactory(
  ...     textWidgetTemplate, widget=widget.Widget)

The first argument, which is also required, is the path to the template
file. An optional ``content_type`` keyword argument allows the developer to
specify the output content type, usually "text/html". Then there are five
keyword arguments that specify the discriminators of the template:

* ``context`` -- This is the context in which the widget is displayed. In a
  simple widget like the one we have now, the context is ``None``.

* ``request`` -- This discriminator allows you to specify the type of request
  for which the widget will be available. In our case this would be a browser
  request. Note that browser requests can be further broken into layer, so you
  could also specify a layer interface here.

* ``view`` -- This is the view from which the widget is used. The simple
  widget at hand, does not have a view associated with it though.

* ``field`` -- This is the field for which the widget provides a
  representation. Again, this simple widget does not use a field, so it is
  ``None``.

* ``widget`` -- This is the widget itself. With this discriminator you can
  specify for which type of widget you are providing a template.

We can now register the template factory. The name of the factory is the mode
of the widget. By default, there are two widget modes: "input" and
"display". However, since the mode is just a string, one can develop other
kinds of modes as needed for a project. The default mode is "input":

  >>> from z3c.form import interfaces
  >>> age.mode is interfaces.INPUT_MODE
  True

  >>> import zope.component
  >>> zope.component.provideAdapter(factory, name=interfaces.INPUT_MODE)

Once everything is set up, the widget is updated and then rendered:

  >>> age.update()
  >>> print(age.render())
  <input type="text" name="age" value="39" />

If a value is found in the request, it takes precedence, since the user
entered the value:

  >>> age.request = TestRequest(form={'age': '25'})
  >>> age.update()
  >>> print(age.render())
  <input type="text" name="age" value="25" />

However, there is an option to turn off all request data:

  >>> age.value = '39'
  >>> age.ignoreRequest = True
  >>> age.update()
  >>> print(age.render())
  <input type="text" name="age" value="39" />

Additionally the widget provides a dictionary representation of its data through a json_data() method:
  >>> from pprint import pprint
  >>> pprint(age.json_data())
  {'error': '',
   'id': '',
   'label': 'Age',
   'mode': 'input',
   'name': 'age',
   'required': False,
   'type': 'text',
   'value': '39'}


Creating and Using Field Widgets
--------------------------------

An extended form of the widget allows fields to control several of the
widget's properties. Let's create a field first:

  >>> ageField = zope.schema.Int(
  ...     __name__ = 'age',
  ...     title = 'Age',
  ...     min = 0,
  ...     max = 130)

We can now use our simple widget and create a field widget from it:

  >>> ageWidget = widget.FieldWidget(ageField, age)

Such a widget provides ``IFieldWidget``:

  >>> interfaces.IFieldWidget.providedBy(ageWidget)
  True

Of course, this is more commonly done using an adapter. Commonly those
adapters look like this:

  >>> @zope.component.adapter(zope.schema.Int, TestRequest)
  ... @zope.interface.implementer(interfaces.IFieldWidget)
  ... def IntWidget(field, request):
  ...     return widget.FieldWidget(field, widget.Widget(request))

  >>> zope.component.provideAdapter(IntWidget)
  >>> ageWidget = zope.component.getMultiAdapter((ageField, request),
  ...     interfaces.IFieldWidget)

Now we just have to update and render the widget:

  >>> ageWidget.update()
  >>> print(ageWidget.render())
  <input type="text" name="age" />

There is no initial value for the widget, since there is no value in the
request and the field does not provide a default. Let's now give our field a
default value and see what happens:

  >>> ageField.default = 30
  >>> ageWidget.update()
  Traceback (most recent call last):
  ...
  TypeError: ('Could not adapt', <Widget 'age'>,
              <InterfaceClass z3c.form.interfaces.IDataConverter>)

In order for the widget to be able to take the field's default value and use
it to provide an initial value the widget, we need to provide a data converter
that defines how to convert from the field value to the widget value.

  >>> from z3c.form import converter
  >>> zope.component.provideAdapter(converter.FieldWidgetDataConverter)
  >>> zope.component.provideAdapter(converter.FieldDataConverter)

  >>> ageWidget.update()
  >>> print(ageWidget.render())
  <input type="text" name="age" value="30" />

Again, the request value is honored above everything else:

  >>> ageWidget.request = TestRequest(form={'age': '25'})
  >>> ageWidget.update()
  >>> print(ageWidget.render())
  <input type="text" name="age" value="25" />


Creating and Using Context Widgets
----------------------------------

When widgets represent an attribute value of an object, then this object must
be set as the context of the widget:

  >>> class Person(object):
  ...     age = 45
  >>> person = Person()

  >>> ageWidget.context = person
  >>> zope.interface.alsoProvides(ageWidget, interfaces.IContextAware)

The result is that the context value takes over precendence over the default
value:

  >>> ageWidget.request = TestRequest()
  >>> ageWidget.update()
  Traceback (most recent call last):
  ...
  ComponentLookupError: ((...), <InterfaceClass ...IDataManager>, '')

This call fails because the widget does not know how to extract the value from
the context. Registering a data manager for the widget does the trick:

  >>> from z3c.form import datamanager
  >>> zope.component.provideAdapter(datamanager.AttributeField)

  >>> ageWidget.update()
  >>> print(ageWidget.render())
  <input type="text" name="age" value="45" />

If the context value is unknown (None), the default value kicks in.

  >>> person.age = None

  >>> ageWidget.update()
  >>> print(ageWidget.render())
  <input type="text" name="age" value="30" />

Unless the widget is explicitely asked to not to show defaults.
This is handy for EditForms.

  >>> ageWidget.showDefault = False

  >>> ageWidget.update()
  >>> print(ageWidget.render())
  <input type="text" name="age" value="" />

  >>> ageWidget.showDefault = True
  >>> person.age = 45

The context can be explicitely ignored, making the widget display the default
value again:

  >>> ageWidget.ignoreContext = True
  >>> ageWidget.update()
  >>> print(ageWidget.render())
  <input type="text" name="age" value="30" />

Again, the request value is honored above everything else:

  >>> ageWidget.request = TestRequest(form={'age': '25'})
  >>> ageWidget.ignoreContext = False
  >>> ageWidget.update()
  >>> print(ageWidget.render())
  <input type="text" name="age" value="25" />

But what happens if the object we are working on is security proxied? In
particular, what happens, if the access to the attribute is denied. To see
what happens, we have to create a proxied person:

  >>> from zope.security import checker
  >>> PersonChecker = checker.Checker({'age': 'Access'}, {'age': 'Edit'})

  >>> ageWidget.request = TestRequest()
  >>> ageWidget.context = checker.ProxyFactory(Person(), PersonChecker)

After changing the security policy, ...

  >>> from zope.security import management
  >>> from z3c.form import testing
  >>> management.endInteraction()
  >>> newPolicy = testing.SimpleSecurityPolicy()
  >>> oldPolicy = management.setSecurityPolicy(newPolicy)
  >>> management.newInteraction()

it is not possible anymore to update the widget:

  >>> ageWidget.update()
  Traceback (most recent call last):
  ...
  Unauthorized: (<Person object at ...>, 'age', 'Access')

If no security declaration has been made at all, we get a
``ForbiddenAttribute`` error:

  >>> ageWidget.context = checker.ProxyFactory(Person(), checker.Checker({}))
  >>> ageWidget.update()
  Traceback (most recent call last):
  ...
  ForbiddenAttribute: ('age', <Person object at ...>)

Let's clean up the setup:

  >>> management.endInteraction()
  >>> newPolicy = management.setSecurityPolicy(oldPolicy)
  >>> management.newInteraction()

  >>> ageWidget.context = Person()


Dynamically Changing Attribute Values
-------------------------------------

Once widgets are used within a framework, it is very tedious to write Python
code to adjust certain attributes, even though hooks exist. The easiest way to
change those attribute values is actually to provide an adapter that provides
the custom value.

We can create a custom label for the age widget:

  >>> AgeLabel = widget.StaticWidgetAttribute(
  ...     'Current Age',
  ...     context=None, request=None, view=None, field=ageField, widget=None)

Clearly, this code does not require us to touch the orginal form and widget
code, given that we have enough control over the selection. In the example
above, all the selection discriminators are listed for demonstration
purposes. Of course, the label in this case can be created as follows:

  >>> AgeLabel = widget.StaticWidgetAttribute('Current Age', field=ageField)

Much better, isn't it? Initially the label is the title of the field:

  >>> ageWidget.label
  'Age'

Let's now simply register the label as a named adapter; the name is the name
of the attribute to change:

  >>> zope.component.provideAdapter(AgeLabel, name='label')

Asking the widget for the label now will return the newly registered label:

  >>> ageWidget.update()
  >>> ageWidget.label
  'Current Age'

Of course, simply setting the label or changing the label extraction via a
sub-class are other options you might want to consider. Furthermore, you
could also create a computed attribute value or implement your own component.

Overriding other attributes, such as ``required``, is done in the same
way. If any widget provides new attributes, they are also overridable this
way. For example, the selection widget defines a label for the option that no
value was selected. We often want to override this, because the German
translation sucks or the wording is often too generic. Widget implementation
should add names of overridable attributes to their "_adapterValueAttributes"
internal attribute.

Let's try to override the ``required`` attribute. By default the widget is required,
because the field is required as well:

  >>> ageWidget.required
  True

Let's provide a static widget attribute adapter with name "required":

  >>> AgeNotRequired = widget.StaticWidgetAttribute(False, field=ageField)
  >>> zope.component.provideAdapter(AgeNotRequired, name="required")

Now, let's check if it works:

  >>> ageWidget.update()
  >>> ageWidget.required
  False

Overriding the default value is somewhat special due to the complexity of
obtaining the value. So let's register one now:

  >>> AgeDefault = widget.StaticWidgetAttribute(50, field=ageField)
  >>> zope.component.provideAdapter(AgeDefault, name="default")

Let's now instantiate, update and render the widget to see the default value:

  >>> ageWidget = zope.component.getMultiAdapter((ageField, request),
  ...     interfaces.IFieldWidget)
  >>> ageWidget.update()
  >>> print(ageWidget.render())
  <input type="text" name="age" value="50" />

This value is also respected by the json_data method:
  >>> from pprint import pprint
  >>> pprint(ageWidget.json_data())
  {'error': '',
   'id': 'age',
   'label': 'Current Age',
   'mode': 'input',
   'name': 'age',
   'required': False,
   'type': 'text',
   'value': '50'}


Sequence Widget
---------------

A common use case in user interfaces is to ask the user to select one or more
items from a set of options/choices. The ``widget`` module provides a basic
widget implementation to support this use case.

The options available for selections are known as terms. Initially, there are
no terms:

  >>> request = TestRequest()
  >>> seqWidget = widget.SequenceWidget(request)
  >>> seqWidget.name = 'seq'

  >>> seqWidget.terms is None
  True

There are two ways terms can be added, either manually or via an
adapter. Those term objects must provide ``ITerms``. There is no simple
default implementation, so we have to provide one ourselves:

  >>> from zope.schema import vocabulary
  >>> @zope.interface.implementer(interfaces.ITerms)
  ... class Terms(vocabulary.SimpleVocabulary):
  ...     def getValue(self, token):
  ...         return self.getTermByToken(token).value

  >>> terms = Terms(
  ...   [Terms.createTerm(1, 'v1', 'Value 1'),
  ...    Terms.createTerm(2, 'v2', 'Value 2'),
  ...    Terms.createTerm(3, 'v3', 'Value 3')])
  >>> seqWidget.terms = terms

Once the ``terms`` attribute is set, updating the widgets does not change the
terms:

  >>> seqWidget.update()
  >>> [term.value for term in seqWidget.terms]
  [1, 2, 3]

The value of a sequence widget is a tuple/list of term tokens. When extracting
values from the request, the values must be valid tokens, otherwise the
default value is returned:

  >>> seqWidget.request = TestRequest(form={'seq': ['v1']})
  >>> seqWidget.extract()
  ('v1',)

  >>> seqWidget.request = TestRequest(form={'seq': ['v4']})
  >>> seqWidget.extract()
  <NO_VALUE>

  >>> seqWidget.request = TestRequest(form={'seq-empty-marker': '1'})
  >>> seqWidget.extract()
  ()

Note that we also support single values being returned outside a sequence. The
extracted value is then wrapped by a tuple. This feature is useful when
integrating with third-party client frameworks that do not know about the Zope
naming conventions.

  >>> seqWidget.request = TestRequest(form={'seq': 'v1'})
  >>> seqWidget.extract()
  ('v1',)

If the no-value token has been selected, it is returned without further
verification:

  >>> seqWidget.request = TestRequest(form={'seq': [seqWidget.noValueToken]})
  >>> seqWidget.extract()
  ('--NOVALUE--',)

Since the value of the widget is a tuple of tokens, when displaying the
values, they have to be converted to the title of the term:

  >>> seqWidget.value = ('v1', 'v2')
  >>> seqWidget.displayValue
  ['Value 1', 'Value 2']

Unknown values/terms get silently ignored.

  >>> seqWidget.value = ('v3', 'v4')
  >>> seqWidget.displayValue
  ['Value 3']

When input forms are directly switched to display forms within the same
request, it can happen that the value contains the "--NOVALUE--" token
entry. This entry should be silently ignored:

  >>> seqWidget.value = (seqWidget.noValueToken,)
  >>> seqWidget.displayValue
  []

To demonstrate how the terms is automatically chosen by a widget, we should
instantiate a field widget. Let's do this with a choice field:

  >>> seqField = zope.schema.Choice(
  ...     title='Sequence Field',
  ...     vocabulary=terms)

Let's now create the field widget:

  >>> seqWidget = widget.FieldWidget(seqField, widget.SequenceWidget(request))
  >>> seqWidget.terms

The terms should be available as soon as the widget is updated:

  >>> seqWidget.update()
  Traceback (most recent call last):
  ...
  ComponentLookupError: ((...), <InterfaceClass ...ITerms>, '')

This failed, because we did not register an adapter for the terms yet. After
the adapter is registered, everything should work as expected:

  >>> from z3c.form import term
  >>> zope.component.provideAdapter(term.ChoiceTermsVocabulary)
  >>> zope.component.provideAdapter(term.ChoiceTerms)

  >>> seqWidget.update()
  >>> seqWidget.terms
  <z3c.form.term.ChoiceTermsVocabulary object at ...>

The representation of this widget as json looks a bit different:
  >>> from pprint import pprint
  >>> pprint(seqWidget.json_data())
  {'error': '',
   'id': '',
   'label': 'Sequence Field',
   'mode': 'input',
   'name': '',
   'required': True,
   'type': 'sequence',
   'value': ()}


So that's it. Everything else is the same from then on.


Multi Widget
------------

A common use case in user interfaces is to ask the user to define one or more
items. The ``widget`` module provides a basic widget implementation to support
this use case.

The `MultiWidget` allows to store none, one or more values for a sequence or dictionary
field.  Don't get confused by the term sequence. The sequence used in
`SequenceWidget` means that the widget can choose from a sequence of values
which is really a collection. The `MultiWidget` can collect values to build
and store a sequence of values like those used in `ITuple` or `IList` field.

  >>> request = TestRequest()
  >>> multiWidget = widget.MultiWidget(request)
  >>> multiWidget.name = 'multi.name'
  >>> multiWidget.id = 'multi-id'

  >>> multiWidget.value
  []

Let's define a field for our multi widget:

  >>> multiField = zope.schema.List(
  ...     value_type=zope.schema.Int(default=42))
  >>> multiWidget.field = multiField

If the multi is used with a schema.List the value of a multi widget is always list.
When extracting values from the
request, the values must be a list of valid values based on the value_type
field used from the used sequence field. The widget also uses a counter which
is required for processing the input from a request. The counter is a marker
for build the right amount of enumerated widgets.

If we provide no request we will get no value:

  >>> multiWidget.extract()
  <NO_VALUE>

If we provide an empty counter we will get an empty list.
This is accordance with Widget.extract(), where a missing request value
is <NO_VALUE> and an empty ('') request value is ''.

  >>> multiWidget.request = TestRequest(form={'multi.name.count':'0'})
  >>> multiWidget.extract()
  []

If we provide real values within the request, we will get it back:

  >>> multiWidget.request = TestRequest(form={'multi.name.count':'2',
  ...                                         'multi.name.0':'42',
  ...                                         'multi.name.1':'43'})
  >>> multiWidget.extract()
  ['42', '43']

If we provide a bad value we will get the bad value within the extract method.
Our widget update process will validate this bad value later:

  >>> multiWidget.request = TestRequest(form={'multi.name.count':'1',
  ...                                         'multi.name.0':'bad'})
  >>> multiWidget.extract()
  ['bad']

Storing a widget value forces to update the (sub) widgets. This forces also to
validate the (sub) widget values. To show this we need to register a
validator:

  >>> from z3c.form.validator import SimpleFieldValidator
  >>> zope.component.provideAdapter(SimpleFieldValidator)

Since the value of the widget is a list of (widget) value items, when
displaying the values, they can be used as they are:

  >>> multiWidget.request = TestRequest(form={'multi.name.count':'2',
  ...                                         'multi.name.0':'42',
  ...                                         'multi.name.1':'43'})
  >>> multiWidget.value = multiWidget.extract()
  >>> multiWidget.value
  ['42', '43']

Each widget normally gets first processed by it's update method call after
initialization. This update call forces to call extract, which first will get
the right amount of (sub) widgets by the given counter value. Based on that
counter value the right amount of widgets will get created. Each widget will
return it's own value and this collected values get returned by the extract
method. The multi widget update method will then store this values if any given
as multi widget value argument. If extract doesn't return a value the multi
widget update method will use it's default value. If we store a given value
from the extract as multi widget value, this will force to setup the multi
widget widgets based on the given values and apply the right value for them.
After that the multi widget is ready for rendering. The good thing about that
pattern is that it is possible to set a value before or after the update method
is called. At any time if we change the multi widget value the (sub) widgets
get updated within the new relevant value.

  >>> multiRequest = TestRequest(form={'multi.name.count':'2',
  ...                                  'multi.name.0':'42',
  ...                                  'multi.name.1':'43'})

  >>> multiWidget = widget.FieldWidget(multiField, widget.MultiWidget(
  ...     multiRequest))
  >>> multiWidget.name = 'multi.name'
  >>> multiWidget.value
  []

  >>> multiWidget.update()

  >>> multiWidget.widgets[0].value
  '42'

  >>> multiWidget.widgets[1].value
  '43'

  >>> multiWidget.value
  ['42', '43']

MultiWidget also declares the ``allowAdding`` and ``allowRemoving``
attributes that can be used in browser presentation to control add/remove
button availability. To ease working with common cases, the
``updateAllowAddRemove`` method provided that will set those attributes
in respect to field's min_length and max_length, if the field provides
zope.schema.interfaces.IMinMaxLen interface.

Let's define a field with min and max length constraints and create
a widget for it.

  >>> multiField = zope.schema.List(
  ...     value_type=zope.schema.Int(),
  ...     min_length=2,
  ...     max_length=5)

  >>> request = TestRequest()
  >>> multiWidget = widget.FieldWidget(multiField, widget.MultiWidget(request))

Lets ensure that the minimum number of widgets are created.

  >>> multiWidget.update()
  >>> len(multiWidget.widgets)
  2

Now, let's check if the function will do the right thing depending on
the value:

No value:

  >>> multiWidget.updateAllowAddRemove()
  >>> multiWidget.allowAdding, multiWidget.allowRemoving
  (True, False)

Minimum length:

  >>> multiWidget.value = ['3', '5']
  >>> multiWidget.updateAllowAddRemove()
  >>> multiWidget.allowAdding, multiWidget.allowRemoving
  (True, False)

Some allowed length:

  >>> multiWidget.value = ['3', '5', '8', '6']
  >>> multiWidget.updateAllowAddRemove()
  >>> multiWidget.allowAdding, multiWidget.allowRemoving
  (True, True)

Maximum length:

  >>> multiWidget.value = ['3', '5', '8', '6', '42']
  >>> multiWidget.updateAllowAddRemove()
  >>> multiWidget.allowAdding, multiWidget.allowRemoving
  (False, True)

Over maximum length:

  >>> multiWidget.value = ['3', '5', '8', '6', '42', '45']
  >>> multiWidget.updateAllowAddRemove()
  >>> multiWidget.allowAdding, multiWidget.allowRemoving
  (False, True)

I know a guy who once switched widget mode in the middle. All simple widgets
are easy to hack, but multiWidget needs to update all subwidgets:

  >>> [w.mode for w in multiWidget.widgets]
  ['input', 'input', 'input', 'input', 'input', 'input']

Switch the multiWidget mode:

  >>> multiWidget.mode = interfaces.DISPLAY_MODE

Yes, all subwidgets switch mode:

  >>> [w.mode for w in multiWidget.widgets]
  ['display', 'display', 'display', 'display', 'display', 'display']

The json data representing the multi widget:
  >>> from pprint import pprint
  >>> pprint(multiWidget.json_data())
  {'error': '',
   'id': '',
   'label': '',
   'mode': 'display',
   'name': '',
   'required': True,
   'type': 'multi',
   'value': ['3', '5', '8', '6', '42', '45'],
   'widgets': [{'error': '',
                'id': '-0',
                'label': '',
                'mode': 'display',
                'name': '.0',
                'required': True,
                'type': 'text',
                'value': '3'},
               {'error': '',
                'id': '-1',
                'label': '',
                'mode': 'display',
                'name': '.1',
                'required': True,
                'type': 'text',
                'value': '5'},
               {'error': '',
                'id': '-2',
                'label': '',
                'mode': 'display',
                'name': '.2',
                'required': True,
                'type': 'text',
                'value': '8'},
               {'error': '',
                'id': '-3',
                'label': '',
                'mode': 'display',
                'name': '.3',
                'required': True,
                'type': 'text',
                'value': '6'},
               {'error': '',
                'id': '-4',
                'label': '',
                'mode': 'display',
                'name': '.4',
                'required': True,
                'type': 'text',
                'value': '42'},
               {'error': '',
                'id': '-5',
                'label': '',
                'mode': 'display',
                'name': '.5',
                'required': True,
                'type': 'text',
                'value': '45'}]}



Multi Dict Widget
-----------------

We can also use a multiWidget in Dict mode by just using a field which a Dict:

  >>> multiField = zope.schema.Dict(
  ...     key_type=zope.schema.Int(),
  ...     value_type=zope.schema.Int(default=42))
  >>> multiWidget.field = multiField
  >>> multiWidget.name = 'multi.name'

Now if we set the value to a list we get an error:

  >>> multiWidget.value = ['3', '5', '8', '6', '42', '45']
  Traceback (most recent call last):
  ...
  ValueError: need more than 1 value to unpack

but a dictionary is good.

  >>> multiWidget.value = [('1', '3'), ('2', '5'), ('3', '8'), ('4', '6'), ('5', '42'), ('6', '45')]

and our requests now have to include keys as well as values

  >>> multiWidget.request = TestRequest(form={'multi.name.count':'2',
  ...                                         'multi.name.key.0':'1',
  ...                                         'multi.name.0':'42',
  ...                                         'multi.name.key.1':'2',
  ...                                         'multi.name.1':'43'})
  >>> multiWidget.extract()
  [('1', '42'), ('2', '43')]

Let's define a field with min and max length constraints and create
a widget for it.

  >>> multiField = zope.schema.Dict(
  ...     key_type=zope.schema.Int(),
  ...     value_type=zope.schema.Int(default=42),
  ...     min_length=2,
  ...     max_length=5)


  >>> request = TestRequest()
  >>> multiWidget = widget.FieldWidget(multiField, widget.MultiWidget(request))

Lets ensure that the minimum number of widgets are created.

  >>> multiWidget.update()
  >>> len(multiWidget.widgets)
  2

We can add new items

  >>> multiWidget.appendAddingWidget()
  >>> multiWidget.appendAddingWidget()

  >>> multiWidget.update()
  >>> len(multiWidget.widgets)
  4

The json data representing the Multi Dict Widget is the same as the Multi widget:

Widget Events
-------------

Widget-system interaction can be very rich and wants to be extended in
unexpected ways. Thus there exists a generic widget event that can be used by
other code.

  >>> event = widget.WidgetEvent(ageWidget)
  >>> event
  <WidgetEvent <Widget 'age'>>

These events provide the ``IWidgetEvent`` interface:

  >>> interfaces.IWidgetEvent.providedBy(event)
  True

There exists a special event that can be send out after a widget has been
updated, ...

  >>> afterUpdate = widget.AfterWidgetUpdateEvent(ageWidget)
  >>> afterUpdate
  <AfterWidgetUpdateEvent <Widget 'age'>>

which provides another special interface:

  >>> interfaces.IAfterWidgetUpdateEvent.providedBy(afterUpdate)
  True

This event should be used by widget-managing components and is not created and
sent out internally by the widget's ``update()`` method. The event was
designed to provide an additional hook between updating the widget and
rendering it.


Cleanup
-------

Let's not leave temporary files lying around

  >>> import os
  >>> os.remove(textWidgetTemplate)
