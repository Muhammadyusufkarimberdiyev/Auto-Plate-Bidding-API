from pydantic import BaseModel
from datetime import datetime
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

class BidCreate(BaseModel):
    amount: float
    plate_id: int

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserResponse(BaseModel):
    id: int
    username: str
    token: str
