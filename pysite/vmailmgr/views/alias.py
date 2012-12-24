# -*- coding: utf-8 -*-

import copy
import colander
import sqlalchemy as sa
from pyramid.view import view_config, view_defaults
import markupsafe
import datetime
from sqlalchemy.exc import StatementError
from sqlalchemy.orm.exc import NoResultFound

import pysite.vmailmgr
from pysite.vmailmgr.models import AliasDd, Alias, DomainDd, Domain
from pysite.models import DbSession, todata
from pysite.tk.grid import Grid


@view_defaults(
    context=pysite.vmailmgr.models.NodeAlias,
    permission='manage_vmail'
)
class AliasView(object):

    def _build_browse_queries(self, request, grid):
        sess = DbSession()
        vw_browse = pysite.vmailmgr.models.get_vw_alias_browse()
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

    def _fetch_browse_data(self, data_qry, total_qry):
        total = total_qry.count()
        rs = data_qry
        data = todata(rs)
        return (data, total, )

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.ENTITY = Alias
        self.GRID_ID = 'grid-aliases'

        self.GRIDOPTS = {
            'multiselect': True,
            'multiboxonly': True
        }

        self.COLOPTS = None

        self.DD = copy.deepcopy(AliasDd)
        self.DD['domain_id']['colModel'].update(dict(
            editable=True,
            edittype='select',
            editoptions=dict(
                dataUrl=request.resource_url(context, 'xhr_list_domains')
            )
        ))
        self.DD['domain_name'] = copy.deepcopy(
            DomainDd['name'])
        self.DD['domain_name']['colModel']['editable'] = False
        self.DD['domain_name']['title'] = 'Domain'

        # If the fieldnames are fully qualified, this is the prefix, e.g.
        # ``myschema.mytable.``. Mind the trailing dot!
        self.PREFIX = ''
        self.PREFIXLEN = len(self.PREFIX)
        self.ID_FIELD = 'id'
        self.BROWSE_FIELDLIST = [
            'is_enabled',
            'id',
            'name',
            'domain_id',
            'domain_name',
            'dest',
            'mtime',
            'editor',
            'editor_display_name',
            'ctime',
            'owner',
            'owner_display_name'
        ]
        self.ADD_FIELDLIST = [
            'name',
            'domain_id',
            'dest'
        ]
        self.EDIT_FIELDLIST = [
            'name',
            'domain_id',
            'dest'
        ]

    @view_config(
        name='',
        renderer='pysite:vmailmgr/templates/alias/index.mako',
    )
    def index(self):
        gr = Grid(self.GRID_ID)
        gr.url = self.request.resource_url(self.context, 'xhr_browse')
        gr.add_opts['url'] = self.request.resource_url(self.context,
            "xhr_add")
        gr.edit_opts['url'] = self.request.resource_url(self.context,
            "xhr_edit")
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
        name='xhr_list_domains',
        renderer='string',
    )
    def xhr_list_domains(self):
        sess = DbSession()
        qry = sess.query(Domain.id, Domain.name).order_by(
            Domain.name)
        opts = "\n".join(['<option value="{0}">{1}</option>'.format(
            markupsafe.escape(x[0]), markupsafe.escape(x[1])) for x in qry])
        return "<select>\n" + opts + "\n</select>"

    @view_config(
        name='xhr_add',
        renderer='json',
    )
    def xhr_add(self):
        sess = DbSession()
        sch = pysite.dd.build_schema(colander.MappingSchema, self.DD,
            fieldlist=self.ADD_FIELDLIST)
        try:
            data = pysite.dd.deserialize(sch, self.request.POST)
        except colander.Invalid as exc:
            return {'status': False, 'msg': 'Errors', 'errors': exc.asdict()}
        try:
            ent = self.ENTITY()
            for k, v in data.items():
                setattr(ent, k[self.PREFIXLEN:], v)
            ent.owner = self.request.user.uid
            sess.add(ent)
            sess.flush()
            return {'status': True, 'msg': 'Ok'}
        except (StatementError, NoResultFound) as exc:
            return {'status': False, 'msg': repr(exc), 'errors': {}}

    @view_config(
        name='xhr_edit',
        renderer='json',
    )
    def xhr_edit(self):
        sess = DbSession()
        sch = pysite.dd.build_schema(colander.MappingSchema, self.DD,
            fieldlist=self.EDIT_FIELDLIST)
        try:
            data = pysite.dd.deserialize(sch, self.request.POST)
        except colander.Invalid as exc:
            return {'status': False, 'msg': 'Errors', 'errors': exc.asdict()}
        try:
            id = int(self.request.POST['id'])
            vv = {}
            for k, v in data.items():
                vv[k[self.PREFIXLEN:]] = v
            vv['editor'] = self.request.user.uid
            vv['mtime'] = datetime.datetime.now()
            sess.query(self.ENTITY).filter(self.ENTITY.id == id).update(
                vv, synchronize_session=False)
            sess.flush()
            return {'status': True, 'msg': 'Ok'}
        except (StatementError, NoResultFound) as exc:
            return {'status': False, 'msg': repr(exc), 'errors': {}}

    @view_config(
        name='xhr_delete',
        renderer='json',
    )
    def xhr_delete(self):
        sess = DbSession()
        try:
            id = int(self.request.POST['id'])
            sess.query(self.ENTITY).filter(self.ENTITY.id == id).delete(
                synchronize_session=False)
            sess.flush()
            return {'status': True, 'msg': 'Ok'}
        except (StatementError, NoResultFound) as exc:
            return {'status': False, 'msg': repr(exc), 'errors': {}}
