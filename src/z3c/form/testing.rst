===============
Testing support
===============

Data Converter for Testing
--------------------------

Sometimes, we want to upload binary files. Particulary in Selenium
tests, it is nearly impossible to correctly input binary data - so we
allow the user to specify `base64` encoded data to be uploaded. This
is accomplished by using a hidden input field that holds the value
of the encoding desired.

  >>> import zope.schema
  >>> from z3c.form import widget
  >>> from z3c.form import testing

As in converter.rst, we want to test a file upload widget.

  >>> filedata = zope.schema.Text(
  ...     __name__='data',
  ...     title=u'Some data to upload',)

Lets try passing a simple string, and not specify any encoding.

  >>> dataWidget = widget.Widget(testing.TestRequest(
  ...    form={'data.testing': 'haha'}))
  >>> dataWidget.name = 'data'

  >>> conv = testing.TestingFileUploadDataConverter(filedata, dataWidget)
  >>> conv.toFieldValue('')
  b'haha'

And now, specify a encoded string

  >>> import base64
  >>> encStr = base64.b64encode(b'hoohoo')
  >>> dataWidget = widget.Widget(testing.TestRequest(
  ...    form={'data.testing': encStr, 'data.encoding': 'base64'}))
  >>> dataWidget.name = 'data'

  >>> conv = testing.TestingFileUploadDataConverter(filedata, dataWidget)
  >>> conv.toFieldValue('')
  b'hoohoo'
