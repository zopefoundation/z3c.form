==============
Field Managers
==============

One of the features in ``zope.formlib`` that works really well is the syntax
used to define the contents of the form. The formlib uses form fields, to
describe how the form should be put together. Since we liked this way of
working, this package offers this feature as well in a very similar way.

A field manager organizes all fields to be displayed within a form. Each field
is associated with additional meta-data. The simplest way to create a field
manager is to specify the schema from which to extract all fields.

Thus, the first step is to create a schema:

  >>> import zope.interface
  >>> import zope.schema

  >>> class IPerson(zope.interface.Interface):
  ...      id = zope.schema.Int(
  ...          title='Id',
  ...          readonly=True)
  ...
  ...      name = zope.schema.TextLine(
  ...          title='Name')
  ...
  ...      country = zope.schema.Choice(
  ...          title='Country',
  ...          values=('Germany', 'Switzerland', 'USA'),
  ...          required=False)

We can now create the field manager:

  >>> from z3c.form import field
  >>> manager = field.Fields(IPerson)

Like all managers in this package, it provides the enumerable mapping API:

  >>> manager['id']
  <Field 'id'>
  >>> manager['unknown']
  Traceback (most recent call last):
  ...
  KeyError: 'unknown'

  >>> manager.get('id')
  <Field 'id'>
  >>> manager.get('unknown', 'default')
  'default'

  >>> 'id' in manager
  True
  >>> 'unknown' in manager
  False

  >>> list(manager.keys())
  ['id', 'name', 'country']

  >>> [key for key in manager]
  ['id', 'name', 'country']

  >>> list(manager.values())
  [<Field 'id'>, <Field 'name'>, <Field 'country'>]

  >>> list(manager.items())
  [('id', <Field 'id'>),
   ('name', <Field 'name'>),
   ('country', <Field 'country'>)]

  >>> len(manager)
  3

You can also select the fields that you would like to have:

  >>> manager = manager.select('name', 'country')
  >>> list(manager.keys())
  ['name', 'country']

Changing the order is simply a matter of changing the selection order:

  >>> manager = manager.select('country', 'name')
  >>> list(manager.keys())
  ['country', 'name']

Selecting a field becomes a little bit more tricky when field names
overlap. For example, let's say that a person can be adapted to a pet:

  >>> class IPet(zope.interface.Interface):
  ...      id = zope.schema.TextLine(
  ...          title='Id')
  ...
  ...      name = zope.schema.TextLine(
  ...          title='Name')

The pet field(s) can only be added to the fields manager with a prefix:

  >>> manager += field.Fields(IPet, prefix='pet')
  >>> list(manager.keys())
  ['country', 'name', 'pet.id', 'pet.name']

When selecting fields, this prefix has to be used:

  >>> manager = manager.select('name', 'pet.name')
  >>> list(manager.keys())
  ['name', 'pet.name']

However, sometimes it is tedious to specify the prefix together with the
field; for example here:

  >>> manager = field.Fields(IPerson).select('name')
  >>> manager += field.Fields(IPet, prefix='pet').select('pet.name', 'pet.id')
  >>> list(manager.keys())
  ['name', 'pet.name', 'pet.id']

It is easier to specify the prefix as an afterthought:

  >>> manager = field.Fields(IPerson).select('name')
  >>> manager += field.Fields(IPet, prefix='pet').select(
  ...     'name', 'id', prefix='pet')
  >>> list(manager.keys())
  ['name', 'pet.name', 'pet.id']

Alternatively, you can specify the interface:

  >>> manager = field.Fields(IPerson).select('name')
  >>> manager += field.Fields(IPet, prefix='pet').select(
  ...     'name', 'id', interface=IPet)
  >>> list(manager.keys())
  ['name', 'pet.name', 'pet.id']

Sometimes it is easier to simply omit a set of fields instead of selecting all
the ones you want:

  >>> manager = field.Fields(IPerson)
  >>> manager = manager.omit('id')
  >>> list(manager.keys())
  ['name', 'country']

Again, you can solve name conflicts using the full prefixed name, ...

  >>> manager = field.Fields(IPerson).omit('country')
  >>> manager += field.Fields(IPet, prefix='pet')
  >>> list(manager.omit('pet.id').keys())
  ['id', 'name', 'pet.name']

