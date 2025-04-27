from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class LectureBase(BaseModel):
    snap_user_id: str
    lecture_id: Optional[str] = None
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    is_active: bool = True
    ongoing_summary: str = ""  # Stores the continuously updated summary
    recent_audio_chunks: List[bytes] = []  # Stores last 5 minutes of audio chunks
    transcripts: List[str] = []  # Stores all transcripts for the lecture

class LectureUpdate(BaseModel):
    audio_data: Optional[str] = None
    image_data: Optional[str] = None

class LectureSummary(BaseModel):
    text: str
    slides: List[str] = []

class Question(BaseModel):
    question: str
    answer: str

class LectureResponse(BaseModel):
    lecture_id: str

class ErrorResponse(BaseModel):
    detail: str 