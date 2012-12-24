CREATE VIEW vw_vmail_mailbox_browse AS
(
    SELECT vmail_mailbox.is_enabled              AS is_enabled,
           vmail_mailbox.id                      AS id,
           vmail_mailbox.domain_id               AS domain_id,
           domain.name                           AS domain_name,
           vmail_mailbox.name                    AS name,
           vmail_mailbox.pwd                     AS pwd,
           vmail_mailbox.uid                     AS uid,
           vmail_mailbox.gid                     AS gid,
           vmail_mailbox.quota                   AS quota,
           vmail_mailbox.home_dir                AS home_dir,
           vmail_mailbox.mail_dir                AS mail_dir,
           vmail_mailbox.mtime                   AS mtime,
           vmail_mailbox.editor                  AS editor,
           e.display_name                        AS editor_display_name,
           vmail_mailbox.ctime                   AS ctime,
           vmail_mailbox.owner                   AS owner,
           o.display_name                        AS owner_display_name
    FROM vmail_mailbox
    JOIN vmail_domain AS domain ON vmail_mailbox.domain_id = domain.id
    LEFT OUTER JOIN principal AS o ON vmail_mailbox.owner = o.id
    LEFT OUTER JOIN principal AS e ON vmail_mailbox.editor = e.id
);
