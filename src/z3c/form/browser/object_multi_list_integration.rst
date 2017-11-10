=====================================
ObjectWidget multi integration tests
=====================================

a.k.a. list of objects widget

  >>> from datetime import date
  >>> from z3c.form import form
  >>> from z3c.form import field
  >>> from z3c.form import testing

  >>> from z3c.form.object import registerFactoryAdapter
  >>> registerFactoryAdapter(testing.IObjectWidgetMultiSubIntegration,
  ...     testing.ObjectWidgetMultiSubIntegration)

  >>> request = testing.TestRequest()

  >>> class EForm(form.EditForm):
  ...     form.extends(form.EditForm)
  ...     fields = field.Fields(
  ...         testing.IMultiWidgetListIntegration).select('listOfObject')

Our multi content object:

  >>> obj = testing.MultiWidgetListIntegration()

We recreate the form each time, to stay as close as possible.
In real life the form gets instantiated and destroyed with each request.

  >>> def getForm(request, fname=None):
  ...     frm = EForm(obj, request)
  ...     testing.addTemplate(frm, 'integration_edit.pt')
  ...     frm.update()
  ...     content = frm.render()
  ...     if fname is not None:
  ...         testing.saveHtml(content, fname)
  ...     return content

Empty
------

All blank and empty values:

  >>> content = getForm(request, 'ObjectMulti_list_edit_empty.html')

  >>> print(testing.plainText(content))
  ListOfObject label
  <BLANKLINE>
  [Add]
  [Apply]

Some valid default values
--------------------------

  >>> sub1 = testing.ObjectWidgetMultiSubIntegration(
  ...     multiInt=-100,
  ...     multiBool=False,
  ...     multiChoice='two',
  ...     multiChoiceOpt='six',
  ...     multiTextLine=u'some text one',
  ...     multiDate=date(2014, 6, 20))

  >>> sub2 = testing.ObjectWidgetMultiSubIntegration(
  ...     multiInt=42,
  ...     multiBool=True,
  ...     multiChoice='one',
  ...     multiChoiceOpt='four',
  ...     multiTextLine=u'second txt',
  ...     multiDate=date(2011, 3, 15))

  >>> obj.listOfObject = [sub1, sub2]

  >>> pprint(obj.listOfObject)
  [<ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: u'some text one'>,
   <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: u'second txt'>]

  >>> content = getForm(request, 'ObjectMulti_list_edit_simple.html')
  >>> print(testing.plainText(content))
  ListOfObject label
  <BLANKLINE>
  Object label *
  [ ]
  Int label *
  [-100]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [some text one]
  Date label *
  [14/06/20]
  Object label *
  [ ]
  Int label *
  [42]
  Bool label *
  (O) yes ( ) no
  Choice label *
  [one]
  ChoiceOpt label
  [four]
  TextLine label *
  [second txt]
  Date label *
  [11/03/15]
  [Add]
  [Remove selected]
  [Apply]

wrong input (Int)
------------------

Set a wrong value and add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.0.widgets.multiInt'] = u'foobar'

  >>> submit['form.widgets.listOfObject.buttons.add'] = u'Add'

  >>> request = testing.TestRequest(form=submit)

