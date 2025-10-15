# app/routes/doctor.py
from fastapi import APIRouter

router = APIRouter(prefix="/doctors", tags=["Doctors"])

# กำหนด list หมอแบบคงที่
DOCTORS = [
    "หมอสมชาย",
    "หมอสมหญิง",
    "หมอดำรงค์",
]

@router.get("/")
def list_doctors():
    """
    คืน list ของหมอทั้งหมด
    """
    return DOCTORS
