from datetime import date
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import SessionLocal, engine, Base
from model import Expense as ExpenseModel
from model import User
from auth import hash_password
from auth import verify_password, create_access_token
from auth import get_current_user
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, extract
from fastapi.middleware.cors import CORSMiddleware
import os

origins = [
    os.getenv("FRONTEND_URL"),
    "http://localhost:3000"
]
Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserCreate(BaseModel):
    email: str
    password: str


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: date
    notes: str | None = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
     existing_user = db.query(User).filter(User.email == user.email).first()

     if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
     new_user = User(
        email=user.email,
        password=hash_password(user.password)
    )
     db.add(new_user)
     db.commit()
     db.refresh(new_user)

     return {"message": "User created"}


@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"user_id": db_user.id})
    return {"access_token": token}    

@app.post("/expenses")
def add_expense(expense: ExpenseCreate,user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    
    new_expense = ExpenseModel(
        amount=expense.amount,
        category=expense.category,
        date=expense.date,
        notes=expense.notes,
        user_id=user_id
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return {"message": "Expense saved"}

@app.get("/expenses")
def get_expenses(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    return db.query(ExpenseModel).filter(
        ExpenseModel.user_id == user_id
    ).all()

@app.delete("/expenses/{id}")
def delete_expense(
    id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    
    expense = db.query(ExpenseModel).filter(
        ExpenseModel.id == id,
        ExpenseModel.user_id == user_id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

    return {"message": "Deleted successfully"}