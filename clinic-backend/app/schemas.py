from datetime import datetime, date, time
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Union

# ---------------- User ----------------
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator('username')
    def username_valid(cls, v):
        if not (3 <= len(v) <= 20):
            raise ValueError('username ต้องมี 3-20 ตัวอักษร')
        if not v.isalnum():
            raise ValueError('username ต้องเป็นตัวอักษรหรือเลขเท่านั้น')
        return v

    @validator('password')
    def password_valid(cls, v):
        if len(v) < 6:
            raise ValueError('password ต้องมีอย่างน้อย 6 ตัวอักษร')
        return v
    

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[Union[date, str]] = None  # รองรับทั้ง date และ string
    address: Optional[str] = None
    phone_number: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None

    @validator('username')
    def username_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not (3 <= len(v) <= 20):
            raise ValueError('username ต้องมี 3-20 ตัวอักษร')
        if not v.isalnum():
            raise ValueError('username ต้องเป็นตัวอักษรหรือเลขเท่านั้น')
        return v

    @validator('password')
    def password_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) < 6:
            raise ValueError('password ต้องมีอย่างน้อย 6 ตัวอักษร')
        return v

    @validator("date_of_birth", pre=True)
    def parse_date(cls, v):
        if not v or v == "":
            return None
        if isinstance(v, date):
            return v
        try:
            return date.fromisoformat(str(v))
        except ValueError:
            raise ValueError("วันเกิดต้องอยู่ในรูปแบบ YYYY-MM-DD")
  
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None

    model_config = {"from_attributes": True}

# ---------------- Appointment ----------------
class AppointmentBase(BaseModel):
    appointment_date: date
    time_slot: str  # เช้า / บ่าย
    reason: Optional[str] = None
    doctor_name: Optional[str]


class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    time_slot: Optional[str] = None
    reason: Optional[str] = None
    doctor_name: Optional[str] = None 

class AppointmentOut(BaseModel):
    id: int
    user_id: Optional[int]
    # user_email: str = None ไม่ใข้ 
    doctor_name: str
    appointment_date: date
    appointment_time: time
    time_slot: str
    reason: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# ---------------- JWT ----------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# Pydantic Model สำหรับข้อมูลผู้ใช้ที่ได้รับจาก Google (OpenID Connect)
class UserGoogleCreate(BaseModel):
    # ข้อมูลที่จำเป็นในการสร้าง/ค้นหา User ใน DB
    email: EmailStr
    name: str # ชื่อเต็มที่ได้จาก Google
    # ข้อมูลเสริม
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None # URL รูปภาพโปรไฟล์
