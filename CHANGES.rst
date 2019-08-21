=========
Changelog
=========

4.2 (unreleased)
----------------

- Drop support for Python 3.4.

- Add support for Python 3.8b4.


4.1.2 (2019-03-04)
------------------

- Fix an edge case when field `missing_value` is not `None` but a custom
  value that works as `None`.
  That ended up calling `zope.i18n` `NumberFormat.format` with `None` what
  then failed.


4.1.1 (2018-11-26)
------------------

- Fix ``FieldWidgets.copy()``. It was broken since ``SelectionManager`` was
  reimplemented using ``OrderedDict``.


4.1.0 (2018-11-15)
------------------

- Add support for Python 3.7.

- Deal with items with same name but different values in ordered field widget.
  [rodfersou]

- Move homegrown Manager implementation to ``OrderedDict``.
  [tomgross]

- Adapt tests to `lxml >= 4.2`, `zope.configuration >= 4.3` and
  `zope.schema >= 4.7`.


4.0.0 (2017-12-20)
------------------

- Upgrade the major version 4 to reflect the breaking changes in 3.3.0.
  (Version 3.6 will be a re-release of 3.2.x not containing the changes since
  3.3.0 besides cherry-picks.)
  Fixes: https://github.com/zopefoundation/z3c.form/issues/41

- Host documentation at https://z3cform.readthedocs.io


3.5.0 (2017-09-19)
------------------

- Add support for Python 3.6.

- Drop support for Python 3.3.

- Avoid duplicated IDs when using a non-required field with
  ``z3c.formwidget.query.widget.QuerySourceRadioWidget``.
  [pgrunewald]


3.4.0 (2016-11-15)
------------------

- Drop support for Python 2.6.

- Support Python 3.5 officially.

- Fix TypeError: object of type 'generator' has no ``len()``.
  Happens with z3c.formwidget.query.  [maurits]

- Turned ``items`` into a property again on all widgets.
  For the select widget it was a method since 2.9.0.
  For the radio and checkbox widgets it was a method since 3.2.10.
  For orderedselect and multi it was always a property.
  Fixes https://github.com/zopefoundation/z3c.form/issues/44
  [maurits]

- Fix handling of missing terms in collections. (See version 2.9 describing
  this feature.)

- Fix `orderedselect_input.js` resource to be usable on browser layers which do
  not extend ``zope.publisher.interfaces.browser.IDefaultBrowserLayer``.

3.3.0 (2016-03-09)
------------------

- *MAJOR* overhaul of ObjectWidget:

  * low level unittests passed, but high level was not tops
    basic rule is that widgets want RAW values and all conversion
    must be done in ``ObjectConverter``

  * ``ObjectSubForm`` and ``SubformAdapter`` is removed,
    it was causing more problems than good

  * added high level integration tests

- Removed ``z3c.coverage`` from ``test`` extra.  [gforcada, maurits]


3.2.10 (2016-03-09)
-------------------

- RadioWidget items are better determined when they are needed [agroszer]

- CheckBoxWidget items are better determined when they are needed [agroszer]

- Bugfix: The ``ChoiceTerms`` adapter blindly assumed that the passed in field
  is unbound, which is not necessarily the case in interesting ObjectWidget
  scenarios. Not it checks for a non-None field context first. [srichter]

3.2.9 (2016-02-01)
------------------

- Correctly handled ``noValueToken`` in RadioWidget.  This avoids a
  ``LookupError: --NOVALUE--``.  [gaudenz,ale-rt]

- Added ``json`` method for forms and ``json_data`` method for
  widgets.  [mmilkin]

- Change javascript for updating ordered select widget hidden structure so it
  works again on IE11 and doesn't send back an empty list that deletes all
  selections on save. Fixes https://github.com/zopefoundation/z3c.form/issues/23
  [fredvd]

- Started on Dutch translations.
  [maurits]


3.2.8 (2015-11-09)
------------------

- Standardized namespace __init__.  [agroszer]


3.2.7 (2015-09-20)
------------------

- Remove "cannot move farther up/down" messages
  in ordered select widget.
  [esteele]

- Updated Traditional Chinese translation.
  [l34marr]


3.2.6 (2015-09-10)
------------------

- Fixed warnings in headers of locales files.
  Checked with `msgfmt -c`.
  [maurits]

- Added Finnish translation.
  [petri]

- Added Traditional Chinese translation.
  [l34marr]


3.2.5 (2015-09-09)
------------------

- Fixed error on Python 3: NameError: global name 'basestring' is not
  defined.  This fixes a bug introduced in version 3.2.1.
  [maurits]


3.2.4 (2015-07-18)
------------------

- Fix ordered select input widget not working.
  [vangheem]

- ReSt fix.
  [timo]


3.2.3 (2015-03-21)
------------------

- 3.2.2 was a brown bag release. Fix MANIFEST.in to include the js file that has been added in 3.2.2.
  [timo]


3.2.2 (2015-03-21)
------------------

- move js to separate file to prevent escaped entities in Plone 5.
  [pbauer]


3.2.1 (2014-06-09)
------------------

- Add DataExtractedEvent, which is thrown after data and errors are extracted
  from widgets. Fixes https://github.com/zopefoundation/z3c.form/pull/18

- Remove spaces at start and end of text field values.

- Explicitly hide span in ``orderedselect_input.pt``.  This only
  contains hidden inputs, but Internet Explorer 10 was showing them
  anyway.  Fixes https://github.com/zopefoundation/z3c.form/issues/19


3.2.0 (2014-03-18)
------------------

- Feature: Added text and password widget HTML5 attributes required by
  plone.login.


