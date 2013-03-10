Installation
============

1. Create a virtual environment
2. Install Pyramid
3. Install Pym-elFinder
4. Install PySite
5. Configure PySite
6. Run PySite server
7. Create a site
8. View and manage the site


1. Create virtual environment
-----------------------------

Create a virtual environment for Python 3 and activate it.
We use virtualenvwrapper::

    $ mkvirtualenv -p python3.2 PySite-env
    
    (PySite-env)$ cdvirtualenv


2. Install Pyramid
------------------
    
Install Pyramid 1.3.1. Versions before 1.3 are not compatible with Python 3,
and version 1.4 we have not tested yet::

	(PySite-env)$ pip install pyramid==1.3.1

This will also install several packages on which Pyramid depends.

.. note:: Do not install Pyramid 1.3, since you will then run into 
	`this bug <https://github.com/Pylons/pyramid/issues/604>`_.


3. Install Pym-elFinder
-----------------------

PySite uses elFinder as the UI of the filemanager, and Pym-elFinder is my
server-side implementation of its client protocol. Clone it from my github
repo and install it in development mode::

    (PySite-env)            $ git clone https://github.com/dmdm/Pym-elFinder
    (PySite-env)            $ cd Pym-elFinder
    (PySite-env)Pym-elFinder$ pip install -e .
    (PySite-env)Pym-elFinder$ cd ..


4. Install PySite
-----------------

4.1 Install Babel
.................

Download and unpack the Py3k port of Babel from here
(see `discussion topic <https://groups.google.com/forum/?fromgroups=#!searchin/python-babel/localedata/python-babel/WS7bakYSdnE/omKrgA15KWkJ>`_):

https://bitbucket.org/vinay.sajip/babel3/get/tip.tar.gz


Download and unpack the CLDR data from here:

http://unicode.org/Public/cldr/1.7.2/core.zip

In the Babel source directory, do::

    $ ./setup.py egg_info
    $ mkdir babel/localedata
    $ ./scripts/import_cldr.py /path/to/cldrdir
    $ ./setup.py install

The Babel site has `detailed instructions <http://babel.edgewall.org/wiki/SubversionCheckout>`_.


4.2 Install PySite
..................

Clone it from its github repo and install in development mode::

    (PySite-env)      $ git clone https://github.com/dmdm/PySite
    (PySite-env)      $ cd PySite
    (PySite-env)PySite$ pip install -e .
    (PySite-env)PySite$ cd ..

This will take a while, PySite pulls several other packages, and some will compile
C extensions.


5. Configure PySite
-------------------

Configuration takes place in several rc-files inside directory "etc". The format is
YAML.

Details about the `configuration system <http://3amcode.de/pharaoh/Cms/pharaoh/parenchym/configuration/>`_.

.. note:: The rc-files are not covered by the reload-feature of the waitress
          webserver. You must restart waitress manually if you change settings here.


5.1 Configure the framework
...........................

Inside directory "etc", create a file "rcsecrets.yaml" with this content::

    auth.tkt_policy.secret : '***'
    auth.user_root.pwd : '***'
    session.key : PySite
    session.secret : '***'

For each ``'***'`` you type a different high-end password, of course ;)


5.2 Create working directories
..............................

PySite needs several more working directories, which are not included in the
git repo. A script creates them and sets their correct permissions::

    (PySite-env)PySite$ ./bin/setup-dirs

Should you need different permissions, edit that script.

.. note:: You almost certainly need to edit the script and change the settings for
	USER and GROUP, and maybe GROUP_APPLICATION!


5.3 Initialise the database
...........................

PySite needs a SQL database to store users and groups etc. For the
sake of simplicity, we use SQLite. Should you want a different
RDBMS, you must configure its SQLAlchemy settings in the appropriate
rc-file and create a database user and a database manually.

Create PySite's schema with this script::
    
	(PySite-env)PySite$ pysite_init_db

(You may run this command from anywhere, it was registered as a console script
during the installation of PySite.)

Afterwards, run this SQL script which creates some database views::

    install/db/setup.sql

.. note:: This script encapsulates the DDL inside a transaction (PostgreSQL rules ;)
  so you need to give a COMMIT, else the changes would be rolled back.


5.4 Optional settings
.....................

If you want to run PySite on different hosts which need different settings,
create for each host a subdirectory in "etc". The name of that subdirectory
is the hostname. There, create files "rc.yaml", and "rcsecrets.yaml".
In these rc-files write only settings which differ from the main settings.


6. Run PySite server
--------------------

Start the webserver with PySite::
    
	(PySite-env)PySite$ pserve development.ini --reload

You may now point your browser to "localhost:6543". Since we have not set up a site
yet, not much is to be seen. Maybe you'll encounter not-found errors.


7. Create a site
----------------

The simplest way to create a new site is with the ``pysite`` command line tool::

    pysite -c production.ini --format yaml create-site '{sitename: www.new-site.com, principal: {principal: sally, email: sally@example.com, pwd: FOO, first_name: Sally, last_name: Müller-Lüdenscheidt, roles: [some_role, other_role]}, title: Neue Site, site_template: default}'

This will create a new site in the SITES_DIR directory (which you had configured in
the rc files as key ``sites_dir``). It then copies the default site template and creates
the specified principal and its roles.

See :doc:`cli-pysite` for details.

Or, proceed with the following steps if you prefer to handle it manually.

7.1 Create SITES_DIR
....................

Firstly, we need a directory where the sites will be stored (SITES_DIR). It can
be located anywhere, and may, and maybe should, be external to the virtual
environment.

E.g.::

    $ mkdir /opt/mysites

In "etc/rc.yaml" tell PySite about this directory::

    sites_dir: /opt/mysites

You may also want to define the filesystem quota, which defaults to 50MB per site::

    quota.max_size: 50

(This is a global default. You may set ``max_size`` individually for each site.)


7.2 Create the site
...................

Let's say we want to create a site called "www.new-site.com".

Copy a site template into the SITES_DIR and name its subdirectory and YAML file
according to your site name::

	cp -a var/site-templates/default SITES_DIR/www.new-site.com
	cp -a var/site-templates/default.yaml SITES_DIR/www.new-site.com.yaml


7.3 Setup site security
.......................

In step 5.3 you initialised the database which also created a user "root" as
administrator. Its password you had configured in step 5.1, key
"auth.user_root.pwd". User root is allowed to access and manage any site.

We now need users with rights that are specific to this new site. Therefore,
you create a role with a name identical to the site name ("www.new-site.com" in
our case). Then create a user, e.g. "Sally" and assign it to that role.

Giving that "manager role" the same name as the site is just a convention. It
allows us to easily identify to which site a role belongs. Of course you may
name your roles any way you find suitable.

Use the command line tool :doc:`cli-pysite` to accomplish this.

Now edit the ACL of your site (in the site's YAML file
``www.new-site.com.yaml``) and grant that role permission "manage_files",
e.g.::

	acl:
	- - allow
	  - r:www.new-site.com
	  - manage_files

.. raw:: html

	Or <del>gangnam</del> inline style:
	
::

	acl:
	- [ "allow", "r:www.new-site.com", "manage_files" ]



8. View and manage the site
---------------------------

Visit the site at "localhost:6543/sites/www.default.local".

Call the filemanager at "localhost:6543/sites/www.default.local/@@filemgr".
You will be prompted to login.
