import torch
from PIL import Image
from torchvision import transforms
from ai.train_and_extract import DeepRiskClassifier, extract_clinical_metrics
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

# Structured Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MY_TIMEZONE = ZoneInfo("Asia/Kuala_Lumpur") # UTC+8

# --- ADDED: AUTOMATIC HARDWARE DETECTION ---
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"🖥️ Hardware Acceleration: {DEVICE}")
# --------------------------------------------

app = FastAPI(
    title="SpeakTrum – Secure Healthcare API",
    description="AI-powered pipeline for Parkinson's Disease risk detection via voice biomarkers.",
    version="1.0.0",
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

# Global AI Model Variable (Step 1)
AI_MODEL = None

# =========================================================
# IMPORT AI MODULES (User's paths)
# =========================================================
try:
    from ai.backend_pipeline.etl_pipeline import AudioETL
    from ai.backend_pipeline.feature_extractor import generate_mel_spectrogram
except ImportError as e:
    logger.error(f"⚠️ AI MODULE IMPORT ERROR: {e}. Check folder naming and __init__.py files.")

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
        logger.error("Signed URL Error: {e}")
        return None

def upload_to_gcs(local_file_path, destination_blob_name, bucket_name):
    try:
        if not os.path.exists(KEY_PATH):
            logger.warning(f"⚠️ SKIPPING GCS: Key not found at {KEY_PATH}")
            return None
        storage_client = storage.Client.from_service_account_json(KEY_PATH)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)
        logger.info(f"☁️ UPLOADED to {bucket_name}: {destination_blob_name}")
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
    username: str = Field(..., alias="Patient_Name") # Maps DB "Patient_Name" to "username"
    probability: float
    diagnosis: str
    audio_source: str # Added this
    jitter_level: float = Field(default=0.0)
    shimmer_level: float = Field(default=0.0)
    hnr_level: float = Field(default=0.0)
    created_at: datetime

    class Config:
        populate_by_name = True # Allows us to use the alias in the response

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
# STARTUP CHECKS & MODEL LOADING
# =========================================================
@app.on_event("startup")
async def startup_event():
    global AI_MODEL
    logger.info("\n🔍 STARTING SYSTEM CHECKS...")
    conn = get_db_connection()
    if conn:
        logger.info("✅ CONNECTED to Google Cloud SQL!")
        conn.close()
    else:
        logger.error("❌ Database Connection Failed (Check IP Whitelist)")

    try:
        if os.path.exists(KEY_PATH):
            storage_client = storage.Client.from_service_account_json(KEY_PATH)
            storage_client.get_bucket(RAW_BUCKET_NAME)
            logger.info(f"✅ CONNECTED to Raw Bucket: {RAW_BUCKET_NAME}")
            storage_client.get_bucket(PROCESSED_BUCKET_NAME)
            logger.info(f"✅ CONNECTED to Processed Bucket: {PROCESSED_BUCKET_NAME}")
        else:
            logger.error(f"❌ Key File Missing at: {KEY_PATH}")
    except Exception as e:
        logger.error("Storage connection failed: {e}")

    # Step 1: Load Model Once into Memory
    logger.info("🧠 Loading AI Model into memory...")
    model_path = "parkinsons_high_acc_model.pth"
    if os.path.exists(model_path):
        AI_MODEL = DeepRiskClassifier().to(DEVICE)
        AI_MODEL.load_state_dict(torch.load(model_path, map_location=DEVICE))
        AI_MODEL.eval()

        # --- THE WARM-UP LOGIC ---
        dummy_input = torch.randn(1, 1, 128, 128).to(DEVICE)
        with torch.no_grad():
            _ = AI_MODEL(dummy_input)
        logger.info("✅ AI Model ready.")
    else:
        logger.error(f"❌ PIPELINE ABORTED: AI Model file '{model_path}' not found!")
    
    logger.info("🚀 SYSTEM READY! Documentation at: http://127.0.0.1:8000/docs\n")

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
def run_audio_processing_pipeline(file_path: str, user_id: str, username: str):
    """Handles ETL, Feature Extraction, and Database Updating in the background."""
    logger.info(f"🔄 PIPELINE: Starting for user {username} ({user_id})...")
    
    directory = os.path.dirname(file_path)
    original_filename = os.path.basename(file_path)
    filename_stem = os.path.splitext(original_filename)[0]
    clean_path = os.path.join(directory, f"cleaned_{original_filename}")
    spec_local_path = os.path.join(directory, f"{filename_stem}.png")

    # Open Connection Once
    conn = get_db_connection()
    if not conn:
        logger.error("❌ PIPELINE ABORTED: Could not connect to Database.")
        return
    cur = conn.cursor() if conn else None

    try:
        # 1. Check if AI Modules loaded properly
        if 'AudioETL' not in globals():
            logger.error("❌ PIPELINE ABORTED: 'AudioETL' was never imported. Check the top of your file.")
            return

        etl_engine = AudioETL()
        logger.info("⏳ Step 1: Running ETL Pipeline (Cleaning Audio)...")
        
        # 2. Check if Audio cleaning succeeds
        if not etl_engine.run_pipeline(file_path, clean_path):
            logger.warning("❌ PIPELINE ABORTED: etl_engine.run_pipeline returned False. Audio rejected.")
            if cur:
                cur.execute(
                    """INSERT INTO parkinsons_results 
                    (patient_uuid, patient_name, diagnosis_timestamp, ai_assessed_risk, parkinsons_probability, audio_source) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (user_id, username, datetime.now(MY_TIMEZONE), "Invalid Audio - Rejected", 0.0, original_filename)
                )
                conn.commit()
            return

        # 3. Generate Spectrogram
        logger.info("⏳ Step 2: Generating Spectrogram...")
        generate_mel_spectrogram(clean_path, directory, filename_stem)
        
        # 4. Extract Biomarkers
        logger.info("⏳ Step 3: Extracting Clinical Biomarkers...")
        clinical = extract_clinical_metrics(clean_path)

        # 5. Check if Model File Exists before loading
        if AI_MODEL is None:
            logger.error("❌ PIPELINE ABORTED: AI Model file 'parkinsons_high_acc_model.pth' not found in root directory!")
            return

        logger.info("⏳ Step 4 & 5: Running AI Inference...")
        preprocess = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
        ])
        img = Image.open(spec_local_path).convert("L")
        img_tensor = preprocess(img).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            output = AI_MODEL(img_tensor)
            prob_pd = torch.nn.functional.softmax(output, dim=1)[0][1].item()
        
        risk = "High" if prob_pd > 0.8 else "Medium" if prob_pd > 0.4 else "Low"
        logger.info(f"✅ AI Result: {risk} Risk (Prob: {round(prob_pd, 4)})")

        # 6. Cloud Uploads
        logger.info("⏳ Step 6: Uploading processed files to GCS...")
        proc_path = upload_to_gcs(clean_path, f"processed/{user_id}/cleaned_{original_filename}", PROCESSED_BUCKET_NAME)
        spec_path = upload_to_gcs(spec_local_path, f"spectrograms/{user_id}/{filename_stem}.png", PROCESSED_BUCKET_NAME)
        
        # 7. Database Update
        logger.info("⏳ Step 7: Saving Results to Database...")
        conn = get_db_connection()
        if not conn:
            logger.error("❌ PIPELINE ABORTED: Could not connect to Database inside background task.")
            return
            
        try:
            cur = conn.cursor()

            print(f"DEBUG: I am connected to: {conn.get_dsn_parameters().get('dbname')} at {conn.get_dsn_parameters().get('host')}")
            
            # A. Update voice_recordings
            cur.execute(
                "UPDATE voice_recordings SET processed_url = %s, spectrogram_url = %s WHERE file_path = %s",
                (proc_path, spec_path, file_path)
            )

            # B. Insert into parkinsons_results
            cur.execute(
                """INSERT INTO "parkinsons_results" 
                ("Patient_UUID", "Patient_Name", "Diagnosis_Timestamp", "AI_Assessed_Risk", "Parkinsons_Probability", 
                 "Jitter_Level", "Shimmer_Level", "HNR_Level", "Audio_Source") 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    user_id, 
                    username,
                    datetime.now(MY_TIMEZONE), 
                    risk, 
                    round(float(prob_pd), 4), 
                    clinical["jitter"], 
                    clinical["shimmer"], 
                    clinical["hnr"], 
                    original_filename
                )
            )

            conn.commit()
            logger.info(f"🎉 SUCCESS: Full diagnosis results officially saved to DB for {user_id}, {username}!")

        except Exception as db_error:
            # Handles errors specifically within the database update steps
            if conn: conn.rollback()
            logger.error(f"❌ SQL ERROR in Background Task: {str(db_error)}")
            raise db_error # Pass it to the outer block to inform the UI

    except Exception as e:
        # This catches EVERY error in the pipeline
        logger.error(f"❌ CRITICAL PIPELINE CRASH: {str(e)}")
        if conn: 
            conn.rollback()
            try:
            # We insert a row so the "Status Check" endpoint sees an error instead of "processing" forever & this "tells" the Flutter app that the analysis failed
                cur.execute(
                    """INSERT INTO "parkinsons_results" ("Patient_UUID", "Patient_Name", "Audio_Source", "AI_Assessed_Risk", "Diagnosis_Timestamp") 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (user_id, username, original_filename, "Error: Analysis Failed", datetime.now(MY_TIMEZONE))
                )
                conn.commit()
            except Exception as db_e:
                logger.error(f"Double Fault: Could not even save error to DB: {db_e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

        # Step 2: Digital Janitor (Clean local files)
        for path in [file_path, clean_path, spec_local_path]:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"🗑️ Cleaned up local file: {path}")

# =========================================================
# API ENDPOINTS
# =========================================================

@app.post("/register", summary="Register a new patient", tags=["Authentication"], status_code=201)
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
        logger.info(f"👤 NEW USER: {user_data.username} registered with ID {new_uuid}")
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

@app.post("/login", summary="Login to get JWT Token", tags=["Authentication"])
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

@app.post("/upload-audio", summary="Analyze Voice for Parkinson's", description="Uploads raw audio, runs the AI pipeline, and saves metrics.", tags=["Diagnosis"], status_code=202)
@limiter.limit("10/minute")
async def upload_audio(
    request: Request,
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

                # Check size before writing to disk
                if file_size > MAX_FILE_SIZE_BYTES:
                    # 'async with' will close the file automatically here
                    os.remove(local_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB."
                    )

                # SUCCESS: Write this specific chunk to the file
                await f.write(chunk)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ File save failed: {str(e)}") # Log the actual error
        raise HTTPException(status_code=500, detail="Internal server error during file save.")

    # 3. FAIL-FAST SNR CHECK (Immediate Quality Gate)
    try:
        y, sr = librosa.load(local_path, sr=TARGET_SAMPLE_RATE)
        
        # --- NEW: Get Duration ---
        duration = float(librosa.get_duration(y=y, sr=sr))
        # -------------------------
        
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
    logger.info(f"🚀 Uploading Original to Raw Bucket for user {current_user['username']}...")
    gcs_path = f"raw/{current_user['user_id']}/{file_id}.{ext}"
    upload_to_gcs(local_path, gcs_path, RAW_BUCKET_NAME)

    # 5. Database Entry (Permanent Storage)
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=503, detail="Database connection failed")
    try:
        cur = conn.cursor()
        # Added duration_seconds to the column list and the %s values
        cur.execute(
            "INSERT INTO voice_recordings (user_id, file_path, audio_format, duration_seconds, created_at, raw_url) VALUES (%s,%s,%s,%s,%s,%s)",
            (current_user["user_id"], local_path, ext, duration, actual_timestamp, gcs_path)
        )
        conn.commit()
        logger.info(f"✅ DB SUCCESS: Recording metadata saved with duration: {round(duration, 2)}s")
    except Exception as e:
        conn.rollback()
        logger.error(f"DB ERROR: {str(e)}")
        raise HTTPException(500, detail=f"Failed to save metadata to database: {str(e)}")
    finally:
        conn.close()

    # Pass both the ID and the Username to the pipeline
    background_tasks.add_task(
        run_audio_processing_pipeline, 
        local_path, 
        current_user["user_id"], 
        current_user["username"]
)
    
    return {
        "message": "Audio accepted. Processing started.",
        "file_id": file_id,
        "snr": float(round(snr, 2)),
        "duration": float(round(duration, 2)),
        "status": "In-Progress"
    }

# =========================================================
# RESTORED ENDPOINTS
# =========================================================

@app.get("/diagnosis-status/{file_id}", summary="Check if AI analysis is finished", tags=["Diagnosis"])
async def check_status(file_id: str, current_user: dict = Depends(get_current_user)):
    """
    Poll this endpoint using the file_id received from /upload-audio.
    Returns 'completed' if the AI results are in the DB, otherwise 'processing'.
    """
    conn = get_db_connection()
    if not conn: 
        raise HTTPException(status_code=503, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        
        # We use LIKE f"{file_id}%" because the DB column 'Audio_Source' 
        # contains the full filename (e.g., 'uuid.wav')
        search_pattern = f"{file_id}%" 

        cur.execute("""
            SELECT "AI_Assessed_Risk", "Parkinsons_Probability" 
            FROM "parkinsons_results" 
            WHERE "Patient_UUID" = %s AND "Audio_Source" LIKE %s
        """, (current_user["user_id"], search_pattern))
        
        result = cur.fetchone()

        if result:
            return {
                "status": "completed",
                "risk": result["AI_Assessed_Risk"],
                "probability": result["Parkinsons_Probability"]
            }
        
        # If no record is found yet, the background task is still running
        return {"status": "processing"}

    except Exception as e:
        logger.error(f"❌ Status Check Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking diagnosis status")
    
    finally:
        # This block ALWAYS runs, even if the code above crashes
        cur.close()
        conn.close()

@app.get("/get-diagnosis-result/{user_id}",summary="Fetch latest diagnosis result", response_model=DiagnosisResultContract, tags=["Diagnosis"])
async def get_result(user_id: str, current_user: dict = Depends(get_current_user)):
    if user_id != current_user["user_id"]:
        raise HTTPException(403, "Unauthorized to view this data")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # FIX
    cur.execute("""
        SELECT 
            "Patient_UUID" as user_id,
            "Patient_Name",
            "Parkinsons_Probability" as probability,
            "AI_Assessed_Risk" as diagnosis,
            "Audio_Source" as audio_source,
            "Jitter_Level" as jitter_level,
            "Shimmer_Level" as shimmer_level,
            "HNR_Level" as hnr_level,
            "Diagnosis_Timestamp" as created_at
        FROM "parkinsons_results" 
        WHERE "Patient_UUID" = %s 
        ORDER BY "Diagnosis_Timestamp" DESC LIMIT 1
    """, (user_id,))
    
    result = cur.fetchone()
    conn.close()
    
    if not result: raise HTTPException(404, "No diagnosis found yet.")
    return result

@app.get("/diagnosis-history/{user_id}", summary="Fetch diagnosis history", response_model=DiagnosisHistoryContract, tags=["User Data"])
async def get_history(user_id: str, current_user: dict = Depends(get_current_user)):
    if user_id != current_user["user_id"]: raise HTTPException(403, "Access denied")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # FIX
    cur.execute("""
        SELECT 
            "Patient_UUID" as user_id,
            "Patient_Name",
            "Parkinsons_Probability" as probability,
            "AI_Assessed_Risk" as diagnosis,
            "Audio_Source" as audio_source,
            "Jitter_Level" as jitter_level,
            "Shimmer_Level" as shimmer_level,
            "HNR_Level" as hnr_level,
            "Diagnosis_Timestamp" as created_at
        FROM parkinsons_results 
        WHERE "Patient_UUID" = %s
        ORDER BY "Diagnosis_Timestamp" DESC
    """, (user_id,))
    
    history = cur.fetchall()
    conn.close()
    return {"user_id": user_id, "diagnosisHistory": history}


# =========================================================
# NEW ENDPOINTS
# =========================================================

@app.get("/my-recordings",summary="Get secure playback URLs", tags=["User Data"])
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

@app.post("/real-time-feedback", summary="Submit patient feedback", tags=["Feedback"])
async def submit_feedback(feedback_data: RealTimeFeedbackContract, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO user_feedback (user_id, feedback_text, submitted_at) 
               VALUES (%s, %s, %s) RETURNING feedback_id""",
            (current_user["user_id"], feedback_data.feedback, datetime.now(MY_TIMEZONE))
        )
        conn.commit()
        logger.info(f"📝 FEEDBACK RECEIVED from {current_user['username']}")
        
        # Return the data back with the user's ID to confirm success
        return {
            "user_id": current_user["user_id"],
            "feedback": feedback_data.feedback,
            "timestamp": datetime.now(MY_TIMEZONE)
        }
    except Exception as e:
        conn.rollback()
        logger.error(f"Feedback Save Error: {e}")
        raise HTTPException(500, "Failed to save feedback")
    finally:
        conn.close()

@app.get("/model-training-status/{modelId}", summary="Check AI Model Status", response_model=ModelTrainingStatusContract, tags=["System"])
async def get_model_status(modelId: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT model_id, training_status, accuracy, deployed_at FROM model_registry WHERE model_id = %s",
            (modelId,)
        )
        row = cur.fetchone()
        
        if not row:
            raise HTTPException(404, detail=f"Model ID '{modelId}' not found in registry.")

        return {
            "modelId": row["model_id"],
            "trainingStatus": row["training_status"],
            "accuracy": row["accuracy"],
            "timestamp": row["deployed_at"]
        }
    finally:
        conn.close()
