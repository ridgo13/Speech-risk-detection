from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks, status
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
import librosa
import numpy as np
from passlib.context import CryptContext
import psycopg2
from psycopg2.extras import RealDictCursor
from google.cloud import storage
from fastapi.security import OAuth2PasswordRequestForm
from zoneinfo import ZoneInfo
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
# =========================================================
# CONFIGURATION & ENVIRONMENT
# =========================================================
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MY_TIMEZONE = ZoneInfo("Asia/Kuala_Lumpur") # UTC+8

app = FastAPI(
    title="SpeakTrum – Secure Healthcare API",
    docs_url="/docs",           # Now you can visit http://127.0.0.1:8000/docs
    redoc_url="/redoc",         # Optional: Alternative documentation view
    openapi_url="/openapi.json" # Required for the docs to work
)

# Check the environment mode from your .env file
ENV_MODE = os.getenv("ENV_MODE", "dev") 

if ENV_MODE != "dev":
    app.add_middleware(HTTPSRedirectMiddleware)
    logger.info("🔒 PRODUCTION MODE: HTTPS Redirect Enabled")
else:
    logger.info("🔓 DEV MODE: HTTPS Redirect Disabled (Local Testing)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # for local testing
        "http://localhost:8080"    # replace with real domain later
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please slow down."},
    )

# Setup Folders
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Audio Standards (Combined User & Teammate logic)
ALLOWED_AUDIO_EXTENSIONS = {"wav", "m4a"} # User's full list
MIN_SNR_DB = 10  #Quality Threshold
TARGET_SAMPLE_RATE = 16000

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

MAX_FILE_SIZE_MB = 10

# Security Config (Passlib + User's Constants)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in environment variables")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Google Cloud Storage Config (User's Paths)
RAW_BUCKET_NAME = "speaktrum-raw-audio"
PROCESSED_BUCKET_NAME = "speaktrum-processed-data"
KEY_PATH = "ai/backend_pipeline/service_account.json" 

# =========================================================
# DATABASE & SECURE HELPER FUNCTIONS
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
        logger.error("Database connection error")
        return None

def generate_secure_url(bucket_name, blob_name):
    """Generates a temporary Signed URL (Valid for 15 minutes)."""
    try:
        if not blob_name: return None
        storage_client = storage.Client.from_service_account_json(KEY_PATH)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="GET",
        )
    except Exception as e:
        logger.error("Signed URL Error")
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
        return destination_blob_name
    except Exception as e:
        logger.error("GCS UPLOAD FAILED")
        return None

