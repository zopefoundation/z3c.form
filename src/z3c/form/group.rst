===========
Group Forms
===========

Group forms allow you to split up a form into several logical units without
much overhead. To the parent form, groups should be only dealt with during
coding and be transparent on the data extraction level.

For the examples to work, we have to bring up most of the form framework:

  >>> from z3c.form import testing
  >>> testing.setupFormDefaults()

So let's first define a complex content component that warrants setting up
multiple groups:

  >>> import zope.interface
  >>> import zope.schema

  >>> class IVehicleRegistration(zope.interface.Interface):
  ...     firstName = zope.schema.TextLine(title=u'First Name')
  ...     lastName = zope.schema.TextLine(title=u'Last Name')
  ...
  ...     license = zope.schema.TextLine(title=u'License')
  ...     address = zope.schema.TextLine(title=u'Address')
  ...
  ...     model = zope.schema.TextLine(title=u'Model')
  ...     make = zope.schema.TextLine(title=u'Make')
  ...     year = zope.schema.TextLine(title=u'Year')

  >>> @zope.interface.implementer(IVehicleRegistration)
  ... class VehicleRegistration(object):
  ...
  ...     def __init__(self, **kw):
  ...         for name, value in kw.items():
  ...             setattr(self, name, value)

The schema above can be separated into basic, license, and car information,
where the latter two will be placed into groups. First we create the two
groups:

  >>> from z3c.form import field, group

  >>> class LicenseGroup(group.Group):
  ...     label = u'License'
  ...     fields = field.Fields(IVehicleRegistration).select(
  ...         'license', 'address')

  >>> class CarGroup(group.Group):
  ...     label = u'Car'
  ...     fields = field.Fields(IVehicleRegistration).select(
  ...         'model', 'make', 'year')

Most of the group is setup like any other (sub)form. Additionally, you can
specify a label, which is a human-readable string that can be used for layout
purposes.

Let's now create an add form for the entire vehicle registration. In
comparison to a regular add form, you only need to add the ``GroupForm`` as
one of the base classes. The groups are specified in a simple tuple:

  >>> import os
  >>> from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
  >>> from z3c.form import form, tests

  >>> class RegistrationAddForm(group.GroupForm, form.AddForm):
  ...     fields = field.Fields(IVehicleRegistration).select(
  ...         'firstName', 'lastName')
  ...     groups = (LicenseGroup, CarGroup)
  ...
  ...     template = ViewPageTemplateFile(
  ...         'simple_groupedit.pt', os.path.dirname(tests.__file__))
  ...
  ...     def create(self, data):
  ...         return VehicleRegistration(**data)
  ...
  ...     def add(self, object):
  ...         self.getContent()['obj1'] = object
  ...         return object


Note: The order of the base classes is very important here. The ``GroupForm``
class must be left of the ``AddForm`` class, because the ``GroupForm`` class
overrides some methods of the ``AddForm`` class.

Now we can instantiate the form:

  >>> request = testing.TestRequest()

  >>> add = RegistrationAddForm(None, request)
  >>> add.update()

After the form is updated the tuple of group classes is converted to group
instances:

  >>> add.groups
  (<LicenseGroup object at ...>, <CarGroup object at ...>)

If we happen to update the add form again, the groups that have
already been converted to instances ares skipped.

  >>> add.update()
  >>> add.groups
  (<LicenseGroup object at ...>, <CarGroup object at ...>)

