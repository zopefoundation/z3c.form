=============================
Utility Functions and Classes
=============================

This file documents the utility functions and classes that are otherwise not
tested.

  >>> from z3c.form import util


``createId(name)`` Function
---------------------------

This function converts an arbitrary unicode string into a valid Python
identifier. If the name is a valid identifier, then it is just returned, but
all upper case letters are lowered:

  >>> util.createId('Change')
  'change'

  >>> util.createId('Change_2')
  'change_2'

If a name is not a valid identifier, a hex code of the string is created:

  >>> util.createId('Change 3')
  '4368616e67652033'

The function can also handle non-ASCII characters:

  >>> id = util.createId('Ändern')

Since the output depends on how Python is compiled (UCS-2 or 4), we only check
that we have a valid id:

  >>> util._identifier.match(id) is not None
  True


``createCSSId(name)`` Function
------------------------------

This function takes any unicode name and coverts it into an id that
can be easily referenced by CSS selectors.  Characters that are in the
ascii alphabet, are numbers, or are '-' or '_' will be left the same.
All other characters will be converted to ordinal numbers:

  >>> util.createCSSId('NormalId')
  'NormalId'
  >>> id = util.createCSSId('عَرَ')
  >>> util._identifier.match(id) is not None
  True
  >>> util.createCSSId('This has spaces')
  'This20has20spaces'

  >>> util.createCSSId(str([(1, 'x'), ('foobar', 42)]))
  '5b2812c2027x27292c202827foobar272c2042295d'


``getWidgetById(form, id)`` Function
------------------------------------

Given a form and a widget id, this function extracts the widget for you. First
we need to create a properly developed form:

  >>> import zope.interface
  >>> import zope.schema

  >>> class IPerson(zope.interface.Interface):
  ...     name = zope.schema.TextLine(title='Name')

  >>> from z3c.form import form, field
  >>> class AddPerson(form.AddForm):
  ...     fields = field.Fields(IPerson)

  >>> from z3c.form import testing
  >>> testing.setupFormDefaults()

  >>> addPerson = AddPerson(None, testing.TestRequest())
  >>> addPerson.update()

We can now ask for the widget:

  >>> util.getWidgetById(addPerson, 'form-widgets-name')
  <TextWidget 'form.widgets.name'>

The widget id can be split into a prefix and a widget name. The id must always
start with the correct prefix, otherwise a value error is raised:

  >>> util.getWidgetById(addPerson, 'myform-widgets-name')
  Traceback (most recent call last):
  ...
  ValueError: Name 'myform.widgets.name' must start with prefix 'form.widgets.'

If the widget is not found but the prefix is correct, ``None`` is returned:

  >>> util.getWidgetById(addPerson, 'form-widgets-myname') is None
  True


``extractFileName(form, id, cleanup=True, allowEmptyPostfix=False)`` Function
-----------------------------------------------------------------------------

Test the filename extraction method:

  >>> class IDocument(zope.interface.Interface):
  ...     data = zope.schema.Bytes(title='Data')

Define a widgets stub and a upload widget stub class and setup them as a
faked form:

  >>> class FileUploadWidgetStub(object):
  ...     def __init__(self):
  ...         self.filename = None

  >>> class WidgetsStub(object):
  ...     def __init__(self):
  ...         self.data = FileUploadWidgetStub()
  ...         self.prefix = 'widgets.'
  ...     def get(self, name, default):
  ...         return self.data

  >>> class FileUploadFormStub(form.AddForm):
  ...     def __init__(self):
  ...         self.widgets = WidgetsStub()
  ...
  ...     def setFakeFileName(self, filename):
  ...         self.widgets.data.filename = filename

Now we can setup the stub form. Note this form is just a fake it's not a real
implementation. We just provide a form like class which simulates the
FileUpload object in the a widget. See `z3c/form/browser/file.rst` for a real
file upload test uscase:

  >>> uploadForm = FileUploadFormStub()
  >>> uploadForm.setFakeFileName('foo.txt')

And extract the filename

  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.txt'

Test a unicode filename:

  >>> uploadForm.setFakeFileName('foo.txt')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.txt'

Test a windows IE uploaded filename:

  >>> uploadForm.setFakeFileName('D:\\some\\folder\\foo.txt')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.txt'

Test another filename:

  >>> uploadForm.setFakeFileName('D:/some/folder/foo.txt')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.txt'

Test another filename:

  >>> uploadForm.setFakeFileName('/tmp/folder/foo.txt')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.txt'

Test special characters in filename, e.g. dots:

  >>> uploadForm.setFakeFileName('/tmp/foo.bar.txt')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.bar.txt'

Test some other special characters in filename:

  >>> uploadForm.setFakeFileName('/tmp/foo-bar.v.0.1.txt')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True)
  'foo-bar.v.0.1.txt'

