from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
import uuid
from datetime import datetime
import os
from pathlib import Path
import tempfile

from models.entry import (
    LectureBase,
    LectureUpdate,
    LectureSummary,
    Question,
    LectureResponse,
)
from database import lectures_collection
from services.gemini import process_audio

router = APIRouter()

@router.post("/startLecture", response_model=LectureResponse)
async def start_lecture(snap_user_id: str):
    lecture_id = str(uuid.uuid4())
    lecture = LectureBase(
        snap_user_id=snap_user_id,
        lecture_id=lecture_id,
    )
    await lectures_collection.insert_one(lecture.dict())
    return LectureResponse(lecture_id=lecture_id)

@router.patch("/updateInfo")
async def update_info(
    snap_user_id: str,
    lecture_id: str,
    audio: Optional[UploadFile] = File(None, description="Audio file in WAV format"),
    image: Optional[UploadFile] = File(None)
):
    try:
        lecture = await lectures_collection.find_one({
            "snap_user_id": snap_user_id,
            "lecture_id": lecture_id,
            "is_active": True
        })
        
        if not lecture:
            raise HTTPException(status_code=404, detail="Active lecture not found")
        
        update_data = {}
        if audio:
            # print(f"Audio received: {audio.filename}, size: {audio.size}, content_type: {audio.content_type}")
            if not audio.filename.lower().endswith('.wav'):
                raise HTTPException(status_code=400, detail="Audio file must be in WAV format")
            
            # Create a temporary file with .wav extension
            
            
            # Process audio with Gemini
            try:
                transcript = await process_audio(audio)
                #print(f"Transcript result: {transcript[:100]}...")  # Print first 100 chars
                
                # Only save transcript if it doesn't contain an error message
                if not transcript.startswith("Error:"):
                    update_data["transcript"] = transcript
            except Exception as e:
                print(f"Gemini processing error: {str(e)}")
        
        if image:
            image_content = await image.read()
            # In a real implementation, you'd want to store this in a proper storage service
            update_data["image_data"] = image_content
        
        if update_data:
            await lectures_collection.update_one(
                {"lecture_id": lecture_id},
                {"$set": update_data}
            )
        
        return {"status": "updated"}
    except Exception as e:
        print(f"Error in updateInfo: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/requestSummary", response_model=LectureSummary)
async def request_summary(snap_user_id: str, lecture_id: str):
    lecture = await lectures_collection.find_one({
        "snap_user_id": snap_user_id,
        "lecture_id": lecture_id
    })
    
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    # In a real implementation, you'd process the actual audio/transcript
    # Here we're just using a placeholder
    # summary = await generate_summary("Sample transcript")
    return LectureSummary(text="summary", slides=[])

@router.get("/requestQuestions")
async def request_questions(snap_user_id: str, lecture_id: str):
    lecture = await lectures_collection.find_one({
        "snap_user_id": snap_user_id,
        "lecture_id": lecture_id
    })
    
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    # In a real implementation, you'd process the actual lecture content
    # questions = await generate_questions("Sample transcript")
    return [
        Question(question=q, pre_searched_answer=a)
        for q, a in []
    ]

@router.post("/endLecture")
async def end_lecture(snap_user_id: str):
    result = await lectures_collection.update_one(
        {
            "snap_user_id": snap_user_id,
            "is_active": True
        },
        {
            "$set": {
                "is_active": False,
                "end_time": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No active lecture found")
    
    return {"status": "ended"}

# @router.post("/debug/upload")
# async def debug_upload(
#     test_param: str,
#     audio: Optional[UploadFile] = File(None)
# ):
#     try:
#         result = {
#             "test_param": test_param,
#             "audio_received": False
#         }
        
#         if audio:
#             result["audio_received"] = True
#             result["audio_filename"] = audio.filename
#             result["audio_content_type"] = audio.content_type
#             audio_content = await audio.read()
#             result["audio_size"] = len(audio_content)
            
#             # Test audio transcription
#             try:
#                 print("Attempting to transcribe audio...")
#                 transcript = await process_audio(audio_content)
#                 print(f"Transcript result: {transcript[:100]}...")
#                 result["transcript"] = transcript
#                 result["transcription_success"] = not transcript.startswith("Error:")
#             except Exception as e:
#                 result["transcription_error"] = str(e)
        
#         return result
#     except Exception as e:
#         print(f"Debug upload error: {str(e)}")
#         import traceback
#         print(traceback.format_exc())
#         return {"error": str(e)} 