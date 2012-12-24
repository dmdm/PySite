CREATE VIEW vw_vmail_domain_browse AS
(
    SELECT vmail_domain.is_enabled               AS is_enabled,
           vmail_domain.id                       AS id,
           vmail_domain.name                     AS name,
           vmail_domain.tenant_id                AS tenant_id,
           tenant.display_name                   AS tenant_display_name,
           coalesce(mailboxes.used, 0)           AS used_mailboxes,
           vmail_domain.max_mailboxes            AS max_mailboxes,
           coalesce(aliases.used, 0)             AS used_aliases,
           vmail_domain.max_aliases              AS max_aliases,
           vmail_domain.quota                    AS quota,
           vmail_domain.mtime                    AS mtime,
           vmail_domain.editor                   AS editor,
           e.display_name                        AS editor_display_name,
           vmail_domain.ctime                    AS ctime,
           vmail_domain.owner                    AS owner,
           o.display_name                        AS owner_display_name
    FROM vmail_domain
    JOIN principal AS tenant ON vmail_domain.tenant_id = tenant.id
    LEFT OUTER JOIN
      (SELECT vmail_mailbox.domain_id AS domain_id,
              count(*) AS used
       FROM vmail_mailbox
       GROUP BY vmail_mailbox.domain_id) AS mailboxes ON mailboxes.domain_id = vmail_domain.id
    LEFT OUTER JOIN
      (SELECT vmail_alias.domain_id AS domain_id,
              count(*) AS used
       FROM vmail_alias
       GROUP BY vmail_alias.domain_id) AS aliases ON aliases.domain_id = vmail_domain.id
    LEFT OUTER JOIN principal AS o ON vmail_domain.owner = o.id
    LEFT OUTER JOIN principal AS e ON vmail_domain.editor = e.id
);
