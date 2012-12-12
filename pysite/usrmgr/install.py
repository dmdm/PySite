
import pysite.models
from pysite.usrmgr.models import (
    Principal,
    Role,
    RoleMember
)
from pysite.usrmgr.const import *


def setup_users(rc):
    sess = pysite.models.DbSession()
    # Principal 'system'
    # Need to create this principal first to have an owner for following entities
    p = Principal(principal='system',email='system@localhost')
    p.id = SYSTEM_UID
    p.first_name = 'system'
    p.display_name = 'System'
    p.owner = SYSTEM_UID
    sess.add(p)
    sess.flush()

    # Create roles

    r = Role(name='system')
    r.id = SYSTEM_RID
    r.notes = 'System'
    r.owner = SYSTEM_UID
    sess.add(r)

    r_wheel = Role(name='wheel')
    r_wheel.id = WHEEL_RID
    r_wheel.notes = 'Site Admins'
    r_wheel.owner = SYSTEM_UID
    sess.add(r_wheel)

    r_users = Role(name='users')
    r_users.id = USERS_RID
    r_users.notes = 'Authenticated Users'
    r_users.owner = SYSTEM_UID
    sess.add(r_users)

    r_unit_testers = Role(name='unit testers')
    r_unit_testers.id = UNIT_TESTERS_RID
    r_unit_testers.notes = 'Unit testers'
    r_unit_testers.owner = SYSTEM_UID
    sess.add(r_unit_testers)

    # This role should not have members.
    # Not-authenticated users are automatically member of 'everyone'
    r = Role(name='everyone')
    r.id = EVERYONE_RID
    r.notes = 'Everyone (including unauthenticated users)'
    r.owner = SYSTEM_UID
    sess.add(r)
    
    sess.flush() # Needed to set ids of above objects

    # Put 'system' into its roles
    e = RoleMember(role_id=r_users.id, principal_id=p.id)
    e.owner = SYSTEM_UID
    sess.add(e)
    e = RoleMember(role_id=r_wheel.id, principal_id=p.id)
    e.owner = SYSTEM_UID
    sess.add(e)
    sess.flush()
    
    # Principal 'root'
    p = Principal(principal='root',email='root@localhost')
    p.id = ROOT_UID
    p.first_name = 'root'
    p.display_name = 'Root'
    p.pwd = rc.data['auth.user_root.pwd']
    p.is_enabled = True
    p.owner = SYSTEM_UID
    sess.add(p)
    sess.flush()
    e = RoleMember(role_id=r_users.id, principal_id=p.id)
    e.owner = SYSTEM_UID
    sess.add(e)
    e = RoleMember(role_id=r_wheel.id, principal_id=p.id)
    e.owner = SYSTEM_UID
    sess.add(e)
    sess.flush()
    
    # Principal 'sample_data'
    # This principal is not member of any role
    p = Principal(principal='sample_data',email='sample_data@localhost')
    p.id = SAMPLE_DATA_UID
    p.first_name = 'Sample Data'
    p.display_name = 'Sample Data'
    p.owner = SYSTEM_UID
    sess.add(p)
    sess.flush()
    
    # Principal 'unit_tester'
    p = Principal(principal='unit_tester',email='unit_tester@localhost')
    p.id = UNIT_TESTER_UID
    p.first_name = 'Unit-Tester'
    p.display_name = 'Unit-Tester'
    p.owner = SYSTEM_UID
    sess.add(p)
    sess.flush()
    e = RoleMember(role_id=r_unit_testers.id, principal_id=p.id)
    e.owner = SYSTEM_UID
    sess.add(e)
    sess.flush()
    
    # Principal 'nobody'
    # This principal is not member of any roles
    # Not-authenticated users are automatically 'nobody'
    p = Principal(principal='nobody',email='nobody@localhost')
    p.id = NOBODY_UID
    p.first_name = 'Nobody'
    p.display_name = 'Nobody'
    p.owner = SYSTEM_UID
    sess.add(p)
    sess.flush()

    # XXX PostgreSQL only
    # Regular users have ID > 100
    sess.execute('ALTER SEQUENCE principal_id_seq RESTART WITH 101')
    # Regular roles have ID > 100
    sess.execute('ALTER SEQUENCE role_id_seq RESTART WITH 101')
    sess.flush()
   
###     # Principal 'Foo' for testing
###     p = Principal(principal='foo',email='foo@localhost')
###     p.first_name = 'Foo'
###     p.last_name = 'Bar'
###     p.display_name = 'Foo Bar'
###     p.owner = SYSTEM_UID
###     e = RoleMember(role_id=r_users.id)
###     e.owner = SYSTEM_UID
###     p.role_members.append(e)
###     sess.add(p)
###     sess.flush()
### #    e = RoleMember(role_id=r_users.id, principal_id=p.id)
### #    e.owner = SYSTEM_UID
### #    sess.add(e)
### #    sess.flush()

