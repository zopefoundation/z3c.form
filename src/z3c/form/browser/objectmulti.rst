Multi+Object Widget
-------------------

The multi widget allows you to add and edit one or more values.

In order to not overwhelm you with our set of well-chosen defaults,
all the default component registrations have been made prior to doing those
examples:

  >>> from z3c.form import testing
  >>> testing.setupFormDefaults()

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

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('multi_display.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IMultiWidget),
  ...     IPageTemplate, name=interfaces.DISPLAY_MODE)

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

  >>> from z3c.form.widget import FieldWidget

  >>> from z3c.form.testing import IMySubObjectMulti
  >>> from z3c.form.testing import MySubObjectMulti

  >>> from z3c.form.object import registerFactoryAdapter
  >>> registerFactoryAdapter(IMySubObjectMulti, MySubObjectMulti)

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Object(title=u'my object widget',
  ...                                   schema=IMySubObjectMulti),
  ...     )

  >>> widget = FieldWidget(field, widget)
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget required">
    <div class="buttons">
      <input type="submit" id="foo-buttons-add"
         name="foo.buttons.add"
         class="submit-widget button-field" value="Add" />
     </div>
  </div>
  <input type="hidden" name="foo.count" value="0" />

As you can see, there is still no input value. Let's provide some values for
this widget. Before we can do that, we will need to register a data converter
for our multi widget and the data converter dispatcher adapter:

  >>> from z3c.form.converter import IntegerDataConverter
  >>> from z3c.form.converter import FieldWidgetDataConverter
  >>> from z3c.form.converter import MultiConverter
  >>> from z3c.form.validator import SimpleFieldValidator
  >>> zope.component.provideAdapter(IntegerDataConverter)
  >>> zope.component.provideAdapter(FieldWidgetDataConverter)
  >>> zope.component.provideAdapter(SimpleFieldValidator)
  >>> zope.component.provideAdapter(MultiConverter)

Bunch of adapters to get objectwidget work:

  >>> from z3c.form import datamanager
  >>> zope.component.provideAdapter(datamanager.DictionaryField)

  >>> import z3c.form.browser.object
  >>> zope.component.provideAdapter(z3c.form.browser.object.ObjectFieldWidget)
  >>> import z3c.form.object
  >>> zope.component.provideAdapter(z3c.form.object.ObjectConverter)
  >>> import z3c.form.error
  >>> zope.component.provideAdapter(z3c.form.error.ValueErrorViewSnippet)

  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form.testing import getPath
  >>> from z3c.form.widget import WidgetTemplateFactory

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('object_input.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IObjectWidget),
  ...     IPageTemplate, name=interfaces.INPUT_MODE)

  >>> zope.component.provideAdapter(
  ...     WidgetTemplateFactory(getPath('object_display.pt'), 'text/html'),
  ...     (None, None, None, None, interfaces.IObjectWidget),
  ...     IPageTemplate, name=interfaces.DISPLAY_MODE)

  >>> widget.update()

It must not fail if we assign values that do not meet the constraints,
just cry about it in the HTML:

  >>> widget.value = [z3c.form.object.ObjectWidgetValue(
  ...     {'foofield': u'', 'barfield': '666'})]
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget required">
    <div class="row" id="foo-0-row">
      <div class="label">
        <label for="foo-0">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="error">An object failed schema or invariant validation.</div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget"
                 id="foo-0-remove" name="foo.0.remove" type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-0-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="error">Required input is missing.</div>
            <div class="widget">
              <input class="text-widget required int-field"
                     id="foo-0-widgets-foofield" name="foo.0.widgets.foofield"
                     type="text" value="">
            </div>
            <div class="label">
              <label for="foo-0-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field"
                     id="foo-0-widgets-barfield" name="foo.0.widgets.barfield"
                     type="text" value="666">
            </div>
            <input name="foo.0-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="buttons">
      <input id="foo-buttons-add" name="foo.buttons.add"
             class="submit-widget button-field" value="Add"
             type="submit" />
      <input id="foo-buttons-remove"
             name="foo.buttons.remove"
             class="submit-widget button-field" value="Remove selected"
             type="submit" />
    </div>
  </div>
  <input name="foo.count" type="hidden" value="1">

