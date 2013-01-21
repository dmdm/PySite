(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(function(require, exports, module) {
            var PYM = require('pym');
            require('pym.editor');
            require('libs/jpicker/jpicker');
            // Also create a global in case some scripts
            // that are loaded still are looking for
            // a global even when an AMD loader is in use.
            return (root.PYM.editor.source = factory($, PYM));
        });
    } else {
        // Browser globals
        root.PYM.editor.source = factory(root.$, root.PYM);
    }
}(this, function ($, PYM) {
    "use strict";

    var is_initialised = false
        , rc
        , mime
        , filename
        , hash
        , editor
        , content
        , modemap = {
                '.html':   'html'
              , '.jinja2': 'html'
              , '.yaml':   'yaml'
              , '.js':     'javascript'
              , '.css':    'css'
              , '.scss':   'scss'
        }
    ;

    function get_content() {
        return editor.getValue();
    }

    function set_content(v) {
        editor.setValue(v);
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
        $.getJSON(rc.url, data, function(data, textStatus, jqXHR) {
            window.document.title = filename;
            var ext = filename.match(/(\.[^.]+)$/)[1].toLowerCase()
                , m = modemap[ext]
            ;
            set_mode(m);
            set_content(data.content);
        });
    }

    function save_file(visual, cascade) {
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
        $.post(rc.url, data, function (data, textStatus, jqXHR) {
            if (visual) PYM.growl({kind: 'success', text: filename + ' saved.'});
            if (rc.reload_opener && ! cascade) {
                window.opener.location.reload();
            }
            if (cascade) {
                cascade.func(cascade.rc);
            }
        });
    }

    function trigger_server_method(rc) {
        $.getJSON(rc.url, function(data, textStatus, jqXHR) {
            for (var i=0, imax=data.msgs.length; i<imax; i++ ) {
                PYM.growl(data.msgs[i]);
            }
            if (rc.reload_opener) {
                if (window.opener) {
                    window.opener.location.reload();
                }
            }
        });
    }

    function init_editor() {
        var th = PYM.cookie.read('theme') || 'tomorrow_night_eighties';
        editor = ace.edit(rc.editor_id);
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
                save_file(true, {
                    func: trigger_server_method
                    , rc: {
                        url: rc.sassc_url
                        , reload_opener: true
                    }
                });
            }
        });
        editor.commands.addCommand({
            name: 'blog_update',
            bindKey: {win: 'Alt-B',  mac: 'Alt-B'},
            exec: function(editor) {
                save_file(true, {
                    func: trigger_server_method
                    , rc: {
                        url: rc.blog_update_url
                        , reload_opener: true
                    }
                });
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
            save_file(true, {
                func: trigger_server_method
                , rc: {
                    url: rc.sassc_url
                    , reload_opener: true
                }
            });
        });
        $('#cmd-resize').on('click', function (evt) {
            editor.resize(true);
        });
        $('#cmd-color-picker').on('click', function (evt) {
            alert('click');
        });
        $('#cmd-blog-update').on('click', function (evt) {
            save_file(true, {
                func: trigger_server_method
                , rc: {
                    url: rc.blog_update_url
                    , reload_opener: true
                }
            });
        });
        $('#cmd-blog-rebuild').on('click', function (evt) {
            save_file(true, {
                func: trigger_server_method
                , rc: {
                    url: rc.blog_rebuild_url
                    , reload_opener: true
                }
            });
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

    function init_colorpicker() {	
        $('#cmd-color-picker').jPicker(
            {
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
                    clientPath: rc.colorpicker.clientPath
                }
            }
            // commit callback
            , function (color, context) {
                var edi = PYM.editor.source.get_editor();
                edi.insert(color.val('ahex'));
                edi.focus();
            }
        );
    }

    function init(arc) {
        var get_param
        ;
        
        if (is_initialised) { return; }

        rc = $.extend({
            editor_id: 'editor'
        }, arc);

        get_param = PYM.parse_get_param();
        if (get_param.mime)     { mime = get_param.mime; }
        if (get_param.filename) { filename = get_param.filename; }
        if (get_param.hash)     { hash = get_param.hash; }
        if (get_param.reload_opener) { rc.reload_opener = parseInt(get_param.reload_opener); }
            
        init_menu();
        init_editor();
        load_file();
        init_menu_options();
        init_colorpicker();

        is_initialised = true;
    }

    function get_editor() {
        return editor;
    }


    return {
        init: init
        , get_editor: get_editor
    };
}));
