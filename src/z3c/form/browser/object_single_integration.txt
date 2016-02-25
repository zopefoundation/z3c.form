=====================================
ObjectWidget single integration tests
=====================================

Checking components on the highest possible level.

  >>> from datetime import date
  >>> from z3c.form import form
  >>> from z3c.form import field
  >>> from z3c.form import testing

  >>> from z3c.form.object import registerFactoryAdapter
  >>> registerFactoryAdapter(testing.IObjectWidgetSingleSubIntegration,
  ...     testing.ObjectWidgetSingleSubIntegration)

  >>> request = testing.TestRequest()

  >> from z3c.form.object import registerFactoryAdapter
  >> registerFactoryAdapter(testing.IObjectWidgetSingleSubIntegration,
  ..     testing.ObjectWidgetSingleSubIntegration)


  >>> class EForm(form.EditForm):
  ...     form.extends(form.EditForm)
  ...     fields = field.Fields(testing.IObjectWidgetSingleIntegration)

Our single content object:

  >>> obj = testing.ObjectWidgetSingleIntegration()

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

  >>> content = getForm(request, 'ObjectWidget_single_edit_empty.html')

  >>> print(testing.plainText(content))
  Object label
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
  ReadOnly label *
  []
  [Apply]

Some valid default values
--------------------------

  >>> obj.subobj = testing.ObjectWidgetSingleSubIntegration(
  ...     singleInt=-100,
  ...     singleBool=False,
  ...     singleChoice='two',
  ...     singleChoiceOpt='six',
  ...     singleTextLine=u'some text one',
  ...     singleDate=date(2014, 6, 20),
  ...     singleReadOnly=u'some R/O text')

  >>> content = getForm(request, 'ObjectWidget_single_edit_simple.html')

  >>> print(testing.plainText(content))
  Object label
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
  ReadOnly label *
  some R/O text
  [Apply]


Wrong values
-------------

Set wrong values:

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.subobj.widgets.singleInt'] = u'foobar'
  >>> submit['form.widgets.subobj.widgets.singleTextLine'] = u'foo\nbar'
  >>> submit['form.widgets.subobj.widgets.singleDate'] = u'foobar'

  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(form=submit)

We should get lots of errors:

  >>> content = getForm(request, 'ObjectWidget_single_edit_submit_wrong.html')
  >>> print(testing.plainText(content,
  ...     './/ul[@id="form-errors"]'))
  * Object label: The entered value is not a valid integer literal.
  Constraint not satisfied
  The datetime string did not match the pattern 'yy/MM/dd'.

  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-subobj"]/b/div[@class="error"]'))
  The entered value is not a valid integer literal.
  Constraint not satisfied
  The datetime string did not match the pattern 'yy/MM/dd'.

  >>> print(testing.plainText(content,
  ...     './/div[@id="row-form-widgets-subobj"]'))
  The entered value is not a valid integer literal.
  Constraint not satisfied
  The datetime string did not match the pattern u'yy/MM/dd'. Object label
  Int label *
  <BLANKLINE>
  The entered value is not a valid integer literal.
  [foobar]
  <BLANKLINE>
  Bool label *
  <BLANKLINE>
  ( ) yes (O) no
  <BLANKLINE>
  Choice label *
  <BLANKLINE>
  [two]
  <BLANKLINE>
  ChoiceOpt label
  <BLANKLINE>
  [six]
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  Constraint not satisfied
  [foo
  bar]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern u'yy/MM/dd'.
  [foobar]
  <BLANKLINE>
  ReadOnly label *
  <BLANKLINE>
  some R/O text

Let's fix the values:

  >>> submit = testing.getSubmitValues(content)

  >>> submit['form.widgets.subobj.widgets.singleInt'] = u'1042'
  >>> submit['form.widgets.subobj.widgets.singleBool'] = u'true'
  >>> submit['form.widgets.subobj.widgets.singleChoice:list'] = u'three'
  >>> submit['form.widgets.subobj.widgets.singleChoiceOpt:list'] = u'four'
  >>> submit['form.widgets.subobj.widgets.singleTextLine'] = u'foobar'
  >>> submit['form.widgets.subobj.widgets.singleDate'] = u'14/06/21'

  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(form=submit)

  >>> content = getForm(request, 'ObjectWidget_single_edit_submit_fixed.html')
  >>> print(testing.plainText(content))
  Data successfully updated.
  <BLANKLINE>
  Object label
  Int label *
  [1,042]
  Bool label *
  (O) yes ( ) no
  Choice label *
  [three]
  ChoiceOpt label
  [four]
  TextLine label *
  [foobar]
  Date label *
  [14/06/21]
  ReadOnly label *
  some R/O text
  [Apply]


Bool was misbehaving

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.subobj.widgets.singleBool'] = u'false'
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(form=submit)

  >>> content = getForm(request, 'ObjectWidget_single_edit_submit_bool1.html')
  >>> print(testing.plainText(content))
  Data successfully updated.
  ...

  >>> pprint(obj.subobj)
  <ObjectWidgetSingleSubIntegration
    singleBool: False
    singleChoice: 'three'
    singleChoiceOpt: 'four'
    singleDate: datetime.date(2014, 6, 21)
    singleInt: 1042
    singleReadOnly: u'some R/O text'
    singleTextLine: u'foobar'>

  >>> submit = testing.getSubmitValues(content)
  >>> submit['form.widgets.subobj.widgets.singleBool'] = u'true'
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(form=submit)

  >>> content = getForm(request, 'ObjectWidget_single_edit_submit_bool2.html')
  >>> print(testing.plainText(content))
  Data successfully updated.
  ...

  >>> pprint(obj.subobj)
  <ObjectWidgetSingleSubIntegration
    singleBool: True
    singleChoice: 'three'
    singleChoiceOpt: 'four'
    singleDate: datetime.date(2014, 6, 21)
    singleInt: 1042
    singleReadOnly: u'some R/O text'
    singleTextLine: u'foobar'>