Let's set acceptable values:

  >>> widget.value = [
  ...     z3c.form.object.ObjectWidgetValue(dict(foofield=u'42', barfield=u'666')),
  ...     z3c.form.object.ObjectWidgetValue(dict(foofield=u'789', barfield=u'321'))]

  >>> print(widget.render())
  <div class="multi-widget required">
      <div id="foo-0-row" class="row">
          <div class="label">
            <label for="foo-0">
              <span>my object widget</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input id="foo-0-remove"
                     name="foo.0.remove"
                     class="multi-widget-checkbox checkbox-widget"
                     type="checkbox" value="1" />
            </div>
            <div class="multi-widget-input">
              <div class="object-widget required">
                <div class="label">
                  <label for="foo-0-widgets-foofield">
                    <span>My foo field</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
                    <input id="foo-0-widgets-foofield"
                           name="foo.0.widgets.foofield"
                           class="text-widget required int-field" value="42"
                           type="text" />
                </div>
                <div class="label">
                  <label for="foo-0-widgets-barfield">
                    <span>My dear bar</span>
                  </label>
                </div>
                <div class="widget">
                    <input id="foo-0-widgets-barfield"
                           name="foo.0.widgets.barfield"
                           class="text-widget int-field" value="666"
                           type="text" />
                </div>
                <input name="foo.0-empty-marker" type="hidden"
                       value="1" />
              </div>
            </div>
          </div>
      </div>
      <div id="foo-1-row" class="row">
          <div class="label">
            <label for="foo-1">
              <span>my object widget</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-checkbox">
              <input id="foo-1-remove"
                     name="foo.1.remove"
                     class="multi-widget-checkbox checkbox-widget"
                     type="checkbox" value="1" />
            </div>
            <div class="multi-widget-input">
              <div class="object-widget required">
                <div class="label">
                  <label for="foo-1-widgets-foofield">
                    <span>My foo field</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
                  <input id="foo-1-widgets-foofield"
                         name="foo.1.widgets.foofield"
                         class="text-widget required int-field"
                         value="789" type="text" />
                </div>
                <div class="label">
                  <label for="foo-1-widgets-barfield">
                    <span>My dear bar</span>
                  </label>
                </div>
                <div class="widget">
                    <input id="foo-1-widgets-barfield"
                           name="foo.1.widgets.barfield"
                           class="text-widget int-field" value="321"
                           type="text" />
                </div>
                <input name="foo.1-empty-marker" type="hidden"
                       value="1" />
              </div>
            </div>
          </div>
      </div>
    <div class="buttons">
      <input id="foo-buttons-add" name="foo.buttons.add"
             class="submit-widget button-field" value="Add"
             type="submit" />
      <input id="foo-buttons-remove"
             name="foo.buttons.remove"
             class="submit-widget button-field" value="Remove selected"
             type="submit" />
    </div>
  </div>
  <input type="hidden" name="foo.count" value="2" />

Let's see what we get on value extraction:

  >>> widget.extract()
  <NO_VALUE>

If we now click on the ``Add`` button, we will get a new input field for enter
a new value:

  >>> widget.request = TestRequest(form={'foo.count':u'2',
  ...                                    'foo.0.widgets.foofield':u'42',
  ...                                    'foo.0.widgets.barfield':u'666',
  ...                                    'foo.0-empty-marker':u'1',
  ...                                    'foo.1.widgets.foofield':u'789',
  ...                                    'foo.1.widgets.barfield':u'321',
  ...                                    'foo.1-empty-marker':u'1',
  ...                                    'foo.buttons.add':'Add'})
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget required">
    <div class="row" id="foo-0-row">
      <div class="label">
        <label for="foo-0">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget"
                 id="foo-0-remove"
                 name="foo.0.remove"
                 type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-0-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field"
                     id="foo-0-widgets-foofield"
                     name="foo.0.widgets.foofield"
                     type="text" value="42">
            </div>
            <div class="label">
              <label for="foo-0-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field"
                     id="foo-0-widgets-barfield"
                     name="foo.0.widgets.barfield"
                     type="text" value="666">
            </div>
            <input name="foo.0-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="row" id="foo-1-row">
      <div class="label">
        <label for="foo-1">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget"
                 id="foo-1-remove"
                 name="foo.1.remove"
                 type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-1-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field"
                     id="foo-1-widgets-foofield"
                     name="foo.1.widgets.foofield"
                     type="text" value="789">
            </div>
            <div class="label">
              <label for="foo-1-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field"
                     id="foo-1-widgets-barfield"
                     name="foo.1.widgets.barfield"
                     type="text" value="321">
            </div>
            <input name="foo.1-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="row" id="foo-2-row">
      <div class="label">
        <label for="foo-2">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget"
                 id="foo-2-remove"
                 name="foo.2.remove"
                 type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-2-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field"
                     id="foo-2-widgets-foofield"
                     name="foo.2.widgets.foofield"
                     type="text" value="">
            </div>
            <div class="label">
              <label for="foo-2-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field"
                     id="foo-2-widgets-barfield"
                     name="foo.2.widgets.barfield"
                     type="text" value="2,222">
            </div>
            <input name="foo.2-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="buttons">
      <input id="foo-buttons-add" name="foo.buttons.add"
             class="submit-widget button-field" value="Add"
             type="submit" />
      <input id="foo-buttons-remove"
             name="foo.buttons.remove"
             class="submit-widget button-field" value="Remove selected"
             type="submit" />
    </div>
  </div>
  <input name="foo.count" type="hidden" value="3">

Let's see what we get on value extraction:

  >>> value = widget.extract()
  >>> pprint(value)
  [{'barfield': '666', 'foofield': '42'}, {'barfield': '321', 'foofield': '789'}]
  >>> converter = interfaces.IDataConverter(widget)

  >>> value = converter.toFieldValue(value)
  >>> value
  [<z3c.form.testing.MySubObjectMulti object at ...>,
  <z3c.form.testing.MySubObjectMulti object at ...>]

  >>> value[0].foofield
  42
  >>> value[0].barfield
  666


