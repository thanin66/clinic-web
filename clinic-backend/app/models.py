from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True) 
    date_joined = Column(DateTime, default=datetime.utcnow)
    
    # ข้อมูลส่วนตัวเพิ่มเติม
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    allergies = Column(String, nullable=True)
    chronic_conditions = Column(String, nullable=True)
    current_medications = Column(String, nullable=True)

    appointments = relationship("Appointment", back_populates="user")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    doctor_name = Column(String)
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    time_slot = Column(String)  # เช้า / บ่าย
    reason = Column(String, nullable=True)
    status = Column(String, default="รอการยืนยัน")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="appointments")