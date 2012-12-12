import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'anyjson',
    'Babel',
    'blinker',
    'pyramid',
    'pyramid_beaker',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_tm',
    'python_magic',
    'pytz',
    'PyYAML',
    'SQLAlchemy',
    'transaction',
    'waitress',
    'zope.sqlalchemy',
    ]

setup(name='PySite',
      version='0.1',
      description='PySite',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        ],
      author='Dirk Makowski',
      author_email='dirk [.] makowski [@] gmail.com',
      url='',
      keywords='web wsgi pyramid cms hosting website',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="pysite",
      entry_points = """\
      [paste.app_factory]
      main = pysite:main
      [console_scripts]
      pysite-init-db = pysite.scripts.initializedb:main
      pysite = pysite.scripts.pysite:main
      pysite-vmail = pysite.scripts.pysite_vmail:main
      """,
      )

