##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Form and Widget Framework Interfaces

$Id: interfaces.py 90925 2008-09-08 06:30:06Z hermann $
"""
__docformat__ = "reStructuredText"
import config

if config.PREFER_Z3C_PT:
    from z3c.pt.pagetemplate import ViewPageTemplateFile

    def bind_template(pt, view):
        return pt.bind(view)
else:
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
    from zope.app.pagetemplate.viewpagetemplatefile import BoundPageTemplate
    bind_template = BoundPageTemplate

class ViewPageTemplateFile(ViewPageTemplateFile):
    pass
