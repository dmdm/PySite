.. PySite documentation master file, created by
   sphinx-quickstart on Mon Dec  3 16:42:10 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
PySite
======

PySite is a system to host and manage multiple websites.

It is not a CMS in the traditional sense. Rather, you manage the contents of a
website via a filemanager interface, which gives you access to all
settings, the pages, the styles, plugins, you name it. Create the pages with
`Jinja <http://jinja.pocoo.org/>`_ templates.

`Fork me on github <https://github.com/dmdm/PySite>`_.

PySite is built with the `Pyramid framework <http://www.pylonsproject.org/>`_ and
uses `elFinder <http://elfinder.org/>`_ which connects to `my implementation <https://github.com/dmdm/Pym-elFinder>`_
of its client API.

.. image:: /img/filemanager.png
   :class: image


TOC
---

.. toctree::
   :maxdepth: 1

   Overview <https://github.com/dmdm/PySite/blob/master/README.rst>
   hilfe
   narr/installation


API
---

.. toctree::
   :maxdepth: 2

   api/pysite/sitemgr/init
   api/pysite/sitemgr/models
   api/pysite/sitemgr/page


TODOs
=====

.. toctree::

   todolist


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

