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
from __future__ import print_function
import base64
import pprint
import os
import re
import six
import shutil
import zope.browserresource
import zope.component
import zope.configuration.xmlconfig
import zope.interface
import zope.schema

from doctest import register_optionflag
from zope.browserpage.viewpagetemplatefile import BoundPageTemplate
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import TestRequest
from zope.schema.fieldproperty import FieldProperty
from zope.security import checker
from zope.security.interfaces import IInteraction
from zope.security.interfaces import ISecurityPolicy

import z3c.form
from z3c.form import browser, button, converter, datamanager, error, field
from z3c.form import form, interfaces, term, validator, widget
from z3c.form import contentprovider
from z3c.form import outputchecker
from z3c.form import tests
from z3c.form.browser import radio, select, text, textarea

import lxml.html
import lxml.doctestcompare

# register lxml doctest option flags
lxml.doctestcompare.NOPARSE_MARKUP = register_optionflag('NOPARSE_MARKUP')

outputChecker = outputchecker.OutputChecker(
    patterns =(
        # Py3 compatibility.
        (re.compile("u('.*?')"), r"\1"),
        (re.compile("b('.*?')"), r"\1"),
        (re.compile("__builtin__"), r"builtins"),
        (re.compile("<type"), r"<class"),
        (re.compile("set\(\[(.*?)\]\)"), r"{\1}"),
    )
)

class TestingFileUploadDataConverter(converter.FileUploadDataConverter):
    """A special file upload data converter that works with testing."""
    zope.component.adapts(
        zope.schema.interfaces.IBytes, interfaces.IFileWidget)

    def toFieldValue(self, value):
        if value is None or value == '':
            value = self.widget.request.get(self.widget.name + '.testing', '')
            encoding = self.widget.request.get(
                self.widget.name + '.encoding', 'plain')

            # allow for the case where the file contents are base64 encoded.
            if encoding == 'base64':
                value = base64.b64decode(value)
            self.widget.request.form[self.widget.name] = value

        return super(TestingFileUploadDataConverter, self).toFieldValue(value)


@zope.interface.implementer(interfaces.IFormLayer)
class TestRequest(TestRequest):
    def __init__(self, body_instream=None, environ=None, form=None,
                 skin=None, **kw):
        if form is not None:
            lists = {}
            for k in list(form.keys()):
                if isinstance(form[k], six.string_types):
                    # ensure unicode otherwise z3c.forms burps on str
                    form[k] = six.text_type(form[k])

                if k.endswith(':list'):
                    key = k.split(':', 1)[0]
                    lists.setdefault(key, []).append(form[k])
                    del form[k]

            form.update(lists)

        super(TestRequest, self).__init__(
            body_instream, environ, form, skin, **kw)


@zope.interface.implementer(IInteraction)
@zope.interface.provider(ISecurityPolicy)
class SimpleSecurityPolicy(object):
    """Allow all access."""

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


@zope.interface.implementer(IMySubObject)
class MySubObject(object):

    foofield = FieldProperty(IMySubObject['foofield'])
    barfield = FieldProperty(IMySubObject['barfield'])


class IMySecond(zope.interface.Interface):
    subfield = zope.schema.Object(
        title=u"Second-subobject",
        schema=IMySubObject)
    moofield = zope.schema.TextLine(title=u"Something")


@zope.interface.implementer(IMySecond)
class MySecond(object):

    subfield = FieldProperty(IMySecond['subfield'])
    moofield = FieldProperty(IMySecond['moofield'])


class IMyObject(zope.interface.Interface):
    subobject = zope.schema.Object(title=u'my object', schema=IMySubObject)
    name = zope.schema.TextLine(title=u'name')


@zope.interface.implementer(IMyObject)
class MyObject(object):

    def __init__(self, name=u'', subobject=None):
        self.subobject = subobject
        self.name = name


class IMyComplexObject(zope.interface.Interface):
    subobject = zope.schema.Object(title=u'my object', schema=IMySecond)
    name = zope.schema.TextLine(title=u'name')


