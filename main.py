# -*- coding: utf-8 -*-
import os
import uuid
import aiofiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mastering API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
RESULT_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Mastering API is running"}


@app.post("/process")
async def process_audio(
    target: UploadFile = File(...),
    reference: UploadFile = File(...)
):
    """Process audio with matchering"""
    
    # Generate unique IDs for files
    job_id = str(uuid.uuid4())[:8]
    
    # Save uploaded files
    target_path = os.path.join(UPLOAD_DIR, f"{job_id}_target.{target.filename.split('.')[-1]}")
    ref_path = os.path.join(UPLOAD_DIR, f"{job_id}_reference.{reference.filename.split('.')[-1]}")
    
    async with aiofiles.open(target_path, 'wb') as f:
        content = await target.read()
        await f.write(content)
    
    async with aiofiles.open(ref_path, 'wb') as f:
        content = await reference.read()
        await f.write(content)
    
    # Import matchering here to avoid import issues
    import matchering as mg
    
    # Configure results
    result_path = os.path.join(RESULT_DIR, f"{job_id}_mastered.wav")
    
    try:
        import matchering as mg
        mg.log(print)
        
        mg.process(
            target=target_path,
            reference=ref_path,
            results=[mg.pcm24(result_path)]
        )
        
        if not os.path.exists(result_path):
            raise HTTPException(status_code=500, detail="Processing failed - no output file")
        
        return FileResponse(
            result_path,
            media_type="audio/wav",
            filename=f"mastered_{target.filename}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)