3.1.1 (2014-03-02)
------------------

- Feature: Added a consistent id on single checkbox and multi checkbox
  widgets.


3.1.0 (2013-12-02)
------------------

- Feature: Added a consistent id on ordered selection widget.

- Feature: Added a hidden template for the textlines widget.

- Feature: added an API to render each radio button separately.


3.0.5 (2013-10-09)
------------------

- Bug: Remove errors for cases where the key field of a dict field uses a
  sequence widget (most notably choices). The sequence widget always returns
  lists as widget values, which are not hashable. We convert those lists to
  tuples now within the dict support.


3.0.4 (2013-10-06)
------------------

- Feature: Moved registration of translation directories to a separate ZCML
  file.

- Bug: Fixed a typo in German translations.


3.0.3 (2013-09-06)
------------------

- Feature: Version 2.9 introduced a solution for missing terms in
  vocabularies. Adapted sources to this solution, too.


3.0.2 (2013-08-14)
------------------

- Bug: Fix unicode decode error in weird cases in
  ``checkbox.CheckboxWidget.update()`` and ``radio.RadioWidget.update()`` (eg:
  when ``term.value`` is an Plone Archetype ATFile)

3.0.1 (2013-06-25)
------------------

- Bug: The alpha slipped out as 3.0.0, removed ``ZODB-4.0.0dev.tar.gz``
  to reduce damage

- Bug: Fixed a bug in ``widget.py`` ``def wrapCSSClass``


3.0.0 (2013-06-24)
------------------

- Feature: Added support for ``IDict`` field in ``MultiWidget``.

- Bug: Only add the 'required' CSS class to widgets when they are in input mode.

- Bug: Catch bug where if a select value was set as from hidden input or
  through a rest url as a single value, it won't error out when trying to
  remove from ignored list. Probably not the 100% right fix but it catches
  core dumps and is sane anyways.


3.0.0a3 (2013-04-08)
--------------------

- Feature: Updated pt_BR translation.

- Bug: Fixed a bug where file input value was interpeted as UTF-8.


3.0.0a2 (2013-02-26)
--------------------

- Bug: The 3.0.0a1 release was missing some files (e.g. ``locales``) due to an
  incomplete ``MANIFEST.in``.


3.0.0a1 (2013-02-24)
--------------------

- Feature: Removed several parts to be installed by default, since some
  packages are not ported yet.

- Feature: Added support for Python 3.3.

- Feature: Replaced deprecated ``zope.interface.implements`` usage with
  equivalent ``zope.interface.implementer`` decorator.

- Feature: Dropped support for Python 2.4 and 2.5.

- Bug: Make sure the call to the method that returns the default value
  is made with a field which has its context bound.


2.9.1 (2012-11-27)
------------------

- Feautre: The ``updateWidgets`` method has received an argument
  ``prefix`` which allows setting the prefix of the field widgets
  adapter.

  This allows updating the common widgets prefix before the individual
  widgets are updated, useful for situations where neither a form, nor
  a widgets prefix is desired.

- Bug: Capitalize the messages 'no value' and 'select a value'. This change
  has been applied also to the existing translations (where applicable).

- Bug: ``TextLinesConverter``: Do not ignore newlines at the end of the
  inputted string, thus do not eat blank items

- Bug: ``TextLinesConverter``: ``toFieldValue()``, convert conversion
  exceptions to ``FormatterValidationError``, for cases like got a string
  instead of int.

2.9.0 (2012-09-17)
------------------

- Feature: Missing terms in vocabularies: this was a pain until now.
  Now it's possible to have the same (missing) value unchanged on the object
  with an EditForm after save as it was before editing.
  That brings some changes with it:

  * *MAJOR*: unchanged values/fields do not get validated anymore
    (unless they are empty or are FileUploads)

  * A temporary ``SimpleTerm`` gets created for the missing value
    Title is by default "Missing: ${value}". See MissingTermsMixin.

- Feature: Split ``configure.zcml``

- Bug: ``SequenceWidget`` DISPLAY_MODE: silently ignore missing tokens,
  because INPUT_MODE and HIDDEN_MODE does that too.

2.8.2 (2012-08-17)
------------------

- Feature: Added ``IForm.ignoreRequiredOnValidation``,
  ``IWidgets.ignoreRequiredOnValidation``,
  ``IWidget.ignoreRequiredOnValidation``.
  Those enable ``extract`` and ``extractData`` to return without errors in
  case a required field is not filled.
  That also means the usual "Missing value" error will not get displayed.
  But the ``required-info`` (usually the ``*``) yes.
  This is handy to store partial state.


2.8.1 (2012-08-06)
------------------

- Fixed broken release, my python 2.7 windows setup didn't release the new
  widget.zcml, widget_layout.pt and widget_layout_hidden.pt files. After
  enhance the pattern in MANIFEST.in everything seems fine. That's probably
  because I patched my python version with the \*build exclude pattern patch.
  And yes, the new files where added to the svn repos! After deep into this
  again, it seems that only previous added \*.txt, \*.pt files get added to
  the release. A fresh checkout sdist release only contains the \*.py and \*.mo
  files. Anyway the enhanced MANIFEST.in file solved the problem.


2.8.0 (2012-08-06)
------------------

