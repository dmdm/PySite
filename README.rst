PySite - Multi-Tenant Site Server
#################################

PySite is a simple, yet multi-tentant capable server for websites, based on
the Pyramid Framework.

Compose your websites with HTML and Jinja templates and store them in a domain
specific directory. Setup your DNS and webserver so that each site is a virtual
host, as described in `Virtual Root Support`_.  Each site will then be
accessible with URLs like these::

    http://localhost/sites/www.site_1.org/index
    http://www.site_1.org/index
    
    http://localhost/sites/www.site_2.org/index
    http://www.site_2.org/index


.. note:: More documentation is in directory "doc".


How to Build a Site
===================

Configure the directory where you want to store the sites in one of the
appropriate configuration files in directory ``etc`` as key ``sites_dir``.

Create a Site
-------------

Inside SITES_DIR, create a directory with the site's domain name, and put file
``rc.yaml`` in it. This file contains the configuration settings of this
site.

The overall tree of a site must be like this::

    SITES_DIR
    |
    +-- www.example.org
        |
        +-- rc.yaml            --> Config of this site
        |
        +-- content
        |   |
        |   +-- base.jinja2    --> Some base template
        |   +-- index.jinja2   --> Template of page index
        |   +-- index.html     --> Content of page index (optional)
        |   +-- index.yaml     --> Config of page index
        |
        +-- assets
        |   |
        |   +-- styles.css
        |
        +-- cache

Create Templates and Content
----------------------------

Create subdirectory ``content``. For each page you want to serve, create a
configuration file with the page's name, e.g. ``index.yaml``. This file
contains configuration settings for this page, e.g. title, keywords etc.
(We could place these into the template, in a separate file however, the
settings are more easy to manage by scripts or to put them into a DB later.)

The filename without extension will be the address of this page in the URL.

In the settings file you may specify the template for this page. If none
is given there, the template defaults to a Jinja2 file, e.g. 
``index.jinja2`` for ``index.yaml``.

Inside a template the settings of the site are available as dict ``site``,
those of the page as dict ``page``. E.g. you may access the page's title
as ``{{ page['title'] }}`` or ``{{ page.title }}``.

You may create subfolders to store your pages. Each subfolder must have a
corresponding YAML file::

    content
    |
    +-- base.jinja2
    +-- index.jinja2
    +-- index.html
    +-- index.yaml
    |
    +-- foo.jinja2       --> Optional template for page/folder `foo'
    +-- foo.yaml         --> Config for page/folder `foo'
    +-- foo              --> Folder `foo'
        |
        +-- bar.yaml     --> Config for page `bar'

You do not need to create template or HTML files for folders. If a folder is
requested, PySite will display a default message then.

This schematic also means that from the user's point of view there is no
distinction between pages and folders. A page has content and may contain
subpages at the same time.

Linking
-------

For static assets like CSS and images, create directory ``assets`` inside the
site's directory.

On startup, PySite adds a static route to the assets directory of each site [#static]_.
The route name is the domain name prefixed with ``static-``. E.g.
``static-www.example.org``.

In a template there are two functions available to conveniently build URLs.
``url()`` to create an absolute URL to another page, and ``asset_url()``
to create an URL to a static asset::

    <a href="{{ url('second') }}">Go to second page</a>
    <img src="{{ asset_url('img/logo.png') }}" />


Hints
=====

Configuration
-------------

Use Pyramid's paster INI files only to configure the (waitress) server,
the app's entry point and includes, and logging. Anything else is moved
into the YAML files in directory ``etc``.

Apart from preferring YAML over INI, this has the advantage of easier
maintaining settings for different environments, because host specific settings
inherit the base ones. Also, secrets may be stored in a separate file and
are excluded from version control (no more accidentally publishing credentials
on github ;).

Read doc strings of module ``rc.py`` and http://3amcode.de/pharaoh/Cms/pharaoh/parenchym/configuration/
for details.


Directories
-----------

The project's directory tree is similar to Linux': ``bin`` for scripts, ``etc`` for
configuration, ``var`` for variable contents, and ``pysite`` for this project's
package.

Rather than having all resources in ``resources.py`` and views in ``views.py`` or
sth. like this as suggested by the Pyramid manual, we use a sub-package layout.
This means for example, all files concerning resources are stored in sub-package
``resmgr`` like this::

    pysite
    |
    +-- resmgr
    |   |
    |   +-- __init__.py
    |   +-- models.py
    |   +-- views.py
    |
    +-- [...] other libs

This way we may use a sub-package in other projects more easily.


Sample Apache Configuration
---------------------------

Enable the following modules: ``headers``, ``proxy``, ``proxy_http``.

Configure a virtual host like this::
    
    <VirtualHost *:80>
       ServerName www.example.org
       RewriteEngine On
       RewriteRule ^/(.*) http://localhost:6543/$1 [L,P]
       ProxyPreserveHost on
       RequestHeader add X-Vhm-Root /sites/www.example.org
    </VirtualHost>

Let your local Python HTTP server listen on localhost, port 6543.

Site Templates
--------------

Directory ``var/site-templates`` contains demo sites. Copy them to your
``sites_dir`` directory.


My Blog
-------

My `blog`_ covers other topics about programming, and stuff.


Roadmap
=======

Step 1 (DONE)
-------------

Build the foundation so that PySite is able to serve several sites.
The sites can be managed via filesystem.

Step 2 (DONE)
-------------

Implement User and group management, auth and authz. Integrate elFinder
so that the site's contents and files can be managed via webbrowser.

Append ``/@@filemgr`` to a site's URL to enter file manager.

Append ``/@@login`` or ``/@@logout`` to any URL to log(?:in|out).

E.g.::

	http://www.my-site.org/@@filemgr

	or

	http://www.master-site.org/sites/www.my-site.org/@@filemgr

Step 3 (todo)
-------------

Append ``/@@edit`` to a page's URL to enter edit mode of this page.

Build UI to allow editing of contents in a more friendly wysiwyg manner.

Have in-line editing with "hallo" or "aloha" editor, like `Mezzanine`_.

Maybe add ACE online code editor.

Step 4..n (todo)
----------------

- Maybe integrate database
- UI to manage sites, not only content, users, ACL etc.


.. [#static]
    
    Yes, this means, every time you add or remove a site, PySite must be
    restarted. This is rather ugly / inconvenient if PySite is served by
    mod_wsgi. So we advice to serve PySite from a Python webserver
    (e.g. gunicorn) and use Apache or nginx as proxy.

.. _Virtual Root Support: http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/vhosting.html#virtual-root-support
.. _Mezzanine: http://mezzanine.jupo.org/docs/inline-editing.html
.. _blog: http://parenchym.com/pymblog/
