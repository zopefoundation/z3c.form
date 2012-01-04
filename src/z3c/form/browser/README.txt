===============
Browser support
===============

The ``z3c.form`` library provides a form framework and widgets. This document
ensures that we implement a widget for each field defined in
``zope.schema``. Take a look at the different widget doctest files for more
information about the widgets.

  >>> import zope.schema
  >>> from z3c.form import browser

Let's setup all required adapters using zcml. This makes sure we test the real
configuration.

  >>> from zope.configuration import xmlconfig
  >>> import zope.component
  >>> import zope.app.component
  >>> import zope.i18n
  >>> import z3c.form
  >>> xmlconfig.XMLConfig('meta.zcml', zope.component)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.app.component)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.i18n)()
  >>> xmlconfig.XMLConfig('meta.zcml', z3c.form)()
  >>> xmlconfig.XMLConfig('configure.zcml', z3c.form)()

This utility is setup by hand, since its ZCML loads to many unwanted files:

  >>> import zope.component
  >>> import zope.i18n.negotiator
  >>> zope.component.provideUtility(zope.i18n.negotiator.negotiator)

also define a helper method for test the widgets:

  >>> from z3c.form import interfaces
  >>> from z3c.form.testing import TestRequest
  >>> def setupWidget(field):
  ...     request = TestRequest()
  ...     widget = zope.component.getMultiAdapter((field, request),
  ...         interfaces.IFieldWidget)
  ...     widget.id = 'foo'
  ...     widget.name = 'bar'
  ...     return widget


ASCII
-----

  >>> field = zope.schema.ASCII(default='This is\n ASCII.')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.textarea.TextAreaWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from ASCII to TextAreaWidget>

  >>> print widget.render()
  <textarea id="foo" name="bar" class="textarea-widget required ascii-field">This is
   ASCII.</textarea>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textarea-widget required ascii-field">This is
   ASCII.</span>


ASCIILine
---------

  >>> field = zope.schema.ASCIILine(default='An ASCII line.')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from ASCIILine to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar"
         class="text-widget required asciiline-field" value="An ASCII line." />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required asciiline-field">An ASCII line.</span>

Bool
----

  >>> field = zope.schema.Bool(default=True, title=u"Check me")
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.radio.RadioWidget'>

  >>> interfaces.IDataConverter(widget)
  <SequenceDataConverter converts from Bool to RadioWidget>

  >>> print widget.render()
  <span class="option">
    <label for="foo-0">
      <input type="radio" id="foo-0" name="bar"
             class="radio-widget required bool-field" value="true"
             checked="checked" />
      <span class="label">yes</span>
    </label>
  </span><span class="option">
    <label for="foo-1">
      <input type="radio" id="foo-1" name="bar"
             class="radio-widget required bool-field" value="false" />
      <span class="label">no</span>
    </label>
  </span>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="radio-widget required bool-field"><span
      class="selected-option">yes</span></span>

For the boolean, the checkbox widget can be used as well:

  >>> from z3c.form.browser import checkbox
  >>> widget = checkbox.CheckBoxFieldWidget(field, TestRequest())
  >>> widget.id = 'foo'
  >>> widget.name = 'bar'
  >>> widget.update()

  >>> print widget.render()
  <span class="option">
    <input type="checkbox" id="foo-0" name="bar:list"
           class="checkbox-widget required bool-field" value="true"
           checked="checked" />
    <label for="foo-0">
      <span class="label">yes</span>
    </label>
  </span><span class="option">
    <input type="checkbox" id="foo-1" name="bar:list"
           class="checkbox-widget required bool-field" value="false" />
    <label for="foo-1">
      <span class="label">no</span>
    </label>
  </span>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="checkbox-widget required bool-field"><span
      class="selected-option">yes</span></span>

