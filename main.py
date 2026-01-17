from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from uuid import uuid4
from datetime import datetime
import os
import shutil

app = FastAPI()

UPLOAD_DIR = "uploads/"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/upload-audio")
async def upload_audio(
    userId: int = Form(...),
    # NO audioFormat box here. The code handles it!
    timestamp: datetime = Form(...),
    audio_file: UploadFile = File(...)
):
    # 1. SECURITY GUARD: Check if the file is actually a WAV
    if audio_file.content_type not in ["audio/wav", "audio/x-wav"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file! Only WAV files are allowed."
        )

    # 2. AUTOMATIC NAMING: We know it's a WAV, so we force the extension
    file_name = f"{uuid4()}.wav"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    return {
        "status": "success", 
        "diagnosisResultId": str(uuid4()),
        "saved_as": file_name,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M"),
        "message": "WAV file detected and saved successfully"
    }

@app.get("/get-diagnosis-result/{userId}")
async def get_diagnosis_result(userId: int):
    return {
        "status": "success", 
        "result": {
            "userId": userId,
            "probability": 85.0, 
            "diagnosis": "Parkinson’s detected"
        }
    }