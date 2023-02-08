=======
Buttons
=======

Buttons are a method to declare actions for a form. Like fields describe
widgets within a form, buttons describe actions. The symmetry goes even
further; like fields, buttons are schema fields within schema. When the form
is instantiated and updated, the buttons are converted to actions.

  >>> from z3c.form import button


Schema Defined Buttons
----------------------

Let's now create a schema that describes the buttons of a form. Having button
schemas allows one to more easily reuse button declarations and to group them
logically. ``Button`` objects are just a simple extension to ``Field``
objects, so they behave identical within a schema:

  >>> import zope.interface
  >>> class IButtons(zope.interface.Interface):
  ...     apply = button.Button(title='Apply')
  ...     cancel = button.Button(title='Cancel')

In reality, only the title and name is relevant. Let's now create a form that
provides those buttons.

  >>> from z3c.form import interfaces
  >>> @zope.interface.implementer(
  ...     interfaces.IButtonForm, interfaces.IHandlerForm)
  ... class Form(object):
  ...     buttons = button.Buttons(IButtons)
  ...     prefix = 'form'
  ...
  ...     @button.handler(IButtons['apply'])
  ...     def apply(self, action):
  ...         print('successfully applied')
  ...
  ...     @button.handler(IButtons['cancel'])
  ...     def cancel(self, action):
  ...         self.request.response.redirect('index.html')

Let's now create an action manager for the button manager in the form. To do
that we first need a request and a form instance:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> form = Form()

We also have to register a button action factory for the buttons:

  >>> zope.component.provideAdapter(
  ...     button.ButtonAction, provides=interfaces.IButtonAction)

Action managers are instantiated using the form, request, and
context/content. A special button-action-manager implementation is available
in the ``button`` package:

  >>> actions = button.ButtonActions(form, request, None)
  >>> actions.update()

Once the action manager is updated, the buttons should be available as
actions:

  >>> list(actions.keys())
  ['apply', 'cancel']

  >>> actions['apply']
  <ButtonAction 'form.buttons.apply' 'Apply'>

It is possible to customize how a button is transformed into an action
by registering an adapter for the request and the button that provides
``IButtonAction``.

  >>> import zope.component
  >>> from zope.publisher.interfaces.browser import IBrowserRequest
  >>> class CustomButtonAction(button.ButtonAction):
  ...     """Custom Button Action Class."""

  >>> zope.component.provideAdapter(
  ...     CustomButtonAction, provides=interfaces.IButtonAction)

Now if we rerun update we will get this other ButtonAction
implementation. Note, there are two strategies what now could happen. We can
remove the existing action and get the new adapter based action or we can
reuse the existing action. Since the ButtonActions class offers an API for
remove existing actions, we reuse the existing action because it very uncommon
to replace existing action during an for update call with an adapter. If
someone really will add an action adapter during process time via directly
provided interface, he is also responsible for remove existing actions.

As you can see we still will get the old button action if we only call update:

  >>> actions.update()
  >>> list(actions.keys())
  ['apply', 'cancel']

  >>> actions['apply']
  <ButtonAction 'form.buttons.apply' 'Apply'>

This means we have to remove the previous action before we call update:

  >>> del actions['apply']
  >>> actions.update()

Make sure we do not append a button twice to the key and value lists by calling
update twice:

  >>> list(actions.keys())
  ['apply', 'cancel']

  >>> actions['apply']
  <CustomButtonAction 'form.buttons.apply' 'Apply'>

Alternatively, customize an individual button by setting its
actionFactory attribute.

  >>> def customButtonActionFactory(request, field):
  ...     print("This button factory creates a button only once.")
  ...     button = CustomButtonAction(request, field)
  ...     button.css = "happy"
  ...     return button

  >>> form.buttons['apply'].actionFactory = customButtonActionFactory

Again, remove the old button action befor we call update:

  >>> del actions['apply']
  >>> actions.update()
  This button factory creates a button only once.

  >>> actions.update()
  >>> actions['apply'].css
  'happy'

Since we only create a button once from an adapter or a factory, we can change
the button attributes without to lose changes:

  >>> actions['apply'].css = 'very happy'
  >>> actions['apply'].css
  'very happy'

  >>> actions.update()
  >>> actions['apply'].css
  'very happy'

But let's not digress too much and get rid of this customization

  >>> form.buttons['apply'].actionFactory = None
  >>> actions.update()

Button actions are locations:

  >>> apply = actions['apply']
  >>> apply.__name__
  'apply'
  >>> apply.__parent__
  <ButtonActions None>

A button action is also a submit widget. The attributes translate as follows:

  >>> interfaces.ISubmitWidget.providedBy(apply)
  True

  >>> apply.value == apply.title
  True
  >>> apply.id == apply.name.replace('.', '-')
  True

