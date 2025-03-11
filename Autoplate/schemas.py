from pydantic import BaseModel
from datetime import datetime


class AutoPlateResponse(BaseModel):
    id: int
    plate_number: str
    starting_price: float
    deadline: datetime
    is_active: bool

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class AutoPlateCreate(BaseModel):
    plate_number: str
    description: str
    deadline: datetime

class BidResponse(BaseModel):
    id: int
    user_id: int
    plate_id: int
    amount: float
    timestamp: datetime

    class Config:
        orm_mode = True
class BidCreate(BaseModel):
    amount: float
    plate_id: int


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserResponse(BaseModel):
    id: int
    username: str
    token: str
