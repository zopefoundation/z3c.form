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
"""Common z3c.form test setups"""

import os
import zope.component
import zope.configuration.xmlconfig
import zope.interface
import zope.schema

from doctest import register_optionflag
from zope.app.testing import setup
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import TestRequest
from zope.schema.fieldproperty import FieldProperty
from zope.security import checker
from zope.security.interfaces import IInteraction
from zope.security.interfaces import ISecurityPolicy

from z3c.form import browser, button, converter, datamanager, error, field
from z3c.form import form, interfaces, term, validator, widget
from z3c.form import contentprovider
from z3c.form.browser import radio, select, text, textarea

import lxml.html
import lxml.doctestcompare

# register lxml doctest option flags
lxml.doctestcompare.NOPARSE_MARKUP = register_optionflag('NOPARSE_MARKUP')

class TestingFileUploadDataConverter(converter.FileUploadDataConverter):
    """A special file upload data converter that works with testing."""
    zope.component.adapts(
        zope.schema.interfaces.IBytes, interfaces.IFileWidget)

    def toFieldValue(self, value):
        if value is None or value == '':
            value = self.widget.request.get(self.widget.name+'.testing', '')
            encoding = self.widget.request.get(
                self.widget.name+'.encoding', 'plain')

            # allow for the case where the file contents are base64 encoded.
            if encoding!='plain':
                value = value.decode(encoding)
            self.widget.request.form[self.widget.name] = value

        return super(TestingFileUploadDataConverter, self).toFieldValue(value)

class TestRequest(TestRequest):
    zope.interface.implements(interfaces.IFormLayer)

class SimpleSecurityPolicy(object):
    """Allow all access."""
    zope.interface.implements(IInteraction)
    zope.interface.classProvides(ISecurityPolicy)

    loggedIn = False
    allowedPermissions = ()

    def __init__(self, loggedIn=False, allowedPermissions=()):
        self.loggedIn = loggedIn
        self.allowedPermissions = allowedPermissions + (checker.CheckerPublic,)

    def __call__(self, *participations):
        self.participations = []
        return self

    def checkPermission(self, permission, object):
        if self.loggedIn:
            if permission in self.allowedPermissions:
                return True
        return False

def getPath(filename):
    return os.path.join(os.path.dirname(browser.__file__), filename)


#############################
# classes required by ObjectWidget tests
#

class IMySubObject(zope.interface.Interface):
    foofield = zope.schema.Int(
        title=u"My foo field",
        default=1111,
        max=9999,
        required=True)
    barfield = zope.schema.Int(
        title=u"My dear bar",
        default=2222,
        required=False)

class MySubObject(object):
    zope.interface.implements(IMySubObject)

    foofield = FieldProperty(IMySubObject['foofield'])
    barfield = FieldProperty(IMySubObject['barfield'])

class IMySecond(zope.interface.Interface):
    subfield = zope.schema.Object(
        title=u"Second-subobject",
        schema=IMySubObject)
    moofield = zope.schema.TextLine(title=u"Something")

class MySecond(object):
    zope.interface.implements(IMySecond)

    subfield = FieldProperty(IMySecond['subfield'])
    moofield = FieldProperty(IMySecond['moofield'])


class IMyObject(zope.interface.Interface):
    subobject = zope.schema.Object(title=u'my object', schema=IMySubObject)
    name = zope.schema.TextLine(title=u'name')

class MyObject(object):
    zope.interface.implements(IMyObject)
    def __init__(self, name=u'', subobject=None):
        self.subobject=subobject
        self.name=name


class IMyComplexObject(zope.interface.Interface):
    subobject = zope.schema.Object(title=u'my object', schema=IMySecond)
    name = zope.schema.TextLine(title=u'name')


class IMySubObjectMulti(zope.interface.Interface):
    foofield = zope.schema.Int(
        title=u"My foo field",
        default=None, #default is None here!
        max=9999,
        required=True)
    barfield = zope.schema.Int(
        title=u"My dear bar",
        default=2222,
        required=False)

class MySubObjectMulti(object):
    zope.interface.implements(IMySubObjectMulti)

    foofield = FieldProperty(IMySubObjectMulti['foofield'])
    barfield = FieldProperty(IMySubObjectMulti['barfield'])

class IMyMultiObject(zope.interface.Interface):
    listOfObject = zope.schema.List(
        title = u"My list field",
        value_type = zope.schema.Object(
            title=u'my object widget',
            schema=IMySubObjectMulti),
    )
    name = zope.schema.TextLine(title=u'name')

class MyMultiObject(object):
    zope.interface.implements(IMyMultiObject)

    listOfObject = FieldProperty(IMyMultiObject['listOfObject'])
    name = FieldProperty(IMyMultiObject['name'])

    def __init__(self, name=u'', listOfObject=None):
        self.listOfObject = listOfObject
        self.name = name

#
#
#############################

def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}

def setUpZPT(suite):
    setUp(suite)

def setUpZ3CPT(suite):
    import z3c.pt
    import z3c.ptcompat
    setUp(suite)
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.pt)()
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.ptcompat)()