Now let's store the new value:


  >>> widget.request = TestRequest(form={'foo.count':u'3',
  ...                                    'foo.0.widgets.foofield':u'42',
  ...                                    'foo.0.widgets.barfield':u'666',
  ...                                    'foo.0-empty-marker':u'1',
  ...                                    'foo.1.widgets.foofield':u'789',
  ...                                    'foo.1.widgets.barfield':u'321',
  ...                                    'foo.1-empty-marker':u'1',
  ...                                    'foo.2.widgets.foofield':u'46',
  ...                                    'foo.2.widgets.barfield':u'98',
  ...                                    'foo.2-empty-marker':u'1',
  ...                                    })
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget required">
    <div class="row" id="foo-0-row">
      <div class="label">
        <label for="foo-0">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget" id="foo-0-remove"
                 name="foo.0.remove" type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-0-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field"
                     id="foo-0-widgets-foofield" name="foo.0.widgets.foofield"
                     type="text" value="42">
            </div>
            <div class="label">
              <label for="foo-0-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field" id="foo-0-widgets-barfield"
                     name="foo.0.widgets.barfield" type="text" value="666">
            </div>
            <input name="foo.0-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="row" id="foo-1-row">
      <div class="label">
        <label for="foo-1">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget" id="foo-1-remove"
                 name="foo.1.remove" type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-1-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field"
                     id="foo-1-widgets-foofield" name="foo.1.widgets.foofield"
                     type="text" value="789">
            </div>
            <div class="label">
              <label for="foo-1-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field" id="foo-1-widgets-barfield"
                     name="foo.1.widgets.barfield" type="text" value="321">
            </div>
            <input name="foo.1-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="row" id="foo-2-row">
      <div class="label">
        <label for="foo-2">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget" id="foo-2-remove"
                 name="foo.2.remove" type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-2-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field"
                     id="foo-2-widgets-foofield" name="foo.2.widgets.foofield"
                     type="text" value="46">
            </div>
            <div class="label">
              <label for="foo-2-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field" id="foo-2-widgets-barfield"
                     name="foo.2.widgets.barfield" type="text" value="98">
            </div>
            <input name="foo.2-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="buttons">
      <input class="submit-widget button-field" id="foo-buttons-add"
             name="foo.buttons.add" type="submit" value="Add">
      <input class="submit-widget button-field" id="foo-buttons-remove"
             name="foo.buttons.remove" type="submit" value="Remove selected">
    </div>
  </div>
  <input name="foo.count" type="hidden" value="3">

Let's see what we get on value extraction:

  >>> value = widget.extract()
  >>> pprint(value)
  [{'barfield': '666', 'foofield': '42'},
   {'barfield': '321', 'foofield': '789'},
   {'barfield': '98', 'foofield': '46'}]
  >>> converter = interfaces.IDataConverter(widget)

  >>> value = converter.toFieldValue(value)
  >>> value
  [<z3c.form.testing.MySubObjectMulti object at ...>,
  <z3c.form.testing.MySubObjectMulti object at ...>]

  >>> value[0].foofield
  42
  >>> value[0].barfield
  666


As you can see in the above sample, the new stored value gets rendered as a
real value and the new adding value input field is gone. Now let's try to
remove an existing value:

  >>> widget.request = TestRequest(form={'foo.count':u'3',
  ...                                    'foo.0.widgets.foofield':u'42',
  ...                                    'foo.0.widgets.barfield':u'666',
  ...                                    'foo.0-empty-marker':u'1',
  ...                                    'foo.1.widgets.foofield':u'789',
  ...                                    'foo.1.widgets.barfield':u'321',
  ...                                    'foo.1-empty-marker':u'1',
  ...                                    'foo.2.widgets.foofield':u'46',
  ...                                    'foo.2.widgets.barfield':u'98',
  ...                                    'foo.2-empty-marker':u'1',
  ...                                    'foo.1.remove':u'1',
  ...                                    'foo.buttons.remove':'Remove selected'})
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget required">
    <div class="row" id="foo-0-row">
      <div class="label">
        <label for="foo-0">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget" id="foo-0-remove"
                 name="foo.0.remove" type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-0-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field"
                     id="foo-0-widgets-foofield" name="foo.0.widgets.foofield"
                     type="text" value="42">
            </div>
            <div class="label">
              <label for="foo-0-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field" id="foo-0-widgets-barfield"
                     name="foo.0.widgets.barfield" type="text" value="666">
            </div>
            <input name="foo.0-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="row" id="foo-1-row">
      <div class="label">
        <label for="foo-1">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget" id="foo-1-remove"
                 name="foo.1.remove" type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-1-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field"
                     id="foo-1-widgets-foofield" name="foo.1.widgets.foofield"
                     type="text" value="46">
            </div>
            <div class="label">
              <label for="foo-1-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field" id="foo-1-widgets-barfield"
                     name="foo.1.widgets.barfield" type="text" value="98">
            </div>
            <input name="foo.1-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="buttons">
      <input class="submit-widget button-field" id="foo-buttons-add"
             name="foo.buttons.add" type="submit" value="Add">
      <input class="submit-widget button-field" id="foo-buttons-remove"
             name="foo.buttons.remove" type="submit" value="Remove selected">
    </div>
  </div>
  <input name="foo.count" type="hidden" value="2">

Let's see what we get on value extraction:
(this is good so, because Remove selected is a widget-internal submit)

  >>> value = widget.extract()
  >>> pprint(value)
  [{'barfield': '666', 'foofield': '42'},
   {'barfield': '321', 'foofield': '789'},
   {'barfield': '98', 'foofield': '46'}]
  >>> converter = interfaces.IDataConverter(widget)

  >>> value = converter.toFieldValue(value)
  >>> value
  [<z3c.form.testing.MySubObjectMulti object at ...>,
  <z3c.form.testing.MySubObjectMulti object at ...>]

  >>> value[0].foofield
  42
  >>> value[0].barfield
  666


