Formatting
##########

Babel

The Babel `formatter <http://babel.edgewall.org/wiki/ApiDocs/babel.support#babel.support:Format>`_
is available in templates as ``bfmt``.

See:

- Date formatting

  - http://babel.edgewall.org/wiki/Documentation/0.9/dates.html
  - http://unicode.org/reports/tr35/#Date_Format_Patterns

Sample::

    {{bfmt.date(evt.date_from, format="d. MMM y")}}


