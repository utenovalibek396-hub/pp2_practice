import psycopg2
from psycopg2.extras import RealDictCursor
import json
import csv
import os
from config import params

def get_connection():
    return psycopg2.connect(**params)

def import_from_csv(filename="contacts_import.csv"):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (row['group'],))
                cur.execute("SELECT id FROM groups WHERE name = %s", (row['group'],))
                g_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO phonebook (first_name, email, birthday, group_id) 
                    VALUES (%s, %s, %s, %s) RETURNING user_id
                """, (row['first_name'], row.get('email'), row.get('birthday'), g_id))
                new_id = cur.fetchone()[0]

                cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                            (new_id, row['phone'], row.get('type', 'mobile')))
        conn.commit()
        print("CSV import successful.")
    except Exception as e:
        print(f"Error: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

def export_to_json(filename="contacts_export.json"):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT pb.first_name, pb.email, pb.birthday, g.name as group_name,
                   (SELECT json_agg(json_build_object('phone', ph.phone, 'type', ph.type)) 
                    FROM phones ph WHERE ph.contact_id = pb.user_id) as phones
            FROM phonebook pb
            LEFT JOIN groups g ON pb.group_id = g.id
        """
        cur.execute(query)
        data = cur.fetchall()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, default=str)
        print("Export successful.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()

def import_from_json(filename="contacts_import.json"):
    if not os.path.exists(filename):
        return
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        with open(filename, "r", encoding="utf-8") as f:
            contacts = json.load(f)
        
        for c in contacts:
            cur.execute("SELECT user_id FROM phonebook WHERE first_name = %s", (c['first_name'],))
            exists = cur.fetchone()
            if exists:
                ans = input(f"Contact {c['first_name']} exists. Overwrite (o) or skip (s)? ")
                if ans.lower() == 's': continue
                cur.execute("DELETE FROM phonebook WHERE user_id = %s", (exists[0],))

            cur.execute("""
                INSERT INTO phonebook (first_name, email, birthday) 
                VALUES (%s, %s, %s) RETURNING user_id
            """, (c['first_name'], c.get('email'), c.get('birthday')))
            new_id = cur.fetchone()[0]

            if 'phones' in c and c['phones']:
                for p in c['phones']:
                    cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                                (new_id, p['phone'], p['type']))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()

def view_contacts():
    limit = 5
    offset = 0
    sort_col = input("Sort by (name, birthday, date): ")
    sort_map = {"name": "first_name", "birthday": "birthday", "date": "created_at"}
    order_by = sort_map.get(sort_col, "first_name")
    group_filter = input("Filter by group (leave empty for all): ")
    
    conn = get_connection()
    cur = conn.cursor()
    while True:
        query = f"""
            SELECT pb.first_name, pb.email, g.name 
            FROM phonebook pb
            LEFT JOIN groups g ON pb.group_id = g.id
            WHERE (%s = '' OR g.name ILIKE %s)
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """
        cur.execute(query, (group_filter, f"%{group_filter}%", limit, offset))
        rows = cur.fetchall()
        
        for row in rows:
            print(f"Name: {row[0]} | Email: {row[1]} | Group: {row[2]}")
            
        cmd = input("[n]ext, [p]rev, [q]uit: ").lower()
        if cmd == 'n' and len(rows) == limit: offset += limit
        elif cmd == 'p' and offset >= limit: offset -= limit
        elif cmd == 'q': break
    conn.close()

def main_menu():
    while True:
        print("\nPHONEBOOK SYSTEM")
        print("1. Search")
        print("2. View Contacts")
        print("3. Export JSON")
        print("4. Import JSON")
        print("5. Import CSV")
        print("6. Add Phone (Procedure)")
        print("7. Change Group (Procedure)")
        print("0. Exit")
        
        choice = input("Select option: ")
        if choice == '1':
            q = input("Query: ")
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT * FROM search_contacts_ext(%s)", (q,))
            for r in cur.fetchall(): print(r)
            conn.close()
        elif choice == '2': view_contacts()
        elif choice == '3': export_to_json()
        elif choice == '4': import_from_json()
        elif choice == '5': import_from_csv()
        elif choice == '6':
            n = input("Name: "); p = input("Phone: "); t = input("Type: ")
            conn = get_connection(); cur = conn.cursor()
            cur.execute("CALL add_phone(%s, %s, %s)", (n, p, t))
            conn.commit(); conn.close()
        elif choice == '7':
            n = input("Name: "); g = input("Group: ")
            conn = get_connection(); cur = conn.cursor()
            cur.execute("CALL move_to_group(%s, %s)", (n, g))
            conn.commit(); conn.close()
        elif choice == '0': break

if __name__ == "__main__":
    main_menu()