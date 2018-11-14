==============
Data Converter
==============

The data converter is the component that converts an internal data value as
described by a field to an external value as required by a widget and vice
versa. The goal of the converter is to avoid field and widget proliferation
solely to handle different types of values. The purpose of fields is to
describe internal data types and structures and that of widgets to provide one
particular mean of input.

The only two discriminators for the converter are the field and the widget.

Let's look at the ``Int`` field to ``TextWidget`` converter as an example:

  >>> import zope.schema
  >>> age = zope.schema.Int(
  ...     __name__='age',
  ...     title=u'Age',
  ...     min=0)

  >>> from z3c.form.testing import TestRequest
  >>> from z3c.form import widget
  >>> text = widget.Widget(TestRequest())

  >>> from z3c.form import converter
  >>> conv = converter.FieldDataConverter(age, text)

The field data converter is a generic data converter that can be used for all
fields that implement ``IFromUnicode``. If, for example, a ``Date`` field
-- which does not provide ``IFromUnicode`` -- is passed in, then a type error
is raised:

  >>> converter.FieldDataConverter(zope.schema.Date(), text)
  Traceback (most recent call last):
  ...
  TypeError: Field of type ``Date`` must provide ``IFromUnicode``.

A named field will tell it's name:

  >>> converter.FieldDataConverter(zope.schema.Date(__name__="foobar"), text)
  Traceback (most recent call last):
  ...
  TypeError: Field ``foobar`` of type ``Date`` must provide ``IFromUnicode``.

However, the ``FieldDataConverter`` is registered for ``IField``, since many
fields (like ``Decimal``) for which we want to create custom converters
provide ``IFromUnicode`` more specifically than their characterizing interface
(like ``IDecimal``).

The converter can now convert any integer to a the value the test widget deals
with, which is an ASCII string:

  >>> conv.toWidgetValue(34)
  u'34'

When the missing value is passed in, an empty string should be returned:

  >>> conv.toWidgetValue(age.missing_value)
  u''

Of course, values can also be converted from a widget value to field value:

  >>> conv.toFieldValue('34')
  34

An empty string means simply that the value is missing and the missing value
of the field is returned:

  >>> age.missing_value = -1
  >>> conv.toFieldValue('')
  -1

Of course, trying to convert a non-integer string representation fails in a
conversion error:

  >>> conv.toFieldValue('3.4')
  Traceback (most recent call last):
  ...
  InvalidIntLiteral: invalid literal for int(): 3.4

Also, the conversion to the field value also validates the data; in this case
negative values are not allowed:

  >>> conv.toFieldValue('-34')
  Traceback (most recent call last):
  ...
  TooSmall: (-34, 0)

That's pretty much the entire API. When dealing with converters within the
component architecture, everything is a little bit simpler. So let's register
the converter:

  >>> import zope.component
  >>> zope.component.provideAdapter(converter.FieldDataConverter)

Once we ensure that our widget is a text widget, we can lookup the adapter:

  >>> import zope.interface
  >>> from z3c.form import interfaces
  >>> zope.interface.alsoProvides(text, interfaces.ITextWidget)

  >>> zope.component.getMultiAdapter((age, text), interfaces.IDataConverter)
  <FieldDataConverter converts from Int to Widget>

For field-widgets there is a helper adapter that makes the lookup even
simpler:

  >>> zope.component.provideAdapter(converter.FieldWidgetDataConverter)

After converting our simple widget to a field widget,

  >>> fieldtext = widget.FieldWidget(age, text)

we can now lookup the data converter adapter just by the field widget itself:

  >>> interfaces.IDataConverter(fieldtext)
  <FieldDataConverter converts from Int to Widget>


Number Data Converters
----------------------

As hinted on above, the package provides a specific data converter for each of
the three main numerical types: ``int``, ``float``, ``Decimal``. Specifically,
those data converters support full localization of the number formatting.

  >>> age = zope.schema.Int()
  >>> intdc = converter.IntegerDataConverter(age, text)
  >>> intdc
  <IntegerDataConverter converts from Int to Widget>

