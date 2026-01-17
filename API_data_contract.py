from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from uuid import uuid4
import os

app = FastAPI()

class AudioData(BaseModel):
    userId: str
    audioFormat: str
    timestamp: str

UPLOAD_DIR = "uploads/"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/upload-audio")
async def upload_audio(audio_data: AudioData, audio_file: UploadFile = File(...)):
    file_name = f"{uuid4()}.{audio_data.audioFormat}"  # Correcting the variable name here
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(await audio_file.read())
    
    # Generating a URL for the uploaded file
    file_url = f"/uploads/{file_name}"
    return {"status": "success", "diagnosisResultId": str(uuid4()), "fileUrl": file_url}

@app.get("/get-diagnosis-result/{userId}")
async def get_diagnosis_result(userId: str):
    return {"status": "success", "result": {"probability": 85.0, "diagnosis": "Parkinson’s detected"}}

# Serve uploaded files via HTTP
@app.get("/uploads/{file_name}")
async def get_uploaded_file(file_name: str):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}


