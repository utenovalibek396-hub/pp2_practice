CREATE OR REPLACE PROCEDURE insert_or_update_user(p_name TEXT, p_phone TEXT)
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE username = p_name) THEN
        UPDATE contacts SET phone = p_phone WHERE username = p_name;
    ELSE
        INSERT INTO contacts(username, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE insert_many_users(p_names TEXT[], p_phones TEXT[])
AS $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 1 .. array_upper(p_names, 1) LOOP
        IF p_phones[i] SIMILAR TO '\+7[0-9]{10}' THEN
            CALL insert_or_update_user(p_names[i], p_phones[i]);
        ELSE
            RAISE NOTICE 'Invalid data: %', p_phones[i];
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE delete_user(val TEXT)
AS $$
BEGIN
    DELETE FROM contacts
    WHERE username = val OR phone = val;
END;
$$ LANGUAGE plpgsql;