Since the age is so small, the formatting is trivial:

  >>> intdc.toWidgetValue(34)
  u'34'

But if we increase the number, the grouping seprator will be used:

  >>> intdc.toWidgetValue(3400)
  u'3,400'

An empty string is returned, if the missing value is passed in:

  >>> intdc.toWidgetValue(None)
  u''

Of course, parsing these outputs again, works as well:

  >>> intdc.toFieldValue(u'34')
  34

But if we increase the number, the grouping seprator will be used:

  >>> intdc.toFieldValue(u'3,400')
  3400

Luckily our parser is somewhat forgiving, and even allows for missing group
characters:

  >>> intdc.toFieldValue(u'3400')
  3400

If an empty string is passed in, the missing value of the field is returned:

  >>> intdc.toFieldValue(u'')

Finally, if the input does not match at all, then a validation error is
returned:

  >>> intdc.toFieldValue(u'fff')
  Traceback (most recent call last):
  ...
  FormatterValidationError:
      (u'The entered value is not a valid integer literal.', u'fff')

The formatter validation error derives from the regular validation error, but
allows you to specify the message that is output when asked for the
documentation:

  >>> err = converter.FormatterValidationError(u'Something went wrong.', None)
  >>> err.doc()
  u'Something went wrong.'

Let's now look at the float data converter.

  >>> rating = zope.schema.Float()
  >>> floatdc = converter.FloatDataConverter(rating, text)
  >>> floatdc
  <FloatDataConverter converts from Float to Widget>

Again, you can format and parse values:

  >>> floatdc.toWidgetValue(7.43)
  u'7.43'
  >>> floatdc.toWidgetValue(10239.43)
  u'10,239.43'

  >>> floatdc.toFieldValue(u'7.43') == 7.43
  True
  >>> type(floatdc.toFieldValue(u'7.43'))
  <type 'float'>
  >>> floatdc.toFieldValue(u'10,239.43')
  10239.43

The error message, however, is customized to the floating point:

  >>> floatdc.toFieldValue(u'fff')
  Traceback (most recent call last):
  ...
  FormatterValidationError:
      (u'The entered value is not a valid decimal literal.', u'fff')

The decimal converter works like the other two before.

  >>> money = zope.schema.Decimal()
  >>> decimaldc = converter.DecimalDataConverter(money, text)
  >>> decimaldc
  <DecimalDataConverter converts from Decimal to Widget>

Formatting and parsing should work just fine:

  >>> import decimal

  >>> decimaldc.toWidgetValue(decimal.Decimal('7.43'))
  u'7.43'
  >>> decimaldc.toWidgetValue(decimal.Decimal('10239.43'))
  u'10,239.43'

  >>> decimaldc.toFieldValue(u'7.43')
  Decimal("7.43")
  >>> decimaldc.toFieldValue(u'10,239.43')
  Decimal("10239.43")

Again, the error message, is customized to the floating point:

  >>> floatdc.toFieldValue(u'fff')
  Traceback (most recent call last):
  ...
  FormatterValidationError:
      (u'The entered value is not a valid decimal literal.', u'fff')


Bool Data Converter
---------------------

  >>> yesno = zope.schema.Bool()
  >>> yesnowidget = widget.Widget(TestRequest())
  >>> conv = converter.FieldDataConverter(yesno, yesnowidget)
  >>> conv.toWidgetValue(True)
  'True'

  >>> conv.toWidgetValue(False)
  'False'


Text Data Converters
----------------------

Users often add empty spaces by mistake, for example when copy-pasting content
into the form.

  >>> name = zope.schema.TextLine()
  >>> namewidget = widget.Widget(TestRequest())
  >>> conv = converter.FieldDataConverter(name, namewidget)
  >>> conv.toFieldValue(u'Einstein ')
  'Einstein'


Date Data Converter
-------------------

