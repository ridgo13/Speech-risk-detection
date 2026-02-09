from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4
from typing import List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import jwt
import aiofiles
from passlib.context import CryptContext
import psycopg2
from psycopg2.extras import RealDictCursor
from google.cloud import storage 

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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# --- GOOGLE CLOUD STORAGE CONFIG (UPDATED FOR BOTH BUCKETS) ---
RAW_BUCKET_NAME = "speaktrum-raw-audio"          # <--- Bucket 1 (Originals)
PROCESSED_BUCKET_NAME = "speaktrum-processed-data" # <--- Bucket 2 (Cleaned/Spectrograms)
KEY_PATH = "backend_scripts/service_account.json" 

# =========================================================
# IMPORT PARISHAD'S ETL MODULES
# =========================================================
try:
    from backend_scripts.etl_pipeline import AudioETL
    from backend_scripts.feature_extractor import generate_mel_spectrogram
except ImportError as e:
    print(f"\n⚠️ IMPORT ERROR: {e}")

# =========================================================
# DATABASE CONNECTION HELPER
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

# =========================================================
# GCS UPLOAD FUNCTION (UPDATED TO ACCEPT BUCKET NAME)
# =========================================================
def upload_to_gcs(local_file_path, destination_blob_name, bucket_name):
    """Uploads a file to a SPECIFIC bucket."""
    try:
        if not os.path.exists(KEY_PATH):
            print(f"⚠️ SKIPPING GCS: Key not found at {KEY_PATH}")
            return None

        storage_client = storage.Client.from_service_account_json(KEY_PATH)
        bucket = storage_client.bucket(bucket_name) # <--- Uses the specific bucket
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
DIAGNOSIS_RESULTS_DB = {} 

def get_user_from_db(username: str):
    conn = get_db_connection()
    if not conn: return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        return user
    except Exception as e:
        print(f"DB Error: {e}")
        return None
    finally:
        if conn: conn.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username: raise HTTPException(status_code=401, detail="Invalid token")
            
        user = get_user_from_db(username)
        if not user: raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# =========================================================
# DATA MODELS
# =========================================================
class UserRegistrationContract(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6)

class DiagnosisResultContract(BaseModel):
    userId: str
    probability: float
    diagnosis: str
    timestamp: datetime

class DiagnosisHistoryContract(BaseModel):
    userId: str
    diagnosisHistory: List[DiagnosisResultContract]

# =========================================================
# PARISHAD'S ETL COORDINATOR
# =========================================================
def run_parishad_etl(file_path: str, user_id: str):
    print(f"🔄 ETL: Starting pipeline for {file_path}...")
    
    # 1. Setup Paths
    directory = os.path.dirname(file_path)
    original_filename = os.path.basename(file_path)
    filename_stem = os.path.splitext(original_filename)[0]
    
    clean_filename = f"cleaned_{original_filename}"
    clean_path = os.path.join(directory, clean_filename)
    
    try:
        # 2. Run Cleaning
        etl_engine = AudioETL() 
        success_clean = etl_engine.run_pipeline(file_path, clean_path)
        
        if not success_clean:
            print("❌ ETL STOPPED: Audio failed quality check.")
            return
            
        print(f"✅ ETL CLEANED: Saved locally to {clean_path}")

        # 3. Run Feature Extraction
        success_feature = generate_mel_spectrogram(clean_path, directory, filename_stem)
        
        if success_feature:
            print(f"✅ ETL FEATURES: Spectrogram generated")
            
            # --- 4. CLOUD UPLOAD (PROCESSED BUCKET) ---
            print("🚀 Starting Processed Uploads...")
            
            # Upload Cleaned Audio -> PROCESSED BUCKET
            gcs_audio_name = f"processed_audio/{user_id}/{clean_filename}"
            upload_to_gcs(clean_path, gcs_audio_name, PROCESSED_BUCKET_NAME)
            
            # Upload Spectrogram -> PROCESSED BUCKET
            image_local_path = os.path.join(directory, f"{filename_stem}.png")
            if os.path.exists(image_local_path):
                gcs_image_name = f"spectrograms/{user_id}/{filename_stem}.png"
                upload_to_gcs(image_local_path, gcs_image_name, PROCESSED_BUCKET_NAME)
                
            print("✨ ETL COMPLETE: Cleaned files sent to Processed Bucket.")
            
        else:
            print("❌ ETL ERROR: Could not generate spectrogram.")

    except Exception as e:
        print(f"❌ PIPELINE ERROR: {str(e)}")