- Feature: Implemented widget layout concept similar to z3c.pagelet. The new
  layout concept allows to register layout templates additional to the widget
  templates. Such a layout template only get used if a widget get called.
  This enhacement is optional and compatible with all previous z3c.form
  versions and doesn't affect existing code and custom implementations
  except if you implemented a own __call__ method for widgets which
  wasn't implemented in previous versions. The new __call__ method will lookup
  and return a layout template which supports additional HTML code used as
  a wrapper for the HTML code returned from the widget render method.
  This concept allows to define additional HTML construct provided for all
  widget and render specific CSS classes arround the widget per context, view,
  request, etc discriminators. Such a HTML constuct was normaly supported in
  form macros which can't get customized on a per widget, view or context base.

  Summary; the new layout concept allows us to define a wrapper CSS elements
  for the widget element (label, widget, error) on a per widgte base and skip
  the generic form macros offered from z3c.formui.

  Note; you only could get into trouble if you define a widget in tal without
  to prefix them with ``nocall:`` e.g. tal:define="widget view/widgets/foo"
  Just add a nocall like tal:define="widget nocall:view/widgets/foo" if your
  rendering engine calls the __call__method by default. Also note that the
  following will also call the __call__ method tal:define="widget myWidget".

- Fixed content type extraction test which returned different values. This
  probably depends on a newer version of guess_content_type. Just allow
  image/x-png and image/pjpeg as valid values.


2.7.0 (2012-07-11)
------------------

- Remove `zope34` extra, use an older version of z3c.form if you need to
  support pre-ZTK versions.

- Require at least zope.app.container 3.7 for adding support.

- Avoid dependency on ZODB3.

- Added IField.showDefault and IWidget.showDefault
  That controls whether the widget should look for field default values
  to display. This can be really helpful in EditForms, where you don't
  want to have default values instead of actual (missing) values.
  By default it is True to provide backwards compatibility.

2.6.1 (2012-01-30)
------------------

- Fixed a potential problem where a non-ascii vocabulary/source term value
  could cause the checkbox and readio widget to crash.

- Fixed a problem with the ``datetime.timedelta`` converter, which failed to
  convert back to the field value, when the day part was missing.


2.6.0 (2012-01-30)
------------------

- Remove ":list" from radio inputs, since radio buttons can be only one value
  by definition. See LP580840.

- Changed radio button and checkbox widget labels from token to value (wrapped
  by a unicode conversion) to make it consistent with the parent
  ``SequenceWidget`` class. This way, edit and display views of the widgets
  show the same label. See LP623210.

- Remove dependency on zope.site.hooks, which was moved to zope.component in
  3.8.0 (present in ZTK 1.0 and above).

- Make zope.container dependency more optional (it is only used in tests)

- Properly escape JS code in script tag for the ordered-select widget. See
  LP829484.

- Cleaned whitespace in page templates.

- Fix ``IGroupForm`` interface and actually use it in the ``GroupForm``
  class. See LP580839.

- Added Spanish translation.

- Added Hungarian translation.

2.5.1 (2011-11-26)
------------------

- Better compatibility with Chameleon 2.x.

- Added \*.mo files missing in version 2.5.0.

- Pinned minimum version of test dependency `z3c.template`.

2.5.0 (2011-10-29)
------------------

- Fixed coverage report generator script buildout setup.

- Note: z3c.pt and chameleon are not fully compatible right now with TAL.
  Traversing the repeat wrapper is not done the same way. ZPT uses the
  following pattern:
  <tal:block condition="not:repeat/value/end">, </tal:block>

  Chameleon only supports python style traversing:
  <tal:block condition="not:python:repeat['value'].end">, </tal:block>

- Upgrade to chameleon 2.0 template engine and use the newest z3c.pt and
  z3c.ptcompat packages adjusted to work with chameleon 2.0.

  See the notes from the z3c.ptcompat package:

  Update z3c.ptcompat implementation to use component-based template engine
  configuration, plugging directly into the Zope Toolkit framework.

  The z3c.ptcompat package no longer provides template classes, or ZCML
  directives; you should import directly from the ZTK codebase.

  Also, note that the ``PREFER_Z3C_PT`` environment option has been
  rendered obsolete; instead, this is now managed via component
  configuration.

  Attention: You need to include the configure.zcml file from z3c.ptcompat
  for enable the z3c.pt template engine. The configure.zcml will plugin the
  template engine. Also remove any custom built hooks which will import
  z3c.ptcompat in your tests or other places.

  You can directly use the BoundPageTemplate and ViewPageTempalteFile from
  zope.browserpage.viewpagetemplatefile if needed. This templates will implicit
  use the z3c.pt template engine if the z3c.ptcompat configure.zcml is
  loaded.


2.4.4 (2011-07-11)
------------------

- Remove unneeded dependency on deprecated ``zope.app.security``.

- Fixed ButtonActions.update() to correctly remove actions when called again,
  after the button condition become false.


2.4.3 (2011-05-20)
------------------

- Declare TextLinesFieldWidget as an IFieldWidget implementer.

- Clarify MultiWidget.extract(), when there are zero items,
  this is now [] instead of <NO_VALUE>

- Some typos fixed

- Fixed test failure due to change in floating point representation in Python
  2.7.

- Ensure at least min_length widgets are rendered for a MultiWidget in input
  mode.

- Added Japanese translation.

- Added base of Czech translation.

- Added Portuguese Brazilian translation.

2.4.2 (2011-01-22)
------------------

- Adjust test for the contentprovider feature to not depend on the
  ContentProviderBase class that was introduced in zope.contentprovider 3.5.0.
  This restores compatibility with Zope 2.10.

- Security issue, removed IBrowserRequest from IFormLayer. This prevents to
  mixin IBrowserRequest into non IBrowserRequest e.g. IJSONRPCRequest.
  This should be compatible since a browser request using z3c.form already
  provides IBrowserRequest and the IFormLayer is only a marker interface used
  as skin layer.