Since the ``Date`` field does not provide ``IFromUnicode``, we have to provide
a custom data converter. This default one is not very sophisticated and is
inteded for use with the text widget:

  >>> date = zope.schema.Date()

  >>> ddc = converter.DateDataConverter(date, text)
  >>> ddc
  <DateDataConverter converts from Date to Widget>

Dates are simply converted to ISO format:

  >>> import datetime
  >>> bday = datetime.date(1980, 1, 25)

  >>> ddc.toWidgetValue(bday)
  u'80/01/25'

If the date is the missing value, an empty string is returned:

  >>> ddc.toWidgetValue(None)
  u''

The converter only knows how to convert this particular format back to a
datetime value:

  >>> ddc.toFieldValue(u'80/01/25')
  datetime.date(1980, 1, 25)

By default the converter converts missing input to missin_input value:

  >>> ddc.toFieldValue(u'') is None
  True

If the passed in string cannot be parsed, a formatter validation error is
raised:

  >>> ddc.toFieldValue(u'8.6.07')
  Traceback (most recent call last):
  ...
  FormatterValidationError: ("The datetime string did not match the pattern
                              u'yy/MM/dd'.", u'8.6.07')

Time Data Converter
-------------------

Since the ``Time`` field does not provide ``IFromUnicode``, we have to provide
a custom data converter. This default one is not very sophisticated and is
inteded for use with the text widget:

  >>> time = zope.schema.Time()

  >>> tdc = converter.TimeDataConverter(time, text)
  >>> tdc
  <TimeDataConverter converts from Time to Widget>

Dates are simply converted to ISO format:

  >>> noon = datetime.time(12, 0, 0)

  >>> tdc.toWidgetValue(noon)
  u'12:00'

The converter only knows how to convert this particular format back to a
datetime value:

  >>> tdc.toFieldValue(u'12:00')
  datetime.time(12, 0)

By default the converter converts missing input to missin_input value:

  >>> tdc.toFieldValue(u'') is None
  True


Datetime Data Converter
-----------------------

Since the ``Datetime`` field does not provide ``IFromUnicode``, we have to
provide a custom data converter. This default one is not very sophisticated
and is inteded for use with the text widget:

  >>> dtField = zope.schema.Datetime()

  >>> dtdc = converter.DatetimeDataConverter(dtField, text)
  >>> dtdc
  <DatetimeDataConverter converts from Datetime to Widget>

Dates are simply converted to ISO format:

  >>> bdayNoon = datetime.datetime(1980, 1, 25, 12, 0, 0)

  >>> dtdc.toWidgetValue(bdayNoon)
  u'80/01/25 12:00'

The converter only knows how to convert this particular format back to a
datetime value:

  >>> dtdc.toFieldValue(u'80/01/25 12:00')
  datetime.datetime(1980, 1, 25, 12, 0)

By default the converter converts missing input to missin_input value:

  >>> dtdc.toFieldValue(u'') is None
  True


Timedelta Data Converter
------------------------

Since the ``Timedelta`` field does not provide ``IFromUnicode``, we have to
provide a custom data converter. This default one is not very sophisticated
and is inteded for use with the text widget:

  >>> timedelta = zope.schema.Timedelta()

  >>> tddc = converter.TimedeltaDataConverter(timedelta, text)
  >>> tddc
  <TimedeltaDataConverter converts from Timedelta to Widget>

Dates are simply converted to ISO format:

  >>> allOnes = datetime.timedelta(1, 3600+60+1)

  >>> tddc.toWidgetValue(allOnes)
  u'1 day, 1:01:01'

The converter only knows how to convert this particular format back to a
datetime value:

  >>> fv = tddc.toFieldValue(u'1 day, 1:01:01')
  >>> (fv.days, fv.seconds)
  (1, 3661)

If no day is available, the following short form is used:

  >>> noDay = datetime.timedelta(0, 3600+60+1)
  >>> tddc.toWidgetValue(noDay)
  u'1:01:01'

And now back to the field value:

  >>> fv = tddc.toFieldValue(u'1:01:01')
  >>> (fv.days, fv.seconds)
  (0, 3661)

By default the converter converts missing input to missin_input value:

  >>> tddc.toFieldValue(u'') is None
  True


File Upload Data Converter
--------------------------

Since the ``Bytes`` field can contain a ``FileUpload`` object, we have to make
sure we can convert ``FileUpload`` objects to bytes too.

  >>> import z3c.form.browser.file
  >>> fileWidget = z3c.form.browser.file.FileWidget(TestRequest())
  >>> bytes = zope.schema.Bytes()

  >>> fudc = converter.FileUploadDataConverter(bytes, fileWidget)
  >>> fudc
  <FileUploadDataConverter converts from Bytes to FileWidget>

The file upload widget usually provides a file object. But sometimes is also
provides a string:

  >>> simple = 'foobar'
  >>> fudc.toFieldValue(simple)
  'foobar'

The converter can also convert ``FileUpload`` objects. So we need to setup a
fields storage stub ...

  >>> class FieldStorageStub:
  ...     def __init__(self, file):
  ...         self.file = file
  ...         self.headers = {}
  ...         self.filename = 'foo.bar'

and a ``FileUpload`` component:

  >>> try:
  ...     from cStringIO import StringIO as BytesIO
  ... except ImportError:
  ...     from io import BytesIO
  >>> from zope.publisher.browser import FileUpload
  >>> myfile = BytesIO(b'File upload contents.')
  >>> aFieldStorage = FieldStorageStub(myfile)
  >>> myUpload = FileUpload(aFieldStorage)

Let's try to convert the input now:

  >>> fudc.toFieldValue(myUpload)
  'File upload contents.'

By default the converter converts missing input to the ``NOT_CHANGED`` value:

  >>> fudc.toFieldValue('')
  <NOT_CHANGED>

This allows machinery later to ignore the field without sending all the data
around.

If we get an empty filename in a ``FileUpload`` obejct, we also get the
``missing_value``. But this really means that there was an error somewhere in
the upload, since you are normaly not able to upload a file without a filename:

  >>> class EmptyFilenameFieldStorageStub:
  ...     def __init__(self, file):
  ...         self.file = file
  ...         self.headers = {}
  ...         self.filename = ''
  >>> myfile = BytesIO(b'')
  >>> aFieldStorage = EmptyFilenameFieldStorageStub(myfile)
  >>> myUpload = FileUpload(aFieldStorage)
  >>> bytes = zope.schema.Bytes()
  >>> fudc = converter.FileUploadDataConverter(bytes, fileWidget)
  >>> fudc.toFieldValue(myUpload) is None
  True

There is also a ``ValueError`` if we don't get a seekable file from the
``FieldStorage`` during the upload:

  >>> myfile = ''
  >>> aFieldStorage = FieldStorageStub(myfile)
  >>> myUpload = FileUpload(aFieldStorage)
  >>> bytes = zope.schema.Bytes()
  >>> fudc = converter.FileUploadDataConverter(bytes, fileWidget)
  >>> fudc.toFieldValue(myUpload) is None
  Traceback (most recent call last):
  ...
  ValueError: (u'Bytes data are not a file object', ...AttributeError...)

When converting to the widget value, not conversion should be done, since
bytes are not convertable in that sense.

  >>> fudc.toWidgetValue(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x04')

When the file upload widget is not used and a text-based widget is desired,
then the regular field data converter will be chosen. Using a text widget,
however, must be setup manually in the form with code like this::

  fields['bytesField'].widgetFactory = TextWidget


Sequence Data Converter
-----------------------

For widgets and fields that work with choices of a sequence, a special data
converter is required that works with terms. A prime example is a choice
field. Before we can use the converter, we have to register some adapters:

  >>> from z3c.form import term
  >>> import zc.sourcefactory.browser.source
  >>> import zc.sourcefactory.browser.token
  >>> zope.component.provideAdapter(term.ChoiceTermsVocabulary)
  >>> zope.component.provideAdapter(term.ChoiceTermsSource)
  >>> zope.component.provideAdapter(term.ChoiceTerms)
  >>> zope.component.provideAdapter(
  ...     zc.sourcefactory.browser.source.FactoredTerms)
  >>> zope.component.provideAdapter(
  ...     zc.sourcefactory.browser.token.fromInteger)

The choice fields can be used together with vocabularies and sources.

Using vocabulary
~~~~~~~~~~~~~~~~

Let's now create a choice field (using a vocabulary) and a widget:

  >>> from zope.schema.vocabulary import SimpleVocabulary

  >>> gender = zope.schema.Choice(
  ...     vocabulary = SimpleVocabulary([
  ...              SimpleVocabulary.createTerm(0, 'm', u'male'),
  ...              SimpleVocabulary.createTerm(1, 'f', u'female'),
  ...              ]) )

  >>> from z3c.form import widget
  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = gender

We now use the field and widget to instantiate the converter:

  >>> sdv = converter.SequenceDataConverter(gender, seqWidget)

We can now convert a real value to a widget value, which will be the term's
token:

  >>> sdv.toWidgetValue(0)
  ['m']

The result is always a sequence, since sequence widgets only deal collections
of values. Of course, we can convert the widget value back to an internal
value:

  >>> sdv.toFieldValue(['m'])
  0

Sometimes a field is not required. In those cases, the internal value is the
missing value of the field. The converter interprets that as no value being
selected:

  >>> gender.missing_value = 'missing'

  >>> sdv.toWidgetValue(gender.missing_value)
  []

If the internal value is not a valid item in the terms, it is treated as
missing:

  >>> sdv.toWidgetValue(object())
  []

If "no value" has been specified in the widget, the missing value
of the field is returned:

  >>> sdv.toFieldValue([u'--NOVALUE--'])
  'missing'

An empty list will also cause the missing value to be returned:

  >>> sdv.toFieldValue([])
  'missing'

Using source
~~~~~~~~~~~~

Let's now create a choice field (using a source) and a widget:

  >>> from zc.sourcefactory.basic import BasicSourceFactory
  >>> class GenderSourceFactory(BasicSourceFactory):
  ...     _mapping = {0: u'male', 1: u'female'}
  ...     def getValues(self):
  ...         return self._mapping.keys()
  ...     def getTitle(self, value):
  ...         return self._mapping[value]
  >>> gender_source = zope.schema.Choice(
  ...     source = GenderSourceFactory())

  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = gender_source

We now use the field and widget to instantiate the converter:

  >>> sdv = converter.SequenceDataConverter(gender, seqWidget)

We can now convert a real value to a widget value, which will be the term's
token:

  >>> sdv.toWidgetValue(0)
  ['0']

The result is always a sequence, since sequence widgets only deal collections
of values. Of course, we can convert the widget value back to an internal
value:

  >>> sdv.toFieldValue(['0'])
  0

Sometimes a field is not required. In those cases, the internalvalue is the
missing value of the field. The converter interprets that as no value being
selected:

  >>> gender.missing_value = 'missing'

  >>> sdv.toWidgetValue(gender.missing_value)
  []

If "no value" has been specified in the widget, the missing value
of the field is returned:

  >>> sdv.toFieldValue([u'--NOVALUE--'])
  'missing'

An empty list will also cause the missing value to be returned:

  >>> sdv.toFieldValue([])
  'missing'


Collection Sequence Data Converter
----------------------------------

For widgets and fields that work with a sequence of choices, another data
converter is required that works with terms. A prime example is a list
field. Before we can use the converter, we have to register the terms adapters:

  >>> from z3c.form import term
  >>> zope.component.provideAdapter(term.CollectionTerms)
  >>> zope.component.provideAdapter(term.CollectionTermsVocabulary)
  >>> zope.component.provideAdapter(term.CollectionTermsSource)

Collections can also use either vocabularies or sources.

Using vocabulary
~~~~~~~~~~~~~~~~

Let's now create a list field (using the previously defined field using
a vocabulary) and a widget:

  >>> genders = zope.schema.List(value_type=gender)
  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = genders

We now use the field and widget to instantiate the converter:

  >>> csdv = converter.CollectionSequenceDataConverter(genders, seqWidget)

We can now convert a real value to a widget value, which will be the term's
token:

  >>> csdv.toWidgetValue([0])
  ['m']

The result is always a sequence, since sequence widgets only deal collections
of values. Of course, we can convert the widget value back to an internal
value:

  >>> csdv.toFieldValue(['m'])
  [0]

Of course, a collection field can also have multiple values:

  >>> csdv.toWidgetValue([0, 1])
  ['m', 'f']

  >>> csdv.toFieldValue(['m', 'f'])
  [0, 1]

If any of the values are not a valid choice, they are simply ignored:

  >>> csdv.toWidgetValue([0, 3])
  ['m']


Sometimes a field is not required. In those cases, the internal value is the
missing value of the field. The converter interprets that as no values being
given:

  >>> genders.missing_value is None
  True
  >>> csdv.toWidgetValue(genders.missing_value)
  []

For some field, like the ``Set``, the collection type is a tuple. Sigh. In
these cases we use the last entry in the tuple as the type to use:

  >>> genders = zope.schema.Set(value_type=gender)
  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = genders

  >>> csdv = converter.CollectionSequenceDataConverter(genders, seqWidget)

  >>> csdv.toWidgetValue(set([0]))
  ['m']

  >>> csdv.toFieldValue(['m'])
  set([0])

Getting Terms
+++++++++++++

As an optimization of this converter, the converter actually does not look up
the terms itself but uses the widget's ``terms`` attribute. If the terms are
not yet retrieved, the converter will ask the widget to do so when in need.

So let's see how this works when getting the widget value:

  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = genders

  >>> seqWidget.terms

  >>> csdv = converter.CollectionSequenceDataConverter(genders, seqWidget)
  >>> csdv.toWidgetValue([0])
  ['m']

  >>> seqWidget.terms
  <z3c.form.term.CollectionTermsVocabulary object ...>

The same is true when getting the field value:

  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = genders

  >>> seqWidget.terms

  >>> csdv = converter.CollectionSequenceDataConverter(genders, seqWidget)
  >>> csdv.toFieldValue(['m'])
  set([0])

  >>> seqWidget.terms
  <z3c.form.term.CollectionTermsVocabulary object ...>


Corner case: Just in case the field has a sequence as ``_type``:

  >>> class myField(zope.schema.List):
  ...     _type = (list, tuple)

  >>> genders = myField(value_type=gender)
  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = genders

We now use the field and widget to instantiate the converter:

  >>> csdv = converter.CollectionSequenceDataConverter(genders, seqWidget)

The converter uses the latter type (tuple) to convert:

  >>> csdv.toFieldValue(['m'])
  (0,)

Using source
~~~~~~~~~~~~

Let's now create a list field (using the previously defined field using
a source) and a widget:

  >>> genders_source = zope.schema.List(value_type=gender_source)
  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = genders_source

