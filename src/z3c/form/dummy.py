############
# REMOVE this after we found a good solution for factory


import zope.interface
import zope.schema
from zope.schema.fieldproperty import FieldProperty

class IMySubObject(zope.interface.Interface):
    foofield = zope.schema.Int(default=1111,
                               max=9999)
    barfield = zope.schema.Int(default=2222)

class MySubObject(object):
    zope.interface.implements(IMySubObject)

    foofield = FieldProperty(IMySubObject['foofield'])
    barfield = FieldProperty(IMySubObject['barfield'])

class IMySecond(zope.interface.Interface):
    subfield = zope.schema.Object(schema=IMySubObject)
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


import zope.interface
import zope.component
import zope.schema.interfaces

from z3c.form import interfaces
from z3c.form.object import IObjectFactory

class FactoryAdapter(object):
    """ """

    zope.interface.implements(IObjectFactory)
    zope.component.adapts(zope.interface.Interface, interfaces.IFormLayer,
        interfaces.IForm, interfaces.IWidget)

    factory = None

    def __init__(self, context, request, form, widget):
        self.context = context
        self.request = request
        self.form = form
        self.widget = widget

    def get(self, value):
        return self.factory()

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)

#class MySubObjectFactory(FactoryAdapter):
#    zope.component.adapts(zope.interface.Interface, interfaces.IFormLayer,
#        interfaces.IForm, zope.interface.Interface, interfaces.IWidget)
#    #zope.component.adapts(zope.interface.Interface, interfaces.IFormLayer,
#    #    interfaces.IForm, zope.schema.interfaces.IObject, interfaces.IWidget)
#
#    factory = MySubObject
#
#class MySecondFactory(FactoryAdapter):
#    zope.component.adapts(zope.interface.Interface, interfaces.IFormLayer,
#        interfaces.IForm, zope.interface.Interface, interfaces.IWidget)
#    #zope.component.adapts(zope.interface.Interface, interfaces.IFormLayer,
#    #    interfaces.IForm, zope.schema.interfaces.IObject, interfaces.IWidget)
#
#    factory = MySecond

class MySubObjectFactory(FactoryAdapter):
    zope.component.adapts(
        zope.interface.Interface, interfaces.IFormLayer,
        interfaces.IForm, interfaces.IWidget)
    #zope.component.adapts(zope.interface.Interface, interfaces.IFormLayer,
    #    interfaces.IForm, zope.schema.interfaces.IObject, interfaces.IWidget)

    factory = MySubObject

class MySecondFactory(FactoryAdapter):
    zope.component.adapts(
        zope.interface.Interface, interfaces.IFormLayer,
        interfaces.IForm, interfaces.IWidget)
    #zope.component.adapts(zope.interface.Interface, interfaces.IFormLayer,
    #    interfaces.IForm, zope.schema.interfaces.IObject, interfaces.IWidget)

    factory = MySecond