We can now render the form:

  >>> print(add.render())
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <form action=".">
        <div class="row">
          <label for="form-widgets-firstName">First Name</label>
          <input type="text" id="form-widgets-firstName"
                 name="form.widgets.firstName"
                 class="text-widget required textline-field"
                 value="" />
        </div>
        <div class="row">
          <label for="form-widgets-lastName">Last Name</label>
          <input type="text" id="form-widgets-lastName"
                 name="form.widgets.lastName"
                 class="text-widget required textline-field"
                 value="" />
        </div>
        <fieldset>
          <legend>License</legend>
          <div class="row">
            <label for="form-widgets-license">License</label>
            <input type="text" id="form-widgets-license"
                   name="form.widgets.license"
                   class="text-widget required textline-field"
                   value="" />
          </div>
          <div class="row">
            <label for="form-widgets-address">Address</label>
            <input type="text" id="form-widgets-address"
                   name="form.widgets.address"
                   class="text-widget required textline-field"
                   value="" />
          </div>
        </fieldset>
        <fieldset>
          <legend>Car</legend>
          <div class="row">
            <label for="form-widgets-model">Model</label>
            <input type="text" id="form-widgets-model"
                   name="form.widgets.model"
                   class="text-widget required textline-field"
                   value="" />
          </div>
          <div class="row">
            <label for="form-widgets-make">Make</label>
            <input type="text" id="form-widgets-make"
                   name="form.widgets.make"
                   class="text-widget required textline-field"
                   value="" />
          </div>
          <div class="row">
            <label for="form-widgets-year">Year</label>
            <input type="text" id="form-widgets-year"
                   name="form.widgets.year"
                   class="text-widget required textline-field"
                   value="" />
          </div>
        </fieldset>
        <div class="action">
          <input type="submit" id="form-buttons-add"
                 name="form.buttons.add" class="submit-widget button-field"
                 value="Add" />
        </div>
      </form>
    </body>
  </html>


Registering a custom event handler for the DataExtractedEvent
--------------------------------------------------------------

  >>> data_extracted_eventlog = []
  >>> from z3c.form.events import DataExtractedEvent
  >>> @zope.component.adapter(DataExtractedEvent)
  ... def data_extracted_logger(event):
  ...     data_extracted_eventlog.append(event)
  >>> zope.component.provideHandler(data_extracted_logger)


Let's now submit the form, but forgetting to enter the address:

  >>> request = testing.TestRequest(form={
  ...     'form.widgets.firstName': u'Stephan',
  ...     'form.widgets.lastName': u'Richter',
  ...     'form.widgets.license': u'MA 40387',
  ...     'form.widgets.model': u'BMW',
  ...     'form.widgets.make': u'325',
  ...     'form.widgets.year': u'2005',
  ...     'form.buttons.add': u'Add'
  ...     })

  >>> add = RegistrationAddForm(None, request)
  >>> add.update()
  >>> print(testing.render(add, './/xmlns:i'))  # doctest: +NOPARSE_MARKUP
  <i >There were some errors.</i>
  ...

  >>> print(testing.render(add, './/xmlns:fieldset[1]/xmlns:ul'))  # doctest: +NOPARSE_MARKUP
  <ul >
    <li>
      Address: <div class="error">Required input is missing.</div>
    </li>
  </ul>
  ...

As you can see, the template is clever enough to just report the errors at the
top of the form, but still report the actual problem within the group.


Check, if DataExtractedEvent was thrown:

  >>> len(data_extracted_eventlog) > 0
  True


So what happens, if errors happen inside and outside a group?

  >>> request = testing.TestRequest(form={
  ...     'form.widgets.firstName': u'Stephan',
  ...     'form.widgets.license': u'MA 40387',
  ...     'form.widgets.model': u'BMW',
  ...     'form.widgets.make': u'325',
  ...     'form.widgets.year': u'2005',
  ...     'form.buttons.add': u'Add'
  ...     })

  >>> add = RegistrationAddForm(None, request)
  >>> add.update()
  >>> print(testing.render(add, './/xmlns:i'))  # doctest: +NOPARSE_MARKUP
  <i >There were some errors.</i>
  ...

  >>> print(testing.render(add, './/xmlns:ul'))  # doctest: +NOPARSE_MARKUP
  <ul >
    <li>
    Last Name:
      <div class="error">Required input is missing.</div>
    </li>
  </ul>
  ...
  <ul >
    <li>
    Address:
      <div class="error">Required input is missing.</div>
    </li>
  </ul>
  ...

  >>> print(testing.render(add, './/xmlns:fieldset[1]/xmlns:ul'))  # doctest: +NOPARSE_MARKUP
  <ul >
    <li>
      Address: <div class="error">Required input is missing.</div>
    </li>
  </ul>
  ...

