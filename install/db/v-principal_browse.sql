CREATE VIEW vw_principal_browse AS
(
    SELECT principal.is_enabled              AS is_enabled,
           principal.is_blocked              AS is_blocked,
           principal.id                      AS id,
           principal.principal               AS principal,
           principal.pwd                     AS pwd,
           principal.identity_url            AS identity_url,
           principal.email                   AS email,
           principal.first_name              AS first_name,
           principal.last_name               AS last_name,
           principal.display_name            AS display_name,
           principal.login_time              AS login_time,
           principal.prev_login_time         AS prev_login_time,
           principal.gui_token               AS gui_token,
           principal.notes                   AS notes,
           principal.mtime                   AS mtime,
           principal.editor                  AS editor,
           e.display_name                    AS editor_display_name,
           principal.ctime                   AS ctime,
           principal.owner                   AS owner,
           o.display_name                    AS owner_display_name
    FROM principal
    LEFT OUTER JOIN principal AS o ON principal.owner = o.id
    LEFT OUTER JOIN principal AS e ON principal.editor = e.id
);
