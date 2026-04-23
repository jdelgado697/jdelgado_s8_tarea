from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from app import database, main


def test_end_to_end_api_flow() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / 'api_test.db'
        original_db = database.DB_PATH
        database.DB_PATH = db_path
        try:
            database.init_db()
            client = TestClient(main.app)

            health_response = client.get('/health')
            assert health_response.status_code == 200
            assert health_response.json()['status'] == 'ok'

            user_response = client.post('/users', json={'name': 'Paula Diaz', 'email': 'paula@example.com'})
            assert user_response.status_code == 201
            user_id = user_response.json()['id']

            book_response = client.post(
                '/books',
                json={
                    'title': 'Arquitectura Limpia',
                    'author': 'Robert C. Martin',
                    'isbn': '9788441532100',
                    'total_copies': 2,
                },
            )
            assert book_response.status_code == 201
            book_id = book_response.json()['id']

            reservation_response = client.post('/reservations', json={'user_id': user_id, 'book_id': book_id})
            assert reservation_response.status_code == 201
            assert reservation_response.json()['status'] == 'ACTIVE'

            loan_response = client.post('/loans', json={'user_id': user_id, 'book_id': book_id, 'loan_days': 7})
            assert loan_response.status_code == 201
            loan_id = loan_response.json()['id']

            list_response = client.get('/books')
            assert list_response.status_code == 200
            assert list_response.json()[0]['available_copies'] == 1

            return_response = client.post(f'/loans/{loan_id}/return')
            assert return_response.status_code == 200
            assert return_response.json()['status'] == 'RETURNED'
        finally:
            database.DB_PATH = original_db
