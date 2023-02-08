Multi Widget
------------

The multi widget allows you to add and edit one or more values.

As for all widgets, the multi widget must provide the new ``IWidget``
interface:

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form import interfaces
  >>> from z3c.form.browser import multi

  >>> verifyClass(interfaces.IWidget, multi.MultiWidget)
  True

The widget can be instantiated only using the request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

We also need to register the template for at least the widget and request:

  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form.testing import getPath
  >>> from z3c.form.widget import WidgetTemplateFactory

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('multi_input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IMultiWidget),
  ...     IPageTemplate, name=interfaces.INPUT_MODE)

For the next test, we need to setup our button handler adapters.

  >>> from z3c.form import button
  >>> zope.component.provideAdapter(button.ButtonActions)
  >>> zope.component.provideAdapter(button.ButtonActionHandler)
  >>> zope.component.provideAdapter(button.ButtonAction,
  ...     provides=interfaces.IButtonAction)

Our submit buttons will need a template as well:

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('submit_input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.ISubmitWidget),
  ...     IPageTemplate, name=interfaces.INPUT_MODE)

We can now render the widget:

  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget">
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="0" />

As you can see the widget is empty and doesn't provide values. This is because
the widget does not know what sub-widgets to display. So let's register a
`IFieldWidget` adapter and a template for our `IInt` field:

  >>> import z3c.form.interfaces
  >>> from z3c.form.browser.text import TextFieldWidget
  >>> zope.component.provideAdapter(TextFieldWidget,
  ...     (zope.schema.interfaces.IInt, z3c.form.interfaces.IFormLayer))

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('text_input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.ITextWidget),
  ...     IPageTemplate, name=interfaces.INPUT_MODE)

Let's now update the widget and check it again.

  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget">
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="0" />

It's still the same. Since the widget doesn't provide a field nothing useful
gets rendered. Now let's define a field for this widget and check it again:

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget">
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field" value="Add" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="0" />

As you can see, there is still no input value. Let's provide some values for
this widget. Before we can do that, we will need to register a data converter
for our multi widget and the data converter dispatcher adapter:

  >>> from z3c.form.converter import IntegerDataConverter
  >>> from z3c.form.converter import FieldWidgetDataConverter
  >>> from z3c.form.validator import SimpleFieldValidator
  >>> zope.component.provideAdapter(IntegerDataConverter)
  >>> zope.component.provideAdapter(FieldWidgetDataConverter)
  >>> zope.component.provideAdapter(SimpleFieldValidator)

  >>> widget.value = ['42', '43']
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget">
      <div id="widget-id-0-row" class="row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-0-remove"
                     name="widget.name.0.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-0" name="widget.name.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row" class="row">
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-1-remove"
                     name="widget.name.1.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-1" name="widget.name.1"
                 class="text-widget required int-field" value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

If we now click on the ``Add`` button, we will get a new input field for enter
a new value:

  >>> widget.request = TestRequest(form={'widget.name.count':'2',
  ...                                    'widget.name.0':'42',
  ...                                    'widget.name.1':'43',
  ...                                    'widget.name.buttons.add':'Add'})
  >>> widget.update()

  >>> widget.extract()
  ['42', '43']

  >>> print(widget.render())
  <div class="multi-widget">
      <div id="widget-id-0-row" class="row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-0-remove"
                     name="widget.name.0.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-0" name="widget.name.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row" class="row">
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-1-remove"
                     name="widget.name.1.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-1" name="widget.name.1"
                 class="text-widget required int-field" value="43" />
          </div>
        </div>
      </div>
      <div id="widget-id-2-row" class="row">
          <div class="label">
            <label for="widget-id-2">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-2-remove"
                     name="widget.name.2.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-2" name="widget.name.2"
                 class="text-widget required int-field" value="" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="3" />

Now let's store the new value:

  >>> widget.request = TestRequest(form={'widget.name.count':'3',
  ...                                    'widget.name.0':'42',
  ...                                    'widget.name.1':'43',
  ...                                    'widget.name.2':'44'})
  >>> widget.update()

  >>> widget.extract()
  ['42', '43', '44']

  >>> print(widget.render())
  <div class="multi-widget">
      <div id="widget-id-0-row" class="row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-0-remove"
                     name="widget.name.0.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-0" name="widget.name.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row" class="row">
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-1-remove"
                     name="widget.name.1.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-1" name="widget.name.1"
                 class="text-widget required int-field" value="43" />
          </div>
        </div>
      </div>
      <div id="widget-id-2-row" class="row">
          <div class="label">
            <label for="widget-id-2">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-2-remove"
                     name="widget.name.2.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-2" name="widget.name.2"
                 class="text-widget required int-field" value="44" />
            </div>
          </div>
      </div>
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="3" />

