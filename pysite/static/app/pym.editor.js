(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(function(require, exports, module) {
            var PYM = require('pym');
            require('libs/jstorage');
            // Also create a global in case some scripts
            // that are loaded still are looking for
            // a global even when an AMD loader is in use.
            return (root.PYM.editor = factory($, PYM));
        });
    } else {
        // Browser globals
        root.PYM.editor = factory(root.$, root.PYM);
    }
}(this, function ($, PYM) {
    "use strict";
   
    var source_windows = {}
    ;

    /**
     * Opens window with source editor.
     *
     * :param amime: Mimetype of the file.
     * :param afilename: Clear text basename of file.
     * :param ahash: Hash of path of file, as used by filemgr.
     * :param aurl: URL to load the editor
     */
    function open_source_window(amime, afilename, ahash, aurl, areload_opener) {
        var data = {
                  mime: amime
                , filename: afilename
                , hash: ahash
                , reload_opener: areload_opener
            }
            , url = aurl
            , qq = []
            , k
            , win
        ;

        for (k in data) {
            qq.push(encodeURIComponent(k) + '=' + encodeURIComponent(data[k])); 
        }
        url += '?' + qq.join('&');
        if (source_windows[data['hash']]) {
            source_windows[data['hash']].focus();
        }
        else {
            win = window.open(url, data['hash'],
                     'resizable=yes,scrollbars=yes,status=yes,centerscreen=yes,width=700,chrome=yes'
            );
            win.onunload = function() {
                for (k in source_windows) {
                    if (source_windows[k] == this) {
                        console.log('Deleting: ' + k);
                        delete source_windows[k];
                        break;
                    }
                }
            };
            source_windows[data['hash']] = win;
        }
    }

    return {
        open_source_window: open_source_window
    };
}));
