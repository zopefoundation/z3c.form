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
"""Unittests for bug fixes."""

import unittest


class TestApplyChangesDictDatamanager(unittest.TestCase):
    # z3c.form.form.applyChanges could not write a value into an empty
    # content dict it got an AttributeError while accessing
    # datamanger.get(). This test makes sure that a dictionary content
    # does not need to be initialized with all keys which might be
    # written on it later on. (This was the behavior before
    # datamanger.DictionaryField.get() raised an AttributeError on not
    # existing keys.

    def setUp(self):
        import zope.component
        import zope.interface

        import z3c.form.datamanager

        zope.component.provideAdapter(
            z3c.form.datamanager.DictionaryField,
            (dict, zope.interface.Interface))

    def tearDown(self):
        import zope.component.globalregistry

        import z3c.form.datamanager

        zope.component.globalregistry.getGlobalSiteManager().unregisterAdapter(
            z3c.form.datamanager.DictionaryField,
            (dict, zope.interface.Interface))

    def test_applyChanges(self):
        import zope.interface
        import zope.schema

        import z3c.form.field
        import z3c.form.form

        class TestInterface(zope.interface.Interface):
            text = zope.schema.TextLine(title='text')

        class TestForm(z3c.form.form.BaseForm):
            fields = z3c.form.field.Fields(TestInterface)

        # content is an empty dict, the `text` key does not yet exist
        content = dict()
        form = TestForm(content, request=None)
        data = dict(text='a')
        changes = z3c.form.form.applyChanges(form, content, data)
        self.assertEqual({TestInterface: ['text']}, changes)
        self.assertEqual({'text': 'a'}, content)


class Mock:
    pass


class MockNumberFormatter:
    def format(self, value):
        if value is None:
            # execution should never get here
            raise ValueError('Cannot format None')
        return str(value)


class MockLocale:
    def getFormatter(self, category):
        return MockNumberFormatter()


class OurNone:
    def __eq__(self, other):
        return isinstance(other, (type(None), OurNone))


OUR_NONE = OurNone()
# OUR_NONE == None
# but
# OUR_NONE is not None


class ConverterFixTests(unittest.TestCase):
    # most of the time `==` and `is` works the same
    # unless you have some custom or mutable values

    def test_BaseDataConverter_toWidgetValue(self):
        from z3c.form.converter import BaseDataConverter

        field = Mock()
        field.missing_value = None
        bdc = BaseDataConverter(field, None)
        self.assertEqual(bdc.toWidgetValue(''), '')
        self.assertEqual(bdc.toWidgetValue(None), '')
        self.assertEqual(bdc.toWidgetValue([]), '[]')

        field.missing_value = []
        self.assertEqual(bdc.toWidgetValue(''), '')
        self.assertEqual(bdc.toWidgetValue(None), 'None')
        self.assertEqual(bdc.toWidgetValue([]), '')

    def test_NumberDataConverter_toWidgetValue(self):
        from z3c.form.converter import NumberDataConverter

        field = Mock()
        field.missing_value = None
        widget = Mock()
        widget.request = Mock()
        widget.request.locale = Mock()
        widget.request.locale.numbers = MockLocale()
        ndc = NumberDataConverter(field, widget)
        self.assertEqual(ndc.toWidgetValue(''), '')
        self.assertEqual(ndc.toWidgetValue(None), '')
        # here is the real deal, OUR_NONE should be considered as None
        self.assertEqual(ndc.toWidgetValue(OUR_NONE), '')
        self.assertEqual(ndc.toWidgetValue([]), '[]')

        field.missing_value = OUR_NONE
        self.assertEqual(ndc.toWidgetValue(''), '')
        self.assertEqual(ndc.toWidgetValue(None), '')
        self.assertEqual(ndc.toWidgetValue(OUR_NONE), '')
        self.assertEqual(ndc.toWidgetValue([]), '[]')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