As you can see in the above sample, the new stored value get rendered as a
real value and the new adding value input field is gone. Now let's try to
remove an existing value:

  >>> widget.request = TestRequest(form={'widget.name.count':'3',
  ...                                    'widget.name.0':'42',
  ...                                    'widget.name.1':'43',
  ...                                    'widget.name.2':'44',
  ...                                    'widget.name.1.remove':'1',
  ...                                    'widget.name.buttons.remove':'Remove selected'})
  >>> widget.update()

This is good so, because the Remove selected is an widget-internal submit action

  >>> widget.extract()
  ['42', '43', '44']

  >>> print(widget.render())
  <div class="multi-widget">
      <div id="widget-id-0-row" class="row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-0-remove"
                     name="widget.name.0.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-0" name="widget.name.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row" class="row">
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-1-remove"
                     name="widget.name.1.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-1" name="widget.name.1"
                 class="text-widget required int-field" value="44" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

Change again a value after delete:

  >>> widget.request = TestRequest(form={'widget.name.count':'2',
  ...                                    'widget.name.0':'42',
  ...                                    'widget.name.1':'45'})
  >>> widget.update()

  >>> print(widget.render())
  <div class="multi-widget">
      <div id="widget-id-0-row" class="row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input id="widget-id-0-remove" name="widget.name.0.remove"
              class="multi-widget-checkbox checkbox-widget"
              type="checkbox" value="1" />
            </div>
            <div class="multi-widget-input">
                <input id="widget-id-0" name="widget.name.0"
                class="text-widget required int-field" value="42" type="text" />
            </div>
          </div>
      </div>
      <div id="widget-id-1-row" class="row">
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input id="widget-id-1-remove" name="widget.name.1.remove"
              class="multi-widget-checkbox checkbox-widget"
              type="checkbox" value="1" />
            </div>
            <div class="multi-widget-input">
                <input id="widget-id-1" name="widget.name.1"
                class="text-widget required int-field" value="45" type="text" />
            </div>
          </div>
      </div>
    <div class="buttons">
      <input id="widget-name-buttons-add" name="widget.name.buttons.add"
      class="submit-widget button-field" value="Add" type="submit" />
      <input id="widget-name-buttons-remove" name="widget.name.buttons.remove"
      class="submit-widget button-field" value="Remove selected" type="submit" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

Error handling is next. Let's use the value "bad" (an invalid integer literal)
as input for our internal (sub) widget.

  >>> from z3c.form.error import ErrorViewSnippet
  >>> from z3c.form.error import StandardErrorViewTemplate
  >>> zope.component.provideAdapter(ErrorViewSnippet)
  >>> zope.component.provideAdapter(StandardErrorViewTemplate)

  >>> widget.request = TestRequest(form={'widget.name.count':'2',
  ...                                    'widget.name.0':'42',
  ...                                    'widget.name.1':'bad'})
  >>> widget.update()

  >>> widget.extract()
  ['42', 'bad']

  >>> print(widget.render())
  <div class="multi-widget">
      <div id="widget-id-0-row" class="row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-0-remove"
                     name="widget.name.0.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-0" name="widget.name.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row" class="row">
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="error">The entered value is not a valid integer
                             literal.</div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-1-remove"
                     name="widget.name.1.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-1" name="widget.name.1"
                 class="text-widget required int-field" value="bad" />
            </div>
          </div>
      </div>
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

The widget filters out the add and remove buttons depending on the
current value and the field constraints. You already saw that there's
no remove button for empty value. Now, let's check rendering with
minimum and maximum lengths defined in the field constraints.

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(title='Number'),
  ...     min_length=1,
  ...     max_length=3
  ...     )
  >>> widget.field = field
  >>> widget.widgets = []
  >>> widget.value = []

Let's test with minimum sequence, there should be no remove button:

  >>> widget.request = TestRequest(form={'widget.name.count':'1',
  ...                                    'widget.name.0':'42'})
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget">
      <div id="widget-id-0-row" class="row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-0-remove"
                     name="widget.name.0.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-0" name="widget.name.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field" value="Add" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="1" />