Let's now successfully complete the add form.

  >>> from zope.container import btree
  >>> context = btree.BTreeContainer()

  >>> request = testing.TestRequest(form={
  ...     'form.widgets.firstName': u'Stephan',
  ...     'form.widgets.lastName': u'Richter',
  ...     'form.widgets.license': u'MA 40387',
  ...     'form.widgets.address': u'10 Main St, Maynard, MA',
  ...     'form.widgets.model': u'BMW',
  ...     'form.widgets.make': u'325',
  ...     'form.widgets.year': u'2005',
  ...     'form.buttons.add': u'Add'
  ...     })

  >>> add = RegistrationAddForm(context, request)
  >>> add.update()

The object is now added to the container and all attributes should be set:

  >>> reg = context['obj1']
  >>> reg.firstName
  u'Stephan'
  >>> reg.lastName
  u'Richter'
  >>> reg.license
  u'MA 40387'
  >>> reg.address
  u'10 Main St, Maynard, MA'
  >>> reg.model
  u'BMW'
  >>> reg.make
  u'325'
  >>> reg.year
  u'2005'

Let's now have a look at an edit form for the vehicle registration:

  >>> class RegistrationEditForm(group.GroupForm, form.EditForm):
  ...     fields = field.Fields(IVehicleRegistration).select(
  ...         'firstName', 'lastName')
  ...     groups = (LicenseGroup, CarGroup)
  ...
  ...     template = ViewPageTemplateFile(
  ...         'simple_groupedit.pt', os.path.dirname(tests.__file__))

  >>> request = testing.TestRequest()

  >>> edit = RegistrationEditForm(reg, request)
  >>> edit.update()

After updating the form, we can render the HTML:

  >>> print(edit.render())
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <form action=".">
        <div class="row">
          <label for="form-widgets-firstName">First Name</label>
          <input type="text" id="form-widgets-firstName"
                 name="form.widgets.firstName"
                 class="text-widget required textline-field"
                 value="Stephan" />
        </div>
        <div class="row">
          <label for="form-widgets-lastName">Last Name</label>
          <input type="text" id="form-widgets-lastName"
                 name="form.widgets.lastName"
                 class="text-widget required textline-field"
                 value="Richter" />
         </div>
        <fieldset>
          <legend>License</legend>
          <div class="row">
            <label for="form-widgets-license">License</label>
            <input type="text" id="form-widgets-license"
                   name="form.widgets.license"
                   class="text-widget required textline-field"
                   value="MA 40387" />
          </div>
          <div class="row">
            <label for="form-widgets-address">Address</label>
            <input type="text" id="form-widgets-address"
                   name="form.widgets.address"
                   class="text-widget required textline-field"
                   value="10 Main St, Maynard, MA" />
          </div>
        </fieldset>
        <fieldset>
          <legend>Car</legend>
          <div class="row">
            <label for="form-widgets-model">Model</label>
            <input type="text" id="form-widgets-model"
                   name="form.widgets.model"
                   class="text-widget required textline-field"
                   value="BMW" />
          </div>
          <div class="row">
            <label for="form-widgets-make">Make</label>
            <input type="text" id="form-widgets-make"
                   name="form.widgets.make"
                   class="text-widget required textline-field"
                   value="325" />
          </div>
          <div class="row">
            <label for="form-widgets-year">Year</label>
            <input type="text" id="form-widgets-year"
                   name="form.widgets.year"
                   class="text-widget required textline-field"
                   value="2005" />
          </div>
        </fieldset>
        <div class="action">
          <input type="submit" id="form-buttons-apply"
                 name="form.buttons.apply" class="submit-widget button-field"
                 value="Apply" />
        </div>
      </form>
    </body>
  </html>

