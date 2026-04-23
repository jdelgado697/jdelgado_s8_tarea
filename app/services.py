from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from .repositories import BookRepository, LoanRepository, ReservationRepository, UserRepository

DAILY_FINE = 0.75


class LibraryService:
    def __init__(
        self,
        users: UserRepository,
        books: BookRepository,
        loans: LoanRepository,
        reservations: ReservationRepository,
    ) -> None:
        self.users = users
        self.books = books
        self.loans = loans
        self.reservations = reservations

    def register_user(self, name: str, email: str) -> dict[str, Any]:
        return self.users.create(name=name, email=email)

    def register_book(self, title: str, author: str, isbn: str, total_copies: int) -> dict[str, Any]:
        return self.books.create(title=title, author=author, isbn=isbn, total_copies=total_copies)

    def create_reservation(self, user_id: int, book_id: int) -> dict[str, Any]:
        self.users.get_by_id(user_id)
        self.books.get_by_id(book_id)
        return self.reservations.create(user_id=user_id, book_id=book_id)

    def borrow_book(self, user_id: int, book_id: int, loan_days: int = 14) -> dict[str, Any]:
        self.users.get_by_id(user_id)
        book = self.books.get_by_id(book_id)
        if book['available_copies'] <= 0:
            raise ValueError('No hay copias disponibles para prestamo')

        borrowed_at = datetime.utcnow()
        due_at = borrowed_at + timedelta(days=loan_days)
        loan = self.loans.create(
            user_id=user_id,
            book_id=book_id,
            borrowed_at=borrowed_at.isoformat(),
            due_at=due_at.isoformat(),
        )
        self.books.update_available_copies(book_id, book['available_copies'] - 1)
        self.reservations.complete_first_active(book_id)
        return loan

    def return_book(self, loan_id: int, return_date: datetime | None = None) -> dict[str, Any]:
        loan = self.loans.get_by_id(loan_id)
        if loan['returned_at']:
            raise ValueError('El prestamo ya fue devuelto')

        returned_at = return_date or datetime.utcnow()
        due_at = datetime.fromisoformat(loan['due_at'])
        overdue_days = max((returned_at.date() - due_at.date()).days, 0)
        fine_amount = round(overdue_days * DAILY_FINE, 2)
        status = 'RETURNED' if overdue_days == 0 else 'OVERDUE'
        updated_loan = self.loans.update_return(
            loan_id=loan_id,
            returned_at=returned_at.isoformat(),
            fine_amount=fine_amount,
            status=status,
        )
        book = self.books.get_by_id(int(loan['book_id']))
        self.books.update_available_copies(int(loan['book_id']), book['available_copies'] + 1)
        return updated_loan
