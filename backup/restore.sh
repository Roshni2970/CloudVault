#!/bin/bash

set -e

BACKUP_DIR="/local_backups"

BACKUP_NAME="$1"

if [ -z "$BACKUP_NAME" ]; then

    echo "No backup specified."

    exit 1

fi


BACKUP_FILE="${BACKUP_DIR}/${BACKUP_NAME}"


if [ ! -f "$BACKUP_FILE" ]; then

    echo "Backup file not found:"
    echo "$BACKUP_FILE"

    exit 1

fi


echo "=========================================="
echo "CloudVault Disaster Recovery"
echo "=========================================="

echo "[$(date)] Restoring:"
echo "$BACKUP_NAME"


echo "[$(date)] Dropping existing database connections..."


PGPASSWORD="${POSTGRES_PASSWORD}" \
psql \
    -h "${POSTGRES_HOST}" \
    -U "${POSTGRES_USER}" \
    -d postgres \
    -c "
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = '${POSTGRES_DB}'
        AND pid <> pg_backend_pid();
    " || true


echo "[$(date)] Recreating database..."


PGPASSWORD="${POSTGRES_PASSWORD}" \
psql \
    -h "${POSTGRES_HOST}" \
    -U "${POSTGRES_USER}" \
    -d postgres \
    -c "DROP DATABASE IF EXISTS ${POSTGRES_DB};"


PGPASSWORD="${POSTGRES_PASSWORD}" \
psql \
    -h "${POSTGRES_HOST}" \
    -U "${POSTGRES_USER}" \
    -d postgres \
    -c "CREATE DATABASE ${POSTGRES_DB};"


echo "[$(date)] Importing backup..."


gunzip -c "$BACKUP_FILE" | \
PGPASSWORD="${POSTGRES_PASSWORD}" \
psql \
    -h "${POSTGRES_HOST}" \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}"


echo "=========================================="
echo "RESTORE COMPLETED SUCCESSFULLY"
echo "=========================================="