The behavior when an error occurs is identical to that of the add form:

  >>> request = testing.TestRequest(form={
  ...     'form.widgets.firstName': u'Stephan',
  ...     'form.widgets.lastName': u'Richter',
  ...     'form.widgets.license': u'MA 40387',
  ...     'form.widgets.model': u'BMW',
  ...     'form.widgets.make': u'325',
  ...     'form.widgets.year': u'2005',
  ...     'form.buttons.apply': u'Apply'
  ...     })

  >>> edit = RegistrationEditForm(reg, request)
  >>> edit.update()
  >>> print(testing.render(edit, './/xmlns:i'))  # doctest: +NOPARSE_MARKUP
  <i >There were some errors.</i>
  ...

  >>> print(testing.render(edit, './/xmlns:ul'))  # doctest: +NOPARSE_MARKUP
  <ul >
    <li>
    Address:
      <div class="error">Required input is missing.</div>
    </li>
  </ul>
  ...

  >>> print(testing.render(edit, './/xmlns:fieldset/xmlns:ul'))  # doctest: +NOPARSE_MARKUP
  <ul >
    <li>
      Address: <div class="error">Required input is missing.</div>
    </li>
  </ul>
  ...

When an edit form with groups is successfully committed, a detailed
object-modified event is sent out telling the system about the changes.
To see the error, let's create an event subscriber for object-modified events:

  >>> eventlog = []
  >>> import zope.lifecycleevent
  >>> @zope.component.adapter(zope.lifecycleevent.ObjectModifiedEvent)
  ... def logEvent(event):
  ...     eventlog.append(event)
  >>> zope.component.provideHandler(logEvent)


Let's now complete the form successfully:

  >>> request = testing.TestRequest(form={
  ...     'form.widgets.firstName': u'Stephan',
  ...     'form.widgets.lastName': u'Richter',
  ...     'form.widgets.license': u'MA 4038765',
  ...     'form.widgets.address': u'11 Main St, Maynard, MA',
  ...     'form.widgets.model': u'Ford',
  ...     'form.widgets.make': u'F150',
  ...     'form.widgets.year': u'2006',
  ...     'form.buttons.apply': u'Apply'
  ...     })

  >>> edit = RegistrationEditForm(reg, request)
  >>> edit.update()

The success message will be shown on the form, ...

  >>> print(testing.render(edit, './/xmlns:i'))  # doctest: +NOPARSE_MARKUP
  <i >Data successfully updated.</i>
  ...

and the data are correctly updated:

  >>> reg.firstName
  u'Stephan'
  >>> reg.lastName
  u'Richter'
  >>> reg.license
  u'MA 4038765'
  >>> reg.address
  u'11 Main St, Maynard, MA'
  >>> reg.model
  u'Ford'
  >>> reg.make
  u'F150'
  >>> reg.year
  u'2006'

Let's look at the event:

  >>> event = eventlog[-1]
  >>> event
  <zope...ObjectModifiedEvent object at ...>

The event's description contains the changed Interface and the names of
all changed fields, even if they where in different groups:

  >>> attrs = event.descriptions[0]
  >>> attrs.interface
  <InterfaceClass __builtin__.IVehicleRegistration>
  >>> attrs.attributes
  ('license', 'address', 'model', 'make', 'year')


Group form as instance
----------------------

It is also possible to use group instances in forms. Let's setup our previous
form and assing a group instance:

  >>> class RegistrationEditForm(group.GroupForm, form.EditForm):
  ...     fields = field.Fields(IVehicleRegistration).select(
  ...         'firstName', 'lastName')
  ...
  ...     template = ViewPageTemplateFile(
  ...         'simple_groupedit.pt', os.path.dirname(tests.__file__))

  >>> request = testing.TestRequest()

  >>> edit = RegistrationEditForm(reg, request)