We can also have a single checkbox button for the boolean.

  >>> widget = checkbox.SingleCheckBoxFieldWidget(field, TestRequest())
  >>> widget.id = 'foo'
  >>> widget.name = 'bar'
  >>> widget.update()

  >>> print widget.render()
  <span class="option">
    <input type="checkbox" id="foo-0" name="bar:list"
           class="single-checkbox-widget required bool-field"
           value="selected" checked="checked" />
    <label for="foo-0">
      <span class="label">Check me</span>
    </label>
  </span>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo"
        class="single-checkbox-widget required bool-field"><span
      class="selected-option">Check me</span></span>

Note that the widget label is not repeated twice:

  >>> widget.label
  u''


Button
------

  >>> from z3c.form import button
  >>> field = button.Button(title=u'Press me!')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.submit.SubmitWidget'>

  >>> print widget.render()
  <input type="submit" id="foo" name="bar"
         class="submit-widget button-field" value="Press me!" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <input type="submit" id="foo" name="bar"
         class="submit-widget button-field" value="Press me!"
         disabled="disabled" />

There exists an alternative widget for the button field, the button widget. It
is not used by default, but available for use:

  >>> from z3c.form.browser.button import ButtonFieldWidget
  >>> widget = ButtonFieldWidget(field, TestRequest())
  >>> widget.id = "foo"
  >>> widget.name = "bar"

  >>> widget.update()
  >>> print widget.render()
  <input type="button" id="foo" name="bar"
         class="button-widget button-field" value="Press me!" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <input type="button" id="foo" name="bar"
         class="button-widget button-field" value="Press me!"
         disabled="disabled" />


Bytes
-----

  >>> field = zope.schema.Bytes(default='Default bytes')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.file.FileWidget'>

  >>> interfaces.IDataConverter(widget)
  <FileUploadDataConverter converts from Bytes to FileWidget>

  >>> print widget.render()
  <input type="file" id="foo" name="bar" class="file-widget required bytes-field" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> widget.render().strip('\n')
  u'<span id="foo" class="file-widget required bytes-field">Default bytes</span>'


BytesLine
---------

  >>> field = zope.schema.BytesLine(default='A Bytes line.')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from BytesLine to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required bytesline-field"
         value="A Bytes line." />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required bytesline-field">A Bytes line.</span>


Choice
------

  >>> from zope.schema import vocabulary
  >>> terms = [vocabulary.SimpleTerm(*value) for value in
  ...          [(True, 'yes', 'Yes'), (False, 'no', 'No')]]
  >>> vocabulary = vocabulary.SimpleVocabulary(terms)
  >>> field = zope.schema.Choice(default=True, vocabulary=vocabulary)
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.select.SelectWidget'>

  >>> interfaces.IDataConverter(widget)
  <SequenceDataConverter converts from Choice to SelectWidget>

  >>> print widget.render()
  <select id="foo" name="bar:list" class="select-widget required choice-field"
          size="1">
    <option id="foo-0" value="yes" selected="selected">Yes</option>
    <option id="foo-1" value="no">No</option>
  </select>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="select-widget required choice-field"><span
    class="selected-option">Yes</span></span>


Date
----

  >>> import datetime
  >>> field = zope.schema.Date(default=datetime.date(2007, 4, 1))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <DateDataConverter converts from Date to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required date-field"
         value="07/04/01" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required date-field">07/04/01</span>


Datetime
--------

  >>> field = zope.schema.Datetime(default=datetime.datetime(2007, 4, 1, 12))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <DatetimeDataConverter converts from Datetime to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required datetime-field"
         value="07/04/01 12:00" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required datetime-field">07/04/01 12:00</span>


