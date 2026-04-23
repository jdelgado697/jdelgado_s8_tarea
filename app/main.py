from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException

from .database import connection_scope, init_db
from .repositories import BookRepository, LoanRepository, ReservationRepository, UserRepository
from .schemas import (
    BookCreate,
    BookResponse,
    LoanCreate,
    LoanResponse,
    ReservationCreate,
    ReservationResponse,
    UserCreate,
    UserResponse,
)
from .services import LibraryService

app = FastAPI(title='Sistema de Gestion de Bibliotecas', version='1.0.0')
init_db()


def get_service() -> LibraryService:
    with connection_scope() as conn:
        yield LibraryService(
            users=UserRepository(conn),
            books=BookRepository(conn),
            loans=LoanRepository(conn),
            reservations=ReservationRepository(conn),
        )


@app.get("/")
def root():
    return {"message": "API Biblioteca funcionando correctamente"}

@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/users', response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, service: LibraryService = Depends(get_service)) -> dict:
    try:
        return service.register_user(name=payload.name, email=payload.email)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post('/books', response_model=BookResponse, status_code=201)
def create_book(payload: BookCreate, service: LibraryService = Depends(get_service)) -> dict:
    try:
        return service.register_book(
            title=payload.title,
            author=payload.author,
            isbn=payload.isbn,
            total_copies=payload.total_copies,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get('/books', response_model=list[BookResponse])
def list_books(service: LibraryService = Depends(get_service)) -> list[dict]:
    try:
        return service.books.list_all()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post('/reservations', response_model=ReservationResponse, status_code=201)
def create_reservation(payload: ReservationCreate, service: LibraryService = Depends(get_service)) -> dict:
    try:
        return service.create_reservation(user_id=payload.user_id, book_id=payload.book_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post('/loans', response_model=LoanResponse, status_code=201)
def create_loan(payload: LoanCreate, service: LibraryService = Depends(get_service)) -> dict:
    try:
        return service.borrow_book(user_id=payload.user_id, book_id=payload.book_id, loan_days=payload.loan_days)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post('/loans/{loan_id}/return', response_model=LoanResponse)
def return_loan(loan_id: int, service: LibraryService = Depends(get_service)) -> dict:
    try:
        return service.return_book(loan_id=loan_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