Important is that we get "The entered value is not a valid integer literal."
for "foobar" and a new input.

  >>> content = getForm(request, 'ObjectMulti_list_edit_submit_int.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="form-widgets-listOfObject-0-row"]'))
  Object label *
  <BLANKLINE>
  The entered value is not a valid integer literal.
  <BLANKLINE>
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [some text one]
  Date label *
  [14/06/20]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'ObjectMulti_list_edit_submit_int_again.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="form-widgets-listOfObject-0-row"]//div[@class="error"]'))
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.

  >>> print(testing.plainText(content,
  ...     './/div[@id="form-widgets-listOfObject-1-row"]//div[@class="error"]'))

  >>> print(testing.plainText(content,
  ...     './/div[@id="form-widgets-listOfObject-2-row"]'))
  Object label *
  <BLANKLINE>
  Wrong contained type
  <BLANKLINE>
  [ ]
  Int label *
  Required input is missing.
  []
  Bool label *
  Required input is missing.
  ( ) yes ( ) no
  Choice label *
  Required input is missing.
  [[    ]]
  ChoiceOpt label
  [No value]
  TextLine label *
  Required input is missing.
  []
  Date label *
  Required input is missing.
  []

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.1.remove'] = u'1'
  >>> submit['form.widgets.listOfObject.2.remove'] = u'1'
  >>> submit['form.widgets.listOfObject.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'ObjectMulti_list_edit_remove_int.html')
  >>> print(testing.plainText(content))
  ListOfObject label
  <BLANKLINE>
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [some text one]
  Date label *
  [14/06/20]
  [Add]
  [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.listOfObject)
  [<ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: u'some text one'>,
   <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: u'second txt'>]


wrong input (TextLine)
-----------------------

Set a wrong value and add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.0.widgets.multiTextLine'] = u'foo\nbar'

  >>> submit['form.widgets.listOfObject.buttons.add'] = u'Add'

  >>> request = testing.TestRequest(form=submit)

Important is that we get "Constraint not satisfied"
for "foo\nbar" and a new input.

  >>> content = getForm(request, 'ObjectMulti_list_edit_submit_textline.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="form-widgets-listOfObject-0-row"]'))
  Object label *
  <BLANKLINE>
  The entered value is not a valid integer literal.
  <BLANKLINE>
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  Constraint not satisfied
  [foo
  bar]
  Date label *
  [14/06/20]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'ObjectMulti_list_edit_submit_textline_again.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="form-widgets-listOfObject-0-row"]//div[@class="error"]'))
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.
  Constraint not satisfied

  >>> print(testing.plainText(content,
  ...     './/div[@id="form-widgets-listOfObject-1-row"]//div[@class="error"]'))
  Wrong contained type
  Required input is missing.
  Required input is missing.
  Required input is missing.
  Required input is missing.
  Required input is missing.

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.1.remove'] = u'1'
  >>> submit['form.widgets.listOfObject.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'ObjectMulti_list_edit_remove_textline.html')
  >>> print(testing.plainText(content))
  ListOfObject label
  <BLANKLINE>
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  Constraint not satisfied
  [foo
  bar]
  Date label *
  [14/06/20]
  [Add]
  [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.listOfObject)
  [<ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: u'some text one'>,
   <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: u'second txt'>]


wrong input (Date)
--------------------

Set a wrong value and add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.0.widgets.multiDate'] = u'foobar'

  >>> submit['form.widgets.listOfObject.buttons.add'] = u'Add'

  >>> request = testing.TestRequest(form=submit)

Important is that we get "The datetime string did not match the pattern"
for "foobar" and a new input.

  >>> content = getForm(request, 'ObjectMulti_list_edit_submit_date.html')
  >>> print(testing.plainText(content))
  ListOfObject label
  <BLANKLINE>
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  Constraint not satisfied
  [foo
  bar]
  Date label *
  The datetime string did not match the pattern u'yy/MM/dd'.
  [foobar]
  Object label *
  [ ]
  Int label *
  []
  Bool label *
  ( ) yes ( ) no
  Choice label *
  [[    ]]
  ChoiceOpt label
  [No value]
  TextLine label *
  []
  Date label *
  []
  [Add]
  [Remove selected]
  [Apply]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content,
  ...     './/div[@id="form-widgets-listOfObject-0-row"]//div[@class="error"]'))
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.
  Constraint not satisfied
  The datetime string did not match the pattern 'yy/MM/dd'.

Add one more field:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.buttons.add'] = u'Add'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)

