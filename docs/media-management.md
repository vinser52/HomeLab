# Media Management Setup

Prowlarr manages indexers, Radarr manages movies, and Sonarr manages series. This first phase installs the applications and registers the existing media library. A download client, download folders, indexer selection, and automatic acquisition are deferred.

## Contracts And Storage

| Application | LAN URL | Docker address | Library root |
| --- | --- | --- | --- |
| Prowlarr | `https://prowlarr.home.arpa` | `http://prowlarr:9696` | None |
| Radarr | `https://radarr.home.arpa` | `http://radarr:7878` | `/data/media/Movies` |
| Sonarr | `https://sonarr.home.arpa` | `http://sonarr:8989` | `/data/media/Series` |

Caddy terminates HTTPS with the existing internal CA. Wildcard DNS already covers these names. The applications communicate using Docker service names, avoiding LAN DNS and certificate dependencies for internal API calls.

Each application stores its database, settings, credentials, and API keys under `${HOMELAB_STATE_DIR}/<application>/config`. These paths belong outside Git and are included by the existing state-backup tool. Stop the applications before making a filesystem backup of their databases.

Radarr sees only Movies and Sonarr sees only Series, with write access required for library management. Unmonitored items can still be renamed or deleted manually; monitoring is an acquisition setting, not filesystem protection. Jellyfin continues reading the same host library read-only through its existing `/media` mount.

## Prepare The Ubuntu Server

Run deployment commands from the repository root on the Ubuntu server. Validation on the MacBook is fine, but do not launch the stack through a remote Docker context from the MacBook.

Update these entries in the server's existing local `.env`:

```env
HOMELAB_STORAGE_DIR=/home/vinser52/homelab/storage
HOMELAB_UID=1000
HOMELAB_GID=1000
HOMELAB_TZ=Europe/Berlin
```

The storage path and UID/GID were confirmed on this server. Preserve the existing `HOMELAB_STATE_DIR`; the storage location does not establish where existing application state lives. This shared storage setting also affects Jellyfin, so confirm it points to the library Jellyfin already uses.

Load the local settings and verify the library directories:

```bash
set -a
. ./.env
set +a
ls -ld "${HOMELAB_STORAGE_DIR}/media/Movies" "${HOMELAB_STORAGE_DIR}/media/Series"
find "${HOMELAB_STORAGE_DIR}/media/Series" -maxdepth 4 -type f | head -40
```

The movie sample already uses `Movie Title (Year)/Movie Title (Year).mkv`. Russian names can be retained; review title matches during import. Series should have one folder per show and recognizable episode identifiers such as `S01E01`, optionally inside `Season 01` directories. The previous depth-limited listing did not reach episode files inside season folders, so verify these before importing.

Prepare only the new configuration directories:

```bash
sudo install -d -m 0750 -o "${HOMELAB_UID}" -g "${HOMELAB_GID}" \
  "${HOMELAB_STATE_DIR:-/homelab/state}/prowlarr/config" \
  "${HOMELAB_STATE_DIR:-/homelab/state}/radarr/config" \
  "${HOMELAB_STATE_DIR:-/homelab/state}/sonarr/config"
```

Do not recursively change media ownership as a default preparation step. Existing folders are owned by UID/GID 1000; inspect specific file permissions if a scan reports access errors.

## Deploy And Check

After transferring the Git changes to the Ubuntu server:

```bash
docker compose config --quiet
docker compose pull prowlarr radarr sonarr
docker compose up -d prowlarr radarr sonarr
docker compose up -d --force-recreate caddy
docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker compose restart homepage
docker compose ps prowlarr radarr sonarr caddy
docker compose logs --tail=100 prowlarr radarr sonarr
```

Caddy's admin API is disabled, so recreate it to activate the new routes. A brief interruption of existing proxied services is expected. The Homepage restart refreshes its updated service cards.

Check container identity and root-folder access:

```bash
docker compose exec radarr id
docker compose exec sonarr id
docker compose exec radarr sh -c 'test -r /data/media/Movies && test -w /data/media/Movies'
docker compose exec sonarr sh -c 'test -r /data/media/Series && test -w /data/media/Series'
docker compose exec radarr ls -la /data/media/Movies
docker compose exec sonarr ls -la /data/media/Series
```

