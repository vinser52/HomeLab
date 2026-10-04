#!/usr/bin/env bash

set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage: backup-state.sh DESTINATION

Create a timestamped archive of HOMELAB_STATE_DIR inside DESTINATION.

Example:
  sudo ./tools/backup-state.sh /mnt/backup/homelab
EOF
}

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 2
fi

for required_command in tar gzip; do
  if ! command -v "${required_command}" >/dev/null 2>&1; then
    echo "Error: ${required_command} is not installed." >&2
    exit 1
  fi
done

if command -v sha256sum >/dev/null 2>&1; then
  checksum_command=(sha256sum)
elif command -v shasum >/dev/null 2>&1; then
  checksum_command=(shasum -a 256)
else
  echo "Error: sha256sum or shasum is required." >&2
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
archive_name="${backup_name}.tar.gz"
partial_path="${destination_path}/.${archive_name}.partial"
partial_checksum_path="${partial_path}.sha256"
backup_path="${destination_path}/${archive_name}"
checksum_path="${backup_path}.sha256"

if [[ -e "${partial_path}" || -e "${partial_checksum_path}" || \
      -e "${backup_path}" || -e "${checksum_path}" ]]; then
  echo "Error: backup path already exists for timestamp ${timestamp}." >&2
  exit 1
fi

echo "Backing up: ${source_path}"
echo "Destination: ${backup_path}"
echo "Excluded: ${source_path}/prometheus/data"
echo

tar_help="$(tar --help 2>&1)"
tar_options=(
  --create
  --file=-
  --numeric-owner
  --exclude=./prometheus/data
)

if grep -q -- '--acls' <<<"${tar_help}"; then
  tar_options+=(--acls)
fi

if grep -q -- '--xattrs' <<<"${tar_help}"; then
  tar_options+=(--xattrs)
fi

if grep -q -- '--one-file-system' <<<"${tar_help}"; then
  tar_options+=(--one-file-system)
fi

echo "Creating compressed archive"
if command -v pv >/dev/null 2>&1; then
  tar "${tar_options[@]}" -C "${source_path}" . \
    | pv \
    | gzip --fast > "${partial_path}"
elif dd --help 2>&1 | grep -q -- 'status='; then
  tar "${tar_options[@]}" -C "${source_path}" . \
    | dd bs=1M status=progress \
    | gzip --fast > "${partial_path}"
else
  echo "Progress details are unavailable; install pv for byte and rate output."
  tar "${tar_options[@]}" -C "${source_path}" . \
    | gzip --fast > "${partial_path}"
fi

echo
echo "Generating SHA-256 checksum"
checksum="$("${checksum_command[@]}" "${partial_path}" | awk '{print $1}')"
printf '%s  %s\n' "${checksum}" "${archive_name}" > "${partial_checksum_path}"

mv -- "${partial_path}" "${backup_path}"
mv -- "${partial_checksum_path}" "${checksum_path}"

echo
echo "Backup completed: ${backup_path}"
echo "Checksum: ${checksum_path}"
