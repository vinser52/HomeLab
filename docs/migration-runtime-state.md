# Runtime State Migration

This document describes the manual migration from the old in-repository runtime data layout to the `/homelab` layout.

Do not delete old runtime directories until services are confirmed working from the new paths.

## 1. Prepare Directories

Run on the Ubuntu HomeLab server:

```bash
sudo mkdir -p /homelab/state /homelab/storage
sudo chown -R $USER:$USER /homelab
```

Create or update `.env`:

```env
HOMELAB_STATE_DIR=/homelab/state
HOMELAB_STORAGE_DIR=/homelab/storage
```

## 2. Stop Services

```bash
docker compose down
```

## 3. Copy Existing Runtime Data

Caddy:

```bash
mkdir -p /homelab/state/caddy
rsync -a infrastructure/caddy/data/ /homelab/state/caddy/data/
rsync -a infrastructure/caddy/config/ /homelab/state/caddy/config/
```

Technitium:

```bash
mkdir -p /homelab/state/technitium
rsync -a infrastructure/technitium/data/config/ /homelab/state/technitium/config/
rsync -a infrastructure/technitium/data/logs/ /homelab/state/technitium/logs/
```

Uptime Kuma:

```bash
mkdir -p /homelab/state/uptime-kuma
rsync -a applications/uptime-kuma/data/ /homelab/state/uptime-kuma/data/
```

If one of the old directories does not exist yet, skip that `rsync` command.

## 4. Start Services

```bash
docker compose up -d
```

## 5. Validate

```bash
docker compose ps
docker compose logs --tail=100 caddy
docker compose logs --tail=100 technitium
docker compose logs --tail=100 uptime-kuma
```

Verify HTTPS:

```bash
curl -I https://homepage.home.arpa
curl -I https://dns.home.arpa
curl -I https://status.home.arpa
```

If the Caddy root CA is not trusted on the client yet, use `curl -k -I` for the initial check and then follow [TLS](tls.md).

## 6. Cleanup Later

After the services are confirmed working and backups are in place, the old in-repository runtime directories can be removed manually.

Do not remove them as part of the migration until you have verified that DNS, HTTPS, and Uptime Kuma history still work.