Open all three LAN URLs. Use the existing trusted Caddy CA on client devices. For a routing check before the CA is trusted:

```bash
curl -k -I https://prowlarr.home.arpa
curl -k -I https://radarr.home.arpa
curl -k -I https://sonarr.home.arpa
```

A setup page, login redirect, or authentication response is expected; a Caddy `502` indicates an upstream problem. These checks establish routing, while the browser setup and library checks establish application readiness.

## Authentication And Initial Settings

In each application, configure Forms authentication and require authentication for all requests, including local addresses. Create administrator credentials in the UI and leave URL Base empty because each application has its own hostname. Keep the application HTTP listener enabled internally; Caddy provides client-facing HTTPS.

Store credentials and API keys only in runtime configuration. Homepage initially uses links rather than authenticated widgets, so no new API tokens are needed in `.env`.

In Radarr and Sonarr:

1. Leave movie/episode renaming disabled and leave metadata writers disabled.
2. Keep media permission-changing options disabled.
3. Add the library root shown in the table above.
4. Leave download clients, import lists, and automatic searches unconfigured.

Health warnings about missing indexers or download clients are expected in this phase. Authentication, permission, or missing-root-folder errors should be resolved before import.

## Import Existing Movies

In Radarr, use **Movies -> Import Existing Movies / Library Import**, select `/data/media/Movies`, and review each folder's title and year. Correct ambiguous or unmatched titles manually. Select a quality profile for future use, choose **Monitor: None** (unmonitored), and leave any search-on-import option disabled.

Import one movie first and confirm that its existing file is detected before importing the rest. Library Import registers an organized collection in place; it does not require copying the files to a new library. Do not use a download-folder Manual Import workflow for this collection. No bulk rename or root-folder move is part of this setup.

Radarr manages a single primary movie file per movie. If a movie folder contains multiple editions or video files, review which one is detected before relying on Radarr to manage it.

## Import Existing Series

In Sonarr, use **Series -> Import Existing Series / Library Import**, select `/data/media/Series`, and review the match for each show. Select a quality profile and **Monitor: None**, then import one series first. Verify that the detected seasons and episodes match its existing files before importing the remainder. Correct unusual or unmatched episode names through Sonarr's episode-management UI after reviewing the files.

Unmonitored movies and series remain visible and can be scanned and managed. Automatic acquisition is disabled for those items; a deliberate manual search remains possible once acquisition is configured later.

After import, confirm that Jellyfin still sees and plays the existing media at its current paths.

## Connect Prowlarr To The Applications

Under **Settings -> Apps** in Prowlarr, add Radarr and Sonarr using:

| Field | Radarr connection | Sonarr connection |
| --- | --- | --- |
| Prowlarr Server | `http://prowlarr:9696` | `http://prowlarr:9696` |
| Application Server | `http://radarr:7878` | `http://sonarr:8989` |
| API Key | Radarr's own key from Settings -> General | Sonarr's own key from Settings -> General |
| Sync Level | Full Sync | Full Sync |

Full Sync makes Prowlarr the owner of indexer configuration in both applications. Add indexers through Prowlarr when that phase begins. Test and save the connections; if an indexer-related test cannot complete with an empty indexer list, defer that connection until indexers are selected. Do not add indexers or a download client merely to clear a first-phase warning.

## Next Phase: Downloads

No download directory needs to exist yet. When a client is chosen, keep `/data/media/Movies` and `/data/media/Series` as the application root paths, and introduce a separate download tree such as `/data/downloads`.

Review bind mounts in that change. For hardlinks and atomic moves, downloads and media must be on the same filesystem and visible through a common mount within Radarr/Sonarr; simply adding a second independent download bind mount is insufficient. Choose the smallest appropriate shared tree then, without exposing unrelated photos, documents, or backups. Container library paths can stay stable even if the enclosing bind mount changes.

## References

- [Radarr library import](https://github.com/Servarr/Wiki/blob/master/radarr/library.md)
- [Sonarr quick start and library import](https://wiki.servarr.com/sonarr/quick-start-guide)
- [Prowlarr quick start](https://wiki.servarr.com/prowlarr/quick-start-guide)
- [LinuxServer non-root operation](https://docs.linuxserver.io/misc/non-root/)
- [LinuxServer Radarr storage guidance](https://docs.linuxserver.io/images/docker-radarr/#media-folders)