Test special characters in file path of filename:

  >>> uploadForm.setFakeFileName('/tmp-v.1.0/foo-bar.v.0.1.txt')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True)
  'foo-bar.v.0.1.txt'

Test optional keyword arguments. But remember it's hard for Zope to guess the
content type for filenames without extensions:

  >>> uploadForm.setFakeFileName('minimal')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True,
  ...     allowEmptyPostfix=True)
  'minimal'

  >>> uploadForm.setFakeFileName('/tmp/minimal')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True,
  ...     allowEmptyPostfix=True)
  'minimal'

  >>> uploadForm.setFakeFileName('D:\\some\\folder\\minimal')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True,
  ...     allowEmptyPostfix=True)
  'minimal'

There will be a ValueError if we get a empty filename by default:

  >>> uploadForm.setFakeFileName('/tmp/minimal')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=True)
  Traceback (most recent call last):
  ...
  ValueError: Missing filename extension.

We also can skip removing a path from a upload. Note only IE will upload a
path in a upload ``<input type="file" ...>`` field:

  >>> uploadForm.setFakeFileName('/tmp/foo.txt')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=False)
  '/tmp/foo.txt'

  >>> uploadForm.setFakeFileName('/tmp-v.1.0/foo-bar.v.0.1.txt')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=False)
  '/tmp-v.1.0/foo-bar.v.0.1.txt'

  >>> uploadForm.setFakeFileName('D:\\some\\folder\\foo.txt')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=False)
  'D:\\some\\folder\\foo.txt'

And missing filename extensions are also not allowed by deafault if we skip
the filename:

  >>> uploadForm.setFakeFileName('/tmp/minimal')
  >>> util.extractFileName(uploadForm, 'form.widgets.data', cleanup=False)
  Traceback (most recent call last):
  ...
  ValueError: Missing filename extension.


``extractContentType(form, id)`` Function
-----------------------------------------

There is also a method which is able to extract the content type for a given
file upload. We can use the stub form from the previous test.

Not sure if this an error but on my windows system this test returns
image/pjpeg (progressive jpeg) for foo.jpg and image/x-png for foo.png. So
let's allow this too since this depends on guess_content_type and is not
really a part of z3c.form.

  >>> uploadForm = FileUploadFormStub()
  >>> uploadForm.setFakeFileName('foo.txt')
  >>> util.extractContentType(uploadForm, 'form.widgets.data')
  'text/plain'

  >>> uploadForm.setFakeFileName('foo.gif')
  >>> util.extractContentType(uploadForm, 'form.widgets.data')
  'image/gif'

  >>> uploadForm.setFakeFileName('foo.jpg')
  >>> util.extractContentType(uploadForm, 'form.widgets.data')
  'image/...jpeg'

  >>> uploadForm.setFakeFileName('foo.png')
  >>> util.extractContentType(uploadForm, 'form.widgets.data')
  'image/...png'

  >>> uploadForm.setFakeFileName('foo.tif')
  >>> util.extractContentType(uploadForm, 'form.widgets.data')
  'image/tiff'

  >>> uploadForm.setFakeFileName('foo.doc')
  >>> util.extractContentType(uploadForm, 'form.widgets.data')
  'application/msword'

  >>> uploadForm.setFakeFileName('foo.zip')
  >>> (util.extractContentType(uploadForm, 'form.widgets.data')
  ...     in ('application/zip', 'application/x-zip-compressed'))
  True

  >>> uploadForm.setFakeFileName('foo.unknown')
  >>> util.extractContentType(uploadForm, 'form.widgets.data')
  'text/x-unknown-content-type'


`Manager` object
----------------

The manager object is a base class of a mapping object that keeps track of the
key order as they are added.

  >>> manager = util.Manager()

Initially the manager is empty:

  >>> len(manager)
  0

Since this base class mainly defines a read-interface, we have to add the
values manually:

  >>> manager['b'] = 2
  >>> manager['a'] = 1

Let's iterate through the manager:

  >>> tuple(iter(manager))
  ('b', 'a')
  >>> list(manager.keys())
  ['b', 'a']
  >>> list(manager.values())
  [2, 1]
  >>> list(manager.items())
  [('b', 2), ('a', 1)]

Let's ow look at item access:

  >>> 'b' in manager
  True
  >>> manager.get('b')
  2
  >>> manager.get('c', 'None')
  'None'

It also supports deletion:

  >>> del manager['b']
  >>> list(manager.items())
  [('a', 1)]


`SelectionManager` object
-------------------------

The selection manager is an extension to the manager and provides a few more
API functions. Unfortunately, this base class is totally useless without a
sensible constructor:

  >>> import zope.interface

  >>> class MySelectionManager(util.SelectionManager):
  ...     managerInterface = zope.interface.Interface
  ...
  ...     def __init__(self, *args):
  ...         super(MySelectionManager, self).__init__()
  ...         args = list(args)
  ...         for arg in args:
  ...             if isinstance(arg, MySelectionManager):
  ...                 args += arg.values()
  ...                 continue
  ...             self[str(arg)] = arg

