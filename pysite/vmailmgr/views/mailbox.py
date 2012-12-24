# -*- coding: utf-8 -*-

import copy
import colander
import sqlalchemy as sa
from pyramid.view import view_config, view_defaults

import pysite.vmailmgr
from pysite.vmailmgr.models import DomainDd
from pysite.usrmgr.models import PrincipalDd
from pysite.models import DbSession
from pysite.tk.grid import Grid


GRID_ID = 'grid-domains'

GRIDOPTS = {
    #'onSelectRow': "$.proxy(PYM.UsrMgr.user_row_selected, PYM.UsrMgr)",
    'multiselect': True,
    'multiboxonly': True
}

COLOPTS = None


DD = copy.deepcopy(DomainDd)
DD['tenant_display_name'] = copy.deepcopy(PrincipalDd['display_name'])
DD['tenant_display_name']['title'] = 'Tenant'
DD['tenant_display_name']['colModel']['editable'] = False
DD['used_mailboxes'] = {
    'type': colander.Int(),
    'title': "Used Mailboxes",
    'colModel': {
        'width': 50,
        'editable': False
    }
}
DD['used_aliases'] = {
    'type': colander.Int(),
    'title': "Used Aliases",
    'colModel': {
        'width': 50,
        'editable': False
    }
}

# The returned data is a list of lists, so we need to specify ID_FIELD as a
# numeric column index.
ID_FIELD = 1  # 'vmail_domain.id'
# The sequence of the fields here must match the sequence of columns in the
# query!!
BROWSE_FIELDLIST = [
    'is_enabled',
    'id',
    'name',
    'tenant_id',
    'tenant_display_name',
    'used_mailboxes',
    'max_mailboxes',
    'used_aliases',
    'max_aliases',
    'quota',
    'mtime',
    'editor',
    'editor_display_name',
    'ctime',
    'owner',
    'owner_display_name'
]


def build_browse_queries(request, grid):
    sess = DbSession()
    vw_browse = pysite.vmailmgr.models.get_vw_domain_browse()
    # Build query for count and apply filter
    qry_total = sess.query(sa.func.count(vw_browse.c.id))
    qry_total = grid.apply_filter(qry_total)
    qry = sess.query(vw_browse)
    # Setup field names for initial order and primary key
    if not grid.order_field:
        grid.order_field = 'id'
    # Apply filter, order and limit from grid to qry.
    # Grid must have been initialised with order_field for this.
    qry = grid.apply_filter(qry)
    qry = grid.apply_order(qry)
    qry = grid.apply_limit(qry)
    return (qry, qry_total, )


def fetch_browse_data(data_qry, total_qry):
    total = total_qry.count()
    data = data_qry.all()
    return (data, total, )


@view_defaults(
    context=pysite.vmailmgr.models.NodeMailbox,
    permission='manage_vmail'
)
class MailboxView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        name='',
        renderer='pysite:vmailmgr/templates/mailbox/index.mako',
    )
    def index(self):
        return dict()
