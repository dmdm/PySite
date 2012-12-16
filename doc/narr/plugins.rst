=======
Plugins
=======

EventList
*********

Write events into a YAML file like this::

     EVENTS:
     - date_from: 2012-10-09
       date_to: 2012-10-12
       title: Breakfast by Tiffany
     - date_from: 2012-11-01
       date_to: 2012-11-30
       date_info: From dusk til dawn
       title: Call me November
       info: "<p>Yes, I am a real month.</br>Visit me next year, too!</p>"

Put the event calendar on a page like this::

	{% from '/plugins/eventlist/macros.jinja2' import eventlist, nextevents with context %}
	{% set _ = plugins.eventlist.load('eventlist.yaml') %}

	<h2>Calendar 2016</h2>
	{{ eventlist(2016) }}
	
	<h2>Upcoming Events</h2>
	{{ nextevents(3) }}


