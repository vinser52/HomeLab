# HomeLab

This repository is the source of truth for a Docker Compose based HomeLab. It is developed and deployed to a home Ubuntu server via Git, and currently runs infrastructure services for the local network.

The current runtime services are Technitium DNS Server, Caddy, Homepage, OpenSpeedTest, and Glances. Technitium provides DNS, Caddy is the local HTTP reverse proxy, Homepage is the dashboard, OpenSpeedTest provides LAN speed testing, and Glances provides lightweight live host monitoring.

## Current Environment

| Component | Current value | Notes |
| --- | --- | --- |
| Router | `192.168.178.1` | FritzBox handles routing, NAT, Wi-Fi, and DHCP. |
| HomeLab server | `192.168.178.2` | Assigned by FritzBox DHCP reservation / fixed lease; stable hostname is `homelab-server.home.arpa`. |
| DHCP range | starts at `192.168.178.20` | Keeps infrastructure addresses outside the normal client range. |
| Local domain | `home.arpa` | Local-only domain for HomeLab names. |
| DNS service | Technitium DNS Server | Current implementation of the DNS service contract. |
| HTTP reverse proxy | Caddy | Routes local HTTP service names such as `dns.home.arpa`. |
| Dashboard | Homepage | Current implementation of `homepage.home.arpa`. |
| Speed test | OpenSpeedTest | Current implementation of `speedtest.home.arpa`. |
| Live monitoring | Glances | Current implementation of `glances.home.arpa`. |

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
|   |   |-- Caddyfile
|   |   |-- compose.yaml
|   |   `-- README.md
|   `-- technitium/
|       |-- compose.yaml
|       `-- data/
`-- applications/
    |-- glances/
    |   |-- compose.yaml
    |   |-- README.md
    |   `-- config/
    |-- homepage/
    |   |-- compose.yaml
    |   |-- README.md
    |   `-- config/
    `-- openspeedtest/
        |-- compose.yaml
        `-- README.md
```

`infrastructure/` contains platform services such as DNS and the Caddy reverse proxy. `applications/` contains user-facing app stacks. Homepage is the dashboard application, OpenSpeedTest is the speed test application, and Glances is the live monitoring application.

Runtime state is intentionally not committed. For example, Technitium data lives under `infrastructure/technitium/data/`, Caddy runtime data lives under `infrastructure/caddy/data/` and `infrastructure/caddy/config/`, and `.env` is local to each deployment.

Homepage configuration lives under `applications/homepage/config/` and is committed to Git. Homepage intentionally contains no secrets; widgets requiring authentication should be added incrementally once a token strategy exists.

Homepage gets live host metrics from Glances over the internal Docker network. Glances is intentionally lightweight; Prometheus and Grafana are deferred until historical metrics, alerting, or long-term dashboards become necessary.

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

Check recent service logs if needed:

```bash
docker compose logs --tail=100 caddy
docker compose logs --tail=100 technitium
docker compose logs --tail=100 homepage
docker compose logs --tail=100 openspeedtest
docker compose logs --tail=100 glances
```

Open the Technitium Web UI through Caddy:

```text
http://dns.home.arpa
```

Open OpenSpeedTest through Caddy:

```text
http://speedtest.home.arpa
```

Open Homepage through Caddy:

```text
http://homepage.home.arpa
```

Open Glances through Caddy:

```text
http://glances.home.arpa
```

Direct access to `http://192.168.178.2:5380` is no longer expected once Caddy is running. DNS protocol traffic still goes directly to Technitium on `192.168.178.2:53/tcp` and `192.168.178.2:53/udp`.

For now, Caddy serves HTTP only on port `80`. HTTPS/TLS will be added later as a separate step.

## Validation

DNS tests:

```bash
nslookup dns.home.arpa 192.168.178.2
nslookup router.home.arpa 192.168.178.2
nslookup homelab-server.home.arpa 192.168.178.2
nslookup homepage.home.arpa
nslookup speedtest.home.arpa
nslookup glances.home.arpa
```

HTTP tests from a Mac or LAN client:

```bash
curl -I http://dns.home.arpa
curl -I http://homepage.home.arpa
curl -I http://speedtest.home.arpa
curl -I http://glances.home.arpa
```

Expected result: `dns.home.arpa`, `homepage.home.arpa`, `speedtest.home.arpa`, and `glances.home.arpa` resolve to `192.168.178.2`, Caddy answers on port `80`, and the Web UIs are reachable through Caddy.

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