Instanciate the form and use a group class and a group instance:

  >>> carGroupInstance = CarGroup(edit.context, request, edit)
  >>> edit.groups = (LicenseGroup, carGroupInstance)
  >>> edit.update()
  >>> print(edit.render())
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <form action=".">
        <div class="row">
          <label for="form-widgets-firstName">First Name</label>
          <input id="form-widgets-firstName"
                 name="form.widgets.firstName"
                 class="text-widget required textline-field"
                 value="Stephan" type="text" />
        </div>
        <div class="row">
          <label for="form-widgets-lastName">Last Name</label>
          <input id="form-widgets-lastName"
                 name="form.widgets.lastName"
                 class="text-widget required textline-field"
                 value="Richter" type="text" />
        </div>
        <fieldset>
          <legend>License</legend>
        <div class="row">
          <label for="form-widgets-license">License</label>
          <input id="form-widgets-license"
                 name="form.widgets.license"
                 class="text-widget required textline-field"
                 value="MA 4038765" type="text" />
        </div>
        <div class="row">
          <label for="form-widgets-address">Address</label>
          <input id="form-widgets-address"
                 name="form.widgets.address"
                 class="text-widget required textline-field"
                 value="11 Main St, Maynard, MA" type="text" />
        </div>
        </fieldset>
        <fieldset>
          <legend>Car</legend>
        <div class="row">
          <label for="form-widgets-model">Model</label>
          <input id="form-widgets-model" name="form.widgets.model"
                 class="text-widget required textline-field"
                 value="Ford" type="text" />
        </div>
        <div class="row">
          <label for="form-widgets-make">Make</label>
          <input id="form-widgets-make" name="form.widgets.make"
                 class="text-widget required textline-field"
                 value="F150" type="text" />
        </div>
        <div class="row">
          <label for="form-widgets-year">Year</label>
          <input id="form-widgets-year" name="form.widgets.year"
                 class="text-widget required textline-field"
                 value="2006" type="text" />
            </div>
        </fieldset>
        <div class="action">
          <input id="form-buttons-apply" name="form.buttons.apply"
                 class="submit-widget button-field" value="Apply"
                 type="submit" />
        </div>
      </form>
    </body>
  </html>

Groups with Different Content
-----------------------------

You can customize the content for a group by overriding a group's
``getContent`` method.  This is a very easy way to get around not
having object widgets.  For example, suppose we want to maintain the
vehicle owner's information in a separate class than the vehicle.  We
might have an ``IVehicleOwner`` interface like so.

  >>> class IVehicleOwner(zope.interface.Interface):
  ...     firstName = zope.schema.TextLine(title=u'First Name')
  ...     lastName = zope.schema.TextLine(title=u'Last Name')

Then out ``IVehicleRegistration`` interface would include an object
field for the owner instead of the ``firstName`` and ``lastName``
fields.

  >>> class IVehicleRegistration(zope.interface.Interface):
  ...     owner = zope.schema.Object(title=u'Owner', schema=IVehicleOwner)
  ...
  ...     license = zope.schema.TextLine(title=u'License')
  ...     address = zope.schema.TextLine(title=u'Address')
  ...
  ...     model = zope.schema.TextLine(title=u'Model')
  ...     make = zope.schema.TextLine(title=u'Make')
  ...     year = zope.schema.TextLine(title=u'Year')

Now let's create simple implementations of these two interfaces.

  >>> @zope.interface.implementer(IVehicleOwner)
  ... class VehicleOwner(object):
  ...
  ...     def __init__(self, **kw):
  ...         for name, value in kw.items():
  ...             setattr(self, name, value)

  >>> @zope.interface.implementer(IVehicleRegistration)
  ... class VehicleRegistration(object):
  ...
  ...     def __init__(self, **kw):
  ...         for name, value in kw.items():
  ...             setattr(self, name, value)

Now we can create a group just for the owner with its own
``getContent`` method that simply returns the ``owner`` object field
of the ``VehicleRegistration`` instance.

  >>> class OwnerGroup(group.Group):
  ...     label = u'Owner'
  ...     fields = field.Fields(IVehicleOwner, prefix='owner')
  ...
  ...     def getContent(self):
  ...         return self.context.owner

When we create an Edit form for example, we should omit the ``owner``
field which is taken care of with the group.

  >>> class RegistrationEditForm(group.GroupForm, form.EditForm):
  ...     fields = field.Fields(IVehicleRegistration).omit(
  ...         'owner')
  ...     groups = (OwnerGroup,)
  ...
  ...     template = ViewPageTemplateFile(
  ...         'simple_groupedit.pt', os.path.dirname(tests.__file__))

  >>> reg = VehicleRegistration(
  ...               license=u'MA 40387',
  ...               address=u'10 Main St, Maynard, MA',
  ...               model=u'BMW',
  ...               make=u'325',
  ...               year=u'2005',
  ...               owner=VehicleOwner(firstName=u'Stephan',
  ...                                  lastName=u'Richter'))
  >>> request = testing.TestRequest()

  >>> edit = RegistrationEditForm(reg, request)
  >>> edit.update()

