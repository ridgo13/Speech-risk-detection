import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_tables():
    print("⏳ Connecting to Google Cloud SQL (Production Instance)...")
    
    try:
        # 1. Connect to Database
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        cur = conn.cursor()

        # 2. Define Real-World Schemas
        # We use VARCHAR(36) for UUIDs to ensure compatibility with Python's str(uuid4())
        
        commands = [
            # --- TABLE 1: USERS ---
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # --- TABLE 2: VOICE RECORDINGS ---
            """
            CREATE TABLE IF NOT EXISTS voice_recordings (
                recording_id SERIAL PRIMARY KEY,
                user_id VARCHAR(36) REFERENCES users(user_id) ON DELETE CASCADE,
                file_path TEXT NOT NULL,
                audio_format VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # --- TABLE 3: DIAGNOSIS RESULTS ---
            # This stores the medical history permanently
            """
            CREATE TABLE IF NOT EXISTS diagnosis_results (
                result_id SERIAL PRIMARY KEY,
                user_id VARCHAR(36) REFERENCES users(user_id) ON DELETE CASCADE,
                probability FLOAT NOT NULL,
                diagnosis TEXT NOT NULL,
                model_version VARCHAR(50) DEFAULT 'v1.0',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # --- TABLE 4: USER FEEDBACK (New!) ---
            """
            CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id SERIAL PRIMARY KEY,
                user_id VARCHAR(36) REFERENCES users(user_id) ON DELETE CASCADE,
                feedback_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]

        # 3. Execute Commands
        for command in commands:
            cur.execute(command)
        
        conn.commit()
        print("✅ SUCCESS: All production tables (Users, Recordings, Diagnosis, Feedback) created!")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")
        print("Tip: If the error says 'Relation already exists', you need to DROP the old tables first.")

if __name__ == "__main__":
    create_tables()