class IMySubObjectMulti(zope.interface.Interface):
    foofield = zope.schema.Int(
        title=u"My foo field",
        default=None,  # default is None here!
        max=9999,
        required=True)
    barfield = zope.schema.Int(
        title=u"My dear bar",
        default=2222,
        required=False)


@zope.interface.implementer(IMySubObjectMulti)
class MySubObjectMulti(object):

    foofield = FieldProperty(IMySubObjectMulti['foofield'])
    barfield = FieldProperty(IMySubObjectMulti['barfield'])


class IMyMultiObject(zope.interface.Interface):
    listOfObject = zope.schema.List(
        title=u"My list field",
        value_type=zope.schema.Object(
            title=u'my object widget',
            schema=IMySubObjectMulti),
    )
    name = zope.schema.TextLine(title=u'name')


@zope.interface.implementer(IMyMultiObject)
class MyMultiObject(object):

    listOfObject = FieldProperty(IMyMultiObject['listOfObject'])
    name = FieldProperty(IMyMultiObject['name'])

    def __init__(self, name=u'', listOfObject=None):
        self.listOfObject = listOfObject
        self.name = name


def setUp(test):
    from zope.component.testing import setUp
    setUp()
    from zope.container.testing import setUp
    setUp()
    from zope.component import hooks
    hooks.setHooks()
    from zope.traversing.testing import setUp
    setUp()

    from zope.publisher.browser import BrowserLanguages
    from zope.publisher.interfaces.http import IHTTPRequest
    from zope.i18n.interfaces import IUserPreferredLanguages
    zope.component.provideAdapter(BrowserLanguages, [IHTTPRequest],
                   IUserPreferredLanguages)

    from zope.site.folder import rootFolder
    site = rootFolder()
    from zope.site.site import LocalSiteManager
    from zope.component.interfaces import ISite
    if not ISite.providedBy(site):
        site.setSiteManager(LocalSiteManager(site))
    hooks.setSite(site)
    test.globs = {
        'print_function': print_function,
        'root': site,
        'pprint': pprint.pprint}


def setUpZPT(suite):
    setUp(suite)


def setUpZ3CPT(suite):
    import z3c.pt
    import z3c.ptcompat
    setUp(suite)
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.pt)()
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.ptcompat)()


def setUpIntegration(test):
    setUp(test)
    zope.configuration.xmlconfig.XMLConfig('meta.zcml', zope.component)()
    zope.configuration.xmlconfig.XMLConfig('meta.zcml', zope.security)()
    zope.configuration.xmlconfig.XMLConfig('meta.zcml', zope.i18n)()
    zope.configuration.xmlconfig.XMLConfig('meta.zcml', zope.browserresource)()
    zope.configuration.xmlconfig.XMLConfig('meta.zcml', z3c.form)()
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.form)()


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

    # Widget Layout
    zope.component.provideAdapter(
        widget.WidgetLayoutFactory(getPath('widget_layout.pt'), 'text/html'),
        (None, None, None, None, interfaces.IWidget),
        interfaces.IWidgetLayoutTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetLayoutFactory(getPath('widget_layout.pt'), 'text/html'),
        (None, None, None, None, interfaces.IWidget),
        interfaces.IWidgetLayoutTemplate, name=interfaces.DISPLAY_MODE)
    zope.component.provideAdapter(
        widget.WidgetLayoutFactory(getPath('widget_layout_hidden.pt'), 'text/html'),
        (None, None, None, None, interfaces.IWidget),
        interfaces.IWidgetLayoutTemplate, name=interfaces.HIDDEN_MODE)

    # Text Field Widget
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
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('radio_input_single.pt'),
                                     'text/html'),
        (None, None, None, None, interfaces.IRadioWidget),
        IPageTemplate, name='input_single')
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('radio_hidden_single.pt'),
                                     'text/html'),
        (None, None, None, None, interfaces.IRadioWidget),
        IPageTemplate, name='hidden_single')

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
    from zope.testing import cleanup
    from zope.component import hooks
    cleanup.cleanUp()
    hooks.resetHooks()
    hooks.setSite()


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