Decimal
-------

  >>> import decimal
  >>> field = zope.schema.Decimal(default=decimal.Decimal('1265.87'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <DecimalDataConverter converts from Decimal to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required decimal-field"
         value="1,265.87" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required decimal-field">1,265.87</span>


Dict
----

There is no default widget for this field, since the sematics are fairly
complex.


DottedName
----------

  >>> field = zope.schema.DottedName(default='z3c.form')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from DottedName to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required dottedname-field"
         value="z3c.form" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required dottedname-field">z3c.form</span>


Float
-----

  >>> field = zope.schema.Float(default=1265.8)
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FloatDataConverter converts from Float to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required float-field"
         value="1,265.8" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required float-field">1,265.8</span>


FrozenSet
---------

  >>> field = zope.schema.FrozenSet(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=frozenset([1, 3]) )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.select.SelectWidget'>

  >>> interfaces.IDataConverter(widget)
  <CollectionSequenceDataConverter converts from FrozenSet to SelectWidget>

  >>> print widget.render()
  <select id="foo" name="bar:list" class="select-widget required frozenset-field"
          multiple="multiple" size="5">
    <option id="foo-0" value="1" selected="selected">1</option>
    <option id="foo-1" value="2">2</option>
    <option id="foo-2" value="3" selected="selected">3</option>
    <option id="foo-3" value="4">4</option>
  </select>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="select-widget required frozenset-field"><span
    class="selected-option">1</span>, <span
    class="selected-option">3</span></span>


Id
--

  >>> field = zope.schema.Id(default='z3c.form')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from Id to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required id-field"
         value="z3c.form" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required id-field">z3c.form</span>


ImageButton
-----------

Let's say we have a simple image field that uses the ``pressme.png`` image.

  >>> from z3c.form import button
  >>> field = button.ImageButton(
  ...     image=u'pressme.png',
  ...     title=u'Press me!')

When the widget is created, the system converts the relative image path to an
absolute image path by looking up the resource. For this to work, we have to
setup some of the traversing machinery:

  # Traversing setup
  >>> from zope.traversing import testing
  >>> testing.setUp()

  # Resource namespace
  >>> import zope.component
  >>> from zope.traversing.interfaces import ITraversable
  >>> from zope.traversing.namespace import resource
  >>> zope.component.provideAdapter(
  ...     resource, (None,), ITraversable, name="resource")
  >>> zope.component.provideAdapter(
  ...     resource, (None, None), ITraversable, name="resource")

  # New absolute URL adapter for resources, if available
  >>> import zope.app.publisher.browser.resource
  >>> if hasattr(zope.app.publisher.browser.resource, 'AbsoluteURL'):
  ...     zope.component.provideAdapter(
  ...         zope.app.publisher.browser.resource.AbsoluteURL)

  # Register the "pressme.png" resource
  >>> from zope.app.publisher.browser.resource import Resource
  >>> testing.browserResource('pressme.png', Resource)

Now we are ready to instantiate the widget:

  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.image.ImageWidget'>

  >>> print widget.render()
  <input type="image" id="foo" name="bar"
         class="image-widget imagebutton-field"
         src="http://127.0.0.1/@@/pressme.png"
         value="Press me!" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <input type="image" id="foo" name="bar"
         class="image-widget imagebutton-field"
         src="http://127.0.0.1/@@/pressme.png"
         value="Press me!" disabled="disabled" />


Int
---

  >>> field = zope.schema.Int(default=1200)
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <IntegerDataConverter converts from Int to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required int-field"
         value="1,200" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required int-field">1,200</span>


List - ASCII
------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.ASCII(
  ...         title=u'ASCII',
  ...         default='This is\n ASCII.'),
  ...     default=['foo\nfoo', 'bar\nbar'])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>ASCII</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-0" name="bar.0"
                 class="textarea-widget required ascii-field">foo
  foo</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>ASCII</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-1" name="bar.1"
                 class="textarea-widget required ascii-field">bar
  bar</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - ASCIILine
----------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.ASCIILine(
  ...         title=u'ASCIILine',
  ...         default='An ASCII line.'),
  ...     default=['foo', 'bar'])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>ASCIILine</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required asciiline-field"
                 value="foo" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>ASCIILine</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required asciiline-field"
                 value="bar" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Choice
