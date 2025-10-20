from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import date, time

class CreateAttendance(BaseModel):
    karyawan_id: UUID
    date: date
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    status: str = 'absent'
    notes: Optional[str] = None

class UpdateAttendance(BaseModel):
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class AttendanceResponse(BaseModel):
    id: UUID
    karyawan_id: UUID
    karyawan_name: Optional[str] = None
    date: date
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    status: str
    notes: Optional[str] = None
    created_at: str
    updated_at: str