Now, with middle-length sequence. All buttons should be there.

  >>> widget.request = TestRequest(form={'widget.name.count':'2',
  ...                                    'widget.name.0':'42',
  ...                                    'widget.name.1':'43'})
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget">
      <div id="widget-id-0-row" class="row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-0-remove"
                     name="widget.name.0.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-0" name="widget.name.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row" class="row">
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-1-remove"
                     name="widget.name.1.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-1" name="widget.name.1"
                 class="text-widget required int-field" value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

Okay, now let's check the maximum-length sequence. There should be
no add button:

  >>> widget.request = TestRequest(form={'widget.name.count':'3',
  ...                                    'widget.name.0':'42',
  ...                                    'widget.name.1':'43',
  ...                                    'widget.name.2':'44'})
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget">
      <div id="widget-id-0-row" class="row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-0-remove"
                     name="widget.name.0.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-0" name="widget.name.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row" class="row">
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-1-remove"
                     name="widget.name.1.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-1" name="widget.name.1"
                 class="text-widget required int-field" value="43" />
          </div>
        </div>
      </div>
      <div id="widget-id-2-row" class="row">
          <div class="label">
            <label for="widget-id-2">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="widget-id-2-remove"
                     name="widget.name.2.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="widget-id-2" name="widget.name.2"
                 class="text-widget required int-field" value="44" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="widget.name.count" value="3" />

Dictionaries
############