Error handling is next. Let's use the value "bad" (an invalid integer literal)
as input for our internal (sub) widget.

  >>> from z3c.form.error import ErrorViewSnippet
  >>> from z3c.form.error import StandardErrorViewTemplate
  >>> zope.component.provideAdapter(ErrorViewSnippet)
  >>> zope.component.provideAdapter(StandardErrorViewTemplate)

  >>> widget.request = TestRequest(form={'foo.count':u'2',
  ...                                    'foo.0.widgets.foofield':u'42',
  ...                                    'foo.0.widgets.barfield':u'666',
  ...                                    'foo.0-empty-marker':u'1',
  ...                                    'foo.1.widgets.foofield':u'bad',
  ...                                    'foo.1.widgets.barfield':u'98',
  ...                                    'foo.1-empty-marker':u'1',
  ...                                    })

  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget required">
    <div class="row" id="foo-0-row">
      <div class="label">
        <label for="foo-0">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget" id="foo-0-remove" name="foo.0.remove" type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-0-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field" id="foo-0-widgets-foofield" name="foo.0.widgets.foofield" type="text" value="42">
            </div>
            <div class="label">
              <label for="foo-0-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field" id="foo-0-widgets-barfield" name="foo.0.widgets.barfield" type="text" value="666">
            </div>
            <input name="foo.0-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="row" id="foo-1-row">
      <div class="label">
        <label for="foo-1">
          <span>my object widget</span>
          <span class="required">*</span>
        </label>
      </div>
      <div class="error">The entered value is not a valid integer literal.</div>
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget" id="foo-1-remove" name="foo.1.remove" type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-1-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="error">The entered value is not a valid integer literal.</div>
            <div class="widget">
              <input class="text-widget required int-field" id="foo-1-widgets-foofield" name="foo.1.widgets.foofield" type="text" value="bad">
            </div>
            <div class="label">
              <label for="foo-1-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field" id="foo-1-widgets-barfield" name="foo.1.widgets.barfield" type="text" value="98">
            </div>
            <input name="foo.1-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="buttons">
      <input class="submit-widget button-field" id="foo-buttons-add" name="foo.buttons.add" type="submit" value="Add">
      <input class="submit-widget button-field" id="foo-buttons-remove" name="foo.buttons.remove" type="submit" value="Remove selected">
    </div>
  </div>
  <input name="foo.count" type="hidden" value="2">

Let's see what we get on value extraction:

  >>> value = widget.extract()
  >>> pprint(value)
  [{'barfield': '666', 'foofield': '42'},
   {'barfield': '98', 'foofield': 'bad'}]


Label
#####

There is an option which allows to disable the label for the (sub) widgets.
You can set the `showLabel` option to `False` which will skip rendering the
labels. Alternatively you can also register your own template for your layer
if you like to skip the label rendering for all widgets.


  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Object(title=u'ignored_title',
  ...                                   schema=IMySubObjectMulti),
  ...     )
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)
  >>> widget = FieldWidget(field, widget)
  >>> widget.value = [
  ...     z3c.form.object.ObjectWidgetValue(dict(foofield='42', barfield='666')),
  ...     z3c.form.object.ObjectWidgetValue(dict(foofield='789', barfield='321'))]
  >>> widget.showLabel = False
  >>> widget.update()
  >>> print(widget.render())
  <div class="multi-widget required">
    <div class="row" id="foo-0-row">
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget" id="foo-0-remove" name="foo.0.remove" type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-0-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field" id="foo-0-widgets-foofield" name="foo.0.widgets.foofield" type="text" value="42">
            </div>
            <div class="label">
              <label for="foo-0-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field" id="foo-0-widgets-barfield" name="foo.0.widgets.barfield" type="text" value="666">
            </div>
            <input name="foo.0-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="row" id="foo-1-row">
      <div class="widget">
        <div class="multi-widget-checkbox">
          <input class="multi-widget-checkbox checkbox-widget" id="foo-1-remove" name="foo.1.remove" type="checkbox" value="1">
        </div>
        <div class="multi-widget-input">
          <div class="object-widget required">
            <div class="label">
              <label for="foo-1-widgets-foofield">
                <span>My foo field</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget required int-field" id="foo-1-widgets-foofield" name="foo.1.widgets.foofield" type="text" value="789">
            </div>
            <div class="label">
              <label for="foo-1-widgets-barfield">
                <span>My dear bar</span>
              </label>
            </div>
            <div class="widget">
              <input class="text-widget int-field" id="foo-1-widgets-barfield" name="foo.1.widgets.barfield" type="text" value="321">
            </div>
            <input name="foo.1-empty-marker" type="hidden" value="1">
          </div>
        </div>
      </div>
    </div>
    <div class="buttons">
      <input class="submit-widget button-field" id="foo-buttons-add" name="foo.buttons.add" type="submit" value="Add">
      <input class="submit-widget button-field" id="foo-buttons-remove" name="foo.buttons.remove" type="submit" value="Remove selected">
    </div>
  </div>
  <input name="foo.count" type="hidden" value="2">

In a form
#########

Let's try a simple example in a form.

We have to provide an adapter first:

  >>> import z3c.form.browser.object
  >>> zope.component.provideAdapter(z3c.form.browser.object.ObjectFieldWidget)


Forms and our objectwidget fire events on add and edit, setup a subscriber
for those:

  >>> eventlog = []
  >>> import zope.lifecycleevent
  >>> @zope.component.adapter(zope.lifecycleevent.ObjectModifiedEvent)
  ... def logEvent(event):
  ...     eventlog.append(event)
  >>> zope.component.provideHandler(logEvent)
  >>> @zope.component.adapter(zope.lifecycleevent.ObjectCreatedEvent)
  ... def logEvent2(event):
  ...     eventlog.append(event)
  >>> zope.component.provideHandler(logEvent2)

  >>> def printEvents():
  ...     for event in eventlog:
  ...         print(event)
  ...         if isinstance(event, zope.lifecycleevent.ObjectModifiedEvent):
  ...             for attr in event.descriptions:
  ...                 print(attr.interface)
  ...                 print(sorted(attr.attributes))

