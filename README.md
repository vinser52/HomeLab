# HomeLab

This repository is the source of truth for a Docker Compose based HomeLab. It is developed and deployed to a home Ubuntu server via Git, and currently runs infrastructure services for the local network.

The current runtime service is Technitium DNS Server. Future application services will live under `applications/` and should eventually be routed through Caddy.

## Current Environment

| Component | Current value | Notes |
| --- | --- | --- |
| Router | `192.168.178.1` | FritzBox handles routing, NAT, Wi-Fi, and DHCP. |
| HomeLab server | `192.168.178.2` | Assigned by FritzBox DHCP reservation / fixed lease. |
| DHCP range | starts at `192.168.178.20` | Keeps infrastructure addresses outside the normal client range. |
| Local domain | `home.arpa` | Local-only domain for HomeLab names. |
| DNS service | Technitium DNS Server | Current implementation of the DNS service contract. |

## Repository Structure

```text
HomeLab/
|-- compose.yaml
|-- .env.example
|-- .gitignore
|-- README.md
|-- docs/
|   |-- architecture.md
|   |-- dns.md
|   |-- networking.md
|   |-- operations.md
|   `-- services.md
|-- infrastructure/
|   |-- caddy/
|   |   `-- README.md
|   `-- technitium/
|       |-- compose.yaml
|       `-- data/
`-- applications/
```

`infrastructure/` contains platform services such as DNS and the planned Caddy reverse proxy. `applications/` is reserved for user-facing app stacks such as Jellyfin, Immich, OpenSpeedTest, and similar services.

Runtime state is intentionally not committed. For example, Technitium data lives under `infrastructure/technitium/data/` and `.env` is local to each deployment.

## Quick Start On The Server

Run these commands on the Ubuntu HomeLab server:

```bash
git pull
```

Create a local environment file if it does not exist yet:

```bash
cp .env.example .env
```

Edit `.env` for this deployment. Do not commit `.env`; it may contain local settings and secrets.

```bash
docker compose config
docker compose up -d
docker compose ps
```

Open the current Technitium Web UI directly while Caddy is not installed yet:

```text
http://192.168.178.2:5380
```

## Documentation

- [Architecture](docs/architecture.md)
- [Networking](docs/networking.md)
- [DNS](docs/dns.md)
- [Operations](docs/operations.md)
- [Services](docs/services.md)

## Local Configuration

Deployment-specific settings live in `.env`, which is ignored by Git. Start from [.env.example](.env.example), set a real `DNS_SERVER_ADMIN_PASSWORD` locally, and keep passwords or API tokens out of the repository.

The current expected values are:

```env
FRITZBOX_ROUTER_IP=192.168.178.1
HOMELAB_SERVER_IP=192.168.178.2
LOCAL_DOMAIN=home.arpa
```