def textOfWithOptionalTitle(node, addTitle=False, showTooltips=False):
    if isinstance(node, (list, tuple)):
        return '\n'.join(textOfWithOptionalTitle(child, addTitle, showTooltips)
                         for child in node)
    text = []
    if node is None:
        return None

    if node.tag == 'br':
        return '\n'
    if node.tag == 'input':
        if addTitle:
            title = node.get('name') or ''
            title += ' '
        else:
            title = ''
        if node.get('type') == 'radio':
            return title + ('(O)' if node.get('checked') else '( )')
        if node.get('type') == 'checkbox':
            return title + ('[x]' if node.get('checked') else '[ ]')
        if node.get('type') == 'hidden':
            return ''
        else:
            return '%s[%s]' % (title, node.get('value') or '')
    if node.tag == 'textarea':
        if addTitle:
            title = node.get('name') or ''
            title += ' '
            text.append(title)
    if node.tag == 'select':
        if addTitle:
            title = node.get('name') or ''
            title += ' '
        else:
            title = ''
        option = node.find('option[@selected]')
        return '%s[%s]' % (title, option.text if option is not None
                                  else '[    ]')
    if node.tag == 'li':
        text.append('*')
    if node.tag == 'script':
        return

    if node.text and node.text.strip():
        text.append(node.text.strip())

    for n, child in enumerate(node):
        s = textOfWithOptionalTitle(child, addTitle, showTooltips)
        if s:
            text.append(s)
        if child.tail and child.tail.strip():
            text.append(child.tail)
    text = ' '.join(text).strip()
    # 'foo<br>bar' ends up as 'foo \nbar' due to the algorithm used above
    text = text.replace(' \n', '\n').replace('\n ', '\n').replace('\n\n', '\n')
    if u'\xA0' in text:
        # don't just .replace, that'll sprinkle my tests with u''
        text = text.replace(u'\xA0', ' ')  # nbsp -> space
    if node.tag == 'li':
        text += '\n'
    if node.tag == 'div':
        text += '\n'
    return text


def textOf(node):
    """Return the contents of an HTML node as text.

    Useful for functional tests, e.g. ::

        print map(textOf, browser.etree.xpath('.//td'))

    """
    return textOfWithOptionalTitle(node, False)


def plainText(content, xpath=None):
    root = lxml.html.fromstring(content)
    if xpath is not None:
        nodes = root.xpath(xpath)
        joinon = '\n'
    else:
        nodes = root
        joinon = ''
    text = joinon.join(map(textOf, nodes))
    lines = [l.strip() for l in text.splitlines()]
    text = '\n'.join(lines)
    return text


def getSubmitValues(content):
    root = lxml.html.fromstring(content)
    form = root.forms[0]
    values = dict(form.form_values())
    return values


def addTemplate(form, fname):
    form.template = BoundPageTemplate(
        ViewPageTemplateFile(
            fname, os.path.dirname(tests.__file__)), form)


def saveHtml(content, fname):
    path = os.path.join(os.getcwd(), 'htmls')
    if not os.path.exists(path):
        os.makedirs(path)
    fullfname = os.path.join(path, fname)
    with open(fullfname, 'wb') as fout:
        fout.write(content.encode('utf8'))

    fullfname = os.path.join(path, 'integration.css')
    cssfname = os.path.join(os.path.dirname(tests.__file__),
                            'integration.css')
    shutil.copy(cssfname, fullfname)


##########################################
# integration test interfaces and classes

class IntegrationBase(object):
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self):
        items = list(self.__dict__.items())
        items.sort()
        return ("<" + self.__class__.__name__+"\n  "
            + "\n  ".join(["%s: %s" % (key, pprint.pformat(value))
            for key, value in items]) + ">")


