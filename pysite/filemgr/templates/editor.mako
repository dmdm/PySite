<%inherit file="pysite:templates/_layouts/editor.mako" />
<%block name="meta_title">DateiManager</%block>
<%block name="styles">
	${parent.styles()}
	<link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/elfinder/css/elfinder.min.css')}">
	<link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/ace/css/editor.css')}">
<style type="text/css" media="screen">
	#topmenu {
		border: outset 1px gray;
		background-color: gray;
		padding: 0;
		margin: 0;
		color: white;
		width: 100%;
		line-height: 1;
	}
	#statusbar {
		background-color: silver;
		padding: 2px 4px;
	}
    #editor { 
        position: absolute;
        top: 57px;
        right: 0;
        bottom: 0;
        left: 0;
    }
ul#css3menu1 a.active { font-weight: bold; color: white; }

ul#css3menu1 { width: 100%; line-height: 1.4; }
ul#css3menu1,ul#css3menu1 ul{
	margin:0;list-style:none;padding:0;}
ul#css3menu1,ul#css3menu1 .submenu{
	background-color:#1f1f1f;border-width:0;border-style:solid;border-color:;}
ul#css3menu1 .submenu{
	visibility:hidden;position:absolute;left:0;top:100%;-ms-filter:"progid:DXImageTransform.Microsoft.Alpha(Opacity=80)";opacity:0;-moz-transition:all 0.5s;-webkit-transition:opacity 0.5s;-o-transition:opacity 0.5s;float:left;background-color:#2A2A2A;border-radius:0 5px 5px 5px;-moz-border-radius:0 5px 5px 5px;-webkit-border-radius:0;-webkit-border-top-right-radius:5px;-webkit-border-bottom-right-radius:5px;-webkit-border-bottom-left-radius:5px;padding:0 3px 3px;filter:alpha(opacity=80)}
ul#css3menu1 li:hover>.submenu{
	visibility:visible;opacity:1;}
ul#css3menu1 li{
	position:relative;display:block;white-space:nowrap;font-size:0;float:left;}
ul#css3menu1 li:hover{
	z-index:1;}
ul#css3menu1 ul .submenu{
	position:absolute;left:100%;top:0;border-width:1px;border-style:solid;border-color:#434343;}
ul#css3menu1>li:hover>.submenu{
	opacity:0.95;}
ul#css3menu1{
	font-size:0;z-index:999;position:relative;display:inline-block;zoom:1;padding:6px 6px 6px 0;
	*display:inline;}
ul#css3menu1 .column{
	float:left;}
* html ul#css3menu1 li a{
	display:inline-block;}
ul#css3menu1>li{
	margin:0 0 0 6px;}
ul#css3menu1 ul>li{
	margin:6px 0 0;}
ul#css3menu1 a:active, ul#css3menu1 a:focus{
	outline-style:none;}
ul#css3menu1 a{
	display:block;vertical-align:middle;text-align:left;text-decoration:none;font:12px Lucida Sans Unicode, sans-serif;color:#C0C0BA;cursor:pointer;padding:7px 14px;background-color:transparent;background-repeat:repeat;border-width:0px;border-style:none;border-color:;}
ul#css3menu1 ul li{
	float:none;margin:3px 0 0;}
ul#css3menu1 ul a{
	text-align:left;padding:5px;background-color:#2A2A2A;border-radius:5px;-moz-border-radius:5px;-webkit-border-radius:5px;-moz-transition:all 0.5s;-webkit-transition:all 0.5s;-o-transition:all 0.5s;font:12px Lucida Sans Unicode, sans-serif;color:#C0C0BA;text-decoration:none;}
ul#css3menu1 li:hover>a,ul#css3menu1 li a.pressed{
	background-color:#2A2A2A;border-style:none;color:#FFFFFF;text-decoration:none;}
ul#css3menu1 img{
	border:none;vertical-align:middle;margin-right:7px;}
ul#css3menu1 span{
	display:block;overflow:visible;background-position:right center;background-repeat:no-repeat;padding-right:0px;}
