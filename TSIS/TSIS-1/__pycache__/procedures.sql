-- Добавление телефона
CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
AS $$
BEGIN
    INSERT INTO phones (contact_id, phone, type)
    SELECT user_id, p_phone, p_type FROM phonebook 
    WHERE first_name = p_contact_name LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Смена группы
CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR, p_group_name VARCHAR)
AS $$
DECLARE
    v_group_id INT;
BEGIN
    INSERT INTO groups (name) VALUES (p_group_name) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    UPDATE phonebook SET group_id = v_group_id WHERE first_name = p_contact_name;
END;
$$ LANGUAGE plpgsql;

-- Расширенный поиск
CREATE OR REPLACE FUNCTION search_contacts_ext(p_query TEXT)
RETURNS TABLE(u_id INT, name VARCHAR, mail VARCHAR, phones_list TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pb.user_id, pb.first_name, pb.email,
        STRING_AGG(ph.phone || ' (' || ph.type || ')', ', ')
    FROM phonebook pb
    LEFT JOIN phones ph ON pb.user_id = ph.contact_id
    WHERE pb.first_name ILIKE '%' || p_query || '%' 
       OR pb.email ILIKE '%' || p_query || '%'
       OR ph.phone ILIKE '%' || p_query || '%'
    GROUP BY pb.user_id;
END;
$$ LANGUAGE plpgsql;