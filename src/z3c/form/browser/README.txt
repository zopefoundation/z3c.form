======
README
======

The z3c.form library provides a form framework and widgets. This document
should make sure that we implement a widget for each field defined in
zope.schema. Take a look at the different widget doctest for more information
about the widgets.

  >>> import zope.schema
  >>> from z3c.form import browser

Let's setup all required adapters using zcml. This makes sure we test the real
configuration.

  >>> from zope.configuration import xmlconfig
  >>> import zope.component
  >>> import z3c.form
  >>> xmlconfig.XMLConfig('meta.zcml', zope.component)()
  >>> xmlconfig.XMLConfig('meta.zcml', z3c.form)()
  >>> xmlconfig.XMLConfig('configure.zcml', z3c.form)()

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
  >>> print widget.render()
  <textarea id="foo" name="bar" class="textAreaWidget ascii-field">This is
   ASCII.</textarea>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textAreaWidget ascii-field">
    This is
   ASCII.
  </span>


ASCIILine
---------

  >>> field = zope.schema.ASCIILine(default='An ASCII line.')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget asciiline-field"
         value="An ASCII line." />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget asciiline-field">
    An ASCII line.
  </span>

Bool
----

  >>> field = zope.schema.Bool(default=True)
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <span class="option">
    <input type="radio" id="foo-0" name="bar:list"
           class="radioWidget bool-field" value="yes" checked="checked" />
    <label for="foo-0">
      <span class="label">yes</span>
    </label>
  </span><span class="option">
    <input type="radio" id="foo-1" name="bar:list"
           class="radioWidget bool-field" value="no" />
    <label for="foo-1">
      <span class="label">no</span>
    </label>
  </span>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="radioWidget bool-field">
    <span class="selected-option">yes</span>
  </span>

For the boolean, the checkbox widget can be used as well:

  >>> from z3c.form.browser import checkbox
  >>> widget = checkbox.CheckBoxFieldWidget(field, TestRequest())
  >>> widget.id = 'foo'
  >>> widget.name = 'bar'
  >>> widget.update()

  >>> print widget.render()
  <span class="option">
    <input type="checkbox" id="foo-0" name="bar:list"
           class="checkBoxWidget bool-field" value="yes"
           checked="checked" />
    <label for="foo-0">
      <span class="label">yes</span>
    </label>
  </span><span class="option">
    <input type="checkbox" id="foo-1" name="bar:list"
           class="checkBoxWidget bool-field" value="no" />
    <label for="foo-1">
      <span class="label">no</span>
    </label>
  </span>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="checkBoxWidget bool-field">
    <span class="selected-option">yes</span>
  </span>


Button
------

  >>> from z3c.form import button
  >>> field = button.Button(title=u'Press me!')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="submit" id="foo" name="bar"
         class="submitWidget button-field" value="Press me!" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <input type="submit" id="foo" name="bar"
         class="submitWidget button-field" value="Press me!"
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
         class="buttonWidget button-field" value="Press me!" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <input type="button" id="foo" name="bar"
         class="buttonWidget button-field" value="Press me!"
         disabled="disabled" />



Bytes
-----

  >>> field = zope.schema.Bytes(default='\10\45\n\32')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="file" id="foo" name="bar" class="fileWidget bytes-field" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> widget.render()
  u'<span id="foo" class="fileWidget bytes-field">\n  \x08%\n\x1a\n</span>\n'


BytesLine
---------

  >>> field = zope.schema.BytesLine(default='A Bytes line.')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget bytesline-field"
         value="A Bytes line." />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget bytesline-field">
    A Bytes line.
  </span>


Choice
------

  >>> from zope.schema import vocabulary
  >>> terms = [vocabulary.SimpleTerm(*value) for value in
  ...          [(True, 'yes', 'Yes'), (False, 'no', 'No')]]
  >>> vocabulary = vocabulary.SimpleVocabulary(terms)
  >>> field = zope.schema.Choice(default=True, vocabulary=vocabulary)
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <select id="foo" name="bar:list" class="selectWidget choice-field"
          size="1">
    <option id="foo-0" value="yes" selected="selected">Yes</option>
    <option id="foo-1" value="no">No</option>
  </select>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="selectWidget choice-field">
    <span class="selected-option">Yes</span>
  </span>

Date
----

  >>> import datetime
  >>> field = zope.schema.Date(default=datetime.date(2007, 4, 1))
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget date-field"
         value="07/04/01" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget date-field">
    07/04/01
  </span>


Datetime
--------

  >>> field = zope.schema.Datetime(default=datetime.datetime(2007, 4, 1, 12))
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget datetime-field"
         value="07/04/01 12:00" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget datetime-field">
    07/04/01 12:00
  </span>


Decimal
-------

  >>> import decimal
  >>> field = zope.schema.Decimal(default=decimal.Decimal('1265.87'))
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget decimal-field"
         value="1,265.87" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget decimal-field">
    1,265.87
  </span>


Dict
----

There is no default widget for this field, since the sematics are fairly
complex.


DottedName
----------

  >>> field = zope.schema.DottedName(default='z3c.form')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget dottedname-field"
         value="z3c.form" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget dottedname-field">
    z3c.form
  </span>


Float
-----

  >>> field = zope.schema.Float(default=1265.8)
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget float-field"
         value="1,265.8" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget float-field">
    1,265.8
  </span>


