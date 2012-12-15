<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">VMail Manager</%block>
<%block name="styles">
${parent.styles()}
<link rel="stylesheet" href="${request.static_url('pysite:static/css/jqgrid.css')}">
<style>

.ui-jqgrid {
    font-size: 90%;
}

.ui-jqgrid .ui-jqgrid-htable th {
    height: inherit;
}

.ui-jqgrid .ui-jqgrid-htable th div {
    height: inherit;
}



.ui-jqgrid tr.jqgrow td {
    height: 105%;
}
</style>
</%block>
<%block name="require_config">
	${parent.require_config()}
	${grid.render_requirejs_config()|n}
</%block>

<p>Welcome to ${meta_title()}</p>

<script>
function foo(opts) {
    opts['height'] = 300;
    opts['width'] = 900;
    return opts;
}
</script>
${grid.render(opts_hook='foo', is_fluid=True)|n}
