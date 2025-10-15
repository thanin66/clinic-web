from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from .. import schemas, crud, database, auth

router = APIRouter(tags=["Users"])
get_db = database.get_db

# ---------------- Register ----------------
@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(crud.models.User).filter(
        (crud.models.User.username == user.username) | (crud.models.User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="ชื่อผู้ใช้หรืออีเมลนี้มีอยู่แล้ว")
    return crud.create_user(db, user)

# ---------------- Login ----------------
from pydantic import BaseModel
class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=schemas.Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.email)
    if not user or not auth.verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="อีเมลหรือรหัสผ่านไม่ถูกต้อง")
    access_token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------- Current User ----------------
@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: crud.models.User = Depends(auth.get_current_user)):
    return current_user

@router.put("/me/profile", response_model=schemas.UserResponse)
def update_profile(
    updated_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: crud.models.User = Depends(auth.get_current_user)
):
    data = updated_data.dict(exclude_unset=True)
    try:
        for key, value in data.items():
            if hasattr(current_user, key):
                setattr(current_user, key, value)
        # ปัญหา: แม้จะมีการเรียก db.commit() แต่ถ้าเกิดความผิดพลาดในส่วนใดส่วนหนึ่ง ข้อมูลอาจไม่ถูกบันทึก
        db.commit() 
        db.refresh(current_user)
        return current_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"การแก้ไข ล้มเหลว: {e}")
    


@router.delete("/me", response_model=dict)
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: crud.models.User = Depends(auth.get_current_user)
):
    
    db.delete(current_user)
    db.commit()
    return {"detail": "User deleted successfully"}