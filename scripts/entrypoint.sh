#!/bin/bash

echo "Initializing database..."
# Initialize db tables if they don't exist
python -c "
from app import create_app
from database import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables created/verified')
" || echo "Database initialization warning, continuing..."

echo "Starting application..."
exec gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 app:app