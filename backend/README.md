# FastAPI Backend

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── models/              # SQLAlchemy models
├── api/                 # API routes
│   ├── student/         # Student endpoints
│   └── admin/           # Admin endpoints
├── services/            # Business logic
├── database.py          # Database configuration
├── requirements.txt     # Python dependencies
└── alembic.ini          # Alembic configuration
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   alembic upgrade head
   ```

3. Start server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
