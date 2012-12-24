<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">VMail Manager</%block>
<%block name="styles">
${parent.styles()}
</%block>

<p>Welcome to ${meta_title()}</p>

<p><a href="${request.resource_url(request.context['domain'])}">Manage Domains</a></p>
<p><a href="${request.resource_url(request.context['mailbox'])}">Manage Mailboxes</a></p>
<p><a href="${request.resource_url(request.context['alias'])}">Manage Aliases</a></p>
