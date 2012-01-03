import os
import unittest
import time
import sys
import random

reload(sys)
sys.setdefaultencoding('utf-8')

import zope.configuration.xmlconfig
import zope.interface
import zope.component
import zope.component.globalregistry
import zope.schema
from zope.pagetemplate.interfaces import IPageTemplateEngine
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

import z3c.pt
import z3c.ptcompat.engine
from z3c.pt.pagetemplate import ViewPageTemplateFile as z3cViewPageTemplateFile

from z3c.form import form
from z3c.form import term
from z3c.form import field
from z3c.form import tests
from z3c.form import testing

def benchmark(title):
    def decorator(f):
        def wrapper(*args):
            print "==============================="
            print title
            print "==============================="
            return f(*args)
        return wrapper
    return decorator

def timing(func, *args, **kwargs):
    t1 = t2 = time.time()
    i = 0
    while t2 - t1 < 3:
        func(*args, **kwargs)
        i += 1
        t2 = time.time()
    return 100*(t2-t1)/i

class ISmallForm(zope.interface.Interface):
    name = zope.schema.TextLine(
        title=u"Name",
        description=u"Please enter your first and last name.")

    address = zope.schema.TextLine(
        title=u"Address",
        description=u"Please enter a valid address.")

class ILargeDataSetsForm(zope.interface.Interface):
    lucky_numer = zope.schema.Choice(
        range(500),
        title=u"Lucky number",
        description=u"Choose your lucky number.")

    favorite_letters = zope.schema.Set(
        title=u"Favorite letter",
        description=u"Choose your favorite letter.",
        value_type=zope.schema.Choice(
           ["".join(chr(random.randint(65, 90)) for i in range(10))]
        ))

def build_many_fields(size):
    for i in range(size):
        name = "".join(chr(random.randint(65, 90)) for i in range(10))
        yield zope.schema.TextLine(
            __name__=name,
            description=u"This field renders %s" % name,
            title=u"Title of %s" % name.capitalize())

IManyFields = tuple(build_many_fields(500))

class BaseTestCase(unittest.TestCase):
    def _setUp(suite):
        testing.setUp(suite)
        testing.setupFormDefaults()
        zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.pt)()
        zope.component.provideAdapter(term.CollectionTerms)

    def _tearDown(suite):
        testing.tearDown(suite)


def enableZ3CPT():
    """Enable z3c.pt engine"""
    base = zope.component.globalregistry.base
    base.registerUtility(z3c.ptcompat.engine.Program, IPageTemplateEngine,
        name=u'', event=False)

def disableZ3CPT():
    """Disable z3c.pt engine"""
    base = zope.component.globalregistry.base
    base.unregisterUtility(z3c.ptcompat.engine.Program, IPageTemplateEngine,
        name=u'')


class BenchmarkTestCase(BaseTestCase):
    def simple_form(self, cls, iface):
        class SimpleForm(form.AddForm):
            fields = field.Fields(
                *(isinstance(iface, tuple) and iface or (iface,)))
            render = cls(
                os.path.join(tests.__path__[0], 'simple_edit.pt'))
        return SimpleForm

    @benchmark(u"Small add-form (update/render)")
    def testSmallForm(self):
        context = object()
        request = testing.TestRequest()

        f_z3c = self.simple_form(
            z3cViewPageTemplateFile, ISmallForm)(context, request)
        f_zope = self.simple_form(
            ViewPageTemplateFile, ISmallForm)(context, request)

        t_z3c = self.benchmark(enableZ3CPT, f_z3c)
        t_zope = self.benchmark(disableZ3CPT, f_zope)

        print "z3c.pt:            %.3f" % t_z3c
        print "zope.pagetemplate: %.3f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)

    @benchmark(u"Large data sets (update/render)")
    def testLargeDataSets(self):
        context = object()
        request = testing.TestRequest()

        f_z3c = self.simple_form(
            z3cViewPageTemplateFile, ILargeDataSetsForm)(context, request)
        f_zope = self.simple_form(
            ViewPageTemplateFile, ILargeDataSetsForm)(context, request)

        t_z3c = self.benchmark(enableZ3CPT, f_z3c)
        t_zope = self.benchmark(disableZ3CPT, f_zope)

        print "z3c.pt:            %.3f" % t_z3c
        print "zope.pagetemplate: %.3f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)

    @benchmark(u"Many fields (update/render)")
    def testManyFields(self):
        context = object()
        request = testing.TestRequest()

        f_z3c = self.simple_form(
            z3cViewPageTemplateFile, IManyFields)(context, request)
        f_zope = self.simple_form(
            ViewPageTemplateFile, IManyFields)(context, request)

        t_z3c = self.benchmark(enableZ3CPT, f_z3c)
        t_zope = self.benchmark(disableZ3CPT, f_zope)

        print "z3c.pt:            %.3f" % t_z3c
        print "zope.pagetemplate: %.3f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)

    def benchmark(self, prep, func, *args):
        self._setUp()
        func(*args)
        prep()
        func(*args)
        t = timing(func, *args)
        self._tearDown()
        return t

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(BenchmarkTestCase),
        ))

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
