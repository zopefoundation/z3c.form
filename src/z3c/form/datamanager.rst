=============
Data Managers
=============

For the longest time the way widgets retrieved and stored their values on the
actual content/model was done by binding the field to a context and then
setting and getting the attribute from it. This has several distinct design
shortcomings:

1. The field has too much responsibility by knowing about its implementations.

2. There is no way of redefining the method used to store and access data
   other than rewriting fields.

3. Finding the right content/model to modify is an implicit policy: Find an
   adapter for the field's schema and then set the value there.

While implementing some real-world projects, we noticed that this approach is
too limiting and we often could not use the form framework when we wanted or
had to jump through many hoops to make it work for us. For example, if we want
to display a form to collect data that does not correspond to a set of content
components, we were forced to not only write a schema for the form, but also
implement that schema as a class. but all we wanted was a dictionary. For
edit-form like tasks we often also had an initial dictionary, which we just
wanted modified.

Data managers abstract the getting and setting of the data. A data manager is
responsible for setting one piece of data in a particular context.

  >>> from z3c.form import datamanager


Attribute Field Manager
-----------------------

The most common case, of course, is the management of class attributes through
fields. In this case, the data manager needs to know about the context and the
field it is managing the data for.

  >>> import zope.interface
  >>> import zope.schema
  >>> class IPerson(zope.interface.Interface):
  ...     name = zope.schema.TextLine(
  ...         title='Name',
  ...         default='<no name>')
  ...     phone = zope.schema.TextLine(
  ...         title='Phone')

  >>> @zope.interface.implementer(IPerson)
  ... class Person(object):
  ...     name = ''
  ...     def __init__(self, name):
  ...         self.name = name

  >>> stephan = Person('Stephan Richter')

We can now instantiate the data manager for Stephan's name:

  >>> nameDm = datamanager.AttributeField(stephan, IPerson['name'])

The data manager consists of a few simple methods to accomplish its
purpose. Getting the value is done using the ``get()`` or ``query()`` method:

  >>> nameDm.get()
  'Stephan Richter'

  >>> nameDm.query()
  'Stephan Richter'

The value can be set using ``set()``:

  >>> nameDm.set('Stephan "Caveman" Richter')

  >>> nameDm.get()
  'Stephan "Caveman" Richter'
  >>> stephan.name
  'Stephan "Caveman" Richter'

If an attribute is not available, ``get()`` fails and ``query()`` returns a
default value:

  >>> phoneDm = datamanager.AttributeField(stephan, IPerson['phone'])

  >>> phoneDm.get()
  Traceback (most recent call last):
  ...
  AttributeError: 'Person' object has no attribute 'phone'

  >>> phoneDm.query()
  <NO_VALUE>
  >>> phoneDm.query('nothing')
  'nothing'

A final feature that is supported by the data manager is the check whether a
value can be accessed and written. When the context is not security proxied,
both, accessing and writing, is allowed:

  >>> nameDm.canAccess()
  True
  >>> nameDm.canWrite()
  True

To demonstrate the behavior for a security-proxied component, we first have to
provide security declarations for our person:

  >>> from zope.security.management import endInteraction
  >>> from zope.security.management import newInteraction
  >>> from zope.security.management import setSecurityPolicy
  >>> import z3c.form.testing
  >>> endInteraction()
  >>> newPolicy = z3c.form.testing.SimpleSecurityPolicy()
  >>> newPolicy.allowedPermissions = ('View', 'Edit')
  >>> oldpolicy = setSecurityPolicy(newPolicy)
  >>> newInteraction()

  >>> from zope.security.checker import Checker
  >>> from zope.security.checker import defineChecker
  >>> personChecker = Checker({'name':'View', 'name':'Edit'})
  >>> defineChecker(Person, personChecker)

We now need to wrap stephan into a proxy:

  >>> protectedStephan = zope.security.checker.ProxyFactory(stephan)

Since we are not logged in as anyone, we cannot acces or write the value:

  >>> nameDm = datamanager.AttributeField(protectedStephan, IPerson['name'])

  >>> nameDm.canAccess()
  False
  >>> nameDm.canWrite()
  False

Clearly, this also means that ``get()`` and ``set()`` are also shut off:

  >>> nameDm.get()
  Traceback (most recent call last):
  ...
  Unauthorized: (<Person object at ...>, 'name', 'Edit')

  >>> nameDm.set('Stephan')
  Traceback (most recent call last):
  ...
  ForbiddenAttribute: ('name', <Person object at ...>)

Now we have to setup the security system and "log in" as a user:

  >>> newPolicy.allowedPermissions = ('View', 'Edit')
  >>> newPolicy.loggedIn = True

The created principal, with which we are logged in now, can only access the
attribute:

  >>> nameDm.canAccess()
  True
  >>> nameDm.canWrite()
  False

