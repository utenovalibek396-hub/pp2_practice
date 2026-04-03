CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM contacts
    WHERE username = p_value OR phone = p_value;
END;
$$;