-------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=[1, 3] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.orderedselect.OrderedSelectWidget'>

  >>> interfaces.IDataConverter(widget)
  <CollectionSequenceDataConverter converts from List to OrderedSelectWidget>

  >>> print widget.render()
  <script type="text/javascript">
  ...
  </script>
  <table border="0" class="ordered-selection-field">
    <tr>
      <td>
        <select id="foo-from" name="bar.from" size="5"
                multiple="multiple"
                class="required list-field">
          <option value="2">2</option>
          <option value="4">4</option>
        </select>
      </td>
      <td>
        <button name="from2toButton" type="button"
                value="&rarr;"
                onclick="javascript:from2to('foo')">&rarr;</button>
        <br />
        <button name="to2fromButton" type="button"
                value="&larr;"
                onclick="javascript:to2from('foo')">&larr;</button>
      </td>
      <td>
        <select id="foo-to" name="bar.to" size="5"
                multiple="multiple" class="required list-field">
          <option value="1">1</option>
          <option value="3">3</option>
        </select>
        <input name="bar-empty-marker" type="hidden" />
        <span id="foo-toDataContainer">
          <script type="text/javascript">
            copyDataForSubmit('foo');</script>
        </span>
      </td>
      <td>
        <button name="upButton" type="button" value="&uarr;"
                onclick="javascript:moveUp('foo')">&uarr;</button>
        <br />
        <button name="downButton" type="button" value="&darr;"
                onclick="javascript:moveDown('foo')">&darr;</button>
      </td>
    </tr>
  </table>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="required list-field"><span
      class="selected-option">1</span>, <span
      class="selected-option">3</span></span>


List - Date
-----------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Date(
  ...         title=u'Date',
  ...         default=datetime.date(2007, 4, 1)),
  ...     default=[datetime.date(2008, 9, 27), datetime.date(2008, 9, 28)])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Date</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required date-field"
                 value="08/09/27" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Date</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required date-field"
                 value="08/09/28" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Datetime
---------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Datetime(
  ...         title=u'Datetime',
  ...         default=datetime.datetime(2007, 4, 1, 12)),
  ...     default=[datetime.datetime(2008, 9, 27, 12),
  ...              datetime.datetime(2008, 9, 28, 12)])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Datetime</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required datetime-field"
                 value="08/09/27 12:00" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Datetime</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required datetime-field"
                 value="08/09/28 12:00" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Decimal
---------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Decimal(
  ...         title=u'Decimal',
  ...         default=decimal.Decimal('1265.87')),
  ...     default=[decimal.Decimal('123.456'), decimal.Decimal('1')])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Decimal</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required decimal-field"
                 value="123.456" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Decimal</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required decimal-field" value="1" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - DottedName
-----------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.DottedName(
  ...         title=u'DottedName',
  ...         default='z3c.form'),
  ...     default=[u'z3c.form', u'z3c.wizard'])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>DottedName</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required dottedname-field"
                 value="z3c.form" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>DottedName</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required dottedname-field"
                 value="z3c.wizard" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Float
------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Float(
  ...         title=u'Float',
  ...         default=123.456),
  ...     default=[1234.5, 1])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Float</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required float-field"
                 value="1,234.5" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Float</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required float-field" value="1.0" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Id
---------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Id(
  ...         title=u'Id',
  ...         default='z3c.form'),
  ...     default=['z3c.form', 'z3c.wizard'])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Id</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required id-field"
                 value="z3c.form" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Id</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required id-field"
                 value="z3c.wizard" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Int
----------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Int(
  ...         title=u'Int',
  ...         default=666),
  ...     default=[42, 43])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Int</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Int</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required int-field" value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Password
---------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Password(
  ...         title=u'Password',
  ...         default=u'mypwd'),
  ...     default=['pwd', 'pass'])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Password</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="password" id="foo-0" name="bar.0"
                 class="password-widget required password-field" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Password</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="password" id="foo-1" name="bar.1"
                 class="password-widget required password-field" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - SourceText
