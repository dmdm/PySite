
import colander
import copy
import os

import sqlalchemy as sa
import sqlalchemy.sql as sasql
from sqlalchemy.orm import aliased

from pysite.models import *
from pysite.vmailmgr.models import *
from pysite.authmgr.models import *
from pysite.dd import fully_qualify
from pysite.cli import Cli

class Args(object):
    config = os.path.normpath(
        os.path.join(
            os.path.dirname(__file__), '../../development.ini'
        )
    )

cli = Cli()
cli.init_app(Args())


sess = DbSession()

# Build query for data
sqry_cnt_mailboxes = aliased(
    sess.query(
        Mailbox.domain_id,
        sa.func.count('*').label('used')
    ).group_by(Mailbox.domain_id).subquery(),
    name="mailboxes"
)
sqry_cnt_aliases = aliased(
    sess.query(
        Alias.domain_id,
        sa.func.count('*').label('used')
    ).group_by(Alias.domain_id).subquery(),
    name="aliases"
)
tenant = aliased(Principal, name='tenant')
owner = aliased(Principal, name='owner')
editor = aliased(Principal, name='editor')
# Ordering and searching in directly mapped fields is regular. Ditto
# ordering in calculated columns, because ORDER BY works also with column
# aliases.
# To search in calculated columns however, we must provide special means,
# because WHERE cannot use aliases.
qry = sess.query(
        Domain.is_enabled,
        Domain.id,
        Domain.name,
        Domain.tenant_id,
        tenant.display_name,
        sa.func.coalesce(sqry_cnt_mailboxes.c.used, 0).label('used_mailboxes'),
        Domain.max_mailboxes,
        sa.func.coalesce(sqry_cnt_aliases.c.used, 0).label('used_aliases'),
        Domain.max_aliases,
        Domain.quota,
        Domain.mtime,
        Domain.editor,
        editor.display_name,
        Domain.ctime,
        Domain.owner,
        owner.display_name
    ) \
    .join(tenant, Domain.tenant_id==tenant.id) \
    .outerjoin(sqry_cnt_mailboxes, sqry_cnt_mailboxes.c.domain_id==Domain.id) \
    .outerjoin(sqry_cnt_aliases, sqry_cnt_aliases.c.domain_id==Domain.id) \
    .outerjoin(owner, Domain.owner==owner.id) \
    .outerjoin(editor, Domain.editor==editor.id)