The multi widget also supports IDict schemas.

  >>> field = zope.schema.Dict(
  ...     __name__='foo',
  ...     key_type=zope.schema.Int(title='Number'),
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.widgets = []
  >>> widget.value = [('1','42')]
  >>> print(widget.render())
    <div class="multi-widget">
        <div id="widget-id-0-row" class="row">
              <div class="label">
                <label for="widget-id-key-0">
                  <span>Number</span>
                  <span class="required">*</span>
                </label>
              </div>
              <div class="widget">
                  <div class="multi-widget-input-key">
        <input id="widget-id-key-0" name="widget.name.key.0" class="text-widget required int-field" value="1" type="text" />
    </div>
              </div>
            <div class="label">
              <label for="widget-id-0">
                <span>Number</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <div class="multi-widget-checkbox">
                <input id="widget-id-0-remove" name="widget.name.0.remove" class="multi-widget-checkbox checkbox-widget" type="checkbox" value="1" />
              </div>
              <div class="multi-widget-input">
        <input id="widget-id-0" name="widget.name.0" class="text-widget required int-field" value="42" type="text" />
    </div>
            </div>
        </div>
     <div class="buttons">
    <input id="widget-name-buttons-remove" name="widget.name.buttons.remove" class="submit-widget button-field" value="Remove selected" type="submit" />
       </div>
    </div>
    <input type="hidden" name="widget.name.count" value="1" />

If we now click on the ``Add`` button, we will get a new input field for entering
a new value:

  >>> widget.request = TestRequest(form={'widget.name.count':'1',
  ...                                    'widget.name.key.0':'1',
  ...                                    'widget.name.0':'42',
  ...                                    'widget.name.buttons.add':'Add'})
  >>> widget.update()

  >>> widget.extract()
  [('1', '42')]

  >>> print(widget.render())
  <html>
    <body>
      <div class="multi-widget">
        <div class="row" id="widget-id-0-row">
          <div class="label">
            <label for="widget-id-key-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-input-key">
              <input class="text-widget required int-field" id="widget-id-key-0" name="widget.name.key.0" type="text" value="1">
            </div>
          </div>
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input class="multi-widget-checkbox checkbox-widget" id="widget-id-0-remove" name="widget.name.0.remove" type="checkbox" value="1">
            </div>
            <div class="multi-widget-input">
              <input class="text-widget required int-field" id="widget-id-0" name="widget.name.0" type="text" value="42">
            </div>
          </div>
        </div>
        <div class="row" id="widget-id-1-row">
          <div class="label">
            <label for="widget-id-key-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-input-key">
              <input class="text-widget required int-field" id="widget-id-key-1" name="widget.name.key.1" type="text" value="">
            </div>
          </div>
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input class="multi-widget-checkbox checkbox-widget" id="widget-id-1-remove" name="widget.name.1.remove" type="checkbox" value="1">
            </div>
            <div class="multi-widget-input">
              <input class="text-widget required int-field" id="widget-id-1" name="widget.name.1" type="text" value="">
            </div>
          </div>
        </div>
        <div class="buttons">
          <input class="submit-widget button-field" id="widget-name-buttons-add" name="widget.name.buttons.add" type="submit" value="Add">
          <input class="submit-widget button-field" id="widget-name-buttons-remove" name="widget.name.buttons.remove" type="submit" value="Remove selected">
        </div>
      </div>
      <input name="widget.name.count" type="hidden" value="2">
    </body>
  </html>

Now let's store the new value:

  >>> widget.request = TestRequest(form={'widget.name.count':'2',
  ...                                    'widget.name.key.0':'1',
  ...                                    'widget.name.0':'42',
  ...                                    'widget.name.key.1':'2',
  ...                                    'widget.name.1':'43'})
  >>> widget.update()

  >>> widget.extract()
  [('1', '42'), ('2', '43')]

We will get an error if we try and set the same key twice

  >>> from z3c.form.error import InvalidErrorViewSnippet
  >>> zope.component.provideAdapter(InvalidErrorViewSnippet)

  >>> widget.request = TestRequest(form={'widget.name.count':'2',
  ...                                    'widget.name.key.0':'1',
  ...                                    'widget.name.0':'42',
  ...                                    'widget.name.key.1':'1',
  ...                                    'widget.name.1':'43'})
  >>> widget.update()

  >>> widget.extract()
  [('1', '42'), ('1', '43')]

  >>> print(widget.render())
    <div class="multi-widget">
        <div id="widget-id-0-row" class="row">
              <div class="label">
                <label for="widget-id-key-0">
                  <span>Number</span>
                  <span class="required">*</span>
                </label>
              </div>
              <div class="widget">
                  <div class="multi-widget-input-key">
        <input id="widget-id-key-0" name="widget.name.key.0" class="text-widget required int-field" value="1" type="text" />
    </div>
              </div>
            <div class="label">
              <label for="widget-id-0">
                <span>Number</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <div class="multi-widget-checkbox">
                <input id="widget-id-0-remove" name="widget.name.0.remove" class="multi-widget-checkbox checkbox-widget" type="checkbox" value="1" />
              </div>
              <div class="multi-widget-input">
        <input id="widget-id-0" name="widget.name.0" class="text-widget required int-field" value="42" type="text" />
    </div>
            </div>
        </div>
        <div id="widget-id-1-row" class="row">
              <div class="label">
                <label for="widget-id-key-1">
                  <span>Number</span>
                  <span class="required">*</span>
                </label>
              </div>
      <div class="error">Duplicate key</div>
              <div class="widget">
                  <div class="multi-widget-input-key">
        <input id="widget-id-key-1" name="widget.name.key.1" class="text-widget required int-field" value="1" type="text" />
    </div>
              </div>
            <div class="label">
              <label for="widget-id-1">
                <span>Number</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <div class="multi-widget-checkbox">
                <input id="widget-id-1-remove" name="widget.name.1.remove" class="multi-widget-checkbox checkbox-widget" type="checkbox" value="1" />
              </div>
              <div class="multi-widget-input">
        <input id="widget-id-1" name="widget.name.1" class="text-widget required int-field" value="43" type="text" />
    </div>
            </div>
        </div>
      <div class="buttons">
    <input id="widget-name-buttons-add" name="widget.name.buttons.add" class="submit-widget button-field" value="Add" type="submit" />
    <input id="widget-name-buttons-remove" name="widget.name.buttons.remove" class="submit-widget button-field" value="Remove selected" type="submit" />
       </div>
    </div>
    <input type="hidden" name="widget.name.count" value="2" />


Displaying
##########

The widget can be instantiated only using the request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

Set the mode to DISPLAY_MODE:

  >>> widget.mode = interfaces.DISPLAY_MODE

We also need to register the template for at least the widget and request:

  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form.testing import getPath
  >>> from z3c.form.widget import WidgetTemplateFactory

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('multi_display.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IMultiWidget),
  ...     IPageTemplate, name=interfaces.DISPLAY_MODE)

We can now render the widget:

  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget" id="widget-id"></div>

As you can see the widget is empty and doesn't provide values. This is because
the widget does not know what sub-widgets to display. So let's register a
`IFieldWidget` adapter and a template for our `IInt` field:

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('text_display.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.ITextWidget),
  ...     IPageTemplate, name=interfaces.DISPLAY_MODE)

Let's now update the widget and check it again.

  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget" id="widget-id"></div>

It's still the same. Since the widget doesn't provide a field nothing useful
gets rendered. Now let's define a field for this widget and check it again:

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget" id="widget-id"></div>

As you can see, there is still no input value. Let's provide some values for
this widget. Before we can do that, we will need to register a data converter
for our multi widget and the data converter dispatcher adapter:

  >>> widget.update()
  >>> widget.value = ['42', '43']
  >>> print(widget.render())
  <div class="multi-widget" id="widget-id">
    <div class="row" id="widget-id-0-row">
      <div class="label">
        <label for="widget-id-0">
          <span>Number</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-display">
          <span class="text-widget int-field" id="widget-id-0">42</span>
        </div>
      </div>
    </div>
    <div class="row" id="widget-id-1-row">
      <div class="label">
        <label for="widget-id-1">
          <span>Number</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-display">
          <span class="text-widget int-field" id="widget-id-1">43</span>
        </div>
      </div>
    </div>
  </div>

We can also use the multi widget with dictionaries

  >>> field = zope.schema.Dict(
  ...     __name__='foo',
  ...     key_type=zope.schema.Int(title='Number'),
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.value = [('1', '42'), ('2', '43')]
  >>> print(widget.render())
  <div class="multi-widget" id="widget-id">
    <div class="row" id="widget-id-0-row">
      <div class="label">
        <label for="widget-id-key-0">
          <span>Number</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-display">
          <span class="text-widget int-field" id="widget-id-key-0">1</span>
        </div>
      </div>
      <div class="label">
        <label for="widget-id-0">
          <span>Number</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-display">
          <span class="text-widget int-field" id="widget-id-0">42</span>
        </div>
      </div>
    </div>
    <div class="row" id="widget-id-1-row">
      <div class="label">
        <label for="widget-id-key-1">
          <span>Number</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-display">
          <span class="text-widget int-field" id="widget-id-key-1">2</span>
        </div>
      </div>
      <div class="label">
        <label for="widget-id-1">
          <span>Number</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-display">
          <span class="text-widget int-field" id="widget-id-1">43</span>
        </div>
      </div>
    </div>
  </div>


Hidden mode
###########

The widget can be instantiated only using the request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

Set the mode to HIDDEN_MODE:

  >>> widget.mode = interfaces.HIDDEN_MODE

We also need to register the template for at least the widget and request:

  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form.testing import getPath
  >>> from z3c.form.widget import WidgetTemplateFactory

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('multi_hidden.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IMultiWidget),
  ...     IPageTemplate, name=interfaces.HIDDEN_MODE)

We can now render the widget:

  >>> widget.update()
  >>> print(widget.render())
  <input name="widget.name.count" type="hidden" value="0">

As you can see the widget is empty and doesn't provide values. This is because
the widget does not know what sub-widgets to display. So let's register a
`IFieldWidget` adapter and a template for our `IInt` field:

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('text_hidden.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.ITextWidget),
  ...     IPageTemplate, name=interfaces.HIDDEN_MODE)

Let's now update the widget and check it again.

  >>> widget.update()
  >>> print(widget.render())
  <input name="widget.name.count" type="hidden" value="0">

It's still the same. Since the widget doesn't provide a field nothing useful
gets rendered. Now let's define a field for this widget and check it again:

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.update()
  >>> print(widget.render())
  <input name="widget.name.count" type="hidden" value="0">

As you can see, there is still no input value. Let's provide some values for
this widget. Before we can do that, we will need to register a data converter
for our multi widget and the data converter dispatcher adapter:

  >>> widget.update()
  >>> widget.value = ['42', '43']
  >>> print(widget.render())
  <input class="hidden-widget"
         id="widget-id-0" name="widget.name.0" type="hidden" value="42">
  <input class="hidden-widget"
         id="widget-id-1" name="widget.name.1" type="hidden" value="43">
  <input name="widget.name.count" type="hidden" value="2">

We can also use the multi widget with dictionaries

  >>> field = zope.schema.Dict(
  ...     __name__='foo',
  ...     key_type=zope.schema.Int(title='Number'),
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.value = [('1', '42'), ('2', '43')]
  >>> print(widget.render())
  <input class="hidden-widget"
         id="widget-id-key-0" name="widget.name.key.0" type="hidden" value="1">
  <input class="hidden-widget"
         id="widget-id-0" name="widget.name.0" type="hidden" value="42">
  <input class="hidden-widget"
         id="widget-id-key-1" name="widget.name.key.1" type="hidden" value="2">
  <input class="hidden-widget"
         id="widget-id-1" name="widget.name.1" type="hidden" value="43">
  <input name="widget.name.count" type="hidden" value="2">


Label
#####

There is an option which allows to disable the label for the subwidgets.
You can set the `showLabel` option to `False` which will skip rendering the
labels. Alternatively you can also register your own template for your layer
if you like to skip the label rendering for all widgets. One more way
is to register an attribute adapter for specific field/widget/layer/etc.
See below for an example.

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(
  ...         title='Ignored'),
  ...     )
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)
  >>> widget.field = field
  >>> widget.value = ['42', '43']
  >>> widget.showLabel = False
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget">
      <div id="None-0-row" class="row">
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="None-0-remove" name="None.0.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="None-0" name="None.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="None-1-row" class="row">
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="None-1-remove" name="None.1.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="None-1" name="None.1"
                 class="text-widget required int-field" value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="widget-buttons-add"
         name="widget.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="widget-buttons-remove"
         name="widget.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="None.count" value="2" />

We can also override the showLabel attribute value with an attribute
adapter. We set it to False for our widget before, but the update method
sets adapted attributes, so if we provide an attribute, it will be used
to set the ``showLabel``. Let's see.

  >>> from z3c.form.widget import StaticWidgetAttribute

  >>> doShowLabel = StaticWidgetAttribute(True, widget=widget)
  >>> zope.component.provideAdapter(doShowLabel, name="showLabel")

  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget">
      <div id="None-0-row" class="row">
          <div class="label">
            <label for="None-0">
              <span>Ignored</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="None-0-remove" name="None.0.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="None-0" name="None.0"
                 class="text-widget required int-field" value="42" />
          </div>
        </div>
      </div>
      <div id="None-1-row" class="row">
          <div class="label">
            <label for="None-1">
              <span>Ignored</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input type="checkbox" value="1"
                     class="multi-widget-checkbox checkbox-widget"
                     id="None-1-remove" name="None.1.remove" />
            </div>
            <div class="multi-widget-input"><input
                 type="text" id="None-1" name="None.1"
                 class="text-widget required int-field" value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
      <input type="submit" id="widget-buttons-add"
         name="widget.buttons.add"
         class="submit-widget button-field" value="Add" />
      <input type="submit" id="widget-buttons-remove"
         name="widget.buttons.remove"
         class="submit-widget button-field" value="Remove selected" />
     </div>
  </div>
  <input type="hidden" name="None.count" value="2" />


Coverage happiness
##################

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)
  >>> widget.field = field
  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'
  >>> widget.widgets = []
  >>> widget.value = []

  >>> widget.request = TestRequest()
  >>> widget.update()

  >>> widget.value = ['42', '43', '44']
  >>> widget.value = ['99']

  >>> print(widget.render())
    <html>
    <body>
      <div class="multi-widget">
        <div class="row" id="widget-id-0-row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input class="multi-widget-checkbox checkbox-widget" id="widget-id-0-remove" name="widget.name.0.remove" type="checkbox" value="1">
            </div>
            <div class="multi-widget-input">
              <input class="text-widget required int-field" id="widget-id-0" name="widget.name.0" type="text" value="99">
            </div>
          </div>
        </div>
        <div class="row" id="widget-id-1-row">
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input class="multi-widget-checkbox checkbox-widget" id="widget-id-1-remove" name="widget.name.1.remove" type="checkbox" value="1">
            </div>
            <div class="multi-widget-input">
              <input class="text-widget required int-field" id="widget-id-1" name="widget.name.1" type="text" value="">
            </div>
          </div>
        </div>
        <div class="row" id="widget-id-2-row">
          <div class="label">
            <label for="widget-id-2">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input class="multi-widget-checkbox checkbox-widget" id="widget-id-2-remove" name="widget.name.2.remove" type="checkbox" value="1">
            </div>
            <div class="multi-widget-input">
              <input class="text-widget required int-field" id="widget-id-2" name="widget.name.2" type="text" value="">
            </div>
          </div>
        </div>
        <div class="buttons">
          <input class="submit-widget button-field" id="widget-name-buttons-add" name="widget.name.buttons.add" type="submit" value="Add">
        </div>
      </div>
      <input name="widget.name.count" type="hidden" value="3">
    </body>
  </html>
