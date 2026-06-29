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
```

## Validation

After deployment, validate DNS and HTTP routing from a Mac or LAN client.

DNS tests:

```bash
nslookup dns.home.arpa 192.168.178.2
nslookup router.home.arpa 192.168.178.2
nslookup homelab-server.home.arpa 192.168.178.2
nslookup homepage.home.arpa
nslookup speedtest.home.arpa
nslookup glances.home.arpa
nslookup status.home.arpa
```

HTTP tests:

```bash
curl -I http://dns.home.arpa
curl -I http://homepage.home.arpa
curl -I http://speedtest.home.arpa
curl -I http://glances.home.arpa
curl -I http://status.home.arpa
```

Expected result: `dns.home.arpa`, `homepage.home.arpa`, `speedtest.home.arpa`, `glances.home.arpa`, and `status.home.arpa` resolve to `192.168.178.2`, Caddy answers on port `80`, and the Technitium Web UI, Homepage UI, OpenSpeedTest UI, Glances UI, and Uptime Kuma UI are reachable through Caddy.

Direct access to `http://192.168.178.2:5380` is no longer expected. The Technitium Web UI is exposed only inside Docker and published through Caddy.

OpenSpeedTest should be accessed through `http://speedtest.home.arpa`. It does not publish an HTTP port directly to the LAN.

Homepage should be accessed through `http://homepage.home.arpa`. It does not publish an HTTP port directly to the LAN. Its committed configuration lives under `applications/homepage/config/` and intentionally contains no secrets.

Glances should be accessed through `http://glances.home.arpa`. It does not publish an HTTP port directly to the LAN. Homepage reads live host metrics from Glances over the internal Docker network.

Uptime Kuma should be accessed through `http://status.home.arpa`. It does not publish an HTTP port directly to the LAN. Its monitor configuration and uptime history live under `applications/uptime-kuma/data/`.

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

## Runtime Data

Runtime data is intentionally ignored by Git. Technitium stores configuration and logs under:

```text
infrastructure/technitium/data/
```

Caddy stores runtime state under:

```text
infrastructure/caddy/data/
infrastructure/caddy/config/
```

Uptime Kuma stores monitor configuration and uptime history under:

```text
applications/uptime-kuma/data/
```

Back up runtime data before destructive maintenance once the DNS service becomes important for daily use.

## Technitium Reset For Early Testing Only

During early experiments, it can be useful to wipe Technitium and start fresh:

```bash
docker compose down
sudo rm -rf infrastructure/technitium/data
docker compose up -d
```

This deletes DNS configuration, zones, records, and logs. Do not use this reset procedure after the DNS service becomes production-like unless you have a backup and intentionally want to rebuild it.
