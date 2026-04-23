from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any


class UserRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, name: str, email: str) -> dict[str, Any]:
        cursor = self.conn.execute(
            'INSERT INTO users(name, email) VALUES(?, ?)',
            (name, email),
        )
        user_id = cursor.lastrowid
        return self.get_by_id(int(user_id))

    def get_by_id(self, user_id: int) -> dict[str, Any]:
        row = self.conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if row is None:
            raise ValueError('Usuario no encontrado')
        return dict(row)


class BookRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, title: str, author: str, isbn: str, total_copies: int) -> dict[str, Any]:
        cursor = self.conn.execute(
            '''
            INSERT INTO books(title, author, isbn, total_copies, available_copies)
            VALUES(?, ?, ?, ?, ?)
            ''',
            (title, author, isbn, total_copies, total_copies),
        )
        book_id = cursor.lastrowid
        return self.get_by_id(int(book_id))

    def get_by_id(self, book_id: int) -> dict[str, Any]:
        row = self.conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if row is None:
            raise ValueError('Libro no encontrado')
        return dict(row)

    def update_available_copies(self, book_id: int, new_value: int) -> None:
        self.conn.execute(
            'UPDATE books SET available_copies = ? WHERE id = ?',
            (new_value, book_id),
        )

    def list_all(self) -> list[dict[str, Any]]:
        rows = self.conn.execute('SELECT * FROM books ORDER BY title').fetchall()
        return [dict(row) for row in rows]


class ReservationRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, user_id: int, book_id: int) -> dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        cursor = self.conn.execute(
            '''
            INSERT INTO reservations(user_id, book_id, created_at, status)
            VALUES(?, ?, ?, 'ACTIVE')
            ''',
            (user_id, book_id, timestamp),
        )
        reservation_id = cursor.lastrowid
        return self.get_by_id(int(reservation_id))

    def complete_first_active(self, book_id: int) -> None:
        row = self.conn.execute(
            '''
            SELECT id FROM reservations
            WHERE book_id = ? AND status = 'ACTIVE'
            ORDER BY created_at ASC LIMIT 1
            ''',
            (book_id,),
        ).fetchone()
        if row is not None:
            self.conn.execute(
                "UPDATE reservations SET status = 'COMPLETED' WHERE id = ?",
                (row['id'],),
            )

    def get_by_id(self, reservation_id: int) -> dict[str, Any]:
        row = self.conn.execute('SELECT * FROM reservations WHERE id = ?', (reservation_id,)).fetchone()
        if row is None:
            raise ValueError('Reserva no encontrada')
        return dict(row)


class LoanRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, user_id: int, book_id: int, borrowed_at: str, due_at: str) -> dict[str, Any]:
        cursor = self.conn.execute(
            '''
            INSERT INTO loans(user_id, book_id, borrowed_at, due_at, fine_amount, status)
            VALUES(?, ?, ?, ?, 0, 'BORROWED')
            ''',
            (user_id, book_id, borrowed_at, due_at),
        )
        loan_id = cursor.lastrowid
        return self.get_by_id(int(loan_id))

    def get_by_id(self, loan_id: int) -> dict[str, Any]:
        row = self.conn.execute('SELECT * FROM loans WHERE id = ?', (loan_id,)).fetchone()
        if row is None:
            raise ValueError('Prestamo no encontrado')
        return dict(row)

    def update_return(self, loan_id: int, returned_at: str, fine_amount: float, status: str) -> dict[str, Any]:
        self.conn.execute(
            '''
            UPDATE loans
            SET returned_at = ?, fine_amount = ?, status = ?
            WHERE id = ?
            ''',
            (returned_at, fine_amount, status, loan_id),
        )
        return self.get_by_id(loan_id)