When we render the form, the group appears as we would expect but with
the ``owner`` prefix for the fields.

  >>> print(edit.render())
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <form action=".">
        <div class="row">
          <label for="form-widgets-license">License</label>
          <input type="text" id="form-widgets-license"
                 name="form.widgets.license"
                 class="text-widget required textline-field"
                 value="MA 40387" />
        </div>
        <div class="row">
          <label for="form-widgets-address">Address</label>
          <input type="text" id="form-widgets-address"
                 name="form.widgets.address"
                 class="text-widget required textline-field"
                 value="10 Main St, Maynard, MA" />
        </div>
        <div class="row">
          <label for="form-widgets-model">Model</label>
          <input type="text" id="form-widgets-model"
                 name="form.widgets.model"
                 class="text-widget required textline-field"
                 value="BMW" />
        </div>
        <div class="row">
          <label for="form-widgets-make">Make</label>
          <input type="text" id="form-widgets-make"
                 name="form.widgets.make"
                 class="text-widget required textline-field"
                 value="325" />
        </div>
        <div class="row">
          <label for="form-widgets-year">Year</label>
          <input type="text" id="form-widgets-year"
                 name="form.widgets.year"
                 class="text-widget required textline-field" value="2005" />
        </div>
        <fieldset>
          <legend>Owner</legend>
          <div class="row">
            <label for="form-widgets-owner-firstName">First Name</label>
            <input type="text" id="form-widgets-owner-firstName"
                   name="form.widgets.owner.firstName"
                   class="text-widget required textline-field"
                   value="Stephan" />
          </div>
          <div class="row">
            <label for="form-widgets-owner-lastName">Last Name</label>
            <input type="text" id="form-widgets-owner-lastName"
                   name="form.widgets.owner.lastName"
                   class="text-widget required textline-field"
                   value="Richter" />
          </div>
        </fieldset>
        <div class="action">
          <input type="submit" id="form-buttons-apply"
                 name="form.buttons.apply"
                 class="submit-widget button-field" value="Apply" />
        </div>
      </form>
    </body>
  </html>

Now let's try and edit the owner.  For example, suppose that Stephan
Richter gave his BMW to Paul Carduner because he is such a nice guy.

  >>> request = testing.TestRequest(form={
  ...     'form.widgets.owner.firstName': u'Paul',
  ...     'form.widgets.owner.lastName': u'Carduner',
  ...     'form.widgets.license': u'MA 4038765',
  ...     'form.widgets.address': u'Berkeley',
  ...     'form.widgets.model': u'BMW',
  ...     'form.widgets.make': u'325',
  ...     'form.widgets.year': u'2005',
  ...     'form.buttons.apply': u'Apply'
  ...     })
  >>> edit = RegistrationEditForm(reg, request)
  >>> edit.update()

We'll see if everything worked on the form side.

  >>> print(testing.render(edit, './/xmlns:i'))  # doctest: +NOPARSE_MARKUP
  <i >Data successfully updated.</i>
  ...

Now the owner object should have updated fields.

  >>> reg.owner.firstName
  u'Paul'
  >>> reg.owner.lastName
  u'Carduner'
  >>> reg.license
  u'MA 4038765'
  >>> reg.address
  u'Berkeley'
  >>> reg.model
  u'BMW'
  >>> reg.make
  u'325'
  >>> reg.year
  u'2005'


Nested Groups
-------------

