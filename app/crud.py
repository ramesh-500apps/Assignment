from sqlalchemy.orm import Session
from app.models import User, OTP
from app.schemas import UserCreate
from passlib.context import CryptContext
import pyotp

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

def reset_password(db: Session, user_data: UserCreate):
    user = get_user(db, user_data.username)
    if user:
        user.hashed_password = pwd_context.hash(user_data.password)
        db.commit()
        return user
    return None

def save_otp(db: Session, username: str, otp: str):
    otp_entry = OTP(username=username, otp=otp)
    db.add(otp_entry)
    db.commit()

def verify_otp(db: Session, username: str, otp: str):
    otp_entry = db.query(OTP).filter(OTP.username == username).order_by(OTP.created_at.desc()).first()
    if otp_entry and otp_entry.otp == otp:
        return True
    return False