- Add English translation (generated from translation template using
  msgen z3c.form.pot > en/LC_MESSAGES/z3c.form.po).

- Added Norwegian translation, thanks to Helge Tesdal and Martijn Pieters.

- Updated German translation.


2.4.1 (2010-07-18)
------------------

- Since version 2.3.4 ``applyChanges`` required that the value exists
  when the field had a ``DictionaryField`` data manager otherwise it
  broke with an ``AttributeError``. Restored previous behavior that
  values need not to be exist before ``applyChanges`` was called by
  using ``datamanager.query()`` instead of ``datamanager.get()`` to
  get the previous value.

- Added missing dependency on ``zope.contentprovider``.

- No longer using deprecated ``zope.testing.doctest`` by using
  python's built-in ``doctest`` module.

2.4.0 (2010-07-01)
------------------

- Feature: mix fields and content providers in forms. This allow to enrich
  the form by interlacing html snippets produced by content providers.
  Adding html outside the widgets avoids the systematic need of
  subclassing or changing the full widget rendering.

- Bug: Radio widget was not treating value as a list in hidden mode.


2.3.4 (2010-05-17)
------------------

- Bugfix: applyChanges should not try to compare old and new values if the old
  value can not be accessed.

- Fix DictionaryField to conform to the IDataManager spec: get() should raise
  an exception if no value can be found.


2.3.3 (2010-04-20)
------------------

- The last discriminator of the 'message' IValue adapter used in the
  ErrorViewSnippet is called 'content', but it was looked up as the error view
  itself. It is now looked up on the form's context.

- Don't let util.getSpecification() generate an interface more than once.
  This causes strange effects when used in value adapters: if two adapters
  use e.g. ISchema['some_field'] as a "discriminator" for 'field', with one
  adapter being more specific on a discriminator that comes later in the
  discriminator list (e.g. 'form' for an ErrorViewMessage), then depending on
  the order in which these two were set up, the adapter specialisation may
  differ, giving unexpected results that make it look like the adapter
  registry is picking the wrong adapter.

- Fix trivial test failures on Python 2.4 stemming from differences in
  pprint's sorting of dicts.

- Don't invoke render() when publishing the form as a view if the HTTP status
  code has been set to one in the 3xx range (e.g. a redirect or not-modified
  response) - the response body will be ignored by the browser anyway.

- Handle Invalid exceptions from constraints and field validators.

- Don't create unnecessary self.items in update() method of
  SelectWidget in DISPLAY_MODE. Now items is a property.

- Add hidden widget templates for radio buttons and checkboxes.

2.3.2 (2010-01-21)
------------------

- Reverted changes made in the previous release as the ``getContent``
  method can return anything it wants to as long as a data manager can
  map the fields to it. So ``context`` should be used for group
  instantiation. In cases where ``context`` is not wanted, the group
  can be instantiated in the ``update`` method of its parent group or
  form. See also
  https://mail.zope.org/pipermail/zope-dev/2010-January/039334.html

  (So version 2.3.2 is the same as version 2.3.0.)


2.3.1 (2010-01-18)
------------------

- ``GroupForm`` and ``Group`` now use ``getContent`` method when
  instantiating group classes instead of directly accessing
  ``self.context``.


2.3.0 (2009-12-28)
------------------

Refactoring
~~~~~~~~~~~

- Removed deprecated zpkg slug and ZCML slugs.

- Adapted tests to `zope.schema` 3.6.0.

- Avoid to use `zope.testing.doctestunit` as it is now deprecated.

Update
~~~~~~

- Updated German translations.


2.2.0 (2009-10-27)
------------------

- Feature: Add ``z3c.form.error.ComputedErrorViewMessage`` factory for easy
  creation of dynamically computed error messages.

- Bug: <div class="error"> was generated twice for MultiWidget and
  ObjectWidget in input mode.

- Bug: Replace dots with hyphens when generating form id from its name.

- Refactored OutputChecker to its own module to allow using
  ``z3c.form.testing`` without needing to depend on ``lxml``.

- Refactored: Folded duplicate code in
  ``z3c.form.datamanager.AttributeField`` into a single property.


2.1.0 (2009-07-22)
------------------

- Feature: The `DictionaryFieldManager` now allows all mappings
  (``zope.interface.common.mapping.IMapping``), even
  ``persistent.mapping.PersistentMapping`` and
  ``persistent.dict.PersistentDict``. By default, however, the field
  manager is only registered for dict, because it would otherwise get
  picked up in undesired scenarios.

- Bug: Updated code to pass all tests on the latest package versions.

- Bug: Completed the Zope 3.4 backwards-compatibility. Also created a buidlout
  configuration file to test the Zope 3.4 compatibility. Note: You *must* use
  the 'latest' or 'zope34' extra now to get all required
  packages. Alternatively, you can specify the packages listed in either of
  those extras explicitely in your product's required packages.


2.0.0 (2009-06-14)
------------------

Features
~~~~~~~~

- KGS 3.4 compatibility. This is a real hard thing, because `z3c.form` tests
  use `lxml` >= 2.1.1 to check test output, but KGS 3.4 has `lxml`
  1.3.6. Therefore we agree on that if tests pass with all package versions
  nailed by KGS 3.4 but `lxml` overridden to 2.1.1 then the `z3c.form` package
  works with a plain KGS 3.4.

- Removed hard `z3c.ptcompat` and thus `z3c.pt` dependency.  If you have
  `z3c.ptcompat` on the Python path it will be used.

- Added nested group support. Groups are rendered as fieldsets.  Nested
  fieldsets are very useful when designing forms.

  WARNING: If your group did have an `applyChanges()` (or any added(?)) method
  the new one added by this change might not match the signature.

