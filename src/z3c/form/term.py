##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Terms Implementation

$Id$
"""

import zope.browser.interfaces
import zope.component
import zope.interface
import zope.schema
from zope.schema import vocabulary

from z3c.form import interfaces
from z3c.form import util
from z3c.form.i18n import MessageFactory as _


@zope.interface.implementer(interfaces.ITerms)
class Terms(object):
    """Base implementation for custom ITerms."""

    def getTerm(self, value):
        return self.terms.getTerm(value)

    def getTermByToken(self, token):
        return self.terms.getTermByToken(token)

    def getValue(self, token):
        return self.getTermByToken(token).value

    def __iter__(self):
        return iter(self.terms)

    def __len__(self):
        return self.terms.__len__()

    def __contains__(self, value):
        return self.terms.__contains__(value)


@zope.interface.implementer(interfaces.ITerms)
class SourceTerms(Terms):
    """Base implementation for ITerms using a source instead of a vocabulary."""

    def __init__(self, context, request, form, field, source, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.source = source
        self.terms = zope.component.getMultiAdapter(
            (self.source, self.request),
            zope.browser.interfaces.ITerms)

    def getTerm(self, value):
        try:
            return super(SourceTerms, self).getTerm(value)
        except KeyError:
            raise LookupError(value)

    def getTermByToken(self, token):
        # This is rather expensive
        for value in self.source:
            term = self.getTerm(value)
            if term.token == token:
                return term
        raise LookupError(token)

    def getValue(self, token):
        try:
            return self.terms.getValue(token)
        except KeyError:
            raise LookupError(token)

    def __iter__(self):
        for value in self.source:
            yield self.terms.getTerm(value)

    def __len__(self):
        return len(self.source)

    def __contains__(self, value):
        return value in self.source


@zope.interface.implementer(interfaces.ITerms)
@zope.component.adapter(
    zope.interface.Interface,
    interfaces.IFormLayer,
    zope.interface.Interface,
    zope.schema.interfaces.IChoice,
    interfaces.IWidget)
def ChoiceTerms(context, request, form, field, widget):
    if field.context is None:
        field = field.bind(context)
    terms = field.vocabulary
    return zope.component.queryMultiAdapter(
        (context, request, form, field, terms, widget),
        interfaces.ITerms)


@zope.interface.implementer(interfaces.ITerms)
class ChoiceTermsVocabulary(Terms):
    """ITerms adapter for zope.schema.IChoice based implementations using
    vocabulary."""

    zope.component.adapts(
        zope.interface.Interface,
        interfaces.IFormLayer,
        zope.interface.Interface,
        zope.schema.interfaces.IChoice,
        zope.schema.interfaces.IBaseVocabulary,
        interfaces.IWidget)

    def __init__(self, context, request, form, field, vocabulary, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.terms = vocabulary


class MissingTermsBase(object):
    """Base class for MissingTermsMixin classes."""

    def _canQueryCurrentValue(self):
        return (interfaces.IContextAware.providedBy(self.widget) and
                not self.widget.ignoreContext)

    def _queryCurrentValue(self):
        return zope.component.getMultiAdapter(
            (self.widget.context, self.field),
            interfaces.IDataManager).query()

    def _makeToken(self, value):
        """create a unique valid ASCII token"""
        return util.createCSSId(util.toUnicode(value))

    def _makeMissingTerm(self, value):
        """Return a term that should be displayed for the missing token"""
        uvalue = util.toUnicode(value)
        return vocabulary.SimpleTerm(
            value, self._makeToken(value),
            title=_(u'Missing: ${value}', mapping=dict(value=uvalue)))


class MissingTermsMixin(MissingTermsBase):
    """This can be used in case previous values/tokens get missing
    from the vocabulary and you still need to display/keep the values"""

    def getTerm(self, value):
        try:
            return super(MissingTermsMixin, self).getTerm(value)
        except LookupError:
            if self._canQueryCurrentValue():
                curValue = self._queryCurrentValue()
                if curValue == value:
                    return self._makeMissingTerm(value)
            raise

    def getTermByToken(self, token):
        try:
            return super(MissingTermsMixin, self).getTermByToken(token)
        except LookupError:
            if self._canQueryCurrentValue():
                value = self._queryCurrentValue()
                term = self._makeMissingTerm(value)
                if term.token == token:
                    # check if the given token matches the value, if not
                    # fall back on LookupError, otherwise we might accept
                    # any crap coming from the request
                    return term

            raise LookupError(token)


class MissingChoiceTermsVocabulary(MissingTermsMixin, ChoiceTermsVocabulary):
    """ITerms adapter for zope.schema.IChoice based implementations using
    vocabulary with missing terms support"""


@zope.interface.implementer(interfaces.ITerms)
class ChoiceTermsSource(SourceTerms):
    "ITerms adapter for zope.schema.IChoice based implementations using source."

    zope.component.adapts(
        zope.interface.Interface,
        interfaces.IFormLayer,
        zope.interface.Interface,
        zope.schema.interfaces.IChoice,
        zope.schema.interfaces.IIterableSource,
        interfaces.IWidget)


class MissingChoiceTermsSource(MissingTermsMixin, ChoiceTermsSource):
    """ITerms adapter for zope.schema.IChoice based implementations using source
       with missing terms support."""


@zope.interface.implementer_only(interfaces.IBoolTerms)
class BoolTerms(Terms):
    """Default yes and no terms are used by default for IBool fields."""

    zope.component.adapts(
        zope.interface.Interface,
        interfaces.IFormLayer,
        zope.interface.Interface,
        zope.schema.interfaces.IBool,
        interfaces.IWidget)

    trueLabel = _('yes')
    falseLabel = _('no')

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        terms = [vocabulary.SimpleTerm(*args)
                 for args in [(True, 'true', self.trueLabel),
                              (False, 'false', self.falseLabel)]]
        self.terms = vocabulary.SimpleVocabulary(terms)


@zope.interface.implementer(interfaces.ITerms)
@zope.component.adapter(
    zope.interface.Interface,
    interfaces.IFormLayer,
    zope.interface.Interface,
    zope.schema.interfaces.ICollection,
    interfaces.IWidget)
def CollectionTerms(context, request, form, field, widget):
    terms = field.value_type.bind(context).vocabulary
    return zope.component.queryMultiAdapter(
        (context, request, form, field, terms, widget),
        interfaces.ITerms)


class CollectionTermsVocabulary(Terms):
    """ITerms adapter for zope.schema.ICollection based implementations using
    vocabulary."""

    zope.component.adapts(
        zope.interface.Interface,
        interfaces.IFormLayer,
        zope.interface.Interface,
        zope.schema.interfaces.ICollection,
        zope.schema.interfaces.IBaseVocabulary,
        interfaces.IWidget)

    def __init__(self, context, request, form, field, vocabulary, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.terms = vocabulary


class MissingCollectionTermsMixin(MissingTermsBase):
    """`MissingTermsMixin` adapted to collections."""

    def getTerm(self, value):
        try:
            return super(MissingCollectionTermsMixin, self).getTerm(value)
        except LookupError:
            if self._canQueryCurrentValue():
                if value in self._queryCurrentValue():
                    return self._makeMissingTerm(value)
            raise

    def getTermByToken(self, token):
        try:
            return super(
                MissingCollectionTermsMixin, self).getTermByToken(token)
        except LookupError:
            if self._canQueryCurrentValue():
                for value in self._queryCurrentValue():
                    term = self._makeMissingTerm(value)
                    if term.token == token:
                        # check if the given token matches the value, if not
                        # fall back on LookupError, otherwise we might accept
                        # any crap coming from the request
                        return term
            raise

    def getValue(self, token):
        try:
            return super(MissingCollectionTermsMixin, self).getValue(token)
        except LookupError:
            if self._canQueryCurrentValue():
                for value in self._queryCurrentValue():
                    term = self._makeMissingTerm(value)
                    if term.token == token:
                        # check if the given token matches the value, if not
                        # fall back on LookupError, otherwise we might accept
                        # any crap coming from the request
                        return value
            raise


class MissingCollectionTermsVocabulary(MissingCollectionTermsMixin,
                                       CollectionTermsVocabulary):
    """ITerms adapter for zope.schema.ICollection based implementations using
    vocabulary with missing terms support."""


@zope.interface.implementer(interfaces.ITerms)
class CollectionTermsSource(SourceTerms):
    """ITerms adapter for zope.schema.ICollection based implementations using
    source."""

    zope.component.adapts(
        zope.interface.Interface,
        interfaces.IFormLayer,
        zope.interface.Interface,
        zope.schema.interfaces.ICollection,
        zope.schema.interfaces.IIterableSource,
        interfaces.IWidget)


class MissingCollectionTermsSource(MissingCollectionTermsMixin,
                                   CollectionTermsSource):
    """ITerms adapter for zope.schema.ICollection based implementations using
    source with missing terms support."""