Next we want to display our button actions. To be able to do this, we have to
register a template for the submit widget:

  >>> from z3c.form import testing, widget
  >>> templatePath = testing.getPath('submit_input.pt')
  >>> factory = widget.WidgetTemplateFactory(templatePath, 'text/html')

  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, TestRequest, None, None,
  ...      interfaces.ISubmitWidget),
  ...     IPageTemplate, name='input')

A widget template has many discriminators: context, request, view, field, and
widget. We can now render each action:

  >>> print(actions['apply'].render())
  <input type="submit" id="form-buttons-apply"
         name="form.buttons.apply" class="submit-widget button-field"
         value="Apply" />

So displaying is nice, but how do button handlers get executed? The action
manager provides attributes and method to check whether actions were
executed. Initially there are no executed actions:

  >>> list(actions.executedActions)
  []

So in this case executing the actions does not do anything:

  >>> actions.execute()

But if the request contains the information that the button was pressed, the
execution works:

  >>> request = TestRequest(form={'form.buttons.apply': 'Apply'})

  >>> actions = button.ButtonActions(form, request, None)
  >>> actions.update()
  >>> actions.execute()

Aehm, something should have happened. But in order for the system to look at
the handlers declared in the form, a special action handler has to be
registered with the system:

  >>> zope.component.provideAdapter(button.ButtonActionHandler)

And voila, the execution works:

  >>> actions.execute()
  successfully applied

Finally, if there is no handler for a button, then the button click is
silently ignored:

  >>> form.handlers = button.Handlers()
  >>> actions.execute()

While this might seem awkward at first, this is an intended feature. Sometimes
there are several sub-forms that listen to a particular button and one form or
another might simply not care about the button at all and not provide a
handler.


In-Form Button Declarations
---------------------------

Some readers might find it cumbersome to declare a full schema just to create
some buttons. A faster method is to write simple arguments to the button
manager:

  >>> @zope.interface.implementer(
  ...     interfaces.IButtonForm, interfaces.IHandlerForm)
  ... class Form(object):
  ...     buttons = button.Buttons(
  ...         button.Button('apply', title='Apply'))
  ...     prefix = 'form.'
  ...
  ...     @button.handler(buttons['apply'])
  ...     def apply(self, action):
  ...         print('successfully applied')

The first argument of the ``Button`` class constructor is the name of the
button. Optionally, this can also be one of the following keyword arguments:

  >>> button.Button(name='apply').__name__
  'apply'
  >>> button.Button(__name__='apply').__name__
  'apply'

If no name is specified, the button will not have a name immediately, ...

  >>> button.Button(title='Apply').__name__
  ''

because if the button is created within an interface, the name is assigned
later:

  >>> class IActions(zope.interface.Interface):
  ...    apply = button.Button(title='Apply')

  >>> IActions['apply'].__name__
  'apply'

However, once the button is added to a button manager, a name will be
assigned:

  >>> btns = button.Buttons(button.Button(title='Apply'))
  >>> btns['apply'].__name__
  'apply'

  >>> btns = button.Buttons(button.Button(title='Apply and more'))
  >>> btns['4170706c7920616e64206d6f7265'].__name__
  '4170706c7920616e64206d6f7265'

This declaration behaves identical to the one before:

  >>> form = Form()
  >>> request = TestRequest()

  >>> actions = button.ButtonActions(form, request, None)
  >>> actions.update()
  >>> actions.execute()

When sending in the right information, the actions are executed:

  >>> request = TestRequest(form={'form.buttons.apply': 'Apply'})
  >>> actions = button.ButtonActions(form, request, None)
  >>> actions.update()
  >>> actions.execute()
  successfully applied

An even simpler method -- resembling closest the API provided by formlib -- is
to create the button and handler at the same time:

  >>> @zope.interface.implementer(
  ...     interfaces.IButtonForm, interfaces.IHandlerForm)
  ... class Form(object):
  ...     prefix = 'form.'
  ...
  ...     @button.buttonAndHandler('Apply')
  ...     def apply(self, action):
  ...         print('successfully applied')

In this case the ``buttonAndHandler`` decorator creates a button and a handler
for it. By default the name is computed from the title of the button, which is
required. All (keyword) arguments are forwarded to the button
constructor. Let's now render the form:

  >>> request = TestRequest(form={'form.buttons.apply': 'Apply'})
  >>> actions = button.ButtonActions(form, request, None)
  >>> actions.update()
  >>> actions.execute()
  successfully applied

If the title is a more complex string, then the name of the button becomes a
hex-encoded string:

  >>> class Form(object):
  ...
  ...     @button.buttonAndHandler('Apply and Next')
  ...     def apply(self, action):
  ...         print('successfully applied')

  >>> list(Form.buttons.keys())
  ['4170706c7920616e64204e657874']

