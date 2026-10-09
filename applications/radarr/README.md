# Radarr

Radarr manages the existing movie library.

Public URL: `https://radarr.home.arpa`.

Caddy connects to `radarr:7878` on the shared `proxy` network. The application does not publish HTTP ports to the LAN.

## Image And Runtime State

Pinned image: `lscr.io/linuxserver/radarr:6.4.4.10685-ls319`.

Configuration, API keys, and the database live in `${HOMELAB_STATE_DIR}/radarr/config`, mounted at `/config`. This is runtime state outside Git.

The container uses LinuxServer's supported non-root operation with `user: "${HOMELAB_UID}:${HOMELAB_GID}"`. Prepare the config directory with this ownership before starting. PUID/PGID are intentionally omitted because they have no effect when an explicit container user is set. No Docker Mods or custom init scripts are required.

Timezone comes from `HOMELAB_TZ`, defaulting to `Europe/Berlin`.

## Library Access

`${HOMELAB_STORAGE_DIR}/media/Movies` is mounted read-write at `/data/media/Movies`. Radarr requires a writable root folder to manage its library. The bind mount refuses to create a missing host library, so a wrong base path fails instead of showing an empty collection.

Use `/data/media/Movies` as the application root folder. Keep it stable when download support is added later. No download folder or client is configured in this phase.

## Setup And Validation

Follow the shared [media management setup guide](../../docs/media-management.md) for host preparation, deployment, authentication, existing-library import, and deferred download-client setup.

Image documentation: [LinuxServer Radarr](https://docs.linuxserver.io/images/docker-radarr/).
Non-root behavior: [LinuxServer non-root operation](https://docs.linuxserver.io/misc/non-root/).

For troubleshooting on the Ubuntu server:

```bash
docker compose logs --tail=100 radarr
docker compose exec radarr id
docker compose exec radarr ls -la /data/media/Movies
```

