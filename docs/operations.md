# Operations

This document covers the normal workflow for deploying and operating the HomeLab from Git.

## Deployment Workflow

Development happens on the MacBook. Runtime happens on the Ubuntu HomeLab server.

Normal flow:

1. Edit documentation or compose files on the MacBook.
2. Commit and push changes to Git.
3. SSH into the Ubuntu HomeLab server.
4. Pull the latest repository state.
5. Validate Docker Compose.
6. Apply the stack.

```bash
git pull
docker compose config
docker compose up -d
docker compose ps
docker compose logs --tail=100 caddy
docker compose logs --tail=100 technitium
docker compose logs --tail=100 homepage
docker compose logs --tail=100 openspeedtest
docker compose logs --tail=100 glances
docker compose logs --tail=100 uptime-kuma
docker compose logs --tail=100 jellyfin
docker compose logs --tail=100 grafana
docker compose logs --tail=100 prometheus
docker compose logs --tail=100 node-exporter
docker compose logs --tail=100 cadvisor
```

Git is the source of truth for intended configuration. Runtime data and local secrets stay outside Git.

## Useful Commands

| Command | Purpose |
| --- | --- |
| `docker compose config` | Render and validate the full Compose configuration. |
| `docker compose up -d` | Create or update services in the background. |
| `docker compose ps` | Show service status and published ports. |
| `docker compose logs --tail=100 <service>` | Show recent logs for one service. |
| `docker compose stop <service>` | Stop one service without removing containers or data. |
| `docker compose start <service>` | Start one stopped service. |
| `docker compose down` | Stop and remove Compose-managed containers and networks. |

Example:

```bash
docker compose logs --tail=100 caddy
docker compose logs --tail=100 technitium
docker compose logs --tail=100 homepage
docker compose logs --tail=100 openspeedtest
docker compose logs --tail=100 glances
docker compose logs --tail=100 uptime-kuma
docker compose logs --tail=100 jellyfin
docker compose logs --tail=100 grafana
docker compose logs --tail=100 prometheus
docker compose logs --tail=100 node-exporter
docker compose logs --tail=100 cadvisor
```

## Validation

After deployment, validate DNS and HTTPS routing from a Mac or LAN client.

Monitoring state directories should be writable by the configured HomeLab service user before first start on the Ubuntu HomeLab server:

```bash
set -a
. ./.env
set +a
sudo install -d -o "${HOMELAB_UID:-1000}" -g "${HOMELAB_GID:-1000}" "${HOMELAB_STATE_DIR:-/homelab/state}/grafana/data"
sudo install -d -o "${HOMELAB_UID:-1000}" -g "${HOMELAB_GID:-1000}" "${HOMELAB_STATE_DIR:-/homelab/state}/prometheus/data"
```

If Grafana logs `GF_PATHS_DATA='/var/lib/grafana' is not writable` or Prometheus logs `open /prometheus/queries.active: permission denied`, Docker likely created the bind directories as `root`. Fix ownership and restart the monitoring services:

```bash
set -a
. ./.env
set +a
sudo chown -R "${HOMELAB_UID:-1000}:${HOMELAB_GID:-1000}" "${HOMELAB_STATE_DIR:-/homelab/state}/grafana/data"
sudo chown -R "${HOMELAB_UID:-1000}:${HOMELAB_GID:-1000}" "${HOMELAB_STATE_DIR:-/homelab/state}/prometheus/data"
docker compose up -d grafana prometheus
```

DNS tests:

```bash
nslookup dns.home.arpa 192.168.178.2
nslookup router.home.arpa 192.168.178.2
nslookup homelab-server.home.arpa 192.168.178.2
nslookup homepage.home.arpa
nslookup speedtest.home.arpa
nslookup glances.home.arpa
nslookup status.home.arpa
nslookup jellyfin.home.arpa
nslookup grafana.home.arpa
```

HTTPS tests before trusting the Caddy root CA:

```bash
curl -k -I https://homepage.home.arpa
curl -k -I https://dns.home.arpa
curl -k -I https://speedtest.home.arpa
curl -k -I https://glances.home.arpa
curl -k -I https://status.home.arpa
curl -k -I https://jellyfin.home.arpa
curl -k -I https://grafana.home.arpa
```

After trusting the Caddy root CA:

```bash
curl -I https://homepage.home.arpa
```

Expected result: `dns.home.arpa`, `homepage.home.arpa`, `speedtest.home.arpa`, `glances.home.arpa`, `status.home.arpa`, `jellyfin.home.arpa`, and `grafana.home.arpa` resolve to `192.168.178.2`, Caddy answers on port `443`, and the Technitium Web UI, Homepage UI, OpenSpeedTest UI, Glances UI, Uptime Kuma UI, Jellyfin UI, and Grafana UI are reachable through Caddy.

Direct access to `http://192.168.178.2:5380` is no longer expected. The Technitium Web UI is exposed only inside Docker and published through Caddy.

OpenSpeedTest should be accessed through `https://speedtest.home.arpa`. It does not publish an HTTP port directly to the LAN.

