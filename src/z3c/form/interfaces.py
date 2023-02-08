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
"""
__docformat__ = "reStructuredText"
import zope.i18nmessageid
import zope.interface
import zope.schema
from zope.interface.common import mapping
from zope.location.interfaces import ILocation


MessageFactory = _ = zope.i18nmessageid.MessageFactory('z3c.form')

INPUT_MODE = 'input'
DISPLAY_MODE = 'display'
HIDDEN_MODE = 'hidden'


class NOT_CHANGED:
    def __repr__(self):
        return '<NOT_CHANGED>'


NOT_CHANGED = NOT_CHANGED()


class NO_VALUE:
    def __repr__(self):
        return '<NO_VALUE>'


NO_VALUE = NO_VALUE()
# BBB: the object was renamed to follow common naming style
NOVALUE = NO_VALUE

# ----[ Layer Declaration ]--------------------------------------------------


class IFormLayer(zope.interface.Interface):
    """A layer that contains all registrations of this package.

    It is intended that someone can just use this layer as a base layer when
    using this package.

    Since version 2.4.2, this layer doesn't provide IBrowserRequst anymore.
    This makes it possible to use the IFormLayer within z3c.jsonrpc without
    to apply the IBrowserRequest into the jsonrpc request.
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

class IData(zope.interface.Interface):
    """A proxy object for form data.

    The object will make all keys within its data attribute available as
    attributes. The schema that is represented by the data will be directly
    provided by instances.
    """

    def __init__(schema, data, context):
        """The data proxy is instantiated using the schema it represents, the
        data fulfilling the schema and the context in which the data are
        validated.
        """

    __context__ = zope.schema.Field(
        title=_('Context'),
        description=_('The context in which the data are validated.'),
        required=True)


class IValidator(zope.interface.Interface):
    """A validator for a particular value."""

    def validate(value, force=False):
        """Validate the value.

        If successful, return ``None``. Otherwise raise an ``Invalid`` error.
        """


class IManagerValidator(zope.interface.Interface):
    """A validator that validates a set of data."""

    def validate(data):
        """Validate a dictionary of data.

        This method is only responsible of validating relationships between
        the values in the data. It can be assumed that all values have been
        validated in isolation before.

        The return value of this method is a tuple of errors that occurred
        during the validation process.
        """

    def validateObject(obj):
        """Validate an object.

        The same semantics as in ``validate()`` apply, except that the values
        are retrieved from the object and not the data dictionary.
        """


# ----[ Errors ]--------------------------------------------------------------

class IErrorViewSnippet(zope.interface.Interface):
    """A view providing a view for an error"""

    widget = zope.schema.Field(
        title=_("Widget"),
        description=_("The widget that the view is on"),
        required=True)

    error = zope.schema.Field(
        title=_('Error'),
        description=_('Error the view is for.'),
        required=True)

    def update():
        """Update view."""

    def render():
        """Render view."""


class IMultipleErrors(zope.interface.Interface):
    """An error that contains many errors"""

    errors = zope.interface.Attribute("List of errors")

# ----[ Fields ]--------------------------------------------------------------


class IField(zope.interface.Interface):
    """Field wrapping a schema field used in the form."""

    __name__ = zope.schema.TextLine(
        title=_('Title'),
        description=_('The name of the field within the form.'),
        required=True)

    field = zope.schema.Field(
        title=_('Schema Field'),
        description=_('The schema field that is to be rendered.'),
        required=True)

    prefix = zope.schema.Field(
        title=_('Prefix'),
        description=_('The prefix of the field used to avoid name clashes.'),
        required=True)

    mode = zope.schema.Field(
        title=_('Mode'),
        description=_('The mode in which to render the widget for the field.'),
        required=True)

    interface = zope.schema.Field(
        title=_('Interface'),
        description=_('The interface from which the field is coming.'),
        required=True)

    ignoreContext = zope.schema.Bool(
        title=_('Ignore Context'),
        description=_('A flag, when set, forces the widget not to look at '
                      'the context for a value.'),
        required=False)

    widgetFactory = zope.schema.Field(
        title=_('Widget Factory'),
        description=_('The widget factory.'),
        required=False,
        default=None,
        missing_value=None)

    showDefault = zope.schema.Bool(
        title=_('Show default value'),
        description=_('A flag, when set, makes the widget to display'
                      'field|adapter provided default values.'),
        default=True,
        required=False)


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


