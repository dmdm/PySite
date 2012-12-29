<%inherit file="pysite:templates/_layouts/default.mako" />
<%block name="meta_title">DateiManager</%block>
<%block name="styles">
	${parent.styles()}
	<link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/elfinder/css/elfinder.min.css')}">
	<style>
	#open-editor { text-decoration: none; }
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
</%block>

<div id="elfinder"></div>

<script>
require(['requirejs/domReady!', 'jquery', 'pym',
    'elfinder/elfinder.min', 'elfinder.commands.edit', 'elfinder/i18n/elfinder.de',
    'elfinder/i18n/elfinder.en', 'pym.editor.source'],
function(doc,                   $,        PYM)
{
	var h = $('#pageContainer').height() - $('#pageHeaderWrapper').outerHeight()
		- $('#pageFooterWrapper').outerHeight() - 10;
	var elf = $('#elfinder').elfinder({
		  lang: 'de'
		, url : '${request.resource_url(request.context, '@@xhr_filemgr')}'
		, height: h
		, handlers : {
			select : function(event, elfinderInstance) {
				if (event.data.selected.length) {
					var hash = event.data.selected[0]
					    , file = elfinderInstance.files()[hash]
					;
					if (file.mime.match(/^text\//)) {
						$('#open-editor')
							.data('hash', file.hash)
							.data('mime', file.mime)
							.data('filename', file.name)
							.text('Edit file "'+file.name+'"')
						;
						$('#open-editor-buttonset').show();
						console.log(hash);
						console.log(file);
					}
					else {
						$('#open-editor-buttonset').hide();
					}
				}
			}
		}
	}).elfinder('instance');
	var elm = $('.elfinder-button-icon-help').closest('.elfinder-buttonset');
	elm.after('<div id="open-editor-buttonset" class="ui-widget-content ui-corner-all elfinder-buttonset">'
		+ '<a id="open-editor" class="ui-widget-header" href="#">Editor</a>&nbsp;'
		+ '</div>'
	);
	$('#open-editor-buttonset').hide();
	$('#open-editor').on('click', function(evt) {
        var o = $(this)
            , mime = o.data('mime')
            , filename = o.data('filename')
            , hash = o.data('hash')
            , url = '${request.resource_url(request.context, '@@editor')}'
        ;
        PYM.editor.open_source_window(mime, filename, hash, url, 0);
    });
});
</script>

<%doc>
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
</%doc>
