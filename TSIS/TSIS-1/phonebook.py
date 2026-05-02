"""
my main phonebook file for TSIS 1. # Docstring: module purpose
adding the new features on top of what we did in practice 7 and 8. # Docstring: context of project extension
"""

import csv # Import the built-in library for handling CSV file operations
import json # Import the built-in library for JSON data parsing and serialization
import os # Import the OS module to interact with the operating system (paths, files)
import sys # Import system-specific parameters and functions
from datetime import date, datetime # Import date and datetime classes for handling temporal data

import psycopg2 # Import the PostgreSQL adapter for Python to connect to databases
import psycopg2.extras # Import extra features like RealDictCursor for dictionary-like query results

from connect import get_connection # Import the custom helper function to establish a DB connection

# --- helper functions --- # Section for internal utility functions

def _conn(): # Define a private-style helper function to get a database connection
    return get_connection() # Return the connection object using the imported helper


def _fmt_date(d): # Define a function to format date objects for display
    return d.isoformat() if d else "" # Return ISO string if date exists, otherwise return an empty string


def _parse_date(s): # Define a function to convert strings into date objects
    """turn string into a date object, return nothing if it's empty or wrong""" # Docstring for date parsing
    s = (s or "").strip() # Clean the input string by removing whitespace or handling None
    if not s: # Check if the string is empty after stripping
        return None # Return None if no data is provided
    try: # Start an exception handling block for date conversion
        return datetime.strptime(s, "%Y-%m-%d").date() # Attempt to parse the string using the YYYY-MM-DD format
    except ValueError: # Catch errors if the string does not match the expected date format
        print(f"  ⚠  Invalid date '{s}' – expected YYYY-MM-DD, skipping.") # Inform the user about the invalid input
        return None # Return None to indicate a failed parse


def _print_contacts(rows): # Define a function to display contact records in a formatted way
    """print out contacts so they look nice on the screen""" # Docstring for the display utility
    if not rows: # Check if the result list is empty
        print("  (no contacts found)") # Inform the user if no data was returned from the database
        return # Exit the function early
    sep = "-" * 80 # Define a separator string of 80 dashes for visual clarity
    print(sep) # Print the top separator line
    for r in rows: # Iterate through each contact record in the provided list
        phones = r.get("phones", []) # Retrieve the list of phones associated with the contact
        phone_str = ", ".join( # Join multiple phone records into a single readable string
            f"{p['phone']} [{p['type']}]" for p in phones # Format each phone with its specific type
        ) if phones else "(no phones)" # Use a placeholder if no phone numbers are attached
        print( # Print the contact details using a multi-line formatted string
            f"  [{r['id']:>4}]  {r['first_name']} {r.get('last_name') or ''}\n" # Print ID and full name
            f"         📧 {r.get('email') or '—'} " # Print email or a dash if missing
            f"   🎂 {_fmt_date(r.get('birthday')) or '—'} " # Print formatted birthday or a dash
            f"   👥 {r.get('group_name') or '—'}\n" # Print group membership
            f"         📞 {phone_str}" # Print the joined phone string
        )
    print(sep) # Print the bottom separator line


def _fetch_contacts_with_phones(conn, contact_ids): # Define a function to retrieve full contact data including phones
    """get contacts and attach their phone numbers to them""" # Docstring for the data fetching logic
    if not contact_ids: # Check if the list of IDs to fetch is empty
        return [] # Return an empty list if no IDs were provided
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: # Create a cursor that returns results as dictionaries
        cur.execute( # Execute a SQL query to fetch basic contact info and group names
            """
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                g.name AS group_name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            WHERE c.id = ANY(%s)
            
            """, # SQL query using a LEFT JOIN for groups and ANY filter for IDs
            (list(contact_ids),), # Pass the list of IDs as a parameter to prevent SQL injection
        )
        contacts = {r["id"]: dict(r) for r in cur.fetchall()} # Convert result rows into a dictionary keyed by contact ID

        cur.execute( # Execute a separate query to fetch all phones for the specified contact IDs
            "SELECT contact_id, phone, type FROM phones WHERE contact_id = ANY(%s)", # SQL to select phone details
            (list(contact_ids),), # Pass IDs parameter
        )
        for row in cur.fetchall(): # Iterate through each phone record fetched
            contacts[row["contact_id"]].setdefault("phones", []).append( # Group phones by contact_id in the dictionary
                {"phone": row["phone"], "type": row["type"]} # Append phone and type details
            )

    for c in contacts.values(): # Iterate through the compiled contact objects
        c.setdefault("phones", []) # Ensure every contact has at least an empty list for phones
    return [contacts[cid] for cid in contact_ids if cid in contacts] # Return list in the order of original IDs


