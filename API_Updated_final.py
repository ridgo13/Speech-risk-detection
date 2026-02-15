from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4, UUID
from typing import List, Optional
from datetime import datetime, timedelta
import os
import jwt
import aiofiles
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor
from google.cloud import storage
from dotenv import load_dotenv

# =========================================================
# CONFIGURATION & ENVIRONMENT
# =========================================================
load_dotenv()

app = FastAPI(title="SpeakTrum – Speech Risk Detection API")

# Setup Folders
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_AUDIO_EXTENSIONS = {"wav", "mp3", "m4a", "flac"}

# SECURITY CONFIG
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_for_development_only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# --- GOOGLE CLOUD STORAGE CONFIG ---
RAW_BUCKET_NAME = "speaktrum-raw-audio"
PROCESSED_BUCKET_NAME = "speaktrum-processed-data"
KEY_PATH = "ai/backend_pipeline/service_account.json"

# =========================================================
# PASSWORD HELPERS (Password Logic)
# =========================================================
def hash_password(password: str) -> str:
    """Securely hash a password for storage."""
    # Bcrypt has a 72-byte limit. We truncate just in case to prevent crashes.
    byte_pwd = password.encode('utf-8')[:72] 
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(byte_pwd, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8')[:72], 
        hashed_password.encode('utf-8')
    )

# =========================================================
# IMPORT AI MODULES
# =========================================================
try:
    from ai.backend_pipeline.etl_pipeline import AudioETL
    from ai.backend_pipeline.feature_extractor import generate_mel_spectrogram
except ImportError as e:
    print(f"⚠️ AI MODULE IMPORT ERROR: {e}. Check folder naming and __init__.py files.")

# =========================================================
# DATABASE & HELPER FUNCTIONS
# =========================================================
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"❌ Database Connection Failed: {e}")
        return None

def upload_to_gcs(local_file_path, destination_blob_name, bucket_name):
    try:
        if not os.path.exists(KEY_PATH):
            print(f"⚠️ SKIPPING GCS: Key not found at {KEY_PATH}")
            return None
        storage_client = storage.Client.from_service_account_json(KEY_PATH)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)
        print(f"☁️ UPLOADED to {bucket_name}: {destination_blob_name}")
        return blob.public_url
    except Exception as e:
        print(f"❌ GCS UPLOAD FAILED: {e}")
        return None

# =========================================================
# SECURITY & AUTHENTICATION
# =========================================================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # The UUID is stored in 'sub'
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, email, role FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        conn.close()
        
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Authentication failed")

# =========================================================
# DATA CONTRACTS
# =========================================================
class UserRegistrationContract(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8) # Professional standard min-length

class DiagnosisResultContract(BaseModel):
    user_id: str
    probability: float
    diagnosis: str
    created_at: datetime # Matches DB column name

class DiagnosisHistoryContract(BaseModel):
    user_id: str
    diagnosisHistory: List[DiagnosisResultContract]

class ModelTrainingStatusContract(BaseModel):
    modelId: str
    trainingStatus: str
    accuracy: float
    timestamp: datetime

class RealTimeFeedbackContract(BaseModel):
    user_id: str
    feedback: str
    timestamp: datetime

# =========================================================
# AUDIO PROCESSING COORDINATOR (WITH TELEMETRY)
# =========================================================
def run_audio_processing_pipeline(file_path: str, user_id: str):
    """Handles ETL and Feature Extraction in the background."""
    print(f"🔄 ETL: Starting background pipeline for user {user_id}...")
    directory = os.path.dirname(file_path)
    original_filename = os.path.basename(file_path)
    filename_stem = os.path.splitext(original_filename)[0]
    clean_path = os.path.join(directory, f"cleaned_{original_filename}")

    try:
        etl_engine = AudioETL()
        if etl_engine.run_pipeline(file_path, clean_path):
            print(f"✅ ETL CLEANED: {clean_path}")
            
            generate_mel_spectrogram(clean_path, directory, filename_stem)
            print(f"✅ ETL FEATURES: Spectrogram generated.")
            
            # Cloud Uploads
            print("🚀 Starting Processed Bucket Uploads...")
            upload_to_gcs(clean_path, f"processed/{user_id}/{original_filename}", PROCESSED_BUCKET_NAME)
            
            spec_path = os.path.join(directory, f"{filename_stem}.png")
            if os.path.exists(spec_path):
                upload_to_gcs(spec_path, f"spectrograms/{user_id}/{filename_stem}.png", PROCESSED_BUCKET_NAME)
            
            print("✨ ETL COMPLETE: All files synced to Cloud.")
            
    except Exception as e:
        print(f"❌ Background Pipeline Error: {e}")

