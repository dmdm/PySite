=========
Templates
=========

Use `Jinja2 <http://jinja.pocoo.org/docs/templates/#comments>`_ as templating language.

Use Babel for :doc:`/narr/i18n`.

Get the site settings::

	{{ site.title }}

Get the page settings::

	{{ page.author }}

Link to another page::

	<p>Go to <a href="{{ url("dir_1/dir_2/other_page") }}">
	other page</a></p>

Link to an asset::
	
	<img src="{{ asset_url("img/grass-mud-horse2.jpg") }}">

Load some configuration settings::

	{% set data = load_config("test.yaml") %}
	{% for k, v in data.items() %}
		<div>Found key "{{k}}" with value "{{v}}".</div>
	{% endfor %}

Use `Markdown <http://daringfireball.net/projects/markdown/syntax>`_::

	{% filter markdown %}

	This is Markdown
	================

	dflkjahflafdf kwewer werj qwölkrjwöekr 
	{: #first-para .some-css-class data-foo="bar" }

	- aaa
	- bbb
	- ccc


	Col 1 | Col 2 | Right Aligned
	------|-------|--------------:
	cell1 | cell2 | 1000
	cell3 | cell4 |    12.45

	{% endfilter %}

Active `extensions <http://packages.python.org/Markdown/extensions/index.html>`_ for Markdown:
'abbr',
'attr_list',
'def_list',
'fenced_code',
'footnotes',
'smart_strong',
'tables',
'codehilite',
'sane_lists',
'toc'

