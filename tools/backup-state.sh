#!/usr/bin/env bash

set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage: backup-state.sh DESTINATION

Create a timestamped rsync backup of HOMELAB_STATE_DIR inside DESTINATION.

Example:
  sudo ./tools/backup-state.sh /mnt/backup/homelab
EOF
}

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 2
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "Error: rsync is not installed." >&2
  exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_dir="$(dirname -- "${script_dir}")"

# Docker Compose reads the repository .env automatically, but shell scripts do
# not. Load it when present while preserving an explicitly exported value.
configured_state_dir="${HOMELAB_STATE_DIR:-}"
if [[ -f "${repository_dir}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${repository_dir}/.env"
  set +a
fi
if [[ -n "${configured_state_dir}" ]]; then
  HOMELAB_STATE_DIR="${configured_state_dir}"
fi
HOMELAB_STATE_DIR="${HOMELAB_STATE_DIR:-/homelab/state}"

destination_root="$1"

if [[ ! -d "${HOMELAB_STATE_DIR}" ]]; then
  echo "Error: state directory does not exist: ${HOMELAB_STATE_DIR}" >&2
  exit 1
fi

mkdir -p -- "${destination_root}"

source_path="$(cd -- "${HOMELAB_STATE_DIR}" && pwd -P)"
destination_path="$(cd -- "${destination_root}" && pwd -P)"

case "${destination_path}/" in
  "${source_path}/"*)
    echo "Error: destination must not be inside HOMELAB_STATE_DIR." >&2
    exit 1
    ;;
esac

timestamp="$(date +%Y%m%d-%H%M%S)"
backup_name="homelab-state-${timestamp}"
partial_path="${destination_path}/.${backup_name}.partial"
backup_path="${destination_path}/${backup_name}"

if [[ -e "${partial_path}" || -e "${backup_path}" ]]; then
  echo "Error: backup path already exists for timestamp ${timestamp}." >&2
  exit 1
fi

mkdir -- "${partial_path}"

echo "Backing up: ${source_path}"
echo "Destination: ${backup_path}"
echo

rsync_help="$(rsync --help 2>&1)"
rsync_options=(
  --archive
  --hard-links
  --numeric-ids
  --exclude=/prometheus/data/
  --stats
  -h
)

if grep -q -- '--acls' <<<"${rsync_help}"; then
  rsync_options+=(--acls)
fi

if grep -q -- '--xattrs' <<<"${rsync_help}"; then
  rsync_options+=(--xattrs)
elif grep -q -- '--extended-attributes' <<<"${rsync_help}"; then
  rsync_options+=(--extended-attributes)
fi

if grep -q -- '--info' <<<"${rsync_help}"; then
  rsync_options+=(--info=progress2)
else
  rsync_options+=(--progress)
fi

rsync "${rsync_options[@]}" -- "${source_path}/" "${partial_path}/"

mv -- "${partial_path}" "${backup_path}"

echo
echo "Backup completed: ${backup_path}"
