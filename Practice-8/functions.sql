CREATE OR REPLACE FUNCTION search_pattern(pattern TEXT)
RETURNS TABLE(username TEXT, phone TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.username::TEXT, c.phone::TEXT
    FROM contacts c
    WHERE c.username ILIKE '%' || pattern || '%'
       OR c.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_paginated(lim INT, off INT)
RETURNS TABLE(username TEXT, phone TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.username::TEXT, c.phone::TEXT
    FROM contacts c
    ORDER BY username
    LIMIT lim OFFSET off;
END;
$$ LANGUAGE plpgsql;