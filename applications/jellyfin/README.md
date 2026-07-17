# Jellyfin

Jellyfin is the HomeLab media streaming application.

Public URL:

```text
https://jellyfin.home.arpa
```

The container does not publish port `8096` directly to the LAN. Caddy reaches it over Docker networking at:

```text
jellyfin:8096
```

## Image

The HomeLab pins the official Jellyfin image to:

```text
docker.io/jellyfin/jellyfin:10.11.0
```

As of July 17, 2026, `10.11.0` is the latest stable Jellyfin release. `12.0` is still only available as release candidates and is intentionally not used here.

## Required Environment Variables

Set these values in the local `.env` file on the Ubuntu HomeLab server:

```env
LOCAL_DOMAIN=home.arpa
HOMELAB_STATE_DIR=/homelab/state
HOMELAB_STORAGE_DIR=/homelab/storage
HOMELAB_UID=1000
HOMELAB_GID=1000
JELLYFIN_VIDEO_GID=44
JELLYFIN_RENDER_GID=109
```

Notes:

- `HOMELAB_UID` and `HOMELAB_GID` should match the non-root host user that should own Jellyfin runtime files.
- `JELLYFIN_VIDEO_GID` and `JELLYFIN_RENDER_GID` must match the host group IDs that own `/dev/dri/card*` and `/dev/dri/renderD*`.

## Required Host Directories

Jellyfin expects these host paths:

```text
${HOMELAB_STATE_DIR}/jellyfin/config
${HOMELAB_STATE_DIR}/jellyfin/cache
${HOMELAB_STORAGE_DIR}/media
${HOMELAB_STORAGE_DIR}/media/Movies
${HOMELAB_STORAGE_DIR}/media/Series
```

Create the Jellyfin state directories on the Ubuntu HomeLab server before first start:

```bash
mkdir -p \
  "${HOMELAB_STATE_DIR}/jellyfin/config" \
  "${HOMELAB_STATE_DIR}/jellyfin/cache"
```

Ensure the runtime directories are writable by `HOMELAB_UID:HOMELAB_GID`:

```bash
sudo chown -R "${HOMELAB_UID}:${HOMELAB_GID}" "${HOMELAB_STATE_DIR}/jellyfin"
```

Media stays in the existing shared storage tree and is mounted read-only into the container at `/media`.

## Intel Quick Sync Preparation

Jellyfin runs as a non-root user and receives GPU access through supplementary groups plus `/dev/dri`.

Check the Intel GPU devices and owning groups on the Ubuntu HomeLab server:

```bash
ls -l /dev/dri
getent group video
getent group render
id "${USER}"
```

Typical Debian or Ubuntu values are `video=44` and `render=109`, but confirm them on the host before deployment.

If the directories do not exist or the GPU is missing, verify that:

1. The Intel iGPU is enabled in BIOS.
2. The host kernel exposes `/dev/dri/renderD128` or a similar render node.
3. The host has working Intel graphics drivers.

## Host Preparation Commands

Run these commands on the Ubuntu HomeLab server after updating `.env`:

```bash
mkdir -p \
  "${HOMELAB_STATE_DIR}/jellyfin/config" \
  "${HOMELAB_STATE_DIR}/jellyfin/cache"
sudo chown -R "${HOMELAB_UID}:${HOMELAB_GID}" "${HOMELAB_STATE_DIR}/jellyfin"
ls -l /dev/dri
```

## Deployment

From the repository root on the Ubuntu HomeLab server:

```bash
docker compose config
docker compose up -d jellyfin caddy homepage
docker compose ps
docker compose logs --tail=100 jellyfin
docker compose logs --tail=100 caddy
```

If Docker on your current machine targets a remote host, do not start containers from that machine. Validate with `docker compose config`, commit the changes, and deploy from the actual Ubuntu HomeLab server instead.

## Validation

Validate the rendered Compose configuration:

```bash
docker compose config
```

Validate Caddy connectivity from a LAN client before trusting the Caddy root CA:

```bash
curl -k -I "https://jellyfin.${LOCAL_DOMAIN}"
```

After trusting the Caddy root CA:

```bash
curl -I "https://jellyfin.${LOCAL_DOMAIN}"
```

Validate that Jellyfin can see the GPU inside the container:

```bash
docker compose exec jellyfin ls -l /dev/dri
docker compose exec jellyfin id
```

Validate effective mounts:

```bash
docker compose exec jellyfin mount | grep -E " /config | /cache | /media "
docker compose exec jellyfin ls -la /media
docker compose exec jellyfin ls -la /media/Movies
docker compose exec jellyfin ls -la /media/Series
```

Validate Intel Quick Sync transcoding:

1. Open `https://jellyfin.home.arpa`.
2. Complete the first-time setup.
3. Enable hardware acceleration in Jellyfin administration with Intel Quick Sync Video, or VA-API if your Intel platform requires it.
4. Start a video that forces transcoding by lowering playback quality in the web client.
5. On the Ubuntu host, watch GPU activity:

```bash
sudo intel_gpu_top
```

When hardware transcoding works, the Intel video engines should show activity during the transcode.

## First-Time Setup

After the container is running:

1. Open `https://jellyfin.home.arpa`.
2. Create the administrator account.
3. Finish the initial server wizard.
4. Create the libraries manually:
   `Movies` -> `/media/Movies`
   `TV Shows` -> `/media/Series`
5. Configure hardware acceleration for Intel Quick Sync if desired.
6. Confirm playback and, if needed, a real transcoding session.

Do not automate library creation in this repository. The administrator should create the libraries manually in the Jellyfin UI.