We need to provide the widgets for the List

  >>> from z3c.form.browser.multi import multiFieldWidgetFactory
  >>> zope.component.provideAdapter(multiFieldWidgetFactory,
  ...     (zope.schema.interfaces.IList, z3c.form.interfaces.IFormLayer))
  >>> zope.component.provideAdapter(multiFieldWidgetFactory,
  ...     (zope.schema.interfaces.ITuple, z3c.form.interfaces.IFormLayer))
  >>> zope.component.provideAdapter(multiFieldWidgetFactory,
  ...     (zope.schema.interfaces.IDict, z3c.form.interfaces.IFormLayer))

We define an interface containing a subobject, and an addform for it:

  >>> from z3c.form import form, field
  >>> from z3c.form.testing import MyMultiObject, IMyMultiObject

Note, that creating an object will print some information about it:

  >>> class MyAddForm(form.AddForm):
  ...     fields = field.Fields(IMyMultiObject)
  ...     def create(self, data):
  ...         print("MyAddForm.create")
  ...         pprint(data)
  ...         return MyMultiObject(**data)
  ...     def add(self, obj):
  ...         self.context[obj.name] = obj
  ...     def nextURL(self):
  ...         pass

We create the form and try to update it:

  >>> request = TestRequest()
  >>> myaddform =  MyAddForm(root, request)


  >>> myaddform.update()

As usual, the form contains a widget manager with the expected widget

  >>> list(myaddform.widgets.keys())
  ['listOfObject', 'name']
  >>> list(myaddform.widgets.values())
  [<MultiWidget 'form.widgets.listOfObject'>, <TextWidget 'form.widgets.name'>]

If we want to render the addform, we must give it a template:

  >>> import os
  >>> from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
  >>> from zope.browserpage.viewpagetemplatefile import BoundPageTemplate
  >>> from z3c.form import tests
  >>> def addTemplate(form):
  ...     form.template = BoundPageTemplate(
  ...         ViewPageTemplateFile(
  ...             'simple_edit.pt', os.path.dirname(tests.__file__)), form)
  >>> addTemplate(myaddform)

Now rendering the addform renders no items yet:

  >>> print(myaddform.render())
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <form action=".">
        <div class="row">
          <label for="form-widgets-listOfObject">My list field</label>
          <div class="multi-widget required">
            <div class="buttons">
              <input class="submit-widget button-field"
                     id="form-widgets-listOfObject-buttons-add"
                     name="form.widgets.listOfObject.buttons.add"
                     type="submit" value="Add">
            </div>
          </div>
          <input name="form.widgets.listOfObject.count" type="hidden" value="0">
        </div>
        <div class="row">
          <label for="form-widgets-name">name</label>
          <input class="text-widget required textline-field"
                 id="form-widgets-name" name="form.widgets.name"
                 type="text" value="">
        </div>
        <div class="action">
          <input class="submit-widget button-field"
                 id="form-buttons-add" name="form.buttons.add"
                 type="submit" value="Add">
        </div>
      </form>
    </body>
  </html>

We don't have the object (yet) in the root:

  >>> root['first']
  Traceback (most recent call last):
  ...
  KeyError: 'first'

Add a row to the multi widget:

  >>> request = TestRequest(form={
  ...     'form.widgets.listOfObject.count':u'0',
  ...     'form.widgets.listOfObject.buttons.add':'Add'})
  >>> myaddform.request = request

Update with the request:

  >>> myaddform.update()

Render the form:

  >>> print(myaddform.render())
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <form action=".">
        <div class="row">
          <label for="form-widgets-listOfObject">My list field</label>
          <div class="multi-widget required">
            <div class="row" id="form-widgets-listOfObject-0-row">
              <div class="label">
                <label for="form-widgets-listOfObject-0">
                  <span>my object widget</span>
                  <span class="required">*</span>
                </label>
              </div>
              <div class="widget">
                <div class="multi-widget-checkbox">
                  <input class="multi-widget-checkbox checkbox-widget"
                         id="form-widgets-listOfObject-0-remove"
                         name="form.widgets.listOfObject.0.remove"
                         type="checkbox" value="1">
                </div>
                <div class="multi-widget-input">
                  <div class="object-widget required">
                    <div class="label">
                      <label for="form-widgets-listOfObject-0-widgets-foofield">
                        <span>My foo field</span>
                        <span class="required">*</span>
                      </label>
                    </div>
                    <div class="widget">
                      <input class="text-widget required int-field"
                             id="form-widgets-listOfObject-0-widgets-foofield"
                             name="form.widgets.listOfObject.0.widgets.foofield"
                             type="text" value="">
                    </div>
                    <div class="label">
                      <label for="form-widgets-listOfObject-0-widgets-barfield">
                        <span>My dear bar</span>
                      </label>
                    </div>
                    <div class="widget">
                      <input class="text-widget int-field"
                             id="form-widgets-listOfObject-0-widgets-barfield"
                             name="form.widgets.listOfObject.0.widgets.barfield"
                             type="text" value="2,222">
                    </div>
                    <input name="form.widgets.listOfObject.0-empty-marker"
                           type="hidden" value="1">
                  </div>
                </div>
              </div>
            </div>
            <div class="buttons">
              <input class="submit-widget button-field"
                     id="form-widgets-listOfObject-buttons-add"
                     name="form.widgets.listOfObject.buttons.add"
                     type="submit" value="Add">
              <input class="submit-widget button-field"
                     id="form-widgets-listOfObject-buttons-remove"
                     name="form.widgets.listOfObject.buttons.remove"
                     type="submit" value="Remove selected">
            </div>
          </div>
          <input name="form.widgets.listOfObject.count" type="hidden" value="1">
        </div>
        <div class="row">
          <label for="form-widgets-name">name</label>
          <input class="text-widget required textline-field"
                 id="form-widgets-name" name="form.widgets.name" type="text" value="">
        </div>
        <div class="action">
          <input class="submit-widget button-field" id="form-buttons-add"
                 name="form.buttons.add" type="submit" value="Add">
        </div>
      </form>
    </body>
  </html>

