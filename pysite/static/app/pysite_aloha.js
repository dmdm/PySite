(function () {
    "use strict";
   
    var $ = Aloha.jQuery
        , area_ids = []
        , selector
        , gui_token
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

    function init_ajax() {
        $.ajaxSetup({
            headers: {
                'X-Pym-GUI-Token': gui_token
            }
        });
        $('body').ajaxError(function (evt, jqXHR, ajaxSettings, thrownError) {
            var msg = 'AJAX ERROR: ';
            if (jqXHR.responseText) {
                msg += jqXHR.responseText.replace(/\n/g, '#')
                        .replace(/^.*<h1>/gi, '')
                        .replace(/<\/?[^>]+>/gi, '')
                        .replace(/#{2,}/g, '#')
                        .replace(/#+\s*$/g, '')
                        .replace(/#/g, '<br />');
            }
            else {
                msg += jqXHR.status + ' ' + jqXHR.statusText;
            }
            growl_error(msg);
        });
    }



    function growl_reset() {
        $('#pysite-aloha-status').html('Hello Josephine')
            .css({'color': 'grey', 'font-size':'100%', 'font-weight': 'normal'});
    }

    function growl(msg) {
        $('#pysite-aloha-status').html(msg)
            .css('color', 'blue');
        window.setTimeout(growl_reset, 15000);
    }

    function growl_ok(msg) {
        $('#pysite-aloha-status').html(msg)
            .css({'color': 'green', 'font-weight': 'bold'});
        window.setTimeout(growl_reset, 15000);
    }

    function growl_error(msg) {
        $('#pysite-aloha-status').html(msg)
            .css({color: 'red', 'font-size': '16px', 'font-weight': 'bold'});
        window.setTimeout(growl_reset, 30000);
    }

    function init(username, logout_url, save_url, aselector, agui_token) {
        selector = aselector;
        gui_token = agui_token;

        // Init our toolbar
        $('body').prepend('<div id="pysite-aloha" style="color: black; background-color: silver; border: inset 2px grey; padding: 1px;">'
            + '<div style="margin-right: 0.5em; display: inline-block;">'+username
            + '&nbsp;<a href="'+logout_url+'">logout</a>'
            +'</div>'
            + '<button id="btn-save-aloha">SAVE</button>'
            + '<button id="btn-toggle-aloha" data-state="1">Switch off</button>'
            + '<div id="pysite-aloha-status" style="margin-left: 0.5em; display: inline-block;">'
            + 'Hello Josephine'
            + '</div>'
            + '</div>'
            + '<div style="clear: both; line-height: 0px; height: 0px;"></div>'
        );
       
        init_ajax();
        // Check IDs and activate Aloha
        check_area_ids(selector);
        $(selector).aloha();
        growl('Aloha');
        
        // On Save
        $('#btn-save-aloha').on('click', function (evt) {
            var data = {}
                , opts = {
                    url: save_url
                    , type: 'POST'
                    , data: data
                }
            ;
            // Collect content of all editable areas that have a valid ID
            // XXX Must we deactivate Aloha to get the edited content?
            $(selector).each(function (ix) {
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
                    var msgs = [];
                    $(resp.msgs).each(function () {
                        msgs.push(this.text);
                    });
                    if (resp.ok) {
                        growl_ok(msgs.join('<br>'));
                    }
                    else {
                        growl_error(msgs.join('<br>'));
                    }
                });
        });

        // On toggle
        $('#btn-toggle-aloha').on('click', function (evt) {
            var btn = $(this)
                , state = btn.data('state')
            ;
            if (state) {
                // Switch off
		        Aloha.jQuery(selector).mahalo();
                btn.data('state', 0);
                btn.html('Switch on');
            }
            else {
                // Switch on
		        Aloha.jQuery(selector).aloha();
                btn.data('state', 1);
                btn.html('Switch off');
            }
        });
    }

    window.pysite_aloha = init;
}());