We now use the field and widget to instantiate the converter:

  >>> csdv = converter.CollectionSequenceDataConverter(
  ...     genders_source, seqWidget)

We can now convert a real value to a widget value, which will be the term's
token:

  >>> csdv.toWidgetValue([0])
  ['0']

The result is always a sequence, since sequence widgets only deal collections
of values. Of course, we can convert the widget value back to an internal
value:

  >>> csdv.toFieldValue(['0'])
  [0]

For some field, like the ``Set``, the collection type is a tuple. Sigh. In
these cases we use the last entry in the tuple as the type to use:

  >>> genders_source = zope.schema.Set(value_type=gender_source)
  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = genders_source

  >>> csdv = converter.CollectionSequenceDataConverter(
  ...     genders_source, seqWidget)

  >>> csdv.toWidgetValue(set([0]))
  ['0']

  >>> csdv.toFieldValue(['0'])
  set([0])

Getting Terms
+++++++++++++

As an optimization of this converter, the converter actually does not look up
the terms itself but uses the widget's ``terms`` attribute. If the terms are
not yet retrieved, the converter will ask the widget to do so when in need.

So let's see how this works when getting the widget value:

  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = genders_source

  >>> seqWidget.terms

  >>> csdv = converter.CollectionSequenceDataConverter(
  ...     genders_source, seqWidget)
  >>> csdv.toWidgetValue([0])
  ['0']

  >>> seqWidget.terms
  <z3c.form.term.CollectionTermsSource object ...>

