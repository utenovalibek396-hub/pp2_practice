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

def create_table():
    execute_query("""
    CREATE TABLE IF NOT EXISTS contacts (
        username VARCHAR(100) PRIMARY KEY,
        phone VARCHAR(20)
    );
    """)

def execute_query(query, params=None):
    conn = connect()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
    except Exception as e:
        print("Query қатесі:", e)
    finally:
        conn.close()

def fetch_data(query, params=None):
    conn = connect()
    if conn is None:
        return []
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as e:
        print("Fetch қатесі:", e)
        return []
    finally:
        conn.close()

def insert_from_csv(filename='contacts.csv'):
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row.get('username')
                phone = row.get('phone')
                if username and phone:
                    execute_query(
                        "INSERT INTO contacts (username, phone) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING;",
                        (username, phone)
                    )
    except Exception as e:
        print("CSV қатесі:", e)

def insert_from_console():
    username = input("Name: ")
    phone = input("Phone: ")
    if username and phone:
        execute_query(
            "INSERT INTO contacts (username, phone) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING;",
            (username, phone)
        )

def update_contact():
    choice = input("1 - Username, 2 - Phone: ")
    if choice == '1':
        old_un = input("Old name: ")
        new_un = input("New name: ")
        execute_query("UPDATE contacts SET username = %s WHERE username = %s;", (new_un, old_un))
    elif choice == '2':
        un = input("Name: ")
        new_ph = input("New phone: ")
        execute_query("UPDATE contacts SET phone = %s WHERE username = %s;", (new_ph, un))

def query_contacts():
    choice = input("1 - All, 2 - By Name, 3 - By Prefix: ")
    if choice == '1':
        res = fetch_data("SELECT username, phone FROM contacts;")
    elif choice == '2':
        val = input("Name: ")
        res = fetch_data("SELECT username, phone FROM contacts WHERE username LIKE %s;", (f"%{val}%",))
    elif choice == '3':
        val = input("Prefix: ")
        res = fetch_data("SELECT username, phone FROM contacts WHERE phone LIKE %s;", (f"{val}%",))
    else:
        return

    if res:
        for r in res:
            print(f"{r[0]}: {r[1]}")
    else:
        print("Мәлімет табылмады")

def delete_contact():
    choice = input("1 - By Name, 2 - By Phone: ")
    if choice == '1':
        val = input("Name: ")
        execute_query("DELETE FROM contacts WHERE username = %s;", (val,))
    elif choice == '2':
        val = input("Phone: ")
        execute_query("DELETE FROM contacts WHERE phone = %s;", (val,))

def main():
    create_table()
    while True:
        print("\n1. CSV Load | 2. Add | 3. Update | 4. Search | 5. Delete | 0. Exit")
        cmd = input("> ")
        if cmd == '1':
            insert_from_csv()
        elif cmd == '2':
            insert_from_console()
        elif cmd == '3':
            update_contact()
        elif cmd == '4':
            query_contacts()
        elif cmd == '5':
            delete_contact()
        elif cmd == '0':
            break

if __name__ == "__main__":
    main()