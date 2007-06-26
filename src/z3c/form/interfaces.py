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
"""Form and Widget Framework Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
from zope.interface.common import mapping
from zope.location.interfaces import ILocation
from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.form.i18n import MessageFactory as _


INPUT_MODE = 'input'
DISPLAY_MODE = 'display'
HIDDEN_MODE = 'hidden'

class NOVALUE(object):
    def __repr__(self):
        return '<NOVALUE>'
NOVALUE = NOVALUE()

# ----[ Layer Declaration ]--------------------------------------------------

class IFormLayer(IBrowserRequest):
    """A layer that contains all registrations of this package.

    It is intended that someone can just use this layer as a base layer when
    using this package.
    """


# ----[ Generic Manager Interfaces ]-----------------------------------------

class IManager(mapping.IEnumerableMapping):
    """A manager of some kind of items.

    *Important*: While managers are mappings, the order of the items is
     assumed to be important! Effectively a manager is an ordered mapping.

    In general, managers do not have to support a manipulation
    API. Oftentimes, managers are populated during initialization or while
    updating.
    """

class ISelectionManager(IManager):
    """Managers that support item selection and management.

    This manager allows one to more carefully specify the contained items.

    *Important*: The API is chosen in a way, that the manager is still
    immutable. All methods in this interface must return *new* instances of
    the manager.
    """

    def __add__(other):
        """Used for merge two managers."""

    def select(*names):
        """Return a modified instance with an ordered subset of items."""

    def omit(*names):
        """Return a modified instance omitting given items."""

    def copy():
        """Copy all items to a new instance and return it."""


# ----[ Validators ]---------------------------------------------------------

class IValidator(zope.interface.Interface):
    """A validator for a particular value."""

    def validate(self, value):
        """Validate the value.

        If successful, return ``None``. Otherwise raise an ``Invalid`` error.
        """

class IManagerValidator(zope.interface.Interface):
    """A validator that validates a set of data."""

    def validate(self, data):
        """Validate a dictionary of data.

        This method is only responsible of validating relationships between
        the values in the data. It can be assumed that all values have been
        validated in isolation before.

        The return value of this method is a tuple of errors that occurred
        during the validation process.
        """

    def validateObject(self, obj):
        """Validate an object.

        The same semantics as in ``validate()`` apply, except that the values
        are retrieved from the object and not the data dictionary.
        """


# ----[ Errors ]--------------------------------------------------------------

class IErrorViewSnippet(zope.interface.Interface):
    """A view providing a view for an error"""

    error = zope.schema.Field(
        title=_('Error'),
        description=_('Error the view is for.'),
        required=True)

    def update(self):
        """Update view."""

    def render(self):
        """Render view."""


# ----[ Fields ]--------------------------------------------------------------

class IField(zope.interface.Interface):
    """Field wrapping a schema field used in the form."""

    # TODO: define this fields
    __name__ = zope.schema.TextLine(
        title=_('Title'),
        description=_('The name of the field within the form.'),
        required=True)

    field = zope.schema.Field(
        title=_('Schema Field'),
        description=_('The schema field that is to be rendered.'),
        required=True)

    prefix = zope.schema.Field()

    mode = zope.schema.Field()

    interface = zope.schema.Field()

    dataProvider = zope.schema.Field()

    widgetFactory = zope.schema.Field(
        title=_('Widget Factory'),
        description=_('The widget factory.'),
        required=False,
        default=None,
        missing_value=None)


class IFields(ISelectionManager):
    """IField manager."""

    def select(prefix=None, interface=None, *names):
        """Return a modified instance with an ordered subset of items.

        This extension to the ``ISelectionManager`` allows for handling cases
        with name-conflicts better by separating field selection and prefix
        specification.
        """

    def omit(prefix=None, interface=None, *names):
        """Return a modified instance omitting given items.

        This extension to the ``ISelectionManager`` allows for handling cases
        with name-conflicts better by separating field selection and prefix
        specification.
        """

# ----[ Data Managers ]------------------------------------------------------

class IDataManager(zope.interface.Interface):
    """Data manager."""

    def get(default=NOVALUE):
        """Get the value.

        If no value can be found, return the default value.
        """

    def set(value):
        """Set the value"""

    def canAccess():
        """Can the value be accessed."""

    def canWrite():
        """Can the data manager write a value."""


# ----[ Data Converters ]----------------------------------------------------

class IDataConverter(zope.interface.Interface):
    """A data converter from field to widget values and vice versa."""

    def toWidgetValue(self, value):
        """Convert the field value to a widget output value.

        If conversion fails or is not possible, a ``ValueError`` *must* be
        raised. However, this method should effectively never fail, because
        incoming value is well-defined.
        """

    def toFieldValue(self, value):
        """Convert an input value to a field/system internal value.

        This methods *must* also validate the converted value against the
        field.

        If the conversion fails, a ``ValueError`` *must* be raised. If
        the validation fails, a ``ValidationError`` *must* be raised.
        """


# value interfaces
class IValue(zope.interface.Interface):
    """A value."""

    def get():
        """Returns the value."""


# term interfaces
class ITerms(zope.interface.Interface):
    """"""

    context = zope.schema.Field()
    request = zope.schema.Field()
    form = zope.schema.Field()
    field = zope.schema.Field()
    widget = zope.schema.Field()

    def getTerm(value):
        """Return an ITitledTokenizedTerm object for the given value

        LookupError is raised if the value isn't in the source
        """

    def getTermByToken(token):
        """Return an ITokenizedTerm for the passed-in token.

        If `token` is not represented in the vocabulary, `LookupError`
        is raised.
        """

    def getValue(token):
        """Return a value for a given identifier token

        LookupError is raised if there isn't a value in the source.
        """


# ----[ Widgets ]------------------------------------------------------------

class IWidget(ILocation):
    """A widget within a form"""

    template = zope.interface.Attribute('''The widget template''')

    mode = zope.schema.BytesLine(
        title=_('Mode'),
        description=_('A widget mode.'),
        required=True,
        default=DISPLAY_MODE)

    label = zope.schema.TextLine(
        title=_('Label'),
        description=_('''
        The widget label.

        Label may be translated for the request.

        The attribute may be implemented as either a read-write or read-only
        property, depending on the requirements for a specific implementation.
        '''),
        required=True)

    required = zope.schema.Bool(
        title=_('Required'),
        description=_('If true the widget should be displayed as required '
                      'input.'),
        required=True)

    error = zope.schema.Field(
        title=_('Error'),
        description=_('If an error occurred during any step, the error view '
                      'stored here.'),
        required=False)

    value = zope.schema.Field(
        title=_('Value'),
        description=_('The value that the widget represents.'),
        required=False)

    ignoreRequest = zope.schema.Bool(
        title=_('Ignore Request'),
        description=_('A flag, when set, forces the widget not to look at '
                      'the request for a value.'),
        default=False,
        required=False)

    def extract(default=NOVALUE):
        """Extract the string value(s) of the widget from the form.

        The return value may be any Python construct, but is typically a
        simple string, sequence of strings or a dictionary.

        The value *must not* be converted into a native format.

        If an error occurs during the extraction, the default value should be
        returned. Since this should never happen, if the widget is properly
        designed and used, it is okay to not raise an error here, since we do
        not want to crash the system during an inproper request.

        If there is no value to extract, the default is to be returned.
        """

    def update():
        """Setup all of the widget information used for displaying."""

    def render():
        """Return the widget's text representation."""


