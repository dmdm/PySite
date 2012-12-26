# -*- coding: utf-8 -*-

import copy
import colander
import sqlalchemy as sa
from pyramid.view import view_config, view_defaults
import datetime
from sqlalchemy.exc import StatementError
from sqlalchemy.orm.exc import NoResultFound

import pysite.authmgr
from pysite.authmgr.models import PrincipalDd, Principal, Role, RoleMember
import pysite.authmgr.manager as manager
from pysite.models import DbSession, todata
from pysite.tk.grid import Grid
from pysite.exc import PySiteError
import pysite.lib


@view_defaults(
    context=pysite.authmgr.models.NodePrincipal,
    permission='manage_auth'
)
class PrincipalView(object):

    def _build_browse_queries(self, request, grid):
        sess = DbSession()
        vw_browse = pysite.authmgr.models.get_vw_principal_browse()
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

        self.ENTITY = Principal
        self.GRID_ID = 'grid-principals'

        self.GRIDOPTS = {
            'multiselect': True,
            'multiboxonly': True
        }

        self.COLOPTS = None

        self.DD = copy.deepcopy(PrincipalDd)
        # Cannot deepcopy colander.Email, so the original DD does not define
        # it, we must define it here.
        self.DD['email']['validator'] = colander.Email()

        # If the fieldnames are fully qualified, this is the prefix, e.g.
        # ``myschema.mytable.``. Mind the trailing dot!
        self.PREFIX = ''
        self.PREFIXLEN = len(self.PREFIX)
        self.ID_FIELD = 'id'
        self.BROWSE_FIELDLIST = [
            'is_enabled',
            'is_blocked',
            'id',
            'principal',
            'pwd',
            'email',
            'first_name',
            'last_name',
            'display_name',
            'notes',
            'login_time',
            'prev_login_time',
            'identity_url',
            'gui_token',
            'mtime',
            'editor',
            'editor_display_name',
            'ctime',
            'owner',
            'owner_display_name'
        ]
        self.EDIT_FIELDLIST = [
            'is_enabled',
            'is_blocked',
            'principal',
            'pwd',
            'email',
            'first_name',
            'last_name',
            'display_name',
            'notes',
        ]
        for k, d in self.DD.items():
            if k.startswith('__'):
                continue
            d['colModel']['editable'] = (k in self.EDIT_FIELDLIST)

    @view_config(
        name='',
        renderer='pysite:authmgr/templates/principal/index.mako',
    )
    def index(self):
        gr = Grid(self.GRID_ID)
        gr.opts.update(self.GRIDOPTS)
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

        sess = DbSession
        roles = sess.query(Role.id, Role.name).order_by(Role.name).all()
        create_rolemember_url = self.request.resource_url(self.context,
            'xhr_create_rolemember')
        return dict(grid=gr, roles=roles,
            create_rolemember_url=create_rolemember_url)

    @view_config(
        name='xhr_create_rolemember',
        renderer='json',
    )
    def xhr_create_rolemember(self):
        log = pysite.lib.StatusResp()
        principal_ids = [int(x) for x in self.request.POST.getall(
            'principal_ids[]') if int(x) != 0]
        if not principal_ids:
            log.error('No principals selected')
            return log.resp
        role_ids = [int(x) for x in self.request.POST.getall(
            'role_ids[]') if int(x) != 0]
        if not role_ids:
            log.error('No roles selected')
            return log.resp
        sess = DbSession()
        try:
            for rid in role_ids:
                for pid in principal_ids:
                    # XXX This is not atomic!
                    if not sess.query(RoleMember.id).filter(
                            sa.and_(RoleMember.principal_id == pid,
                                RoleMember.role_id == rid)).all():
                        manager.create_rolemember(dict(
                            owner=self.request.user.uid,
                            principal_id=pid,
                            role_id=rid
                        ))
        except (StatementError) as exc:
            log.fatal(str(exc))
            return log.resp
        else:
            log.ok("{0} principals added to {1} roles"
                .format(len(principal_ids), len(role_ids)))
            return log.resp

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
            manager.create_principal(vv)
            return {'status': True, 'msg': 'Ok'}
        except (StatementError, NoResultFound, PySiteError) as exc:
            return {'status': False, 'msg': str(exc), 'errors': {}}

    @view_config(
        name='xhr_update',
        renderer='json',
    )
    def xhr_update(self):
        sch = pysite.dd.build_schema(colander.MappingSchema, self.DD,
            fieldlist=self.EDIT_FIELDLIST)
        try:
            data = pysite.dd.deserialize(sch, self.request.POST)
        except colander.Invalid as exc:
            return {'status': False, 'msg': 'Errors', 'errors': exc.asdict()}
        try:
            vv = {}
            for k, v in data.items():
                # If client did not set a new password, keep the current one.
                if k == 'pwd' and (v is None or v == ''):
                    continue
                vv[k[self.PREFIXLEN:]] = v
            vv['id'] = int(self.request.POST['id'])
            vv['editor'] = self.request.user.uid
            vv['mtime'] = datetime.datetime.now()
            manager.update_principal(vv)
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
                manager.delete_principal(id)
            return {'status': True, 'msg': 'Ok'}
        except (StatementError, NoResultFound, PySiteError) as exc:
            return {'status': False, 'msg': str(exc), 'errors': {}}