# --- setup database --- # Section for initializing the database environment

def init_schema(): # Define a function to set up tables and logic in the database
    """run the sql files to create tables and functions""" # Docstring for schema initialization
    base = os.path.dirname(os.path.abspath(__file__)) # Get the absolute directory path of the current script
    with _conn() as conn: # Open a new database connection
        with conn.cursor() as cur: # Create a cursor for executing SQL commands
            for fname in ("schema.sql", "procedures.sql"): # Loop through the required SQL setup files
                fpath = os.path.join(base, fname) # Construct the full file path for each SQL file
                with open(fpath, encoding="utf-8") as f: # Open the SQL file with UTF-8 encoding
                    sql = f.read() # Read the entire contents of the SQL file
                cur.execute(sql) # Execute the SQL script in the database
        conn.commit() # Commit the changes to make them permanent
    print("✅  Schema and procedures applied.") # Notify the user of successful setup


# --- search and filters --- # Section for data retrieval features

def filter_by_group(): # Define a function to show contacts based on their group
    """find people that belong to a specific group""" # Docstring for group filtering
    with _conn() as conn: # Open a database connection
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: # Use a dictionary-based cursor
            cur.execute("SELECT id, name FROM groups ORDER BY name") # Fetch all existing groups alphabetically
            groups = cur.fetchall() # Store the list of groups

    if not groups: # Check if the groups table is empty
        print("No groups found.") # Inform the user
        return # Exit the function

    print("\nAvailable groups:") # Header for the group list
    for g in groups: # Loop through and display each available group
        print(f"  {g['id']}. {g['name']}") # Print group ID and name
    choice = input("Enter group number (or name): ").strip() # Prompt user for input to filter by

    with _conn() as conn: # Re-open connection for the filter query
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: # Create cursor
            # accept id or name
            if choice.isdigit(): # If the user input is a number, search by group ID
                cur.execute( # SQL to find contact IDs by group ID
                    """
                    SELECT c.id FROM contacts c
                    JOIN groups g ON g.id = c.group_id
                    WHERE g.id = %s
                    """,
                    (int(choice),), # Pass input as an integer
                )
            else: # If the input is text, search by group name
                cur.execute( # SQL to find contact IDs by case-insensitive name match
                    """
                    SELECT c.id FROM contacts c
                    JOIN groups g ON g.id = c.group_id
                    WHERE LOWER(g.name) = LOWER(%s)
                    """,
                    (choice,), # Pass the string choice
                )
            ids = [r["id"] for r in cur.fetchall()] # Extract contact IDs from the query results

        results = _fetch_contacts_with_phones(conn, ids) # Fetch full contact details for the found IDs
    _print_contacts(results) # Display the filtered results


def search_by_email(): # Define a function to search contacts using email fragments
    """search contacts by typing part of their email""" # Docstring for email search
    query = input("Email search term: ").strip() # Get the search string from the user
    with _conn() as conn: # Open database connection
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: # Create cursor
            cur.execute( # SQL using LIKE for partial matches in the email field
                "SELECT id FROM contacts WHERE LOWER(email) LIKE %s", # Case-insensitive search
                (f"%{query.lower()}%",), # Add wildcard symbols for partial matching
            )
            ids = [r["id"] for r in cur.fetchall()] # Get list of contact IDs
        results = _fetch_contacts_with_phones(conn, ids) # Fetch full details for those IDs
    _print_contacts(results) # Print the found contacts


def sort_and_list(): # Define a function to list all contacts with custom sorting
    """show all contacts but ordered by what the user picks""" # Docstring for sorting functionality
    print("\nSort by:  1) Name   2) Birthday   3) Date added") # Show sorting options
    choice = input("Choice [1]: ").strip() or "1" # Get user choice, default to '1'
    order_map = {"1": "c.first_name, c.last_name", "2": "c.birthday NULLS LAST", "3": "c.created_at"} # Map choice to SQL order clause
    order = order_map.get(choice, "c.first_name, c.last_name") # Determine final SQL order string

    with _conn() as conn: # Open database connection
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: # Create cursor
            cur.execute(f"SELECT id FROM contacts c ORDER BY {order}") # Execute sorting query
            ids = [r["id"] for r in cur.fetchall()] # Collect IDs in the sorted order
        results = _fetch_contacts_with_phones(conn, ids) # Fetch detailed data maintaining order
    _print_contacts(results) # Print the sorted list


