========
Overview
========

This package provides an implementation for HTML forms and
widgets. The goal is to provide a simple API but with the ability to
easily customize any data or steps. Below is an overview of this
package's documentation. The documents are ordered in the way they
should be read:

Must Read
---------

- :ref:`form.txt`

  Describes the setup and usage of forms in the most common usages. Some
  details are provided to the structure of form components.

- :ref:`group.txt`

  This document describes how widget groups are implemented within this
  package and how they can be used.

- :ref:`subform.txt`

  Introduces the complexities surrounding sub-forms and details two classes of
  sub-forms, including code examples.

- :ref:`field.txt`

  Provides a comprehensive explanation of the field manager API and how it is
  to be used.

- :ref:`button.txt`

  Provides a comprehensive explanation of the button manager API. It also
  outlines how to create buttons within schemas and how buttons are converted
  to actions.

- :ref:`zcml.txt`

  Explains the ZCML directives defines by this package, which are designed to
  make it easier to register new templates without writing Python code.

Advanced Users
--------------

- :ref:`validator.txt`

  Validators are used to validate converted form data. This document provides
  a comprehensive overview of the API and how to use it effectively.

- :ref:`widget.txt`

  Explains in detail the design goals surrounding widgets and widget managers
  and how they were realized with the implemented API.

- :ref:`action.txt`

  Explains in detail the design goals surrounding action managers and
  actions. The execution of actions using action handlers is also covered. The
  document demonstrates how actions can be created without the use of buttons.

Informative
-----------

- :ref:`value.txt`

  The concept of attribute value adapters is introduced and fully
  explained. Some motivation for this new and powerful pattern is given as
  well.

- :ref:`datamanager.txt`

  Data managers are resposnsible for accessing and writing the data. While
  attribute access is the most common case, data managers can also manage
  other data structures, such as dictionaries.

- :ref:`converter.txt`

  Data converters convert data between internal and widget values and vice
  versa.

- :ref:`term.txt`

  Terms are wrappers around sources and vocabularies to provide a common
  interface for choices in this package.

- :ref:`util.txt`

  The ``util`` module provides several helper functions and classes. The
  components not tested otherwise are explained in this file.

- :ref:`adding.txt`

  This module provides a base class for add forms that work with the
  ``IAdding`` interface.


Browser Documentation
---------------------

There are several documentation files in the ``browser/`` sub-package. They
mainly document the basic widgets provided by the package.

Advanced Users
--------------

- :ref:`browserREADME.txt`

  This file contains a checklist, ensuring that all fields have a widget.

- ``<fieldname>.txt``

  Each field name documentation file comprehensively explains the widget and
  how it is ensured to work properly.