- Added `labelRequired` and `requiredInfo` form attributes. This is useful for
  conditional rendering a required info legend in form templates.  The
  `requiredInfo` label depends by default on a given `labelRequired` message
  id and will only return the label if at least one widget field is required.

- Add support for refreshing actions after their execution. This is useful
  when button action conditions are changing as a result of action
  execution. All you need is to set the `refreshActions` flag of the form to
  `True` in your action handler.

- Added support for using sources. Where it was previosly possible to use a
  vocabulary it is now also possible to use a source. This works both for
  basic and contextual sources.

  **IMPORTANT:** The `ChoiceTerms` and `CollectionTerms` in `z3c.form.term`
  are now simple functions that query for real `ITerms` adapters for field's
  `source` or `value_type` respectively. So if your code inherits the old
  `ChoiceTerms` and `CollectionTerms` classes, you'll need to review and adapt
  it. See the `z3c.form.term` module and its documentation.

- The new `z3c.form.interfaces.NOT_CHANGED` special value is available to
  signal that the current value should be left as is.  It's currently handled
  in the `z3c.form.form.applyChanges()` function.

- When no file is specified in the file upload widget, instead of overwriting
  the value with a missing one, the old data is retained.  This is done by
  returning the new `NOT_CHANGED` special value from the
  `FileUploadDataConvereter`.

- Preliminary support for widgets for the `schema.IObject` field has been
  added. However, there is a big caveat, please read the ``object-caveat.txt``
  document inside the package.

  A new `objectWidgetTemplate` ZCML directive is provided to register widget
  templates for specific object field schemas.

- Implemented the `MultiWidget` widget. This widget allows you to use simple
  fields like `ITextLine`, `IInt`, `IPassword`, etc. in a `IList` or `ITuple`
  sequence.

- Implemented `TextLinesWidget` widget. This widget offers a text area element
  and splits lines in sequence items. This is usfull for power user
  interfaces.  The widget can be used for sequence fields (e.g. `IList`) that
  specify a simple value type field (e.g. `ITextLine` or `IInt`).

- Added a new flag `ignoreContext` to the form field, so that one can
  individually select which fields should and which ones should not ignore the
  context.

- Allow raw request values of sequence widgets to be non-sequence values,
  which makes integration with Javascript libraries easier.

- Added support in the file upload widget's testing flavor to specify
  'base64'-encoded strings in the hidden text area, so that binary data can be
  uploaded as well.

- Allow overriding the `required` widget attribute using `IValue` adapter just
  like it's done for `label` and `name` attributes.

- Add the `prompt` attribute of the `SequenceWidget` to the list of adaptable
  attributes.

- Added benchmarking suite demonstrating performance gain when using
  ``z3c.pt``.

- Added support for ``z3c.pt``. Usage is switched on via the "PREFER_Z3C_PT"
  environment variable or via ``z3c.ptcompat.config.[enable/diable]()``.

- The `TypeError` message used when a field does not provide `IFormUnicode`
  now also contains the type of the field.

- Add support for internationalization of `z3c.form` messages.  Added Russian,
  French, German and Chinese translations.

- Sphinx documentation for the package can now be created using the new `docs`
  script.

- The widget for fields implementing `IChoice` is now looked up by querying
  for an adapter for ``(field, field.vocabulary, request)`` so it can be
  differentiated according to the type of the source used for the field.

- Move `formErrorsMessage` attribute from `AddForm` and `EditForm` to the
  `z3c.form.form.Form` base class as it's very common validation status
  message and can be easily reused (especially when translations are
  provided).

Refactoring
~~~~~~~~~~~

- Removed compatibility support with Zope 3.3.

- Templates now declare XML namespaces.

- HTML output is now compared using a modified version of the XML-aware output
  checker provided by `lxml`.

- Remove unused imports, adjust buildout dependencies in `setup.py`.

- Use the `z3c.ptcompat` template engine compatibility layer.

Fixed Bugs
~~~~~~~~~~

- **IMPORTANT** - The signature of `z3c.form.util.extractFileName` function
  changed because of spelling mistake fix in argument name. The
  `allowEmtpyPostFix` is now called `allowEmptyPostfix` (note `Empty` instead
  of `Emtpy` and `Postfix` instead of `PostFix`).

- **IMPORTANT** - The `z3c.form.interfaces.NOVALUE` special value has been
  renamed to `z3c.form.interfaces.NO_VALUE` to follow the common naming
  style. The backward-compatibility `NOVALUE` name is still in place, but the
  `repr` output of the object has been also changed, thus it may break your
  doctests.

- When dealing with `Bytes` fields, we should do a null conversion when going
  to its widget value.

- `FieldWidgets` update method were appending keys and values within each
  update call. Now the `util.Manager` uses a `UniqueOrderedKeys`
  implementation which will ensure that we can't add duplicated manager
  keys. The implementation also ensures that we can't override the
  `UniqueOrderedKeys` instance with a new list by using a decorator. If this
  `UniqueOrderedKeys` implementation doesn't fit for all use cases, we should
  probably use a customized `UserList` implementation. Now we can call
  ``widgets.update()`` more then one time without any side effect.

- `ButtonActions` update where appending keys and values within each update
  call. Now we can call ``actions.update()`` more then one time without any
  side effect.

- The `CollectionSequenceDataConverter` no longer throws a ``TypeError:
  'NoneType' object is not iterable`` when passed the value of a non-required
  field (which in the case of a `List` field is `None`).

