# HomeLab Tools

## State Backup

`backup-state.sh` creates a compressed, timestamped archive of
`${HOMELAB_STATE_DIR}`. It is intended for manual local backups before
maintenance and during the current early HomeLab stage.

The script reads `HOMELAB_STATE_DIR` from the repository `.env` file when it is
available and otherwise uses `/homelab/state`.

### Requirements

- Run the script on the Ubuntu HomeLab server.
- Ensure `tar`, `gzip`, and `sha256sum` are available. They are included in a
  normal Ubuntu Server installation.
- Use a destination outside `${HOMELAB_STATE_DIR}`.
- Run with enough permissions to read every service's state files. This will
  normally require `sudo`.

### Create A Consistent Backup

Stop the Compose services so applications flush their databases and do not
change files while the archive is created:

```bash
docker compose stop
sudo ./tools/backup-state.sh /path/to/backup-folder
docker compose start
```

Replace `/path/to/backup-folder` with the mounted disk or directory that should
contain the backup.

The script displays transferred bytes, rate, and elapsed time when `pv` is
installed. Otherwise, it uses GNU `dd` progress output, which is available on
Ubuntu. A successful run creates an archive and checksum such as:

```text
/path/to/backup-folder/homelab-state-20261004-130730.tar.gz
/path/to/backup-folder/homelab-state-20261004-130730.tar.gz.sha256
```

Each run creates a new timestamped archive. Existing backups are not changed or
automatically removed. Unix ownership, permissions, links, ACLs, and extended
attributes are stored inside the archive, so the destination filesystem does
not need to support them. This makes the format suitable for destinations such
as exFAT-formatted external disks.

### Included Data

The backup contains the service state under `${HOMELAB_STATE_DIR}`, including
Technitium configuration, Caddy state and internal PKI, Uptime Kuma data,
Jellyfin configuration, and Grafana state.

Prometheus time-series data is deliberately excluded:

```text
${HOMELAB_STATE_DIR}/prometheus/data/
```

Historical metrics are regenerable and can consume substantial backup space.
Other files under `${HOMELAB_STATE_DIR}/prometheus/` remain included.

### Interrupted Backups

The script first writes a hidden archive whose name ends in `.partial`. It
removes that marker only after archive creation and checksum generation succeed.
A remaining `.partial` file is incomplete and must not be used as a known-good
backup.

The script does not restart services itself. If the backup fails, run:

```bash
docker compose start
```

### Restore

Verify the archive checksum from its containing directory:

```bash
sha256sum --check homelab-state-YYYYMMDD-HHMMSS.tar.gz.sha256
```

Stop the Compose services before restoring. Review the archive and destination
carefully, then extract it into the state directory:

```bash
docker compose stop
set -a
. ./.env
set +a
sudo tar --extract --gzip --numeric-owner --same-owner --acls --xattrs \
  --file=/path/to/backup-folder/homelab-state-YYYYMMDD-HHMMSS.tar.gz \
  --directory="${HOMELAB_STATE_DIR:-/homelab/state}"
docker compose start
```

Validate DNS and application access after the restore. Prometheus starts with
an empty time-series database because that data is not part of the backup.

The archive retains Unix metadata even when it is stored on a filesystem that
cannot represent that metadata directly.

### Recovery Boundary

A backup stored on the same physical disk as `${HOMELAB_STATE_DIR}` does not
protect against disk failure. Prefer a separately mounted disk for meaningful
local recovery, and add an off-site copy if the HomeLab begins storing
irreplaceable data.
