-- ============================================================
-- procedures.sql  –  PL/pgSQL objects for TSIS 1
-- ============================================================

-- 1. add_phone
-- find the contact by name and add a new phone number to them

-- Define the procedure to add a phone number, replacing it if it already exists
CREATE OR REPLACE PROCEDURE add_phone(
    -- Parameter for the name of the contact
    p_contact_name VARCHAR,
    -- Parameter for the phone number string
    p_phone         VARCHAR,
    -- Parameter for the phone type, defaults to 'mobile' if not provided
    p_type         VARCHAR DEFAULT 'mobile'
)
-- Use PL/pgSQL as the procedural language
LANGUAGE plpgsql AS $$
-- Declare local variables for the procedure logic
DECLARE
    -- Variable to store the internal ID of the contact found
    v_contact_id INTEGER;
BEGIN
    -- Search for the contact ID using a case-insensitive match on full name or first name
    -- figure out the contact id by checking their first or full name
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE LOWER(first_name || COALESCE(' ' || last_name, '')) = LOWER(TRIM(p_contact_name))
       OR LOWER(first_name) = LOWER(TRIM(p_contact_name))
    LIMIT 1;

    -- If no contact is found with the provided name, stop and throw an error
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Check if the provided phone type matches the allowed categories
    -- make sure they gave a correct phone type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Must be home, work, or mobile.', p_type;
    END IF;

    -- Insert the new phone record into the phones table linked to the contact
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    -- Print a success notification message
    RAISE NOTICE 'Phone % (%) added to contact "%".', p_phone, p_type, p_contact_name;
END;
$$;


-- 2. move_to_group
-- move a contact to a group, and make the group if it's missing

-- Define the procedure to assign a contact to a group
CREATE OR REPLACE PROCEDURE move_to_group(
    -- Parameter for the name of the contact
    p_contact_name VARCHAR,
    -- Parameter for the name of the group
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    -- Local variable for the contact's ID
    v_contact_id INTEGER;
    -- Local variable for the group's ID
    v_group_id   INTEGER;
BEGIN
    -- Search for the contact ID using case-insensitive matching
    -- get the contact id first
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE LOWER(first_name || COALESCE(' ' || last_name, '')) = LOWER(TRIM(p_contact_name))
       OR LOWER(first_name) = LOWER(TRIM(p_contact_name))
    LIMIT 1;

    -- Error out if the contact does not exist
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Try to insert the group name; if it already exists, do nothing (prevent duplicates)
    -- insert group if it's not already in the db
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    -- Retrieve the ID of the group (whether just created or already existing)
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- Update the contact record to link it with the found/created group ID
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;

    -- Print a success notification message
    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;


-- 3. search_contacts
-- search across everything: name, email, phones

-- Define a function that returns a result set for contact searching
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
-- Define the structure of the table that will be returned
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    -- Create a search pattern with wildcards for partial string matching
    v_pattern TEXT := '%' || LOWER(TRIM(p_query)) || '%';
BEGIN
    -- Execute the query and return the result rows
    RETURN QUERY
    -- Select unique records to avoid duplicates if a contact has multiple phones
    SELECT DISTINCT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name AS group_name
    -- Primary table is contacts, joined with groups and phones for wide searching
    FROM contacts c
    LEFT JOIN groups g  ON g.id  = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE
        -- Match against first name, last name, email, or phone number
        LOWER(c.first_name)                               LIKE v_pattern
        OR LOWER(COALESCE(c.last_name,  ''))          LIKE v_pattern
        OR LOWER(COALESCE(c.email,      ''))          LIKE v_pattern
        OR LOWER(COALESCE(ph.phone,     ''))          LIKE v_pattern
    -- Sort the results alphabetically by first name
    ORDER BY c.first_name, c.last_name;
END;
$$;

-- Define a function to retrieve contacts with pagination support
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INTEGER, p_offset INTEGER)
-- Define the schema of the returned table to match the contacts table
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_id   INTEGER,
    created_at TIMESTAMP
) 
LANGUAGE plpgsql AS $$
BEGIN
    -- Return the result of a simple query with LIMIT and OFFSET
    RETURN QUERY
    SELECT * FROM contacts
    ORDER BY first_name, last_name
    -- Limits the number of rows returned
    LIMIT p_limit
    -- Skips the specified number of rows for paging
    OFFSET p_offset;
END;
$$;