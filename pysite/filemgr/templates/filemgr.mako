<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">DateiManager</%block>
<%block name="styles">
${parent.styles()}
<link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/elfinder/css/elfinder.min.css')}">
</%block>
<%block name="scripts">
${parent.scripts()}
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/elfinder.min.js')}"></script>
<%doc>
<!-- elfinder core -->
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/elFinder.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/elFinder.version.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/jquery.elfinder.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/elFinder.resources.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/elFinder.options.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/elFinder.history.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/elFinder.command.js')}"></script>

<!-- elfinder ui -->
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/overlay.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/workzone.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/navbar.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/dialog.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/tree.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/cwd.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/toolbar.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/button.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/uploadButton.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/viewbutton.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/searchbutton.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/sortbutton.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/panel.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/contextmenu.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/path.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/stat.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/ui/places.js')}"></script>

<!-- elfinder commands -->
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/back.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/forward.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/reload.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/up.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/home.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/copy.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/cut.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/paste.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/open.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/rm.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/info.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/duplicate.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/rename.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/help.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/getfile.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/mkdir.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/mkfile.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/upload.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/download.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/edit.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/quicklook.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/quicklook.plugins.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/extract.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/archive.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/search.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/view.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/resize.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/sort.js')}"></script>	
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/commands/netmount.js')}"></script>	
</%doc>

<script src="${request.static_url('pysite:static/app/libs/elfinder/js/i18n/elfinder.de.js')}"></script>
<script src="${request.static_url('pysite:static/app/libs/elfinder/js/i18n/elfinder.en.js')}"></script>
</%block>

<script type="text/javascript" charset="utf-8">
	$().ready(function() {
		var elf = $('#elfinder').elfinder({
			lang: 'de',
			url : '${request.resource_url(request.context, '@@xhr_filemgr')}'
		}).elfinder('instance');
	});
</script>

<div id="elfinder"></div>
