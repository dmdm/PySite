Installation
============

1. Create a virtual environment
2. Install Pyramid
3. Install Pym-elFinder
4. Install PySite
5. Configure PySite
6. Run PySite
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
    
Install Pyramid 1.3.1. Versions before that are not compatible with Python 3,
and version 1.4 we have not tested yet::

	(PySite-env)$ pip install pyramid==1.3.1

This will also install several packages on which Pyramid depends.

Do not install Pyramid 1.3, since you will then run into 
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


5.3 Initialise the database
...........................

PySite needs a SQL database to store users and groups etc. For the
sake of simplicity, we use SQLite. Should you want a different
RDBMS, you must configure its SQLAlchemy settings in the appropriate
rc-file.

Create the database with this script::
    
	(PySite-env)PySite$ initialize_PySite_db

(You may run this command from anywhere, it was registered as a console script
during the installation of PySite.)

(Will rename this script in the future. Look for sth. like "pysite_init_db".)


5.4 Optional settings
.....................

If you want to run PySite on different hosts which need different settings,
create for each host a subdirectory in "etc". The name of that subdirectory
is the hostname. There, create files "rc.yaml", and "rcsecrets.yaml".
In these rc-files write only settings which differ from the main settings.


6. Run PySite
-------------

Start the webserver with PySite::
    
	(PySite-env)PySite$ pserve development.ini --reload

You may now point your browser to "localhost:6543". Since we have not set up a site
yet, not much is to be seen. Maybe you'll encounter not-found errors.


7. Create a site
----------------

Several steps are necessary to create a new site. Currently we have to do them
manually. Will provide scripts soon.


7.1 Create SITES_DIR
....................

Firstly, we need a directory where the sites will be stored. It can be located
anywhere, and may, and maybe should, be external to the virtual environment.

E.g.::

    $ mkdir /opt/mysites

In "etc/rc.yaml" tell PySite about this directory::

    sites_dir: /opt/mysites

You may also want to define the filesystem quota, which defaults to 50MB per site::

    quota.max_size: 50000000


7.2 Create the site
...................

From "var/site-templates", copy the subdirectory "www.default.local" and its YAML
file to the directory you created in step 7.2


7.3 Setup site security
.......................

In step 5.3 you initialised the database which also created a user "root" as
administrator. Its password you had configured in step 5.1, key
"auth.user_root.pwd". User root is allowed to access and manage any site.

We now need users with rights that are specific to this new site. Therefore,
you create a role with a name identical to the site name ("www.default.local" in
our case). Then create a user, e.g. "Sally" and assign it to that role.

Sorry, there are no scripts for that yet. Look at `pysite/usrmgr/install.py`
to get an idea.

The idea is, that all members of a role whose name corresponds to the site name
get manage rights for the filemanager.

This may change in the future.


8. View and manage the site
---------------------------

Visit the site at "localhost:6543/sites/www.default.local".

Call the filemanager at "localhost:6543/sites/www.default.local/@@filemgr".
You will be prompted to login.
