<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">Plugins</%block>
<%block name="styles">
${parent.styles()}
</%block>
<%block name="scripts">
${parent.scripts()}
</%block>

<p>${meta_title()}</p>

<ul>
% for k, it in request.context.items():
<li><a href="${request.resource_url(it)}">${it.title}</a></li>
% endfor
</ul>