And fill in a valid value:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.2.widgets.multiDate'] = u'14/06/21'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'ObjectMulti_list_edit_submit_date2.html')
  >>> print(testing.plainText(content))
  ListOfObject label
  <BLANKLINE>
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  Constraint not satisfied
  [foo
  bar]
  Date label *
  The datetime string did not match the pattern 'yy/MM/dd'.
  [foobar]
  Object label *
  Wrong contained type
  [ ]
  Int label *
  Required input is missing.
  []
  Bool label *
  Required input is missing.
  ( ) yes ( ) no
  Choice label *
  Required input is missing.
  [[    ]]
  ChoiceOpt label
  [No value]
  TextLine label *
  Required input is missing.
  []
  Date label *
  Required input is missing.
  []
  Object label *
  Wrong contained type
  [ ]
  Int label *
  Required input is missing.
  []
  Bool label *
  Required input is missing.
  ( ) yes ( ) no
  Choice label *
  Required input is missing.
  [[    ]]
  ChoiceOpt label
  [No value]
  TextLine label *
  Required input is missing.
  []
  Date label *
  [14/06/21]
  [Add]
  [Remove selected]
  [Apply]

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.2.remove'] = u'1'
  >>> submit['form.widgets.listOfObject.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'ObjectMulti_list_edit_remove_date.html')
  >>> print(testing.plainText(content))
  ListOfObject label
  <BLANKLINE>
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  Constraint not satisfied
  [foo
  bar]
  Date label *
  The datetime string did not match the pattern 'yy/MM/dd'.
  [foobar]
  Object label *
  Wrong contained type
  [ ]
  Int label *
  Required input is missing.
  []
  Bool label *
  Required input is missing.
  ( ) yes ( ) no
  Choice label *
  Required input is missing.
  [[    ]]
  ChoiceOpt label
  [No value]
  TextLine label *
  Required input is missing.
  []
  Date label *
  Required input is missing.
  []
  [Add]
  [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.listOfObject)
  [<ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: u'some text one'>,
   <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: u'second txt'>]

Fix values
-----------

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.0.widgets.multiInt'] = u'1042'
  >>> submit['form.widgets.listOfObject.0.widgets.multiTextLine'] = u'moo900'
  >>> submit['form.widgets.listOfObject.0.widgets.multiDate'] = u'14/06/23'

  >>> submit['form.widgets.listOfObject.1.remove'] = u'1'
  >>> submit['form.widgets.listOfObject.buttons.remove'] = u'Remove selected'

  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'ObjectMulti_list_edit_fix_values.html')
  >>> print(testing.plainText(content))
  ListOfObject label
  <BLANKLINE>
  Object label *
  [ ]
  Int label *
  [1,042]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [moo900]
  Date label *
  [14/06/23]
  [Add]
  [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.listOfObject)
  [<ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: u'some text one'>,
   <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: u'second txt'>]

And apply

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.buttons.apply'] = u'Apply'

  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content))
  Data successfully updated.
  <BLANKLINE>
  ListOfObject label
  <BLANKLINE>
  Object label *
  [ ]
  Int label *
  [1,042]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [moo900]
  Date label *
  [14/06/23]
  [Add]
  [Remove selected]
  [Apply]

Now the object gets updated:

  >>> pprint(obj.listOfObject)
  [<ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 23)
    multiInt: 1042
    multiTextLine: u'moo900'>]


Bool was misbehaving
---------------------

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.0.widgets.multiBool'] = u'true'
  >>> submit['form.buttons.apply'] = u'Apply'

  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content))
  Data successfully updated.
  ...

  >>> pprint(obj.listOfObject)
  [<ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 23)
    multiInt: 1042
    multiTextLine: u'moo900'>]


  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfObject.0.widgets.multiBool'] = u'false'
  >>> submit['form.buttons.apply'] = u'Apply'

  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content))
  Data successfully updated.
  ...

  >>> pprint(obj.listOfObject)
  [<ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 23)
    multiInt: 1042
    multiTextLine: u'moo900'>]
