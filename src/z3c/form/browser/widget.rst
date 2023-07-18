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


attributes
..........

On widgets you can programatically add, remove or modify HTML attributes::

  >>> form = HTMLFormElement()
  >>> form.id = "my-input"
  >>> form.title = "This is my input."

  >>> form.attributes
  {'id': 'my-input', 'title': 'This is my input.'}


Only attributes with values are included in :code:`attributes`::

  >>> form = HTMLFormElement()
  >>> form.id = "my-input"

  >>> form.attributes
  {'id': 'my-input'}


The :code:`klass` attibute of the :code:`HTMLFormElement` is changed to :code:`class`::

  >>> form = HTMLFormElement()
  >>> form.klass = "class-a class-b"

  >>> form.attributes
  {'class': 'class-a class-b'}


Once :code:`attributes` was accessed you cannot set the HTML attributes on the `HTMLFormElement` directly anymore::

  >>> form = HTMLFormElement()
  >>> form.id = "my-input"

  >>> form.attributes
  {'id': 'my-input'}

  >>> form.id = "no-input"
  >>> form.title = "This is my input."

  >>> form.attributes
  {'id': 'my-input'}


But you can change them via the :code:`attributes` property::

  >>> form = HTMLFormElement()
  >>> form.id = "my-input"

  >>> form.attributes
  {'id': 'my-input'}

  >>> form.attributes["id"] = "no-input"
  >>> form.attributes["title"] = "Okay. No input then."

  >>> form.attributes
  {'id': 'no-input', 'title': 'Okay. No input then.'}

  >>> form.attributes.update({"title": "The no input input.", "class": "class-a"})

  >>> form.attributes
  {'id': 'no-input', 'title': 'The no input input.', 'class': 'class-a'}

You can delete items::

  >>> del form.attributes["class"]
  >>> form.attributes
  {'id': 'no-input', 'title': 'The no input input.'}


And directly set it anew::

  >>> form.attributes = {'id': 'okay', 'title': 'I give up.'}
  >>> form.attributes
  {'id': 'okay', 'title': 'I give up.'}


You can use attributes to render inputs in a generic way without explicitly including all the HTML attributes.

Note: This only works if you use Chameleon templates. It does not work with the Zope PageTemplate reference implementation.

This is how you would write your Chameleon template::

  <input type="text" tal:attributes="view/attributes" />

