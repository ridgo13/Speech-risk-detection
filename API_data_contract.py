from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from uuid import uuid4
import os
from typing import List

app = FastAPI(title="Speech Risk Detection API")

# --- DIRECTORY SETUP ---
UPLOAD_DIR = "uploads/"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- MODELS (CONTRACTS) ---
class AudioData(BaseModel):
    userId: str
    audioFormat: str
    timestamp: str

class DiagnosisResultContract(BaseModel):
    userId: str
    probability: float
    diagnosis: str
    timestamp: str

class UserRegistrationContract(BaseModel):
    username: str
    email: str
    password: str

class UserLoginContract(BaseModel):
    username: str
    password: str

class DiagnosisHistoryContract(BaseModel):
    userId: str
    diagnosisHistory: List[DiagnosisResultContract]

class RealTimeFeedbackContract(BaseModel):
    userId: str
    feedback: str
    timestamp: str

class ModelTrainingStatusContract(BaseModel):
    modelId: str
    trainingStatus: str
    accuracy: float
    timestamp: str

class AdminDiagnosisReviewContract(BaseModel):
    adminId: str
    userId: str

# --- ENDPOINTS ---

# 1. Authentication
@app.post("/test-user-registration", response_model=UserRegistrationContract, tags=["Authentication"])
async def register_user(user_data: UserRegistrationContract):
    return user_data

@app.post("/login", response_model=UserLoginContract, tags=["Authentication"])
async def login_user(credentials: UserLoginContract):
    return credentials

# 2. Audio & Diagnosis
@app.post("/upload-audio", response_model=AudioData, tags=["Diagnosis"])
async def upload_audio(audio_data: AudioData, audio_file: UploadFile = File(...)):
    file_name = f"{uuid4()}.{audio_data.audioFormat}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(await audio_file.read())
    return audio_data

@app.get("/get-diagnosis-result/{userId}", response_model=DiagnosisResultContract, tags=["Diagnosis"])
async def get_diagnosis_result(userId: str):
    return {"userId": userId, "probability": 85.0, "diagnosis": "Parkinson’s detected", "timestamp": "2026-01-17T10:00:00"}

@app.get("/diagnosis-history/{userId}", response_model=DiagnosisHistoryContract, tags=["User Data"])
async def get_diagnosis_history(userId: str):
    return {
        "userId": userId,
        "diagnosisHistory": [
            {"userId": userId, "probability": 85.0, "diagnosis": "Parkinson’s detected", "timestamp": "2026-01-17T10:00:00"}
        ]
    }

# 3. System & Admin
@app.get("/uploads/{file_name}", tags=["System"])
async def get_uploaded_file(file_name: str):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

@app.get("/model-training-status/{modelId}", response_model=ModelTrainingStatusContract, tags=["System"])
async def get_model_status(modelId: str):
    return {"modelId": modelId, "trainingStatus": "Completed", "accuracy": 0.92, "timestamp": "2026-01-17T12:00:00"}

@app.post("/admin/review-diagnosis", response_model=AdminDiagnosisReviewContract, tags=["Admin"])
async def review_diagnosis(review: AdminDiagnosisReviewContract):
    return review

@app.post("/real-time-feedback", response_model=RealTimeFeedbackContract, tags=["Feedback"])
async def real_time_feedback(feedback: RealTimeFeedbackContract):
    return feedback

# Startup Message
@app.on_event("startup")
async def startup_event():
    print("\n🚀 Server started successfully!")
    print("📂 Swagger UI: http://127.0.0.1:8000/docs\n")