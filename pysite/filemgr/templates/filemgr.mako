<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">DateiManager</%block>
<%block name="styles">
	${parent.styles()}
	<link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/elfinder/css/elfinder.min.css')}">
</%block>
<%block name="require_config">
	${parent.require_config()}
	require.paths['elfinder'] = 'libs/elfinder/js';
	require.shim['elfinder/elfinder.min'] = {
		  deps: ['ui/jquery-ui']
		, exports: 'elFinder' // The i18n files need this
	};
	// All i18n files depend on the elFinder instance from the main script
	require.shim['elfinder/i18n/elfinder.de'] = ['elfinder/elfinder.min'];
	require.shim['elfinder/i18n/elfinder.en'] = ['elfinder/elfinder.min'];
</%block>

<div id="elfinder"></div>

<script>
require(['requirejs/domReady!', 'jquery', 'elfinder/elfinder.min', 'elfinder/i18n/elfinder.de', 'elfinder/i18n/elfinder.en'],
function(doc,                   $)
{
	var elf = $('#elfinder').elfinder({
		lang: 'de',
		url : '${request.resource_url(request.context, '@@xhr_filemgr')}'
	}).elfinder('instance');
});
</script>
