#!/bin/bash

set -e

BACKUP_DIR="/local_backups"

INTERVAL="${BACKUP_INTERVAL:-300}"

REMOTE_TARGET="${RCLONE_REMOTE:-}"

mkdir -p "$BACKUP_DIR"


create_backup() {

    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

    BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql.gz"

    echo "=========================================="
    echo "CloudVault Backup"
    echo "=========================================="

    echo "[$(date)] Starting PostgreSQL backup..."

    PGPASSWORD="${POSTGRES_PASSWORD}" \
    pg_dump \
        -h "${POSTGRES_HOST}" \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        | gzip > "${BACKUP_FILE}"


    echo "[$(date)] Backup created:"
    echo "${BACKUP_FILE}"


    if [ -n "$REMOTE_TARGET" ]; then

        echo "[$(date)] Uploading backup to cloud..."

        rclone copy \
            "${BACKUP_FILE}" \
            "${REMOTE_TARGET}"

        echo "[$(date)] Cloud upload completed."

    else

        echo "[$(date)] Cloud storage not configured."
        echo "[$(date)] Running in local backup mode."

    fi


    # Keep local backups for 7 days

    find "$BACKUP_DIR" \
        -type f \
        -name "*.sql.gz" \
        -mtime +7 \
        -delete


    echo "[$(date)] Backup completed successfully."

    echo

}


echo "=========================================="
echo "CloudVault Backup Worker"
echo "=========================================="

echo "Backup interval: ${INTERVAL} seconds"


while true; do

    # Manual backup trigger

    if [ -f "${BACKUP_DIR}/.backup_now" ]; then

        echo "[$(date)] Manual backup requested."

        rm -f "${BACKUP_DIR}/.backup_now"

        create_backup

    fi


    # Restore trigger

    for RESTORE_FILE in "${BACKUP_DIR}"/.restore_*.sql.gz; do

        if [ -f "$RESTORE_FILE" ]; then

            BACKUP_NAME=$(basename "$RESTORE_FILE")

            BACKUP_NAME="${BACKUP_NAME#.restore_}"

            echo "[$(date)] Restore requested:"
            echo "$BACKUP_NAME"

            rm -f "$RESTORE_FILE"

            /app/restore.sh "$BACKUP_NAME"

        fi

    done


    # Automatic backup timer

    CURRENT_TIME=$(date +%s)

    if [ -z "$LAST_BACKUP_TIME" ]; then

        LAST_BACKUP_TIME=0

    fi


    ELAPSED=$((CURRENT_TIME - LAST_BACKUP_TIME))


    if [ "$ELAPSED" -ge "$INTERVAL" ]; then

        create_backup

        LAST_BACKUP_TIME=$(date +%s)

    fi


    sleep 5

done