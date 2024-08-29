from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models import Base
from app.crud import create_user, get_user, authenticate_user, reset_password, save_otp, verify_otp
from app.schemas import UserCreate, UserResponse, Token, OTPVerify
from app.config import DATABASE_URL, SECRET_KEY, EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import jwt
from passlib.context import CryptContext
import pyotp
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

# Setup Database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Setup Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions
def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

import smtplib
from email.mime.text import MIMEText
from fastapi import HTTPException

def send_email(subject: str, body: str, to_email: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USERNAME
    msg["To"] = to_email
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, to_email, msg.as_string())
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")
    except Exception as e:
        print(f"General error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while sending email")


def generate_otp():
    return pyotp.random_base32()

def verify_otp_token(otp: str, token: str):
    otp_provided = pyotp.TOTP(token)
    return otp_provided.verify(otp)

# Routes
@app.post("/signup/")
def signup(user: UserCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    db_user = create_user(db, user)
    if db_user:
        otp = generate_otp()
        save_otp(db, user.username, otp)
        if background_tasks:
            background_tasks.add_task(send_email, "Your OTP Code", f"Your OTP code is {otp}", user.username)
        return {"msg": "Signup successful, check your email for OTP"}
    raise HTTPException(status_code=400, detail="User already exists")


@app.post("/verify-otp/")
def verify_otp_route(otp_request: OTPVerify, db: Session = Depends(get_db)):
    if verify_otp(db, otp_request.username, otp_request.otp):
        return {"msg": "OTP verified successfully"}
    raise HTTPException(status_code=400, detail="Invalid OTP")

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user:
        token = create_jwt_token({"sub": user.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/reset-password/")
def reset_password_route(user_data: UserCreate, db: Session = Depends(get_db)):
    user = reset_password(db, user_data)
    if user:
        return {"msg": "Password reset successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/{username}")
def get_user_route(username: str, db: Session = Depends(get_db)):
    user = get_user(db, username)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")
