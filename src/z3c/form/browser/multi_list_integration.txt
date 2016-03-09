===================================
MultiWidget List integration tests
===================================

Checking components on the highest possible level.

  >>> from datetime import date
  >>> from z3c.form import form
  >>> from z3c.form import field
  >>> from z3c.form import testing

  >>> request = testing.TestRequest()

  >>> class EForm(form.EditForm):
  ...     form.extends(form.EditForm)
  ...     fields = field.Fields(
  ...         testing.IMultiWidgetListIntegration).omit(
  ...             'listOfChoice', 'listOfObject')

Our single content object:

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

  >>> content = getForm(request, 'MultiWidget_list_edit_empty.html')

  >>> print(testing.plainText(content))
  ListOfInt label
  <BLANKLINE>
  [Add]
  ListOfBool label
  <BLANKLINE>
  [Add]
  ListOfTextLine label
  <BLANKLINE>
  [Add]
  ListOfDate label
  <BLANKLINE>
  [Add]
  [Apply]

Some valid default values
--------------------------

  >>> obj.listOfInt = [-100, 1, 100]
  >>> obj.listOfBool = [True, False, True]
  >>> obj.listOfChoice = ['two', 'three']
  >>> obj.listOfTextLine = [u'some text one', u'some txt two']
  >>> obj.listOfDate = [date(2014, 6, 20)]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    listOfBool: [True, False, True]
    listOfChoice: ['two', 'three']
    listOfDate: [datetime.date(2014, 6, 20)]
    listOfInt: [-100, 1, 100]
    listOfTextLine: [u'some text one', u'some txt two']>

  >>> content = getForm(request, 'MultiWidget_list_edit_simple.html')

  >>> print(testing.plainText(content))
  ListOfInt label
  <BLANKLINE>
  Int label *
  [ ]
  [-100]
  Int label *
  [ ]
  [1]
  Int label *
  [ ]
  [100]
  [Add]
  [Remove selected]
  ListOfBool label
  <BLANKLINE>
  Bool label *
  [ ]
  (O) yes ( ) no
  Bool label *
  [ ]
  ( ) yes (O) no
  Bool label *
  [ ]
  (O) yes ( ) no
  [Add]
  [Remove selected]
  ListOfTextLine label
  <BLANKLINE>
  TextLine label *
  [ ]
  [some text one]
  TextLine label *
  [ ]
  [some txt two]
  [Add]
  [Remove selected]
  ListOfDate label
  <BLANKLINE>
  Date label *
  [ ]
  [14/06/20]
  [Add]
  [Remove selected]
  [Apply]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    listOfBool: [True, False, True]
    listOfChoice: ['two', 'three']
    listOfDate: [datetime.date(2014, 6, 20)]
    listOfInt: [-100, 1, 100]
    listOfTextLine: [u'some text one', u'some txt two']>

listOfInt
----------

Set a wrong value and add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfInt.1'] = u'foobar'

  >>> submit['form.widgets.listOfInt.buttons.add'] = u'Add'

  >>> request = testing.TestRequest(form=submit)

Important is that we get "The entered value is not a valid integer literal."
for "foobar" and a new input.

  >>> content = getForm(request, 'MultiWidget_list_edit_submit_int.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-listOfInt"]'))
  ListOfInt label
  <BLANKLINE>
  Int label *
  [ ]
  [-100]
  Int label *
  The entered value is not a valid integer literal.
  [ ]
  [foobar]
  Int label *
  [ ]
  [100]
  Int label *
  [ ]
  []
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-listOfInt"]//div[@class="error"]'))
  The entered value is not a valid integer literal.
  Required input is missing.

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfInt.1.remove'] = u'1'
  >>> submit['form.widgets.listOfInt.2.remove'] = u'1'
  >>> submit['form.widgets.listOfInt.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_list_edit_remove_int.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-listOfInt"]'))
  ListOfInt label
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  [ ]
  [-100]
  Int label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    listOfBool: [True, False, True]
    listOfChoice: ['two', 'three']
    listOfDate: [datetime.date(2014, 6, 20)]
    listOfInt: [-100, 1, 100]
    listOfTextLine: [u'some text one', u'some txt two']>


listOfBool
-----------

Add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfBool.buttons.add'] = u'Add'
  >>> request = testing.TestRequest(form=submit)

Important is that we get a new input.

  >>> content = getForm(request, 'MultiWidget_list_edit_submit_bool.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-listOfBool"]'))
  ListOfBool label
  <BLANKLINE>
  Bool label *
  <BLANKLINE>
  [ ]
  (O) yes ( ) no
  Bool label *
  <BLANKLINE>
  [ ]
  ( ) yes (O) no
  Bool label *
  <BLANKLINE>
  [ ]
  (O) yes ( ) no
  Bool label *
  <BLANKLINE>
  [ ]
  ( ) yes ( ) no
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-listOfBool"]//div[@class="error"]'))
  Required input is missing.

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfBool.1.remove'] = u'1'
  >>> submit['form.widgets.listOfBool.2.remove'] = u'1'
  >>> submit['form.widgets.listOfBool.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_list_edit_remove_bool.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-listOfBool"]'))
  ListOfBool label
  <BLANKLINE>
  Bool label *
  <BLANKLINE>
  [ ]
  (O) yes ( ) no
  Bool label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  ( ) yes ( ) no
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    listOfBool: [True, False, True]
    listOfChoice: ['two', 'three']
    listOfDate: [datetime.date(2014, 6, 20)]
    listOfInt: [-100, 1, 100]
    listOfTextLine: [u'some text one', u'some txt two']>


