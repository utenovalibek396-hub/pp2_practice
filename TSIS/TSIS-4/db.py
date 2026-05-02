# db.py — PostgreSQL / psycopg2 database layer # File header indicating this is the database abstraction layer

import psycopg2 # Import the main PostgreSQL adapter for Python
import psycopg2.extras # Import extra modules for extended functionality like DictCursor
from datetime import datetime # Import datetime class to handle time-related data
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS # Import database credentials from a config file

_conn = None # Initialize a private global variable to store the database connection object


def get_connection(): # Define a function to establish or retrieve a database connection
    global _conn # Reference the global _conn variable inside the function scope
    if _conn is None or _conn.closed: # Check if the connection doesn't exist or has been closed
        _conn = psycopg2.connect( # Establish a new connection using the imported credentials
            host=DB_HOST, # Specify the database server address
            port=DB_PORT, # Specify the port number for the database connection
            dbname=DB_NAME, # Specify the name of the specific database to use
            user=DB_USER, # Specify the database user account
            password=DB_PASS, # Provide the password for the database user
        ) # End of connection parameters
    return _conn # Return the active connection object


def init_db(): # Define a function to initialize the database schema
    """Create tables if they don't exist.""" # Docstring explaining the function's purpose
    sql = """ 
    CREATE TABLE IF NOT EXISTS players ( 
        id       SERIAL PRIMARY KEY, 
        username VARCHAR(50) UNIQUE NOT NULL 
    ); 

    CREATE TABLE IF NOT EXISTS game_sessions ( 
        id             SERIAL PRIMARY KEY, 
        player_id      INTEGER REFERENCES players(id), 
        score          INTEGER   NOT NULL, 
        level_reached  INTEGER   NOT NULL, 
        played_at      TIMESTAMP DEFAULT NOW() 
    ); 
    """ # Multi-line string containing SQL commands to create necessary tables
    try: # Start a block to handle potential database errors
        conn = get_connection() # Get the current active database connection
        with conn.cursor() as cur: # Create a cursor object for executing SQL commands using a context manager
            cur.execute(sql) # Execute the table creation SQL commands
        conn.commit() # Commit the transaction to save changes to the database
        return True # Return True indicating successful initialization
    except Exception as e: # Catch any exceptions that occur during the process
        print(f"[DB] init_db error: {e}") # Print a formatted error message to the console
        return False # Return False indicating that initialization failed


def get_or_create_player(username: str) -> int | None: # Function to find a player's ID or create a new player entry
    """Return player id, creating the row if it doesn't exist.""" # Docstring explaining the logic
    try: # Start error handling block
        conn = get_connection() # Retrieve the database connection
        with conn.cursor() as cur: # Open a cursor for database interaction
            cur.execute( # Execute an INSERT statement
                "INSERT INTO players (username) VALUES (%s) " # Insert the new username
                "ON CONFLICT (username) DO NOTHING", # Avoid error if the username already exists
                (username,), # Pass the username as a tuple to prevent SQL injection
            ) # End of execute statement
            conn.commit() # Save the insertion change
            cur.execute("SELECT id FROM players WHERE username = %s", (username,)) # Retrieve the ID of the player
            row = cur.fetchone() # Fetch the first result row from the query
            return row[0] if row else None # Return the ID if found, otherwise return None
    except Exception as e: # Catch exceptions during player retrieval/creation
        print(f"[DB] get_or_create_player error: {e}") # Log the error to the console
        return None # Return None in case of failure


def save_session(player_id: int, score: int, level: int): # Function to record a finished game session
    """Persist a finished game session.""" # Docstring explaining the persistence purpose
    try: # Start error handling block
        conn = get_connection() # Retrieve the database connection
        with conn.cursor() as cur: # Open a cursor for SQL execution
            cur.execute( # Execute an INSERT statement for game history
                "INSERT INTO game_sessions (player_id, score, level_reached) " # Specify target columns
                "VALUES (%s, %s, %s)", # Use placeholders for values
                (player_id, score, level), # Provide data as a tuple for security
            ) # End of execute statement
        conn.commit() # Commit the session record to the database
        return True # Return True indicating the session was saved successfully
    except Exception as e: # Catch exceptions during the save process
        print(f"[DB] save_session error: {e}") # Log the error to the console
        return False # Return False if saving failed


def get_personal_best(player_id: int) -> int: # Function to retrieve a specific player's highest score
    """Return the player's all-time highest score (0 if none).""" # Docstring for score retrieval logic
    try: # Start error handling block
        conn = get_connection() # Retrieve the database connection
        with conn.cursor() as cur: # Open a cursor for the query
            cur.execute( # Execute a SELECT query with an aggregate function
                "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s", # Find max score or 0 if NULL
                (player_id,), # Provide the player ID as a safe parameter
            ) # End of execute statement
            row = cur.fetchone() # Fetch the result of the aggregation
            return row[0] if row else 0 # Return the score or 0 if no records exist
    except Exception as e: # Catch exceptions during score retrieval
        print(f"[DB] get_personal_best error: {e}") # Log the error
        return 0 # Return 0 if an error occurs


def get_leaderboard(limit: int = 10) -> list[dict]: # Function to get a list of top scores
    """Return top <limit> scores across all players.""" # Docstring for the leaderboard query
    try: # Start error handling block
        conn = get_connection() # Retrieve the database connection
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur: # Use DictCursor to get results as dictionaries
            cur.execute( # Execute a complex JOIN query for the leaderboard
                """
                SELECT p.username, gs.score, gs.level_reached,
                       gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC, gs.played_at DESC
                LIMIT %s
                """, # SQL that joins tables, sorts by score/date, and limits results
                (limit,), # Pass the limit as a parameter
            ) # End of execute statement
            rows = cur.fetchall() # Fetch all matching rows
            return [dict(r) for r in rows] # Convert each DictRow object into a standard Python dictionary
    except Exception as e: # Catch exceptions during leaderboard retrieval
        print(f"[DB] get_leaderboard error: {e}") # Log the error
        return [] # Return an empty list if an error occurs


def close(): # Function to manually close the database connection
    global _conn # Reference the global connection variable
    if _conn and not _conn.closed: # Check if a connection exists and is still open
        _conn.close() # Close the database connection
        _conn = None # Reset the connection variable to None