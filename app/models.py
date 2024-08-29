from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(225), unique=True, index=True)
    hashed_password = Column(String(225))

class OTP(Base):
    __tablename__ = 'otps'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(225), index=True)
    otp = Column(String(225))
    created_at = Column(DateTime, default=func.now())
