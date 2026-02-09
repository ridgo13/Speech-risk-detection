import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    print("⏳ Connecting to Google Cloud SQL...")
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        cur = conn.cursor()

        # SQL Command to create the table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS voice_recordings (
            recording_id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            audio_format VARCHAR(10),
            duration_seconds FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cur.execute(create_table_query)
        conn.commit()
        
        print("✅ SUCCESS: Table 'voice_recordings' created in Google Cloud!")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: Could not create table. {e}")

if __name__ == "__main__":
    create_tables()