Homepage should be accessed through `https://homepage.home.arpa`. It does not publish an HTTP port directly to the LAN. Its committed configuration lives under `applications/homepage/config/` and intentionally contains no secrets.

Glances should be accessed through `https://glances.home.arpa`. It does not publish an HTTP port directly to the LAN. Homepage reads live host metrics from Glances over the internal Docker network.

Uptime Kuma should be accessed through `https://status.home.arpa`. It does not publish an HTTP port directly to the LAN. Its monitor configuration and uptime history live under `${HOMELAB_STATE_DIR}/uptime-kuma/data`.

Jellyfin should be accessed through `https://jellyfin.home.arpa`. It does not publish port `8096` directly to the LAN. Its runtime state lives under `${HOMELAB_STATE_DIR}/jellyfin/config` and `${HOMELAB_STATE_DIR}/jellyfin/cache`, while media stays under `${HOMELAB_STORAGE_DIR}/media`.

Grafana should be accessed through `https://grafana.home.arpa`. It does not publish port `3000` directly to the LAN. Prometheus and node-exporter are internal-only services and do not publish ports directly to the LAN. Grafana runtime state lives under `${HOMELAB_STATE_DIR}/grafana/data`; Prometheus metrics data lives under `${HOMELAB_STATE_DIR}/prometheus/data`.

Monitoring runtime checks should be run on the Ubuntu HomeLab server, not on the MacBook:

```bash
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="node-exporter"}'
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="cadvisor"}'
```

In Grafana, confirm that the Prometheus datasource is healthy and that the `Host Metrics Overview` dashboard shows host CPU, memory, filesystem, load, and network metrics. The `up{job="node-exporter"}` query should return `1`; filesystem metrics should not be dominated by `overlay`, `/proc`, `/sys`, `/dev`, Ubuntu Snap mounts, or Docker runtime paths; and network panels should focus on physical host interfaces rather than `lo`, Docker bridges, or `veth` devices. node-exporter uses host networking intentionally so network panels reflect the Ubuntu host instead of the node-exporter container.

Also confirm that the `Container Metrics Overview` dashboard shows per-container CPU, memory, network, filesystem usage, and filesystem I/O.

Also confirm that the `Monitoring Health` dashboard shows Prometheus, node-exporter, and cAdvisor target health, scrape duration, scraped samples, active series, Prometheus DB size, and Prometheus process CPU and memory usage.

See [TLS](tls.md) for Caddy root CA trust setup.

## `.env` Handling

`.env` is local to each deployment and is ignored by Git. Create it from `.env.example` when needed:

```bash
cp .env.example .env
chmod 600 .env
```

Rules:

| Rule | Reason |
| --- | --- |
| Do not commit `.env`. | It may contain passwords, tokens, or deployment-specific values. |
| Do not commit real passwords or API tokens. | Git history is hard to clean safely. |
| Keep `.env` readable only by the owner where practical. | Limits accidental local exposure. |
| Update `.env.example` only with safe defaults or placeholder values. | Keeps onboarding easy without leaking secrets. |

For the current HomeLab stage, a protected `.env` file is acceptable. If secret handling becomes more complex, consider Docker secrets, SOPS with age, or Vault-like tools.

`.env` also defines host-specific base paths:

```env
HOMELAB_STATE_DIR=/homelab/state
HOMELAB_STORAGE_DIR=/homelab/storage
```

## Runtime Data

Runtime data is intentionally outside the Git repository. Service state lives under `${HOMELAB_STATE_DIR}`.

Technitium stores configuration and logs under:

```text
${HOMELAB_STATE_DIR}/technitium/config
${HOMELAB_STATE_DIR}/technitium/logs
```

Caddy stores runtime state under:

```text
${HOMELAB_STATE_DIR}/caddy/data
${HOMELAB_STATE_DIR}/caddy/config
```

Caddy also stores internal CA certificates and keys under `${HOMELAB_STATE_DIR}/caddy/data`. Do not commit this material to Git.

Uptime Kuma stores monitor configuration and uptime history under:

```text
${HOMELAB_STATE_DIR}/uptime-kuma/data
```

Jellyfin stores application state under:

```text
${HOMELAB_STATE_DIR}/jellyfin/config
${HOMELAB_STATE_DIR}/jellyfin/cache
```

Grafana and Prometheus store state under:

```text
${HOMELAB_STATE_DIR}/grafana/data
${HOMELAB_STATE_DIR}/prometheus/data
```

User storage belongs under `${HOMELAB_STORAGE_DIR}` and is separate from service state. See [Storage Layout](storage-layout.md) and [Runtime State Migration](migration-runtime-state.md).

Back up runtime data before destructive maintenance once the DNS service becomes important for daily use.

## Technitium Reset For Early Testing Only

During early experiments, it can be useful to wipe Technitium and start fresh:

```bash
docker compose down
sudo rm -rf "${HOMELAB_STATE_DIR:-/homelab/state}/technitium"
docker compose up -d
```

This deletes DNS configuration, zones, records, and logs. Do not use this reset procedure after the DNS service becomes production-like unless you have a backup and intentionally want to rebuild it.