The group can contains groups. Let's adapt the previous RegistrationEditForm:

  >>> class OwnerGroup(group.Group):
  ...     label = u'Owner'
  ...     fields = field.Fields(IVehicleOwner, prefix='owner')
  ...
  ...     def getContent(self):
  ...         return self.context.owner

  >>> class VehicleRegistrationGroup(group.Group):
  ...     label = u'Registration'
  ...     fields = field.Fields(IVehicleRegistration).omit(
  ...         'owner')
  ...     groups = (OwnerGroup,)
  ...
  ...     template = ViewPageTemplateFile(
  ...         'simple_groupedit.pt', os.path.dirname(tests.__file__))

  >>> class RegistrationEditForm(group.GroupForm, form.EditForm):
  ...     groups = (VehicleRegistrationGroup,)
  ...
  ...     template = ViewPageTemplateFile(
  ...         'simple_nested_groupedit.pt', os.path.dirname(tests.__file__))

  >>> reg = VehicleRegistration(
  ...               license=u'MA 40387',
  ...               address=u'10 Main St, Maynard, MA',
  ...               model=u'BMW',
  ...               make=u'325',
  ...               year=u'2005',
  ...               owner=VehicleOwner(firstName=u'Stephan',
  ...                                  lastName=u'Richter'))
  >>> request = testing.TestRequest()

  >>> edit = RegistrationEditForm(reg, request)
  >>> edit.update()

Now let's try and edit the owner.  For example, suppose that Stephan
Richter gave his BMW to Paul Carduner because he is such a nice guy.

  >>> request = testing.TestRequest(form={
  ...     'form.widgets.owner.firstName': u'Paul',
  ...     'form.widgets.owner.lastName': u'Carduner',
  ...     'form.widgets.license': u'MA 4038765',
  ...     'form.widgets.address': u'Berkeley',
  ...     'form.widgets.model': u'BMW',
  ...     'form.widgets.make': u'325',
  ...     'form.widgets.year': u'2005',
  ...     'form.buttons.apply': u'Apply'
  ...     })
  >>> edit = RegistrationEditForm(reg, request)
  >>> edit.update()

We'll see if everything worked on the form side.

  >>> print(testing.render(edit, './/xmlns:i'))  # doctest: +NOPARSE_MARKUP
  <i >Data successfully updated.</i>
  ...

Now the owner object should have updated fields.

  >>> reg.owner.firstName
  u'Paul'
  >>> reg.owner.lastName
  u'Carduner'
  >>> reg.license
  u'MA 4038765'
  >>> reg.address
  u'Berkeley'
  >>> reg.model
  u'BMW'
  >>> reg.make
  u'325'
  >>> reg.year
  u'2005'

So what happens, if errors happen inside a nested group? Let's use an empty
invalid object for the test missing input errors:

  >>> reg = VehicleRegistration(owner=VehicleOwner())

  >>> request = testing.TestRequest(form={
  ...     'form.widgets.owner.firstName': u'',
  ...     'form.widgets.owner.lastName': u'',
  ...     'form.widgets.license': u'',
  ...     'form.widgets.address': u'',
  ...     'form.widgets.model': u'',
  ...     'form.widgets.make': u'',
  ...     'form.widgets.year': u'',
  ...     'form.buttons.apply': u'Apply'
  ...     })

  >>> edit = RegistrationEditForm(reg, request)
  >>> edit.update()
  >>> data, errors = edit.extractData()
  >>> print(testing.render(edit, './/xmlns:i'))  # doctest: +NOPARSE_MARKUP
  <i >There were some errors.</i>
  ...

  >>> print(testing.render(edit, './/xmlns:fieldset/xmlns:ul'))  # doctest: +NOPARSE_MARKUP
  <ul >
    <li>
    License:
      <div class="error">Required input is missing.</div>
    </li>
    <li>
    Address:
      <div class="error">Required input is missing.</div>
    </li>
    <li>
    Model:
      <div class="error">Required input is missing.</div>
    </li>
    <li>
    Make:
      <div class="error">Required input is missing.</div>
    </li>
    <li>
    Year:
      <div class="error">Required input is missing.</div>
    </li>
  </ul>
  ...
  <ul >
    <li>
    First Name:
      <div class="error">Required input is missing.</div>
    </li>
    <li>
    Last Name:
      <div class="error">Required input is missing.</div>
    </li>
  </ul>
  ...

Group instance in nested group
------------------------------

Let's also test if the Group class can handle group objects as instances:

  >>> reg = VehicleRegistration(
  ...               license=u'MA 40387',
  ...               address=u'10 Main St, Maynard, MA',
  ...               model=u'BMW',
  ...               make=u'325',
  ...               year=u'2005',
  ...               owner=VehicleOwner(firstName=u'Stephan',
  ...                                  lastName=u'Richter'))
  >>> request = testing.TestRequest()

  >>> edit = RegistrationEditForm(reg, request)
  >>> vrg = VehicleRegistrationGroup(edit.context, request, edit)
  >>> ownerGroup = OwnerGroup(edit.context, request, edit)