class ISequenceWidget(IWidget):
    """Sequence widget."""

    noValueToken = zope.schema.ASCIILine(
        title=_('NOVALUE Token'),
        description=_('The token to be used, if no value has been selected.'))

    terms = zope.schema.Object(
        title=_('Terms'),
        description=_('A component that provides the options for selection.'),
        schema=ITerms)

class ISelectWidget(ISequenceWidget):
    """Select widget with ITerms option."""

class IOrderedSelectWidget(ISequenceWidget):
    """Ordered Select widget with ITerms option."""

class ICheckBoxWidget(ISequenceWidget):
    """Checbox widget."""

class IRadioWidget(ISequenceWidget):
    """Radio widget."""

class ISubmitWidget(IWidget):
    """Submit widget."""

class ITextAreaWidget(IWidget):
    """Text widget."""

class ITextWidget(IWidget):
    """Text widget."""

class IFileWidget(ITextWidget):
    """File widget."""

class IPasswordWidget(ITextWidget):
    """Password widget."""


class IWidgets(IManager):
    """A widget manager"""

    prefix = zope.schema.BytesLine(
        title=_('Prefix'),
        description=_('The prefix of the widgets.'),
        default='widgets.',
        required=True)

    mode = zope.schema.BytesLine(
        title=_('Prefix'),
        description=_('The prefix of the widgets.'),
        default=INPUT_MODE,
        required=True)

    errors = zope.schema.Field(
        title=_('Errors'),
        description=_('The collection of errors that occured during '
                      'validation.'),
        default=(),
        required=True)

    ignoreContext = zope.schema.Bool(
        title=_('Ignore Context'),
        description=_('If set the context is ignored to retrieve a value.'),
        default=False,
        required=False)

    ignoreRequest = zope.schema.Bool(
        title=_('Ignore Request'),
        description=_('If set the request is ignored to retrieve a value.'),
        default=False,
        required=False)


    def update():
        """Setup widgets."""

    def extract():
        """Extract the values from the widgets and validate them.
        """