using the prefix keyword argument, ...

  >>> manager = field.Fields(IPerson).omit('country')
  >>> manager += field.Fields(IPet, prefix='pet')
  >>> list(manager.omit('id', prefix='pet').keys())
  ['id', 'name', 'pet.name']

or, using the interface:

  >>> manager = field.Fields(IPerson).omit('country')
  >>> manager += field.Fields(IPet, prefix='pet')
  >>> list(manager.omit('id', interface=IPet).keys())
  ['id', 'name', 'pet.name']

You can also add two field managers together:

  >>> manager = field.Fields(IPerson).select('name', 'country')
  >>> manager2 = field.Fields(IPerson).select('id')
  >>> list((manager + manager2).keys())
  ['name', 'country', 'id']

Adding anything else to a field manager is not well defined:

  >>> manager + 1
  Traceback (most recent call last):
  ...
  TypeError: unsupported operand type(s) for +: 'Fields' and 'int'

You also cannot make any additions that would cause a name conflict:

  >>> manager + manager
  Traceback (most recent call last):
  ...
  ValueError: ('Duplicate name', 'name')

When creating a new form derived from another, you often want to keep existing
fields and add new ones. In order to not change the super-form class, you need
to copy the field manager:

  >>> list(manager.keys())
  ['name', 'country']
  >>> list(manager.copy().keys())
  ['name', 'country']


More on the Constructor
-----------------------

The constructor does not only accept schemas to be passed in; one can also
just pass in schema fields:

  >>> list(field.Fields(IPerson['name']).keys())
  ['name']

However, the schema field has to have a name:

  >>> email = zope.schema.TextLine(title='E-Mail')
  >>> field.Fields(email)
  Traceback (most recent call last):
  ...
  ValueError: Field has no name

Adding a name helps:

  >>> email.__name__ = 'email'
  >>> list(field.Fields(email).keys())
  ['email']

Or, you can just pass in other field managers, which is the feature that the add
mechanism uses:

  >>> list(field.Fields(manager).keys())
  ['name', 'country']

Last, but not least, the constructor also accepts form fields, which are used
by ``select()`` and ``omit()``:

  >>> list(field.Fields(manager['name'], manager2['id']).keys())
  ['name', 'id']

If the constructor does not recognize any of the types above, it raises a
``TypeError`` exception:

  >>> field.Fields(object())
  Traceback (most recent call last):
  ...
  TypeError: ('Unrecognized argument type', <object object at ...>)

Additionally, you can specify several keyword arguments in the field manager
constructor that are used to set up the fields:

* ``omitReadOnly``

  When set to ``True`` all read-only fields are omitted.

    >>> list(field.Fields(IPerson, omitReadOnly=True).keys())
    ['name', 'country']

* ``keepReadOnly``

  Sometimes you want to keep a particular read-only field around, even though
  in general you want to omit them. In this case you can specify the fields to
  keep:

    >>> list(field.Fields(
    ...     IPerson, omitReadOnly=True, keepReadOnly=('id',)).keys())
    ['id', 'name', 'country']

* ``prefix``

  Sets the prefix of the fields. This argument is passed on to each field.

    >>> manager = field.Fields(IPerson, prefix='myform.')
    >>> manager['myform.name']
    <Field 'myform.name'>


* ``interface``

  Usually the interface is inferred from the field itself. The interface is
  used to determine whether an adapter must be looked up for a given
  context.

  But sometimes fields are generated in isolation to an interface or the
  interface of the field is not the one you want. In this case you can specify
  the interface:

    >>> class IMyPerson(IPerson):
    ...     pass

    >>> manager = field.Fields(email, interface=IMyPerson)
    >>> manager['email'].interface
    <InterfaceClass builtins.IMyPerson>

* ``mode``

  The mode in which the widget will be rendered. By default there are two
  available, "input" and "display". When mode is not specified, "input" is
  chosen.

    >>> from z3c.form import interfaces
    >>> manager = field.Fields(IPerson, mode=interfaces.DISPLAY_MODE)
    >>> manager['country'].mode
    'display'

* ``ignoreContext``

  While the ``ignoreContext`` flag is usually set on the form, it is sometimes
  desirable to set the flag for a particular field.

    >>> manager = field.Fields(IPerson)
    >>> manager['country'].ignoreContext

    >>> manager = field.Fields(IPerson, ignoreContext=True)
    >>> manager['country'].ignoreContext
    True

    >>> manager = field.Fields(IPerson, ignoreContext=False)
    >>> manager['country'].ignoreContext
    False

