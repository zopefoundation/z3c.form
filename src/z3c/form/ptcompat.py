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
"""z3c.pt optional compatibility

$Id$
"""
__docformat__ = "reStructuredText"

try:
    from z3c.ptcompat import ViewPageTemplateFile
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

if AVAILABLE:
    #ViewPageTemplateFile = ptcompat.ViewPageTemplateFile
    from z3c.ptcompat import bind_template
else:
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
    from zope.app.pagetemplate.viewpagetemplatefile import BoundPageTemplate \
         as bind_template
