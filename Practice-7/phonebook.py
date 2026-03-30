import csv
import os
import psycopg2

CSV_FILE = "contacts.csv"

memory_contacts = []

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

def create_table():
    execute_query("""
        CREATE TABLE IF NOT EXISTS contacts (
            username VARCHAR(100) PRIMARY KEY,
            phone VARCHAR(20)
        );
    """)

# ------------------- CSV -------------------
def read_csv():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def append_to_csv(new_data):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["username", "phone"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for c in new_data:
            writer.writerow(c)

# ------------------- Контакт операциялары -------------------
def insert_from_console():
    username = input("Name: ")
    phone = input("Phone: ")

    # PostgreSQL-ға жазамыз
    execute_query(
        "INSERT INTO contacts (username, phone) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING;",
        (username, phone)
    )

    # Тек memory-ге сақтаймыз
    memory_contacts.append({"username": username, "phone": phone})

    print("✅ Memory-ге сақталды (CSV-ға әлі жазылған жоқ)")

def export_to_csv():
    if not memory_contacts:
        print("⚠️ Export жасайтын мәлімет жоқ")
        return

    existing = read_csv()

    new_unique = []
    for m in memory_contacts:
        if all(not (c["username"] == m["username"] and c["phone"] == m["phone"]) for c in existing):
            new_unique.append(m)

    append_to_csv(new_unique)

    print("✅ CSV-ға қосылды!")

def update_contact():
    print("1 - Username, 2 - Phone")
    choice = input("> ")

    if choice == '1':
        old_un = input("Old name: ")
        new_un = input("New name: ")

        execute_query(
            "UPDATE contacts SET username = %s WHERE username = %s;",
            (new_un, old_un)
        )

        data = read_csv()
        for c in data:
            if c["username"] == old_un:
                c["username"] = new_un
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["username", "phone"])
            writer.writeheader()
            writer.writerows(data)

        print("✅ Жаңартылды!")

    elif choice == '2':
        un = input("Name: ")
        new_ph = input("New phone: ")

        execute_query(
            "UPDATE contacts SET phone = %s WHERE username = %s;",
            (new_ph, un)
        )

        data = read_csv()
        for c in data:
            if c["username"] == un:
                c["phone"] = new_ph

        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["username", "phone"])
            writer.writeheader()
            writer.writerows(data)

        print("✅ Жаңартылды!")

def query_contacts():
    res = fetch_data("SELECT username, phone FROM contacts;")

    data_csv = read_csv()
    for c in data_csv:
        if (c["username"], c["phone"]) not in res:
            res.append((c["username"], c["phone"]))

    print("\n--- НӘТИЖЕ ---")
    if not res:
        print("Мәлімет табылмады")
    else:
        for u, p in res:
            print(f"{u} -> {p}")

def delete_contact():
    val = input("Name: ")

    execute_query(
        "DELETE FROM contacts WHERE username = %s;",
        (val,)
    )

    data = read_csv()
    data = [c for c in data if c["username"] != val]

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["username", "phone"])
        writer.writeheader()
        writer.writerows(data)

    print("🗑 Өшірілді!")

# ------------------- MAIN -------------------
def main():
    create_table()
    while True:
        print("\n--- MAIN MENU ---")
        print("1. Add | 2. Update | 3. Search | 4. Delete | 5. Export to CSV | 0. Exit")
        cmd = input("> ")

        if cmd == '1':
            insert_from_console()
        elif cmd == '2':
            update_contact()
        elif cmd == '3':
            query_contacts()
        elif cmd == '4':
            delete_contact()
        elif cmd == '5':
            export_to_csv()
        elif cmd == '0':
            break
        else:
            print("❌ Қате команда")

if __name__ == "__main__":
    main()