listOfTextLine
---------------

Set a wrong value and add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfTextLine.1'] = u'foo\nbar'

  >>> submit['form.widgets.listOfTextLine.buttons.add'] = u'Add'

  >>> request = testing.TestRequest(form=submit)

Important is that we get "Constraint not satisfied"
for "foo\nbar" and a new input.

  >>> content = getForm(request, 'MultiWidget_list_edit_submit_textline.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-listOfTextLine"]'))
  ListOfTextLine label
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  [ ]
  [some text one]
  TextLine label *
  <BLANKLINE>
  Constraint not satisfied
  [ ]
  [foo
  bar]
  TextLine label *
  <BLANKLINE>
  [ ]
  []
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-listOfTextLine"]//div[@class="error"]'))
  Constraint not satisfied
  Required input is missing.

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfTextLine.0.remove'] = u'1'
  >>> submit['form.widgets.listOfTextLine.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_list_edit_remove_textline.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-listOfTextLine"]'))
  ListOfTextLine label
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  Constraint not satisfied
  [ ]
  [foo
  bar]
  TextLine label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    listOfBool: [True, False, True]
    listOfChoice: ['two', 'three']
    listOfDate: [datetime.date(2014, 6, 20)]
    listOfInt: [-100, 1, 100]
    listOfTextLine: [u'some text one', u'some txt two']>


listOfDate
-----------

Set a wrong value and add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfDate.0'] = u'foobar'

  >>> submit['form.widgets.listOfDate.buttons.add'] = u'Add'

  >>> request = testing.TestRequest(form=submit)

Important is that we get "The datetime string did not match the pattern"
for "foobar" and a new input.

  >>> content = getForm(request, 'MultiWidget_list_edit_submit_date.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-listOfDate"]'))
  ListOfDate label
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern u'yy/MM/dd'.
  [ ]
  [foobar]
  Date label *
  <BLANKLINE>
  [ ]
  []
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-listOfDate"]//div[@class="error"]'))
  The datetime string did not match the pattern u'yy/MM/dd'.
  Required input is missing.

Add one more field:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfDate.buttons.add'] = u'Add'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)

And fill in a valid value:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfDate.2'] = u'14/06/21'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_list_edit_submit_date2.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-listOfDate"]'))
  ListOfDate label
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern u'yy/MM/dd'.
  [ ]
  [foobar]
  Date label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  Date label *
  <BLANKLINE>
  [ ]
  [14/06/21]
  [Add]
  [Remove selected]

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfDate.2.remove'] = u'1'
  >>> submit['form.widgets.listOfDate.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_list_edit_remove_date.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-listOfDate"]'))
  ListOfDate label
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern u'yy/MM/dd'.
  [ ]
  [foobar]
  Date label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    listOfBool: [True, False, True]
    listOfChoice: ['two', 'three']
    listOfDate: [datetime.date(2014, 6, 20)]
    listOfInt: [-100, 1, 100]
    listOfTextLine: [u'some text one', u'some txt two']>


And apply

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.buttons.apply'] = u'Apply'

  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content))
  There were some errors.
  * ListOfInt label: Wrong contained type
  * ListOfBool label: Wrong contained type
  * ListOfTextLine label: Constraint not satisfied
  * ListOfDate label: The datetime string did not match the pattern 'yy/MM/dd'.
  ...

  >>> pprint(obj)
  <MultiWidgetListIntegration
    listOfBool: [True, False, True]
    listOfChoice: ['two', 'three']
    listOfDate: [datetime.date(2014, 6, 20)]
    listOfInt: [-100, 1, 100]
    listOfTextLine: [u'some text one', u'some txt two']>

Let's fix the values

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.listOfInt.1'] = '42'
  >>> submit['form.widgets.listOfBool.1'] = 'false'
  >>> submit['form.widgets.listOfTextLine.0'] = 'ipsum lorem'
  >>> submit['form.widgets.listOfTextLine.1'] = 'lorem ipsum'
  >>> submit['form.widgets.listOfDate.0'] = '14/06/25'
  >>> submit['form.widgets.listOfDate.1'] = '14/06/24'
  >>> submit['form.buttons.apply'] = u'Apply'

  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content))
  Data successfully updated.
  ...

  >>> pprint(obj)
  <MultiWidgetListIntegration
    listOfBool: [True, False]
    listOfChoice: ['two', 'three']
    listOfDate: [datetime.date(2014, 6, 25), datetime.date(2014, 6, 24)]
    listOfInt: [-100, 42]
    listOfTextLine: [u'ipsum lorem', u'lorem ipsum']>
