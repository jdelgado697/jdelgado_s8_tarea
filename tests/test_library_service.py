from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from app.database import connection_scope, init_db
from app.repositories import BookRepository, LoanRepository, ReservationRepository, UserRepository
from app.services import DAILY_FINE, LibraryService


def build_service(tmp_path: Path) -> LibraryService:
    db_path = tmp_path / 'test_library.db'
    init_db(db_path)
    conn = connection_scope(db_path)
    managed_conn = conn.__enter__()
    service = LibraryService(
        users=UserRepository(managed_conn),
        books=BookRepository(managed_conn),
        loans=LoanRepository(managed_conn),
        reservations=ReservationRepository(managed_conn),
    )
    service._conn_cm = conn  # type: ignore[attr-defined]
    return service


def teardown_service(service: LibraryService) -> None:
    service._conn_cm.__exit__(None, None, None)  # type: ignore[attr-defined]


def test_borrow_book_reduces_availability(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    try:
        user = service.register_user('Ana Soto', 'ana@example.com')
        book = service.register_book('Clean Code', 'Robert C. Martin', '9780132350884', 2)

        loan = service.borrow_book(user['id'], book['id'])
        updated_book = service.books.get_by_id(book['id'])

        assert loan['status'] == 'BORROWED'
        assert updated_book['available_copies'] == 1
    finally:
        teardown_service(service)


def test_borrow_book_without_stock_raises_error(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    try:
        user = service.register_user('Luis Perez', 'luis@example.com')
        book = service.register_book('Domain-Driven Design', 'Eric Evans', '9780321125217', 1)
        service.borrow_book(user['id'], book['id'])

        try:
            service.borrow_book(user['id'], book['id'])
            assert False, 'Se esperaba ValueError por falta de stock'
        except ValueError as exc:
            assert 'No hay copias disponibles' in str(exc)
    finally:
        teardown_service(service)


def test_return_book_calculates_fine_for_overdue_loan(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    try:
        user = service.register_user('Maria Vera', 'maria@example.com')
        book = service.register_book('Refactoring', 'Martin Fowler', '9780201485677', 1)
        loan = service.borrow_book(user['id'], book['id'], loan_days=1)

        return_date = datetime.fromisoformat(loan['due_at']) + timedelta(days=3)
        returned_loan = service.return_book(loan['id'], return_date=return_date)

        assert returned_loan['status'] == 'OVERDUE'
        assert returned_loan['fine_amount'] == round(3 * DAILY_FINE, 2)
    finally:
        teardown_service(service)


def test_reservation_is_completed_when_book_is_borrowed(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    try:
        user = service.register_user('Diego Lagos', 'diego@example.com')
        book = service.register_book('Python Testing', 'Brian Okken', '9781680502404', 2)
        reservation = service.create_reservation(user['id'], book['id'])

        service.borrow_book(user['id'], book['id'])
        updated_reservation = service.reservations.get_by_id(reservation['id'])

        assert updated_reservation['status'] == 'COMPLETED'
    finally:
        teardown_service(service)