Now we can fill in some values to the object, and a name to the whole schema:

  >>> request = TestRequest(form={
  ...     'form.widgets.listOfObject.count':u'1',
  ...     'form.widgets.listOfObject.0.widgets.foofield':u'66',
  ...     'form.widgets.listOfObject.0.widgets.barfield':u'99',
  ...     'form.widgets.listOfObject.0-empty-marker':u'1',
  ...     'form.widgets.name':u'first',
  ...     'form.buttons.add':'Add'})
  >>> myaddform.request = request

Update the form with the request:

  >>> myaddform.update()
  MyAddForm.create
  {'listOfObject': [<z3c.form.testing.MySubObjectMulti ...],
   'name': 'first'}


Wow, it got added:

  >>> root['first']
  <z3c.form.testing.MyMultiObject object at ...>

  >>> root['first'].listOfObject
  [<z3c.form.testing.MySubObjectMulti object at ...>]

Field values need to be right:

  >>> root['first'].listOfObject[0].foofield
  66
  >>> root['first'].listOfObject[0].barfield
  99

Let's see our event log:

  >>> len(eventlog)
  6

((why is IMySubObjectMulti created twice???))

  >>> printEvents()
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass z3c.form.testing.IMySubObjectMulti>
  ['barfield', 'foofield']
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass z3c.form.testing.IMySubObjectMulti>
  ['barfield', 'foofield']
  <zope...ObjectCreatedEvent object at ...>
  <zope...contained.ContainerModifiedEvent object at ...>


  >>> eventlog=[]

Let's try to edit that newly added object:

  >>> class MyEditForm(form.EditForm):
  ...     fields = field.Fields(IMyMultiObject)

  >>> editform = MyEditForm(root['first'], TestRequest())
  >>> addTemplate(editform)
  >>> editform.update()

Watch for the widget values in the HTML:

  >>> print(editform.render())
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <form action=".">
        <div class="row">
          <label for="form-widgets-listOfObject">My list field</label>
          <div class="multi-widget required">
            <div class="row" id="form-widgets-listOfObject-0-row">
              <div class="label">
                <label for="form-widgets-listOfObject-0">
                  <span>my object widget</span>
                  <span class="required">*</span>
                </label>
              </div>
              <div class="widget">
                <div class="multi-widget-checkbox">
                  <input class="multi-widget-checkbox checkbox-widget"
                         id="form-widgets-listOfObject-0-remove"
                         name="form.widgets.listOfObject.0.remove"
                         type="checkbox" value="1">
                </div>
                <div class="multi-widget-input">
                  <div class="object-widget required">
                    <div class="label">
                      <label for="form-widgets-listOfObject-0-widgets-foofield">
                        <span>My foo field</span>
                        <span class="required">*</span>
                      </label>
                    </div>
                    <div class="widget">
                      <input class="text-widget required int-field"
                             id="form-widgets-listOfObject-0-widgets-foofield"
                             name="form.widgets.listOfObject.0.widgets.foofield"
                             type="text" value="66">
                    </div>
                    <div class="label">
                      <label for="form-widgets-listOfObject-0-widgets-barfield">
                        <span>My dear bar</span>
                      </label>
                    </div>
                    <div class="widget">
                      <input class="text-widget int-field"
                             id="form-widgets-listOfObject-0-widgets-barfield"
                             name="form.widgets.listOfObject.0.widgets.barfield"
                             type="text" value="99">
                    </div>
                    <input name="form.widgets.listOfObject.0-empty-marker"
                           type="hidden" value="1">
                  </div>
                </div>
              </div>
            </div>
            <div class="buttons">
              <input class="submit-widget button-field"
                     id="form-widgets-listOfObject-buttons-add"
                     name="form.widgets.listOfObject.buttons.add"
                     type="submit" value="Add">
              <input class="submit-widget button-field"
                     id="form-widgets-listOfObject-buttons-remove"
                     name="form.widgets.listOfObject.buttons.remove"
                     type="submit" value="Remove selected">
            </div>
          </div>
          <input name="form.widgets.listOfObject.count" type="hidden" value="1">
        </div>
        <div class="row">
          <label for="form-widgets-name">name</label>
          <input class="text-widget required textline-field"
                 id="form-widgets-name" name="form.widgets.name"
                 type="text" value="first">
        </div>
        <div class="action">
          <input class="submit-widget button-field" id="form-buttons-apply"
                 name="form.buttons.apply" type="submit" value="Apply">
        </div>
      </form>
    </body>
  </html>

