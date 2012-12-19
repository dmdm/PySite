<%inherit file="pysite:filemgr/templates/editor_base.mako" />
<%block name="meta_title">DateiManager</%block>
<%block name="styles">
    ${parent.styles()}
    <link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/ace/css/editor.css')}">
    <link rel="stylesheet" href="${request.static_url('pysite:static/app/libs/jpicker/jpicker-1.css')}">
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
	body { overflow: none; }
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
	require.shim['libs/jpicker/jpicker'] = ['ui/jquery-ui'];
</%block>
<%block name="scripts">
    ${parent.scripts()}
    <script src="${request.static_url('pysite:static/app/libs/ace/ace.js')}"></script>
</%block>

<nav id="topmenu">
<ul id="css3menu1" class="topmenu">
  <li class="topmenu"><a href="#" style="height:24px;line-height:24px;">File</a>
    <div class="submenu" style="width:200px;">
        <ul>
          <li><a id="cmd-file-save" href="#">Save &lt;Ctrl-S&gt;</a></li>
          <li><a id="cmd-file-save_sassc" href="#">Save &amp; compile Sass &lt;Alt-S&gt;</a></li>
          <li><a id="cmd-file-reload" href="#">Reload</a></li>
        </ul>
    </div>
  </li>
  <li class="toproot"><a href="#" style="height:24px;line-height:24px;">Options</a>
    <div class="submenu menu-options" style="width:200px;">
        <ul>
          <li><a href="#" data-obj="session" data-func="UseSoftTabs">Soft Tabs</a></li>
          <li><a href="#" data-obj="editor" data-func="ShowInvisibles">Show Invisibles</a></li>
          <li><a href="#" data-obj="session" data-func="UseWrapMode">Wrap Mode</a></li>
        </ul>
    </div>
  </li>
  <li class="toproot"><a href="#" style="height:24px;line-height:24px;"><span>Theme</span></a>
    <div class="submenu menu-themes" style="width:370px;">
      <div class="column" style="width:50%">
        <ul>
          <li><a href="#">ambiance</a></li>
          <li><a href="#">chrome</a></li>
          <li><a href="#">clouds</a></li>
          <li><a href="#">clouds_midnight</a></li>
          <li><a href="#">cobalt</a></li>
          <li><a href="#">crimson_editor</a></li>
          <li><a href="#">dawn</a></li>
          <li><a href="#">dreamweaver</a></li>
          <li><a href="#">eclipse</a></li>
          <li><a href="#">github</a></li>
          <li><a href="#">idle_fingers</a></li>
          <li><a href="#">kr</a></li>
          <li><a href="#">merbivore</a></li>
          <li><a href="#">merbivore_soft</a></li>
        </ul>
      </div>
      <div class="column" style="width:50%">
        <ul>
          <li><a href="#">mono_industrial</a></li>
          <li><a href="#">monokai</a></li>
          <li><a href="#">pastel_on_dark</a></li>
          <li><a href="#">solarized_dark</a></li>
          <li><a href="#">solarized_light</a></li>
          <li><a href="#">textmate</a></li>
          <li><a href="#">tomorrow</a></li>
          <li><a href="#">tomorrow_night</a></li>
          <li><a href="#">tomorrow_night_blue</a></li>
          <li><a href="#">tomorrow_night_bright</a></li>
          <li><a href="#">tomorrow_night_eighties</a></li>
          <li><a href="#">twilight</a></li>
          <li><a href="#">vibrant_ink</a></li>
          <li><a href="#">xcode</a></li>
        </ul>
      </div>
    </div>
  </li>
  <li class="toproot"><a href="#" style="height:24px;line-height:24px;"><span>Mode</span></a>
    <div class="submenu menu-modes" style="width:400px;">
      <div class="column" style="width:33%">
        <ul>
          <li><a href="#">abap</a></li>
          <li><a href="#">asciidoc</a></li>
          <li><a href="#">c9search</a></li>
          <li><a href="#">c_cpp</a></li>
          <li><a href="#">clojure</a></li>
          <li><a href="#">coffee</a></li>
          <li><a href="#">coldfusion</a></li>
          <li><a href="#">csharp</a></li>
          <li><a href="#">css</a></li>
          <li><a href="#">dart</a></li>
          <li><a href="#">diff</a></li>
          <li><a href="#">dot</a></li>
          <li><a href="#">glsl</a></li>
          <li><a href="#">golang</a></li>
          <li><a href="#">groovy</a></li>
          <li><a href="#">haml</a></li>
          <li><a href="#">haxe</a></li>
          <li><a href="#">html</a></li>
          <li><a href="#">jade</a></li>
          <li><a href="#">java</a></li>
        </ul>
      </div>
      <div class="column" style="width:33%">
        <ul>
          <li><a href="#">javascript</a></li>
          <li><a href="#">json</a></li>
          <li><a href="#">jsp</a></li>
          <li><a href="#">jsx</a></li>
          <li><a href="#">latex</a></li>
          <li><a href="#">less</a></li>
          <li><a href="#">liquid</a></li>
          <li><a href="#">lisp</a></li>
          <li><a href="#">lua</a></li>
          <li><a href="#">luapage</a></li>
          <li><a href="#">lucene</a></li>
          <li><a href="#">makefile</a></li>
          <li><a href="#">markdown</a></li>
          <li><a href="#">objectivec</a></li>
          <li><a href="#">ocaml</a></li>
          <li><a href="#">perl</a></li>
          <li><a href="#">pgsql</a></li>
          <li><a href="#">php</a></li>
          <li><a href="#">powershell</a></li>
          <li><a href="#">python</a></li>
      </ul>
      </div>
      <div class="column" style="width:33%">
        <ul>
          <li><a href="#">r</a></li>
          <li><a href="#">rdoc</a></li>
          <li><a href="#">rhtml</a></li>
          <li><a href="#">ruby</a></li>
          <li><a href="#">scad</a></li>
          <li><a href="#">scala</a></li>
          <li><a href="#">scss</a></li>
          <li><a href="#">sh</a></li>
          <li><a href="#">sql</a></li>
          <li><a href="#">stylus</a></li>
          <li><a href="#">svg</a></li>
          <li><a href="#">tcl</a></li>
          <li><a href="#">tex</a></li>
          <li><a href="#">text</a></li>
          <li><a href="#">textile</a></li>
          <li><a href="#">typescript</a></li>
          <li><a href="#">xml</a></li>
          <li><a href="#">xquery</a></li>
          <li><a href="#">yaml</a></li>
        </ul>
      </div>
    </div>
  </li>
  <li class="toproot"><a href="#" style="height:24px;line-height:24px;">Tools</a>
    <div class="submenu" style="width:200px;">
        <ul>
          <li><a id="cmd-color-picker" href="#">Color Picker</a></li>
          <li><a id="cmd-resize" href="#">Resize</a></li>
          <li><a id="cmd-key-bindings" href="#">Key Bindings</a></li>
        </ul>
    </div>
  </li>
