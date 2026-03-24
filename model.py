from sqlalchemy import Column, Integer, String, Float, Date
from db import Base
from sqlalchemy import ForeignKey
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    notes = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id")) 