FrozenSet
---------

  >>> field = zope.schema.FrozenSet(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=frozenset([1, 3]) )
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <select id="foo" name="bar:list" class="selectWidget frozenset-field"
          multiple="multiple" size="5">
    <option id="foo-0" value="1" selected="selected">1</option>
    <option id="foo-1" value="2">2</option>
    <option id="foo-2" value="3" selected="selected">3</option>
    <option id="foo-3" value="4">4</option>
  </select>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="selectWidget frozenset-field">
    <span class="selected-option">1</span>,
    <span class="selected-option">3</span>
  </span>


Id
--

  >>> field = zope.schema.Id(default='z3c.form')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget id-field"
         value="z3c.form" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget id-field">
    z3c.form
  </span>


Int
---

  >>> field = zope.schema.Int(default=1200)
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget int-field"
         value="1,200" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget int-field">
    1,200
  </span>


List
----

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=[1, 3] )
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <script type="text/javascript">
  ...
  </script>
  <BLANKLINE>
  <table border="0" class="ordered-selection-field">
    <tr>
      <td>
        <select id="foo-from" name="bar.from" size="5"
                multiple="multiple" class="list-field">
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4</option>
        </select>
      </td>
      <td>
        <button name="from2toButton" type="button"
                value=" -&gt;"
                onclick="javascript:from2to('foo')">&nbsp;-&gt;</button>
        <br />
        <button name="to2fromButton" type="button"
                value="&lt;- "
                onclick="javascript:to2from('foo')">&lt;-&nbsp;</button>
      </td>
      <td>
        <select id="foo-to" name="bar.to" size="5"
                multiple="multiple" class="list-field">
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
        <button name="upButton" type="button" value="^"
                onclick="javascript:moveUp('foo')">^</button>
        <br />
        <button name="downButton" type="button" value="v"
                onclick="javascript:moveDown('foo')">v</button>
      </td>
    </tr>
  </table>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="list-field">
    <span class="selected-option">1</span>,
    <span class="selected-option">3</span>
  </span>


Object
------

By default, we are not going to provide widgets for an object, since we
believe this is better done using sub-forms.


Password
--------

  >>> field = zope.schema.Password(default=u'mypwd')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="password" id="foo" name="bar"
         class="passwordWidget password-field" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="passwordWidget password-field">
    mypwd
  </span>


Set
---

  >>> field = zope.schema.Set(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=set([1, 3]) )
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <select id="foo" name="bar:list" class="selectWidget set-field"
          multiple="multiple"  size="5">
    <option id="foo-0" value="1" selected="selected">1</option>
    <option id="foo-1" value="2">2</option>
    <option id="foo-2" value="3" selected="selected">3</option>
    <option id="foo-3" value="4">4</option>
  </select>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="selectWidget set-field">
    <span class="selected-option">1</span>,
    <span class="selected-option">3</span>
  </span>


SourceText
----------

  >>> field = zope.schema.SourceText(default=u'<source />')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <textarea id="foo" name="bar"
            class="textAreaWidget sourcetext-field">&lt;source /&gt;</textarea>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textAreaWidget sourcetext-field">
    &lt;source /&gt;
  </span>


Text
----

  >>> field = zope.schema.Text(default=u'Some\n Text.')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <textarea id="foo" name="bar" class="textAreaWidget text-field">Some
   Text.</textarea>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textAreaWidget text-field">
    Some
    Text.
  </span>


TextLine
--------

  >>> field = zope.schema.TextLine(default=u'Some Text line.')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget textline-field"
         value="Some Text line." />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget textline-field">
    Some Text line.
  </span>


Time
----

  >>> field = zope.schema.Time(default=datetime.time(12, 0))
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget time-field"
         value="12:00" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget time-field">
    12:00
  </span>


Timedelta
---------

  >>> field = zope.schema.Timedelta(default=datetime.timedelta(days=3))
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget timedelta-field"
         value="3 days, 0:00:00" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget timedelta-field">
    3 days, 0:00:00
  </span>


Tuple
-----

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=(1, 3) )
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <script type="text/javascript">
  ...
  </script>
  <BLANKLINE>
  <table border="0" class="ordered-selection-field">
    <tr>
      <td>
        <select id="foo-from" name="bar.from" size="5"
                multiple="multiple" class="tuple-field">
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4</option>
        </select>
      </td>
      <td>
        <button name="from2toButton" type="button"
                value=" -&gt;"
                onclick="javascript:from2to('foo')">&nbsp;-&gt;</button>
        <br />
        <button name="to2fromButton" type="button"
                value="&lt;- "
                onclick="javascript:to2from('foo')">&lt;-&nbsp;</button>
      </td>
      <td>
        <select id="foo-to" name="bar.to" size="5"
                multiple="multiple" class="tuple-field">
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
        <button name="upButton" type="button" value="^"
                onclick="javascript:moveUp('foo')">^</button>
        <br />
        <button name="downButton" type="button" value="v"
                onclick="javascript:moveDown('foo')">v</button>
      </td>
    </tr>
  </table>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="tuple-field">
    <span class="selected-option">1</span>,
    <span class="selected-option">3</span>
  </span>


URI
---

  >>> field = zope.schema.URI(default='http://zope.org')
  >>> widget = setupWidget(field)
  >>> widget.update()
  >>> print widget.render()
  <input type="text" id="foo" name="bar" class="textWidget uri-field"
         value="http://zope.org" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print widget.render()
  <span id="foo" class="textWidget uri-field">
    http://zope.org
  </span>