The same is true when getting the field value:

  >>> seqWidget = widget.SequenceWidget(TestRequest())
  >>> seqWidget.field = genders_source

  >>> seqWidget.terms

  >>> csdv = converter.CollectionSequenceDataConverter(
  ...     genders_source, seqWidget)
  >>> csdv.toFieldValue(['0'])
  set([0])

  >>> seqWidget.terms
  <z3c.form.term.CollectionTermsSource object ...>


Boolean to Single Checkbox Data Converter
-----------------------------------------

The conversion from any field to the single checkbox widget value is a special
case, because it has to be defined what selecting the value means. In the case
of the boolean field, "selected" means ``True`` and if unselected, ``False``
is returned:

  >>> boolField = zope.schema.Bool()

  >>> bscbx = converter.BoolSingleCheckboxDataConverter(boolField, seqWidget)
  >>> bscbx
  <BoolSingleCheckboxDataConverter converts from Bool to SequenceWidget>

Let's now convert boolean field to widget values:

  >>> bscbx.toWidgetValue(True)
  ['selected']
  >>> bscbx.toWidgetValue(False)
  []

Converting back is equally simple:

  >>> bscbx.toFieldValue(['selected'])
  True
  >>> bscbx.toFieldValue([])
  False

Note that this widget has no concept of missing value, since it can only
represent two states by desgin.


