File Widget
-----------

The file widget allows you to upload a new file to the server. The "file" type
of the "INPUT" element is described here:

http://www.w3.org/TR/1999/REC-html401-19991224/interact/forms.html#edef-INPUT

As for all widgets, the file widget must provide the new ``IWidget``
interface:

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form import interfaces
  >>> from z3c.form.browser import file

  >>> verifyClass(interfaces.IWidget, file.FileWidget)
  True

The widget can be instantiated only using the request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = file.FileWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.name'

We also need to register the template for the widget:

  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form.testing import getPath
  >>> from z3c.form.widget import WidgetTemplateFactory

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('file_input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IFileWidget),
  ...     IPageTemplate, name=interfaces.INPUT_MODE)

If we render the widget we get a simple input element:

  >>> print(widget.render())
  <input type="file" id="widget.id" name="widget.name"
         class="file-widget" />

Let's now make sure that we can extract user entered data from a widget:

  >>> from io import BytesIO
  >>> myfile = BytesIO(b'My file contents.')

  >>> widget.request = TestRequest(form={'widget.name': myfile})
  >>> widget.update()
  >>> isinstance(widget.extract(), BytesIO)
  True

If nothing is found in the request, the default is returned:

  >>> widget.request = TestRequest()
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>

Make also sure that we can handle FileUpload objects given form a file upload.

  >>> from zope.publisher.browser import FileUpload

Let's define a FieldStorage stub:

  >>> class FieldStorageStub:
  ...     def __init__(self, file):
  ...         self.file = file
  ...         self.headers = {}
  ...         self.filename = 'foo.bar'

Now build a FileUpload:

  >>> myfile = BytesIO(b'File upload contents.')
  >>> aFieldStorage = FieldStorageStub(myfile)
  >>> myUpload = FileUpload(aFieldStorage)

  >>> widget.request = TestRequest(form={'widget.name': myUpload})
  >>> widget.update()
  >>> widget.extract()
  <zope.publisher.browser.FileUpload object at ...>

If we render them, we get a regular file upload widget:

  >>> print(widget.render())
  <input type="file" id="widget.id" name="widget.name"
         class="file-widget" />
