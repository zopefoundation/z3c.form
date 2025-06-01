Text Widget
-----------

The widget can render a input field for a text line:

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form import interfaces
  >>> from z3c.form.browser import text

The TextWidget is a widget:

 >>> verifyClass(interfaces.IWidget, text.TextWidget)
  True

The widget can render a input field only by adapting a request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = text.TextWidget(request)

Such a field provides IWidget:

 >>> interfaces.IWidget.providedBy(widget)
  True

We also need to register the template for at least the widget and request:

  >>> import os.path
  >>> import zope.interface
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> import z3c.form.browser
  >>> import z3c.form.widget
  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'text_input.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='input')

If we render the widget we get the HTML:

  >>> print(widget.render())
  <input type="text" class="text-widget" value="" />

Adding some more attributes to the widget will make it display more:

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.value = u'value'
  >>> widget.style = u'color: blue'
  >>> widget.placeholder = u'Email address'
  >>> widget.autocapitalize = u'off'

  >>> print(widget.render())
  <input type="text" id="id" name="name" class="text-widget"
         placeholder="Email address" autocapitalize="off"
         style="color: blue" value="value" />


Check DISPLAY_MODE:

  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'text_display.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='display')

  >>> widget.value = u'foobar'
  >>> widget.style = None
  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="id" class="text-widget">foobar</span>

Check HIDDEN_MODE:

  >>> template = os.path.join(os.path.dirname(z3c.form.browser.__file__),
  ...     'text_hidden.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='hidden')

  >>> widget.value = u'foobar'
  >>> widget.mode = interfaces.HIDDEN_MODE
  >>> print(widget.render())
  <input id="id" name="name" value="foobar" class="hidden-widget" type="hidden" />


Number widgets - Integer
------------------------

Let's create a new widget for integer fields

  >>> integer_widget = text.TextWidget(request)
  >>> integer_widget.name = 'integer-name'
  >>> integer_widget.field = zope.schema.Int()

  >>> print(integer_widget.render())
  <input
      class="text-widget"
      name="integer-name"
      step="1"
      type="number"
      value=""
      >

  >>> float_widget = text.TextWidget(request)
  >>> float_widget.name = 'float-name'
  >>> float_widget.field = zope.schema.Float()

  >>> print(float_widget.render())
  <input
      class="text-widget"
      name="float-name"
      step="any"
      type="number"
      value=""
      >

  >>> decimal_widget = text.TextWidget(request)
  >>> decimal_widget.name = 'decimal-name'
  >>> decimal_widget.field = zope.schema.Float()

  >>> print(decimal_widget.render())
  <input
      class="text-widget"
      name="decimal-name"
      step="any"
      type="number"
      value=""
      >
