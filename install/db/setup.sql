BEGIN;



-- ### \i v-vmail_domain_browse.sql
-- ### \i v-vmail_mailbox_browse.sql
-- ### \i v-vmail_alias_browse.sql
-- ### \i v-principal_browse.sql
-- ### \i v-role_browse.sql
DROP VIEW vw_rolemember_browse;
\i v-rolemember_browse.sql







SELECT 'If erronneous, rollback.' AS "Ready";
