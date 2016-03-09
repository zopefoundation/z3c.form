===================================
MultiWidget Dict integration tests
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
  ...         testing.IMultiWidgetDictIntegration).omit('dictOfObject')

Our single content object:

  >>> obj = testing.MultiWidgetDictIntegration()

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

  >>> content = getForm(request, 'MultiWidget_dict_edit_empty.html')

  >>> print(testing.plainText(content))
  DictOfInt label
  <BLANKLINE>
  [Add]
  DictOfBool label
  <BLANKLINE>
  [Add]
  DictOfChoice label
  <BLANKLINE>
  [Add]
  DictOfTextLine label
  <BLANKLINE>
  [Add]
  DictOfDate label
  <BLANKLINE>
  [Add]
  [Apply]

Some valid default values
--------------------------

  >>> obj.dictOfInt = {-101: -100, -1:1, 101:100}
  >>> obj.dictOfBool = {True: False, False: True}
  >>> obj.dictOfChoice = {'key1': 'three', 'key3': 'two'}
  >>> obj.dictOfTextLine = {u'textkey1': u'some text one',
  ...     u'textkey2': u'some txt two'}
  >>> obj.dictOfDate = {
  ...     date(2011, 1, 15): date(2014, 6, 20),
  ...     date(2012, 2, 20): date(2013, 5, 19)}

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dictOfBool: {False: True, True: False}
    dictOfChoice: {'key1': 'three', 'key3': 'two'}
    dictOfDate: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dictOfInt: {-101: -100, -1: 1, 101: 100}
    dictOfTextLine: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>

  >>> content = getForm(request, 'MultiWidget_dict_edit_simple.html')

  >>> print(testing.plainText(content))
  DictOfInt label
  <BLANKLINE>
  Int key *
  [-1]
  Int label *
  [ ]
  [1]
  Int key *
  [-101]
  Int label *
  [ ]
  [-100]
  Int key *
  [101]
  Int label *
  [ ]
  [100]
  [Add]
  [Remove selected]
  DictOfBool label
  <BLANKLINE>
  Bool key *
  ( ) yes (O) no
  Bool label *
  [ ]
  (O) yes ( ) no
  Bool key *
  (O) yes ( ) no
  Bool label *
  [ ]
  ( ) yes (O) no
  [Add]
  [Remove selected]
  DictOfChoice label
  <BLANKLINE>
  Choice key *
  [key1]
  Choice label *
  [ ]
  [three]
  Choice key *
  [key3]
  Choice label *
  [ ]
  [two]
  [Add]
  [Remove selected]
  DictOfTextLine label
  <BLANKLINE>
  TextLine key *
  [textkey1]
  TextLine label *
  [ ]
  [some text one]
  TextLine key *
  [textkey2]
  TextLine label *
  [ ]
  [some txt two]
  [Add]
  [Remove selected]
  DictOfDate label
  <BLANKLINE>
  Date key *
  [11/01/15]
  Date label *
  [ ]
  [14/06/20]
  Date key *
  [12/02/20]
  Date label *
  [ ]
  [13/05/19]
  [Add]
  [Remove selected]
  [Apply]

dictOfInt
----------

Set a wrong value and add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfInt.key.2'] = u'foobar'
  >>> submit['form.widgets.dictOfInt.2'] = u'foobar'

  >>> submit['form.widgets.dictOfInt.buttons.add'] = u'Add'

  >>> request = testing.TestRequest(form=submit)

Important is that we get "The entered value is not a valid integer literal."
for "foobar" and a new input.

  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_int.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-dictOfInt"]'))
  DictOfInt label
  <BLANKLINE>
  Int key *
  <BLANKLINE>
  [-1]
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  [ ]
  [1]
  Int key *
  <BLANKLINE>
  [-101]
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  [ ]
  [-100]
  Int key *
  <BLANKLINE>
  The entered value is not a valid integer literal.
  [foobar]
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  The entered value is not a valid integer literal.
  [ ]
  [foobar]
  Int key *
  <BLANKLINE>
  []
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  [ ]
  []
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_int2.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-dictOfInt"]//div[@class="error"]'))
  Required input is missing.
  Required input is missing.
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfInt.1.remove'] = u'1'
  >>> submit['form.widgets.dictOfInt.3.remove'] = u'1'
  >>> submit['form.widgets.dictOfInt.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_remove_int.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-dictOfInt"]'))
  DictOfInt label
  <BLANKLINE>
  Int key *
  <BLANKLINE>
  Required input is missing.
  []
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  Int key *
  <BLANKLINE>
  [-101]
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  [ ]
  [-100]
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dictOfBool: {False: True, True: False}
    dictOfChoice: {'key1': 'three', 'key3': 'two'}
    dictOfDate: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dictOfInt: {-101: -100, -1: 1, 101: 100}
    dictOfTextLine: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>


