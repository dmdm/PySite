CREATE VIEW vw_rolemember_browse AS
(
    SELECT rm.id                             AS id,
           principal.id                      AS principal_id,
           principal.principal               AS principal_principal,
           principal.is_enabled              AS principal_is_enabled,
           principal.is_blocked              AS principal_is_blocked,
           principal.email                   AS principal_email,
           principal.first_name              AS principal_first_name,
           principal.last_name               AS principal_last_name,
           principal.display_name            AS principal_display_name,
           principal.notes                   AS principal_notes,
           role.id                           AS role_id,
           role.name                         AS role_name,
           role.notes                        AS role_notes,
           rm.ctime                          AS ctime,
           rm.owner                          AS owner,
           o.display_name                    AS owner_display_name
    FROM rolemember rm
    -- Use outer joins to principal and role to see if we have 
    -- member records for non-existing principals or roles.
    LEFT OUTER JOIN principal      ON rm.principal_id = principal.id
    LEFT OUTER JOIN role           ON rm.role_id      = role.id
    LEFT OUTER JOIN principal AS o ON principal.owner = o.id
);
