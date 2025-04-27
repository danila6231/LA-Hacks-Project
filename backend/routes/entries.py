from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional, List
import uuid
from datetime import datetime
import os
from pathlib import Path
import tempfile
import json
from config import MAX_RECENT_CHUNKS

from models.entry import (
    LectureBase,
    LectureUpdate,
    LectureSummary,
    Question,
    LectureResponse,
)
from database import lectures_collection
from services.gemini import process_image, process_audio, generate_summary, generate_questions, combine_transcripts
from shared_state import CAPTIONS_BUFFER

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
    image_url: Optional[str] = None
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
            
            # Store audio chunk
            audio_content = await audio.read()
            await audio.seek(0)  # Reset for transcription
            
            # Process audio with Gemini
            try:
                transcript = await process_audio(audio)
                
                if not transcript.startswith("Error:"):
                    # Update transcripts list
                    update_data["transcripts"] = lecture.get("transcripts", []) + [transcript]
                    
                    # Generate updated summary
                    new_summary = await generate_summary(transcript, lecture.get("ongoing_summary", ""))
                    update_data["ongoing_summary"] = new_summary
                    
                    # Update recent audio chunks (keep last 5)
                    recent_chunks = lecture.get("recent_audio_chunks", [])
                    recent_chunks.append(audio_content)
                    if len(recent_chunks) > MAX_RECENT_CHUNKS:  
                    # Keep only last 5 minutes
                        recent_chunks = recent_chunks[-MAX_RECENT_CHUNKS:]
                    update_data["recent_audio_chunks"] = recent_chunks
            except Exception as e:
                print(f"Gemini processing error: {str(e)}")
        
        if image_url:
            update_data["image_url"] = image_url
        
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
    
    return LectureSummary(
        text=lecture.get("ongoing_summary", "No summary available"),
        slides=[]  # TODO: Implement slide extraction if needed
    )

@router.get("/requestQuestions", response_model=List[Question])
async def request_questions(snap_user_id: str, lecture_id: str):
    lecture = await lectures_collection.find_one({
        "snap_user_id": snap_user_id,
        "lecture_id": lecture_id
    })
    
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    # Get the last 5 transcripts
    recent_transcripts = combine_transcripts(lecture.get("transcripts", [])[-5:])
    if not recent_transcripts:
        return []
    
    # Combine recent transcripts
    combined_transcript = "\n".join(recent_transcripts)
    
    # Get existing questions if any
    existing_questions = [q["question"] for q in lecture.get("questions", [])]
    
    # Generate new questions based on recent content
    questions_and_answers = await generate_questions(
        transcript=combined_transcript,
        current_questions=existing_questions
    )
    
    # Format response
    formatted_questions = json.loads(questions_and_answers)["qa-pair"]
    
    # Update the lecture document with new questions
    await lectures_collection.update_one(
        {"lecture_id": lecture_id},
        {"$set": {"questions": formatted_questions}}
    )
    print(formatted_questions)
    return [Question(question=q['question'], answer=q['answer']) for q in formatted_questions]

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

@router.post("/getAndClearTranscripts")
async def get_and_clear_transcripts(snap_user_id: str, lecture_id: str):
    output = "; ".join(CAPTIONS_BUFFER)
    CAPTIONS_BUFFER.clear()
    
    return output


