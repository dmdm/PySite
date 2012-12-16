.. PySite documentation master file, created by
   sphinx-quickstart on Mon Dec  3 16:42:10 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
PySite
======

PySite is a system to host and manage multiple websites.

It is not a CMS in the traditional sense. Rather, you manage the contents of a
website via a filemanager interface, which gives you access to all
settings, the pages, the styles, plugins, you name it. Compose your pages with
`Jinja <http://jinja.pocoo.org/>`_ templates, and edit your code comfortably
with syntax highlighting in the `ACE <http://ace.ajax.org>`_ editor.

PySite also contains a facility to manage virtual mailboxes, if you
maintain your own SMTP and IMAP server, e.g. with
`Postfix <http://www.postfix.org/>`_ and `Dovecot <http://www.dovecot.org/>`_.
Websites and email domains are independent, so you can host mailboxes for
domains that do not have a website, and vice versa.

`Fork me on github <https://github.com/dmdm/PySite>`_.

PySite is built with the `Pyramid framework <http://www.pylonsproject.org/>`_ and
uses `elFinder <http://elfinder.org/>`_ which connects to `my implementation <https://github.com/dmdm/Pym-elFinder>`_
of its client API.

.. image:: /img/filemanager.png
   :class: image

Additional info can be found in `my blog <http://parenchym.com/pymblog/>`_,
and here is the code of a `sample site <https://github.com/dmdm/PySite/tree/master/var/site-templates/default>`_.

TOC
---

.. toctree::
   :maxdepth: 1

   narr/installation
   narr/templates
   narr/i18n
   narr/plugins
   Overview (draft) <https://github.com/dmdm/PySite/blob/master/README.rst>
   Hilfe (German) <hilfe>

Command Line Tools
..................
.. toctree::
   :maxdepth: 1

   narr/cli-pysite


API
---

.. toctree::
   :maxdepth: 2

   api/pysite/sitemgr/init
   api/pysite/sitemgr/page
   api/pysite/sitemgr/models


TODOs
=====

.. toctree::

   todolist


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

