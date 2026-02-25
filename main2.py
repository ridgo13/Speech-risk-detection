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
import librosa
import numpy as np
from passlib.context import CryptContext
from psycopg2.extras import RealDictCursor
from google.cloud import storage
from sqlalchemy import create_engine

# =========================================================
# CONFIGURATION & ENVIRONMENT
# =========================================================
load_dotenv()

app = FastAPI(title="SpeakTrum – Secure Healthcare API")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# REPORT COMPLIANCE: Formats & Quality Thresholds
ALLOWED_AUDIO_EXTENSIONS = {"wav", "m4a"}
MIN_SNR_DB = 10 
TARGET_SAMPLE_RATE = 16000

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_for_development_only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Bucket Names & Key Path
RAW_BUCKET_NAME = "speaktrum-raw-audio"
PROCESSED_BUCKET_NAME = "speaktrum-processed-data"
KEY_PATH = "backend_scripts/service_account.json" 

# =========================================================
# CLOUD STORAGE HELPERS
# =========================================================

def upload_to_gcs(local_path, destination_blob_name, bucket_name):
    """Uploads a file to the specified Google Cloud Storage bucket."""
    try:
        storage_client = storage.Client.from_service_account_json(KEY_PATH)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_path)
        return destination_blob_name
    except Exception as e:
        print(f"❌ GCS Upload Error: {e}")
        return None

def generate_secure_url(bucket_name, blob_name):
    """Generates a signed URL for secure, temporary access to a file."""
    try:
        storage_client = storage.Client.from_service_account_json(KEY_PATH)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.generate_signed_url(expiration=timedelta(hours=1), method="GET")
    except Exception as e:
        print(f"❌ Signed URL Error: {e}")
        return None

# =========================================================
# DATABASE & SECURE HELPER FUNCTIONS (PUBLIC IP METHOD)
# =========================================================

# Construct standard connection string using Public IP from .env
# Double-check this in train_and_extract.py
DB_URL = "postgresql://postgres:qz*,2zZQ=4<6v4jY@127.0.0.1:5432/speaktrum_db"
# Create standard SQLAlchemy engine
engine = create_engine(DB_URL)

def get_db_connection():
    """Returns a raw connection using the Public IP logic."""
    try:
        connection = engine.raw_connection()
        connection.cursor_factory = RealDictCursor 
        return connection
    except Exception as e:
        print(f"⚠️ DB CONNECTION ERROR: {e}")
        return None

# =========================================================
# STARTUP CHECKS
# =========================================================
@app.on_event("startup")
async def startup_event():
    print("\n🔍 STARTING SYSTEM CHECKS...")
    
    # 1. Test Database Connection
    conn = get_db_connection()
    if conn:
        print("✅ CONNECTED to Google Cloud SQL via Public IP!")
        conn.close()
    else:
        print("❌ Database Connection Failed (Verify Whitelist & IP!)")

    # 2. Test Cloud Storage
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
        print(f"❌ Storage Connection Failed: {e}")
    
    print("🚀 SYSTEM READY!\n")

# =========================================================
# IMPORT AI MODULES
# =========================================================
try:
    from backend_scripts.etl_pipeline import AudioETL
    from backend_scripts.feature_extractor import generate_mel_spectrogram
except ImportError as e:
    print(f"⚠️ AI MODULE IMPORT ERROR: {e}")

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
        user_id: str = payload.get("sub")
        conn = get_db_connection()
        if not conn:
             raise HTTPException(status_code=503, detail="Database Unavailable")
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, email FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        conn.close()
        return user
    except:
        raise HTTPException(status_code=401, detail="Authentication failed")