class IContentProviders(IManager):
    """
    A content provider manager
    """

# ----[ Data Managers ]------------------------------------------------------


class IDataManager(zope.interface.Interface):
    """Data manager."""

    def get():
        """Get the value.

        If no value can be found, raise an error
        """

    def query(default=NO_VALUE):
        """Get the value.

        If no value can be found, return the default value.
        If access is forbidden, raise an error.
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

    def toWidgetValue(value):
        """Convert the field value to a widget output value.

        If conversion fails or is not possible, a ``ValueError`` *must* be
        raised. However, this method should effectively never fail, because
        incoming value is well-defined.
        """

    def toFieldValue(value):
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
    """ """

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

    def __iter__():
        """Iterate over terms."""

    def __len__():
        """Return number of terms."""

    def __contains__(value):
        """Check wether terms containes the ``value``."""


class IBoolTerms(ITerms):
    """A specialization that handles boolean choices."""

    trueLabel = zope.schema.TextLine(
        title=_('True-value Label'),
        description=_('The label for a true value of the Bool field.'),
        required=True)

    falseLabel = zope.schema.TextLine(
        title=_('False-value Label'),
        description=_('The label for a false value of the Bool field.'),
        required=False)


# ----[ Object factory ]-----------------------------------------------------

class IObjectFactory(zope.interface.Interface):
    """Factory that will instantiate our objects for ObjectWidget.
    It could also pre-populate properties as it gets the values extracted
    from the form passed in ``value``.
    """

    def __call__(value):
        """Return a default object created to be populated.
        """


# ----[ Widget layout template ]----------------------------------------------

class IWidgetLayoutTemplate(zope.interface.Interface):
    """Widget layout template marker used for render the widget layout.

    It is important that we don't inherit this template from IPageTemplate.
    otherwise we will get into trouble since we lookup an IPageTemplate
    in the widget/render method.

    """

# ----[ Widgets ]------------------------------------------------------------


class IWidget(ILocation):
    """A widget within a form"""

    name = zope.schema.ASCIILine(
        title=_('Name'),
        description=_('The name the widget is known under.'),
        required=True)

    label = zope.schema.TextLine(
        title=_('Label'),
        description=_('''
        The widget label.

        Label may be translated for the request.

        The attribute may be implemented as either a read-write or read-only
        property, depending on the requirements for a specific implementation.
        '''),
        required=True)

    mode = zope.schema.ASCIILine(
        title=_('Mode'),
        description=_('A widget mode.'),
        default=INPUT_MODE,
        required=True)

    required = zope.schema.Bool(
        title=_('Required'),
        description=_('If true the widget should be displayed as required '
                      'input.'),
        default=False,
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

    template = zope.interface.Attribute('''The widget template''')
    layout = zope.interface.Attribute('''The widget layout template''')

    ignoreRequest = zope.schema.Bool(
        title=_('Ignore Request'),
        description=_('A flag, when set, forces the widget not to look at '
                      'the request for a value.'),
        default=False,
        required=False)

    # ugly thing to remove setErrors parameter from extract
    setErrors = zope.schema.Bool(
        title=_('Set errors'),
        description=_('A flag, when set, the widget sets error messages '
                      'on calling extract().'),
        default=True,
        required=False)

    # a bit different from ignoreRequiredOnExtract, because we record
    # here the fact, but for IValidator, because the check happens there
    ignoreRequiredOnValidation = zope.schema.Bool(
        title=_('Ignore Required validation'),
        description=_("If set then required fields will pass validation "
                      "regardless whether they're filled in or not"),
        default=False,
        required=True)

    showDefault = zope.schema.Bool(
        title=_('Show default value'),
        description=_('A flag, when set, makes the widget to display'
                      'field|adapter provided default values.'),
        default=True,
        required=False)

    def extract(default=NO_VALUE):
        """Extract the string value(s) of the widget from the form.

        The return value may be any Python construct, but is typically a
        simple string, sequence of strings or a dictionary.

        The value *must not* be converted into a native format.

        If an error occurs during the extraction, the default value should be
        returned. Since this should never happen, if the widget is properly
        designed and used, it is okay to NOT raise an error here, since we do
        not want to crash the system during an inproper request.

        If there is no value to extract, the default is to be returned.
        """

    def update():
        """Setup all of the widget information used for displaying."""

    def render():
        """Render the plain widget without additional layout"""

    def json_data():
        """Returns a dictionary for the widget"""

    def __call__():
        """Render a layout template which is calling widget/render"""


class ISequenceWidget(IWidget):
    """Term based sequence widget base.

    The sequence widget is used for select items from a sequence. Don't get
    confused, this widget does support to choose one or more values from a
    sequence. The word sequence is not used for the schema field, it's used
    for the values where this widget can choose from.

    This widget base class is used for build single or sequence values based
    on a sequence which is in most use case a collection. e.g.
    IList of IChoice for sequence values or IChoice for single values.

    See also the MultiWidget for build sequence values based on none collection
    based values. e.g. IList of ITextLine
    """

    noValueToken = zope.schema.ASCIILine(
        title=_('NO_VALUE Token'),
        description=_('The token to be used, if no value has been selected.'))

    terms = zope.schema.Object(
        title=_('Terms'),
        description=_('A component that provides the options for selection.'),
        schema=ITerms)

    def updateTerms():
        """Update the widget's ``terms`` attribute and return the terms.

        This method can be used by external components to get the terms
        without having to worry whether they are already created or not.
        """


class IMultiWidget(IWidget):
    """None Term based sequence widget base.

    The multi widget is used for ITuple, IList or IDict if no other widget is
    defined.

    Some IList or ITuple are using another specialized widget if they can
    choose from a collection. e.g. a IList of IChoice. The base class of such
    widget is the ISequenceWidget.

    This widget can handle none collection based sequences and offers add or
    remove values to or from the sequence. Each sequence value get rendered by
    it's own relevant widget. e.g. IList of ITextLine or ITuple of IInt
    """


class ISelectWidget(ISequenceWidget):
    """Select widget with ITerms option."""

    prompt = zope.schema.Bool(
        title=_('Prompt'),
        description=_('A flag, when set, enables a choice explicitely '
                      'requesting the user to choose a value.'),
        default=False)

    items = zope.schema.Tuple(
        title=_('Items'),
        description=_('A collection of dictionaries containing all pieces of '
                      'information for rendering. The following keys must '
                      'be in each dictionary: id, value, content, selected'))

    noValueMessage = zope.schema.Text(
        title=_('No-Value Message'),
        description=_('A human-readable text that is displayed to refer the '
                      'missing value.'))

    promptMessage = zope.schema.Text(
        title=_('Prompt Message'),
        description=_('A human-readable text that is displayed to refer the '
                      'missing value.'))


class IOrderedSelectWidget(ISequenceWidget):
    """Ordered Select widget with ITerms option."""


class ICheckBoxWidget(ISequenceWidget):
    """Checbox widget."""


class ISingleCheckBoxWidget(ICheckBoxWidget):
    """Single Checbox widget."""


class IRadioWidget(ISequenceWidget):
    """Radio widget."""

    def renderForValue(value):
        """Render a single radio button element for a given value.

        Here the word ``value`` is used in the HTML sense, in other
        words it is a term token.
        """


class ISubmitWidget(IWidget):
    """Submit widget."""


class IImageWidget(IWidget):
    """Submit widget."""


class IButtonWidget(IWidget):
    """Button widget."""


class ITextAreaWidget(IWidget):
    """Text widget."""


class ITextLinesWidget(IWidget):
    """Text lines widget."""


class ITextWidget(IWidget):
    """Text widget."""


class IFileWidget(ITextWidget):
    """File widget."""


class IPasswordWidget(ITextWidget):
    """Password widget."""


class IObjectWidget(IWidget):
    """Object widget."""

    def setupFields():
        """setup fields on the widget, by default taking the fields of
        self.schema"""


class IWidgets(IManager):
    """A widget manager"""

    prefix = zope.schema.ASCIILine(
        title=_('Prefix'),
        description=_('The prefix of the widgets.'),
        default='widgets.',
        required=True)

    mode = zope.schema.ASCIILine(
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
        required=True)

    ignoreRequest = zope.schema.Bool(
        title=_('Ignore Request'),
        description=_('If set the request is ignored to retrieve a value.'),
        default=False,
        required=True)

    ignoreReadonly = zope.schema.Bool(
        title=_('Ignore Readonly'),
        description=_('If set then readonly fields will also be shown.'),
        default=False,
        required=True)

    ignoreRequiredOnExtract = zope.schema.Bool(
        title=_('Ignore Required validation on extract'),
        description=_(
            "If set then required fields will pass validation "
            "on extract regardless whether they're filled in or not"),
        default=False,
        required=True)

    hasRequiredFields = zope.schema.Bool(
        title=_('Has required fields'),
        description=_('A flag set when at least one field is marked as '
                      'required'),
        default=False,
        required=False)

    # ugly thing to remove setErrors parameter from extract
    setErrors = zope.schema.Bool(
        title=_('Set errors'),
        description=_('A flag, when set, the contained widgets set error '
                      'messages on calling extract().'),
        default=True,
        required=False)

    def update():
        """Setup widgets."""

    def extract():
        """Extract the values from the widgets and validate them.
        """

    def extractRaw():
        """Extract the RAW/string values from the widgets and validate them.
        """


class IFieldWidget(zope.interface.Interface):
    """Offers a field attribute.

    For advanced uses the widget will make decisions based on the field
    it is rendered for.
    """

    field = zope.schema.Field(
        title=_('Field'),
        description=_('The schema field which the widget is representing.'),
        required=True)

# ----[ Actions ]------------------------------------------------------------


class ActionExecutionError(Exception):
    """An error that occurs during the execution of an action handler."""

    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return '<{} wrapping {!r}>'.format(self.__class__.__name__, self.error)


class WidgetActionExecutionError(ActionExecutionError):
    """An action execution error that occurred due to a widget value being
    incorrect."""

    def __init__(self, widgetName, error):
        ActionExecutionError.__init__(self, error)
        self.widgetName = widgetName


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


class IActionEvent(zope.interface.Interface):
    """An event specific for an action."""

    action = zope.schema.Object(
        title=_('Action'),
        description=_('The action for which the event is created.'),
        schema=IAction,
        required=True)


class IActionErrorEvent(IActionEvent):
    """An action event that is created when an error occurred."""

    error = zope.schema.Field(
        title=_('Error'),
        description=_('The error that occurred during the action.'),
        required=True)


class IActions(IManager):
    """A action manager"""

    executedActions = zope.interface.Attribute(
        '''An iterable of all executed actions (usually just one).''')

    def update():
        """Setup actions."""

    def execute():
        """Exceute actions.

        If an action execution error is raised, the system is notified using
        the action occurred error; on the other hand, if successful, the
        action successfull event is sent to the system.
        """


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


class IImageButton(IButton):
    """An image button in a form."""

    image = zope.schema.TextLine(
        title=_('Image Path'),
        description=_('A relative image path to the root of the resources.'),
        required=True)


class IButtons(ISelectionManager):
    """Button manager."""


class IButtonAction(IAction, IWidget, IFieldWidget):
    """Button action."""


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

    def __call__(form, action):
        """Execute the handler."""


# ----[ Forms ]--------------------------------------------------------------

class IHandlerForm(zope.interface.Interface):
    """A form that stores the handlers locally."""

    handlers = zope.schema.Object(
        title=_('Handlers'),
        description=_('A list of action handlers defined on the form.'),
        schema=IButtonHandlers,
        required=True)


class IActionForm(zope.interface.Interface):
    """A form that stores executable actions"""

    actions = zope.schema.Object(
        title=_('Actions'),
        description=_('A list of actions defined on the form'),
        schema=IActions,
        required=True)

    refreshActions = zope.schema.Bool(
        title=_('Refresh actions'),
        description=_('A flag, when set, causes form actions to be '
                      'updated again after their execution.'),
        default=False,
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


class IForm(zope.interface.Interface):
    """Form"""

    mode = zope.schema.Field(
        title=_('Mode'),
        description=_('The mode in which to render the widgets.'),
        required=True)

    ignoreContext = zope.schema.Bool(
        title=_('Ignore Context'),
        description=_('If set the context is ignored to retrieve a value.'),
        default=False,
        required=True)

    ignoreRequest = zope.schema.Bool(
        title=_('Ignore Request'),
        description=_('If set the request is ignored to retrieve a value.'),
        default=False,
        required=True)

    ignoreReadonly = zope.schema.Bool(
        title=_('Ignore Readonly'),
        description=_('If set then readonly fields will also be shown.'),
        default=False,
        required=True)

    ignoreRequiredOnExtract = zope.schema.Bool(
        title=_('Ignore Required validation on extract'),
        description=_(
            "If set then required fields will pass validation "
            "on extract regardless whether they're filled in or not"),
        default=False,
        required=True)

    widgets = zope.schema.Object(
        title=_('Widgets'),
        description=_('A widget manager containing the widgets to be used in '
                      'the form.'),
        schema=IWidgets)

    label = zope.schema.TextLine(
        title=_('Label'),
        description=_('A human readable text describing the form that can be '
                      'used in the UI.'),
        required=False)

    labelRequired = zope.schema.TextLine(
        title=_('Label required'),
        description=_('A human readable text describing the form that can be '
                      'used in the UI for rendering a required info legend.'),
        required=False)

    prefix = zope.schema.ASCIILine(
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

    def updateWidgets(prefix=None):
        '''Update the widgets for the form.

        This method is commonly called from the ``update()`` method and is
        mainly meant to be a hook for subclasses.

        Note that you can pass an argument for ``prefix`` to override
        the default value of ``"widgets."``.
        '''

    def extractData(setErrors=True):
        '''Extract the data of the form.

        setErrors: needs to be passed to extract() and to sub-widgets'''

    def update():
        '''Update the form.'''

    def render():
        '''Render the form.'''

    def json():
        '''Returns the form in json format'''


class ISubForm(IForm):
    """A subform."""


class IDisplayForm(IForm):
    """Mark a form as display form, used for templates."""


class IInputForm(zope.interface.Interface):
    """A form that is meant to process the input of the form controls."""

    action = zope.schema.URI(
        title=_('Action'),
        description=_('The action defines the URI to which the form data are '
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
                      'By default this is unknown.'),
        required=False)

    accept = zope.schema.ASCIILine(
        title=_('Accepted Content Types'),
        description=_('This is a list of content types the server can '
                      'safely handle.'),
        required=False)


class IAddForm(IForm):
    """A form to create and add a new component."""

    def create(data):
        """Create the new object using the given data.

        Returns the newly created object.
        """

    def add(object):
        """Add the object somewhere."""

    def createAndAdd(data):
        """Call create and add.

        This method can be used for keep all attributes internal during create
        and add calls. On sucess we return the new created and added object.
        If something fails, we return None. The default handleAdd method will
        only set the _finishedAdd marker on sucess.
        """


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


class IFieldsAndContentProvidersForm(IForm):
    """A form that is based upon defined fields and content providers"""

    contentProviders = zope.schema.Object(
        title=_('Content providers'), description=_(
            'A manager describing the content providers to be used for '
            'the form.'), schema=IContentProviders)


class IButtonForm(IForm):
    """A form that is based upon defined buttons."""

    buttons = zope.schema.Object(
        title=_('Buttons'),
        description=_('A button manager describing the buttons to be used for '
                      'the form.'),
        schema=IButtons)


class IGroup(IForm):
    """A group of fields/widgets within a form."""


class IGroupForm(IForm):
    """A form that supports groups."""

    groups = zope.schema.Tuple(
        title='Groups',
        description=('Initially a collection of group classes, which are '
                     'converted to group instances when the form is '
                     'updated.'))


# ----[ Events ]--------------------------------------------------------------


class IWidgetEvent(zope.interface.Interface):
    """A simple widget event."""

    widget = zope.schema.Object(
        title=_('Widget'),
        description=_('The widget for which the event was created.'),
        schema=IWidget)


class IAfterWidgetUpdateEvent(IWidgetEvent):
    """An event sent out after the widget was updated."""


class IDataExtractedEvent(zope.interface.Interface):
    """Event sent after data and errors are extracted from widgets.
    """
    data = zope.interface.Attribute(
        "Extracted form data. Usually, the widgets extract field names from "
        "the request and return a dictionary of field names and field values."
    )
    errors = zope.interface.Attribute(
        "Tuple of errors providing IErrorViewSnippet."
    )
    form = zope.interface.Attribute("Form instance.")