# =========================================================
# DATA CONTRACTS
# =========================================================
class UserRegistrationContract(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class DiagnosisResultContract(BaseModel):
    user_id: str
    probability: float
    diagnosis: str
    created_at: datetime 

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
# STARTUP CHECKS
# =========================================================
@app.on_event("startup")
async def startup_event():
    print("\n🔍 STARTING SYSTEM CHECKS...")
    conn = get_db_connection()
    if conn:
        print("✅ CONNECTED to Google Cloud SQL!")
        conn.close()
    else:
        print("❌ Database Connection Failed (Check IP Whitelist)")

    try:
        if os.path.exists(KEY_PATH):
            storage_client = storage.Client.from_service_account_json(KEY_PATH)
            storage_client.get_bucket(RAW_BUCKET_NAME)
            print(f"✅ CONNECTED to Raw Bucket: {RAW_BUCKET_NAME}")
            storage_client.get_bucket(PROCESSED_BUCKET_NAME)
            print(f"✅ CONNECTED to Processed Bucket: {PROCESSED_BUCKET_NAME}")
        else:
            print(f"❌ Key File Missing at: {KEY_PATH}")
    except Exception as e:
        logger.error("Storage connection failed")
    print("🚀 SYSTEM READY! Documentation at: http://127.0.0.1:8000/docs\n")

# =========================================================
# IMPORT AI MODULES (User's paths)
# =========================================================
try:
    from ai.backend_pipeline.etl_pipeline import AudioETL
    from ai.backend_pipeline.feature_extractor import generate_mel_spectrogram
except ImportError as e:
    print(f"⚠️ AI MODULE IMPORT ERROR: {e}. Check folder naming and __init__.py files.")

# =========================================================
# SECURITY & AUTHENTICATION
# =========================================================

# This tells Swagger: "Go to the /login endpoint to get a token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(MY_TIMEZONE) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub")

        # Check Database
        conn = get_db_connection()
        if not conn:
             raise HTTPException(status_code=503, detail="Database Unavailable")
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, email FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        conn.close()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# =========================================================
# BACKGROUND PIPELINE (Merged logic)
# =========================================================
def run_audio_processing_pipeline(file_path: str, user_id: str):
    """Handles ETL, Feature Extraction, and Database Updating in the background."""
    print(f"🔄 ETL: Starting background pipeline for user {user_id}...")
    directory = os.path.dirname(file_path)
    original_filename = os.path.basename(file_path)
    filename_stem = os.path.splitext(original_filename)[0]
    clean_path = os.path.join(directory, f"cleaned_{original_filename}")

    try:
        if 'AudioETL' in globals():
            etl_engine = AudioETL()
            if etl_engine.run_pipeline(file_path, clean_path):
                generate_mel_spectrogram(clean_path, directory, filename_stem)
                
                # Cloud Uploads
                print("🚀 Starting Processed Bucket Uploads...")
                proc_path = upload_to_gcs(clean_path, f"processed/{user_id}/cleaned_{original_filename}", PROCESSED_BUCKET_NAME)
                spec_path = upload_to_gcs(os.path.join(directory, f"{filename_stem}.png"), f"spectrograms/{user_id}/{filename_stem}.png", PROCESSED_BUCKET_NAME)
                
                # Update DB with GCS Paths
                conn = get_db_connection()
                if conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE voice_recordings SET processed_url = %s, spectrogram_url = %s WHERE file_path = %s",
                        (proc_path, spec_path, file_path)
                    )
                    conn.commit()
                    conn.close()
                    print(f"✅ AI SUCCESS: Database metadata updated for {user_id}")
    except Exception as e:
        logger.error("Background processing failed")

# =========================================================
# API ENDPOINTS
# =========================================================

@app.post("/register", tags=["Authentication"], status_code=201)
async def register_user(user_data: UserRegistrationContract):
    """User's JSON Contract with Teammate's Passlib Security"""
    conn = get_db_connection()
    if not conn: raise HTTPException(503, "Database connection failed")
    try:
        cur = conn.cursor()
        new_uuid = str(uuid4()) 
        hashed_pwd = pwd_context.hash(user_data.password)
        
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
        if conn: conn.close()

class SlimOAuth2Form:
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...)
    ):
        self.username = username
        self.password = password

@app.post("/login", tags=["Authentication"])
@limiter.limit("5/minute")
async def login(request: Request, form_data: SlimOAuth2Form = Depends()):
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=503, detail="Database connection failed")
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id, hashed_password FROM users WHERE username = %s", (form_data.username,))
        user = cur.fetchone()
        
        if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
            raise HTTPException(401, "Invalid credentials")
            
        token = create_access_token(data={"sub": user["user_id"]})
        return {"access_token": token, "token_type": "bearer"}
    finally:
        if conn: conn.close()

