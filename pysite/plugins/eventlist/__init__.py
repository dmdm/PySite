# -*- coding: utf-8 -*-

import os
import datetime

from pysite.lib import load_site_config


NAME = "eventlist"

TITLE = "Loads a list of events."

DESCR = """
*************
The Eventlist
*************

Basic Format
============

An eventlist is a YAML mapping. The field ``EVENTS`` contains the list of
events.

Each event is a mapping which has at least fields ``date_from`` and ``date_to``.
Both dates must be strings, preferrably as ISO dates: YYYY-MM-DD.

An event may have arbitrary additional fields. Their meaning depends on the
used Jinja template.

The order of the fields or of events is not relevant. The list is
automatically sorted by ``date_from``.

Sample::

    EVENTS:
    - date_from: 2012-10-09
      date_to: 2012-10-12
      title: Breakfast by Tiffany
    - date_from: 2012-11-01
      date_to: 2012-11-30
      date_info: From dusk til dawn
      title: Call me November
      info: "<p>Yes, I am a real month.</br>Visit me next year, too!</p>"


Default Format
==============

Event Fields
------------

``date_info``: (optional) A text line with additional information about the
               date.
               E.g.: "Do 16 Uhr - So 13 Uhr"

``title``:     Title of event

``subtitle``:  (optional) A subtitle

``location``:  The location.
               E.g. "Baden-Baden"

``address``:   (optional) A string with address information. Use HTML to format
               it.
               E.g. "Seminarhaus Breema<br />Obere Windeckstr. 20"

``contacts``:  (optional) A list of contacts (see below). Either an explicit
               contact mapping or a reference to a contact of the CONTACTS
               list.


Contacts
--------

Each contact is a mapping with these fields:

``email``: Email address

``name``:  Name of contact person

``phone``: A phone number

To avoid redundancy, you may collect all contact mappings as a list of key
``CONTACTS`` and inside an event refer to it with a YAML reference.

E.g.::

    CONTACTS:
    - &idFOO
      email: foo@example.com
      name: Mr. Foo
      phone: 555-7745
    EVENTS:
    - date_from: 2012-12-01
      date_to:   2012-12-02
      title: The Big Frobotz
      contacts:
      - *idFOO

"""

def factory(rc=None):
    """
    Returns plugin instance for use as a thread local variable.

    In other words, this instance is create once within a Pyramid
    application. Store it e.g. in the application registry.
    """
    pass

def request_factory(site, context, request, rc=None):
    """
    Returns plugin instance for use within a request.

    In other words, this instance is created freshly for each request.
    Use :func:`factory` to create an instance suitable as a thread local.

    :param site: Resource node of the current site.
    :param context: Context of current request
    :param request: Current request
    :param rc: Optional config settings
    :returns: A fully initialised instance of the plugin
    """
    o = Eventlist(site, context, request, rc)
    return o


class Eventlist(object):

    def __init__(self, site, context, request, rc=None):
        self._site = site
        self._context = context
        self._request = request
        self._rc = rc
        self._data = None
        self._eventlist = None

    def load(self, fn):
        fn = os.path.join('plugins', NAME, os.path.normpath(fn))
        self._eventlist = load_site_config(self._site.dir_, fn)
        # TODO Convert dates into datetime objects
        self._eventlist['EVENTS'].sort(key=lambda it: it['date_from'])

    def all_events(self, year=None):
        """
        Returns list of all events.

        :param year: Optionally filter by year
        """
        if year:
            r = []
            for evt in self._eventlist['EVENTS']:
                if evt['date_from'].year == year:
                    r.append(evt)
            return r
        else:
            return self._eventlist['EVENTS']

    def next_events(self, n=3):
        """
        Returns list of n coming events.

        :param n: Number of events to return, 0=all coming events
        """
        now = datetime.date.today()
        i = 0
        r = []
        for evt in self._eventlist['EVENTS']:
            if evt['date_from'] < now:
                continue
            r.append(evt)
            i += 1
            if n > 0 and i >= n:
                break
        return r
