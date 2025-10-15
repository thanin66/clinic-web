# crud.py
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas
import re

# ---------------- Users ----------------
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    from passlib.hash import bcrypt

    # ตรวจอีเมลซ้ำ
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = bcrypt.hash(user.password)
    db_user = models.User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()

# ---------------- Appointments ----------------
# ---------------- Create ----------------
def create_appointment(db: Session, user_id: int, appointment: schemas.AppointmentCreate):
    # คำนวณเวลาใน slot
    existing_count = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.appointment_date == appointment.appointment_date,
            models.Appointment.time_slot == appointment.time_slot
        ).count()
    )

    start_time = datetime.strptime("08:00", "%H:%M") if appointment.time_slot == "เช้า" else datetime.strptime("13:00", "%H:%M")
    appointment_time = (start_time + timedelta(minutes=30 * existing_count)).time()

    db_appointment = models.Appointment(
        user_id=user_id,
        doctor_name="หมอประจำ",
        appointment_date=appointment.appointment_date,
        appointment_time=appointment_time,
        time_slot=appointment.time_slot,
        reason=appointment.reason,
        status="รอการยืนยัน",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# ---------------- Read ----------------
def get_appointments(db: Session):
    return db.query(models.Appointment).all()

def get_appointment(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

# ---------------- Update ----------------
def update_appointment(db: Session, appointment_id: int, user_id: int, update: schemas.AppointmentUpdate):
    appointment = get_appointment(db, appointment_id)
    if not appointment or appointment.user_id != user_id:
        return None

    if update.appointment_date or update.time_slot:
        new_date = update.appointment_date or appointment.appointment_date
        new_slot = update.time_slot or appointment.time_slot

        existing_count = db.query(models.Appointment)\
            .filter(
                models.Appointment.appointment_date == new_date,
                models.Appointment.time_slot == new_slot,
                models.Appointment.id != appointment.id
            ).count()

        start_time = datetime.strptime("08:00", "%H:%M") if new_slot == "เช้า" else datetime.strptime("13:00", "%H:%M")
        appointment_time = (start_time + timedelta(minutes=30 * existing_count)).time()

        appointment.appointment_date = new_date
        appointment.time_slot = new_slot
        appointment.appointment_time = appointment_time

    if update.reason is not None:
        appointment.reason = update.reason

    appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    return appointment

# ---------------- Delete ----------------
def delete_appointment(db: Session, appointment_id: int, user_id: int):
    appointment = get_appointment(db, appointment_id)
    if not appointment or appointment.user_id != user_id:
        return None
    db.delete(appointment)
    db.commit()
    return True

# ---------------- google ----------------

def create_google_user(db: Session, user: schemas.UserGoogleCreate):
    # ตรวจสอบว่ามีอีเมลนี้อยู่แล้วหรือไม่
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    if existing_user:
        # ถือว่า User นั้นสมัครแล้ว (ไม่ว่าจะด้วย Google หรือ Email/Pass)
        return existing_user
    
    # สร้าง username โดยใช้ส่วนแรกของอีเมล และเพิ่มตัวเลขถ้าซ้ำ (ตัวอย่างง่ายๆ)
    username_base = user.email.split('@')[0]
    # NOTE: ใน Production คุณอาจต้องมีตรรกะที่ซับซ้อนกว่านี้
    clean_username = re.sub(r'[^a-zA-Z0-9]', '', username_base)

    db_user = models.User(
        # ตรวจสอบว่า username ซ้ำหรือไม่ (ถ้าต้องการให้ Google User มี username ที่ไม่ซ้ำ)
        # เนื่องจาก username ถูกกำหนดเป็น unique=True ใน models.py คุณต้องแน่ใจว่ามันไม่ซ้ำ
        # สำหรับตอนนี้ เราจะใช้ username_base ตรงๆ เพราะการชนกันจะถูกจับเมื่อ commit
        username=clean_username, 
        email=user.email,
        password=None, # <--- กำหนดเป็น None ให้ชัดเจน
        first_name=user.given_name,
        last_name=user.family_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user