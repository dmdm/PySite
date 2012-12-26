# -*- coding: utf-8 -*-

import copy
import colander
import sqlalchemy as sa
from pyramid.view import view_config, view_defaults
import datetime
from sqlalchemy.exc import StatementError
from sqlalchemy.orm.exc import NoResultFound

import pysite.authmgr
from pysite.authmgr.models import (RoleMemberDd, RoleMember, PrincipalDd,
    RoleDd)
import pysite.authmgr.manager as manager
from pysite.models import DbSession, todata
from pysite.tk.grid import Grid
from pysite.exc import PySiteError


@view_defaults(
    context=pysite.authmgr.models.NodeRoleMember,
    permission='manage_auth'
)
class RoleMemberView(object):

    def _build_browse_queries(self, request, grid):
        sess = DbSession()
        vw_browse = pysite.authmgr.models.get_vw_rolemember_browse()
        # Build query for count and apply filter
        qry_total = sess.query(sa.func.count(vw_browse.c.id))
        qry_total = grid.apply_filter(qry_total)
        # Build query for data
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

    def _fetch_browse_data(self, data_qry, total_qry):
        total = total_qry.one()[0]
        rs = data_qry
        data = todata(rs)
        return (data, total, )

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.ENTITY = RoleMember
        self.GRID_ID = 'grid-rolemembers'

        self.GRID_OPTS = {
            'multiselect': True,
            'multiboxonly': True
        }
        self.NAVGRID_OPTS = {
            'add': False,
            'edit': False,
        }

        self.COLOPTS = None

        self.DD = copy.deepcopy(RoleMemberDd)
        for f in ['id', 'principal', 'is_enabled', 'is_blocked', 'email',
                'first_name', 'last_name', 'display_name', 'notes']:
            self.DD['principal_' + f] = copy.deepcopy(PrincipalDd[f])
        for f in ['id', 'name', 'notes']:
            self.DD['role_' + f] = copy.deepcopy(RoleDd[f])
        self.DD['principal_id']['title'] = 'Principal Id'
        self.DD['role_id']['title'] = 'Role Id'
        self.DD['role_name']['title'] = 'Role Name'
        self.DD['role_notes']['title'] = 'Role Notes'

        # If the fieldnames are fully qualified, this is the prefix, e.g.
        # ``myschema.mytable.``. Mind the trailing dot!
        self.PREFIX = ''
        self.PREFIXLEN = len(self.PREFIX)
        self.ID_FIELD = 'id'
        self.BROWSE_FIELDLIST = [
            'id',
            'principal_id',
            'principal_principal',
            'principal_is_enabled',
            'principal_is_blocked',
            'principal_email',
            'principal_first_name',
            'principal_last_name',
            'principal_display_name',
            'principal_notes',
            'role_id',
            'role_name',
            'role_notes',
            'ctime',
            'owner',
            'owner_display_name'
        ]
        self.EDIT_FIELDLIST = []
        for k, d in self.DD.items():
            if k.startswith('__'):
                continue
            d['colModel']['editable'] = (k in self.EDIT_FIELDLIST)

    @view_config(
        name='',
        renderer='pysite:authmgr/templates/rolemember/index.mako',
    )
    def index(self):
        gr = Grid(self.GRID_ID)
        gr.opts.update(self.GRID_OPTS)
        gr.navgrid_opts.update(self.NAVGRID_OPTS)
        gr.url = self.request.resource_url(self.context, 'xhr_browse')
        gr.add_opts['url'] = self.request.resource_url(self.context,
            "xhr_create")
        gr.edit_opts['url'] = self.request.resource_url(self.context,
            "xhr_update")
        gr.delete_opts['url'] = self.request.resource_url(self.context,
            "xhr_delete")

        self._build_browse_queries(self.request, gr)
        gr.build_colmodel(self.DD, fieldlist=self.BROWSE_FIELDLIST,
            opts=self.COLOPTS)
        return dict(grid=gr)

    @view_config(
        name='xhr_browse',
        renderer='json',
    )
    def xhr_browse(self):
        gr = Grid(self.GRID_ID)
        # Need to build the colModel here to initialise the list of allowed
        # fields e.g. for search.
        gr.build_colmodel(self.DD, fieldlist=self.BROWSE_FIELDLIST,
            opts=self.COLOPTS)
        # Apply request before building the queries. Otherwise
        # build_browse_queries() gets an unitialised grid and sets defaults
        # e.g. for order_field. The settings from the request will then not
        # be applied to the queries.
        gr.apply_request(self.request)
        data_qry, total_qry = self._build_browse_queries(self.request, gr)
        data, total = self._fetch_browse_data(data_qry, total_qry)
        gr.total_rows = total
        resp = gr.get_data_response(data, self.BROWSE_FIELDLIST, self.ID_FIELD)
        return resp

    @view_config(
        name='xhr_create',
        renderer='json',
    )
    def xhr_create(self):
        sch = pysite.dd.build_schema(colander.MappingSchema, self.DD,
            fieldlist=self.EDIT_FIELDLIST)
        try:
            data = pysite.dd.deserialize(sch, self.request.POST)
        except colander.Invalid as exc:
            return {'status': False, 'msg': 'Errors', 'errors': exc.asdict()}
        try:
            vv = {}
            for k, v in data.items():
                vv[k[self.PREFIXLEN:]] = v
            vv['owner'] = self.request.user.uid
            vv['ctime'] = datetime.datetime.now()
            manager.create_rolemember(vv)
            return {'status': True, 'msg': 'Ok'}
        except (StatementError, NoResultFound, PySiteError) as exc:
            return {'status': False, 'msg': str(exc), 'errors': {}}

    @view_config(
        name='xhr_delete',
        renderer='json',
    )
    def xhr_delete(self):
        try:
            ids = [int(x) for x in self.request.POST['id'].split(',')
                if int(x) != 0]
            for id in ids:
                manager.delete_rolemember(id)
            return {'status': True, 'msg': 'Ok'}
        except (StatementError, NoResultFound, PySiteError) as exc:
            return {'status': False, 'msg': str(exc), 'errors': {}}