def paginated_browse(): # Define a function to view contacts page by page
    """look through contacts a few at a time so it doesn't spam the screen""" # Docstring for pagination
    page_size = 5 # Set the number of records to show per page
    page = 0 # Initialize starting page index

    with _conn() as conn: # Open connection to get total count
        with conn.cursor() as cur: # Create cursor
            cur.execute("SELECT COUNT(*) FROM contacts") # Count total number of contacts in DB
            total = cur.fetchone()[0] # Store the count result

    total_pages = max(1, (total + page_size - 1) // page_size) # Calculate total number of pages needed
    print(f"\nTotal contacts: {total}  |  Page size: {page_size}") # Display total count info

    while True: # Start interaction loop for navigating pages
        offset = page * page_size # Calculate SQL offset based on current page
        with _conn() as conn: # Open connection for fetching page data
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: # Create cursor
                # Re-use the pagination function from Practice 8
                cur.execute( # Execute a stored function to get a specific page of results
                    "SELECT * FROM get_contacts_paginated(%s, %s)", # SQL call to stored procedure/function
                    (page_size, offset), # Pass limits and offset
                )
                rows = cur.fetchall() # Retrieve the page rows

        print(f"\n── Page {page + 1} / {total_pages} ──") # Show current page header
        if rows: # If there are contacts on this page
            ids = [r["id"] for r in rows] # Extract IDs for the current page
            results = _fetch_contacts_with_phones(conn, ids) # Fetch full details including phones
            _print_contacts(results) # Display current page contacts
        else: # If page is empty
            print("  (empty page)") # Inform the user

        cmd = input("[N]ext  [P]rev  [Q]uit: ").strip().lower() # Get navigation command
        if cmd == "n": # Handle 'Next' command
            if page + 1 < total_pages: # Check if next page exists
                page += 1 # Increment page index
            else: # If on the last page
                print("  Already on the last page.") # Warn the user
        elif cmd == "p": # Handle 'Previous' command
            if page > 0: # Check if previous page exists
                page -= 1 # Decrement page index
            else: # If on the first page
                print("  Already on the first page.") # Warn the user
        elif cmd == "q": # Handle 'Quit' command
            break # Exit the pagination loop


# --- import and export stuff --- # Section for external file synchronization

def export_to_json(filepath="contacts_export.json"): # Define a function to export DB to a JSON file
    """save everything to a json file""" # Docstring for JSON export
    with _conn() as conn: # Open database connection
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: # Create cursor
            cur.execute("SELECT id FROM contacts c ORDER BY first_name, last_name") # Get all IDs in alphabetical order
            ids = [r["id"] for r in cur.fetchall()] # Store all IDs
        contacts = _fetch_contacts_with_phones(conn, ids) # Fetch full objects for all contacts

    # Make dates JSON-serialisable
    for c in contacts: # Loop through fetched contacts to sanitize data for JSON
        if isinstance(c.get("birthday"), date): # Check if birthday field is a date object
            c["birthday"] = c["birthday"].isoformat() # Convert date object to ISO string

    with open(filepath, "w", encoding="utf-8") as f: # Open the target file for writing
        json.dump(contacts, f, indent=2, ensure_ascii=False) # Write data as pretty-printed JSON

    print(f"✅  Exported {len(contacts)} contacts to '{filepath}'.") # Confirm success to user


def _upsert_contact_from_dict(conn, data, on_duplicate="ask"): # Define internal function to add or update contacts
    """add a new contact, or update them if they already exist""" # Docstring for upsert logic
    first = (data.get("first_name") or "").strip() # Extract first name and clean it
    last  = (data.get("last_name")  or "").strip() or None # Extract last name, handle as None if empty
    if not first: # Check for mandatory field
        print("  ⚠  Skipping record with no first_name.") # Warn and skip invalid data
        return # Exit function

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: # Create dictionary cursor
        cur.execute( # SQL to check if a contact with the same name already exists
            "SELECT id FROM contacts WHERE first_name = %s AND "
            "(last_name = %s OR (last_name IS NULL AND %s IS NULL))",
            (first, last, last), # Parameters for name matching
        )
        existing = cur.fetchone() # Check for search result

    if existing: # If contact already exists in database
        action = on_duplicate # Determine how to handle the duplicate
        if action == "ask": # If mode is interactive
            print(f"  ⚠  Duplicate: '{first} {last or ''}'.  [S]kip / [O]verwrite? ", end="") # Prompt user
            action = "skip" if input().strip().lower() != "o" else "overwrite" # Resolve action
        if action == "skip": # If skipping duplicates
            print(f"     → Skipped.") # Log skip action
            return # Exit function
        # overwrite: delete and re-insert to cascade phones
        with conn.cursor() as cur: # If overwriting, delete the old record first
            cur.execute("DELETE FROM contacts WHERE id = %s", (existing["id"],)) # Remove existing record

    # Resolve group
    group_id = None # Initialize group ID as None
    group_name = (data.get("group_name") or data.get("group") or "").strip() # Extract group name from various possible keys
    if group_name: # If a group name is specified
        with conn.cursor() as cur: # Open cursor to manage groups
            cur.execute( # Attempt to insert group name if it doesn't already exist
                "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                (group_name,), # Pass group name
            )
            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,)) # Retrieve ID of the group
            row = cur.fetchone() # Fetch the group ID row
            if row: # If found
                group_id = row[0] # Set the group ID for the contact

    birthday = _parse_date(data.get("birthday")) # Parse the birthday string into a date object
    email    = (data.get("email") or "").strip() or None # Extract email, set to None if empty

    with conn.cursor() as cur: # Open cursor for contact insertion
        cur.execute( # SQL to insert the main contact record
            """
            INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (first, last, email, birthday, group_id), # Provide data parameters
        )
        contact_id = cur.fetchone()[0] # Retrieve the auto-generated ID of the new contact

    # Insert phones
    phones = data.get("phones", []) # Extract list of phone objects
    # Also accept flat single-phone fields (from CSV)
    if not phones and data.get("phone"): # Handle simple format where only one phone is provided as a field
        phones = [{"phone": data["phone"], "type": data.get("phone_type", "mobile")}] # Format as list

    with conn.cursor() as cur: # Open cursor for phone insertions
        for p in phones: # Iterate through each phone to be added
            ph_type = (p.get("type") or "mobile").lower() # Determine phone type, default to mobile
            if ph_type not in ("home", "work", "mobile"): # Validate against allowed PostgreSQL enum types
                ph_type = "mobile" # Fallback to mobile if invalid
            cur.execute( # SQL to link phone to the contact
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, p["phone"], ph_type), # Pass relational and phone data
            )

    conn.commit() # Commit all insertions as a single transaction
    print(f"  ✅  Saved: {first} {last or ''}") # Notify user that contact is saved


def import_from_json(filepath=None): # Define function to import data from a JSON file
    """load contacts from json""" # Docstring for JSON import
    if filepath is None: # If no path was passed
        filepath = input("JSON file path [contacts_export.json]: ").strip() or "contacts_export.json" # Get path from user
    if not os.path.exists(filepath): # Check if the file actually exists
        print(f"  ✗  File not found: {filepath}") # Inform user if file is missing
        return # Exit function

    with open(filepath, encoding="utf-8") as f: # Open JSON file for reading
        records = json.load(f) # Load data into a Python list/dict structure

    print(f"Found {len(records)} records in '{filepath}'.") # Log number of records found
    mode = input("On duplicate — [A]sk each / [S]kip all / [O]verwrite all [A]: ").strip().lower() # Set duplicate policy
    on_dup = {"s": "skip", "o": "overwrite"}.get(mode, "ask") # Map user input to internal logic flags

    with _conn() as conn: # Open database connection
        for rec in records: # Loop through each record in the JSON file
            _upsert_contact_from_dict(conn, rec, on_duplicate=on_dup) # Save record to database
    print("✅  Import complete.") # Notify completion


def import_from_csv(filepath=None): # Define function to import data from a CSV file
    """read the csv file and save people to the db. handles the new columns like birthday/email""" # Docstring for CSV import
    if filepath is None: # If no path was passed
        filepath = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv" # Get path from user
    if not os.path.exists(filepath): # Check file existence
        print(f"  ✗  File not found: {filepath}") # Log error if missing
        return # Exit function

    mode = input("On duplicate — [A]sk each / [S]kip all / [O]verwrite all [A]: ").strip().lower() # Set duplicate policy
    on_dup = {"s": "skip", "o": "overwrite"}.get(mode, "ask") # Map input to logic

    imported = 0 # Initialize counter for processed rows
    with _conn() as conn, open(filepath, newline="", encoding="utf-8") as f: # Open DB and CSV file
        reader = csv.DictReader(f) # Create a CSV reader that uses the first row as dictionary keys
        for row in reader: # Iterate through each row in the CSV
            _upsert_contact_from_dict(conn, row, on_duplicate=on_dup) # Process and save each row
            imported += 1 # Increment counter
    print(f"✅  CSV import complete: processed {imported} rows.") # Notify completion


# --- calling db procedures --- # Section for executing server-side stored logic

def call_add_phone(): # Define function to trigger a SQL procedure for adding phones
    """use the sql procedure to add a phone""" # Docstring for procedure call
    name  = input("Contact name: ").strip() # Get contact name
    phone = input("Phone number: ").strip() # Get phone number
    ptype = input("Type (home/work/mobile) [mobile]: ").strip().lower() or "mobile" # Get type with default
    with _conn() as conn: # Open connection
        with conn.cursor() as cur: # Create cursor
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype)) # Call the PostgreSQL stored procedure
        conn.commit() # Commit procedure changes
    print("✅  Phone added.") # Notify user


def call_move_to_group(): # Define function to trigger a SQL procedure for group migration
    """use the sql procedure to change someone's group""" # Docstring for group move procedure
    name  = input("Contact name: ").strip() # Get name of contact to move
    group = input("Target group name: ").strip() # Get name of target group
    with _conn() as conn: # Open connection
        with conn.cursor() as cur: # Create cursor
            cur.execute("CALL move_to_group(%s, %s)", (name, group)) # Execute the 'move_to_group' procedure
        conn.commit() # Commit the group change
    print("✅  Contact moved.") # Notify user


def call_search_contacts(): # Define function to use a SQL search function
    """use the sql function to search across everything""" # Docstring for global search
    query = input("Search query: ").strip() # Get search term
    with _conn() as conn: # Open connection
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: # Create dictionary cursor
            cur.execute("SELECT * FROM search_contacts(%s)", (query,)) # Select from a set-returning SQL function
            rows = cur.fetchall() # Retrieve matching records
        ids = [r["id"] for r in rows] # Extract IDs from results
        results = _fetch_contacts_with_phones(conn, ids) # Fetch full details including phone numbers
    _print_contacts(results) # Display the results


# --- main menu loop --- # Section for the User Interface logic

MENU = """
╔══════════════════════════════════════════════════╗
║         PhoneBook  –  TSIS 1 Extended Menu       ║
╠══════════════════════════════════════════════════╣
║  SCHEMA                                          ║
║  0.  Apply schema & procedures                   ║
╠══════════════════════════════════════════════════╣
║  SEARCH & FILTER                                 ║
║  1.  Filter contacts by group                    ║
║  2.  Search by email                             ║
║  3.  List all contacts (sorted)                  ║
║  4.  Browse contacts (paginated)                 ║
╠══════════════════════════════════════════════════╣
║  IMPORT / EXPORT                                 ║
║  5.  Export to JSON                              ║
║  6.  Import from JSON                            ║
║  7.  Import from CSV (extended)                  ║
╠══════════════════════════════════════════════════╣
║  STORED PROCEDURES                               ║
║  8.  Add phone number to contact                 ║
║  9.  Move contact to group                       ║
║  10. Search contacts (all fields + phones)       ║
╠══════════════════════════════════════════════════╣
║  Q.  Quit                                        ║
╚══════════════════════════════════════════════════╝
""" # Multi-line string holding the visual menu layout

HANDLERS = { # Dictionary mapping user input strings to function references
    "0":  init_schema, # Map '0' to schema setup
    "1":  filter_by_group, # Map '1' to group filtering
    "2":  search_by_email, # Map '2' to email search
    "3":  sort_and_list, # Map '3' to sorted listing
    "4":  paginated_browse, # Map '4' to pagination
    "5":  export_to_json, # Map '5' to JSON export
    "6":  import_from_json, # Map '6' to JSON import
    "7":  import_from_csv, # Map '7' to CSV import
    "8":  call_add_phone, # Map '8' to add phone procedure
    "9":  call_move_to_group, # Map '9' to move group procedure
    "10": call_search_contacts, # Map '10' to universal search function
}


def main(): # Define the main application entry point function
    while True: # Infinite loop to keep the program running until quit
        print(MENU) # Display the main menu to the user
        choice = input("Select option: ").strip().lower() # Get and normalize user input
        if choice == "q": # If user wants to quit
            print("Goodbye!") # Say goodbye
            break # Exit the infinite loop
        handler = HANDLERS.get(choice) # Look up the corresponding function for the choice
        if handler: # If a valid handler function was found
            try: # Start safety block for runtime errors
                handler() # Execute the selected function
            except psycopg2.Error as e: # Catch database-specific exceptions
                print(f"  ✗  Database error: {e.pgerror or e}") # Display DB error message
            except KeyboardInterrupt: # Catch user interruption (Ctrl+C)
                print() # Print a newline for clean output
        else: # If the user input does not match any menu option
            print("  Invalid choice, please try again.") # Warn the user and loop again


if __name__ == "__main__": # Boilerplate to check if script is being run directly
    main() # Start the main program execution