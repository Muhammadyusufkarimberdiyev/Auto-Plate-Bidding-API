from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from models import User, AutoPlate, Bid
from schemas import *
from auth import get_current_user, create_access_token, get_password_hash

router = APIRouter()

# ✅ Foydalanuvchini ro'yxatdan o'tkazish
@router.post("/register/", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu foydalanuvchi nomi allaqachon band")
    hashed_password = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, hashed_password=hashed_password, is_admin=user_data.is_admin)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token(new_user.id)
    return {"id": new_user.id, "username": new_user.username, "token": token}

# ✅ Login qilish
@router.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return {"username": form_data.username, "password": form_data.password}

# ✅ Avtomobil raqamlarini ko'rish
@router.get("/plates/", response_model=List[AutoPlateResponse])
def list_plates(ordering: str = None, plate_number__contains: str = None, db: Session = Depends(get_db)):
    query = db.query(AutoPlate).filter(AutoPlate.is_active == True)
    if plate_number__contains:
        query = query.filter(AutoPlate.plate_number.contains(plate_number__contains))
    if ordering == "deadline":
        query = query.order_by(AutoPlate.deadline)
    return query.all()

# ✅ Avtomobil raqamini qo'shish
@router.post("/plates/", response_model=AutoPlateResponse)
def create_plate(plate: AutoPlateCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Faqat adminlar raqam qo'shishi mumkin")
    if db.query(AutoPlate).filter(AutoPlate.plate_number == plate.plate_number).first():
        raise HTTPException(status_code=400, detail="Bunday raqam allaqachon mavjud")
    if plate.deadline < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Tugash vaqti kelajakda bo'lishi kerak")
    new_plate = AutoPlate(**plate.dict(), created_by=current_user.id)
    db.add(new_plate)
    db.commit()
    db.refresh(new_plate)
    return new_plate

# ✅ Bitta raqamni ko'rish
@router.get("/plates/{id}/", response_model=AutoPlateResponse)
def get_plate(id: int, db: Session = Depends(get_db)):
    plate = db.query(AutoPlate).filter(AutoPlate.id == id).first()
    if not plate:
        raise HTTPException(status_code=404, detail="Raqam topilmadi")
    return plate

# ✅ Raqamni yangilash
@router.put("/plates/{id}/", response_model=AutoPlateResponse)
def update_plate(id: int, plate_data: AutoPlateCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plate = db.query(AutoPlate).filter(AutoPlate.id == id).first()
    if not plate or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Faqat adminlar raqamni o'zgartirishi mumkin")
    for key, value in plate_data.dict().items():
        setattr(plate, key, value)
    db.commit()
    return plate

# ✅ Raqamni o'chirish
@router.delete("/plates/{id}/")
def delete_plate(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plate = db.query(AutoPlate).filter(AutoPlate.id == id).first()
    if not plate or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Faqat adminlar raqamni o'chirishi mumkin")
    if db.query(Bid).filter(Bid.plate_id == id).first():
        raise HTTPException(status_code=400, detail="Aktiv takliflar mavjud bo'lsa, raqamni o'chirib bo'lmaydi")
    db.delete(plate)
    db.commit()
    return {"message": "Raqam o'chirildi"}

# ✅ Foydalanuvchining takliflari
@router.get("/bids/", response_model=List[BidResponse])
def list_bids(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Bid).filter(Bid.user_id == current_user.id).all()

# ✅ Taklif berish
@router.post("/bids/", response_model=BidResponse)
def place_bid(bid: BidCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plate = db.query(AutoPlate).filter(AutoPlate.id == bid.plate_id).first()
    if not plate or not plate.is_active or plate.deadline < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Taklif berish muddati tugagan")
    highest_bid = db.query(Bid).filter(Bid.plate_id == bid.plate_id).order_by(Bid.amount.desc()).first()
    if highest_bid and bid.amount <= highest_bid.amount:
        raise HTTPException(status_code=400, detail="Taklif hozirgi eng yuqori summadan oshishi kerak")
    if db.query(Bid).filter(Bid.user_id == current_user.id, Bid.plate_id == bid.plate_id).first():
        raise HTTPException(status_code=400, detail="Siz allaqachon ushbu raqamga taklif bergansiz")
    new_bid = Bid(**bid.dict(), user_id=current_user.id)
    db.add(new_bid)
    db.commit()
    db.refresh(new_bid)
    return new_bid

# ✅ Bitta taklifni ko'rish
@router.get("/bids/{id}/")
def get_bid(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bid = db.query(Bid).filter(Bid.id == id, Bid.user_id == current_user.id).first()
    if not bid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q")
    return bid

# ✅ Taklifni yangilash
@router.put("/bids/{id}/")
def update_bid(id: int, bid_data: BidCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bid = db.query(Bid).filter(Bid.id == id, Bid.user_id == current_user.id).first()
    if not bid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q")
    plate = db.query(AutoPlate).filter(AutoPlate.id == bid.plate_id).first()
    if plate.deadline < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Taklif muddati tugagan")
    bid.amount = bid_data.amount
    db.commit()
    return bid

# ✅ Taklifni o'chirish
@router.delete("/bids/{id}/")
def delete_bid(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bid = db.query(Bid).filter(Bid.id == id, Bid.user_id == current_user.id).first()
    if not bid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q")
    db.delete(bid)
    db.commit()
    return {"message": "Taklif o'chirildi"}
