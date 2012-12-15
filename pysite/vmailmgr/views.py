# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
import pysite.vmailmgr
from pysite.vmailmgr.models import Domain
from pysite.models import DbSession, todata
from pysite.tk.grid import Grid


GRID_ID = 'grid-domains'

GRIDOPTS = {
    #'onSelectRow': "$.proxy(PYM.UsrMgr.user_row_selected, PYM.UsrMgr)",
    'multiselect': True,
    'multiboxonly': True
}

COLOPTS = None

BROWSE_FIELDLIST = (
    'is_enabled',
    'id',
    'name',
    'tenant_display_name',
    'tenant_id',
    'used_mailboxes',
    'max_mailboxes',
    'used_aliases',
    'max_aliases',
    'quota',
    'mtime',
    #'editor_display_name',
    'editor',
    'ctime',
    #'owner_display_name',
    'owner'
)

DD = pysite.vmailmgr.models.DomainDd
ORDER_FIELD = 'id'
ID_FIELD = 'id'


def fetch_browse_data(request, grid):
    fmap = dict(
        tenant_display_name = lambda it: it.tenant.display_name,
        used_mailboxes = lambda it: len(it.mailboxes),
        used_aliases = lambda it: len(it.aliases)
    )
    sess = DbSession()
    # Specify entities, joins and columns
    qry = sess.query(Domain)
    # Apply filter, sort order and limit
    #qry = grid.apply_query(qry)
    total = qry.count()
    data = todata(qry.all(), fmap=fmap)
    return (data, total, )


@view_defaults(
    context=pysite.vmailmgr.models.Node,
    permission='manage_vmail'
)
class VmailMgrView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        name='',
        renderer='pysite:vmailmgr/templates/index.mako',
    )
    def index(self):
        gr = Grid(GRID_ID)
        gr.url = self.request.resource_url(self.context, 'xhr_browse')
        gr.add_opts['url'] = self.request.resource_url(self.context, "xhr_add")
        gr.edit_opts['url'] = self.request.resource_url(self.context, "xhr_edit")
        gr.delete_opts['url'] = self.request.resource_url(self.context, "xhr_delete")
        gr.build_colmodel(DD, fieldlist=BROWSE_FIELDLIST, opts=COLOPTS)
        gr.order_field = ORDER_FIELD
        return dict(grid=gr)

    @view_config(
        name='xhr_browse',
        renderer='json',
    )
    def xhr_browse(self):
        grid = Grid(GRID_ID)
        grid.build_colmodel(DD, fieldlist=BROWSE_FIELDLIST)
        grid.order_field = ORDER_FIELD
        grid.apply_request(self.request)
        data, total = fetch_browse_data(self.request, grid)
        grid.total_rows = total
        resp = grid.get_data_response(data, BROWSE_FIELDLIST, ID_FIELD)
        return resp