Let's now create two managers:

  >>> manager1 = MySelectionManager(1, 2)
  >>> manager2 = MySelectionManager(3, 4)

You can add two managers:

  >>> manager = manager1 + manager2
  >>> list(manager.values())
  [1, 2, 3, 4]

Next, you can select only certain names:

  >>> list(manager.select('1', '2', '3').values())
  [1, 2, 3]

Or simply omit a value.

  >>> list(manager.omit('2').values())
  [1, 3, 4]

You can also easily copy a manager:

  >>> manager.copy() is not manager
  True

That's all.

`getSpecification()` function
-----------------------------

This function is capable of returning an `ISpecification` for any object,
including instances.

For an interface, it simply returns the interface:

  >>> import zope.interface
  >>> class IFoo(zope.interface.Interface):
  ...     pass

  >>> util.getSpecification(IFoo) == IFoo
  True

Ditto for a class:

  >>> class Bar(object):
  ...     pass

  >>> util.getSpecification(Bar) == Bar
  True

For an instance, it will create a marker interface on the fly if necessary:

  >>> bar = Bar()
  >>> util.getSpecification(bar) # doctest: +ELLIPSIS
  <InterfaceClass z3c.form.util.IGeneratedForObject_...>

The ellipsis represents a hash of the object.

If the function is called twice on the same object, it will not create a new
marker each time:

  >>> baz = Bar()
  >>> barMarker = util.getSpecification(bar)
  >>> bazMarker1 = util.getSpecification(baz)
  >>> bazMarker2 = util.getSpecification(baz)

  >>> barMarker is bazMarker1
  False

  >>> bazMarker1 == bazMarker2
  True
  >>> bazMarker1 is bazMarker2
  True

`changedField()` function
-------------------------

Decide whether a field was changed/modified.

  >>> class IPerson(zope.interface.Interface):
  ...     login = zope.schema.TextLine(
  ...         title='Login')
  ...     address = zope.schema.Object(
  ...         schema=zope.interface.Interface)

  >>> @zope.interface.implementer(IPerson)
  ... class Person(object):
  ...     login = 'johndoe'
  >>> person = Person()

field.context is None and no context passed:

  >>> util.changedField(IPerson['login'], 'foo')
  True

IObject field:

  >>> util.changedField(IPerson['address'], object(), context = person)
  True

field.context or context passed:

  >>> import z3c.form.datamanager
  >>> zope.component.provideAdapter(z3c.form.datamanager.AttributeField)

  >>> util.changedField(IPerson['login'], 'foo', context = person)
  True
  >>> util.changedField(IPerson['login'], 'johndoe', context = person)
  False

  >>> fld = IPerson['login'].bind(person)
  >>> util.changedField(fld, 'foo')
  True
  >>> util.changedField(fld, 'johndoe')
  False

No access:

  >>> save = z3c.form.datamanager.AttributeField.canAccess
  >>> z3c.form.datamanager.AttributeField.canAccess = lambda self: False

  >>> util.changedField(IPerson['login'], 'foo', context = person)
  True
  >>> util.changedField(IPerson['login'], 'johndoe', context = person)
  True

  >>> z3c.form.datamanager.AttributeField.canAccess = save


`changedWidget()` function
---------------------------

Decide whether a widget value was changed/modified.

  >>> import z3c.form.testing
  >>> request = z3c.form.testing.TestRequest()
  >>> import z3c.form.widget
  >>> widget = z3c.form.widget.Widget(request)

If the widget is not IContextAware, there's nothing to check:

  >>> from z3c.form import interfaces
  >>> interfaces.IContextAware.providedBy(widget)
  False

  >>> util.changedWidget(widget, 'foo')
  True

Make it IContextAware:

  >>> widget.context = person
  >>> zope.interface.alsoProvides(widget, interfaces.IContextAware)

  >>> widget.field = IPerson['login']

  >> util.changedWidget(widget, 'foo')
  True

  >>> util.changedWidget(widget, 'johndoe')
  False

Field and context is also overridable:

  >>> widget.field = None
  >>> util.changedWidget(widget, 'johndoe', field=IPerson['login'])
  False

  >>> p2 = Person()
  >>> p2.login = 'foo'

  >>> util.changedWidget(widget, 'foo', field=IPerson['login'], context=p2)
  False

`sortedNone()` function
------------------------

  >>> util.sortedNone([None, 'a', 'b'])
  [None, 'a', 'b']

  >>> util.sortedNone([None, 1, 2])
  [None, 1, 2]

  >>> util.sortedNone([None, True, False])
  [None, False, True]

  >>> util.sortedNone([['true'], [], ['false']])
  [[], ['false'], ['true']]

  >>> util.sortedNone([('false',), ('true',), ()])
  [(), ('false',), ('true',)]
