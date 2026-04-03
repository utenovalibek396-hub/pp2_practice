import csv
import os
import psycopg2

CSV_FILE = "Practice-7/contacts.csv"

# ------------------- PostgreSQL -------------------
def connect():
    try:
        return psycopg2.connect(
            host="localhost",
            database="testdb",
            user="postgres",
            password="123456789qaz",
            sslmode="disable"
        )
    except Exception as e:
        print("Қосылу қатесі:", e)
        return None

def execute_query(query, params=None):
    conn = connect()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        print("Query қатесі:", e)
        return False
    finally:
        cur.close()
        conn.close()

def fetch_data(query, params=None):
    conn = connect()
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        return cur.fetchall()
    except Exception as e:
        print("Fetch қатесі:", e)
        return []
    finally:
        cur.close()
        conn.close()

# ------------------- CREATE ALL -------------------
def create_all():
    execute_query("""
        CREATE TABLE IF NOT EXISTS contacts (
            username VARCHAR(100) PRIMARY KEY,
            phone VARCHAR(20)
        );
    """)

    execute_query("""
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
    """)

    execute_query("""
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
    """)

    execute_query("""
    CREATE OR REPLACE PROCEDURE insert_many_users(names TEXT[], phones TEXT[])
    AS $$
    DECLARE
        i INT;
    BEGIN
        FOR i IN 1..array_length(names,1) LOOP
            IF phones[i] NOT LIKE '+7%' THEN
                RAISE NOTICE 'Қате номер: %', phones[i];
            ELSE
                INSERT INTO contacts(username, phone)
                VALUES (names[i], phones[i])
                ON CONFLICT (username) DO NOTHING;
            END IF;
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;
    """)

    execute_query("""
    CREATE OR REPLACE FUNCTION get_paginated(lim INT, off INT)
    RETURNS TABLE(username TEXT, phone TEXT)
    AS $$
    BEGIN
        RETURN QUERY
        SELECT c.username::TEXT, c.phone::TEXT
        FROM contacts c
        LIMIT lim OFFSET off;
    END;
    $$ LANGUAGE plpgsql;
    """)

    execute_query("""
    CREATE OR REPLACE PROCEDURE delete_user(val TEXT)
    AS $$
    BEGIN
        DELETE FROM contacts
        WHERE username = val OR phone = val;
    END;
    $$ LANGUAGE plpgsql;
    """)

# ------------------- CSV -------------------
def read_csv():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def export_to_csv():
    data = fetch_data("SELECT username, phone FROM contacts;")

    if not data:
        print("⚠️ Экспорт жасайтын мәлімет жоқ")
        return

    existing = read_csv()

    new_data = []
    for u, p in data:
        if all(not (c["username"] == u and c["phone"] == p) for c in existing):
            new_data.append({"username": u, "phone": p})

    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["username", "phone"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerows(new_data)

    print("✅ CSV-ға экспорт жасалды!")

# ------------------- FUNCTIONS -------------------
def insert_user():
    name = input("Name: ")
    phone = input("Phone: ")

    execute_query("CALL insert_or_update_user(%s, %s);", (name, phone))
    print("✅ Added/Updated")

def insert_many():
    names = input("Names (comma): ").split(",")
    phones = input("Phones (comma): ").split(",")

    execute_query("CALL insert_many_users(%s, %s);", (names, phones))
    print("✅ Done")

def search():
    pattern = input("Search: ")
    res = fetch_data("SELECT * FROM search_pattern(%s);", (pattern,))

    print("\n--- НӘТИЖЕ ---")
    if not res:
        print("Мәлімет табылмады")
    else:
        for u, p in res:
            print(f"{u} -> {p}")

def pagination():
    limit = int(input("Limit: "))
    offset = int(input("Offset: "))

    res = fetch_data("SELECT * FROM get_paginated(%s, %s);", (limit, offset))

    print("\n--- PAGE ---")
    for u, p in res:
        print(f"{u} -> {p}")

def delete():
    val = input("Name or phone: ")
    execute_query("CALL delete_user(%s);", (val,))
    print("🗑 Deleted")

# ------------------- MAIN -------------------
def main():
    create_all()

    while True:
        print("\n--- MENU ---")
        print("1.Add/Update  2.Search  3.Insert Many")
        print("4.Pagination  5.Delete  6.Export CSV  0.Exit")

        cmd = input("> ")

        if cmd == '1':
            insert_user()
        elif cmd == '2':
            search()
        elif cmd == '3':
            insert_many()
        elif cmd == '4':
            pagination()
        elif cmd == '5':
            delete()
        elif cmd == '6':
            export_to_csv()
        elif cmd == '0':
            break
        else:
            print("❌ Қате команда")

if __name__ == "__main__":
    main()