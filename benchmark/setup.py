from setuptools import setup, find_packages

version = '0.1'

setup(name='benchmark',
      version=version,
      description="Benchmark-suite for z3c.form.",
      long_description="""\
      """,
      keywords='',
      author = "Malthe Borch and the Zope Community",
      author_email = "zope-dev@zope.org",
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
         'zope.app.pagetemplate',
         'zope.schema',
         'z3c.form',
         'z3c.pt',
         'z3c.ptcompat',
      ],
      )