Let's modify the values:

  >>> request = TestRequest(form={
  ...     'form.widgets.listOfObject.count':u'1',
  ...     'form.widgets.listOfObject.0.widgets.foofield':u'43',
  ...     'form.widgets.listOfObject.0.widgets.barfield':u'55',
  ...     'form.widgets.listOfObject.0-empty-marker':u'1',
  ...     'form.widgets.name':u'first',
  ...     'form.buttons.apply':'Apply'})

They are still the same:

  >>> root['first'].listOfObject[0].foofield
  66
  >>> root['first'].listOfObject[0].barfield
  99

  >>> editform.request = request
  >>> editform.update()

Until we have updated the form:

  >>> root['first'].listOfObject[0].foofield
  43
  >>> root['first'].listOfObject[0].barfield
  55

Let's see our event log:

  >>> len(eventlog)
  5

((TODO: now this is real crap here, why is IMySubObjectMulti created 3 times???))

  >>> printEvents()
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass z3c.form.testing.IMySubObjectMulti>
  ['barfield', 'foofield']
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass z3c.form.testing.IMySubObjectMulti>
  ['barfield', 'foofield']
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass z3c.form.testing.IMyMultiObject>
  ['listOfObject']

  >>> eventlog=[]


After the update the form says that the values got updated and renders the new
values:

  >>> print(editform.render())
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <i>Data successfully updated.</i>
      <form action=".">
        <div class="row">
          <label for="form-widgets-listOfObject">My list field</label>
          <div class="multi-widget required">
            <div class="row" id="form-widgets-listOfObject-0-row">
              <div class="label">
                <label for="form-widgets-listOfObject-0">
                  <span>my object widget</span>
                  <span class="required">*</span>
                </label>
              </div>
              <div class="widget">
                <div class="multi-widget-checkbox">
                  <input class="multi-widget-checkbox checkbox-widget"
                         id="form-widgets-listOfObject-0-remove"
                         name="form.widgets.listOfObject.0.remove"
                         type="checkbox" value="1">
                </div>
                <div class="multi-widget-input">
                  <div class="object-widget required">
                    <div class="label">
                      <label for="form-widgets-listOfObject-0-widgets-foofield">
                        <span>My foo field</span>
                        <span class="required">*</span>
                      </label>
                    </div>
                    <div class="widget">
                      <input class="text-widget required int-field"
                             id="form-widgets-listOfObject-0-widgets-foofield"
                             name="form.widgets.listOfObject.0.widgets.foofield"
                             type="text" value="43">
                    </div>
                    <div class="label">
                      <label for="form-widgets-listOfObject-0-widgets-barfield">
                        <span>My dear bar</span>
                      </label>
                    </div>
                    <div class="widget">
                      <input class="text-widget int-field"
                             id="form-widgets-listOfObject-0-widgets-barfield"
                             name="form.widgets.listOfObject.0.widgets.barfield"
                             type="text" value="55">
                    </div>
                    <input name="form.widgets.listOfObject.0-empty-marker"
                           type="hidden" value="1">
                  </div>
                </div>
              </div>
            </div>
            <div class="buttons">
              <input class="submit-widget button-field"
                     id="form-widgets-listOfObject-buttons-add"
                     name="form.widgets.listOfObject.buttons.add" type="submit"
                     value="Add">
              <input class="submit-widget button-field"
                     id="form-widgets-listOfObject-buttons-remove"
                     name="form.widgets.listOfObject.buttons.remove"
                     type="submit" value="Remove selected">
            </div>
          </div>
          <input name="form.widgets.listOfObject.count" type="hidden" value="1">
        </div>
        <div class="row">
          <label for="form-widgets-name">name</label>
          <input class="text-widget required textline-field"
                 id="form-widgets-name" name="form.widgets.name"
                 type="text" value="first">
        </div>
        <div class="action">
          <input class="submit-widget button-field" id="form-buttons-apply"
                 name="form.buttons.apply" type="submit" value="Apply">
        </div>
      </form>
    </body>
  </html>


Let's see if the widget keeps the old object on editing:

We add a special property to keep track of the object:

  >>> root['first'].listOfObject[0].__marker__ = "ThisMustStayTheSame"

  >>> root['first'].listOfObject[0].foofield
  43
  >>> root['first'].listOfObject[0].barfield
  55

Let's modify the values:

  >>> request = TestRequest(form={
  ...     'form.widgets.listOfObject.count':u'1',
  ...     'form.widgets.listOfObject.0.widgets.foofield':u'666',
  ...     'form.widgets.listOfObject.0.widgets.barfield':u'999',
  ...     'form.widgets.listOfObject.0-empty-marker':u'1',
  ...     'form.widgets.name':u'first',
  ...     'form.buttons.apply':'Apply'})

  >>> editform.request = request

  >>> editform.update()

Let's check what are ther esults of the update:

  >>> root['first'].listOfObject[0].foofield
  666
  >>> root['first'].listOfObject[0].barfield
  999

