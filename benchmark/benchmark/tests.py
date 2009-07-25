import os
import unittest
import time
import sys
import random

reload(sys)
sys.setdefaultencoding('utf-8')

import zope.configuration.xmlconfig
import z3c.pt

from zope import interface
from zope import component
from zope import schema

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from z3c.pt.pagetemplate import ViewPageTemplateFile as z3cViewPageTemplateFile
import z3c.ptcompat as compat

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

class ISmallForm(interface.Interface):
    name = schema.TextLine(
        title=u"Name",
        description=u"Please enter your first and last name.")

    address = schema.TextLine(
        title=u"Address",
        description=u"Please enter a valid address.")

class ILargeDataSetsForm(interface.Interface):
    lucky_numer = schema.Choice(
        range(500),
        title=u"Lucky number",
        description=u"Choose your lucky number.")

    favorite_letters = schema.Set(
        title=u"Favorite letter",
        description=u"Choose your favorite letter.",
        value_type=schema.Choice(
           ["".join(chr(random.randint(65, 90)) for i in range(10))]
        ))

def build_many_fields(size):
    for i in range(size):
        name = "".join(chr(random.randint(65, 90)) for i in range(10))
        yield schema.TextLine(
            __name__=name,
            description=u"This field renders %s" % name,
            title=u"Title of %s" % name.capitalize())

IManyFields = tuple(build_many_fields(500))

class BaseTestCase(unittest.TestCase):
    def _setUp(suite):
        testing.setUp(suite)
        testing.setupFormDefaults()
        zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.pt)()
        component.provideAdapter(term.CollectionTerms)

    def _tearDown(suite):
        testing.tearDown(suite)

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

        t_z3c = self.benchmark(compat.config.enable, f_z3c)
        t_zope = self.benchmark(compat.config.disable, f_zope)

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

        t_z3c = self.benchmark(compat.config.enable, f_z3c)
        t_zope = self.benchmark(compat.config.disable, f_zope)

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

        t_z3c = self.benchmark(compat.config.enable, f_z3c)
        t_zope = self.benchmark(compat.config.disable, f_zope)

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