- The `SequenceDataConverter` and `CollectionSequenceDataConverter` converter
  classes now ignore values that are not present in the terms when converting
  to a widget value.

- Use ``nocall:`` modifier in `orderedselect_input.pt` to avoid calling list
  entry if it is callable.

- `SingleCheckBoxFieldWidget` doesn't repeat the label twice (once in ``<div
  class="label">``, and once in the ``<label>`` next to the checkbox).

- Don't cause warnings in Python 2.6.

- `validator.SimpleFieldValidator` is now able to handle
  `interfaces.NOT_CHANGED`. This value is set for file uploads when the user
  does not choose a file for upload.


1.9.0 (2008-08-26)
------------------

- Feature: Use the ``query()`` method in the widget manager to try extract a
  value. This ensures that the lookup is never failing, which is particularly
  helpful for dictionary-based data managers, where dictionaries might not
  have all keys.

- Feature: Changed the ``get()`` method of the data manager to throw an error
  when the data for the field cannot be found. Added ``query()`` method to
  data manager that returns a default value, if no value can be found.

- Feature: Deletion of widgets from field widget managers is now possible.

- Feature: Groups now produce detailed `ObjectModifiedEvent` descriptions like
  regular edit forms do. (Thanks to Carsten Senger for providing a patch.)

- Feature: The widget manager's ``extract()`` method now supports an optional
  ``setErrors`` (default value: True) flag that allows one to not set errors
  on the widgets and widget manager during data extraction. Use case: You want
  to inspect the entered data and handle errors manually.

- Bug: The ``ignoreButtons`` flag of the ``z3c.form.form.extends()`` method
  was not honored. (Thanks to Carsten Senger for providing a patch.)

- Bug: Group classes now implement ``IGroup``. This also helps with the
  detection of group instantiation. (Thanks to Carsten Senger for providing a
  patch.)

- Bug: The list of changes in a group were updated incorrectly, since it was
  assumed that groups would modify mutually exclusive interfaces. Instead of
  using an overwriting dictionary ``update()`` method, a purely additive merge
  is used now. (Thanks to Carsten Senger for providing a patch.)

- Bug: Added a widget for ``IDecimal`` field in testing setup.

- Feature: The ``z3c.form.util`` module has a new function, ``createCSSId()``
  method that generates readable ids for use with css selectors from any
  unicode string.

- Bug: The ``applyChanges()`` method in group forms did not return a changes
  dictionary, but simply a boolean. This is now fixed and the group form
  changes are now merged with the main form changes.

- Bug: Display widgets did not set the style attribute if it was
  available, even though the input widgets did set the style attribute.


1.8.2 (2008-04-24)
------------------

- Bug: Display Widgets added spaces (due to code indentation) to the displayed
  values, which in some cases, like when displaying Python source code, caused
  the appearance to be incorrect.

- Bug: Prevent to call ``__len__`` on ``ITerms`` and use ``is None`` for check
  for existence. Because ``__len__`` is not a part of the ITerms API and ``not
  widget.terms`` will end in calling ``__len__`` on existing terms.


1.8.1 (2008-04-08)
------------------

- Bug: Fixed a bug that prohibited groups from having different contents than
  the parent form.  Previously, the groups contents were not being properly
  updated. Added new documentation on how to use groups to generate
  object-based sub-forms. Thanks to Paul Carduner for providing the fix and
  documentation.


1.8.0 (2008-01-23)
------------------

- Feature: Implemented ``IDisplayForm`` interface.

- Feature: Added integration tests for form interfaces. Added default class
  attribute called ``widgets`` in form class with default value ``None``. This
  helps to pass the integration tests. Now, the ``widgets`` attribute can also
  be used as a indicator for updated forms.

- Feature: Implemented additional ``createAndAdd`` hook in ``AddForm``. This
  allows you to implement create and add in a single method. It also supports
  graceful abortion of a create and add process if we do not return the new
  object. This means it can also be used as a hook for custom error messages
  for errors happen during create and add.

- Feature: Add a hidden widget template for the ``ISelectWidget``.

- Feature: Arrows in the ordered select widget replaced by named entities.

- Feature: Added ``CollectionSequenceDataConverter`` to ``setupFormDefaults``.

- Feature: Templates for the CheckBox widget are now registered in
  ``checkbox.zcml``.

- Feature: If a value cannot be converted from its unicode representation to a
  field value using the field's ``IFromUnicode`` interface, the resulting type
  error now shows the field name, if available.

- Bug: ``createId`` could not handle arbitrary unicode input. Thanks to
  Andreas Reuleaux for reporting the bug and a patch for it. (Added
  descriptive doctests for the function in the process.)

- Bug: Interface invariants where not working when not all fields needed for
  computing the invariant are in the submitted form.

- Bug: Ordered select didn't submit selected values.

- Bug: Ordered select lists displayed tokens instead of value,

- Bug: ``SequenceWidget`` displayed tokens instead of value.


1.7.0 (2007-10-09)
------------------

- Feature: Implemented ``ImageButton``, ``ImageAction``, ``ImageWidget``, and
  ``ImageFieldWidget`` to support imge submit buttons.

- Feature: The ``AttributeField`` data manager now supports adapting
  the content to the fields interface when the content doesn't implement
  this interface.

- Feature: Implemented single checkbox widget that can be used for boolean
  fields. They are not available by default but can be set using the
  ``widgetFactory`` attribute.

- Bug: More lingual issues have been fixed in the documentation. Thanks to
  Martijn Faassen for doing this.

- Bug: When an error occurred during processing of the request the
  widget ended up being security proxied and the system started
  throwing `TraversalError`-'s trying to access the `label` attribute of
  the widget. Declared that the widgets require the `zope.Public`
  permission in order to access these attributes.

