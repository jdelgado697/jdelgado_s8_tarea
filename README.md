# Sistema de Gestion de Bibliotecas

Proyecto base funcional para la evaluacion de Ingenieria de Software - Semana 8.

## Arquitectura
- API REST con FastAPI.
- Separacion por capas: `schemas`, `repositories`, `services` y `database`.
- Persistencia con SQLite para facilitar la ejecucion local.
- Preparado para evolucionar a microservicios mediante contenedores.

## Requisitos
- Python 3.11+

## Instalacion y ejecucion
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints principales
- `GET /health`
- `POST /users`
- `POST /books`
- `GET /books`
- `POST /reservations`
- `POST /loans`
- `POST /loans/{loan_id}/return`

## Ejecucion de pruebas unitarias
```bash
pytest --cov=app --cov-report=term-missing --cov-report=xml
```

## SonarQube
Este proyecto incluye el archivo `sonar-project.properties` para integracion con SonarQube.

Ejemplo de ejecucion:
```bash
sonar-scanner
```

## Flujo Git recomendado
- `main`: rama estable
- `develop`: integracion de cambios
- `feature/*`: nuevas funcionalidades
- Pull Request obligatorio con revision de codigo
