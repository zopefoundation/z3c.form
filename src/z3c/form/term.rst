=====
Terms
=====

Terms are used to provide choices for sequence widgets or any other construct
needing them. Since Zope 3 already has sources and vocabularies, the base
terms class simply builds on them.

Vocabularies
------------

Thus, let's create a vocabulary first:

  >>> from zope.schema import vocabulary
  >>> ratings = vocabulary.SimpleVocabulary([
  ...     vocabulary.SimpleVocabulary.createTerm(0, '0', 'bad'),
  ...     vocabulary.SimpleVocabulary.createTerm(1, '1', 'okay'),
  ...     vocabulary.SimpleVocabulary.createTerm(2, '2', 'good')
  ...     ])

Terms
~~~~~

Now we can create the terms object:

  >>> from z3c.form import term
  >>> terms = term.Terms()
  >>> terms.terms = ratings

Getting a term from a given value is simple:

  >>> terms.getTerm(0).title
  'bad'
  >>> terms.getTerm(3)
  Traceback (most recent call last):
  ...
  LookupError: 3

When converting values from their Web representation back to the internal
representation, we have to be able to look up a term by its token:

  >>> terms.getTermByToken('0').title
  'bad'
  >>> terms.getTerm('3')
  Traceback (most recent call last):
  ...
  LookupError: 3

However, often we just want the value so asking for the value that is
represented by a token saves usually one line of code:

  >>> terms.getValue('0')
  0
  >>> terms.getValue('3')
  Traceback (most recent call last):
  ...
  LookupError: 3

You can also iterate through all terms:

  >>> [entry.title for entry in terms]
  ['bad', 'okay', 'good']

Or ask how many terms you have in the first place:

  >>> len(terms)
  3

Finally the API allows you to check whether a particular value is available in
the terms:

  >>> 0 in terms
  True
  >>> 3 in terms
  False

Now, there are several terms implementations that were designed for particular
fields. Within the framework, terms are used as adapters with the follwoing
discriminators: context, request, form, field, vocabulary/source and widget.


Choice field
~~~~~~~~~~~~

The first terms implementation is for ``Choice`` fields. Choice fields
unfortunately can have a vocabulary and a source which behave differently.
Let's have a look a the vocabulary first:

  >>> import zope.component
  >>> zope.component.provideAdapter(term.ChoiceTermsVocabulary)
  >>> import z3c.form.testing
  >>> request = z3c.form.testing.TestRequest()
  >>> import z3c.form.widget
  >>> widget = z3c.form.widget.Widget(request)

  >>> import zope.schema

  >>> ratingField = zope.schema.Choice(
  ...     title='Rating',
  ...     vocabulary=ratings)

  >>> terms = term.ChoiceTerms(
  ...     None, request, None, ratingField, widget)
  >>> [entry.title for entry in terms]
  ['bad', 'okay', 'good']

Sometimes choice fields only specify a vocabulary name and the actual
vocabulary is looked up at run time.

  >>> ratingField2 = zope.schema.Choice(
  ...     title='Rating',
  ...     vocabulary='Ratings')

Initially we get an error because the "Ratings" vocabulary is not defined:

  >>> terms = term.ChoiceTerms(
  ...     None, request, None, ratingField2, widget)
  Traceback (most recent call last):
  ...
  MissingVocabularyError: Can't validate value without vocabulary named 'Ratings'

Let's now register the vocabulary under this name:

  >>> def RatingsVocabulary(obj):
  ...     return ratings

  >>> from zope.schema import vocabulary
  >>> vr = vocabulary.getVocabularyRegistry()
  >>> vr.register('Ratings', RatingsVocabulary)

We should now be able to get all terms as before:

  >>> terms = term.ChoiceTerms(
  ...     None, request, None, ratingField, widget)
  >>> [entry.title for entry in terms]
  ['bad', 'okay', 'good']


Missing terms
+++++++++++++

Sometimes it happens that a term goes away from the vocabulary, but our
stored objects still reference that term.

  >>> zope.component.provideAdapter(term.MissingChoiceTermsVocabulary)

  >>> terms = term.ChoiceTerms(
  ...     None, request, None, ratingField, widget)
  >>> term = terms.getTermByToken('42')
  Traceback (most recent call last):
  ...
  LookupError: 42

The same goes with looking up a term by value:

  >>> term = terms.getTerm('42')
  Traceback (most recent call last):
  ...
  LookupError: 42

Ooops, well this works only if the context has the right value for us.
This is because we don't want to accept any crap that's coming from HTML.

  >>> class IPerson(zope.interface.Interface):
  ...     gender = zope.schema.Choice(title='Gender', vocabulary='Genders')
  >>> @zope.interface.implementer(IPerson)
  ... class Person(object):
  ...     gender = None
  >>> gendersVocabulary = vocabulary.SimpleVocabulary([
  ...     vocabulary.SimpleVocabulary.createTerm(1, 'male', 'Male'),
  ...     vocabulary.SimpleVocabulary.createTerm(2, 'female', 'Female'),
  ...     ])
  >>> def GendersVocabulary(obj):
  ...     return ratings
  >>> vr.register('Genders', GendersVocabulary)

  >>> ctx = Person()
  >>> ctx.gender = 42

  >>> genderWidget = z3c.form.widget.Widget(request)
  >>> genderWidget.context = ctx
  >>> from z3c.form import interfaces
  >>> zope.interface.alsoProvides(genderWidget, interfaces.IContextAware)
  >>> from z3c.form.datamanager import AttributeField
  >>> zope.component.provideAdapter(AttributeField)

  >>> terms = term.ChoiceTerms(
  ...     ctx, request, None, IPerson['gender'], genderWidget)

Here we go:

  >>> missingTerm = terms.getTermByToken('42')

We get the term, we passed the token, the value is coming from the context.

  >>> missingTerm.token
  '42'
  >>> missingTerm.value
  42

We cannot figure the title, so we construct one.
Override ``makeMissingTerm`` if you want your own.

  >>> missingTerm.title
  'Missing: ${value}'

Still we raise LookupError if the token does not fit the context's value:

  >>> missingTerm = terms.getTermByToken('99')
  Traceback (most recent call last):
  ...
  LookupError: 99

The same goes with looking up a term by value.
We get the term if the context's value fits:

  >>> missingTerm = terms.getTerm(42)
  >>> missingTerm.token
  '42'

And an exception if it does not:

  >>> missingTerm = terms.getTerm(99)
  Traceback (most recent call last):
  ...
  LookupError: 99


Bool fields
~~~~~~~~~~~

A similar terms implementation exists for a ``Bool`` field:

  >>> truthField = zope.schema.Bool()

  >>> terms = term.BoolTerms(None, None, None, truthField, None)
  >>> [entry.title for entry in terms]
  ['yes', 'no']

In case you don't like the choice of 'yes' and 'no' for the labels, we
can subclass the ``BoolTerms`` class to control the display labels.

  >>> class MyBoolTerms(term.BoolTerms):
  ...   trueLabel = 'True'
  ...   falseLabel = 'False'

  >>> terms = MyBoolTerms(None, None, None, truthField, None)
  >>> [entry.title for entry in terms]
  ['True', 'False']


Collections
~~~~~~~~~~~

Finally, there are a terms adapters for all collections. But we have to
register some adapters before using it:

  >>> from z3c.form import term
  >>> zope.component.provideAdapter(term.CollectionTerms)
  >>> zope.component.provideAdapter(term.CollectionTermsVocabulary)
  >>> zope.component.provideAdapter(term.CollectionTermsSource)

  >>> ratingsField = zope.schema.List(
  ...     title='Ratings',
  ...     value_type=ratingField)

  >>> terms = term.CollectionTerms(
  ...     None, request, None, ratingsField, widget)
  >>> [entry.title for entry in terms]
  ['bad', 'okay', 'good']


Sources
-------

Basic sources
~~~~~~~~~~~~~

Basic sources need no context to compute their value. Let's create a
source first:

  >>> from zc.sourcefactory.basic import BasicSourceFactory
  >>> class RatingSourceFactory(BasicSourceFactory):
  ...     _mapping = {10: 'ugly', 20: 'nice', 30: 'great'}
  ...     def getValues(self):
  ...         return self._mapping.keys()
  ...     def getTitle(self, value):
  ...         return self._mapping[value]

As we did not include the configure.zcml of zc.sourcefactory we have
to register some required adapters manually. We also need the
ChoiceTermsSource adapter:

  >>> import zope.component
  >>> import zc.sourcefactory.browser.source
  >>> import zc.sourcefactory.browser.token
  >>> zope.component.provideAdapter(
  ...     zc.sourcefactory.browser.source.FactoredTerms)
  >>> zope.component.provideAdapter(
  ...     zc.sourcefactory.browser.token.fromInteger)
  >>> zope.component.provideAdapter(term.ChoiceTermsSource)

Choice fields
+++++++++++++

Sources can be used with ``Choice`` fields like vocabularies.  First
we create a field based on the source:

  >>> sourceRatingField = zope.schema.Choice(
  ...     title='Sourced Rating',
  ...     source=RatingSourceFactory())

