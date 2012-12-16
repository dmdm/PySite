<%inherit file="pysite:templates/_layouts/editor.mako" />
<%block name="meta_title">DateiManager</%block>
<%block name="styles">
	${parent.styles()}
	<!--link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/ace/css/editor.css')}"-->
<style type="text/css" media="screen">
	#menu {
		height: 16px;
	}
	#statusbar {
		height: 16px;
	}
    #__editor { 
        position: absolute;
        top: 200px;
        left: 0;
        bottom: 0;
        right: 0;
    }
</style></%block>
<%block name="require_config">
	${parent.require_config()}
</%block>
<%block name="scripts">
	${parent.scripts()}
	<!--script src="${request.static_url('pysite:static/app/libs/ace/ace.js')}"></script-->
</%block>
<div id="menu">Menu</div>
<div id="statusbar">Statusbar</div>
<div id="editor"></div>

<script>
require(['requirejs/domReady!', 'jquery', 'pym' ],
function(doc,                   $,        PYM)
{
	PYM.editor = function ($) {
		/**
		 * Private
		 */

		var rc
			, mime
			, hash
			, filename
			, is_initialised = false
			, content
			, url = '${request.resource_url(request.context, '@@xhr_filemgr')}'
			, editor
			, editor_id = 'editor'
			, mode = 'html'
			, modemap = {
				    '.html':   'html'
				  , '.jinja2': 'html'
				  , '.yaml':   'yaml'
				  , '.js':     'javascript'
				  , '.css':    'css'
			  }
			, themes = [
					'ambiance'
					, 'chrome'
					, 'clouds'
					, 'clouds_midnight'
					, 'cobalt'
					, 'crimson_editor'
					, 'dawn'
					, 'dreamweaver'
					, 'eclipse'
					, 'github'
					, 'idle_fingers'
					, 'kr'
					, 'merbivore'
					, 'merbivore_soft'
					, 'mono_industrial'
					, 'monokai'
					, 'pastel_on_dark'
					, 'solarized_dark'
					, 'solarized_light'
					, 'textmate'
					, 'tomorrow'
					, 'tomorrow_night'
					, 'tomorrow_night_blue'
					, 'tomorrow_night_bright'
					, 'tomorrow_night_eighties'
					, 'twilight'
					, 'vibrant_ink'
					, 'xcode'
				]
				, cur_theme = 24
			;

		function load_file() {
			// GET URL parameters:
			//     _=1355571502963
			//     cmd=get
			//     target=l1_Y29udGVudC90d28ueWFtbA
			// Response:
			//     {"content": "title: Page Two\n"}
			var
				that = this
				, data = {
					'_': 123456789
					, cmd: 'get'
					, target: hash
				}
			;
			$.getJSON(url, data, function(data, textStatus, jqXHR) {
				window.document.title = filename;
				var ext = filename.match(/(\.[^.]+)$/)[1]
					, m = modemap[ext]
				;
				if (m) set_mode(m);
				set_content(data.content);
			});
		}

		function save_file(visual) {
			// POST:
			//     cmd=put
            //     content=title: Page Two
            //
            //     target=l1_Y29udGVudC90d28ueWFtbA
			var
				that = this
				, data = {
					cmd: 'put'
					, target: hash
					, content: get_content()
				}
			;
			console.log('saving');
			console.log(data);
			$.post(url, data, function (data, textStatus, jqXHR) {
				if (visual) PYM.growl({text: filename + ' saved.'}); //alert(filename + ' saved.');
			});
		}

		function get_content() {
			return editor.getValue();
		}

		function set_content(v) {
			editor.setValue(v);
		}

		function set_mode(m) {
			editor.getSession().setMode('ace/mode/' + m);
		}

		function init_editor() {
    		editor = ace.edit(editor_id);
		    editor.setTheme('ace/theme/' + themes[cur_theme]);
			editor.setShowInvisibles(true);
			set_mode(mode);
			/**
			 * Command "save" --> CTRL-S
			 */
			editor.commands.addCommand({
				name: 'save',
				bindKey: {win: 'Ctrl-S',  mac: 'Command-S'},
				exec: function(editor) {
					save_file(true);
				}
			});
			/**
			 * Command "switch_theme" --> CTRL-T
			 */
			editor.commands.addCommand({
				name: 'switch_theme',
				bindKey: {win: 'Ctrl-T',  mac: 'Command-T'},
				exec: function(editor) {
					++cur_theme;
					if (cur_theme >= themes.length) cur_theme = 0;
		    		editor.setTheme('ace/theme/' + themes[cur_theme]);
		    		window.document.title = cur_theme + ': ' + themes[cur_theme];
				}
			});
		}

		/**
		 * Public API
		 */
		var my = {};

		my.init = function (newrc) {
			// If user focuses an already open but hidden editor window,
			// init() gets called again. Prevent this.
			if (this.is_initialised) return;
			rc = newrc;
			var search
				, data = {}
				, items
			;
			search = window.location.search.match(/^\?([^#]+)/)[1];
			items = search.split(/\&/);
			for (var i=0, maxi=items.length; i<maxi; i++) {
				var kv = items[i].split(/=/);
				if ([kv[0]] == 'mime') mime = kv[1];
				if ([kv[0]] == 'filename') filename = kv[1];
				if ([kv[0]] == 'hash') hash = kv[1];
			}
			//init_editor();
			//load_file();
			PYM.growl({text: "huhu"});
		}

		return my;
	}($);
	
	PYM.editor.init({});
});
</script>
