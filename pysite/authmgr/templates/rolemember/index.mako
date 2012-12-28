<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">Manage Rolemembers</%block>
<%block name="styles">
${parent.styles()}
${grid.render_css(request)|n}
</%block>
<%block name="require_config">
	${parent.require_config()}
	${grid.render_requirejs_config()|n}
</%block>
${grid.render(is_fluid=True)|n}
