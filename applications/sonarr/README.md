# Sonarr

Sonarr manages the existing series library.

Public URL: `https://sonarr.home.arpa`.

Caddy connects to `sonarr:8989` on the shared `proxy` network. The application does not publish HTTP ports to the LAN.

## Image And Runtime State

Pinned image: `lscr.io/linuxserver/sonarr:4.0.20.3014-ls326`.

Configuration, API keys, and the database live in `${HOMELAB_STATE_DIR}/sonarr/config`, mounted at `/config`. This is runtime state outside Git.

The container uses LinuxServer's supported non-root operation with `user: "${HOMELAB_UID}:${HOMELAB_GID}"`. Prepare the config directory with this ownership before starting. PUID/PGID are intentionally omitted because they have no effect when an explicit container user is set. No Docker Mods or custom init scripts are required.

Timezone comes from `HOMELAB_TZ`, defaulting to `Europe/Berlin`.

## Library Access

`${HOMELAB_STORAGE_DIR}/media/Series` is mounted read-write at `/data/media/Series`. Sonarr requires a writable root folder to manage its library. The bind mount refuses to create a missing host library, so a wrong base path fails instead of showing an empty collection.

Use `/data/media/Series` as the application root folder. Keep it stable when download support is added later. No download folder or client is configured in this phase.

## Setup And Validation

Follow the shared [media management setup guide](../../docs/media-management.md) for host preparation, deployment, authentication, existing-library import, and deferred download-client setup.

Image documentation: [LinuxServer Sonarr](https://docs.linuxserver.io/images/docker-sonarr/).
Non-root behavior: [LinuxServer non-root operation](https://docs.linuxserver.io/misc/non-root/).

For troubleshooting on the Ubuntu server:

```bash
docker compose logs --tail=100 sonarr
docker compose exec sonarr id
docker compose exec sonarr ls -la /data/media/Series
```

