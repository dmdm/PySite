# -*- coding: utf-8 -*-
import colander

class DomainDd(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.Str(),
        validator=colander.Length(max=100)
    )
    max_mailboxes = colander.SchemaNode(
        colander.Int(),
        validator=colander.Length(min=-1)
    )
    max_aliases = colander.SchemaNode(
        colander.Int(),
        validator=colander.Length(min=-1)
    )
    quota = colander.SchemaNode(
        colander.Int(),
        validator=colander.Length(min=0)
    )
    is_enabled = colander.SchemaNode(
        colander.Bool(),
        validator=colander.Length(min=0)
    )
    foo = colander.SchemaNode(
        colander.Bool(),
        validator=colander.Length(min=0),
        some = dict(a=1, b=2, c=3)
    )

