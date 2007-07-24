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
import zope.schema
from zope.schema import vocabulary

from z3c.form import interfaces
from z3c.form.i18n import MessageFactory as _


class Terms(object):
    """Base implementationf or custom ITerms."""

    zope.interface.implements(interfaces.ITerms)

    def getTerm(self, value):
        return self.terms.getTerm(value)

    def getTermByToken(self, token):
        return self.terms.getTermByToken(token)

    def getValue(self, token):
        return self.terms.getTermByToken(token).value

    def __iter__(self):
        return iter(self.terms)

    def __len__(self):
        return self.terms.__len__()

    def __contains__(self, value):
        return self.terms.__contains__(value)


class ChoiceTerms(Terms):
    """ITerms adapter for zope.schema.IChoice based implementations."""

    zope.component.adapts(
        zope.interface.Interface,
        interfaces.IFormLayer,
        zope.interface.Interface,
        zope.schema.interfaces.IChoice,
        interfaces.IWidget)

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        if field.vocabulary is None:
            field = field.bind(context)
        self.terms = field.vocabulary


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


class CollectionTerms(Terms):
    """ITerms adapter for zope.schema.ICollection based implementations."""

    zope.component.adapts(
        zope.interface.Interface,
        interfaces.IFormLayer,
        zope.interface.Interface,
        zope.schema.interfaces.ICollection,
        interfaces.IWidget)

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.terms = field.value_type.bind(self.context).vocabulary