# ----[ Actions ]------------------------------------------------------------

class IAction(zope.interface.Interface):
    """Action"""

    __name__ = zope.schema.TextLine(
        title=_('Name'),
        description=_('The object name.'),
        required=False,
        default=None)

    title = zope.schema.TextLine(
        title=_('Title'),
        description=_('The action title.'),
        required=True)

    def isExecuted():
        """Determine whether the action has been executed."""


class IActionHandler(zope.interface.Interface):
    """Action handler."""


class IActions(IManager):
    """A action manager"""

    executedActions = zope.interface.Attribute(
        '''An iterable of all executed actions (usually just one).''')

    def update():
        """Setup actions."""

    def execute():
        """Exceute actions."""


class IButton(zope.schema.interfaces.IField):
    """A button in a form."""

    accessKey = zope.schema.TextLine(
        title=_('Access Key'),
        description=_('The key when pressed causes the button to be pressed.'),
        min_length=1,
        max_length=1,
        required=False)

    actionFactory = zope.schema.Field(
        title=_('Action Factory'),
        description=_('The action factory.'),
        required=False,
        default=None,
        missing_value=None)


class IButtons(ISelectionManager):
    """Button manager."""


class IButtonHandlers(zope.interface.Interface):
    """A collection of handlers for buttons."""

    def addHandler(button, handler):
        """Add a new handler for a button."""

    def getHandler(button):
        """Get the handler for the button."""

    def copy():
        """Copy this object and return the copy."""

    def __add__(other):
        """Add another handlers object.

        During the process a copy of the current handlers object should be
        created and the other one is added to the copy. The return value is
        the copy.
        """


class IButtonHandler(zope.interface.Interface):
    """A handler managed by the button handlers."""

    def __call__(self, form, action):
        """Execute the handler."""


# ----[ Forms ]--------------------------------------------------------------

class IHandlerForm(zope.interface.Interface):
    """A form that stores the handlers locally."""

    handlers = zope.schema.Object(
        title=_('Handlers'),
        description=_('A list of action handlers defined on the form.'),
        schema=IButtonHandlers,
        required=True)


class IContextAware(zope.interface.Interface):
    """Offers a context attribute.

    For advanced uses, the widget will make decisions based on the context
    it is rendered in.
    """

    context = zope.schema.Field(
        title=_('Context'),
        description=_('The context in which the widget is displayed.'),
        required=True)

    ignoreContext = zope.schema.Bool(
        title=_('Ignore Context'),
        description=_('A flag, when set, forces the widget not to look at '
                      'the context for a value.'),
        default=False,
        required=False)