Of course, you can use the ``__name__`` argument to specify a name
yourself. The decorator, however, also allows the keyword ``name``:

  >>> class Form(object):
  ...
  ...     @button.buttonAndHandler('Apply and Next', name='applyNext')
  ...     def apply(self, action):
  ...         print('successfully applied')

  >>> list(Form.buttons.keys())
  ['applyNext']

This helper function also supports a keyword argument ``provides``, which
allows the developer to specify a sequence of interfaces that the generated
button should directly provide. Those provided interfaces can be used for a
multitude of things, including handler discrimination and UI layout:

  >>> class IMyButton(zope.interface.Interface):
  ...    pass

  >>> class Form(object):
  ...
  ...     @button.buttonAndHandler('Apply', provides=(IMyButton,))
  ...     def apply(self, action):
  ...         print('successfully applied')

  >>> IMyButton.providedBy(Form.buttons['apply'])
  True


Button Conditions
-----------------

Sometimes it is desirable to only show a button when a certain condition is
fulfilled. The ``Button`` field supports conditions via a simple argument. The
``condition`` argument must be a callable taking the form as argument and
returning a truth-value. If the condition is not fulfilled, the button will not
be converted to an action:

  >>> class Form(object):
  ...     prefix = 'form'
  ...     showApply = True
  ...
  ...     @button.buttonAndHandler(
  ...         'Apply', condition=lambda form: form.showApply)
  ...     def apply(self, action):
  ...         print('successfully applied')

In this case a form variable specifies the availability. Initially the button
is available as action:

  >>> myform = Form()
  >>> actions = button.ButtonActions(myform, TestRequest(), None)
  >>> actions.update()
  >>> list(actions.keys())
  ['apply']

If we set the show-apply attribute to false, the action will not be available.

  >>> myform.showApply = False
  >>> actions.update()
  >>> list(actions.keys())
  []
  >>> list(actions.values())
  []

This feature is very helpful in multi-forms and wizards.


Customizing the Title
---------------------

As for widgets, it is often desirable to change attributes of the button
actions without altering any original code. Again we will be using attribute
value adapters to complete the task. Originally, our title is as follows:

  >>> myform = Form()
  >>> actions = button.ButtonActions(myform, TestRequest(), None)
  >>> actions.update()
  >>> actions['apply'].title
  'Apply'

Let's now create a custom label for the action:

  >>> ApplyLabel = button.StaticButtonActionAttribute(
  ...     'Apply now', button=myform.buttons['apply'])
  >>> zope.component.provideAdapter(ApplyLabel, name='title')

Once the button action manager is updated, the new title is chosen:

  >>> actions.update()
  >>> actions['apply'].title
  'Apply now'


The Button Manager
------------------

The button manager contains several additional API methods that make the
management of buttons easy.

First, you are able to add button managers:

  >>> bm1 = button.Buttons(IButtons)
  >>> bm2 = button.Buttons(button.Button('help', title='Help'))

  >>> bm1 + bm2
  Buttons([...])
  >>> list(bm1 + bm2)
  ['apply', 'cancel', 'help']

The result of the addition is another button manager. Also note that the order
of the buttons is preserved throughout the addition. Adding anything else is
not well-defined:

  >>> bm1 + 1
  Traceback (most recent call last):
  ...
  TypeError: unsupported operand type(s) for +: 'Buttons' and 'int'

Second, you can select the buttons in a particular order:

  >>> bm = bm1 + bm2
  >>> list(bm)
  ['apply', 'cancel', 'help']

  >>> list(bm.select('help', 'apply', 'cancel'))
  ['help', 'apply', 'cancel']

The ``select()`` method can also be used to eliminate another button:

  >>> list(bm.select('help', 'apply'))
  ['help', 'apply']

Of course, in the example above we eliminated one and reorganized the buttons.

Third, you can omit one or more buttons:

  >>> list(bm.omit('cancel'))
  ['apply', 'help']

Finally, while the constructor is very flexible, you cannot just pass in
anything:

  >>> button.Buttons(1, 2)
  Traceback (most recent call last):
  ...
  TypeError: ('Unrecognized argument type', 1)

When creating a new form derived from another, you often want to keep existing
buttons and add new ones. In order not to change the super-form class, you need
to copy the button manager:

  >>> list(bm.keys())
  ['apply', 'cancel', 'help']
  >>> list(bm.copy().keys())
  ['apply', 'cancel', 'help']


The Handlers Object
-------------------

All handlers of a form are collected in the ``handlers`` attribute, which is a
``Handlers`` instance:

  >>> isinstance(form.handlers, button.Handlers)
  True
  >>> form.handlers
  <Handlers [<Handler for <Button 'apply' 'Apply'>>]>

