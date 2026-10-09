# Prowlarr

Prowlarr manages media indexers and synchronizes them with Radarr and Sonarr.

Public URL: `https://prowlarr.home.arpa`.

Caddy connects to `prowlarr:9696` on the shared `proxy` network. The application does not publish HTTP ports to the LAN.

## Image And Runtime State

Pinned image: `lscr.io/linuxserver/prowlarr:2.6.5.5623-ls163`.

Configuration, API keys, and the database live in `${HOMELAB_STATE_DIR}/prowlarr/config`, mounted at `/config`. This is runtime state outside Git.

The container uses LinuxServer's supported non-root operation with `user: "${HOMELAB_UID}:${HOMELAB_GID}"`. Prepare the config directory with this ownership before starting. PUID/PGID are intentionally omitted because they have no effect when an explicit container user is set. No Docker Mods or custom init scripts are required.

Timezone comes from `HOMELAB_TZ`, defaulting to `Europe/Berlin`.

## Filesystem Access

Prowlarr only mounts its configuration directory. It does not need access to movie, series, or download files.

## Setup And Validation

Follow the shared [media management setup guide](../../docs/media-management.md) for host preparation, deployment, authentication, application connections, and deferred download-client setup.

Image documentation: [LinuxServer Prowlarr](https://docs.linuxserver.io/images/docker-prowlarr/).
Non-root behavior: [LinuxServer non-root operation](https://docs.linuxserver.io/misc/non-root/).

For troubleshooting on the Ubuntu server:

```bash
docker compose logs --tail=100 prowlarr
docker compose exec prowlarr id
```

