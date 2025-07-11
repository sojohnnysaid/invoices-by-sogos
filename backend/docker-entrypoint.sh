#!/bin/bash

echo "Waiting for database..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "Database is ready!"

echo "Running database migrations..."
# Try to run migrations
alembic upgrade head 2>&1 | tee /tmp/migration.log
MIGRATION_EXIT_CODE=${PIPESTATUS[0]}

if [ $MIGRATION_EXIT_CODE -ne 0 ]; then
  if grep -q "type \"invoicestatus\" already exists" /tmp/migration.log; then
    echo "Database already has schema, marking migration as complete..."
    python mark_migration_complete.py
    echo "Migration marked as complete, continuing..."
  else
    echo "Migration failed with unexpected error"
    cat /tmp/migration.log
    exit 1
  fi
else
  echo "Migrations completed successfully"
fi

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload