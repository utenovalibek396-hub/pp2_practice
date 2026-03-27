import psycopg2
import csv

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

def create_table():
    execute_query("""
    CREATE TABLE IF NOT EXISTS contacts (
        username VARCHAR(100) PRIMARY KEY,
        phone VARCHAR(20)
    );
    """)

def insert_from_console():
    username = input("Name: ")
    phone = input("Phone: ")

    ok = execute_query(
        "INSERT INTO contacts (username, phone) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING;",
        (username, phone)
    )

    if ok:
        print("✅ Қосылды!")

def update_contact():
    choice = input("1 - Username, 2 - Phone: ")

    if choice == '1':
        old_un = input("Old name: ")
        new_un = input("New name: ")

        ok = execute_query(
            "UPDATE contacts SET username = %s WHERE username = %s;",
            (new_un, old_un)
        )

        if ok:
            print("✅ Аты жаңартылды!")

    elif choice == '2':
        un = input("Name: ")
        new_ph = input("New phone: ")

        ok = execute_query(
            "UPDATE contacts SET phone = %s WHERE username = %s;",
            (new_ph, un)
        )

        if ok:
            print("✅ Телефон жаңартылды!")

def query_contacts():
    print("\n--- SEARCH MENU ---")
    print("1. All | 2. By Name | 3. By Prefix")
    choice = input("> ")

    if choice == '1':
        res = fetch_data("SELECT username, phone FROM contacts;")
    elif choice == '2':
        val = input("Name: ")
        res = fetch_data(
            "SELECT username, phone FROM contacts WHERE username ILIKE %s;",
            (f"%{val}%",)
        )
    elif choice == '3':
        val = input("Prefix: ")
        res = fetch_data(
            "SELECT username, phone FROM contacts WHERE phone LIKE %s;",
            (f"{val}%",)
        )
    else:
        print("❌ Қате таңдау")
        return

    print("\n--- НӘТИЖЕ ---")
    if not res:
        print("Мәлімет табылмады")
    else:
        for u, p in res:
            print(f"{u} -> {p}")

def delete_contact():
    choice = input("1 - By Name, 2 - By Phone: ")

    if choice == '1':
        val = input("Name: ")
        ok = execute_query(
            "DELETE FROM contacts WHERE username = %s;",
            (val,)
        )
        if ok:
            print("🗑 Өшірілді!")

    elif choice == '2':
        val = input("Phone: ")
        ok = execute_query(
            "DELETE FROM contacts WHERE phone = %s;",
            (val,)
        )
        if ok:
            print("🗑 Өшірілді!")

def main():
    create_table()

    while True:
        print("\n--- MAIN MENU ---")
        print("1. Add | 2. Update | 3. Search | 4. Delete | 0. Exit")
        cmd = input("> ")

        if cmd == '1':
            insert_from_console()
        elif cmd == '2':
            update_contact()
        elif cmd == '3':
            query_contacts()
        elif cmd == '4':
            delete_contact()
        elif cmd == '0':
            break
        else:
            print("❌ Қате команда")

if __name__ == "__main__":
    main()