ul#css3menu1 ul span{
	background-image:url("arrowsub.png");padding-right:9px;}
ul#css3menu1 ul li:hover>a,ul#css3menu1 ul li a.pressed{
	background-color:#525252;color:#FFFFFF;text-decoration:none;}
ul#css3menu1 li.topmenu>a{
	border-width:1px;border-style:solid;border-color:transparent;border-radius:5px;-moz-border-radius:5px;-webkit-border-radius:5px;opacity:0.95;-moz-transition:all 0.5s;-webkit-transition:all 0.5s;-o-transition:all 0.5s;}
ul#css3menu1 li.topmenu:hover>a,ul#css3menu1 li.topmenu a.pressed{
	border-style:solid;border-color:#434343;}
ul#css3menu1 li.toproot>a{
	border-width:1px 1px 0 1px;border-style:solid;border-color:transparent;border-radius:5px 5px 0 0;-moz-border-radius:5px 5px 0 0;-webkit-border-radius:5px;-webkit-border-bottom-right-radius:0;-webkit-border-bottom-left-radius:0;opacity:0.95;-moz-transition:all 0.5s;-webkit-transition:all 0.5s;-o-transition:all 0.5s;}
ul#css3menu1 li.toproot:hover>a,ul#css3menu1 li.toproot a.pressed{
	border-style:solid;border-color:#434343;}
</style></%block>
<%block name="require_config">
	${parent.require_config()}
</%block>
<%block name="scripts">
	${parent.scripts()}
	<script src="${request.static_url('pysite:static/app/libs/ace/ace.js')}"></script>
</%block>