- Bug: When rendering a widget the ``style`` attribute was not honored. Thanks
  to Andreas Reuleaux for reporting.

- Bug: When an error occurred in the sub-form, the status message was not set
  correctly. Fixed the code and the incorrect test. Thanks to Markus
  Kemmerling for reporting.

- Bug: Several interfaces had the ``self`` argument in the method
  signature. Thanks to Markus Kemmerling for reporting.


1.6.0 (2007-08-24)
------------------

- Feature: An event handler for ``ActionErrorOccurred`` events is registered
  to merge the action error into the form's error collectors, such as
  ``form.widgets.errors`` and ``form.widgets['name'].error`` (if
  applicable). It also sets the status of the form. (Thanks to Herman
  Himmelbauer, who requested the feature, for providing use cases.)

- Feature: Action can now raise ``ActionExecutionError`` exceptions that will
  be handled by the framework. These errors wrap the original error. If an
  error is specific to a widget, then the widget name is passed to a special
  ``WidgetActionExecutionError`` error. (Thanks to Herman Himmelbauer, who
  requested the feature, for providing use cases.)

- Feature: After an action handler has been executed, an action executed event
  is sent to the system. If the execution was successful, the event is
  ``ActionSuccessfull`` event is sent. If an action execution error was
  raised, the ``ActionErrorOccurred`` event is raised. (Thanks to Herman
  Himmelbauer, who requested the feature, for providing use cases.)

- Feature: The ``applyChanges()`` function now returns a dictionary of changes
  (grouped by interface) instead of a boolean. This allows us to generate a
  more detailed object-modified event. If no changes are applied, an empty
  dictionary is returned. The new behavior is compatible with the old one, so
  no changes to your code are required. (Thanks to Darryl Cousins for the
  request and implementation.)

- Feature: A new ``InvalidErrorViewSnippet`` class provides an error view
  snippet for ``zope.interface.Invalid`` exceptions, which are frequently used
  for invariants.

- Feature: When a widget is required, HTML-based widgets now declare a
  "required" class.

- Feature: The validation data wrapper now knows about the context of the
  validation, which provides a hook for invariants to access the environment.

- Feature: The BoolTerms term tokens are now cosntants and stay the same, even
  if the label has changed. The choice for the token is "true" and "false". By
  default it used to be "yes" and "no", so you probably have to change some
  unit tests. Functional tests are still okay, because you select by term
  title.

- Feature: BoolTerms now expose the labels for the true and false values
  to the class. This makes it a matter of doing trivial sub-classing to
  change the labels for boolean terms.

- Feature: Exposed several attributes of the widget manager to the form for
  convenience. The attributes are: mode, ignoreContext, ignoreRequest,
  ignoreReadonly.

- Feature: Provide more user-friendly error messages for number formatting.

- Refactoring: The widget specific class name was in camel-case. A converntion
  that later developed uses always dash-based naming of HTML/CSS related
  variables. So for example, the class name "textWidget" is now
  "text-widget". This change will most likely require some changes to your CSS
  declarations!

- Documentation: The text of ``field.txt`` has been reviewed linguistically.

- Documentation: While reviewing the ``form.txt`` with some people, several
  unclear and incomplete statements were discovered and fixed.

- Bug (IE): In Internet Explorer, when a label for a radio input field is only
  placed around the text describing the choice, then only the text is
  surrounded by a dashed box. IE users reported this to be confusing, thus we
  now place the label around the text and the input element so that both are
  surrounded by the dashed border. In Firefox and KHTML (Safari) only the
  radio button is surrounded all the time.

- Bug: When extracting and validating data in the widget manager, invariant
  errors were not converted to error view snippets.

- Bug: When error view snippets were not widget-specific -- in other words,
  the ``widget`` attribute was ``None`` -- rendering the template would fail.


1.5.0 (2007-07-18)
------------------

- Feature: Added a span around values for widgets in display mode. This allows
  for easier identification widget values in display mode.

- Feature: Added the concept of widget events and implemented a particular
  "after widget update" event that is called right after a widget is updated.

- Feature: Restructured the approach to customize button actions, by requiring
  the adapter to provide a new interface ``IButtonAction``. Also, an adapter
  is now provided by default, still allowing cusotmization using the usual
  methods though.

- Feature: Added button widget. While it is not very useful without
  Javascript, it still belongs into this package for completion.

- Feature: All ``IFieldWidget`` instances that are also HTML element widgets
  now declare an additional CSS class of the form "<fieldtype.lower()>-field".

- Feature: Added ``addClass()`` method to HTML element widgets, so that adding
  a new CSS class is simpler.

- Feature: Renamed "css" attribute of the widget to "klass", because the class
  of an HTML element is a classification, not a CSS marker.

- Feature: Reviewed all widget attributes. Added all available HTML attributes
  to the widgets.

- Documentation: Removed mentioning of widget's "hint" attribute, since it
  does not exist.

- Optimization: The terms for a sequence widget were looked up multiple times
  among different components. The widget is now the canonical source for the
  terms and other components, such as the converter uses them. This avoids
  looking up the terms multiple times, which can be an expensive process for
  some applications.

- Bug/Feature: Correctly create labels for radio button choices.

- Bug: Buttons did not honor the name given by the schema, if created within
  one, because we were too anxious to give buttons a name. Now name assignment
  is delayed until the button is added to the button manager.

- Bug: Button actions were never updated in the actions manager.

- Bug: Added tests for textarea widget.


1.4.0 (2007-06-29)
------------------

