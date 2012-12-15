# -*- coding: utf-8 -*-

"""
This module contains helpers and mixins for data dictionaries.

Data dictionaries are Python dicts that define the structure of some data, the
type of their nodes, validation rules and arbitrary other aspects, like title,
widget, colModel for the grid.

Data dictionaries are based on Colander, which means that the type of a node is
given as a colander SchemaNode class. Ditto is the validator an instance of a
colander validator.

Each datadictionary has two special keys, whose value must be the same as in
their SQLAlchemy declarative counterparts: ``__tablename__`` and ``__schema__``
(which may be given in SA's table_args).

Typically, the keys of a data dictionary correspond to the column names. In
cases where it is necessary to have fully qualified column names, ``__schema__``
and ``__tablename__`` are used to build the prefix. Such a case is e.g. if 
you build a query that joins two or more entities. SA uses fully qualified
column names to avoid clashing if any tables have the same column names.
"""

import colander


def deserialize(schema, in_data0):
    """
    Deserializes given data with given schema and replaces ``Colander.null``
    with None.

    Use this when you want to transform data sent back from the grid into
    a Python data structure.

    Lets any errors bubble up to caller.
    """
    # In HTML ids cannot have `.', so Grid's form uses `-' in colModel `name'
    # We have to reverse this here!
    in_data = {}
    for k0, v in in_data0.items():
        k = k0.replace('-', '.')
        in_data[k] = v
    out_data = schema.deserialize(in_data)
    for k, v in out_data.items():
        if v == colander.null:
            out_data[k] = None
        try:
            if len(v) == 0:
                out_data[k] = None
        except TypeError:
            pass
    return out_data


def build_schema(schema_type, *dds, **kw):
    """
    Builds a Colander schema by given datadicts.

    If a field name starts with ``__`` (double underscore), it is left
    out in the schema.

    :param schema_type: A class of a colander schema
    :param *dds: List of dicts with data dictionaries.
    :param **kw: Additional keyword params. If ``fieldlist`` is given,
        only those fields are taken into the schema.
    :returns: Instance of the given colander schema.
    """
    sch = schema_type()
    for dd in dds:
        internals = {}
        for name, d in dd.items():
            if name.startswith('__'):
                internals[name] = d
        for name, x in dd.items():
            d = x.copy()
            if name.startswith('__'):
                continue
            if 'fieldlist' in kw and name not in kw['fieldlist']:
                continue
            d['name'] = name
            typ = d['type']
            del(d['type'])
            sch.add(colander.SchemaNode(typ, **d))
    return sch


def apply_mixin(dd, *mixins):
    """
    Inserts mixins into given data dictionary.

    The data dictionary is modified in-place, so there is no return value.

    Determines automatically whether the column names of the data dictionary
    are fully qualified, i.e. start with schema or table name, or not. The
    mixed-in keys are prefixed likewise.

    :param dd: The data dictionary
    :param *mixins: One or more mixins
    """
    # If dd has fully qualified column names, we need to prefix
    # the mixed-in keys likewise.
    k = next(iter(dd.keys()))
    if dd['__schema__'] and k.startswith(dd['__schema__']):
        prefix = dd['__schema__'] + '.' + dd['__tablename__'] + '.'
    elif k.startswith(dd['__tablename__']):
        prefix = dd['__tablename__'] + '.'
    else:
         prefix = ''
    for m in mixins:
        for k, v in m.items():
            dd[prefix + k] = v


###def apply_mixin(dd, prefix, *mixins):
###    """
###    Puts given mixins into given dd with given prefix.
###
###    Modifies ``dd`` in-place, so nothing is returned.
###
###    A ``dd`` is a Python dict whose keys denote the column names. You may
###    have set fully qualified column names, e.g. ``principal.display_name``
###    instead of ``display_name``. Since a mixin is 'table-less' so to speak,
###    you must prefix its keys with the name of the target table.
###
###    :param dd: Dict with data dictionary.
###    :param prefix: String to prefix the keys (field names) of the mixins with.
###    :param *mixins: One or more dicts with data dictionaries to mix in.
###    """
###    if not prefix.endswith('_') and not prefix.endswith('.'):
###        prefix = prefix + '.'
###    for mixin in mixins:
###        for k, v in mixin.items():
###            dd[prefix + k] = v


def list_titles(dd, fieldlist=None):
    """
    Returns list of titles of given datadict.

    Fields with names starting with ``__`` (double under) are left out.

    :param dd: The data dictionary, either a dict or a class or instance of
        :class:`colander.SchemaNode`.
    :param fieldlist: Optional. Tuple with wanted fields.
    :returns: List of titles
    :raises TypeError: If ``dd`` is neither a dict nor instance or class of
        :class:`colander.SchemaNode`.
    """
    tt = []
    if isinstance(dd, colander.SchemaNode):
        try:
            # dd is an instance
            items = dd.children
        except AttributeError:
            # dd is a class
            items = dd.nodes
        for it in items:
            if it.name.startswith('__'):
                continue
            if (fieldlist and it.name in fieldlist) \
                    or not fieldlist:
                tt.append(it.title)
    elif isinstance(dd, dict):
        if fieldlist is None:
            fieldlist = dd.keys()
        for f in fieldlist:
            if f.startswith('__'):
                continue
            tt.append(dd[f]['title'])
    else:
        raise TypeError("Argument 'dd' must be dict or colander.SchemaNode")
    return tt