Text Lines Data Converter
-------------------------

For sequence widgets and fields that work with a sequence of `TextLine` value
fields, a simple data converter is required. Let's create a list of text lines
field and a widget:

  >>> languages = zope.schema.List(
  ...     value_type=zope.schema.TextLine(),
  ...     default=[],
  ...     missing_value=None,
  ...     )

  >>> from z3c.form.browser import textlines
  >>> tlWidget = textlines.TextLinesWidget(TestRequest())
  >>> tlWidget.field = languages

We now use the field and widget to instantiate the converter:

  >>> tlc = converter.TextLinesConverter(languages, tlWidget)

We can now convert a real value to a widget value:

  >>> tlc.toWidgetValue([u'de', u'fr', u'en'])
  u'de\nfr\nen'

Empty entries are significant:

  >>> tlc.toWidgetValue([u'de', u'fr', u'en', u''])
  u'de\nfr\nen\n'


The result is always a string, since text lines widgets only deal with textarea
as input field. Of course, we can convert the widget value back to an internal
value:

  >>> tlc.toFieldValue('de\nfr\nen')
  [u'de', u'fr', u'en']

Each line should be one item:

  >>> tlc.toFieldValue('this morning\ntomorrow evening\nyesterday')
  [u'this morning', u'tomorrow evening', u'yesterday']

