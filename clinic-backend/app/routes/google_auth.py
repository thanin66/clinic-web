# routers/google_auth.py
import os
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from .. import crud, schemas, database, auth  # ต้องแน่ใจว่า import ถูกต้อง
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(tags=["Google Auth"])
get_db = database.get_db

# ต้องตั้งค่า OAuth object โดยใช้ Client ID และ Secret
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# Endpoint สำหรับเริ่มต้น Login
@router.get('/google/login')
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

#Endpoint สำหรับรับ Callback จาก Google
@router.get('/google/callback', name='auth_google_callback')
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        #แลก Code เป็น Access Token และ User Info
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info or 'email' not in user_info:
             # ถ้า authlib ทำงานได้ แต่ Google ไม่ให้ข้อมูล email มา (ไม่น่าจะเกิดถ้า scope ถูก)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not get user email from Google")

        email = user_info['email']

        #ค้นหาผู้ใช้ในฐานข้อมูล (ใช้ฟังก์ชันที่คุณมีใน crud.py)
        user = crud.get_user_by_email(db, email)

        if not user:
            # ผู้ใช้ใหม่: สร้างบัญชีใหม่
            google_user_data = schemas.UserGoogleCreate(
                email=email,
                name=user_info.get('name', email.split('@')[0]),
                given_name=user_info.get('given_name'),
                family_name=user_info.get('family_name'),
                picture=user_info.get('picture')
            )
            user = crud.create_google_user(db, google_user_data) # สร้างผู้ใช้ใน DB
        
        #สร้าง JWT Token สำหรับผู้ใช้ที่ล็อกอิน
        # ตรวจสอบว่า 'user' มีค่าหรือไม่ ก่อนจะเรียก user.id
        if not user:
            raise Exception("Failed to create or retrieve user from database.")
            
        access_token = auth.create_access_token({"sub": str(user.id), "auth_method": "google"})
        
        #Redirect กลับไปที่ Frontend (ถ้าสำเร็จ)
        frontend_redirect_url = os.getenv("FRONTEND_URL", "http://localhost:8080")
        response = RedirectResponse(
            # ส่ง token กลับไปให้ Vue.js จัดการ
            url=f"{frontend_redirect_url}/login/callback?token={access_token}", 
            status_code=status.HTTP_302_FOUND
        )
        return response

    except Exception as e:
        #จัดการ Error และแสดงรายละเอียด
        print(f"GOOGLE AUTH FAILURE: {e}")
        
        # ตรวจสอบประเภท Error ที่อาจเกิดจาก Authlib 
        # (Invalid token, code already used, invalid credentials)
        error_str = str(e).lower()
        if "access_token_not_found" in error_str:
            detail_msg = "OAuth Error: Authorization code not found or expired."
        elif "invalid_grant" in error_str or "invalid_client" in error_str:
            detail_msg = "OAuth Error: Client ID/Secret is invalid or code already used."
        elif "mismatch" in error_str or "credentials" in error_str:
            detail_msg = f"OAuth Setup Error: Please check Client ID/Secret or Redirect URIs. Detail: {error_str}"
        else:
             detail_msg = "Google login failed due to an unexpected server error."
        
        # Redirect กลับไปหน้า Login ใน Frontend พร้อม error message
        frontend_redirect_url = os.getenv("FRONTEND_URL", "http://localhost:8080")
        return RedirectResponse(
            url=f"{frontend_redirect_url}/login?error=google_auth_failed",
            status_code=status.HTTP_302_FOUND
        )