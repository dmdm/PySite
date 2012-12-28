(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(function(require, exports, module) {
            var PYM = require('pym');
            require('libs/jstorage');
            // Also create a global in case some scripts
            // that are loaded still are looking for
            // a global even when an AMD loader is in use.
            return (root.PYM.grid = factory($, PYM));
        });
    } else {
        // Browser globals
        root.PYM.grid = factory(root.$, root.PYM);
    }
}(this, function ($, PYM) {
    /**
     * Private
     */
    function resize(grid) {
        p = grid.closest('.ui-jqgrid').parent();
        width = p.innerWidth();
        grid.setGridWidth(width);
    }

    function doAfterSubmit(response, postdata) {
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

    /**
     * Persisting grid state based on Oleg's example on StackOverflow:
     * http://www.ok-soft-gmbh.com/jqGrid/ColumnChooserAndLocalStorage.htm
     * http://stackoverflow.com/questions/8422878/persisting-jqgrid-column-preferences/8436273#8436273
     */

    /**
     * Returns data struct that describes current grid state.
     *
     * State comprises ordering of columns (permutation), ordering of rows,
     * current page, filter settings.
     *
     * TODO  Rows per page
     *
     * :param gr: jqueryfied instance of the grid, e.g. $(this) from inside an
     *     event handler.
     * :returns: Data struct
     */
    function collect_state(gr) {
        var colModel = gr.jqGrid('getGridParam', 'colModel')
            , i
            , cmlen = colModel.length
            , col
            , name
            , post_data = gr.jqGrid('getGridParam', 'postData')
            , state = {
                search: gr.jqGrid('getGridParam', 'search')
                , page: gr.jqGrid('getGridParam', 'page')
                , sortname: gr.jqGrid('getGridParam', 'sortname')
                , sortorder: gr.jqGrid('getGridParam', 'sortorder')
                , permutation: gr[0].p.remapColumns
                , cols: {}
            }
        ;
        if (typeof (post_data.filters) !== 'undefined') {
            state.filters = post_data.filters;
        }
        for (i=0; i<cmlen; i++) {
            col = colModel[i];
            name = col.name;
            // Omit columns of row number (rn), checkbox (cb) and subgrid.
            if (name !== 'rn' && name !== 'cb' && name !== 'subgrid') {
                state.cols[name] = {
                    width: col.width,
                    hidden: col.hidden
                };
            }
        }
        return state;
    }

    /**
     * Loads grid state and applies it to options.
     *
     * It seems best to apply the saved state to the grid options before
     * the grid is constructed. If we'd e.g. modify the colModel thereafter,
     * the grid seems not to reflect the changes although we can fetch the
     * colModel again and see the changed values there. A grid.trigger('reloadGrid')
     * does not help.
     *
     * This function is used as a opts_hook, i.e. its input is the opts struct,
     * and it outputs the opts struct again.
     */
    function apply_state(opts) {
        var colModel = opts.colModel
            , i
            , cmlen = colModel.length
            , name
            , col
            , state = load_state(opts.grid_id)
        ;
        console.log('State is:', state)
        if (state) {
            opts.search = state.search;
            opts.page = state.page;
            opts.sortname = state.sortname;
            opts.sortorder = state.sortorder;
            opts.postData = { filters: state.filters };
            for (i=0; i<cmlen; i++) {
                col = colModel[i];
                name = col.name;
                if (name !== 'rn' && name !== 'cb' && name !== 'subgrid') {
                    colModel[i] = $.extend(true, {}, colModel[i], state.cols[name]);
                }
            }
        }
        return opts;
    }

    /**
     * Collects state from given grid and stores it.
     *
     * :param gr: jqueryfied instance of grid.
     */
    function save_state(gr) {
        var state = collect_state(gr)
            , key = window.location.pathname + '#' + gr[0].id
        ;
        console.log('saving key:', key, state)
        $.jStorage.set(key, state);
    }

    /**
     * Loads state from storage and returns it.
     *
     * :param gr_or_grid_id: jqueryfied instance of grid or grid ID as string.
     */
    function load_state(gr_or_grid_id) {
        var grid_id = gr_or_grid_id[0].id || gr_or_grid_id
            , key = window.location.pathname + '#' + grid_id
            , state = $.jStorage.get(key)
        ;
        console.log('loaded key:', key, state);
        return state;
    }

    /**
     * Deletes state from storage.
     *
     * :param gr_or_grid_id: jqueryfied instance of grid or grid ID as string.
     */
    function delete_state(gr_or_grid_id) {
        var grid_id = gr_or_grid_id[0].id || gr_or_grid_id
            , key = window.location.pathname + '#' + grid_id
        console.log('deleted key:', key);
        $.jStorage.deleteKey(key);
    }

    function init_state_handler(gr) {
        console.log('backend:', $.jStorage.currentBackend());
        console.log('available:', $.jStorage.storageAvailable());
        gr.bind('jqGridAfterLoadComplete.loadstate', function () {
            console.log('Loading state');
            var state = PYM.grid.load_state($(this));
            if (state && state.permutation.length) {
                console.log('applying permutations:', state.permutation);
                $(this).jqGrid("remapColumns", state.permutation, true);
            }
            $(this).unbind('jqGridAfterLoadComplete.loadstate');
        });
        gr.bind('jqGridAfterLoadComplete.savestate', function () {
            console.log('Saving state after load complete');
            PYM.grid.save_state($(this));
        });
        gr.bind('jqGridResizeStop.savestate', function () {
            console.log('Saving state on resize stop');
            PYM.grid.save_state($(this));
        });
    }

    /**
     * Public API
     */
    var my = {};

    my = {
        resize: resize
        , doAfterSubmit: doAfterSubmit
        , apply_state: apply_state
        , load_state: load_state
        , save_state: save_state
        , delete_state: delete_state
        , init_state_handler: init_state_handler
    };

    return my;
}));