-----------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.SourceText(
  ...         title=u'SourceText',
  ...         default=u'<source />'),
  ...     default=[u'<html></body>foo</body></html>', u'<h1>bar</h1>'] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>SourceText</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-0" name="bar.0"
                 class="textarea-widget required sourcetext-field">&lt;html&gt;&lt;/body&gt;foo&lt;/body&gt;&lt;/html&gt;</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>SourceText</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-1" name="bar.1"
                 class="textarea-widget required sourcetext-field">&lt;h1&gt;bar&lt;/h1&gt;</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Text
-----------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Text(
  ...         title=u'Text',
  ...         default=u'Some\n Text.'),
  ...     default=[u'foo\nfoo', u'bar\nbar'] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Text</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-0" name="bar.0"
            class="textarea-widget required text-field">foo
  foo</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Text</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-1" name="bar.1"
            class="textarea-widget required text-field">bar
  bar</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - TextLine
---------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.TextLine(
  ...         title=u'TextLine',
  ...         default=u'Some Text line.'),
  ...     default=[u'foo', u'bar'] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>TextLine</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required textline-field"
                 value="foo" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>TextLine</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required textline-field"
                 value="bar" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Time
-----------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Time(
  ...         title=u'Time',
  ...         default=datetime.time(12, 0)),
  ...     default=[datetime.time(13, 0), datetime.time(14, 0)] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Time</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required time-field" value="13:00" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Time</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required time-field" value="14:00" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Timedelta
----------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Timedelta(
  ...         title=u'Timedelta',
  ...         default=datetime.timedelta(days=3)),
  ...     default=[datetime.timedelta(days=4), datetime.timedelta(days=5)] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Timedelta</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required timedelta-field"
                 value="4 days, 0:00:00" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Timedelta</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required timedelta-field"
                 value="5 days, 0:00:00" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - URI
----------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.URI(
  ...         title=u'URI',
  ...         default='http://zope.org'),
  ...     default=['http://www.python.org', 'http://www.zope.com'] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>URI</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required uri-field"
                 value="http://www.python.org" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>URI</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required uri-field"
                 value="http://www.zope.com" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Object
------

By default, we are not going to provide widgets for an object, since we
believe this is better done using sub-forms.


Password
--------

  >>> field = zope.schema.Password(default=u'mypwd')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.password.PasswordWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from Password to PasswordWidget>

  >>> print widget.render()
  <input type="password" id="foo" name="bar"
         class="password-widget required password-field" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="password-widget required password-field">mypwd</span>


Set
---

  >>> field = zope.schema.Set(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=set([1, 3]) )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.select.SelectWidget'>

  >>> interfaces.IDataConverter(widget)
  <CollectionSequenceDataConverter converts from Set to SelectWidget>

  >>> print widget.render()
  <select id="foo" name="bar:list" class="select-widget required set-field"
          multiple="multiple"  size="5">
    <option id="foo-0" value="1" selected="selected">1</option>
    <option id="foo-1" value="2">2</option>
    <option id="foo-2" value="3" selected="selected">3</option>
    <option id="foo-3" value="4">4</option>
  </select>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="select-widget required set-field"><span
      class="selected-option">1</span>, <span
      class="selected-option">3</span></span>


SourceText
----------

  >>> field = zope.schema.SourceText(default=u'<source />')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.textarea.TextAreaWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from SourceText to TextAreaWidget>

  >>> print widget.render()
  <textarea id="foo" name="bar"
            class="textarea-widget required sourcetext-field">&lt;source /&gt;</textarea>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textarea-widget required sourcetext-field">&lt;source /&gt;</span>


Text
----

  >>> field = zope.schema.Text(default=u'Some\n Text.')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.textarea.TextAreaWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from Text to TextAreaWidget>

  >>> print widget.render()
  <textarea id="foo" name="bar" class="textarea-widget required text-field">Some
   Text.</textarea>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textarea-widget required text-field">Some
    Text.</span>


TextLine
--------

  >>> field = zope.schema.TextLine(default=u'Some Text line.')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from TextLine to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required textline-field"
         value="Some Text line." />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required textline-field">Some Text line.</span>