* ``showDefault``

  The ``showDefault`` can be set on fields.

    >>> manager = field.Fields(IPerson)
    >>> manager['country'].showDefault

    >>> manager = field.Fields(IPerson, showDefault=True)
    >>> manager['country'].showDefault
    True

    >>> manager = field.Fields(IPerson, showDefault=False)
    >>> manager['country'].showDefault
    False


Fields Widget Manager
---------------------

When a form (or any other widget-using view) is updated, one of the tasks is
to create the widgets. Traditionally, generating the widgets involved looking
at the form fields (or similar) of a form and generating the widgets using the
information of those specifications. This solution is good for the common
(about 85%) use cases, since it makes writing new forms very simple and allows
a lot of control at a class-definition level.

It has, however, its limitations. It does not, for example, allow for
customization without rewriting a form. This can range from omitting fields on
a particular form to generically adding a new widget to the form, such as an
"object name" button on add forms. This package solves this issue by providing
a widget manager, which is responsible providing the widgets for a particular
view.

The default widget manager for forms is able to look at a form's field
definitions and create widgets for them. Thus, let's create a schema first:

  >>> import zope.interface
  >>> import zope.schema

  >>> class LastNameTooShort(zope.schema.interfaces.ValidationError):
  ...     """The last name is too short."""

  >>> def lastNameConstraint(value):
  ...     if value and value == value.lower():
  ...         raise zope.interface.Invalid(u"Name must have at least one capital letter")
  ...     return True

  >>> class IPerson(zope.interface.Interface):
  ...     id = zope.schema.TextLine(
  ...         title='ID',
  ...         description=u"The person's ID.",
  ...         readonly=True,
  ...         required=True)
  ...
  ...     lastName = zope.schema.TextLine(
  ...         title='Last Name',
  ...         description=u"The person's last name.",
  ...         default='',
  ...         required=True,
  ...         constraint=lastNameConstraint)
  ...
  ...     firstName = zope.schema.TextLine(
  ...         title='First Name',
  ...         description=u"The person's first name.",
  ...         default='-- unknown --',
  ...         required=False)
  ...
  ...     @zope.interface.invariant
  ...     def twiceAsLong(person):
  ...         # note: we're protecting here values against being None
  ...         # just in case ignoreRequiredOnExtract lets that through
  ...         if len(person.lastName or '') >= 2 * len(person.firstName or ''):
  ...             raise LastNameTooShort()

Next we need a form that specifies the fields to be added:

  >>> from z3c.form import field

  >>> class PersonForm(object):
  ...     prefix = 'form.'
  ...     fields = field.Fields(IPerson)
  >>> personForm = PersonForm()

For more details on how to define fields within a form, see :doc:`form`. We
can now create the fields widget manager. Its discriminators are the form for
which the widgets are created, the request, and the context that is being
manipulated. In the simplest case the context is ``None`` and ignored, as it
is true for an add form.

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> context = object()

  >>> manager = field.FieldWidgets(personForm, request, context)
  >>> manager.ignoreContext = True


Widget Mapping
~~~~~~~~~~~~~~

The main responsibility of the manager is to provide the ``IEnumerableMapping``
interface and an ``update()`` method. Initially the mapping, going from widget
id to widget value, is empty:

  >>> from zope.interface.common.mapping import IEnumerableMapping
  >>> IEnumerableMapping.providedBy(manager)
  True

  >>> list(manager.keys())
  []

Only by "updating" the manager, will the widgets become available; before we can
use the update method, however, we have to register the ``IFieldWidget`` adapter
for the ``ITextLine`` field:

  >>> from z3c.form import interfaces, widget

  >>> @zope.component.adapter(zope.schema.TextLine, TestRequest)
  ... @zope.interface.implementer(interfaces.IFieldWidget)
  ... def TextFieldWidget(field, request):
  ...     return widget.FieldWidget(field, widget.Widget(request))

  >>> zope.component.provideAdapter(TextFieldWidget)

  >>> from z3c.form import converter
  >>> zope.component.provideAdapter(converter.FieldDataConverter)
  >>> zope.component.provideAdapter(converter.FieldWidgetDataConverter)

  >>> manager.update()

Other than usual mappings in Python, the widget manager's widgets are always
in a particular order:

  >>> list(manager.keys())
  ['id', 'lastName', 'firstName']

