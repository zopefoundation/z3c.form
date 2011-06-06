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
        import z3c.form.field
        import z3c.form.form
        import zope.schema
        import zope.interface

        class TestInterface(zope.interface.Interface):
            text = zope.schema.TextLine(title=u'text')

        class TestForm(z3c.form.form.BaseForm):
            fields = z3c.form.field.Fields(TestInterface)

        # content is an empty dict, the `text` key does not yet exist
        content = dict()
        form = TestForm(content, request=None)
        data = dict(text='a')
        changes = z3c.form.form.applyChanges(form, content, data)
        self.assertEqual({TestInterface: ['text']}, changes)
        self.assertEqual({'text': 'a'}, content)


def test_suite():
    return unittest.makeSuite(TestApplyChangesDictDatamanager)
