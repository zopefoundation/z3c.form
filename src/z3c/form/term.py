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

import zope.browser
import zope.component
import zope.schema
from zope.schema import vocabulary

from z3c.form import interfaces
from z3c.form.i18n import MessageFactory as _


class Terms(object):
    """Base implementation for custom ITerms."""

    zope.interface.implements(interfaces.ITerms)

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


class SourceTerms(Terms):
    """Base implementation for ITerms using a source instead of a vocabulary."""

    zope.interface.implements(interfaces.ITerms)

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

    def getTermByToken(self, token):
        # This is rather expensive
        for value in self.source:
            term = self.getTerm(value)
            if term.token == token:
                return term

    def getValue(self, token):
        return self.terms.getValue(token)

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
    field = field.bind(context)
    terms = field.vocabulary
    return zope.component.queryMultiAdapter(
        (context, request, form, field, terms, widget),
        interfaces.ITerms)


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

    zope.interface.implements(interfaces.ITerms)

    def __init__(self, context, request, form, field, vocabulary, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.terms = vocabulary


class MissingTermsMixin(object):
    """This can be used in case previous values/tokens get missing
    from the vocabulary and you still need to display/keep the values"""

    def getTerm(self, value):
        try:
            return self.terms.getTerm(value)
        except LookupError:
            return self.makeMissingTerm(value)

    def makeToken(self, value):
        return unicode(value).encode('utf8').encode('base64').strip()

    def makeMissingTerm(self, value, token=None):
        """Return a term that should be displayed for the missing token or
        raise LookupError if it's really invalid"""
        if token is None:
            token = self.makeToken(value)
        return vocabulary.SimpleTerm(value, token,
            title=_(u'Missing: ${value}', mapping=dict(value=unicode(value))))

    def getTermByToken(self, token):
        try:
            return self.terms.getTermByToken(token)
        except LookupError:
            if (interfaces.IContextAware.providedBy(self.widget) and
                not self.widget.ignoreContext):
                value = zope.component.getMultiAdapter(
                    (self.widget.context, self.widget.field),
                    interfaces.IDataManager).query()
                return self.makeMissingTerm(value, token=token)

            raise LookupError(token)


class MissingChoiceTermsVocabulary(MissingTermsMixin, ChoiceTermsVocabulary):
    """ITerms adapter for zope.schema.IChoice based implementations using
    vocabulary with missing terms support"""

    zope.component.adapts(
        zope.interface.Interface,
        interfaces.IFormLayer,
        zope.interface.Interface,
        interfaces.IForgivingChoice,
        zope.schema.interfaces.IBaseVocabulary,
        interfaces.IWidget)


class ChoiceTermsSource(SourceTerms):
    "ITerms adapter for zope.schema.IChoice based implementations using source."

    zope.component.adapts(
        zope.interface.Interface,
        interfaces.IFormLayer,
        zope.interface.Interface,
        zope.schema.interfaces.IChoice,
        zope.schema.interfaces.IIterableSource,
        interfaces.IWidget)

    zope.interface.implements(interfaces.ITerms)


class BoolTerms(Terms):
    """Default yes and no terms are used by default for IBool fields."""

    zope.component.adapts(
        zope.interface.Interface,
        interfaces.IFormLayer,
        zope.interface.Interface,
        zope.schema.interfaces.IBool,
        interfaces.IWidget)

    zope.interface.implementsOnly(interfaces.IBoolTerms)

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


class MissingCollectionTermsVocabulary(MissingTermsMixin,
                                       CollectionTermsVocabulary):
    """ITerms adapter for zope.schema.ICollection based implementations using
    vocabulary with missing terms support."""


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

    zope.interface.implements(interfaces.ITerms)
