from datetime import date
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import SessionLocal, engine, Base
from model import Expense as ExpenseModel
from model import User
Base.metadata.create_all(bind=engine)
app = FastAPI()

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
    
    new_user = User(
        email=user.email,
        password=user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created"}

@app.post("/expenses")
def add_expense(expense: ExpenseCreate, user_id: int, db: Session = Depends(get_db)):
    
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
def get_expenses(user_id: int, db: Session = Depends(get_db)):
    
    expenses = db.query(ExpenseModel).filter(
        ExpenseModel.user_id == user_id
    ).all()

    return expenses

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or db_user.password != user.password:
        return {"error": "Invalid credentials"}

    return {"message": "Login successful", "user_id": db_user.id}