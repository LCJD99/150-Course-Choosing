#!/usr/bin/env bash
set -euo pipefail

# Usage: ./migrate_with_backup.sh [backend_dir]
BACKEND_DIR="${1:-$(pwd)}"
DB_REL_PATH="data/course_selection.db"
BACKUP_DIR_REL="data/backups"
ALEMBIC_CMD="python3 -m alembic"

DB_PATH="${BACKEND_DIR}/${DB_REL_PATH}"
BACKUP_DIR="${BACKEND_DIR}/${BACKUP_DIR_REL}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_PATH="${BACKUP_DIR}/course_selection_${TIMESTAMP}.db"

echo "[INFO] backend dir: ${BACKEND_DIR}"
echo "[INFO] db path    : ${DB_PATH}"

if [[ ! -d "${BACKEND_DIR}" ]]; then
  echo "[ERROR] backend dir not found: ${BACKEND_DIR}"
  exit 1
fi

if [[ ! -f "${BACKEND_DIR}/alembic.ini" ]]; then
  echo "[ERROR] alembic.ini not found in: ${BACKEND_DIR}"
  exit 1
fi

mkdir -p "${BACKUP_DIR}"

if [[ -f "${DB_PATH}" ]]; then
  cp "${DB_PATH}" "${BACKUP_PATH}"
  echo "[INFO] backup created: ${BACKUP_PATH}"
else
  echo "[WARN] database file not found, skip backup"
fi

cd "${BACKEND_DIR}"
echo "[INFO] running migration: upgrade head"
${ALEMBIC_CMD} upgrade head

echo "[INFO] current revision:"
${ALEMBIC_CMD} current

echo "[OK] migration completed successfully"

if [[ -f "${BACKUP_PATH}" ]]; then
  echo "[HINT] restore command if needed:"
  echo "       cp \"${BACKUP_PATH}\" \"${DB_PATH}\""
fi
