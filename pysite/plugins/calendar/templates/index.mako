<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">Calendar</%block>
<%block name="styles">
${parent.styles()}
</%block>
<%block name="scripts">
${parent.scripts()}
</%block>

<p>Welcome to ${meta_title()}</p>