As you can see, if we call update twice, we still get the same amount and
order of keys:

  >>> manager.update()
  >>> list(manager.keys())
  ['id', 'lastName', 'firstName']

Let's make sure that all enumerable mapping functions work correctly:

  >>> manager['lastName']
  <Widget 'form.widgets.lastName'>

  >>> manager['unknown']
  Traceback (most recent call last):
  ...
  KeyError: 'unknown'

  >>> manager.get('lastName')
  <Widget 'form.widgets.lastName'>

  >>> manager.get('unknown', 'default')
  'default'

  >>> 'lastName' in manager
  True
  >>> 'unknown' in manager
  False

  >>> [key for key in manager]
  ['id', 'lastName', 'firstName']

  >>> list(manager.values())
  [<Widget 'form.widgets.id'>,
   <Widget 'form.widgets.lastName'>,
   <Widget 'form.widgets.firstName'>]

  >>> list(manager.items())
  [('id', <Widget 'form.widgets.id'>),
   ('lastName', <Widget 'form.widgets.lastName'>),
   ('firstName', <Widget 'form.widgets.firstName'>)]

  >>> len(manager)
  3

It is also possible to delete widgets from the manager:

  >>> del manager['firstName']
  >>> len(manager)
  2
  >>> list(manager.values())
  [<Widget 'form.widgets.id'>, <Widget 'form.widgets.lastName'>]
  >>> list(manager.keys())
  ['id', 'lastName']
  >>> list(manager.items())
  [('id', <Widget 'form.widgets.id'>),
  ('lastName', <Widget 'form.widgets.lastName'>)]

Note that deleting a non-existent widget causes a ``KeyError`` to be raised:

  >>> del manager['firstName']
  Traceback (most recent call last):
  ...
  KeyError: 'firstName'

Also, the field widget manager, like any selection manager,  can be cloned:

  >>> clone = manager.copy()
  >>> clone is not manager
  True
  >>> clone.form == manager.form
  True
  >>> clone.request == manager.request
  True
  >>> clone.content == manager.content
  True
  >>> list(clone.items()) == list(manager.items())
  True


Properties of widgets within a manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a widget is added to the widget manager, it is located:

  >>> lname = manager['lastName']

  >>> lname.__name__
  'lastName'
  >>> lname.__parent__
  FieldWidgets([...])

All widgets created by this widget manager are context aware:

  >>> interfaces.IContextAware.providedBy(lname)
  True
  >>> lname.context is context
  True


Determination of the widget mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, all widgets will also assume the mode of the manager:

  >>> manager['lastName'].mode
  'input'

  >>> manager.mode = interfaces.DISPLAY_MODE
  >>> manager.update()

  >>> manager['lastName'].mode
  'display'

The exception is when some fields specifically desire a different mode. In the
first case, all "readonly" fields will be shown in display mode:

  >>> manager.mode = interfaces.INPUT_MODE
  >>> manager.update()

  >>> manager['id'].mode
  'display'

An exception is made when the flag, "ignoreReadonly" is set:

  >>> manager.ignoreReadonly = True
  >>> manager.update()

  >>> manager['id'].mode
  'input'

In the second case, the last name will inherit the mode from the widget
manager, while the first name will want to use a display widget:

  >>> personForm.fields = field.Fields(IPerson).select('lastName')
  >>> personForm.fields += field.Fields(
  ...     IPerson, mode=interfaces.DISPLAY_MODE).select('firstName')

  >>> manager.mode = interfaces.INPUT_MODE
  >>> manager.update()

  >>> manager['lastName'].mode
  'input'
  >>> manager['firstName'].mode
  'display'

In a third case, the widget will be shown in display mode, if the attribute of
the context is not writable. Clearly this can never occur in add forms, since
there the context is ignored, but is an important use case in edit forms.

Thus, we need an implementation of the ``IPerson`` interface including some
security declarations:

  >>> from zope.security import checker

  >>> @zope.interface.implementer(IPerson)
  ... class Person(object):
  ...
  ...     def __init__(self, firstName, lastName):
  ...         self.id = firstName[0].lower() + lastName.lower()
  ...         self.firstName = firstName
  ...         self.lastName = lastName

  >>> PersonChecker = checker.Checker(
  ...     get_permissions = {'id': checker.CheckerPublic,
  ...                        'firstName': checker.CheckerPublic,
  ...                        'lastName': checker.CheckerPublic},
  ...     set_permissions = {'firstName': 'test.Edit',
  ...                        'lastName': checker.CheckerPublic}
  ...     )

  >>> srichter = checker.ProxyFactory(
  ...     Person('Stephan', 'Richter'), PersonChecker)

