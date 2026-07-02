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
|   |-- technitium
|   |-- uptime-kuma
|   `-- jellyfin
`-- storage
    |-- media
    |   |-- Movies
    |   |-- TV
    |   `-- Music
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
| Homepage | Git-managed YAML in `applications/homepage/config/` |
| Glances | Git-managed config in `applications/glances/config/glances.conf` |
| OpenSpeedTest | No persistent state |

Homepage and Glances keep static configuration in Git because those files describe desired configuration, not runtime state.

## Future Jellyfin Layout

Jellyfin is not currently deployed. If it is added later, use this layout:

```yaml
volumes:
  - ${HOMELAB_STATE_DIR:-/homelab/state}/jellyfin/config:/config
  - ${HOMELAB_STATE_DIR:-/homelab/state}/jellyfin/cache:/cache
  - ${HOMELAB_STORAGE_DIR:-/homelab/storage}/media:/media:ro
```

## Rationale

Service state is separated from Git so the repository stays clean, reproducible, and safe to share.

User data is separated from service state because media, photos, documents, and backups have different backup and storage needs than application databases or generated config.

State should live on fast SSD storage where practical. User storage may later move to DAS, ZFS, or another larger storage backend without changing the repository layout.

Do not use `/srv` or `/var/lib/homelab` for this HomeLab. Use the configured `/homelab` layout unless a future architecture decision changes it.
