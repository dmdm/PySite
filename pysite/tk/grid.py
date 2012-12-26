# -*- coding_ utf-8 -*-

import json
import re
import sqlalchemy as sa
import sqlalchemy.sql as sasql
import colander


class GridError(Exception):
    pass


class Grid(object):

    RE_CHECK_FLD = re.compile('^[\w.]+$')
    """RegEx to check that field names have only valid chars
    """

    EVENTS = (
        # form events
        'afterclickPgButtons',
        'afterComplete',
        'afterShowForm',
        'afterSubmit',
        'beforeCheckValues',
        'beforeInitData',
        'beforeShowForm',
        'beforeSubmit',
        'onclickPgButtons',
        'onclickSubmit',
        'onInitializeForm',
        'onClose',
        'errorTextFormat',
        'serializeEditData',
        # grid events
        'afterInsertRow',
        'beforeRequest',
        'beforeSelectRow',
        'gridComplete',
        'loadBeforeSend',
        'loadComplete',
        'loadError',
        'onCellSelect',
        'ondblClickRow',
        'onHeaderClick',
        'onPaging',
        'onRightClickRow',
        'onSelectAll',
        'onSelectRow',
        'onSortCol',
        'resizeStart',
        'resizeStop',
        'serializeGridData'
    )

    def __init__(self, grid_id, locales=None):
        self.grid_id = grid_id
        if locales is None:
            locales = ['en']
        self.locales = locales
        self.requires = [
            'requirejs/domReady!',
            'jquery',
            'jqgrid/jquery.jqGrid.min'
        ]
        self._page = 1
        self._allowed_fields = []
        """
        List of valid field names
        Autogenerated when colModel is set; uses its key 'index'
        """
        self.filter_expr = None
        """
        The filter as an SQLALchemy expression suitable for ``query().filter(...)``.
        """
        self.filter = None
        """
        The requested filter as nested dict.
        """
        self._dd = None
        """
        Datadict used to build colModel
        """
        self._fieldlist = None
        """
        List of fields in datadict used to build colModel
        """
        self._total_rows = 9999
        self._total_pages = 9999
        self.opts = {
            'url'         : '',
            'datatype'    : 'json',
            'mtype'       : 'GET',
            'colNames'    : [],
            'colModel'    : [],
            'pager'       : '#gridpager',
            'rowNum'      : 30,
            'rowList'     : [10, 30, 50, 100, 250, 500, 1000],
            'sortname'    : '',
            'sortorder'   : 'asc',
            'viewrecords' : True,
            'gridview'    : True,
            'caption'     : '',
            'height'      : 345, # 345 has 15 rows with bottom pager, no caption and filter toolbar
            'rownumbers'  : True,
            'toppager'    : False,
            'width'       : 850,
            'shrinkToFit' : False,
            'rownumWidth' : 30,
            'scrollrows'  : True,
            'prmNames'    : {
                'page'      : 'pg',
                'rows'      : 'limit',
                'sort'      : 'of',
                'order'     : 'od',
                'search'    : '_search',
                'nd'        : 'nd',
                'id'        : 'id',
                'oper'      : 'oper',
                'editoper'  : 'edit',
                'addoper'   : 'add',
                'deloper'   : 'del',
                'subgridid' : 'sid',
                'npage'     : None,
                'totalrows' : 'totalrows'
            }
        }
        self.navgrid_opts = {
            'edit' : True,
            'add': True,
            'del': True,
            'search': False,
            'view': True,
            'refresh': True,
        }
        self.edit_opts = {
            'id': self.grid_id + 'edit'
            , 'afterSubmit': 'PYM.grid.doAfterSubmit'
            , 'recreateForm': True
        }
        self.add_opts = {
            'id': self.grid_id + 'add'
            , 'afterSubmit': 'PYM.grid.doAfterSubmit'
            , 'recreateForm': True
        }
        self.delete_opts = {
            'id': self.grid_id + 'del'
            , 'afterSubmit': 'PYM.grid.doAfterSubmit'
        }
        self.navgrid_search_opts = {
            'id': self.grid_id + 'search',
            'sopt': ['eq','ne','lt','le','gt','ge','bw','bn','in','ni','ew',
                'en','cn','nc'],
        }
        self.navgrid_view_opts = {'id': self.grid_id + 'view'}
        self.filter_opts = {
            'stringResult': True,
            'groupOp': 'AND',
            'defaultSearch': 'cn'
        }
        self.has_navgrid = True
        self.has_filter = True
        self.is_fluid = True
    
    def build_colmodel(self, dd, fieldlist, opts=None):
        """
        Builds colModel by given data dictionary.

        :param dd: The data dictionary
        :param fieldlist: List of fields to use.
        :param opts: Inject additional colModel options which are not set in dd
        """

        self._dd = dd
        self._fieldlist = fieldlist
        cm = []
        for f in fieldlist:
            d = dd[f]
            # Derive colModel values directly from dd
            r = {}
            r['editoptions'] = {}
            r['editrules'] = {}
            r['formoptions'] = {}
            # Grid's form uses this as ID. In HTML ids cannot have `.', so we use `-'
            # Remember that POST data has to reverse this!
            r['name'] = f.replace('.', '-')
            r['index'] = f
            #r['editrules']['required'] = True
            r['editrules']['required'] = False
            r['formoptions']['elmprefix'] = '<span class="requiredMarker">*</span>'
            r['formoptions']['elmsuffix'] = '<div id="{0}" class="formError"></div>'.format(r['name'] + '-error')
            if isinstance(d['type'], colander.Int) \
                    or isinstance(d['type'], colander.Float) \
                    or isinstance(d['type'], colander.Decimal):
                r['align'] = 'right'
            # Our title is jqGrid's label
            if 'title' in d:
                r['label'] = d['title']
            # If we'd defined a `missing' value, field is not required
            if 'missing' in d:
                r['editrules']['required'] = False
                r['formoptions']['elmprefix'] = None
                r['defaultValue'] = None if d['missing'] == colander.null else d['missing']

            # If dd has 'colModel', apply its values
            if 'colModel' in d:
                r.update(d['colModel'])

            # Apply options given by caller
            if opts:
                if f in opts:
                    if 'editoptions' in opts:
                        r['editoptions'].update(opts['editoptions'])
                        del(opts['editoptions'])
                    if 'editrules' in opts:
                        r['editrules'].update(opts['editrules'])
                        del(opts['editrules'])
                    if 'formoptions' in opts:
                        r['formoptions'].update(opts['formoptions'])
                        del(opts['formoptions'])
                    r.update(opts[f])
            cm.append(r)
        self.colModel = cm

    def apply_request(self, request):
        """
        Configures grid according to request parameters.

        The request parameters are: ``limit``, ``pg`` (page number), ``of`
        (order field), ``od`` (order direction), and ``filters`` and
        ``_search``.
        """
        # Data is from GET or POST
        if self.opts['mtype'].lower() == 'get':
            oo = request.GET
        else:
            oo = request.POST
        # Limit
        if 'limit' in oo:
            self.limit = int(oo['limit'])
        # Page number
        if 'pg' in oo:
            self.page = int(oo['pg'])
        # Order field
        if 'of' in oo:
            if not self.__class__.RE_CHECK_FLD.match(oo['of']):
                raise GridError("Invalid order field: '{0}'".format(oo['of']))
            self.order_field = oo['of']
        # Order direction
        if 'od' in oo:
            if oo['od'] not in ['asc', 'ASC', 'desc', 'DESC']:
                raise GridError("Invalid order direction: '{0}'".format(oo['od']))
            self.order_dir = oo['od']
        # Filter
        if '_search' in oo and oo['_search'] == 'true':
            if 'filters' in oo:
                self.filter = json.loads(oo['filters'])

    def parse_filter(self):
        """Parses datastruct of filter.
        
        Searchtoolbar and complex search send this struct
        Searchtoolbar must have opt['stringResult':True] for this

        {
            "groupOp":"AND",
            "rules":
                [
                    {
                        "field":"pym.principal.principal",
                        "op":"bw",
                        "data":"root"
                    },
                    {
                        "field":"pym.principal.is_enabled",
                        "op":"bw",
                        "data":"5"
                    },
                    {
                        "field":"pym.principal.is_blocked",
                        "op":"bw",
                        "data":"7"
                    },
                    {
                        "field":"pym.principal.display_name",
                        "op":"bw",
                        "data":"rrrrrr"
                    }
                ]
        }

        Or, nested:

           {
            "groupOp":"OR",
            "rules":[{"field":"a.id","op":"eq","data":"1"}],
            "groups":[
                 {
                     "groupOp":"AND",
                     "rules":[{"field":"a.id","op":"eq","data":"2"}],
                     "groups":[...]
                 }
             ]
           }
        """
        self.filter_expr = self._parse_filter_level(self.filter)

    def _parse_filter_level(self, fil):
        if fil['groupOp'].upper() == 'AND':
            group_op = sasql.and_
        elif fil['groupOp'].upper() == 'OR':
            group_op = sasql.or_
        else:
            raise GridError("Invalid groupOp: '{0}'".format(fil['groupOp']))
        rules = []
        for rule in fil['rules']:
            ty = self._dd[rule['field']]['type']
            if isinstance(ty, colander.String):
                r = sasql.column(rule['field']).ilike('%' + rule['data'] + '%')
            elif isinstance(ty, (colander.Int, colander.Float, colander.Decimal)):
                r = sasql.column(rule['field']) == rule['data']
            else:
                r = sa.cast(sasql.column(rule['field']), sa.Unicode).ilike(
                    '%' + rule['data'] + '%')
            rules.append(r)
        if 'groups' in fil:
            for group in fil['groups']:
                rules.append(self._parse_filter_level(group))
        return group_op(*rules)

    def apply_limit(self, qry):
        """
        Applies limit and offset to given query
        """
        if self.limit is not None:
            qry = qry.limit(self.limit)
        if self.offset is not None:
            qry = qry.offset(self.offset)
        return qry

    def apply_order(self, qry):
        """
        Applies sort order (ORDER BY clause) to given query
        """
        oo = []
        if self.order_field is not None:
            if not self.__class__.RE_CHECK_FLD.match(self.order_field):
                raise GridError("Invalid order field: '{0}'".format(
                    self.order_field))
            oo.append(self.order_field)
            if self.order_dir is not None:
                if self.order_dir.lower() not in ['asc', 'desc']:
                    raise GridError("Invalid order dir: '{0}'".format(
                        self.order_dir))
                oo.append(self.order_dir)
        if len(oo):
            qry = qry.order_by(" ".join(oo))
        return qry

    def apply_filter(self, qry):
        """
        Applies filter (WHERE clause) to given query.
        """
        if self.filter:
            self.parse_filter()
        if self.filter_expr is not None:
            qry = qry.filter(self.filter_expr)
        return qry

    def get_data_response(self, data, fieldlist, id_field):
        """Returns reponse to client grid

        Formats data and some params as JSON-struct that the client grid wants
        http://www.trirand.com/jqgridwiki/doku.php?id=wiki:retrieving_data#json_data
            {
              "page": "1",
              "records": "10",
              "total": "2",
              "rows": [
                  {
                      "id": 3,
                      "cell": [
                          3,
                          "cell 1",
                          "2010-09-29T19:05:32",
                          "2010-09-29T20:15:56",
                          "hurrf",
                          0 
                      ] 
                  },
                  {
                      "id": 1,
                      "cell": [
                          1,
                          "teaasdfasdf",
                          "2010-09-28T21:49:21",
                          "2010-09-28T21:49:21",
                          "aefasdfsadf",
                          1 
                      ] 
                  } 
              ]
            }
        """
        rows = []
        for row in data:
            cell = []
            for f in fieldlist:
                v = row[f]
                # We need to cast value into string, because data may be a SQLAlchemy
                # ResultProxy and values may be of type datetime.datetime(...)
                if v is not None:
                    # If we'd unconditionally call str(v), we may run into
                    # unicode conversion problems like
                    #   UnicodeEncodeError: 'ascii' codec can't encode character u'\u912d' ...
                    if not isinstance(v, str) and not isinstance(v, bool):
                        v = str(v)
                cell.append(v)
            id = row[id_field]
            rows.append( { 'id': id, 'cell': cell } )
        resp = {}
        resp['page'] = self.page
        resp['records'] = self._total_rows
        resp['total'] = self._total_pages
        resp['rows'] = rows
        return resp

    def _opts2json(self, opts):
        """
        JSON-encodes opts, renders event handlers as unquoted string.
        """
        loc_opts = opts.copy()
        evts = {}
        for evt in Grid.EVENTS:
            if evt in loc_opts:
                evts[evt] = loc_opts[evt]
                del(loc_opts[evt])
        a = []
        for k,v in evts.items():
            a.append('"' + k + '":' + v)
        s = '{' + ", ".join(a) + '}'
        return '$.extend(' + json.dumps(loc_opts) + ', ' + s + ')'

    def render_requirejs_config(self):
        """
        Returns rendered JavaScript to configure requirejs.

        This method is called from a template.
        """
        a = ["require.paths['jqgrid'] = 'libs/jqgrid';",
             "require.shim['jqgrid/jquery.jqGrid.min'] = ['ui/jquery-ui'];"
        ]
        for loc in self.locales:
            a.append(("require.shim['jqgrid/i18n/grid.locale-{loc}']"
                + "= ['jqgrid/jquery.jqGrid.min'];").format(loc=loc.lower()))
        return "\n".join(a)

    def render(self, opts_hook=None, is_fluid=None):
        """
        Returns rendered HTML and JavaScript to start the grid.

        To give client-sided JavaScript a chance to manipulate the grid
        options, parameter ``opts_hook`` may be the name of a JavaScript
        function which is called before the grid is started with the options as
        its single input parameter. The function must return the options data
        which is passed to the grid constructor.

        This method is called from a template; and the parameters can be set by
        the designer from inside a template.

        :param opts_hook: JavaScript function name
        :param is_fluid: Tells whether the grid resizes with the browser window
            or not.
        """
        if is_fluid is not None:
            self.is_fluid = is_fluid
        req = self.requires[:]
        for loc in self.locales:
            req.append("jqgrid/i18n/grid.locale-{0}".format(loc.lower()))
        sreq = json.dumps(req)
        
        sopts = self._opts2json(self.opts)
        if opts_hook:
            sopts = "{opts_hook}({opts})".format(opts_hook=opts_hook, opts=sopts)

        init = TPL_INIT.format(opts=sopts)
        
        navgrid = ''
        if self.has_navgrid:
            navgrid = TPL_NAVGRID.format(
                pager_id = self.pager_id,
                opts   = self._opts2json(self.navgrid_opts),
                edit   = self._opts2json(self.edit_opts),
                add    = self._opts2json(self.add_opts),
                dele   = self._opts2json(self.delete_opts),
                search = self._opts2json(self.navgrid_search_opts),
                view   = self._opts2json(self.navgrid_view_opts),
            )

        filter = ''
        if self.has_filter:
            filter = TPL_FILTER.format(opts=self._opts2json(self.filter_opts))

        fluid = ''
        if self.is_fluid:
            fluid = TPL_FLUID.format(grid_id=self.grid_id)

        return TPL_GRID.format(
            req=sreq,
            grid_id=self.grid_id,
            pager_id=self.pager_id,
            init=init,
            navgrid=navgrid,
            filter=filter,
            fluid=fluid
        )


    # ID
    @property
    def id(self):
        """ID of grid, for use as HTML attribute
        """
        return self.grid_id

    @id.setter
    def id(self, v):
        self.grid_id = v
        self.add_opts['id'] = v + 'add'
        self.edit_opts['id'] = v + 'edit'
        self.delete_opts['id'] = v + 'del'
        self.filter_opts['id'] = v + 'filter'
        self.refresh_opts['id'] = v + 'refresh'

    # PagerID
    @property
    def pager_id(self):
        """ID of pager, for use as HTML attribute
        """
        return self.opts['pager'].lstrip('#')

    @pager_id.setter
    def pager_id(self, v):
        self.opts['pager'] = '#' + v

    # URL
    @property
    def url(self):
        return self.opts['url']

    @url.setter
    def url(self, v):
        self.opts['url'] = v

    # colNames
    @property
    def colNames(self):
        """
        List of column names, i.e. table header
           
        Must match colModel!
        """
        return self.opts['colNames']

    @colNames.setter
    def colNames(self, v):
        self.opts['colNames'] = v

    # colModel
    @property
    def colModel(self):
        """
        List of settings for each column
        """
        return self.opts['colModel']

    @colModel.setter
    def colModel(self, v):
        self.opts['colModel'] = v
        self._allowed_fields = []
        for row in v:
            self._allowed_fields.append(row['index'])

    # rowNum
    @property
    def rowNum(self):
        """
        Show this many records in grid (limit)
        """
        return self.opts['rowNum']

    @rowNum.setter
    def rowNum(self, v):
        self.opts['rowNum'] = v

    # limit
    @property
    def limit(self):
        """
        Show this many records in grid (limit)

        Same as rowNum
        """
        return self.opts['rowNum']

    @limit.setter
    def limit(self, v):
        self.opts['rowNum'] = v

    # page
    @property
    def page(self):
        """
        Current page
        """
        return self._page

    @page.setter
    def page(self, v):
        self._page = v

    # offset
    @property
    def offset(self):
        """
        Offset, calculated from page and limit (rowNum)
        """
        return (self._page - 1) * self.limit

    # order_field
    @property
    def order_field(self):
        """
        Order by this field (opts[sortname])
        """
        return self.opts['sortname']

    @order_field.setter
    def order_field(self, v):
        self.opts['sortname'] = v

    # order_dir
    @property
    def order_dir(self):
        """
        Order in this direction (opts[sortorder])
        """
        return self.opts['sortorder']

    @order_dir.setter
    def order_dir(self, v):
        self.opts['sortorder'] = v

    # search_ops
    @property
    def search_ops(self):
        """
        Allowed operators for search/filtering
        """
        return self.navgrid_search_opts['sopt']

    @search_ops.setter
    def search_ops(self, v):
        self.navgrid_search_opts['sopt'] = v

    # total_rows
    @property
    def total_rows(self):
        """
        Total rows in last query
        """
        return self._total_rows

    @total_rows.setter
    def total_rows(self, v):
        import math
        self._total_rows = v
        self._total_pages = int(math.ceil(v / self.limit))

    # total_pages
    @property
    def total_pages(self):
        """
        Total pages in last query
        """
        return self._total_pages


TPL_INIT = """
    gr.jqGrid(
        {opts}
    );"""

TPL_NAVGRID = """
    gr.jqGrid('navGrid', '#{pager_id}',
        {opts},
        {edit},
        {add},
        {dele},
        {search},
        {view}
    );"""

TPL_FILTER = """
    gr.jqGrid('filterToolbar', {opts});"""

TPL_FLUID = """
    PYM.grid.resize(gr);
    $(window).resize(function () {{ PYM.grid.resize($('#{grid_id}')); }});
"""

TPL_GRID = """
<div class="grid">
    <table id="{grid_id}"><tr><td/></tr></table>
    <div id="{pager_id}"></div>
</div>
<script>
require({req},
function(doc, $)
{{
    var gr = $("#{grid_id}");
    {init}{navgrid}{filter}{fluid}
}});
</script>
"""
