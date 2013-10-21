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
"""Implementation of an addform for IAdding

$Id$
"""
__docformat__ = "reStructuredText"
from z3c.form import form

class AddForm(form.AddForm):
    """An addform for the IAdding interface."""

    def add(self, object):
        ob = self.context.add(object)
        self._finishedAdd = True
        return ob

    def nextURL(self):
        return self.context.nextURL()
