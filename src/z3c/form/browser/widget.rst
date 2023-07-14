Widget base classes
===================

HTMLFormElement
---------------
The widget base class.
::

  >>> from z3c.form.browser.widget import HTMLFormElement
  >>> form = HTMLFormElement()


addClass
........

Widgets based on :code:`HTMLFormElement` also have the :code:`addClass` method which can be used to add CSS classes to the widget.

The :code:`klass` attribute is used because :code:`class` is a reserved keyword in Python.
It's empty per default::

  >>> form = HTMLFormElement()
  >>> form.klass


After adding a class it shows up in :code:`klass`::

  >>> form.addClass("my-css-class")
  >>> form.klass
  'my-css-class'


:code:`addClass` prevents adding the same class twice::

  >>> form.addClass("my-css-class")
  >>> form.klass
  'my-css-class'

  >>> form.addClass("another-class")
  >>> form.klass
  'my-css-class another-class'

  >>> form.addClass("another-class third-class")
  >>> form.klass
  'my-css-class another-class third-class'


The duplicate removal also keeps the original order of CSS classes::

  >>> form.addClass("third-class another-class")
  >>> form.klass
  'my-css-class another-class third-class'