In this case the last name is always editable, but for the first name the user
will need the edit ("test.Edit") permission.

We also need to register the data manager and setup a new security policy:

  >>> from z3c.form import datamanager
  >>> zope.component.provideAdapter(datamanager.AttributeField)

  >>> from zope.security import management
  >>> from z3c.form import testing
  >>> management.endInteraction()
  >>> newPolicy = testing.SimpleSecurityPolicy()
  >>> oldpolicy = management.setSecurityPolicy(newPolicy)
  >>> management.newInteraction()

Now we can create the widget manager:

  >>> personForm = PersonForm()
  >>> request = TestRequest()
  >>> manager = field.FieldWidgets(personForm, request, srichter)

After updating the widget manager, the fields are available as widgets, the
first name being in display and the last name is input mode:

  >>> manager.update()
  >>> manager['id'].mode
  'display'
  >>> manager['firstName'].mode
  'display'
  >>> manager['lastName'].mode
  'input'

However, explicitly overriding the mode in the field declaration overrides
this selection for you:

  >>> personForm.fields['firstName'].mode = interfaces.INPUT_MODE

  >>> manager.update()
  >>> manager['id'].mode
  'display'
  >>> manager['firstName'].mode
  'input'
  >>> manager['lastName'].mode
  'input'


``showDefault``
---------------

``showDefault`` by default is ``True``:

  >>> manager['firstName'].showDefault
  True

``showDefault`` gets set on the widget based on the field's setting.

  >>> personForm.fields['firstName'].showDefault = False

  >>> manager.update()
  >>> manager['firstName'].showDefault
  False

  >>> personForm.fields['firstName'].showDefault = True

  >>> manager.update()
  >>> manager['firstName'].showDefault
  True


Required fields
---------------

There is a flag for required fields. This flag get set if at least one field
is required. This let us render a required info legend in forms if required
fields get used.

  >>> manager.hasRequiredFields
  True


Data extraction and validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Besides managing widgets, the widget manager also controls the process of
extracting and validating extracted data. Let's start with the validation
first, which only validates the data as a whole, assuming each individual
value being already validated.

Before we can use the method, we have to register a "manager validator":

  >>> from z3c.form import validator
  >>> zope.component.provideAdapter(validator.InvariantsValidator)

  >>> personForm.fields = field.Fields(IPerson)
  >>> manager.update()

  >>> manager.validate(
  ...     {'firstName': 'Stephan', 'lastName': 'Richter'})
  ()

The result of this method is a tuple of errors that occurred during the
validation. An empty tuple means the validation succeeded. Let's now make the
validation fail:

  >>> errors = manager.validate(
  ...     {'firstName': 'Stephan', 'lastName': 'Richter-Richter'})

  >>> [error.doc() for error in errors]
  ['The last name is too short.']

A special case occurs when the schema fields are not associated with an
interface:

  >>> name = zope.schema.TextLine(__name__='name')

  >>> class PersonNameForm(object):
  ...     prefix = 'form.'
  ...     fields = field.Fields(name)
  >>> personNameForm = PersonNameForm()

  >>> manager = field.FieldWidgets(personNameForm, request, context)

In this case, the widget manager's ``validate()`` method should simply ignore
the field and not try to look up any invariants:

  >>> manager.validate({'name': 'Stephan'})
  ()

Let's now have a look at the widget manager's ``extract()``, which returns a
data dictionary and the collection of errors. Before we can validate, we have
to register a validator for the widget:

  >>> zope.component.provideAdapter(validator.SimpleFieldValidator)

When all goes well, the data dictionary is complete and the error collection
empty:

  >>> request = TestRequest(form={
  ...     'form.widgets.id': 'srichter',
  ...     'form.widgets.firstName': 'Stephan',
  ...     'form.widgets.lastName': 'Richter'})
  >>> manager = field.FieldWidgets(personForm, request, context)
  >>> manager.ignoreContext = True
  >>> manager.update()

  >>> data, errors = manager.extract()
  >>> data['firstName']
  'Stephan'
  >>> data['lastName']
  'Richter'
  >>> errors
  ()

