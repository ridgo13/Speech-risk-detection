from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, status
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

# =========================================================
# CONFIGURATION & ENVIRONMENT
# =========================================================
load_dotenv()  # This loads the variables from your .env file

app = FastAPI(title="SpeakTrum – Speech Risk Detection API")

# These now pull from the .env file for better security
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_for_development_only")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
ALLOWED_AUDIO_EXTENSIONS = {"wav", "mp3", "m4a", "flac"}

os.makedirs(UPLOAD_DIR, exist_ok=True)

# =========================================================
# SECURITY SETUP
# =========================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# In-memory mock DB (Will be replaced with PostgreSQL/SQLite later)
USERS_DB = {}
DIAGNOSIS_RESULTS_DB = {}   # user_id -> list of diagnosis results               
FILES_DB = {}               # file_name -> user_id (ownership)

# =========================================================
# UTILITY FUNCTIONS (DATABASE & AUTH)
# =========================================================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id not in USERS_DB:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return USERS_DB[user_id]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# =========================================================
# DATA CONTRACTS
# =========================================================
class AudioData(BaseModel):
    audioFormat: str
    timestamp: datetime

class DiagnosisResultContract(BaseModel):
    userId: str
    probability: float
    diagnosis: str
    timestamp: datetime

class UserRegistrationContract(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6)

class DiagnosisHistoryContract(BaseModel):
    userId: str
    diagnosisHistory: List[DiagnosisResultContract]

class RealTimeFeedbackContract(BaseModel):
    userId: str
    feedback: str
    timestamp: datetime

class ModelTrainingStatusContract(BaseModel):
    modelId: str
    trainingStatus: str
    accuracy: float
    timestamp: datetime

class AdminDiagnosisReviewContract(BaseModel):
    adminId: str
    userId: str

# =========================================================
# BACKGROUND TASK (AI PIPELINE)
# =========================================================
def mock_inference_pipeline(user_id: str):
    """
    This is where your future AI code (Librosa/Model) will live.
    It runs in the background so the user doesn't have to wait.
    """
    result = {
        "userId": user_id,
        "probability": 0.87,
        "diagnosis": "Parkinson’s risk detected",
        "timestamp": datetime.utcnow()
    }

    DIAGNOSIS_RESULTS_DB.setdefault(user_id, []).append(result)


# =========================================================
# AUTHENTICATION ENDPOINTS
# =========================================================
@app.post("/test-user-registration", tags=["Authentication"])
async def register_user(user_data: UserRegistrationContract):
    if user_data.username in USERS_DB:
        raise HTTPException(status_code=400, detail="User already exists")

    USERS_DB[user_data.username] = {
        "id": user_data.username,
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "role": "user"
    }
    return {"message": "User registered successfully"}

@app.post("/login", tags=["Authentication"])
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["id"]})
    return {"access_token": token, "token_type": "bearer"}

# =========================================================
# AUDIO UPLOAD & DIAGNOSIS
# =========================================================
@app.post("/upload-audio", tags=["Diagnosis"], status_code=202)
async def upload_audio(
    audio_data: AudioData,
    audio_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    # 1. Validate File Format
    ext = audio_file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    # 2. Secure Filename
    file_name = f"{uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    # 3. Synchronous File Save (Prevents background corruption)
    # We write the file IMMEDIATELY while the connection is still open
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await audio_file.read(1024 * 1024):
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    FILES_DB[file_name] = current_user["id"]

    # 4. Background AI Inference (Using verified current_user["id"] for security)
    background_tasks.add_task(mock_inference_pipeline, current_user["id"])

    return {
        "message": "Audio uploaded successfully. Analysis in progress.",
        "file_assigned": file_name,
        "verified_user": current_user["id"]
    }

@app.get("/get-diagnosis-result/{userId}", response_model=DiagnosisResultContract, tags=["Diagnosis"])
async def get_diagnosis_result(userId: str, current_user: dict = Depends(get_current_user)):
    # Security: Ensure users can only see their OWN result
    if userId != current_user["id"] and current_user.get("role") != "admin":
         raise HTTPException(status_code=403, detail="You can only view your own results")

    if userId not in DIAGNOSIS_RESULTS_DB:
        raise HTTPException(status_code=404, detail="Diagnosis not found yet. Please wait.")
    
    return DIAGNOSIS_RESULTS_DB[userId][-1]

@app.get("/diagnosis-history/{userId}", response_model=DiagnosisHistoryContract, tags=["User Data"])
async def get_diagnosis_history(userId: str, current_user: dict = Depends(get_current_user)):
    if userId != current_user["id"]:
         raise HTTPException(status_code=403, detail="Access denied")

    history = []
    if userId in DIAGNOSIS_RESULTS_DB:
        history.append(DIAGNOSIS_RESULTS_DB[userId])
    return {"userId": userId, "diagnosisHistory": history}

# =========================================================
# SYSTEM & ADMIN
# =========================================================
@app.get("/uploads/{file_name}", tags=["System"])
async def get_uploaded_file(file_name: str, current_user: dict = Depends(get_current_user)):
    if file_name not in FILES_DB or FILES_DB[file_name] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    

    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

@app.get("/model-training-status/{modelId}", response_model=ModelTrainingStatusContract, tags=["System"])
async def get_model_status(modelId: str):
    return {
        "modelId": modelId,
        "trainingStatus": "Completed",
        "accuracy": 0.92,
        "timestamp": datetime.utcnow()
    }

@app.post("/admin/review-diagnosis", response_model=AdminDiagnosisReviewContract, tags=["Admin"])
async def review_diagnosis(review: AdminDiagnosisReviewContract):
    return review

@app.post("/real-time-feedback", response_model=RealTimeFeedbackContract, tags=["Feedback"])
async def real_time_feedback(feedback: RealTimeFeedbackContract):
    return feedback

# =========================================================
# HEALTH CHECK
# =========================================================
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "OK", "time": datetime.utcnow()}

# =========================================================
# STARTUP EVENT
# =========================================================
@app.on_event("startup")
async def startup_event():
    print("\n🚀 SpeakTrum Backend Started Successfully")
    print("📘 Swagger UI: http://127.0.0.1:8000/docs\n")
    print("🏥 Health Check: http://127.0.0.1:8000/health\n")