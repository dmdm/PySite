# -*- coding: utf-8 -*-

import sys
import yaml
from collections import OrderedDict
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )
import json
import os
from prettytable import PrettyTable

from pysite.rc import Rc
import pysite.models


# Init YAML to dump an OrderedDict like a regular dict, i.e.
# without creating a specific object tag.
def _represent_ordereddict(self, data):
    return self.represent_mapping('tag:yaml.org,2002:map', data.items())

yaml.add_representer(OrderedDict, _represent_ordereddict)


class Cli(object):

    def __init__(self):
        self.dump_opts_json = dict(
            sort_keys=False,
            indent=4,
            ensure_ascii=False
        )
        self.dump_opts_yaml = dict(
            allow_unicode=True,
            default_flow_style=False
        )

    def init_app(self, args):
        """
        Initialises Pyramid application.

        Loads config settings. Initialises SQLAlchemy.
        """
        self._args = args
        setup_logging(self._args.config)
        settings = get_appsettings(self._args.config)

        if 'environment' not in settings:
            raise KeyError('Missing key "environment" in config. Specify '
                'environment in paster INI file.')
        # The directory of the config file is our root_dir
        rc = Rc(environment=settings['environment'],
            root_dir=os.path.normpath(
                os.path.join(os.getcwd(), os.path.dirname(
                    self._args.config))
            )
        )
        rc.load()
        settings.update(rc.data)
        settings['rc'] = rc

        pysite.models.init(settings, 'db.pysite.sa.')

        self._rc = rc
        self._settings = settings

        pysite._init_vmail(rc)

    def _db_data_to_list(self, rs, fkmaps=None):
        """
        Transmogrifies db data into list including relationships.

        We use :func:`~.pysite.models.todict` to turn an entity into a dict,
        which will only catch regular field, not foreign keys (relationships).
        Parameter ``fkmaps`` is a dict that maps relationship names to
        functions.  The function must have one input parameter which obtains a
        reference to the processed foreign entity. The function then returns
        the computed value.

        E.g.::

            class Principal(DbBase):
                roles = relationship(Role)

        If accessed, member ``roles`` is a list of associated roles. For each
        role the mapped function is called and the current role given::

            for attr, func in fkmaps.items():
                r[attr] = [func(it) for it in getattr(obj, attr)]

        And the function is defined like this::

            fkmaps=dict(roles=lambda it: it.name)

        :param rs: Db resultset, like a list of entities
        :param fkmaps: Dict with foreign key mappings
        """
        rr = []
        for obj in rs:
            it = pysite.models.todict(obj)
            r = OrderedDict()
            r['id'] = it['id']
            for k in sorted(it.keys()):
                if k in ['id', 'owner', 'ctime', 'editor', 'mtime']:
                    continue
                r[k] = it[k]
            for k in ['owner', 'ctime', 'editor', 'mtime']:
                try:
                    r[k] = it[k]
                except KeyError:
                    pass
            if fkmaps:
                for attr, func in fkmaps.items():
                    r[attr] = [func(it) for it in getattr(obj, attr)]
            rr.append(r)
        return rr

    def _print(self, data):
        fmt = self._args.format.lower()
        if fmt == 'json':
            self._print_json(data)
        elif fmt == 'tsv':
            self._print_tsv(data)
        elif fmt == 'txt':
            self._print_txt(data)
        else:
            self._print_yaml(data)

    def _print_json(self, data):
        print(json.dumps(data, **self.dump_opts_json))

    def _print_tsv(self, data):
        try:
            hh = data[0].keys()
            print("\t".join(hh))
        except KeyError:  # missing data[0]
            # Data was not a list, maybe a dict
            hh = data.keys()
            print("\t".join(hh))
            print("\t".join([str(v) for v in data.values()]))
        except AttributeError:  # missing data.keys()
            # Data is just a list
            print("\t".join(data))
        else:
            # Data is list of dicts (like resultset from DB)
            for row in data:
                print("\t".join([str(v) for v in row.values()]))

    def _print_txt(self, data):
        # We need a list of hh for prettytable, otherwise we get
        # TypeError: 'KeysView' object does not support indexing
        try:
            hh = data[0].keys()
        except KeyError:  # missing data[0]
            # Data was not a list, maybe a dict
            hh = data.keys()
            t = PrettyTable(list(hh))
            t.align = 'l'
            t.add_row([data[h] for h in hh])
            print(t)
        except AttributeError:  # missing data.keys()
            # Just a simple list
            # PrettyTable *must* have column headers and the headers *must*
            # be str, not int or else!
            t = PrettyTable([ str(i) for i in range(len(data))])
            t.align = 'l'
            t.add_row(data)
            print(t)
        else:
            # Data is list of dicts (like resultset from DB)
            t = PrettyTable(list(hh))
            t.align = 'l'
            for row in data:
                t.add_row([row[h] for h in hh])
            print(t)

    def _print_yaml(self, data):
        yaml.dump(data, sys.stdout, **self.dump_opts_yaml)

    def _parse(self, data):
        fmt = self._args.format.lower()
        if fmt == 'json':
            return self._parse_json(data)
        if fmt == 'tsv':
            return self._parse_tsv(data)
        if fmt == 'txt':
            raise NotImplementedError("Reading data from pretty ASCII tables"
                "is not implemented")
        else:
            return self._parse_yaml(data)

    def _parse_json(self, data):
        return json.loads(data)

    def _parse_tsv(self, data):
        data = []
        for row in "\n".split(data):
            data.append([x.strip() for x in "\t".split(row)])
        return data

    def _parse_yaml(self, data):
        return yaml.load(data)

    def _build_query(self, entity):
        sess = pysite.models.DbSession()
        qry = sess.query(entity)
        if self._args.idlist:
            qry = qry.filter(entity.id.in_(self._args.idlist))
        else:
            if self._args.filter:
                qry = qry.filter(self._args.filter)
        if self._args.order:
            qry = qry.order_by(self._args.order)
        return qry
