from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from uuid import uuid4
import os
from typing import List

app = FastAPI()

# Define the AudioData model (contract)
class AudioData(BaseModel):
    userId: str
    audioFormat: str
    timestamp: str

# Directory for uploads
UPLOAD_DIR = "uploads/"

# Ensure the uploads directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Endpoint to upload audio files
@app.post("/upload-audio", response_model=AudioData)
async def upload_audio(audio_data: AudioData, audio_file: UploadFile = File(...)):
    file_name = f"{uuid4()}.{audio_data.audioFormat}"  # Unique file name based on UUID
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(await audio_file.read())
    
    # Generating a URL for the uploaded file
    file_url = f"/uploads/{file_name}"
    return {"status": "success", "diagnosisResultId": str(uuid4()), "fileUrl": file_url}

# Endpoint to get the diagnosis result for a user
class DiagnosisResultContract(BaseModel):
    userId: str
    probability: float  # Probability score, e.g., 0.85 means 85% confidence
    diagnosis: str  # Diagnosis result, e.g., "Parkinson’s detected" or "No Parkinson's detected"
    timestamp: str  # Timestamp when the result was generated

@app.get("/get-diagnosis-result/{userId}", response_model=DiagnosisResultContract)
async def get_diagnosis_result(userId: str):
    return {"status": "success", "result": {"probability": 85.0, "diagnosis": "Parkinson’s detected", "timestamp": "2026-01-17T10:00:00"}}

# Endpoint to serve uploaded files via HTTP
@app.get("/uploads/{file_name}")
async def get_uploaded_file(file_name: str):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

# Define the User Registration model (contract)
class UserRegistrationContract(BaseModel):
    username: str
    email: str
    password: str  # Store hashed passwords in a real application

# Define the User Login model (contract)
class UserLoginContract(BaseModel):
    username: str
    password: str

# Define the Diagnosis History model (contract)
class DiagnosisHistoryContract(BaseModel):
    userId: str
    diagnosisHistory: List[DiagnosisResultContract]  # List of past diagnosis results

# Define the Real-Time Feedback model (contract)
class RealTimeFeedbackContract(BaseModel):
    userId: str
    feedback: str  # Describes feedback, e.g., "Speak louder", "Adjust pitch", etc.
    timestamp: str  # Timestamp when the feedback was generated

# Define the Model Training Status model (contract)
class ModelTrainingStatusContract(BaseModel):
    modelId: str
    trainingStatus: str  # E.g., "Training", "Completed", "Failed"
    accuracy: float  # Accuracy metric after training
    timestamp: str  # Timestamp when the training completed or failed

# Define the Admin Diagnosis Review model (contract)
class AdminDiagnosisReviewContract(BaseModel):
    adminId: str
    userId: str  # Admin who is reviewing the diagnosis and the user being reviewed

# Add a test endpoint to ensure the models are showing in Swagger UI
@app.post("/test-user-registration", response_model=UserRegistrationContract)
async def register_user(user_data: UserRegistrationContract):
    return {"status": "success", "user": user_data}