dictOfBool
-----------

Add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfBool.buttons.add'] = u'Add'
  >>> request = testing.TestRequest(form=submit)

Important is that we get a new input.

  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_bool.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-dictOfBool"]'))
  DictOfBool label
  <BLANKLINE>
  Bool key *
  <BLANKLINE>
  ( ) yes (O) no
  <BLANKLINE>
  Bool label *
  <BLANKLINE>
  [ ]
  (O) yes ( ) no
  Bool key *
  <BLANKLINE>
  (O) yes ( ) no
  <BLANKLINE>
  Bool label *
  <BLANKLINE>
  [ ]
  ( ) yes (O) no
  Bool key *
  <BLANKLINE>
  ( ) yes ( ) no
  <BLANKLINE>
  Bool label *
  <BLANKLINE>
  [ ]
  ( ) yes ( ) no
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_bool2.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-dictOfBool"]//div[@class="error"]'))
  Required input is missing.
  Required input is missing.

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfBool.1.remove'] = u'1'
  >>> submit['form.widgets.dictOfBool.2.remove'] = u'1'
  >>> submit['form.widgets.dictOfBool.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_remove_bool.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-dictOfBool"]'))
  DictOfBool label
  <BLANKLINE>
  Bool key *
  <BLANKLINE>
  Required input is missing.
  ( ) yes ( ) no
  <BLANKLINE>
  Bool label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  ( ) yes ( ) no
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dictOfBool: {False: True, True: False}
    dictOfChoice: {'key1': 'three', 'key3': 'two'}
    dictOfDate: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dictOfInt: {-101: -100, -1: 1, 101: 100}
    dictOfTextLine: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>


dictOfChoice
-------------

Add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfChoice.buttons.add'] = u'Add'
  >>> request = testing.TestRequest(form=submit)

Important is that we get a new input.

  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_choice.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-dictOfChoice"]'))
  DictOfChoice label
  <BLANKLINE>
  Choice key *
  <BLANKLINE>
  [key1]
  <BLANKLINE>
  Choice label *
  <BLANKLINE>
  [ ]
  [three]
  Choice key *
  <BLANKLINE>
  [key3]
  <BLANKLINE>
  Choice label *
  <BLANKLINE>
  [ ]
  [two]
  Choice key *
  <BLANKLINE>
  [[    ]]
  <BLANKLINE>
  Choice label *
  <BLANKLINE>
  [ ]
  [[    ]]
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_choice2.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-dictOfChoice"]//div[@class="error"]'))
  Required input is missing.
  Required input is missing.

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfChoice.0.remove'] = u'1'
  >>> submit['form.widgets.dictOfChoice.1.remove'] = u'1'
  >>> submit['form.widgets.dictOfChoice.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_remove_choice.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-dictOfChoice"]'))
  DictOfChoice label
  <BLANKLINE>
  Choice key *
  <BLANKLINE>
  [key3]
  <BLANKLINE>
  Choice label *
  <BLANKLINE>
  [ ]
  [two]
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dictOfBool: {False: True, True: False}
    dictOfChoice: {'key1': 'three', 'key3': 'two'}
    dictOfDate: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dictOfInt: {-101: -100, -1: 1, 101: 100}
    dictOfTextLine: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>


dictOfTextLine
---------------

Set a wrong value and add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfTextLine.key.0'] = u'foo\nbar'
  >>> submit['form.widgets.dictOfTextLine.0'] = u'foo\nbar'

  >>> submit['form.widgets.dictOfTextLine.buttons.add'] = u'Add'

  >>> request = testing.TestRequest(form=submit)

