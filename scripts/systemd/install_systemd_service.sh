#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="vietnam-stock-pipeline.service"
REPO_DIR="/u01/Vanh_projects/vietnam-stock-pipeline"
SOURCE_UNIT="${REPO_DIR}/scripts/systemd/${SERVICE_NAME}"
TARGET_UNIT="/etc/systemd/system/${SERVICE_NAME}"

if [[ ! -f "${SOURCE_UNIT}" ]]; then
  echo "Missing unit file: ${SOURCE_UNIT}"
  exit 1
fi

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run as root: sudo bash ${SOURCE_UNIT%/*}/install_systemd_service.sh"
  exit 1
fi

cp "${SOURCE_UNIT}" "${TARGET_UNIT}"
chmod 644 "${TARGET_UNIT}"

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

echo "Installed and started ${SERVICE_NAME}"
systemctl status "${SERVICE_NAME}" --no-pager