Since all errors are immediately converted to error view snippets, we have to
provide the adapter from a validation error to an error view snippet first:

  >>> from z3c.form import error
  >>> zope.component.provideAdapter(error.ErrorViewSnippet)
  >>> zope.component.provideAdapter(error.InvalidErrorViewSnippet)

Let's now cause a widget-level error by not submitting the required last
name:

  >>> request = TestRequest(form={
  ...     'form.widgets.firstName': 'Stephan', 'form.widgets.id': 'srichter'})
  >>> manager = field.FieldWidgets(personForm, request, context)
  >>> manager.ignoreContext = True
  >>> manager.update()
  >>> manager.extract()
  ({'firstName': 'Stephan'}, (<ErrorViewSnippet for RequiredMissing>,))

We can also turn off ``required`` checking for data extraction:

  >>> request = TestRequest(form={
  ...     'form.widgets.firstName': 'Stephan', 'form.widgets.id': 'srichter'})
  >>> manager = field.FieldWidgets(personForm, request, context)
  >>> manager.ignoreContext = True
  >>> manager.ignoreRequiredOnExtract = True
  >>> manager.update()

Here we get the required field as ``None`` and no errors:

  >>> pprint(manager.extract())
  ({'firstName': 'Stephan', 'lastName': None}, ())

  >>> manager.ignoreRequiredOnExtract = False

Or, we could violate a constraint. This constraint raises Invalid, which is
a convenient way to raise errors where we mainly care about providing a custom
error message.

  >>> request = TestRequest(form={
  ...     'form.widgets.firstName': 'Stephan',
  ...     'form.widgets.lastName': 'richter',
  ...     'form.widgets.id': 'srichter'})
  >>> manager = field.FieldWidgets(personForm, request, context)
  >>> manager.ignoreContext = True
  >>> manager.update()
  >>> extracted = manager.extract()
  >>> extracted
  ({'firstName': 'Stephan'}, (<InvalidErrorViewSnippet for Invalid>,))

  >>> extracted[1][0].createMessage()
  'Name must have at least one capital letter'

Finally, let's ensure that invariant failures are also caught:

  >>> request = TestRequest(form={
  ...     'form.widgets.id': 'srichter',
  ...     'form.widgets.firstName': 'Stephan',
  ...     'form.widgets.lastName': 'Richter-Richter'})
  >>> manager = field.FieldWidgets(personForm, request, context)
  >>> manager.ignoreContext = True
  >>> manager.update()
  >>> data, errors = manager.extract()
  >>> errors[0].error.doc()
  'The last name is too short.'

Note that the errors coming from invariants are all error view snippets as
well, just as it is the case for field-specific validation errors. And that's
really all there is!

By default, the ``extract()`` method not only returns the errors that it
catches, but also sets them on individual widgets and on the manager:

  >>> manager.errors
  (<ErrorViewSnippet for LastNameTooShort>,)

This behavior can be turned off. To demonstrate, let's make a new request that
causes a widget-level error:

  >>> request = TestRequest(form={
  ...     'form.widgets.firstName': 'Stephan', 'form.widgets.id': 'srichter'})
  >>> manager = field.FieldWidgets(personForm, request, context)
  >>> manager.ignoreContext = True
  >>> manager.update()

We have to set the setErrors property to False before calling extract,
we still get the same result from the method call, ...

  >>> manager.setErrors = False
  >>> manager.extract()
  ({'firstName': 'Stephan'}, (<ErrorViewSnippet for RequiredMissing>,))

but there are no side effects on the manager and the widgets:

  >>> manager.errors
  ()
  >>> manager['lastName'].error is None
  True

Customization of Ignoring the Context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note that you can also manually control ignoring the context per field.

  >>> class CustomPersonForm(object):
  ...     prefix = 'form.'
  ...     fields = field.Fields(IPerson).select('id')
  ...     fields += field.Fields(IPerson, ignoreContext=True).select(
  ...                   'firstName', 'lastName')
  >>> customPersonForm = CustomPersonForm()

Let's now create a manager and update it:

  >>> customManager = field.FieldWidgets(customPersonForm, request, context)
  >>> customManager.update()

  >>> customManager['id'].ignoreContext
  False
  >>> customManager['firstName'].ignoreContext
  True
  >>> customManager['lastName'].ignoreContext
  True


