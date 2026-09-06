FROM postgres:16-alpine

RUN apk add --no-cache \
    bash \
    gzip \
    coreutils \
    rclone

WORKDIR /app

COPY backup.sh /app/backup.sh
COPY restore.sh /app/restore.sh

RUN chmod +x /app/backup.sh /app/restore.sh

CMD ["/app/backup.sh"]