class IFormAware(zope.interface.Interface):
    """Offers a form attribute.

    For advanced uses the widget will make decisions based on the form
    it is rendered in.
    """

    form = zope.schema.Field()


class IFieldWidget(zope.interface.Interface):
    """Offers a field attribute.

    For advanced uses the widget will make decisions based on the field
    it is rendered for.
    """

    field = zope.schema.Field(
        title=_('Field'),
        description=_('The schema field which the widget is representing.'),
        required=True)


class IForm(zope.interface.Interface):
    """Form"""

    widgets = zope.schema.Object(
        title=_('Widgets'),
        description=_('A widget manager containing the widgets to be used in '
                      'the form.'),
        schema=IWidgets)

    prefix = zope.schema.BytesLine(
        title=_('Prefix'),
        description=_('The prefix of the form used to uniquely identify it.'),
        default='form.')

    status = zope.schema.Text(
        title=_('Status'),
        description=_('The status message of the form.'),
        default=None,
        required=False)

    def getContent():
        '''Return the content to be displayed and/or edited.'''

    def updateWidgets(self):
        '''Update the widgets for the form.

        This method is commonly called from the ``update()`` method and is
        mainly meant to be a hook for subclasses.
        '''

    def extractData():
        '''Extract the data of the form.'''

    def update():
        '''Update the form.'''

    def render():
        '''Render the form.'''

class ISubForm(IForm):
    """A subform."""

class IInputForm(zope.interface.Interface):
    """A form that is meant to process the input of the form controls."""

    action = zope.schema.URI(
        title=_('Action'),
        description=_('The action defines the URI to which the form data is '
                      'sent.'),
        required=True)

    name = zope.schema.TextLine(
        title=_('Name'),
        description=_('The name of the form used to identify it.'),
        required=False)

    id = zope.schema.TextLine(
        title=_('Id'),
        description=_('The id of the form used to identify it.'),
        required=False)

    method = zope.schema.Choice(
        title=_('Method'),
        description=_('The HTTP method used to submit the form.'),
        values=('get', 'post'),
        default='post',
        required=False)

    enctype = zope.schema.ASCIILine(
        title=_('Encoding Type'),
        description=_('The data encoding used to submit the data safely.'),
        default='multipart/form-data',
        required=False)

    acceptCharset = zope.schema.ASCIILine(
        title=_('Accepted Character Sets'),
        description=_('This is a list of character sets the server accepts. '
                      'By default this is unknwon.'),
        required=False)

    accept = zope.schema.ASCIILine(
        title=_('Accepted Content Types'),
        description=_('This is a list of content types the server can '
                      'safely handle.'),
        required=False)


class IAddForm(IForm):
    """A form to create and add a new component."""

    def create(self, data):
        """Create the new object using the given data.

        Returns the newly created object.
        """

    def add(self, object):
        """Add the object somewhere."""


class IEditForm(IForm):
    """A form to edit data of a component."""

    def applyChanges(data):
        """Apply the changes to the content component."""


class IFieldsForm(IForm):
    """A form that is based upon defined fields."""

    fields = zope.schema.Object(
        title=_('Fields'),
        description=_('A field manager describing the fields to be used for '
                      'the form.'),
        schema=IFields)


class IButtonForm(IForm):
    """A form that is based upon defined buttons."""

    buttons = zope.schema.Object(
        title=_('Buttons'),
        description=_('A button manager describing the buttons to be used for '
                      'the form.'),
        schema=IButtons)

class IGroup(IForm):
    """A group of fields/widgets within a form."""

    label = zope.schema.TextLine(
        title=u'Label',
        description=u'A test describing the group. Commonly used for the UI.')


class IGroupForm(object):
    """A form that supports groups."""

    groups = zope.schema.Tuple(
        title=u'Groups',
        description=(u'Initially a collection of group classes, which are '
                     u'converted to group instances when the form is '
                     u'updated.'))
