<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">Manage Rolemembers</%block>
<%block name="styles">
${parent.styles()}
<link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/jqgrid/css/ui.jqgrid.css')}">
</%block>
<%block name="require_config">
	${parent.require_config()}
	${grid.render_requirejs_config()|n}
</%block>
${grid.render(is_fluid=True)|n}
