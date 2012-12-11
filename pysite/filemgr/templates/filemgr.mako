<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">DateiManager</%block>
<%block name="styles">
	${parent.styles()}
	<link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/elfinder/css/elfinder.min.css')}">
	<link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/ace/css/editor.css')}">
	<style>
	#content { padding-left: 0px; padding-right: 0px; }
	#editor { width: 100%; height: 100%; border: solid 2px red;}
	</style>
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
	require.shim['elfinder.commands.edit'] = ['elfinder/elfinder.min'];
</%block>
<%block name="scripts">
	${parent.scripts()}
	<script src="${request.static_url('pysite:static/app/libs/ace/ace.js')}"></script>
</%block>

<div id="elfinder"></div>

<script>
var editor;
require(['requirejs/domReady!', 'jquery', 'elfinder/elfinder.min', 'elfinder.commands.edit', 'elfinder/i18n/elfinder.de', 'elfinder/i18n/elfinder.en'],
function(doc,                   $)
{
	var h = $('#pageContainer').height() - $('#pageHeaderWrapper').outerHeight()
		- $('#pageFooterWrapper').outerHeight() - 10;
	var elf = $('#elfinder').elfinder({
		  lang: 'de'
		, url : '${request.resource_url(request.context, '@@xhr_filemgr')}'
		, height: h
		, commandsOptions: {
			edit: {
				editors: [
					{
						mimes: ['text/html', 'text/plain']
						, load: function(textarea, mime, filename) {
							var ta = $('#' + textarea.id)
								, div_editor = ta.before('<div id="editor" style="z-index:9999;height:500px;"></div>')
								, mode
							;
							$('.elfinder-dialog-active').on('dialogresize', function(evt) {
								var dlg = $('.ui-dialog-content');
								$('editor').height(this.height()).width(this.width());
								editor.editor.resize();
							});
							editor = ace.edit('editor');
							editor.getSession().setValue(ta.val());
							editor.setTheme('ace/theme/monokai');
							if (mime == 'text/html') {
								mode = "ace/mode/html"
							}
							else if (mime == 'text/plain') {
								if (filename.match(/\.yaml$/i)) {
									mode = "ace/mode/yaml";
								}
								else if (filename.match(/(\.html?)|(\.jinja2)$/i)) {
									mode = "ace/mode/html";
								}
								else {
									mode = "ace/mode/text";
								}
							}
							editor.getSession().setMode(mode);
						}
						, close: function(textarea) {
							$('#editor').remove();
						}
						, save: function(textarea) {
							var ta = $('#' + textarea.id);
							ta.val(editor.getSession().getValue());
							alert(ta.val());
						}
					}
				]
			}
		}
		, handlers : {
			select : function(event, elfinderInstance) {
				console.log(event.data);
				console.log(event.data.selected); // selected files hashes list
			}
		}
	}).elfinder('instance');
});
</script>