Important is that we get "Constraint not satisfied"
for "foo\nbar" and a new input.

  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_textline.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-dictOfTextLine"]'))
  DictOfTextLine label
  <BLANKLINE>
  TextLine key *
  <BLANKLINE>
  Constraint not satisfied
  [foo
  bar]
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  Constraint not satisfied
  [ ]
  [foo
  bar]
  TextLine key *
  <BLANKLINE>
  [textkey2]
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  [ ]
  [some txt two]
  TextLine key *
  <BLANKLINE>
  []
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  [ ]
  []
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_textline2.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-dictOfTextLine"]//div[@class="error"]'))
  Required input is missing.
  Required input is missing.
  Constraint not satisfied
  Constraint not satisfied

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfTextLine.2.remove'] = u'1'
  >>> submit['form.widgets.dictOfTextLine.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_remove_textline.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-dictOfTextLine"]'))
  DictOfTextLine label
  <BLANKLINE>
  TextLine key *
  <BLANKLINE>
  Required input is missing.
  []
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  TextLine key *
  <BLANKLINE>
  Constraint not satisfied
  [foo
  bar]
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  Constraint not satisfied
  [ ]
  [foo
  bar]
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dictOfBool: {False: True, True: False}
    dictOfChoice: {'key1': 'three', 'key3': 'two'}
    dictOfDate: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dictOfInt: {-101: -100, -1: 1, 101: 100}
    dictOfTextLine: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>


dictOfDate
-----------

Set a wrong value and add a new input:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfDate.key.0'] = u'foobar'
  >>> submit['form.widgets.dictOfDate.0'] = u'foobar'

  >>> submit['form.widgets.dictOfDate.buttons.add'] = u'Add'

  >>> request = testing.TestRequest(form=submit)

Important is that we get "The entered value is not a valid integer literal."
for "foobar" and a new input.

  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_date.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-dictOfDate"]'))
  DictOfDate label
  <BLANKLINE>
  Date key *
  <BLANKLINE>
  [12/02/20]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  [ ]
  [13/05/19]
  Date key *
  <BLANKLINE>
  The datetime string did not match the pattern 'yy/MM/dd'.
  [foobar]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern 'yy/MM/dd'.
  [ ]
  [foobar]
  Date key *
  <BLANKLINE>
  []
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  [ ]
  []
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.getSubmitValues(content)
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_date2.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-dictOfDate"]//div[@class="error"]'))
  Required input is missing.
  Required input is missing.
  The datetime string did not match the pattern 'yy/MM/dd'.
  The datetime string did not match the pattern 'yy/MM/dd'.

And fill in a valid value:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfDate.key.0'] = u'14/05/12'
  >>> submit['form.widgets.dictOfDate.0'] = u'14/06/21'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_submit_date3.html')
  >>> print(testing.plainText(content,
  ...     './/form/div[@id="row-form-widgets-dictOfDate"]'))
  DictOfDate label
  <BLANKLINE>
  Date key *
  <BLANKLINE>
  [12/02/20]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  [ ]
  [13/05/19]
  Date key *
  <BLANKLINE>
  [14/05/12]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  [ ]
  [14/06/21]
  Date key *
  <BLANKLINE>
  The datetime string did not match the pattern 'yy/MM/dd'.
  [foobar]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern 'yy/MM/dd'.
  [ ]
  [foobar]
  [Add]
  [Remove selected]

Let's remove some items:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfDate.1.remove'] = u'1'
  >>> submit['form.widgets.dictOfDate.buttons.remove'] = u'Remove selected'
  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_remove_date.html')
  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-dictOfDate"]'))
  DictOfDate label
  <BLANKLINE>
  Date key *
  <BLANKLINE>
  [12/02/20]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  [ ]
  [13/05/19]
  Date key *
  <BLANKLINE>
  The datetime string did not match the pattern 'yy/MM/dd'.
  [foobar]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern 'yy/MM/dd'.
  [ ]
  [foobar]
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dictOfBool: {False: True, True: False}
    dictOfChoice: {'key1': 'three', 'key3': 'two'}
    dictOfDate: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dictOfInt: {-101: -100, -1: 1, 101: 100}
    dictOfTextLine: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>

And apply

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.buttons.apply'] = u'Apply'

  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)
  >>> print(testing.plainText(content))
  There were some errors.
  * DictOfInt label: Wrong contained type
  * DictOfBool label: Wrong contained type
  * DictOfTextLine label: Constraint not satisfied
  * DictOfDate label: The datetime string did not match the pattern u'yy/MM/dd'.
  ...

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dictOfBool: {False: True, True: False}
    dictOfChoice: {'key1': 'three', 'key3': 'two'}
    dictOfDate: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dictOfInt: {-101: -100, -1: 1, 101: 100}
    dictOfTextLine: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>

