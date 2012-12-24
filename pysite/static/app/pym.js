(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(function(require, exports, module) {
            var $ = require('jquery');
            require('ui/pnotify/jquery.pnotify');
            // Also create a global in case some scripts
            // that are loaded still are looking for
            // a global even when an AMD loader is in use.
            return (root.PYM = factory($));
        });
    } else {
        // Browser globals
        root.PYM = factory(root.$);
    }
}(this, function ($) {
    /**
     * Private
     */

    var rc
        ;

    /**
     * Public API
     */
    var my = {};

    my.gui_token = '';
    my.base_url = '';

    my.init = function (rc) {
        this.rc = rc;
        this.gui_token = rc['gui_token'];
        this.base_url = rc['gui_token'];
        my.init_growl();
        my.init_pym(rc);
        my.init_ajax();
    }

    my.init_growl = function () {
        /*$.pnotify.defaults.width = '400px';
        $.pnotify.defaults.shadow = true;
        $.pnotify.defaults.closer = true;
        */
        $.pnotify.defaults.opacity = .9;
        $.pnotify.defaults.styling = 'jqueryui';
    }

    my.init_pym = function () {
        // Enable hover css for buttons
        $('button.ui-state-default').hover(
            function(){ $(this).addClass('ui-state-hover'); }, 
            function(){ $(this).removeClass('ui-state-hover'); }
        );
    }

    my.init_ajax = function () {
        var that = this;
        $.ajaxSetup({
            headers: {
                'X-Pym-GUI-Token': that.gui_token
            }
        });
        $('body').ajaxError(function (evt, jqXHR, ajaxSettings, thrownError) {
            var resp = {};
            resp.kind = 'error';
            if (jqXHR.responseText) {
                var s = jqXHR.responseText.replace(/\n/g, '#')
                        .replace(/^.*<h1>/gi, '')
                        .replace(/<\/?[^>]+>/gi, '')
                        .replace(/#{2,}/g, '#')
                        .replace(/#+\s*$/g, '')
                        .replace(/#/g, '<br />');
                resp.text = s;
            }
            else {
                resp.text = jqXHR.status + ' ' + jqXHR.statusText;
            }
            resp.title = 'Ajax Error';
            resp.insert_brs = false;
            that.growl(resp);
        });
    }
    
    /**
     * Sort select list by text
     *
     * http://sebastienayotte.wordpress.com/2009/08/04/sorting-drop-down-list-with-jquery/
     */
    my.sort_select_by_text = function (e) {
        $(e).html($("option", $(e)).sort(function(a, b) {
            return a.text == b.text ? 0 : a.text < b.text ? -1 : 1
        }));
    }

    /**
     * Cookie object
     *
     * Code inspired by http://www.quirksmode.org/js/cookies.html
     */
    my.cookie = {
        write: function (name, value, days, path) {
            if (days) {
                var date = new Date();
                date.setTime(date.getTime()+(days*24*60*60*1000));
                var expires = '; expires=' + date.toGMTString();
            }
            else var expires = '';
            if (! path) path = window.location.pathname
                .replace(/\/[^/]*$/, '/');
            document.cookie = name + '=' + value + expires
                + '; path=' + path;
        }

        , read: function (name) {
            var nameEQ = name + "=";
            var ca = document.cookie.split(';');
            for(var i=0;i < ca.length;i++) {
                var c = ca[i];
                while (c.charAt(0)==' ') c = c.substring(1, c.length);
                if (c.indexOf(nameEQ) == 0)
                    return c.substring(nameEQ.length, c.length);
            }
            return null;
        }

        , delete: function (name) {
            PYM.cookie.write(name, '', -1);
        }
    }

    my.growl = function(msg) {
        if (! msg.kind) msg.kind = 'notice';
        if (! msg.title) msg.title = msg.kind;
        // Put timestamp into title
        // We get time as UTC
        var dt;
        if (msg.time) {
            dt = new Date(Date.UTC(m.time[0], m.time[1], m.time[2], m.time[3],
                m.time[4], m.time[5]));
        }
        else {
            dt = new Date();
        }
        msg.title = msg.title
            + '<br><span style="font-weight:normal;font-size:xx-small;">'
            + dt.toString()
            + '</span>';
        // Setup type, icon and persistance according to kind
        var icon;
        switch (msg.kind[0]) {
            case 'n':
                msg.type = 'notice';
                icon = 'ui-icon ui-icon-comment';
                break;
            case 'i':
                msg.type = 'info';
                icon = 'ui-icon ui-icon-info';
                break;
            case 'w':
                msg.type = 'warning';
                icon = 'ui-icon ui-icon-notice';
                break;
            case 'e':
                icon = 'ui-icon ui-icon-alert';
                msg.type = 'error';
                break;
            case 'f':
                icon = 'ui-icon ui-icon-alert';
                msg.type = 'error';
                break;
            case 's':
                icon = 'ui-icon ui-icon-check';
                msg.type = 'success';
                break;
        }
        if (! msg.icon) msg.icon = icon;
        msg.hide = ! (msg.kind[0] == 'e' || msg.kind[0] == 'f');
        // Show message
        $.pnotify(msg);
    }

    my.grid = {
        resize: function (grid) {
            p = grid.closest('.ui-jqgrid').parent();
            width = p.innerWidth();
            grid.setGridWidth(width);
        }
        , doAfterSubmit: function (response, postdata) {
            var resp = $.parseJSON(response.responseText);
            var ok = resp.status;
            $('.formError', '.ui-jqdialog').html('');
            if (ok) {
                var new_id = resp.new_id || null;
                var msg = resp.msg || 'Ok';
                return [ true, msg, new_id ];
            }
            else {
                var msg = resp.msg || 'Errors';
                var errors = resp.errors;
                for (var k in errors) {
                    var id = '#' + k.replace(/\./g, '-');
                    var div_id = id + '-error';
                    $(div_id).html(errors[k]);
                }
                return [ false, msg, null ];
            }
        }
    };

    return my;
}));