# =========================================================
# BACKGROUND PIPELINE
# =========================================================
def run_audio_processing_pipeline(file_path: str, user_id: str):
    directory = os.path.dirname(file_path)
    original_filename = os.path.basename(file_path)
    filename_stem = os.path.splitext(original_filename)[0]
    clean_path = os.path.join(directory, f"cleaned_{original_filename}")

    try:
        if 'AudioETL' in globals():
            etl_engine = AudioETL()
            if etl_engine.run_pipeline(file_path, clean_path):
                generate_mel_spectrogram(clean_path, directory, filename_stem)
                
                # Upload processed audio and spectrogram
                proc_url = upload_to_gcs(clean_path, f"processed/{user_id}/cleaned_{original_filename}", PROCESSED_BUCKET_NAME)
                spec_url = upload_to_gcs(os.path.join(directory, f"{filename_stem}.png"), f"spectrograms/{user_id}/{filename_stem}.png", PROCESSED_BUCKET_NAME)
                
                conn = get_db_connection()
                if conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE voice_recordings SET processed_url = %s, spectrogram_url = %s WHERE file_path = %s",
                        (proc_url, spec_url, file_path)
                    )
                    conn.commit()
                    conn.close()
                    print(f"✅ AI SUCCESS: Data updated for {user_id}")
    except Exception as e:
        print(f"❌ ETL Error: {e}")

# =========================================================
# API ENDPOINTS
# =========================================================

@app.post("/register", tags=["Auth"])
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database connection failed")
    try:
        cur = conn.cursor()
        new_uuid = str(uuid4())
        hashed = pwd_context.hash(password)
        cur.execute("INSERT INTO users (user_id, username, email, hashed_password) VALUES (%s,%s,%s,%s)", 
                    (new_uuid, username, email, hashed))
        conn.commit()
        return {"user_id": new_uuid}
    finally:
        if conn: conn.close()

@app.post("/login", tags=["Auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database connection failed")
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id, hashed_password FROM users WHERE username = %s", (form_data.username,))
        user = cur.fetchone()
        if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
            raise HTTPException(401, "Invalid credentials")
        return {"access_token": create_access_token({"sub": user["user_id"]}), "token_type": "bearer"}
    finally:
        if conn: conn.close()

@app.post("/upload-audio", tags=["Main"])
async def upload_audio(
    audioFormat: str = Form(...),
    timestamp: datetime = Form(...),
    audio_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    ext = audio_file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(400, detail=f"Invalid format '.{ext}'. Use WAV/M4A.")

    file_id = str(uuid4())
    local_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")

    async with aiofiles.open(local_path, "wb") as f:
        while chunk := await audio_file.read(1024*1024):
            await f.write(chunk)

    # SNR Quality Check
    try:
        y, sr = librosa.load(local_path, sr=TARGET_SAMPLE_RATE)
        S = np.abs(librosa.stft(y))
        power = np.mean(S**2, axis=0)
        signal_p = np.mean(np.sort(power)[-int(len(power)*0.1):])
        noise_p = np.mean(np.sort(power)[:int(len(power)*0.1)]) + 1e-10
        snr = float(10 * np.log10(signal_p / noise_p))

        if snr < MIN_SNR_DB:
            os.remove(local_path)
            raise HTTPException(400, detail=f"SNR too low ({round(snr, 2)}dB). Record in a quieter area.")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(500, detail="Audio Quality Analysis Failed")

    # GCS Upload
    gcs_path = f"raw/{current_user['user_id']}/{file_id}.{ext}"
    upload_to_gcs(local_path, gcs_path, RAW_BUCKET_NAME)

    conn = get_db_connection()
    if not conn: raise HTTPException(503, detail="Database connection failed")
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO voice_recordings (user_id, file_path, audio_format, created_at, raw_url) VALUES (%s,%s,%s,%s,%s)",
            (current_user["user_id"], local_path, audioFormat, timestamp, gcs_path)
        )
        conn.commit()
    finally:
        conn.close()

    background_tasks.add_task(run_audio_processing_pipeline, local_path, current_user["user_id"])
    return {"status": "Accepted", "snr": float(round(snr, 2)), "file_id": file_id}

@app.get("/my-recordings", tags=["Main"])
async def get_my_recordings(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if not conn: raise HTTPException(503, detail="Database connection failed")
    cur = conn.cursor()
    cur.execute("SELECT * FROM voice_recordings WHERE user_id = %s", (current_user["user_id"],))
    rows = cur.fetchall()
    conn.close()

    for row in rows:
        if row.get('raw_url'): row['raw_url'] = generate_secure_url(RAW_BUCKET_NAME, row['raw_url'])
        if row.get('processed_url'): row['processed_url'] = generate_secure_url(PROCESSED_BUCKET_NAME, row['processed_url'])
        if row.get('spectrogram_url'): row['spectrogram_url'] = generate_secure_url(PROCESSED_BUCKET_NAME, row['spectrogram_url'])
    return rows