Internally the object uses an adapter registry to manage the handlers for
buttons. If a handler is registered for a button, it simply behaves as an
instance-adapter.

The object itself is pretty simple. You can get a handler as follows:

  >>> apply = form.buttons['apply']
  >>> form.handlers.getHandler(apply)
  <Handler for <Button 'apply' 'Apply'>>

But you can also register handlers for groups of buttons, either by interface
or class:

  >>> class SpecialButton(button.Button):
  ...     pass

  >>> def handleSpecialButton(form, action):
  ...     return 'Special button action'

  >>> form.handlers.addHandler(
  ...     SpecialButton, button.Handler(SpecialButton, handleSpecialButton))

  >>> form.handlers
  <Handlers
      [<Handler for <Button 'apply' 'Apply'>>,
       <Handler for <class 'SpecialButton'>>]>

Now all special buttons should use that handler:

  >>> button1 = SpecialButton(name='button1', title='Button 1')
  >>> button2 = SpecialButton(name='button2', title='Button 2')

  >>> form.handlers.getHandler(button1)(form, None)
  'Special button action'
  >>> form.handlers.getHandler(button2)(form, None)
  'Special button action'

However, registering a more specific handler for button 1 will override the
general handler:

  >>> def handleButton1(form, action):
  ...     return 'Button 1 action'

  >>> form.handlers.addHandler(
  ...     button1, button.Handler(button1, handleButton1))

  >>> form.handlers.getHandler(button1)(form, None)
  'Button 1 action'
  >>> form.handlers.getHandler(button2)(form, None)
  'Special button action'

You can also add handlers objects:

  >>> handlers2 = button.Handlers()

  >>> button3 = SpecialButton(name='button3', title='Button 3')
  >>> handlers2.addHandler(
  ...     button3, button.Handler(button3, None))

  >>> form.handlers + handlers2
  <Handlers
      [<Handler for <Button 'apply' 'Apply'>>,
       <Handler for <class 'SpecialButton'>>,
       <Handler for <SpecialButton 'button1' 'Button 1'>>,
       <Handler for <SpecialButton 'button3' 'Button 3'>>]>

However, adding other components is not supported:

  >>> form.handlers + 1
  Traceback (most recent call last):
  ...
  NotImplementedError

The handlers also provide a method to copy the handlers to a new instance:

  >>> copy = form.handlers.copy()
  >>> isinstance(copy, button.Handlers)
  True
  >>> copy is form.handlers
  False

This is commonly needed when one wants to extend the handlers of a super-form.


Image Buttons
-------------

A special type of button is the image button. Instead of creating a "submit"-
or "button"-type input, an "image" button is created. An image button is a
simple extension of a button, requiring an `image` argument to the constructor:

  >>> imgSubmit = button.ImageButton(
  ...     name='submit',
  ...     title='Submit',
  ...     image='submit.png')
  >>> imgSubmit
  <ImageButton 'submit' 'submit.png'>

Some browsers do not submit the value of the input, but only the coordinates
of the image where the mouse click occurred. Thus we also need a special
button action:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> imgSubmitAction = button.ImageButtonAction(request, imgSubmit)
  >>> imgSubmitAction
  <ImageButtonAction 'submit' 'Submit'>

Initially, we did not click on the image:

  >>> imgSubmitAction.isExecuted()
  False

Now the button is clicked:

  >>> request = TestRequest(form={'submit.x': '3', 'submit.y': '4'})

  >>> imgSubmitAction = button.ImageButtonAction(request, imgSubmit)
  >>> imgSubmitAction.isExecuted()
  True

The "image" type of the "input"-element also requires there to be a `src`
attribute, which is the URL to the image to be used. The attribute is also
supported by the Python API. However, in order for the attribute to work, the
image must be available as a resource, so let's do that now:

  # Traversing setup
  >>> from zope.traversing import testing
  >>> testing.setUp()

  # Resource namespace
  >>> import zope.component
  >>> from zope.traversing.interfaces import ITraversable
  >>> from zope.traversing.namespace import resource
  >>> zope.component.provideAdapter(
  ...     resource, (None,), ITraversable, name="resource")
  >>> zope.component.provideAdapter(
  ...     resource, (None, None), ITraversable, name="resource")

  # New absolute URL adapter for resources, if available
  >>> from zope.browserresource.resource import AbsoluteURL
  >>> zope.component.provideAdapter(AbsoluteURL)

  # Register the "submit.png" resource
  >>> from zope.browserresource.resource import Resource
  >>> testing.browserResource('submit.png', Resource)

Now the attribute can be called:

  >>> imgSubmitAction.src
  'http://127.0.0.1/@@/submit.png'