Time
----

  >>> field = zope.schema.Time(default=datetime.time(12, 0))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <TimeDataConverter converts from Time to TextWidget>


  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required time-field"
         value="12:00" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required time-field">12:00</span>


Timedelta
---------

  >>> field = zope.schema.Timedelta(default=datetime.timedelta(days=3))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <TimedeltaDataConverter converts from Timedelta to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required timedelta-field"
         value="3 days, 0:00:00" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required timedelta-field">3 days, 0:00:00</span>


Tuple - ASCII
-------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.ASCII(
  ...         title=u'ASCII',
  ...         default='This is\n ASCII.'),
  ...     default=('foo\nfoo', 'bar\nbar'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>ASCII</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-0" name="bar.0"
                 class="textarea-widget required ascii-field">foo
  foo</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>ASCII</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-1" name="bar.1"
                 class="textarea-widget required ascii-field">bar
  bar</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - ASCIILine
-----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.ASCIILine(
  ...         title=u'ASCIILine',
  ...         default='An ASCII line.'),
  ...     default=('foo', 'bar'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>ASCIILine</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required asciiline-field"
                 value="foo" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>ASCIILine</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required asciiline-field"
                 value="bar" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Choice
--------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=(1, 3) )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.orderedselect.OrderedSelectWidget'>

  >>> interfaces.IDataConverter(widget)
  <CollectionSequenceDataConverter converts from Tuple to OrderedSelectWidget>

  >>> print widget.render()
  <script type="text/javascript">
  ...
  </script>
  <table border="0" class="ordered-selection-field">
    <tr>
      <td>
        <select id="foo-from" name="bar.from" size="5"
                multiple="multiple"
                class="required tuple-field">
          <option value="2">2</option>
          <option value="4">4</option>
        </select>
      </td>
      <td>
        <button name="from2toButton" type="button"
                value="&rarr;"
                onclick="javascript:from2to('foo')">&rarr;</button>
        <br />
        <button name="to2fromButton" type="button"
                value="&larr;"
                onclick="javascript:to2from('foo')">&larr;</button>
      </td>
      <td>
        <select id="foo-to" name="bar.to" size="5"
                multiple="multiple" class="required tuple-field">
          <option value="1">1</option>
          <option value="3">3</option>
        </select>
        <input name="bar-empty-marker" type="hidden" />
        <span id="foo-toDataContainer">
          <script type="text/javascript">
            copyDataForSubmit('foo');</script>
        </span>
      </td>
      <td>
        <button name="upButton" type="button" value="&uarr;"
                onclick="javascript:moveUp('foo')">&uarr;</button>
        <br />
        <button name="downButton" type="button" value="&darr;"
                onclick="javascript:moveDown('foo')">&darr;</button>
      </td>
    </tr>
  </table>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="required tuple-field"><span
    class="selected-option">1</span>, <span
    class="selected-option">3</span></span>


Tuple - Date
------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Date(
  ...         title=u'Date',
  ...         default=datetime.date(2007, 4, 1)),
  ...     default=(datetime.date(2008, 9, 27), datetime.date(2008, 9, 28)))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Date</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required date-field"
                 value="08/09/27" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Date</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required date-field"
                 value="08/09/28" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Datetime
----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Datetime(
  ...         title=u'Datetime',
  ...         default=datetime.datetime(2007, 4, 1, 12)),
  ...     default=(datetime.datetime(2008, 9, 27, 12),
  ...              datetime.datetime(2008, 9, 28, 12)))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Datetime</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required datetime-field"
                 value="08/09/27 12:00" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Datetime</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required datetime-field"
                 value="08/09/28 12:00" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Decimal
----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Decimal(
  ...         title=u'Decimal',
  ...         default=decimal.Decimal('1265.87')),
  ...     default=(decimal.Decimal('123.456'), decimal.Decimal('1')))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Decimal</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required decimal-field"
                 value="123.456" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Decimal</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required decimal-field" value="1" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - DottedName
