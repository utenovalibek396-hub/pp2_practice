CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(username VARCHAR, phone VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.username, c.phone
    FROM contacts c
    ORDER BY c.username
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;