We connect the field to a widget to see the ITerms adapter for sources
at work:

  >>> terms = term.ChoiceTerms(
  ...     None, request, None, sourceRatingField, widget)

Iterating over the terms adapter returnes the term objects:

  >>> [entry for entry in terms]
  [<zc.sourcefactory.browser.source.FactoredTerm object at 0x...>,
   <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>,
   <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>]
  >>> len(terms)
  3
  >>> [entry.token for entry in terms]
  ['10', '20', '30']
  >>> [entry.title for entry in terms]
  ['ugly', 'nice', 'great']

Using a token it is possible to look up the term and the value:

  >>> terms.getTermByToken('20').title
  'nice'
  >>> terms.getValue('30')
  30

With can test if a value is in the source:

  >>> 30 in terms
  True
  >>> 25 in terms
  False

Missing terms
#############

Sometimes it happens that a value goes away from the source, but our
stored objects still has this value.

  >>> zope.component.provideAdapter(term.MissingChoiceTermsSource)

  >>> terms = term.ChoiceTerms(
  ...     None, request, None, sourceRatingField, widget)
  >>> terms.getTermByToken('42')
  Traceback (most recent call last):
  ...
  LookupError: 42

The same goes with looking up a term by value:

  >>> terms.getTerm(42)
  Traceback (most recent call last):
  ...
  LookupError: 42

Ooops, well this works only if the context has the right value for us.
This is because we don't want to accept any crap that's coming from HTML.

  >>> class IRating(zope.interface.Interface):
  ...     rating = zope.schema.Choice(title='Sourced Rating',
  ...                                 source=RatingSourceFactory())
  >>> @zope.interface.implementer(IRating)
  ... class Rating(object):
  ...     rating = None

  >>> ctx = Rating()
  >>> ctx.rating = 42

  >>> ratingWidget = z3c.form.widget.Widget(request)
  >>> ratingWidget.context = ctx
  >>> from z3c.form import interfaces
  >>> zope.interface.alsoProvides(ratingWidget, interfaces.IContextAware)
  >>> from z3c.form.datamanager import AttributeField
  >>> zope.component.provideAdapter(AttributeField)

  >>> terms = term.ChoiceTerms(
  ...     ctx, request, None, IRating['rating'], ratingWidget)

Here we go:

  >>> missingTerm = terms.getTermByToken('42')

We get the term, we passed the token, the value is coming from the context.

  >>> missingTerm.token
  '42'
  >>> missingTerm.value
  42

We cannot figure the title, so we construct one.
Override ``makeMissingTerm`` if you want your own.

  >>> missingTerm.title
  'Missing: ${value}'

Still we raise LookupError if the token does not fit the context's value:

  >>> missingTerm = terms.getTermByToken('99')
  Traceback (most recent call last):
  ...
  LookupError: 99

The same goes with looking up a term by value.
We get the term if the context's value fits:

  >>> missingTerm = terms.getTerm(42)
  >>> missingTerm.token
  '42'

And an exception if it does not:

  >>> missingTerm = terms.getTerm(99)
  Traceback (most recent call last):
  ...
  LookupError: 99


Collections
+++++++++++

Finally, there are terms adapters for all collections:

  >>> sourceRatingsField = zope.schema.List(
  ...     title='Sourced Ratings',
  ...     value_type=sourceRatingField)

  >>> terms = term.CollectionTerms(
  ...     None, request, None, sourceRatingsField, widget)
  >>> [entry.title for entry in terms]
  ['ugly', 'nice', 'great']


Contextual sources
~~~~~~~~~~~~~~~~~~

Contextual sources depend on the context they are called on. Let's
create a context and a contextual source:

  >>> from zc.sourcefactory.contextual import BasicContextualSourceFactory
  >>> class RatingContext(object):
  ...     base_value = 10
  >>> class ContextualRatingSourceFactory(BasicContextualSourceFactory):
  ...     _mapping = {10: 'ugly', 20: 'nice', 30: 'great'}
  ...     def getValues(self, context):
  ...         return [context.base_value + x for x in self._mapping.keys()]
  ...     def getTitle(self, context, value):
  ...         return self._mapping[value - context.base_value]

As we did not include the configure.zcml of zc.sourcefactory we have
to register some required adapters manually. We also need the
ChoiceTermsSource adapter:

  >>> import zope.component
  >>> import zc.sourcefactory.browser.source
  >>> import zc.sourcefactory.browser.token
  >>> zope.component.provideAdapter(
  ...     zc.sourcefactory.browser.source.FactoredContextualTerms)
  >>> zope.component.provideAdapter(
  ...     zc.sourcefactory.browser.token.fromInteger)
  >>> zope.component.provideAdapter(term.ChoiceTermsSource)

