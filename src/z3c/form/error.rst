===========
Error Views
===========

Error views are looked up every time a validation error occurs during data
extraction and/or validation. Unfortunately, it was often hard to adjust error
messages based on specific situations. The error view implementation in this
package is designed to provide several high-level features that make
customizing error messages easier.

  >>> from z3c.form import error


Creating and Displaying the Default Error View
----------------------------------------------

Let's create an error view message for the ``TooSmall`` validation error:

  >>> from zope.schema.interfaces import TooSmall, TooBig
  >>> from z3c.form.testing import TestRequest

  >>> view = error.ErrorViewSnippet(
  ...     TooSmall(), TestRequest(), None, None, None, None)
  >>> view
  <ErrorViewSnippet for TooSmall>

The discriminators for an error view are as follows: error, request, widget,
field, form, and content. After updating the view, a test message is available:

  >>> view.update()
  >>> view.message
  'Value is too small'

And after registering a template for the error view, we can also render the
view:

  >>> import os
  >>> filename = os.path.join(os.path.dirname(error.__file__), 'error.pt')

  >>> import zope.component
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> from z3c.form import interfaces

  >>> zope.component.provideAdapter(
  ...     error.ErrorViewTemplateFactory(filename, 'text/html'),
  ...     (interfaces.IErrorViewSnippet, None), IPageTemplate)

  >>> print(view.render())
  <div class="error">Value is too small</div>


Customizing Error Messages
--------------------------

As you can imagine, writing new error views for every scenario can be very
tedious, especially if you only want to provide a specific error *message*. So
let's create somewhat more interesting setup:

  >>> import zope.interface
  >>> import zope.schema
  >>> class IPerson(zope.interface.Interface):
  ...     name = zope.schema.TextLine(title='Name')
  ...     age = zope.schema.Int(
  ...         title='Age',
  ...         min=0)

You must agree, that the follwoing message is pretty dull when entering a
negative age:

  >>> print(view.render())
  <div class="error">Value is too small</div>

So let's register a better message for this particular situation:

  >>> NegativeAgeMessage = error.ErrorViewMessage(
  ...     'A negative age is not sensible.',
  ...     error=TooSmall, field=IPerson['age'])

  >>> zope.component.provideAdapter(NegativeAgeMessage, name='message')

The created object is a common attribute value for the error view message. The
discriminators are the same as for the error view itself. Now we create an
error view message for ``TooSmall`` of the age field:

  >>> view = error.ErrorViewSnippet(
  ...     TooSmall(), TestRequest(), None, IPerson['age'], None, None)

  >>> view.update()
  >>> print(view.render())
  <div class="error">A negative age is not sensible.</div>

Much better, isn't it?

We can also provide dynamic error view messages that are computed each time we
get an error. For example, we have an IAdult interface that have minimal age of
18:

  >>> class IAdult(zope.interface.Interface):
  ...     age = zope.schema.Int(title='Age', min=18)

Now, let's create a function that will be called by a message value adapter,
it receives one argument, a special ``z3c.form.value.ComputedValue`` object
that will have all needed attributes: error, request, widget, field, form and
content. Let's use one of them:

  >>> def getAgeTooSmallErrorMessage(value):
  ...     return 'Given age is smaller than %d, you are not adult.' % (
  ...         value.field.min)

Now, register the computed view message:

  >>> ComputedAgeMessage = error.ComputedErrorViewMessage(
  ...     getAgeTooSmallErrorMessage, error=TooSmall, field=IAdult['age'])
  >>> zope.component.provideAdapter(ComputedAgeMessage, name='message')

Now, the error view snippet will show dynamically generated message:

  >>> view = error.ErrorViewSnippet(
  ...     TooSmall(), TestRequest(), None, IAdult['age'], None, None)
  >>> view.update()
  >>> print(view.render())
  <div class="error">Given age is smaller than 18, you are not adult.</div>


Registering Custom Error Views
------------------------------

Even though message attribute values will solve most of our customization
needs, sometimes one wishes to register a custom view to have more complex
views. In this example we wish to register a custom error message:

  >>> from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
  >>> from z3c.form import tests

  >>> class NegativeAgeView(error.ErrorViewSnippet):
  ...     template = ViewPageTemplateFile(
  ...         'custom_error.pt', os.path.dirname(tests.__file__))

We now need to assert the special discriminators specific to this view:

  >>> error.ErrorViewDiscriminators(
  ...     NegativeAgeView, error=TooSmall, field=IPerson['age'])

After registering the new and default error view, ...

  >>> zope.component.provideAdapter(NegativeAgeView)
  >>> zope.component.provideAdapter(error.ErrorViewSnippet)

we can now make use of it, but only for this particular field and error:

  >>> zope.component.getMultiAdapter(
  ...     (TooSmall(), TestRequest(), None, IPerson['age'], None, None),
  ...     interfaces.IErrorViewSnippet)
  <NegativeAgeView for TooSmall>

Other combinations will return the default screen instead:

  >>> zope.component.getMultiAdapter(
  ...     (TooBig(), TestRequest(), None, IPerson['age'], None, None),
  ...     interfaces.IErrorViewSnippet)
  <ErrorViewSnippet for TooBig>

  >>> zope.component.getMultiAdapter(
  ...     (TooSmall(), TestRequest(), None, IPerson['name'], None, None),
  ...     interfaces.IErrorViewSnippet)
  <ErrorViewSnippet for TooSmall>


Value Error View Snippets
-------------------------

In the previous examples we have always worked with the view of the validation
error. Since data managers can also return value errors, there is also an
error view for them:

  >>> valueError = ValueError(2)
  >>> errorView = error.ValueErrorViewSnippet(
  ...     valueError, TestRequest(), None, None, None, None)

It uses the same template:

  >>> errorView.update()
  >>> print(errorView.render())
  <div class="error">The system could not process the given value.</div>

Unfortunately, we cannot make use of the original string representation of the
value error, since it cannot be localized well enough. Thus we provide our own
message. Of course, the message can be overridden:

  >>> CustomMessage = error.ErrorViewMessage(
  ...     'The entered value is not valid.', error=ValueError)
  >>> zope.component.provideAdapter(CustomMessage, name='message')

Let's now render the snippet again:

  >>> errorView.update()
  >>> print(errorView.render())
  <div class="error">The entered value is not valid.</div>


Invalid Error View Snippets
---------------------------

When invariants are used, commonly the ``Invalid`` exception (from the
``zope.interface`` package) is raised from within the invariant, if the
invariant finds a problem. We need a special error view snippet for this class
of errors:

  >>> invalidError = zope.interface.Invalid('The data was invalid.')
  >>> errorView = error.InvalidErrorViewSnippet(
  ...     invalidError, TestRequest(), None, None, None, None)

Since the same template as before is used, the error simply renders:

  >>> errorView.update()
  >>> print(errorView.render())
  <div class="error">The data was invalid.</div>

As you can see, the first argument to the exception is used as the explanatory
message of the error.