# =========================================================
# API ENDPOINTS
# =========================================================

@app.post("/test-user-registration", tags=["Authentication"])
async def register_user(user_data: UserRegistrationContract):
    conn = get_db_connection()
    if not conn: raise HTTPException(500, "DB Connection Error")
    try:
        cur = conn.cursor()
        hashed = pwd_context.hash(user_data.password)
        cur.execute("INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)",
                    (user_data.username, user_data.email, hashed))
        conn.commit()
        return {"message": "User registered permanently in DB!"}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        conn.close()

@app.post("/login", tags=["Authentication"])
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_from_db(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/upload-audio", tags=["Diagnosis"], status_code=202)
async def upload_audio(
    audioFormat: str = Form(...),
    timestamp: datetime = Form(...), 
    audio_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    # 1. Validate
    ext = audio_file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    # 2. Save Raw File to Disk
    file_name = f"{uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await audio_file.read(1024 * 1024):
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # --- 3. UPLOAD RAW TO GCS (NEW!) ---
    # We do this immediately so the original is safe in the RAW bucket
    print("🚀 Uploading Original to Raw Bucket...")
    raw_gcs_path = f"raw_uploads/{current_user['username']}/{file_name}"
    upload_to_gcs(file_path, raw_gcs_path, RAW_BUCKET_NAME)

    # 4. Save Info to Database
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            insert_query = """
            INSERT INTO voice_recordings (user_id, file_path, audio_format, created_at)
            VALUES (%s, %s, %s, %s)
            """
            cur.execute(insert_query, (current_user["username"], file_path, audioFormat, timestamp))
            conn.commit()
            conn.close()
            print(f"✅ DB SUCCESS: Metadata saved.")
        except Exception as db_e:
            print(f"❌ DB ERROR: {db_e}")

    # 5. Trigger ETL (Clean & Process)
    background_tasks.add_task(run_parishad_etl, file_path, current_user["username"])

    # 6. Mock Result
    mock_result = {
        "userId": current_user["username"],
        "probability": 0.87,
        "diagnosis": "Parkinson’s risk detected",
        "timestamp": datetime.utcnow()
    }
    DIAGNOSIS_RESULTS_DB.setdefault(current_user["username"], []).append(mock_result)

    return {
        "message": "Audio received. Raw upload complete. ETL started.",
        "file_id": file_name,
        "user": current_user["username"]
    }

@app.get("/get-diagnosis-result/{userId}", response_model=DiagnosisResultContract, tags=["Diagnosis"])
async def get_diagnosis_result(userId: str, current_user: dict = Depends(get_current_user)):
    if userId != current_user["username"]: raise HTTPException(403, "Access denied")
    if userId not in DIAGNOSIS_RESULTS_DB: raise HTTPException(404, "Diagnosis not found")
    return DIAGNOSIS_RESULTS_DB[userId][-1]

@app.get("/diagnosis-history/{userId}", response_model=DiagnosisHistoryContract, tags=["User Data"])
async def get_diagnosis_history(userId: str, current_user: dict = Depends(get_current_user)):
    if userId != current_user["username"]: raise HTTPException(403, "Access denied")
    history = []
    if userId in DIAGNOSIS_RESULTS_DB: history.append(DIAGNOSIS_RESULTS_DB[userId])
    return {"userId": userId, "diagnosisHistory": history}

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "OK", "time": datetime.utcnow()}

@app.on_event("startup")
async def startup_event():
    print("\n🚀 SpeakTrum Backend Started Successfully")
    conn = get_db_connection()
    if conn:
        print("✅ CONNECTED to Google Cloud SQL!")
        conn.close()
    else:
        print("⚠️ WARNING: Could not connect to Database.")
    print("📘 Swagger UI: http://127.0.0.1:8000/docs\n")