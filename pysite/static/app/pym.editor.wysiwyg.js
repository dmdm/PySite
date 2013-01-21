(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(function(require, exports, module) {
            var PYM = require('pym');
            require('pym.editor');
            // Also create a global in case some scripts
            // that are loaded still are looking for
            // a global even when an AMD loader is in use.
            return (root.PYM.editor.wysiwyg = factory($, PYM));
        });
    } else {
        // Browser globals
        root.PYM.editor.wysiwyg = factory(root.$, root.PYM);
    }
}(this, function ($, PYM) {
    "use strict";

    var rc
        , area_ids = []
    ;

    /**
     * Check editable areas for valid IDs
     *
     * If an area has no ID, Aloha sets its own. This is not desired.
     * We need our own well-defined IDs to identify the parts in the file
     * that will be overwritten by a save. Aloha's IDs are unknown to the
     * file.
     */
    function check_area_ids(selector) {
        $(selector).each(function (ix) {
            var elm = $(this)
                , id = elm.attr('id')
            ;
            if (! id) {
                elm.prepend('<div style="background-color: red; color: yellow;'
                    +' font-weight: bold; font-size: 16px;">'
                    + 'Missing ID, cannot save this area!</div>');
            }
            else {
                area_ids.push(id);
            }
        });
    }

    //(username, logout_url, save_url, source_url, selector, mime, filename, hash)
    function init(arc) {
        rc = arc;

        // Init our toolbar
        $('body').prepend('<div id="pysite-aloha" style="color: black; background-color: silver; border: inset 2px grey; padding: 1px;">'
            + '<div style="margin-right: 0.5em; display: inline-block;">'+rc.username
            + '&nbsp;<a href="'+rc.logout_url+'">logout</a>'
            +'</div>'
            + '<button id="btn-save-content" style="font-weight:bold; color:green;">SAVE</button>'
            + '<button id="btn-toggle-wysiwyg" data-state="1">Switch off</button>'
            + '<button id="btn-open-source">Source</button>'
            + '<button id="btn-filemgr">FileManager</button>'
            + '</div>'
            + '<div style="clear: both; line-height: 0px; height: 0px;"></div>'
        );
       
        // Check IDs and activate Aloha
        check_area_ids(rc.selector);
        PYM.growl({kind:'notice', text:'Click in a yellow frame to edit.<br>Do not forget to <span style="color:green; font-weight:bold;">SAVE</span> the page!'});
        Aloha.jQuery(rc.selector).aloha();
        
        // On Save
        $('#btn-save-content').on('click', function (evt) {
            var data = {}
                , opts = {
                    url: rc.save_url
                    , type: 'POST'
                    , data: data
                }
            ;
            // Collect content of all editable areas that have a valid ID
            // XXX Must we deactivate Aloha to get the edited content?
            $(rc.selector).each(function (ix) {
                var elm = $(this)
                    , id = elm.attr('id')
                ;
                if (area_ids.indexOf(id) >= 0) {
                    data[id] = elm.html();
                }
            });
            // Send contents to server
            $.ajax(opts)
                .done(function (resp) {
                    console.log(resp);
                    $(resp.msgs).each(function () {
                        PYM.growl(this);
                    });
                });
        });

        // On toggle
        $('#btn-toggle-wysiwyg').on('click', function (evt) {
            var btn = $(this)
                , state = btn.data('state')
            ;
            if (state) {
                // Switch off
		        Aloha.jQuery(rc.selector).mahalo();
                btn.data('state', 0);
                btn.html('Switch on');
            }
            else {
                // Switch on
		        Aloha.jQuery(rc.selector).aloha();
                btn.data('state', 1);
                btn.html('Switch off');
            }
        });

        // On open-source
        $('#btn-open-source').on('click', function (evt) {
            PYM.editor.open_source_window(rc.mime, rc.filename, rc.hash,
                rc.source_url, 1);
        });

        // On FileManager
        $('#btn-filemgr').on('click', function (evt) {
            window.location.href = rc.filemgr_url;
        });
    }

    return {
        init: init
    };
}));