def setupFormDefaults():
    # Validator adapters
    zope.component.provideAdapter(validator.SimpleFieldValidator)
    zope.component.provideAdapter(validator.InvariantsValidator)
    # Data manager adapter to get and set values to content
    zope.component.provideAdapter(datamanager.AttributeField)
    # Adapter to use form.fields to generate widgets
    zope.component.provideAdapter(field.FieldWidgets)
    # Adapter that uses form.fields to generate widgets
    # AND interlace content providers
    zope.component.provideAdapter(contentprovider.FieldWidgetsAndProviders)
    # Adapters to lookup the widget for a field
    # Text Field Widget
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IBytesLine, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IASCIILine, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.ITextLine, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IId, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IInt, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IFloat, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IDecimal, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IDate, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IDatetime, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.ITime, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.ITimedelta, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IURI, interfaces.IFormLayer))
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('text_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.ITextWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('text_display.pt'), 'text/html'),
        (None, None, None, None, interfaces.ITextWidget),
        IPageTemplate, name=interfaces.DISPLAY_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('text_hidden.pt'), 'text/html'),
        (None, None, None, None, interfaces.ITextWidget),
        IPageTemplate, name=interfaces.HIDDEN_MODE)

    # Textarea Field Widget
    zope.component.provideAdapter(
        textarea.TextAreaFieldWidget,
        adapts=(zope.schema.interfaces.IASCII, interfaces.IFormLayer))
    zope.component.provideAdapter(
        textarea.TextAreaFieldWidget,
        adapts=(zope.schema.interfaces.IText, interfaces.IFormLayer))
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('textarea_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.ITextAreaWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('textarea_display.pt'), 'text/html'),
        (None, None, None, None, interfaces.ITextAreaWidget),
        IPageTemplate, name=interfaces.DISPLAY_MODE)

    # Radio Field Widget
    zope.component.provideAdapter(radio.RadioFieldWidget)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('radio_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.IRadioWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('radio_display.pt'), 'text/html'),
        (None, None, None, None, interfaces.IRadioWidget),
        IPageTemplate, name=interfaces.DISPLAY_MODE)

    # Select Widget
    zope.component.provideAdapter(select.ChoiceWidgetDispatcher)
    zope.component.provideAdapter(select.SelectFieldWidget)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('select_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.ISelectWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('select_display.pt'), 'text/html'),
        (None, None, None, None, interfaces.ISelectWidget),
        IPageTemplate, name=interfaces.DISPLAY_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('select_hidden.pt'), 'text/html'),
        (None, None, None, None, interfaces.ISelectWidget),
        IPageTemplate, name=interfaces.HIDDEN_MODE)

    # Checkbox Field Widget; register only templates
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('checkbox_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.ICheckBoxWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(
        getPath('checkbox_display.pt'), 'text/html'),
        (None, None, None, None, interfaces.ICheckBoxWidget),
        IPageTemplate, name=interfaces.DISPLAY_MODE)
    # Submit Field Widget
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('submit_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.ISubmitWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    # selectwidget helper adapters
    zope.component.provideAdapter(select.CollectionSelectFieldWidget)
    zope.component.provideAdapter(select.CollectionChoiceSelectFieldWidget)
    # Adapter to  convert between field/internal and widget values
    zope.component.provideAdapter(converter.FieldDataConverter)
    zope.component.provideAdapter(converter.SequenceDataConverter)
    zope.component.provideAdapter(converter.CollectionSequenceDataConverter)
    zope.component.provideAdapter(converter.FieldWidgetDataConverter)
    # special data converter
    zope.component.provideAdapter(converter.IntegerDataConverter)
    zope.component.provideAdapter(converter.FloatDataConverter)
    zope.component.provideAdapter(converter.DecimalDataConverter)
    zope.component.provideAdapter(converter.DateDataConverter)
    zope.component.provideAdapter(converter.TimeDataConverter)
    zope.component.provideAdapter(converter.DatetimeDataConverter)
    zope.component.provideAdapter(converter.TimedeltaDataConverter)
    # Adapter for providing terms to radio list and other widgets
    zope.component.provideAdapter(term.BoolTerms)
    zope.component.provideAdapter(term.ChoiceTerms)
    zope.component.provideAdapter(term.ChoiceTermsVocabulary)
    zope.component.provideAdapter(term.ChoiceTermsSource)
    zope.component.provideAdapter(term.CollectionTerms)
    zope.component.provideAdapter(term.CollectionTermsVocabulary)
    zope.component.provideAdapter(term.CollectionTermsSource)
    # Adapter to create an action from a button
    zope.component.provideAdapter(
        button.ButtonAction, provides=interfaces.IButtonAction)
    # Adapter to use form.buttons to generate actions
    zope.component.provideAdapter(button.ButtonActions)
    # Adapter to use form.handlers to generate handle actions
    zope.component.provideAdapter(button.ButtonActionHandler)
    # Subscriber handling action execution error events
    zope.component.provideHandler(form.handleActionError)
    # Error View(s)
    zope.component.provideAdapter(error.ErrorViewSnippet)
    zope.component.provideAdapter(error.InvalidErrorViewSnippet)
    zope.component.provideAdapter(error.StandardErrorViewTemplate)

def tearDown(test):
    setup.placefulTearDown()


##########################
def render(view, xpath='.'):
    method = getattr(view, 'render', None)
    if method is None:
        method = view.__call__

    string = method()
    if string == "":
        return string

    try:
        root = lxml.etree.fromstring(string)
    except lxml.etree.XMLSyntaxError:
        root = lxml.html.fromstring(string)

    output = ""
    for node in root.xpath(
        xpath, namespaces={'xmlns': 'http://www.w3.org/1999/xhtml'}):
        s = lxml.etree.tounicode(node, pretty_print=True)
        s = s.replace(' xmlns="http://www.w3.org/1999/xhtml"', ' ')
        output += s

    if not output:
        raise ValueError("No elements matched by %s." % repr(xpath))

    # let's get rid of blank lines
    output = output.replace('\n\n', '\n')

    # self-closing tags are more readable with a space before the
    # end-of-tag marker
    output = output.replace('"/>', '" />')

    return output
