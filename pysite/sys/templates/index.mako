<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">System</%block>
<%block name="styles">
${parent.styles()}
</%block>
<%block name="scripts">
${parent.scripts()}
</%block>

<p>Welcome to ${meta_title()}</p>

<ul>
<li><a href="${request.resource_url(request.context['plugins'])}">Manage plugins</a></li>
<li><a href="${request.resource_url(request.context.__parent__, '@@filemgr')}">File Manager</a></li>
</ul>
