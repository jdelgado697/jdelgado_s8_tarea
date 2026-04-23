from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    author: str = Field(min_length=2, max_length=100)
    isbn: str = Field(min_length=10, max_length=20)
    total_copies: int = Field(ge=1)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int


class LoanCreate(BaseModel):
    user_id: int
    book_id: int
    loan_days: int = Field(default=14, ge=1, le=30)


class LoanResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrowed_at: datetime
    due_at: datetime
    returned_at: datetime | None
    fine_amount: float
    status: str


class ReservationCreate(BaseModel):
    user_id: int
    book_id: int


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    created_at: datetime
    status: str