Thus only the ``get()`` method is allowed:

  >>> nameDm.get()
  'Stephan "Caveman" Richter'

  >>> nameDm.set('Stephan')
  Traceback (most recent call last):
  ...
  ForbiddenAttribute: ('name', <Person object at ...>)

If field's schema is not directly provided by the context, the datamanager
will attempt to find an adapter. Let's give the person an address for example:

  >>> class IAddress(zope.interface.Interface):
  ...     city = zope.schema.TextLine(title='City')

  >>> @zope.interface.implementer(IAddress)
  ... class Address(object):
  ...     zope.component.adapts(IPerson)
  ...     def __init__(self, person):
  ...         self.person = person
  ...     @property
  ...     def city(self):
  ...         return getattr(self.person, '_city', None)
  ...     @city.setter
  ...     def city(self, value):
  ...         self.person._city = value

  >>> zope.component.provideAdapter(Address)

Now we can create a data manager for the city attribute:

  >>> cityDm = datamanager.AttributeField(stephan, IAddress['city'])

We can access and write to the city attribute:

  >>> cityDm.canAccess()
  True
  >>> cityDm.canWrite()
  True

Initially there is no value, but of course we can create one:

  >>> cityDm.get()

  >>> cityDm.set('Maynard')
  >>> cityDm.get()
  'Maynard'

The value can be accessed through the adapter itself as well:

  >>> IAddress(stephan).city
  'Maynard'

While we think that implicitly looking up an adapter is not the cleanest
solution, it allows us to mimic the behavior of ``zope.formlib``. We think
that we will eventually provide alternative ways to accomplish the same in a
more explicit way.

If we try to set a value that is read-only, a type error is raised:

  >>> readOnlyName = zope.schema.TextLine(
  ...     __name__='name',
  ...     readonly=True)

  >>> nameDm = datamanager.AttributeField(stephan, readOnlyName)
  >>> nameDm.set('Stephan')
  Traceback (most recent call last):
  ...
  TypeError: Can't set values on read-only fields
             (name=name, class=__builtin__.Person)

Finally, we instantiate the data manager with a ``zope.schema``
field. And we can access the different methods like before.

  >>> nameDm = datamanager.AttributeField(
  ...    stephan, zope.schema.TextLine(__name__ = 'name'))
  >>> nameDm.canAccess()
  True
  >>> nameDm.canWrite()
  True

  >>> nameDm.get()
  'Stephan "Caveman" Richter'
  >>> nameDm.query()
  'Stephan "Caveman" Richter'

  >>> nameDm.set('Stephan Richter')
  >>> nameDm.get()
  'Stephan Richter'

Dictionary Field Manager
------------------------

Another implementation of the data manager interface is provided by the
dictionary field manager, which does not expect an instance with attributes as
its context, but a dictionary. It still uses a field to determine the key to
modify.

  >>> personDict = {}
  >>> nameDm = datamanager.DictionaryField(personDict, IPerson['name'])

The datamanager can really only deal with dictionaries and mapping types:

  >>> import zope.interface.common.mapping
  >>> import persistent.mapping
  >>> import persistent.dict
  >>> @zope.interface.implementer(zope.interface.common.mapping.IMapping)
  ... class MyMapping(object):
  ...     pass
  >>> datamanager.DictionaryField(MyMapping(), IPerson['name'])
  <z3c.form.datamanager.DictionaryField object at ...>
  >>> datamanager.DictionaryField(persistent.mapping.PersistentMapping(),
  ...     IPerson['name'])
  <z3c.form.datamanager.DictionaryField object at ...>
  >>> datamanager.DictionaryField(persistent.dict.PersistentDict(),
  ...     IPerson['name'])
  <z3c.form.datamanager.DictionaryField object at ...>

  >>> datamanager.DictionaryField([], IPerson['name'])
  Traceback (most recent call last):
  ...
  ValueError: Data are not a dictionary: <type 'list'>

Let's now access the name:

  >>> nameDm.get()
  Traceback (most recent call last):
  ...
  AttributeError

  >>> nameDm.query()
  <NO_VALUE>

Initially we get the default value (as specified in the field), since the
person dictionariy has no entry. If no default value has been specified in the
field, the missing value is returned.

Now we set a value and it should be available:

  >>> nameDm.set('Roger Ineichen')

  >>> nameDm.get()
  'Roger Ineichen'
  >>> personDict
  {'name': 'Roger Ineichen'}

Since this dictionary is not security proxied, any field can be accessed and
written to:

  >>> nameDm.canAccess()
  True
  >>> nameDm.canWrite()
  True

As with the attribute data manager, readonly fields cannot be set:

  >>> nameDm = datamanager.DictionaryField(personDict, readOnlyName)
  >>> nameDm.set('Stephan')
  Traceback (most recent call last):
  ...
  TypeError: Can't set values on read-only fields name=name


Cleanup
-------

We clean up the changes we made in these examples:

  >>> endInteraction()
  >>> ignore = setSecurityPolicy(oldpolicy)