class IObjectWidgetSingleSubIntegration(zope.interface.Interface):
    singleInt = zope.schema.Int(
        title=u'Int label')
    singleBool = zope.schema.Bool(
        title=u'Bool label')
    singleChoice = zope.schema.Choice(
        title=u'Choice label',
        values=('one', 'two', 'three'))
    singleChoiceOpt = zope.schema.Choice(
        title=u'ChoiceOpt label',
        values=('four', 'five', 'six'),
        required=False)
    singleTextLine = zope.schema.TextLine(
        title=u'TextLine label')
    singleDate = zope.schema.Date(
        title=u'Date label')
    singleReadOnly = zope.schema.TextLine(
        title=u'ReadOnly label',
        readonly=True)


@zope.interface.implementer(IObjectWidgetSingleSubIntegration)
class ObjectWidgetSingleSubIntegration(IntegrationBase):

    singleInt = FieldProperty(IObjectWidgetSingleSubIntegration['singleInt'])
    singleBool = FieldProperty(IObjectWidgetSingleSubIntegration['singleBool'])
    singleChoice = FieldProperty(IObjectWidgetSingleSubIntegration['singleChoice'])
    singleChoiceOpt = FieldProperty(
        IObjectWidgetSingleSubIntegration['singleChoiceOpt'])
    singleTextLine = FieldProperty(
        IObjectWidgetSingleSubIntegration['singleTextLine'])
    singleDate = FieldProperty(IObjectWidgetSingleSubIntegration['singleDate'])
    singleReadOnly = FieldProperty(
        IObjectWidgetSingleSubIntegration['singleReadOnly'])


class IObjectWidgetSingleIntegration(zope.interface.Interface):
    subobj = zope.schema.Object(
        title=u'Object label',
        schema=IObjectWidgetSingleSubIntegration
    )


@zope.interface.implementer(IObjectWidgetSingleIntegration)
class ObjectWidgetSingleIntegration(object):

    subobj = FieldProperty(IObjectWidgetSingleIntegration['subobj'])


class IObjectWidgetMultiSubIntegration(zope.interface.Interface):
    multiInt = zope.schema.Int(
        title=u'Int label')
    multiBool = zope.schema.Bool(
        title=u'Bool label')
    multiChoice = zope.schema.Choice(
        title=u'Choice label',
        values=('one', 'two', 'three'))
    multiChoiceOpt = zope.schema.Choice(
        title=u'ChoiceOpt label',
        values=('four', 'five', 'six'),
        required=False)
    multiTextLine = zope.schema.TextLine(
        title=u'TextLine label')
    multiDate = zope.schema.Date(
        title=u'Date label')


@zope.interface.implementer(IObjectWidgetMultiSubIntegration)
class ObjectWidgetMultiSubIntegration(IntegrationBase):

    multiInt = FieldProperty(IObjectWidgetMultiSubIntegration['multiInt'])
    multiBool = FieldProperty(IObjectWidgetMultiSubIntegration['multiBool'])
    multiChoice = FieldProperty(IObjectWidgetMultiSubIntegration['multiChoice'])
    multiChoiceOpt = FieldProperty(
        IObjectWidgetMultiSubIntegration['multiChoiceOpt'])
    multiTextLine = FieldProperty(
        IObjectWidgetMultiSubIntegration['multiTextLine'])
    multiDate = FieldProperty(IObjectWidgetMultiSubIntegration['multiDate'])


class IObjectWidgetMultiIntegration(zope.interface.Interface):
    subobj = zope.schema.Object(
        title=u'Object label',
        schema=IObjectWidgetMultiSubIntegration
    )


@zope.interface.implementer(IObjectWidgetMultiIntegration)
class ObjectWidgetMultiIntegration(object):

    subobj = FieldProperty(IObjectWidgetMultiIntegration['subobj'])


