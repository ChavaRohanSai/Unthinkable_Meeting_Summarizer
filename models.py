from pydantic import BaseModel
from typing import List, Optional

class Meeting(BaseModel):
    id: str
    filename: str
    transcript: str
    summary: str
    key_points: Optional[List[str]] = []
    action_points: Optional[List[str]] = []
    meeting_date: Optional[str] = None   # Format: 'YYYY-MM-DD'
    start_time: Optional[str] = None     # Format: 'HH:MM:SS'
    end_time: Optional[str] = None       # Format: 'HH:MM:SS'

    class Config:
        orm_mode = True