@app.post("/upload-audio", tags=["Diagnosis"], status_code=202)
@limiter.limit("10/minute")
async def upload_audio(
    request: Request,
    audioFormat: str = Form(...),
    timestamp: Optional[datetime] = Form(None), # Made optional just in case
    audio_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    
    # FORCE LOCAL TIME:
    # We ignore the 'Z' or offset from the frontend and just use your current local clock.
    actual_timestamp = datetime.now(MY_TIMEZONE)

    # 1. Validation
    ext = audio_file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid format '.{ext}'. Supported: {ALLOWED_AUDIO_EXTENSIONS}")

    file_id = str(uuid4())
    local_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")

    # 2. Secure local save
    try:
        file_size = 0

        async with aiofiles.open(local_path, "wb") as f:
            while chunk := await audio_file.read(1024 * 1024):
                file_size += len(chunk)

            if file_size > MAX_FILE_SIZE_BYTES:
                await f.close()
                os.remove(local_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB."
                )

            await f.write(chunk)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"File save failed: {str(e)}")

    # 3. FAIL-FAST SNR CHECK (Immediate Quality Gate)
    try:
        y, sr = librosa.load(local_path, sr=TARGET_SAMPLE_RATE)
        S = np.abs(librosa.stft(y))
        power = np.mean(S**2, axis=0)
        signal_p = np.mean(np.sort(power)[-int(len(power)*0.1):])
        noise_p = np.mean(np.sort(power)[:int(len(power)*0.1)]) + 1e-10
        
        snr = float(10 * np.log10(signal_p / noise_p))

        if snr < MIN_SNR_DB:
            os.remove(local_path) 
            raise HTTPException(status_code=400, detail=f"SNR too low ({round(snr, 2)}dB). Please record in a quieter area.")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Audio Quality Analysis Failed")

    # 4. GCS Upload & DB Persistence
    print(f"🚀 Uploading Original to Raw Bucket for user {current_user['username']}...")
    gcs_path = f"raw/{current_user['user_id']}/{file_id}.{ext}"
    upload_to_gcs(local_path, gcs_path, RAW_BUCKET_NAME)

    # 5. Database Entry (Permanent Storage)
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=503, detail="Database connection failed")
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO voice_recordings (user_id, file_path, audio_format, created_at, raw_url) VALUES (%s,%s,%s,%s,%s)",
            (current_user["user_id"], local_path, audioFormat, actual_timestamp, gcs_path)
        )
        conn.commit()
        print(f"✅ DB SUCCESS: Recording metadata saved.")
    except Exception as e:
        conn.rollback()
        logger.error("DB ERROR")
    finally:
        conn.close()

    background_tasks.add_task(run_audio_processing_pipeline, local_path, current_user["user_id"])
    
    return {
        "message": "Audio accepted. Processing started.",
        "file_id": file_id,
        "snr": float(round(snr, 2)),
        "status": "In-Progress"
    }

# =========================================================
# RESTORED ENDPOINTS
# =========================================================

@app.get("/get-diagnosis-result/{user_id}", response_model=DiagnosisResultContract, tags=["Diagnosis"])
async def get_result(user_id: str, current_user: dict = Depends(get_current_user)):
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
    return feedback_data

@app.get("/model-training-status/{modelId}", response_model=ModelTrainingStatusContract, tags=["System"])
async def get_model_status(modelId: str):
    return {
        "modelId": modelId,
        "trainingStatus": "Optimized",
        "accuracy": 0.945,
        "timestamp": datetime.now(MY_TIMEZONE)
    }

# =========================================================
# NEW ENDPOINTS
# =========================================================

@app.get("/my-recordings", tags=["User Data"])
async def get_my_recordings(current_user: dict = Depends(get_current_user)):
    """Fetches user recordings and generates secure 15-minute URLs for playback."""
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=503, detail="Database connection failed")
    cur = conn.cursor()
    cur.execute("SELECT * FROM voice_recordings WHERE user_id = %s ORDER BY created_at DESC", (current_user["user_id"],))
    rows = cur.fetchall()
    conn.close()

    for row in rows:
        if row.get('raw_url'): 
            row['raw_url'] = generate_secure_url(RAW_BUCKET_NAME, row['raw_url'])
        if row.get('processed_url'): 
            row['processed_url'] = generate_secure_url(PROCESSED_BUCKET_NAME, row['processed_url'])
        if row.get('spectrogram_url'): 
            row['spectrogram_url'] = generate_secure_url(PROCESSED_BUCKET_NAME, row['spectrogram_url'])
            
    return rows