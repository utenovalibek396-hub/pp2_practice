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

# ------------------- CREATE -------------------
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
        print("⚠️ Мәлімет жоқ")
        return

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["username", "phone"])
        writer.writeheader()
        for u, p in data:
            writer.writerow({"username": u, "phone": p})

    print("✅ CSV жаңартылды!")

# ------------------- FUNCTIONS -------------------
def insert_user():
    name = input("Name: ")
    phone = input("Phone: ")

    execute_query("CALL insert_or_update_user(%s, %s);", (name, phone))
    print("✅ Added/Updated")

def insert_many():
    names = [n.strip() for n in input("Names (comma): ").split(",")]
    phones = [p.strip() for p in input("Phones (comma): ").split(",")]

    if len(names) != len(phones):
        print("⚠️ Names пен Phones саны сәйкес емес!")
        return

    for name, phone in zip(names, phones):
        if not phone.startswith("+7"):
            print(f"⚠️ Қате номер: {phone}")
            continue
        execute_query("CALL insert_or_update_user(%s, %s);", (name, phone))

    print("✅ Done")

def search():
    pattern = input("Search: ").lower()

    # DB search
    db_res = fetch_data("SELECT * FROM search_pattern(%s);", (pattern,))

    # CSV search
    csv_res = []
    for row in read_csv():
        if pattern in row["username"].lower() or pattern in row["phone"]:
            csv_res.append((row["username"], row["phone"]))

    print("\n--- НӘТИЖЕ ---")

    if not db_res and not csv_res:
        print("Мәлімет табылмады")
        return

    print("\n[DB]:")
    for u, p in db_res:
        print(f"{u} -> {p}")

    print("\n[CSV]:")
    for u, p in csv_res:
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