<nav id="topmenu">
<ul id="css3menu1" class="topmenu">
  <li class="topmenu"><a href="#" id="cmd-reload" title="Reload" style="height:24px;line-height:24px;">Reload</a>
  </li>
  <li class="toproot"><a href="#" title="Options" style="height:24px;line-height:24px;">Options</a>
    <div class="submenu menu-options" style="width:250px;">
        <ul>
          <li><a href="#" title="Soft Tabs" data-obj="session" data-func="UseSoftTabs">Soft Tabs</a></li>
          <li><a href="#" title="Show Invisibles" data-obj="editor" data-func="ShowInvisibles">Show Invisibles</a></li>
        </ul>
	</div>
  </li>
  <li class="toproot"><a href="#" title="Theme" style="height:24px;line-height:24px;"><span>Theme</span></a>
    <div class="submenu menu-themes" style="width:370px;">
      <div class="column" style="width:50%">
        <ul>
          <li><a href="#" title="ambiance">ambiance</a></li>
          <li><a href="#" title="chrome">chrome</a></li>
          <li><a href="#" title="clouds">clouds</a></li>
          <li><a href="#" title="clouds_midnight">clouds_midnight</a></li>
          <li><a href="#" title="cobalt">cobalt</a></li>
          <li><a href="#" title="crimson_editor">crimson_editor</a></li>
          <li><a href="#" title="dawn">dawn</a></li>
          <li><a href="#" title="dreamweaver">dreamweaver</a></li>
          <li><a href="#" title="eclipse">eclipse</a></li>
          <li><a href="#" title="github">github</a></li>
          <li><a href="#" title="idle_fingers">idle_fingers</a></li>
          <li><a href="#" title="kr">kr</a></li>
          <li><a href="#" title="merbivore">merbivore</a></li>
          <li><a href="#" title="merbivore_soft">merbivore_soft</a></li>
        </ul>
	  </div>
      <div class="column" style="width:50%">
        <ul>
          <li><a href="#" title="mono_industrial">mono_industrial</a></li>
          <li><a href="#" title="monokai">monokai</a></li>
          <li><a href="#" title="pastel_on_dark">pastel_on_dark</a></li>
          <li><a href="#" title="solarized_dark">solarized_dark</a></li>
          <li><a href="#" title="solarized_light">solarized_light</a></li>
          <li><a href="#" title="textmate">textmate</a></li>
          <li><a href="#" title="tomorrow">tomorrow</a></li>
          <li><a href="#" title="tomorrow_night">tomorrow_night</a></li>
          <li><a href="#" title="tomorrow_night_blue">tomorrow_night_blue</a></li>
          <li><a href="#" title="tomorrow_night_bright">tomorrow_night_bright</a></li>
          <li><a href="#" title="tomorrow_night_eighties">tomorrow_night_eighties</a></li>
          <li><a href="#" title="twilight">twilight</a></li>
          <li><a href="#" title="vibrant_ink">vibrant_ink</a></li>
          <li><a href="#" title="xcode">xcode</a></li>
        </ul>
      </div>
    </div>
  </li>
  <li class="toproot"><a href="#" title="Mode" style="height:24px;line-height:24px;"><span>Mode</span></a>
    <div class="submenu menu-modes" style="width:400px;">
      <div class="column" style="width:33%">
        <ul>
          <li><a href="#" title="abap">abap</a></li>
          <li><a href="#" title="asciidoc">asciidoc</a></li>
          <li><a href="#" title="c9search">c9search</a></li>
          <li><a href="#" title="c_cpp">c_cpp</a></li>
          <li><a href="#" title="clojure">clojure</a></li>
          <li><a href="#" title="coffee">coffee</a></li>
          <li><a href="#" title="coldfusion">coldfusion</a></li>
          <li><a href="#" title="csharp">csharp</a></li>
          <li><a href="#" title="css">css</a></li>
          <li><a href="#" title="dart">dart</a></li>
          <li><a href="#" title="diff">diff</a></li>
          <li><a href="#" title="dot">dot</a></li>
          <li><a href="#" title="glsl">glsl</a></li>
          <li><a href="#" title="golang">golang</a></li>
          <li><a href="#" title="groovy">groovy</a></li>
          <li><a href="#" title="haml">haml</a></li>
          <li><a href="#" title="haxe">haxe</a></li>
          <li><a href="#" title="html">html</a></li>
          <li><a href="#" title="jade">jade</a></li>
          <li><a href="#" title="java">java</a></li>
        </ul>
      </div>
      <div class="column" style="width:33%">
        <ul>
          <li><a href="#" title="javascript">javascript</a></li>
          <li><a href="#" title="json">json</a></li>
          <li><a href="#" title="jsp">jsp</a></li>
          <li><a href="#" title="jsx">jsx</a></li>
          <li><a href="#" title="latex">latex</a></li>
          <li><a href="#" title="less">less</a></li>
          <li><a href="#" title="liquid">liquid</a></li>
          <li><a href="#" title="lisp">lisp</a></li>
          <li><a href="#" title="lua">lua</a></li>
          <li><a href="#" title="luapage">luapage</a></li>
          <li><a href="#" title="lucene">lucene</a></li>
          <li><a href="#" title="makefile">makefile</a></li>
          <li><a href="#" title="markdown">markdown</a></li>
          <li><a href="#" title="objectivec">objectivec</a></li>
          <li><a href="#" title="ocaml">ocaml</a></li>
          <li><a href="#" title="perl">perl</a></li>
          <li><a href="#" title="pgsql">pgsql</a></li>
          <li><a href="#" title="php">php</a></li>
          <li><a href="#" title="powershell">powershell</a></li>
          <li><a href="#" title="python">python</a></li>
	  </ul>
	  </div>
      <div class="column" style="width:33%">
        <ul>
          <li><a href="#" title="r">r</a></li>
          <li><a href="#" title="rdoc">rdoc</a></li>
          <li><a href="#" title="rhtml">rhtml</a></li>
          <li><a href="#" title="ruby">ruby</a></li>
          <li><a href="#" title="scad">scad</a></li>
          <li><a href="#" title="scala">scala</a></li>
          <li><a href="#" title="scss">scss</a></li>
          <li><a href="#" title="sh">sh</a></li>
          <li><a href="#" title="sql">sql</a></li>
          <li><a href="#" title="stylus">stylus</a></li>
          <li><a href="#" title="svg">svg</a></li>
          <li><a href="#" title="tcl">tcl</a></li>
          <li><a href="#" title="tex">tex</a></li>
          <li><a href="#" title="text">text</a></li>
          <li><a href="#" title="textile">textile</a></li>
          <li><a href="#" title="typescript">typescript</a></li>
          <li><a href="#" title="xml">xml</a></li>
          <li><a href="#" title="xquery">xquery</a></li>
          <li><a href="#" title="yaml">yaml</a></li>
        </ul>
      </div>
    </div>
  </li>