- Feature: The select widget grew a new ``prompt`` flag, which allows you to
  explicitely request a selection prompt as the first option in the selection
  (even for required fields). When set, the prompt message is shown. Such a
  prompt as option is common in Web-UIs.

- Feature: Allow "no value message" of select widgets to be dynamically
  changed using an attribute value adapter.

- Feature: Internationalized data conversion for date, time, date/time,
  integer, float and decimal. Now the locale data is used to format and parse
  those data types to provide the bridge to text-based widgets. While those
  features require the latest zope.i18n package, backward compatibility is
  provided.

- Feature: All forms now have an optional label that can be used by the UI.

- Feature: Implemented groups within forms. Groups allow you to combine a set
  of fields/widgets into a logical unit. They were designed with ease of use
  in mind.

- Feature: Button Actions -- in other words, the widget for the button field
  -- can now be specified either as the "actionFactory" on the button field or
  as an adapter.

- Bug: Recorded all public select-widget attributes in the interface.


1.3.0 (2007-06-22)
------------------

- Feature: In an edit form applying the data and generating all necessary
  messages was all done within the "Apply" button handler. Now the actual task
  of storing is factored out into a new method called "applyChanges(data)",
  which returns whether the data has been changed. This is useful for forms
  not dealing with objects.

- Feature: Added support for ``hidden`` fields. You can now use the ``hidden``
  mode for widgets which should get rendered as ``<input type="hidden"
  />``.

  Note: Make sure you use the new formui templates which will avoid rendering
        labels for hidden widgets or adjust your custom form macros.

- Feature: Added ``missing_value`` support to data/time converters

- Feature: Added named vocabulary lookup in ``ChoiceTerms`` and
  ``CollectionTerms``.

- Feature: Implemented support for ``FileUpload`` in ``FileWidget``.

  * Added helper for handling ``FileUpload`` widgets:

    + ``extractContentType(form, id)``

      Extracts the content type if ``IBytes``/``IFileWidget`` was used.

    + ``extractFileName(form, id, cleanup=True, allowEmtpyPostFix=False)``

      Extracts a filename if ``IBytes``/``IFileWidget`` was used.

      Uploads from win/IE need some cleanup because the filename includes also
      the path. The option ``cleanup=True`` will do this for you. The option
      ``allowEmtpyPostFix`` allows you to pass a filename without
      extensions. By default this option is set to ``False`` and will raise a
      ``ValueError`` if a filename doesn't contain an extension.

  * Created afile upload data converter registered for
    ``IBytes``/``IFileWidget`` ensuring that the converter will only be used
    for fiel widgets. The file widget is now the default for the bytes
    field. If you need to use a text area widget for ``IBytes``, you have to
    register a custom widget in the form using::

      fields['foobar'].widgetFactory = TextWidget

- Feature: Originally, when an attribute access failed in Unauthorized or
  ForbiddenAttribute exceptions, they were ignored as if the attribute would
  have no value. Now those errors are propagated and the system will fail
  providing the developer with more feedback. The datamanager also grew a new
  ``query()`` method that returns always a default and the ``get()`` method
  propagates any exceptions.

- Feature: When writing to a field is forbidden due to insufficient
  priviledges, the resulting widget mode will be set to "display". This
  behavior can be overridden by explicitely specifying the mode on a field.

- Feature: Added an add form implementation against ``IAdding``. While this is
  not an encouraged method of adding components, many people still use this
  API to extend the ZMI.

- Feature: The ``IFields`` class' ``select()`` and ``omit()`` method now
  support two ketword arguments "prefix" and "interface" that allow the
  selection and omission of prefixed fields and still specify the short
  name. Thanks to Nikolay Kim for the idea.

- Feature: HTML element ids containing dots are not very good, because then
  the "element#id" CSS selector does not work and at least in Firefox the
  attribute selector ("element[attr=value]") does not work for the id
  either. Converted the codebase to use dashes in ids instead.

- Bug/Feature: The ``IWidgets`` component is now an adapter of the form
  content and not the form context. This guarantees that vocabulary factories
  receive a context that is actually useful.

- Bug: The readonly flag within a field was never honored. When a field is
  readonly, it is displayed in "display" mode now. This can be overridden by
  the widget manager's "ignoreReadonly" flag, which is necessary for add
  forms.

- Bug: The mode selection made during the field layout creation was not
  honored and the widget manager always overrode the options providing its
  value. Now the mode specified in the field is more important than the one
  from the widget manager.

- Bug: It sometimes happens that the sequence widget has the no-value token as
  one element. This caused ``displayValue()`` to fail, since it tried to find
  a term for it. For now we simply ignore the no-value token.

- Bug: Fixed the converter when the incoming value is an empty string. An
  empty string really means that we have no value and it is thus missing,
  returning the missing value.

- Bug: Fix a slightly incorrect implementation. It did not cause any harm in
  real-world forms, but made unit testing much harder, since an API
  expectation was not met correctly.

- Bug: When required selections where not selected in radio and checkbox
  widgets, then the conversion did not behave correctly. This also revealed
  some issues with the converter code that have been fixed now.

- Bug: When fields only had a vocabulary name, the choice terms adaptation
  would fail, since the field was not bound. This has now been corrected.

- Documentation: Integrated English language and content review improvements
  by Roy Mathew in ``form.txt``.


1.2.0 (2007-05-30)
------------------

- Feature: Added ability to change the button action title using an ``IValue``
  adapter.


1.1.0 (2007-05-30)
------------------

- Feature: Added compatibility for Zope 3.3 and thus Zope 2.10.


1.0.0 (2007-05-24)
------------------

- Initial Release