Fields -- Custom Widget Factories
---------------------------------

It is possible to declare custom widgets for fields within the field's
declaration.

Let's have a look at the default form first. Initially, the standard
registered widgets are used:

  >>> manager = field.FieldWidgets(personForm, request, srichter)
  >>> manager.update()

  >>> manager['firstName']
  <Widget 'form.widgets.firstName'>

Now we would like to have our own custom input widget:

  >>> class CustomInputWidget(widget.Widget):
  ...     pass

  >>> def CustomInputWidgetFactory(field, request):
  ...     return widget.FieldWidget(field, CustomInputWidget(request))

It can be simply assigned as follows:

  >>> personForm.fields['firstName'].widgetFactory = CustomInputWidgetFactory
  >>> personForm.fields['lastName'].widgetFactory = CustomInputWidgetFactory

Now this widget should be used instead of the registered default one:

  >>> manager = field.FieldWidgets(personForm, request, srichter)
  >>> manager.update()
  >>> manager['firstName']
  <CustomInputWidget 'form.widgets.firstName'>

In the background the widget factory assignment really just registered the
default factory in the ``WidgetFactories`` object, which manages the
custom widgets for all modes. Now all modes show this input widget:

  >>> manager = field.FieldWidgets(personForm, request, srichter)
  >>> manager.mode = interfaces.DISPLAY_MODE
  >>> manager.update()
  >>> manager['firstName']
  <CustomInputWidget 'form.widgets.firstName'>

However, we can also register a specific widget for the display mode:

  >>> class CustomDisplayWidget(widget.Widget):
  ...     pass

  >>> def CustomDisplayWidgetFactory(field, request):
  ...     return widget.FieldWidget(field, CustomDisplayWidget(request))

  >>> personForm.fields['firstName']\
  ...     .widgetFactory[interfaces.DISPLAY_MODE] = CustomDisplayWidgetFactory
  >>> personForm.fields['lastName']\
  ...     .widgetFactory[interfaces.DISPLAY_MODE] = CustomDisplayWidgetFactory

Now the display mode should produce the custom display widget, ...

  >>> manager = field.FieldWidgets(personForm, request, srichter)
  >>> manager.mode = interfaces.DISPLAY_MODE
  >>> manager.update()
  >>> manager['firstName']
  <CustomDisplayWidget 'form.widgets.firstName'>
  >>> manager['lastName']
  <CustomDisplayWidget 'form.widgets.lastName'>

... while the input mode still shows the default custom input widget
on the ``lastName`` field but not on the ``firstName`` field since we
don't have the ``test.Edit`` permission:

  >>> manager = field.FieldWidgets(personForm, request, srichter)
  >>> manager.mode = interfaces.INPUT_MODE
  >>> manager.update()
  >>> manager['firstName']
  <CustomDisplayWidget 'form.widgets.firstName'>
  >>> manager['lastName']
  <CustomInputWidget 'form.widgets.lastName'>

The widgets factories component,

  >>> factories = personForm.fields['firstName'].widgetFactory
  >>> factories
  {'display': <function CustomDisplayWidgetFactory at ...>}

is pretty much a standard dictionary that also manages a default value:

  >>> factories.default
  <function CustomInputWidgetFactory at ...>

When getting a value for a key, if the key is not found, the default is
returned:

  >>> sorted(factories.keys())
  ['display']

  >>> factories[interfaces.DISPLAY_MODE]
  <function CustomDisplayWidgetFactory at ...>
  >>> factories[interfaces.INPUT_MODE]
  <function CustomInputWidgetFactory at ...>

  >>> factories.get(interfaces.DISPLAY_MODE)
  <function CustomDisplayWidgetFactory at ...>
  >>> factories.get(interfaces.INPUT_MODE)
  <function CustomInputWidgetFactory at ...>

If no default is specified,

  >>> factories.default = None

then the dictionary behaves as usual:

  >>> factories[interfaces.DISPLAY_MODE]
  <function CustomDisplayWidgetFactory at ...>
  >>> factories[interfaces.INPUT_MODE]
  Traceback (most recent call last):
  ...
  KeyError: 'input'

  >>> factories.get(interfaces.DISPLAY_MODE)
  <function CustomDisplayWidgetFactory at ...>
  >>> factories.get(interfaces.INPUT_MODE)
