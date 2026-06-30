# HomeLab

This repository is the source of truth for a Docker Compose based HomeLab. It is developed and deployed to a home Ubuntu server via Git, and currently runs infrastructure services for the local network.

The current runtime services are Technitium DNS Server, Caddy, Homepage, OpenSpeedTest, Glances, and Uptime Kuma. Technitium provides DNS, Caddy is the local HTTP reverse proxy, Homepage is the dashboard, OpenSpeedTest provides LAN speed testing, Glances provides lightweight live host monitoring, and Uptime Kuma tracks service availability.

## Current Environment

| Component | Current value | Notes |
| --- | --- | --- |
| Router | `192.168.178.1` | FritzBox handles routing, NAT, Wi-Fi, and DHCP. |
| HomeLab server | `192.168.178.2` | Assigned by FritzBox DHCP reservation / fixed lease; stable hostname is `homelab-server.home.arpa`. |
| DHCP range | starts at `192.168.178.20` | Keeps infrastructure addresses outside the normal client range. |
| Local domain | `home.arpa` | Local-only domain for HomeLab names. |
| DNS service | Technitium DNS Server | Current implementation of the DNS service contract. |
| HTTP/HTTPS reverse proxy | Caddy | Routes local web service names such as `dns.home.arpa`. |
| Dashboard | Homepage | Current implementation of `homepage.home.arpa`. |
| Speed test | OpenSpeedTest | Current implementation of `speedtest.home.arpa`. |
| Live monitoring | Glances | Current implementation of `glances.home.arpa`. |
| Availability monitoring | Uptime Kuma | Current implementation of `status.home.arpa`. |

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
|   |-- tls.md
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
    |-- uptime-kuma/
    |   |-- compose.yaml
    |   |-- README.md
    |   `-- data/
    |-- homepage/
    |   |-- compose.yaml
    |   |-- README.md
    |   `-- config/
    `-- openspeedtest/
        |-- compose.yaml
        `-- README.md
```

`infrastructure/` contains platform services such as DNS and the Caddy reverse proxy. `applications/` contains user-facing app stacks. Homepage is the dashboard application, OpenSpeedTest is the speed test application, Glances is the live monitoring application, and Uptime Kuma is the availability monitoring application.

Runtime state is intentionally not committed. For example, Technitium data lives under `infrastructure/technitium/data/`, Caddy runtime data lives under `infrastructure/caddy/data/` and `infrastructure/caddy/config/`, Uptime Kuma data lives under `applications/uptime-kuma/data/`, and `.env` is local to each deployment.

Homepage configuration lives under `applications/homepage/config/` and is committed to Git. Homepage intentionally contains no secrets; widgets requiring authentication should be added incrementally once a token strategy exists.

Homepage gets live host metrics from Glances over the internal Docker network. Uptime Kuma monitors service availability and response time. Glances and Uptime Kuma are intentionally lightweight; Prometheus and Grafana are deferred until historical metrics, alerting, or long-term dashboards become necessary.

Caddy provides LAN-only HTTPS using its internal CA. Browsers will warn until the Caddy root CA is trusted on each client device. See [TLS](docs/tls.md).

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
docker compose logs --tail=100 uptime-kuma
```

Open the Technitium Web UI through Caddy:

```text
https://dns.home.arpa
```

Open OpenSpeedTest through Caddy:

```text
https://speedtest.home.arpa
```

Open Homepage through Caddy:

```text
https://homepage.home.arpa
```

Open Glances through Caddy:

```text
https://glances.home.arpa
```

Open Uptime Kuma through Caddy:

```text
https://status.home.arpa
```

Direct access to `http://192.168.178.2:5380` is no longer expected once Caddy is running. DNS protocol traffic still goes directly to Technitium on `192.168.178.2:53/tcp` and `192.168.178.2:53/udp`.

Caddy publishes HTTP on port `80` and HTTPS on port `443`. HTTPS is preferred for HomeLab web services. TLS uses Caddy's internal CA, not Let's Encrypt.

## Validation

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

HTTPS tests from a Mac or LAN client before trusting the Caddy root CA:

```bash
curl -k -I https://dns.home.arpa
curl -k -I https://homepage.home.arpa
curl -k -I https://speedtest.home.arpa
curl -k -I https://glances.home.arpa
curl -k -I https://status.home.arpa
```

After trusting the Caddy root CA:

```bash
curl -I https://homepage.home.arpa
```

Expected result: `dns.home.arpa`, `homepage.home.arpa`, `speedtest.home.arpa`, `glances.home.arpa`, and `status.home.arpa` resolve to `192.168.178.2`, Caddy answers on port `443`, and the Web UIs are reachable through Caddy.

## Documentation

- [Architecture](docs/architecture.md)
- [Networking](docs/networking.md)
- [DNS](docs/dns.md)
- [Operations](docs/operations.md)
- [Services](docs/services.md)
- [TLS](docs/tls.md)

## Local Configuration

Deployment-specific settings live in `.env`, which is ignored by Git. Start from [.env.example](.env.example), set a real `DNS_SERVER_ADMIN_PASSWORD` locally, and keep passwords or API tokens out of the repository.

The current expected values are:

```env
FRITZBOX_ROUTER_IP=192.168.178.1
HOMELAB_SERVER_IP=192.168.178.2
LOCAL_DOMAIN=home.arpa
```
