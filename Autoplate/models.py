from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base  

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    bids = relationship("Bid", back_populates="user")
    plates = relationship("AutoPlate", back_populates="owner")

class AutoPlate(Base):
    __tablename__ = "plates"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, index=True)
    description = Column(String)
    deadline = Column(DateTime)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="plates")
    bids = relationship("Bid", back_populates="plate")

class Bid(Base):
    __tablename__ = "bids"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2))
    user_id = Column(Integer, ForeignKey("users.id"))
    plate_id = Column(Integer, ForeignKey("plates.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="bids")
    plate = relationship("AutoPlate", back_populates="bids")
    
    __table_args__ = (UniqueConstraint("user_id", "plate_id", name="unique_user_plate"),)
