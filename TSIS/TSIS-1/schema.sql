-- ============================================================
-- setting up the tables for the extended phonebook (TSIS 1)
-- run this once to create everything or upgrade the old tables

-- Create a table to store contact categories like 'Family' or 'Work'
CREATE TABLE IF NOT EXISTS groups (
    -- Auto-incrementing unique identifier for each group
    id   SERIAL PRIMARY KEY,
    -- Unique name for the group, maximum 50 characters, cannot be empty
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed the groups table with default categories
-- add some basic groups to start with
INSERT INTO groups (name) VALUES
    ('Family'), ('Work'), ('Friend'), ('Other')
-- If the group name already exists, skip the insertion to avoid errors
ON CONFLICT (name) DO NOTHING;

-- Create the main table to store personal information for contacts
-- main table for people
CREATE TABLE IF NOT EXISTS contacts (
    -- Auto-incrementing unique identifier for each contact
    id         SERIAL PRIMARY KEY,
    -- Contact's first name, required field
    first_name VARCHAR(50)  NOT NULL,
    -- Contact's last name, optional field
    last_name  VARCHAR(50),
    -- Contact's email address, optional field
    email      VARCHAR(100),
    -- Contact's date of birth
    birthday   DATE,
    -- Foreign key linking the contact to a specific group ID
    group_id   INTEGER REFERENCES groups(id),
    -- Timestamp of when the contact was created, defaults to current time
    created_at TIMESTAMP DEFAULT NOW()
);

-- Anonymous block to handle schema updates without losing existing data
-- if the table already exists, just add the new columns so we don't lose old data
DO $$
BEGIN
    -- Check if the 'email' column exists in the 'contacts' table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'contacts' AND column_name = 'email'
    ) THEN
        -- Add the 'email' column if it is missing
        ALTER TABLE contacts ADD COLUMN email VARCHAR(100);
    END IF;

    -- Check if the 'birthday' column exists in the 'contacts' table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'contacts' AND column_name = 'birthday'
    ) THEN
        -- Add the 'birthday' column if it is missing
        ALTER TABLE contacts ADD COLUMN birthday DATE;
    END IF;

    -- Check if the 'group_id' column exists in the 'contacts' table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'contacts' AND column_name = 'group_id'
    ) THEN
        -- Add the 'group_id' column with a reference to the 'groups' table
        ALTER TABLE contacts ADD COLUMN group_id INTEGER REFERENCES groups(id);
    END IF;
END
$$;

-- Create a table for storing multiple phone numbers per contact
-- table for phone numbers. one person can have many phones
CREATE TABLE IF NOT EXISTS phones (
    -- Auto-incrementing unique identifier for each phone record
    id         SERIAL PRIMARY KEY,
    -- Reference to the contact, deletes phone if the contact is removed
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    -- The actual phone number string
    phone      VARCHAR(20) NOT NULL,
    -- Category of the phone, restricted to 'home', 'work', or 'mobile'
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);