Now build the group instance object chain:

  >>> vrg.groups = (ownerGroup,)
  >>> edit.groups = (vrg,)

Also use refreshActions which is not needed but will make coverage this
additional line of code in the update method:

  >>> edit.refreshActions = True

Update and render:

  >>> edit.update()
  >>> print(edit.render())
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <form action=".">
        <fieldset>
          <legend>Registration</legend>
        <div class="row">
          <label for="form-widgets-license">License</label>
          <input id="form-widgets-license"
                 name="form.widgets.license"
                 class="text-widget required textline-field"
                 value="MA 40387" type="text" />
        </div>
        <div class="row">
          <label for="form-widgets-address">Address</label>
          <input id="form-widgets-address"
                 name="form.widgets.address"
                 class="text-widget required textline-field"
                 value="10 Main St, Maynard, MA" type="text" />
        </div>
        <div class="row">
          <label for="form-widgets-model">Model</label>
          <input id="form-widgets-model" name="form.widgets.model"
                 class="text-widget required textline-field"
                 value="BMW" type="text" />
        </div>
        <div class="row">
          <label for="form-widgets-make">Make</label>
          <input id="form-widgets-make" name="form.widgets.make"
                 class="text-widget required textline-field"
                 value="325" type="text" />
        </div>
        <div class="row">
          <label for="form-widgets-year">Year</label>
          <input id="form-widgets-year" name="form.widgets.year"
                 class="text-widget required textline-field"
                 value="2005" type="text" />
        </div>
          <fieldset>
          <legend>Owner</legend>
        <div class="row">
          <label for="form-widgets-owner-firstName">First Name</label>
          <input id="form-widgets-owner-firstName"
                 name="form.widgets.owner.firstName"
                 class="text-widget required textline-field"
                 value="Stephan" type="text" />
        </div>
        <div class="row">
          <label for="form-widgets-owner-lastName">Last Name</label>
          <input id="form-widgets-owner-lastName"
                 name="form.widgets.owner.lastName"
                 class="text-widget required textline-field"
                 value="Richter" type="text" />
        </div>
        </fieldset>
        </fieldset>
        <div class="action">
          <input id="form-buttons-apply" name="form.buttons.apply"
                 class="submit-widget button-field" value="Apply"
                 type="submit" />
          </div>
      </form>
    </body>
  </html>


Now test the error handling if just one missing value is given in a group:

  >>> request = testing.TestRequest(form={
  ...     'form.widgets.owner.firstName': u'Paul',
  ...     'form.widgets.owner.lastName': u'',
  ...     'form.widgets.license': u'MA 4038765',
  ...     'form.widgets.address': u'Berkeley',
  ...     'form.widgets.model': u'BMW',
  ...     'form.widgets.make': u'325',
  ...     'form.widgets.year': u'2005',
  ...     'form.buttons.apply': u'Apply'
  ...     })

  >>> edit = RegistrationEditForm(reg, request)
  >>> vrg = VehicleRegistrationGroup(edit.context, request, edit)
  >>> ownerGroup = OwnerGroup(edit.context, request, edit)
  >>> vrg.groups = (ownerGroup,)
  >>> edit.groups = (vrg,)

  >>> edit.update()
  >>> data, errors = edit.extractData()
  >>> print(testing.render(edit, './/xmlns:i'))  # doctest: +NOPARSE_MARKUP
  <i >There were some errors.</i>
  ...

  >>> print(testing.render(edit, './/xmlns:fieldset/xmlns:ul'))  # doctest: +NOPARSE_MARKUP
  <ul >
    <li>
    Last Name:
      <div class="error">Required input is missing.</div>
    </li>
  </ul>
  ...

Just check whether we fully support the interface:

  >>> from z3c.form import interfaces
  >>> from zope.interface.verify import verifyClass
  >>> verifyClass(interfaces.IGroup, group.Group)
  True
