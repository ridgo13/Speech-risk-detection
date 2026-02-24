import sqlalchemy
from sqlalchemy import create_engine, text
import urllib.parse

# --- YOUR DETAILS ---
DB_HOST = "103.145.155.250"
DB_USER = "postgres"
DB_PASS = "qz*,2zZQ=4<6v4jY"
DB_NAME = "speaktrum_db"
DB_PORT = "5432"

# 1. Encode the password (crucial because of special characters like '*')
safe_password = urllib.parse.quote_plus(DB_PASS)

# 2. Build the URL
DB_URL = f"postgresql://{DB_USER}:{safe_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 3. Test Connection
print(f"📡 Attempting to reach SpeakTrum DB at {DB_HOST}...")

engine = create_engine(DB_URL)

try:
    with engine.connect() as conn:
        # A simple query that just returns the number 1
        result = conn.execute(text("SELECT 1"))
        if result.fetchone()[0] == 1:
            print("✅ CONNECTION ONLINE: Your cloud database is ready!")
except Exception as e:
    print("\n❌ CONNECTION FAILED")
    print(f"Error details: {e}")
    print("\n--- Troubleshooting Checklist ---")
    print("1. Is your current IP added to Google Cloud 'Authorized Networks'?")
    print("2. Is 'speaktrum_db' created in the 'Databases' tab of your SQL instance?")
    print("3. Did you install psycopg2-binary? (pip install psycopg2-binary)")