Let's fix the values

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfInt.key.1'] = '42'
  >>> submit['form.widgets.dictOfInt.1'] = '43'
  >>> submit['form.widgets.dictOfTextLine.0.remove'] = '1'
  >>> submit['form.widgets.dictOfTextLine.buttons.remove'] = 'Remove selected'

  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request)

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfTextLine.key.0'] = 'lorem ipsum'
  >>> submit['form.widgets.dictOfTextLine.0'] = 'ipsum lorem'
  >>> submit['form.widgets.dictOfDate.key.1'] = '14/06/25'
  >>> submit['form.widgets.dictOfDate.1'] = '14/07/28'
  >>> submit['form.widgets.dictOfInt.key.0'] = u'-101'
  >>> submit['form.widgets.dictOfInt.0'] = u'-100'
  >>> submit['form.widgets.dictOfBool.key.0'] = u'false'
  >>> submit['form.widgets.dictOfBool.0'] = u'true'

  >>> submit['form.buttons.apply'] = u'Apply'

  >>> request = testing.TestRequest(form=submit)
  >>> content = getForm(request, 'MultiWidget_dict_edit_fixit.html')
  >>> print(testing.plainText(content))
  Data successfully updated.
  ...

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dictOfBool: {False: True}
    dictOfChoice: {'key3': 'two'}
    dictOfDate: {datetime.date(2012, 2, 20): datetime.date(2013, 5, 19),
   datetime.date(2014, 6, 25): datetime.date(2014, 7, 28)}
    dictOfInt: {-101: -100, 42: 43}
    dictOfTextLine: {'lorem ipsum': 'ipsum lorem'}>

Twisting some keys
-------------------

Change key values, item values must stick to the new values.

  >>> obj.dictOfInt = {-101: -100, -1:1, 101:100}
  >>> obj.dictOfBool = {True: False, False: True}
  >>> obj.dictOfChoice = {'key1': 'three', 'key3': 'two'}
  >>> obj.dictOfTextLine = {u'textkey1': u'some text one',
  ...     u'textkey2': u'some txt two'}
  >>> obj.dictOfDate = {
  ...     date(2011, 1, 15): date(2014, 6, 20),
  ...     date(2012, 2, 20): date(2013, 5, 19)}

  >>> request = testing.TestRequest()
  >>> content = getForm(request, 'MultiWidget_dict_edit_twist.html')

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.dictOfInt.key.2'] = u'42'  # was 101:100
  >>> submit['form.widgets.dictOfBool.key.0'] = u'true'  # was False:True
  >>> submit['form.widgets.dictOfBool.key.1'] = u'false'  # was True:False
  >>> submit['form.widgets.dictOfChoice.key.1:list'] = u'key2'  # was key3: two
  >>> submit['form.widgets.dictOfChoice.key.0:list'] = u'key3'  # was key1: three
  >>> submit['form.widgets.dictOfTextLine.key.1'] = u'lorem'  # was textkey2: some txt two
  >>> submit['form.widgets.dictOfTextLine.1'] = u'ipsum'  # was textkey2: some txt two
  >>> submit['form.widgets.dictOfTextLine.key.0'] = u'foobar'  # was textkey1: some txt one
  >>> submit['form.widgets.dictOfDate.key.0'] = u'14/06/25'  # 11/01/15: 14/06/20

  >>> submit['form.buttons.apply'] = u'Apply'

  >>> request = testing.TestRequest(form=submit)

  >>> content = getForm(request, 'MultiWidget_dict_edit_twist2.html')

  >>> submit = testing.getSubmitValues(content)

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dictOfBool: {False: False, True: True}
    dictOfChoice: {'key2': 'two', 'key3': 'three'}
    dictOfDate: {datetime.date(2012, 2, 20): datetime.date(2013, 5, 19),
   datetime.date(2014, 6, 25): datetime.date(2014, 6, 20)}
    dictOfInt: {-101: -100, -1: 1, 42: 100}
    dictOfTextLine: {'foobar': 'some text one', 'lorem': 'ipsum'}>
