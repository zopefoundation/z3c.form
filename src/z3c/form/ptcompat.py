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

#import utilities from z3c.ptcompat when available and set AVAILABLE flag

AVAILABLE = False
Z3CPT_AVAILABLE = False

try:
    from z3c.ptcompat import ViewPageTemplateFile
    from z3c.ptcompat import bind_template
    AVAILABLE = True
except ImportError:
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
    from zope.app.pagetemplate.viewpagetemplatefile import BoundPageTemplate \
         as bind_template

try:
    import z3c.pt
    Z3CPT_AVAILABLE = True
except ImportError:
    pass