((TODO: bummer... we can't keep the old object))

  #>>> root['first'].listOfObject[0].__marker__
  #'ThisMustStayTheSame'


Let's make a nasty error, by typing 'bad' instead of an integer:

  >>> request = TestRequest(form={
  ...     'form.widgets.listOfObject.count':u'1',
  ...     'form.widgets.listOfObject.0.widgets.foofield':u'99',
  ...     'form.widgets.listOfObject.0.widgets.barfield':u'bad',
  ...     'form.widgets.listOfObject.0-empty-marker':u'1',
  ...     'form.widgets.name':u'first',
  ...     'form.buttons.apply':'Apply'})

  >>> editform.request = request
  >>> eventlog=[]
  >>> editform.update()

Eventlog must be clean:

  >>> len(eventlog)
  2

((TODO: bummer... who creates those 2 objects???))

  >>> printEvents()
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectCreatedEvent object at ...>


Watch for the error message in the HTML:
it has to appear at the field itself and at the top of the form:
((not nice: at the top ``Object is of wrong type.`` appears))

  >>> print(editform.render())
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <i>There were some errors.</i>
      <ul>
        <li>
        My list field:
          <div class="error">The entered value is not a valid integer literal.</div>
        </li>
      </ul>
      <form action=".">
        <div class="row">
          <b>
            <div class="error">The entered value is not a valid integer literal.</div>
          </b>
          <label for="form-widgets-listOfObject">My list field</label>
          <div class="multi-widget required">
            <div class="row" id="form-widgets-listOfObject-0-row">
              <div class="label">
                <label for="form-widgets-listOfObject-0">
                  <span>my object widget</span>
                  <span class="required">*</span>
                </label>
              </div>
              <div class="error">The entered value is not a valid integer literal.</div>
              <div class="widget">
                <div class="multi-widget-checkbox">
                  <input class="multi-widget-checkbox checkbox-widget"
                         id="form-widgets-listOfObject-0-remove"
                         name="form.widgets.listOfObject.0.remove"
                         type="checkbox" value="1">
                </div>
                <div class="multi-widget-input">
                  <div class="object-widget required">
                    <div class="label">
                      <label for="form-widgets-listOfObject-0-widgets-foofield">
                        <span>My foo field</span>
                        <span class="required">*</span>
                      </label>
                    </div>
                    <div class="widget">
                      <input class="text-widget required int-field"
                             id="form-widgets-listOfObject-0-widgets-foofield"
                             name="form.widgets.listOfObject.0.widgets.foofield"
                             type="text" value="99">
                    </div>
                    <div class="label">
                      <label for="form-widgets-listOfObject-0-widgets-barfield">
                        <span>My dear bar</span>
                      </label>
                    </div>
                    <div class="error">The entered value is not a valid integer literal.</div>
                    <div class="widget">
                      <input class="text-widget int-field"
                             id="form-widgets-listOfObject-0-widgets-barfield"
                             name="form.widgets.listOfObject.0.widgets.barfield"
                             type="text" value="bad">
                    </div>
                    <input name="form.widgets.listOfObject.0-empty-marker" type="hidden" value="1">
                  </div>
                </div>
              </div>
            </div>
            <div class="buttons">
              <input class="submit-widget button-field"
                     id="form-widgets-listOfObject-buttons-add"
                     name="form.widgets.listOfObject.buttons.add"
                     type="submit" value="Add">
              <input class="submit-widget button-field"
                     id="form-widgets-listOfObject-buttons-remove"
                     name="form.widgets.listOfObject.buttons.remove"
                     type="submit" value="Remove selected">
            </div>
          </div>
          <input name="form.widgets.listOfObject.count" type="hidden" value="1">
        </div>
        <div class="row">
          <label for="form-widgets-name">name</label>
          <input class="text-widget required textline-field"
                 id="form-widgets-name" name="form.widgets.name"
                 type="text" value="first">
        </div>
        <div class="action">
          <input class="submit-widget button-field" id="form-buttons-apply"
                 name="form.buttons.apply" type="submit" value="Apply">
        </div>
      </form>
    </body>
  </html>

The object values must stay at the old ones:

  >>> root['first'].listOfObject[0].foofield
  666
  >>> root['first'].listOfObject[0].barfield
  999



Simple but often used use-case is the display form:

  >>> editform = MyEditForm(root['first'], TestRequest())
  >>> addTemplate(editform)
  >>> editform.mode = interfaces.DISPLAY_MODE
  >>> editform.update()
  >>> print(editform.render())
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <form action=".">
        <div class="row">
          <label for="form-widgets-listOfObject">My list field</label>
          <div class="multi-widget" id="form-widgets-listOfObject">
            <div class="row" id="form-widgets-listOfObject-0-row">
              <div class="label">
                <label for="form-widgets-listOfObject-0">
                  <span>my object widget</span>
                  <span class="required">*</span>
                </label>
              </div>
              <div class="widget">
                <div class="multi-widget-display">
                  <div class="object-widget">
                    <div class="label">
                      <label for="form-widgets-listOfObject-0-widgets-foofield">
                        <span>My foo field</span>
                        <span class="required">*</span>
                      </label>
                    </div>
                    <div class="widget">
                      <span class="text-widget int-field"
                            id="form-widgets-listOfObject-0-widgets-foofield">666</span>
                    </div>
                    <div class="label">
                      <label for="form-widgets-listOfObject-0-widgets-barfield">
                        <span>My dear bar</span>
                      </label>
                    </div>
                    <div class="widget">
                      <span class="text-widget int-field"
                            id="form-widgets-listOfObject-0-widgets-barfield">999</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="row">
          <label for="form-widgets-name">name</label>
          <span class="text-widget textline-field"
                id="form-widgets-name">first</span>
        </div>
        <div class="action">
          <input class="submit-widget button-field"
                 id="form-buttons-apply" name="form.buttons.apply"
                 type="submit" value="Apply">
        </div>
      </form>
    </body>
  </html>
