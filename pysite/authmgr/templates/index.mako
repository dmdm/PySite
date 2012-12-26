<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">Authentication Manager</%block>
<%block name="styles">
${parent.styles()}
</%block>

<p>Welcome to ${meta_title()}</p>

<p><a href="${request.resource_url(request.context['principal'])}">Manage Principals</a></p>
<p><a href="${request.resource_url(request.context['role'])}">Manage Roles</a></p>
<p><a href="${request.resource_url(request.context['rolemember'])}">Manage Rolemembers</a></p>
