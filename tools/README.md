# HomeLab Tools

## State Backup

`backup-state.sh` creates a timestamped copy of `${HOMELAB_STATE_DIR}` with
`rsync`. It is intended for manual local backups before maintenance and during
the current early HomeLab stage.

The script reads `HOMELAB_STATE_DIR` from the repository `.env` file when it is
available and otherwise uses `/homelab/state`.

### Requirements

- Run the script on the Ubuntu HomeLab server.
- Install `rsync` on the server.
- Use a destination outside `${HOMELAB_STATE_DIR}`.
- Run with enough permissions to read every service's state files. This will
  normally require `sudo`.

### Create A Consistent Backup

Stop the Compose services so applications flush their databases and do not
change files while `rsync` reads them:

```bash
docker compose stop
sudo ./tools/backup-state.sh /path/to/backup-folder
docker compose start
```

Replace `/path/to/backup-folder` with the mounted disk or directory that should
contain the backup.

The script displays transfer progress and statistics. A successful run creates
a directory such as:

```text
/path/to/backup-folder/homelab-state-20261004-130730/
```

Each run creates a new timestamped directory. Existing backups are not changed
or automatically removed.

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

The script first writes into a hidden directory whose name ends in `.partial`.
It removes that marker only after `rsync` completes successfully. A remaining
`.partial` directory is incomplete and must not be used as a known-good backup.

The script does not restart services itself. If the backup fails, run:

```bash
docker compose start
```

### Restore

Stop the Compose services before restoring. Review the source and destination
carefully, then copy the contents of the selected backup into the state
directory:

```bash
docker compose stop
set -a
. ./.env
set +a
sudo rsync --archive --hard-links --numeric-ids --info=progress2 \
  /path/to/backup-folder/homelab-state-YYYYMMDD-HHMMSS/ \
  "${HOMELAB_STATE_DIR:-/homelab/state}/"
docker compose start
```

Validate DNS and application access after the restore. Prometheus starts with
an empty time-series database because that data is not part of the backup.

### Recovery Boundary

A backup stored on the same physical disk as `${HOMELAB_STATE_DIR}` does not
protect against disk failure. Prefer a separately mounted disk for meaningful
local recovery, and add an off-site copy if the HomeLab begins storing
irreplaceable data.
