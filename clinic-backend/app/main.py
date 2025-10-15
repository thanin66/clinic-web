from fastapi import FastAPI
from .database import engine, Base
import app.models  # ต้อง import models ก่อน create_all
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware # <--- IMPORT นี้
import os

from .routes import users, appointments, doctor, google_auth

load_dotenv()


print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created")

app = FastAPI()  # Instantiate FastAPI app


app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "super-secret-key-for-session"))


app.include_router(users.router)  
app.include_router(appointments.router)
app.include_router(doctor.router)
app.include_router(google_auth.router, prefix="/auth")





# ตั้งค่า CORS

origins = [
    "http://localhost:8080",  # frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI with PostgreSQL!"}