------------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.DottedName(
  ...         title=u'DottedName',
  ...         default='z3c.form'),
  ...     default=(u'z3c.form', u'z3c.wizard'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>DottedName</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required dottedname-field"
                 value="z3c.form" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>DottedName</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required dottedname-field"
                 value="z3c.wizard" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Float
-------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Float(
  ...         title=u'Float',
  ...         default=123.456),
  ...     default=(1234.5, 1))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Float</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required float-field"
                 value="1,234.5" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Float</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required float-field" value="1.0" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Id
----------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Id(
  ...         title=u'Id',
  ...         default='z3c.form'),
  ...     default=('z3c.form', 'z3c.wizard'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Id</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required id-field"
                 value="z3c.form" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Id</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required id-field"
                 value="z3c.wizard" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Int
-----------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Int(
  ...         title=u'Int',
  ...         default=666),
  ...     default=(42, 43))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Int</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Int</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required int-field" value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Password
----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Password(
  ...         title=u'Password',
  ...         default=u'mypwd'),
  ...     default=('pwd', 'pass'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Password</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="password" id="foo-0" name="bar.0"
                 class="password-widget required password-field" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Password</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="password" id="foo-1" name="bar.1"
                 class="password-widget required password-field" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - SourceText
------------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.SourceText(
  ...         title=u'SourceText',
  ...         default=u'<source />'),
  ...     default=(u'<html></body>foo</body></html>', u'<h1>bar</h1>'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>SourceText</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-0" name="bar.0"
                 class="textarea-widget required sourcetext-field">&lt;html&gt;&lt;/body&gt;foo&lt;/body&gt;&lt;/html&gt;</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>SourceText</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-1" name="bar.1"
                 class="textarea-widget required sourcetext-field">&lt;h1&gt;bar&lt;/h1&gt;</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Text
------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Text(
  ...         title=u'Text',
  ...         default=u'Some\n Text.'),
  ...     default=(u'foo\nfoo', u'bar\nbar'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Text</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-0" name="bar.0"
            class="textarea-widget required text-field">foo
  foo</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Text</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><textarea id="foo-1" name="bar.1"
            class="textarea-widget required text-field">bar
  bar</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - TextLine
----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.TextLine(
  ...         title=u'TextLine',
  ...         default=u'Some Text line.'),
  ...     default=(u'foo', u'bar'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>TextLine</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required textline-field"
                 value="foo" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>TextLine</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required textline-field"
                 value="bar" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Time
------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Time(
  ...         title=u'Time',
  ...         default=datetime.time(12, 0)),
  ...     default=(datetime.time(13, 0), datetime.time(14, 0)))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Time</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required time-field" value="13:00" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Time</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required time-field" value="14:00" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Timedelta
-----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Timedelta(
  ...         title=u'Timedelta',
  ...         default=datetime.timedelta(days=3)),
  ...     default=(datetime.timedelta(days=4), datetime.timedelta(days=5)))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>Timedelta</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required timedelta-field"
                 value="4 days, 0:00:00" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>Timedelta</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required timedelta-field"
                 value="5 days, 0:00:00" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - URI
-----------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.URI(
  ...         title=u'URI',
  ...         default='http://zope.org'),
  ...     default=('http://www.python.org', 'http://www.zope.com'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print widget.render()
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>URI</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-0-remove" name="bar.0.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-0" name="bar.0"
                 class="text-widget required uri-field"
                 value="http://www.python.org" />
          </div>
        </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>URI</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="foo-1-remove" name="bar.1.remove" />
            </div>
            <div class="multi-widget-input"><input type="text" id="foo-1" name="bar.1"
                 class="text-widget required uri-field"
                 value="http://www.zope.com" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


URI
---

  >>> field = zope.schema.URI(default='http://zope.org')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'z3c.form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from URI to TextWidget>

  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="text-widget required uri-field"
         value="http://zope.org" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="text-widget required uri-field">http://zope.org</span>
