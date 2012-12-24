CREATE VIEW vw_vmail_alias_browse AS
(
    SELECT vmail_alias.is_enabled              AS is_enabled,
           vmail_alias.id                      AS id,
           vmail_alias.domain_id               AS domain_id,
           domain.name                         AS domain_name,
           vmail_alias.name                    AS name,
           vmail_alias.dest                    AS dest,
           vmail_alias.mtime                   AS mtime,
           vmail_alias.editor                  AS editor,
           e.display_name                      AS editor_display_name,
           vmail_alias.ctime                   AS ctime,
           vmail_alias.owner                   AS owner,
           o.display_name                      AS owner_display_name
    FROM vmail_alias
    JOIN vmail_domain AS domain ON vmail_alias.domain_id = domain.id
    LEFT OUTER JOIN principal AS o ON vmail_alias.owner = o.id
    LEFT OUTER JOIN principal AS e ON vmail_alias.editor = e.id
);
