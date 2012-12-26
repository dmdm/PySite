CREATE VIEW vw_role_browse AS
(
    SELECT role.id                      AS id,
           role.name                    AS name,
           role.notes                   AS notes,
           role.mtime                   AS mtime,
           role.editor                  AS editor,
           e.display_name               AS editor_display_name,
           role.ctime                   AS ctime,
           role.owner                   AS owner,
           o.display_name               AS owner_display_name
    FROM role
    LEFT OUTER JOIN principal AS o ON role.owner = o.id
    LEFT OUTER JOIN principal AS e ON role.editor = e.id
);