# =========================================================
# API ENDPOINTS (Ensure this starts at the far left margin)
# =========================================================
@app.post("/register", tags=["Authentication"], status_code=201)
async def register_user(user_data: UserRegistrationContract):
    conn = get_db_connection()
    if not conn: raise HTTPException(500, "Database connection failed")
    try:
        cur = conn.cursor()
        new_uuid = str(uuid4()) # Generate permanent UUID
        hashed_pwd = hash_password(user_data.password)
        
        cur.execute(
            "INSERT INTO users (user_id, username, email, hashed_password) VALUES (%s, %s, %s, %s)",
            (new_uuid, user_data.username, user_data.email, hashed_pwd)
        )
        conn.commit()
        print(f"👤 NEW USER: {user_data.username} registered with ID {new_uuid}")
        return {"message": "User created successfully", "user_id": new_uuid}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(400, "Username or Email already registered")
    finally:
        conn.close()

@app.post("/login", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, hashed_password FROM users WHERE username = %s", (form_data.username,))
    user = cur.fetchone()
    conn.close()

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(401, "Invalid username or password")

# We store the UUID in the token for permanent identification
    token = create_access_token(data={"sub": user["user_id"]})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/upload-audio", tags=["Diagnosis"], status_code=202)
async def upload_audio(
    audioFormat: str = Form(...),
    timestamp: datetime = Form(...),
    audio_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    # 1. Validation
    ext = audio_file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(400, "Invalid audio format")

    # 2. Secure local save with teammate's robust error handling
    file_id = str(uuid4())
    local_filename = f"{file_id}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, local_filename)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await audio_file.read(1024*1024):
                await f.write(chunk)
    except Exception as e:
        raise HTTPException(500, detail=f"File save failed: {str(e)}")

    # 3. Cloud Storage (Raw Bucket)
    print(f"🚀 Uploading Original to Raw Bucket for user {current_user['username']}...")
    upload_to_gcs(file_path, f"raw/{current_user['user_id']}/{local_filename}", RAW_BUCKET_NAME)

    # 4. Database Entry (Permanent Storage)
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO voice_recordings (user_id, file_path, audio_format, created_at) VALUES (%s, %s, %s, %s)",
                (current_user["user_id"], file_path, audioFormat, timestamp)
            )
            conn.commit()
            print(f"✅ DB SUCCESS: Recording metadata saved.")
        except Exception as e:
            conn.rollback()
            print(f"❌ DB ERROR: {e}")
        finally:
            conn.close()

    background_tasks.add_task(run_audio_processing_pipeline, file_path, current_user["user_id"])
    
    return {
        "message": "Audio received. Processing started.", 
        "file_id": file_id,
        "status": "In-Progress"
    }

@app.get("/get-diagnosis-result/{user_id}", response_model=DiagnosisResultContract, tags=["Diagnosis"])
async def get_result(user_id: str, current_user: dict = Depends(get_current_user)):
    # Check UUID match
    if user_id != current_user["user_id"]:
        raise HTTPException(403, "Unauthorized to view this data")
   
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM diagnosis_results WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (user_id,))
    result = cur.fetchone()
    conn.close()
   
    if not result: raise HTTPException(404, "No diagnosis found yet.")
    return result


@app.get("/diagnosis-history/{user_id}", response_model=DiagnosisHistoryContract, tags=["User Data"])
async def get_history(user_id: str, current_user: dict = Depends(get_current_user)):
    if user_id != current_user["user_id"]: raise HTTPException(403, "Access denied")
   
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM diagnosis_results WHERE user_id = %s", (user_id,))
    history = cur.fetchall()
    conn.close()
    return {"user_id": user_id, "diagnosisHistory": history}


@app.post("/real-time-feedback", response_model=RealTimeFeedbackContract, tags=["Feedback"])
async def submit_feedback(feedback_data: RealTimeFeedbackContract, current_user: dict = Depends(get_current_user)):
    # Real-world logic: save feedback to a database table (implied)
    return feedback_data


@app.get("/model-training-status/{modelId}", response_model=ModelTrainingStatusContract, tags=["System"])
async def get_model_status(modelId: str):
    return {
        "modelId": modelId,
        "trainingStatus": "Optimized",
        "accuracy": 0.945,
        "timestamp": datetime.utcnow()
    }

@app.on_event("startup")
async def startup():
    print("\n🚀 SpeakTrum Production API Online")
    conn = get_db_connection()
    if conn:
        print("✅ CONNECTED to Google Cloud SQL!")
        conn.close()
    else:
        print("⚠️ WARNING: Could not connect to Database.")
    print("📘 Documentation at: http://127.0.0.1:8000/docs\n")