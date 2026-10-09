# Storage Layout

The HomeLab separates desired configuration, service runtime state, and user storage.

## Locations

| Location | Purpose | Managed by Git |
| --- | --- | --- |
| `~/repos/HomeLab` | Desired configuration, documentation, Compose files, Caddyfile, Homepage YAML, scripts. | Yes |
| `${HOMELAB_STATE_DIR}` | Service runtime state, databases, generated config, service logs, PKI material, app metadata. | No |
| `${HOMELAB_STORAGE_DIR}` | User data such as media, photos, documents, and backups. | No |

Defaults:

```env
HOMELAB_STATE_DIR=/homelab/state
HOMELAB_STORAGE_DIR=/homelab/storage
```

These paths are host-specific and are configured through `.env`.

## Expected Tree

```text
/homelab
|-- state
|   |-- caddy
|   |-- jellyfin
|   |-- technitium
|   |-- uptime-kuma
|   `-- ...
`-- storage
    |-- media
    |   |-- Movies
    |   `-- Series
    |-- photos
    |-- documents
    `-- backups
```

## Current Service State

| Service | Runtime state |
| --- | --- |
| Caddy | `${HOMELAB_STATE_DIR}/caddy/data`, `${HOMELAB_STATE_DIR}/caddy/config` |
| Technitium | `${HOMELAB_STATE_DIR}/technitium/config`, `${HOMELAB_STATE_DIR}/technitium/logs` |
| Uptime Kuma | `${HOMELAB_STATE_DIR}/uptime-kuma/data` |
| Jellyfin | `${HOMELAB_STATE_DIR}/jellyfin/config`, `${HOMELAB_STATE_DIR}/jellyfin/cache` |
| Prowlarr | `${HOMELAB_STATE_DIR}/prowlarr/config` |
| Radarr | `${HOMELAB_STATE_DIR}/radarr/config` |
| Sonarr | `${HOMELAB_STATE_DIR}/sonarr/config` |
| Grafana | `${HOMELAB_STATE_DIR}/grafana/data` |
| Prometheus | `${HOMELAB_STATE_DIR}/prometheus/data` |
| Homepage | Git-managed YAML in `applications/homepage/config/` |
| Glances | Git-managed config in `applications/glances/config/glances.conf` |
| OpenSpeedTest | No persistent state |

Homepage, Glances, Prometheus, and Grafana provisioning keep static configuration in Git because those files describe desired configuration, not runtime state. Grafana dashboards created in the UI live in Grafana runtime state unless they are exported and committed under `applications/monitoring/config/grafana/dashboards/`.

## Jellyfin Layout

Jellyfin uses this layout:

```yaml
volumes:
  - ${HOMELAB_STATE_DIR:-/homelab/state}/jellyfin/config:/config
  - ${HOMELAB_STATE_DIR:-/homelab/state}/jellyfin/cache:/cache
  - ${HOMELAB_STORAGE_DIR:-/homelab/storage}/media:/media:ro
```

## Media Management Layout

Radarr mounts `${HOMELAB_STORAGE_DIR}/media/Movies` read-write at `/data/media/Movies`; Sonarr mounts `${HOMELAB_STORAGE_DIR}/media/Series` read-write at `/data/media/Series`. Prowlarr mounts no user storage. The library paths remain stable for later download integration, while the initial mounts limit each application to its own collection.

On the current Ubuntu server, the existing storage root is `/home/vinser52/homelab/storage`, with UID/GID `1000:1000`. Set that absolute path in the local `.env`; preserve the deployment's existing state path independently. Repository defaults remain generic. Missing media bind sources fail rather than being automatically created.

Downloads are deferred. When introduced, they must live separately from library roots. Review the enclosing mounts and filesystem at that time so downloads and media share a common mount for hardlinks and atomic moves. See [Media Management Setup](media-management.md).

## Rationale

Service state is separated from Git so the repository stays clean, reproducible, and safe to share.

User data is separated from service state because media, photos, documents, and backups have different backup and storage needs than application databases or generated config.

State should live on fast SSD storage where practical. User storage may later move to DAS, ZFS, or another larger storage backend without changing the repository layout.

Do not use `/srv` or `/var/lib/homelab` for this HomeLab. Use the configured `/homelab` layout unless a future architecture decision changes it.