</ul>
</nav>

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
				if (visual) PYM.growl({kind: 'success', text: filename + ' saved.'});
			});
		}

		function get_content() {
			return editor.getValue();
		}

		function set_content(v) {
			editor.setValue(v);
		}

		function init_editor() {
			var th = PYM.cookie.read('theme');
    		editor = ace.edit(editor_id);
			editor.setShowInvisibles(true);
			if (th) {
				set_theme( th );
				$('.menu-themes a').each(function(ix, it) {
					it = $(it);
					if (it.text() == th) it.addClass('active');
				});
			}
			editor.commands.addCommand({
				name: 'save',
				bindKey: {win: 'Ctrl-S',  mac: 'Command-S'},
				exec: function(editor) {
					save_file(true);
				}
			});
			editor.commands.addCommand({
				name: 'switch_theme',
				bindKey: {win: 'Ctrl-T',  mac: 'Command-T'},
				exec: function(editor) {
					++cur_theme;
					if (cur_theme >= themes.length) cur_theme = 0;
		    		editor.setTheme('ace/theme/' + themes[cur_theme]);
		    		PYM.growl({text: cur_theme + ': ' + themes[cur_theme]});
				}
			});
		}

		function set_mode(m) {
			if (! m) return;
			editor.getSession().setMode('ace/mode/' + m);
			$('.menu-modes a').each(function(ix, it) {
				it = $(it);
				if (it.text() == m) {
					it.addClass('active');
				}
				else {
					it.removeClass('active');
				}
			});
		}

		function set_theme(theme) {
			if (! theme) theme = 'tomorrow_night_eighties';
			editor.setTheme('ace/theme/' + theme);
			PYM.cookie.write('theme', theme);
			$('.menu-themes a').each(function(ix, it) {
				it = $(it);
				if (it.text() == theme) {
					it.addClass('active');
				}
				else {
					it.removeClass('active');
				}
			});
		}

		function init_menu() {
			$('.menu-themes a').on('click', function(evt) {
				set_theme($(this).text());
			});
			$('.menu-modes a').on('click', function(evt) {
				set_mode($(this).text());
			});
			$('.menu-options a').on('click', function(evt) {
				var it = $(this)
					, func = it.data('func')
					, getter = 'get' + func
					, setter = 'set' + func
					, objname = it.data('obj')
					, obj
				;
				if (objname == 'editor') { obj = editor; }
				else { obj = editor.getSession(); }
				var val = ! obj[getter]();
				if (val) {
					it.addClass('active');
				}
				else {
					it.removeClass('active');
				}
				obj[setter](val);
			});
			$('#cmd-reload').on('click', function (evt) {
				if (window.confirm('You will lose any changes. Are you sure to reload?')) {
					load_file();
				}
			});
		}
		
		function init_menu_options() {
			$('.menu-options a').each(function(ix, it) {
				it = $(it);
				var func = it.data('func')
					, getter = 'get' + func
					, objname = it.data('obj')
					, obj
				;
				if (objname == 'editor') { obj = editor; }
				else { obj = editor.getSession(); }
				var val = obj[getter]();
				if (val) {
					it.addClass('active');
				}
				else {
					it.removeClass('active');
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
			init_menu();
			init_editor();
			load_file();
			init_menu_options();
		}

		return my;
	}($);
	
	PYM.editor.init({});
});
</script>