</ul>
</nav>

<div id="editor"></div>

<script>
require(['requirejs/domReady!', 'jquery', 'pym', 'libs/jpicker/jpicker' ],
function(doc,                   $,        PYM)
{
	$('#cmd-color-picker').jPicker({
		window: {
			expandable: true
			, position: {
				y: 'bottom'
			}
			, alphaSupport: true 
			, alphaPrecision: 2
			, effects: {
				speed: {
					show: 'fast'
					, hide: 'fast'
				}
			}
		}
		, color: {
			alphaSupport: true
			, active: new $.jPicker.Color({ ahex: '99330099' })
		}
		, images: {
			clientPath: '${request.static_url('pysite:static/app/libs/jpicker/images/')}'
		}
	}
	// commit callback
	, function (color, context) {
		var edi = PYM.editor.get_editor();
		edi.insert(color.val('ahex'));
		edi.focus();
	}
	);
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
            , modemap = {
                    '.html':   'html'
                  , '.jinja2': 'html'
                  , '.yaml':   'yaml'
                  , '.js':     'javascript'
                  , '.css':    'css'
                  , '.scss':    'scss'
              }
            , sassc_url = '${sassc_url}'
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
                var ext = filename.match(/(\.[^.]+)$/)[1].toLowerCase()
                    , m = modemap[ext]
                ;
                set_mode(m);
                set_content(data.content);
            });
        }

        function save_file(visual, call_sassc) {
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
            $.post(url, data, function (data, textStatus, jqXHR) {
				// TODO Check the response data.
				//      If e.g. session expired, we will nonetheless get
				//      an HTTP 200, because we are redirected to the login
				//      page. Since XHR is non-visual, nobody notices that
				//      and this method signals "saving ok" to the user
				//      -- which is wrong! Nothing was saved.
                if (visual) PYM.growl({kind: 'success', text: filename + ' saved.'});
                if (call_sassc) {
                    $.getJSON(sassc_url, function(data, textStatus, jqXHR) {
                        for (var i=0, imax=data.msgs.length; i<imax; i++ ) {
                            PYM.growl(data.msgs[i]);
                        }
                    });
                }
            });
        }

        function get_content() {
            return editor.getValue();
        }

        function set_content(v) {
            editor.setValue(v);
        }

        function init_editor() {
            var th = PYM.cookie.read('theme') || 'tomorrow_night_eighties';
            editor = ace.edit(editor_id);
            editor.setShowInvisibles(true);
			set_theme( th );
			$('.menu-themes a').each(function(ix, it) {
				it = $(it);
				if (it.text() == th) it.addClass('active');
			});
            editor.commands.addCommand({
                name: 'save',
                bindKey: {win: 'Ctrl-S',  mac: 'Command-S'},
                exec: function(editor) {
                    save_file(true);
                }
            });
            editor.commands.addCommand({
                name: 'save_sassc',
                bindKey: {win: 'Alt-S',  mac: 'Alt-S'},
                exec: function(editor) {
                    save_file(true, true);
                }
            });
			editor.getSession().selection.on('changeSelection', function(evt) {
				var sel = editor.session.getTextRange(editor.getSelectionRange());
				if (sel.match(/^#?[0-9a-f]+$/i)) {
					console.log('color:' + sel);
					$.jPicker.List[0].color.active.val('ahex', sel);
				}
			});
			console.log(editor.commands);
        }

        function set_mode(m) {
            if (! m) {
				PYM.cookie.read('mode') || 'text';
			};
            editor.getSession().setMode('ace/mode/' + m);
			PYM.cookie.write('mode', m);
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
            $('#cmd-file-reload').on('click', function (evt) {
                if (window.confirm('You will lose any changes. Are you sure to reload?')) {
                    load_file();
                }
            });
            $('#cmd-file-save').on('click', function (evt) {
                save_file(true);
            });
            $('#cmd-file-save_sassc').on('click', function (evt) {
                save_file(true, true);
            });
            $('#cmd-resize').on('click', function (evt) {
                editor.resize(true);
            });
            $('#cmd-color-picker').on('click', function (evt) {
                alert('click');
            });
            $('#cmd-key-bindings').on('click', function (evt) {
				var s
					, key
					, platform = editor.commands.platform
					, cmds = editor.commands.byName
					, names = []
					, name
				;
				for (var name in cmds) {
			 		if(cmds.hasOwnProperty(name)) {
						names.push(name);
					}
				}
				names.sort();

				s = '<div id="key-bindings" style="position: absolute; top:0px; left:20px; height: 500px; width:500px; z-index:10000; background-color:#333; color: silver; font-size:80%;">'
					+ '<div style="text-align:right;" onclick="$(this).parent().remove();">[ close ]</div>'
					+ '<div>Platform: <strong>' + platform + '</strong></div>'
					+ '<div style="height: 450px; overflow: auto;">'
					+ '<table><thead><tr><th>Name</th><th>Key</th></tr></thead>'
					+ '<tbody>';
				for (var i=0, imax=names.length; i<imax; i++) {
					name = names[i];
					if (cmds[name].bindKey) {
						key = cmds[name].bindKey[platform];
					}
					else {
						key = 'unknown';
					}
					s += '<tr style="border-bottom:solid 1px gray;"><td>' + name + '</td><td>' + key + '</td></tr>';
				}
				s += '</tbody></table></div></div>';
				$('#editor').before(s);
				$('#key-bindings').css('top', $('#editor').css('top'));
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

		my.get_editor = function () {
			return editor;
		}

        return my;
    }($);
    
    PYM.editor.init({});
});
</script>
