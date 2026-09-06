CloudVault 🛡️

CloudVault is an automated, containerized cloud backup and disaster recovery utility built with Docker, Bash, PostgreSQL, and rclone. It creates encrypted, compressed snapshots of persistent Docker volumes and database instances, syncing them seamlessly to free offsite cloud storage endpoints (such as Google Drive, MEGA, or S3-compatible targets) with retention management and one-click recovery.

Core Architecture Breakdown

<img width="2048" height="2048" alt="image" src="https://github.com/user-attachments/assets/e9c46e80-f559-40d7-97c4-b2bc215cccec" />

✨ Features
Automated Snapshot Creation: Creates compressed (.sql.gz) snapshots of database states and persistent Docker volumes.
Offsite Cloud Syncing: Integrates with rclone to transfer backups over encrypted TLS connections to Google Drive, MEGA, AWS S3, or any supported cloud provider.
Automated Retention Management: Automatically purges local backups older than 7 days to prevent host disk exhaustion.
Zero-Downtime Recovery: Includes dedicated disaster recovery scripts to pull the latest remote snapshot and restore data.
Fully Containerized: Zero local dependencies required on the host beyond Docker and Docker Compose.

🛠️ Tech Stack
Frontend: HTML, CSS, JavaScript
Backend: Python, Flask
Database: PostgreSQL 16
Containerization: Docker, Docker Compose
Backup: pg_dump, Bash, Gzip
Cloud Storage: Rclone
Operating System: Windows + Docker Desktop
Version Control: Git & GitHub

Core Technologies:
Python + Flask + PostgreSQL + Docker + Docker Compose + Bash + Rclone