class IMultiWidgetListIntegration(zope.interface.Interface):
    listOfInt = zope.schema.List(
        title=u"ListOfInt label",
        value_type=zope.schema.Int(
            title=u'Int label'),
    )
    listOfBool = zope.schema.List(
        title=u"ListOfBool label",
        value_type=zope.schema.Bool(
            title=u'Bool label'),
    )
    listOfChoice = zope.schema.List(
        title=u"ListOfChoice label",
        value_type=zope.schema.Choice(
            title=u'Choice label',
            values=('one', 'two', 'three')
            ),
    )
    listOfTextLine = zope.schema.List(
        title=u"ListOfTextLine label",
        value_type=zope.schema.TextLine(
            title=u'TextLine label'),
    )
    listOfDate = zope.schema.List(
        title=u"ListOfDate label",
        value_type=zope.schema.Date(
            title=u'Date label'),
    )
    listOfObject = zope.schema.List(
        title=u"ListOfObject label",
        value_type=zope.schema.Object(
            title=u'Object label',
            schema=IObjectWidgetMultiSubIntegration),
    )


@zope.interface.implementer(IMultiWidgetListIntegration)
class MultiWidgetListIntegration(IntegrationBase):

    listOfInt = FieldProperty(IMultiWidgetListIntegration['listOfInt'])
    listOfBool = FieldProperty(IMultiWidgetListIntegration['listOfBool'])
    listOfChoice = FieldProperty(IMultiWidgetListIntegration['listOfChoice'])
    listOfTextLine = FieldProperty(IMultiWidgetListIntegration['listOfTextLine'])
    listOfDate = FieldProperty(IMultiWidgetListIntegration['listOfDate'])
    listOfObject = FieldProperty(IMultiWidgetListIntegration['listOfObject'])


class IMultiWidgetDictIntegration(zope.interface.Interface):
    dictOfInt = zope.schema.Dict(
        title=u"DictOfInt label",
        key_type=zope.schema.Int(
            title=u'Int key'),
        value_type=zope.schema.Int(
            title=u'Int label'),
    )
    dictOfBool = zope.schema.Dict(
        title=u"DictOfBool label",
        key_type=zope.schema.Bool(
            title=u'Bool key'),
        value_type=zope.schema.Bool(
            title=u'Bool label'),
    )
    dictOfChoice = zope.schema.Dict(
        title=u"DictOfChoice label",
        key_type=zope.schema.Choice(
            title=u'Choice key',
            values=('key1', 'key2', 'key3')
            ),
        value_type=zope.schema.Choice(
            title=u'Choice label',
            values=('one', 'two', 'three')
            ),
    )
    dictOfTextLine = zope.schema.Dict(
        title=u"DictOfTextLine label",
        key_type=zope.schema.TextLine(
            title=u'TextLine key'),
        value_type=zope.schema.TextLine(
            title=u'TextLine label'),
    )
    dictOfDate = zope.schema.Dict(
        title=u"DictOfDate label",
        key_type=zope.schema.Date(
            title=u'Date key'),
        value_type=zope.schema.Date(
            title=u'Date label'),
    )
    dictOfObject = zope.schema.Dict(
        title=u"DictOfObject label",
        key_type=zope.schema.TextLine(
            title=u'Object key'),
        value_type=zope.schema.Object(
            title=u'Object label',
            schema=IObjectWidgetMultiSubIntegration),
    )


@zope.interface.implementer(IMultiWidgetDictIntegration)
class MultiWidgetDictIntegration(IntegrationBase):

    dictOfInt = FieldProperty(IMultiWidgetDictIntegration['dictOfInt'])
    dictOfBool = FieldProperty(IMultiWidgetDictIntegration['dictOfBool'])
    dictOfChoice = FieldProperty(IMultiWidgetDictIntegration['dictOfChoice'])
    dictOfTextLine = FieldProperty(IMultiWidgetDictIntegration['dictOfTextLine'])
    dictOfDate = FieldProperty(IMultiWidgetDictIntegration['dictOfDate'])
    dictOfObject = FieldProperty(IMultiWidgetDictIntegration['dictOfObject'])