Empty lines are significant:

  >>> tlc.toFieldValue('de\n\nfr\nen')
  [u'de', u'', u'fr', u'en']

Empty lines are also significant at the end:

  >>> tlc.toFieldValue('de\nfr\nen\n')
  [u'de', u'fr', u'en', u'']


An empty string will also cause the missing value to be returned:

  >>> tlc.toFieldValue('') is None
  True

It also should work for schema fields that define their type as tuple,
for instance zope.schema.Int declares its type as (int, long).

  >>> ids = zope.schema.List(
  ...     value_type=zope.schema.Int(),
  ...     )

Let's illustrate the problem:

  >>> zope.schema.Int._type == zope.schema._compat.integer_types
  True

  Note: Should be int and long in Python 2.

The converter will use the first one.

  >>> tlWidget.field = ids
  >>> tlc = converter.TextLinesConverter(ids, tlWidget)

Of course, it still can convert to the widget value:

  >>> tlc.toWidgetValue([1,2,3])
  u'1\n2\n3'

And back:

  >>> tlc.toFieldValue(u'1\n2\n3')
  [1, 2, 3]

An empty string will also cause the missing value to be returned:

  >>> tlc.toFieldValue('') is None
  True

Converting Missing value to Widget value returns '':

  >>> tlc.toWidgetValue(tlc.field.missing_value)
  u''

