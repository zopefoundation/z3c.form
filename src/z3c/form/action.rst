===============
Action Managers
===============

Action managers are components that manage all actions that can be taken
within a view, usually a form. They are also responsible for executing actions
when asked to do so.

Creating an action manager
--------------------------

An action manager is a form-related adapter that has the following
discriminator: form, request, and content. While there is a base
implementation for an action manager, the ``action`` module does not provide a
full implementation.

So we first have to build a simple implementation based on the ``Actions``
manager base class which allows us to add actions. Note that the following
implementation is for demonstration purposes. If you want to see a real action
manager implementation, then have a look at ``ButtonActions``. Let's now
implement our simple action manager:

  >>> from z3c.form import action
  >>> class SimpleActions(action.Actions):
  ...     """Simple sample."""
  ...
  ...     def append(self, name, action):
  ...         """See z3c.form.interfaces.IActions."""
  ...         self[name] = action

Before we can initialise the action manager, we have to create instances for
our three discriminators, just enough to get it working:

  >>> import zope.interface
  >>> from z3c.form import interfaces
  >>> @zope.interface.implementer(interfaces.IForm)
  ... class Form(object):
  ...     pass
  >>> form = Form()

  >>> @zope.interface.implementer(zope.interface.Interface)
  ... class Content(object):
  ...     pass
  >>> content = Content()

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()

We are now ready to create the action manager, which is a simple
triple-adapter:

  >>> manager = SimpleActions(form, request, content)
  >>> manager
  <SimpleActions None>

As we can see in the manager representation above, the name of the manager is
``None``, since we have not specified one:

  >>> manager.__name__ = 'example'
  >>> manager
  <SimpleActions 'example'>


Managing and Accessing Actions
------------------------------

Initially there are no actions in the manager:

  >>> list(manager.keys())
  []

Our simple implementation of has an additional ``append()`` method, which we
will use to add actions:

  >>> apply = action.Action(request, 'Apply')
  >>> manager.append(apply.name, apply)

The action is added immediately:

  >>> list(manager.keys())
  ['apply']

However, you should not rely on it being added, and always update the manager
once all actions were defined:

  >>> manager.update()

Note: If the title of the action is a more complex unicode string and no name
is specified for the action, then a hexadecimal name is created from the
title:

  >>> action.Action(request, 'Apply Now!').name
  '4170706c79204e6f7721'

Since the action manager is an enumerable mapping, ...

  >>> from zope.interface.common.mapping import IEnumerableMapping
  >>> IEnumerableMapping.providedBy(manager)
  True

there are several API methods available:

  >>> manager['apply']
  <Action 'apply' 'Apply'>
  >>> manager['foo']
  Traceback (most recent call last):
  ...
  KeyError: 'foo'

  >>> manager.get('apply')
  <Action 'apply' 'Apply'>
  >>> manager.get('foo', 'default')
  'default'

  >>> 'apply' in manager
  True
  >>> 'foo' in manager
  False

  >>> list(manager.values())
  [<Action 'apply' 'Apply'>]

  >>> list(manager.items())
  [('apply', <Action 'apply' 'Apply'>)]

  >>> len(manager)
  1


Executing actions
-----------------

When an action is executed, an execution adapter is looked up. If there is no
adapter, nothing happens. So let's create a request that submits the apply
button:

  >>> request = TestRequest(form={'apply': 'Apply'})
  >>> manager = SimpleActions(form, request, content)

We also want to have two buttons in this case, so that we can ensure that only
one is executed:

  >>> apply = action.Action(request, 'Apply')
  >>> manager.append(apply.name, apply)

  >>> cancel = action.Action(request, 'Cancel')
  >>> manager.append(cancel.name, cancel)
  >>> manager.update()

Now that the manager is updated, we can ask it for the "executed" actions:

  >>> manager.executedActions
  [<Action 'apply' 'Apply'>]

Executing the actions does nothing, because there are no handlers yet:

  >>> manager.execute()


Let's now register an action handler that listens to the "Apply" action. An
action handler has four discriminators: form, request, content, and
action. All those objects are available to the handler under those names. When
using the base action handler from the ``action`` module, ``__call__()`` is
the only method that needs to be implemented:

  >>> from z3c.form import util

  >>> class SimpleActionHandler(action.ActionHandlerBase):
  ...     zope.component.adapts(
  ...         None, TestRequest, None, util.getSpecification(apply))
  ...     def __call__(self):
  ...         print('successfully applied')

  >>> zope.component.provideAdapter(SimpleActionHandler)

As you can see, we registered the action specifically for the apply
action. Now, executing the actions calls this handler:

  >>> manager.execute()
  successfully applied

Of course it only works for the "Apply" action and not ""Cancel":

  >>> request = TestRequest(form={'cancel': 'Cancel'})
  >>> manager.request = apply.request = cancel.request = request
  >>> manager.execute()

Further, when a handler is successfully executed, an event is sent out, so
let's register an event handler:

  >>> eventlog = []
  >>> @zope.component.adapter(interfaces.IActionEvent)
  ... def handleEvent(event):
  ...     eventlog.append(event)

  >>> zope.component.provideHandler(handleEvent)

Let's now execute the "Apply" action again:

  >>> request = TestRequest(form={'apply': 'Apply'})
  >>> manager.request = apply.request = cancel.request = request
  >>> manager.execute()
  successfully applied

  >>> eventlog[-1]
  <ActionSuccessful for <Action 'apply' 'Apply'>>

Action handlers, however, can also raise action errors. These action errors
are caught and an event is created notifying the system of the problem. The
error is not further propagated. Other errors are not handled by the system to
avoid hiding real failures of the code.

Let's see how action errors can be used by implementing a handler for the
cancel action:

  >>> class ErrorActionHandler(action.ActionHandlerBase):
  ...     zope.component.adapts(
  ...         None, TestRequest, None, util.getSpecification(cancel))
  ...     def __call__(self):
  ...         raise interfaces.ActionExecutionError(
  ...             zope.interface.Invalid('Something went wrong'))

  >>> zope.component.provideAdapter(ErrorActionHandler)

As you can see, the action execution error wraps some other execption, in this
case a simple invalid error.

Executing the "Cancel" action now produces the action error event:

  >>> request = TestRequest(form={'cancel': 'Cancel'})
  >>> manager.request = apply.request = cancel.request = request
  >>> manager.execute()

  >>> eventlog[-1]
  <ActionErrorOccurred for <Action 'cancel' 'Cancel'>>

  >>> eventlog[-1].error
  <ActionExecutionError wrapping ...Invalid...>
