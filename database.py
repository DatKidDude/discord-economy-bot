import sqlite3

class Database:
    
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        discord_id TEXT PRIMARY KEY,
                        currency INT NOT NULL
                    ); """
                )

                # commit the changes
                conn.commit()

                print("Tables created successfully.")
        except sqlite3.OperationalError as e:
            print(f"Failed to create table: {e}")
    
    def add_user(self, discord_id, currency=1000):
        """Adds a user and their starting currency to the database"""
        with self._connect() as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users (discord_id, currency) VALUES (?, ?)", (discord_id, currency))
            conn.commit()
    
    def remove_user(self):
        """Removes the user from the database"""
        pass
    
    def update_currency(self):
        """Adds or subtracts currency from the user"""
        pass
    
    def get_users(self):
        """Displays all the users and their currency in the database"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            return rows

