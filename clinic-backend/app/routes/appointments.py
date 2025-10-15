# ---------------- ROUTER ----------------
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from .. import schemas, database, auth, models

router = APIRouter(prefix="/appointments", tags=["Appointments"])
get_db = database.get_db
get_current_user = auth.get_current_user

# ---------------- CREATE ----------------
@router.post("/", response_model=schemas.AppointmentOut)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # จำนวน appointment ในวัน/slot
    existing_count = db.query(models.Appointment).filter(
        models.Appointment.appointment_date == appointment.appointment_date,
        models.Appointment.time_slot == appointment.time_slot
    ).count()

    # เวลาเริ่ม/สิ้นสุด
    if appointment.time_slot == "เช้า":
        start_time = datetime.strptime("08:00", "%H:%M")
        end_time = datetime.strptime("11:30", "%H:%M")
    else:
        start_time = datetime.strptime("13:00", "%H:%M")
        end_time = datetime.strptime("17:30", "%H:%M")

    # คำนวณเวลานัด
    new_time = (start_time + timedelta(minutes=30 * existing_count)).time()

    # ตรวจสอบ slot เต็ม
    if new_time > end_time.time():
        raise HTTPException(status_code=400, detail=f"{appointment.time_slot}เต็มแล้ว")

    new_appointment = models.Appointment(
        user_id=current_user.id,
        doctor_name=appointment.doctor_name,
        appointment_date=appointment.appointment_date,
        appointment_time=new_time,
        time_slot=appointment.time_slot,
        reason=appointment.reason,
        status="รอการยืนยัน",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


# ---------------- READ ALL ----------------
@router.get("/", response_model=List[schemas.AppointmentOut])
def read_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    appointments = db.query(models.Appointment).all()
    return appointments

# ---------------- READ ONE ----------------
@router.get("/{appointment_id}", response_model=schemas.AppointmentOut)
def read_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    appointment = db.get(models.Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="ไม่พบการนัดหมาย")
    return appointment

# ---------------- UPDATE ----------------
@router.put("/{appointment_id}", response_model=schemas.AppointmentOut)
def update_appointment(
    appointment_id: int,
    appointment_update: schemas.AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    appointment = db.get(models.Appointment, appointment_id)
    if not appointment or appointment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="ไม่พบการนัดหมาย")

    # อัปเดตวัน/slot
    if appointment_update.appointment_date or appointment_update.time_slot:
        new_date = appointment_update.appointment_date or appointment.appointment_date
        new_slot = appointment_update.time_slot or appointment.time_slot

        # จำนวน appointment ใน slot นั้น (ยกเว้นตัวเอง)
        existing_count = db.query(models.Appointment).filter(
            models.Appointment.appointment_date == new_date,
            models.Appointment.time_slot == new_slot,
            models.Appointment.id != appointment.id
        ).count()

        if new_slot == "เช้า":
            start_time = datetime.strptime("08:00", "%H:%M")
            end_time = datetime.strptime("11:30", "%H:%M")
        else:
            start_time = datetime.strptime("13:00", "%H:%M")
            end_time = datetime.strptime("17:30", "%H:%M")

        new_time = (start_time + timedelta(minutes=30 * existing_count)).time()

        if new_time > end_time.time():
            raise HTTPException(status_code=400, detail=f"{new_slot}เต็มแล้ว")

        appointment.appointment_date = new_date
        appointment.time_slot = new_slot
        appointment.appointment_time = new_time

    if appointment_update.reason:
        appointment.reason = appointment_update.reason

    if appointment_update.doctor_name:
        appointment.doctor_name = appointment_update.doctor_name

    appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    return appointment

# ---------------- DELETE ----------------
@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    appointment = db.get(models.Appointment, appointment_id)
    if not appointment or appointment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="ไม่พบการนัดหมาย")
    db.delete(appointment)
    db.commit()
    return {"detail": "ลบการนัดหมายเรียบร้อยแล้ว"}
