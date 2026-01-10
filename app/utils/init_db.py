import os
import psycopg
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DB_URL = os.environ.get("POSTGRESQL_URL", "")

def init_db():
    if not DB_URL:
        logger.error("POSTGRESQL_URL is not set. Cannot initialize database.")
        return

    try:
        # Connect to an existing database
        with psycopg.connect(DB_URL) as conn:
            # Open a cursor to perform database operations
            with conn.cursor() as cur:
                # Create the users table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Check if it was created
                cur.execute("SELECT to_regclass('public.users');")
                if cur.fetchone()[0]:
                    logger.info("✅ 'users' table checked/created successfully.")
                else:
                    logger.warning("⚠️ 'users' table might not have been created.")
            
            # Make the changes to the database persistent
            conn.commit()

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