Choice fields
+++++++++++++

Contextual sources can be used with ``Choice`` fields like
vocabularies.  First we create a field based on the source:

  >>> contextualSourceRatingField = zope.schema.Choice(
  ...     title='Context Sourced Rating',
  ...     source=ContextualRatingSourceFactory())

We create an context object and connect the field to a widget to see
the ITerms adapter for sources at work:

  >>> rating_context = RatingContext()
  >>> rating_context.base_value = 100
  >>> terms = term.ChoiceTerms(
  ...     rating_context, request, None, contextualSourceRatingField, widget)

Iterating over the terms adapter returnes the term objects:

  >>> [entry for entry in terms]
  [<zc.sourcefactory.browser.source.FactoredTerm object at 0x...>,
   <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>,
   <zc.sourcefactory.browser.source.FactoredTerm object at 0x...>]
  >>> len(terms)
  3
  >>> [entry.token for entry in terms]
  ['110', '120', '130']
  >>> [entry.title for entry in terms]
  ['ugly', 'nice', 'great']

Using a token, it is possible to look up the term and the value:

  >>> terms.getTermByToken('120').title
  'nice'
  >>> terms.getValue('130')
  130

With can test if a value is in the source:

  >>> 130 in terms
  True
  >>> 125 in terms
  False

Collections
+++++++++++

Finally, there are terms adapters for all collections:

  >>> contextualSourceRatingsField = zope.schema.List(
  ...     title='Contextual Sourced Ratings',
  ...     value_type=contextualSourceRatingField)

  >>> terms = term.CollectionTerms(
  ...     rating_context, request, None, contextualSourceRatingsField, widget)
  >>> [entry.title for entry in terms]
  ['ugly', 'nice', 'great']


Missing terms in collections
############################

Sometimes it happens that a value goes away from the source, but our
stored collection still has this value.

  >>> zope.component.provideAdapter(term.MissingCollectionTermsSource)

  >>> terms = term.CollectionTerms(
  ...     RatingContext(), request, None, contextualSourceRatingsField, widget)
  >>> terms
  <z3c.form.term.MissingCollectionTermsSource object at 0x...>
  >>> terms.getTermByToken('42')
  Traceback (most recent call last):
  ...
  LookupError: 42

The same goes with looking up a term by value:

  >>> terms.getTerm(42)
  Traceback (most recent call last):
  ...
  LookupError: 42

The same goes with looking up a value by the token:

  >>> terms.getValue('42')
  Traceback (most recent call last):
  ...
  LookupError: 42


Ooops, well this works only if the context has the right value for us.
This is because we don't want to accept any crap that's coming from HTML.

  >>> class IRatings(zope.interface.Interface):
  ...     ratings = zope.schema.List(
  ...         title='Contextual Sourced Ratings',
  ...         value_type=contextualSourceRatingField)
  >>> @zope.interface.implementer(IRatings)
  ... class Ratings(object):
  ...     ratings = None
  ...     base_value = 10

  >>> ctx = Ratings()
  >>> ctx.ratings = [42, 10]

  >>> ratingsWidget = z3c.form.widget.Widget(request)
  >>> ratingsWidget.context = ctx
  >>> from z3c.form import interfaces
  >>> zope.interface.alsoProvides(ratingsWidget, interfaces.IContextAware)
  >>> from z3c.form.datamanager import AttributeField
  >>> zope.component.provideAdapter(AttributeField)

  >>> terms = term.CollectionTerms(
  ...     ctx, request, None, IRatings['ratings'], ratingsWidget)

Here we go:

  >>> term = terms.getTerm(42)
  >>> missingTerm = terms.getTermByToken('42')

We get the term, we passed the token, the value is coming from the context.

  >>> missingTerm.token
  '42'
  >>> missingTerm.value
  42

We cannot figure the title, so we construct one.
Override ``makeMissingTerm`` if you want your own.

  >>> missingTerm.title
  'Missing: ${value}'

We can get the value for a missing term:

  >>> terms.getValue('42')
  42

Still we raise LookupError if the token does not fit the context's value:

  >>> missingTerm = terms.getTermByToken('99')
  Traceback (most recent call last):
  ...
  LookupError: 99

The same goes with looking up a term by value.
We get the term if the context's value fits:

  >>> missingTerm = terms.getTerm(42)
  >>> missingTerm.token
  '42'

And an exception if it does not:

  >>> missingTerm = terms.getTerm(99)
  Traceback (most recent call last):
  ...
  LookupError: 99