Just in case the field has sequence as its ``_type``:

  >>> class myField(zope.schema.List):
  ...     _type = (list, tuple)

  >>> ids = myField(
  ...     value_type=zope.schema.Int(),
  ...     )

The converter will use the latter one.

  >>> tlWidget.field = ids
  >>> tlc = converter.TextLinesConverter(ids, tlWidget)

Of course, it still can convert to the widget value:

  >>> tlc.toWidgetValue([1,2,3])
  u'1\n2\n3'

And back:

  >>> tlc.toFieldValue(u'1\n2\n3')
  (1, 2, 3)

What if we have a wrong number:

  >>> tlc.toFieldValue(u'1\n2\n3\nfoo')
  Traceback (most recent call last):
  ...
  FormatterValidationError: ("invalid literal for int() with base 10: 'foo'", u'foo')




Multi Data Converter
--------------------

For multi widgets and fields that work with a sequence of other basic types, a
separate data converter is required. Let's create a list of integers field and
a widget:

  >>> numbers = zope.schema.List(
  ...     value_type=zope.schema.Int(),
  ...     default=[],
  ...     missing_value=None,
  ...     )

  >>> from z3c.form.browser import multi
  >>> multiWidget = multi.MultiWidget(TestRequest())
  >>> multiWidget.field = numbers

Before we can convert, we have to regsiter a widget for the integer field:

  >>> from z3c.form.browser import text
  >>> zope.component.provideAdapter(
  ...     text.TextFieldWidget,
  ...     (zope.schema.Int, TestRequest))

We now use the field and widget to instantiate the converter:

  >>> conv = converter.MultiConverter(numbers, multiWidget)

We can now convert a list of integers to the multi-widget internal
representation:

  >>> conv.toWidgetValue([1, 2, 3])
  [u'1', u'2', u'3']

If the value is the missing value, an empty list is returned:

  >>> conv.toWidgetValue(None)
  []

Now, let's look at the reverse:

  >>> conv.toFieldValue([u'1', u'2', u'3'])
  [1, 2, 3]

If the list is empty, the missing value is returned:

  >>> conv.toFieldValue([]) is None
  True

Dict Multi Data Converter
-------------------------

For multi widgets and fields that work with a dictionary of other basic types, a
separate data converter is required. Let's create a dict of integers field and
a widget:

  >>> numbers = zope.schema.Dict(
  ...     value_type=zope.schema.Int(),
  ...     key_type=zope.schema.Int(),
  ...     default={},
  ...     missing_value=None,
  ...     )

  >>> from z3c.form.browser import multi
  >>> multiWidget = multi.MultiWidget(TestRequest())
  >>> multiWidget.field = numbers

Before we can convert, we have to regsiter a widget for the integer field:

  >>> from z3c.form.browser import text
  >>> zope.component.provideAdapter(
  ...     text.TextFieldWidget,
  ...     (zope.schema.Int, TestRequest))

We now use the field and widget to instantiate the converter:

  >>> conv = converter.DictMultiConverter(numbers, multiWidget)

We can now convert a dict of integers to the multi-widget internal
representation:

  >>> sorted(conv.toWidgetValue({1:1, 2:4, 3:9}))
  [(u'1', u'1'), (u'2', u'4'), (u'3', u'9')]

If the value is the missing value, an empty dict is returned:

  >>> conv.toWidgetValue(None)
  []

Now, let's look at the reverse:

  >>> conv.toFieldValue([(u'1',u'1'), (u'2',u'4'), (u'3',u'9')])
  {1: 1, 2: 4, 3: 9}

If the list is empty, the missing value is returned:

  >>> conv.toFieldValue([]) is None
  True
