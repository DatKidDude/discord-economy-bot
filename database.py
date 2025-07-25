import sqlite3
from datetime import datetime, timezone

def adapt_datetime_iso(val):
    return val.replace(tzinfo=timezone.utc).isoformat()

sqlite3.register_adapter(datetime, adapt_datetime_iso)

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

sqlite3.register_converter("datetime", convert_datetime)

class Database:
    
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    
    def _init_db(self):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        discord_id INTEGER PRIMARY KEY,
                        currency INTEGER NOT NULL,
                        event_time datetime DEFAULT NULL
                    ); """
                )

                # commit the changes
                conn.commit()

        except sqlite3.OperationalError as e:
            print(f"Failed to create table: {e}")
    
    def add_user(self, discord_id, currency=1000):
        """Adds a user and their starting currency to the database"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (discord_id, currency) VALUES (?, ?)", (discord_id, currency))
            conn.commit()
    
    def remove_user(self, discord_id):
        """Removes the user from the database"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM users WHERE discord_id = ?", (discord_id,))
            conn.commit()
    
    def update_currency(self, discord_id, currency, event_time):
        """Updates the user's currency"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET currency = currency + ?, event_time = ? WHERE discord_id = ?", (currency, event_time, discord_id))
            conn.commit()
    
    def get_currency(self, discord_id):
        """Returns the user's currency"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT currency FROM users WHERE discord_id = ?", (discord_id,))
            return cursor.fetchone()[0]
            
    def get_all_users(self):
        """Displays all the users and their currency in the database"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            return rows
    
    def get_user(self, discord_id):
        """Returns a user from the database"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
            row = cursor.fetchone()
            return row
    
    def check_user_exists(self, discord_id):
        """Returns 1 if the user exists"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE discord_id = ?", (discord_id,))
            row = cursor.fetchone()[0]
            return row
    
    def remove_table(self):
        """Only used for development"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE users")
            conn.commit()

if __name__ == "__main__":
    db = Database()