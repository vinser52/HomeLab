# Services

This document records naming and folder conventions for current and future HomeLab services.

## Naming Convention

Services should use names under `home.arpa`:

| Service | Planned name |
| --- | --- |
| DNS Web UI | `dns.home.arpa` |
| Homepage | `homepage.home.arpa` |
| Jellyfin | `jellyfin.home.arpa` |
| Immich | `immich.home.arpa` |
| Grafana | `grafana.home.arpa` |
| OpenSpeedTest | `speedtest.home.arpa` |
| Glances | `glances.home.arpa` |
| Uptime Kuma | `status.home.arpa` |
| Paperless | `paperless.home.arpa` |

The wildcard DNS record `*.home.arpa -> 192.168.178.2` means new application names should not require DNS changes. Caddy decides which container receives each HTTP request.

Machine names such as `homelab-server.home.arpa` belong to infrastructure hosts, not this service naming table.

`homepage.home.arpa` is the stable public contract for the HomeLab dashboard. Homepage is the current implementation and can be replaced later without changing the client-facing URL.

`speedtest.home.arpa` is the stable public contract. OpenSpeedTest is the current implementation and can be replaced later without changing the client-facing URL.

`glances.home.arpa` is the stable public contract for live host monitoring. Glances is the current implementation and can be replaced later without changing the client-facing URL.

`status.home.arpa` is the stable public contract for service availability monitoring. Uptime Kuma is the current implementation and can be replaced later without changing the client-facing URL.

`jellyfin.home.arpa` is the stable public contract for local media streaming. Jellyfin is the current implementation and can be replaced later without changing the client-facing URL.

`grafana.home.arpa` is the stable public contract for historical HomeLab metrics dashboards. Grafana is the current UI implementation. Prometheus and node-exporter are internal implementation details and are not exposed directly to the LAN.

## Folder Convention

| Path | Purpose |
| --- | --- |
| `infrastructure/<implementation>/` | Platform services such as DNS and reverse proxy implementations. |
| `applications/<service>/` | User-facing application stacks. |

Current infrastructure:

| Path | Status |
| --- | --- |
| `infrastructure/technitium/` | Current DNS implementation. |
| `infrastructure/caddy/` | Current HTTP reverse proxy. |

Current applications:

| Path | Status |
| --- | --- |
| `applications/homepage/` | Current implementation of `homepage.home.arpa`. |
| `applications/openspeedtest/` | Current implementation of `speedtest.home.arpa`. |
| `applications/glances/` | Current implementation of `glances.home.arpa`. |
| `applications/uptime-kuma/` | Current implementation of `status.home.arpa`. |
| `applications/jellyfin/` | Current implementation of `jellyfin.home.arpa`. |
| `applications/monitoring/` | Current implementation of `grafana.home.arpa` and historical host metrics. |

## Runtime Data

The repository contains desired configuration only. Persistent service state belongs under `${HOMELAB_STATE_DIR}`, which defaults to `/homelab/state`.

Current state paths:

| Service | State path |
| --- | --- |
| Caddy | `${HOMELAB_STATE_DIR}/caddy/` |
| Technitium | `${HOMELAB_STATE_DIR}/technitium/` |
| Uptime Kuma | `${HOMELAB_STATE_DIR}/uptime-kuma/` |
| Jellyfin | `${HOMELAB_STATE_DIR}/jellyfin/` |
| Grafana | `${HOMELAB_STATE_DIR}/grafana/` |
| Prometheus | `${HOMELAB_STATE_DIR}/prometheus/` |

User storage belongs under `${HOMELAB_STORAGE_DIR}`, which defaults to `/homelab/storage`. Future media applications such as Jellyfin should mount media from `${HOMELAB_STORAGE_DIR}/media`.

## Future Application Onboarding

Planned flow for adding an application:

1. Add a folder under `applications/<service>/`.
2. Add an application-specific `compose.yaml`.
3. Attach the application service to the Caddy/proxy Docker network.
4. Add a Caddy route for `service.home.arpa`.
5. Start the updated stack with Docker Compose.

No DNS change should be needed for normal application names because `*.home.arpa` already points to the HomeLab server.

## Port Publishing Rule

Caddy is the single HomeLab HTTP entrypoint. Application HTTP ports should not be published directly to the LAN once a service is behind Caddy. Caddy should reach application containers through Docker networks and service names.

Direct application port publishing is acceptable only for short-lived testing or troubleshooting, and should be removed once the service is routed through Caddy.

Caddy publishes HTTP on port `80` and HTTPS on port `443`. HTTPS is preferred for HomeLab web services and uses Caddy's internal CA.

## Homepage

Homepage is reachable at:

```text
https://homepage.home.arpa
```

Caddy routes `homepage.home.arpa` to the `homepage` Docker service on port `3000`. The Homepage container does not publish ports directly to the LAN and is reachable only through Caddy.

Homepage configuration is stored in `applications/homepage/config/` and committed to Git. It intentionally contains no committed secrets. Authenticated widgets should use local `.env` placeholders so tokens stay out of the repository.

Homepage gets live host metrics from Glances over the internal Docker `proxy` network.

The DNS card also uses Homepage's Technitium widget over Docker networking at `http://technitium:5380`. The widget should authenticate with a dedicated Technitium API token stored only in local `.env` as `HOMEPAGE_VAR_TECHNITIUM_API_KEY`.

## OpenSpeedTest

OpenSpeedTest is reachable at:

```text
https://speedtest.home.arpa
```

Caddy routes `speedtest.home.arpa` to the `openspeedtest` Docker service on port `3000`. The OpenSpeedTest container does not publish ports directly to the LAN and is reachable only through Caddy.

## Glances

Glances is reachable at:

```text
https://glances.home.arpa
```

Caddy routes `glances.home.arpa` to the `glances` Docker service on port `61208`. The Glances container does not publish ports directly to the LAN and is reachable only through Caddy.

Glances provides lightweight live monitoring for the HomeLab server. It is used by Homepage for current host metrics. Prometheus and Grafana are intentionally deferred until historical metrics or alerting become necessary.

## Uptime Kuma

Uptime Kuma is reachable at:

```text
https://status.home.arpa
```

Caddy routes `status.home.arpa` to the `uptime-kuma` Docker service on port `3001`. The Uptime Kuma container does not publish ports directly to the LAN and is reachable only through Caddy.

Uptime Kuma monitors HomeLab service availability, response time, uptime history, and local status. Its configuration and history live under `${HOMELAB_STATE_DIR}/uptime-kuma/data`, which is runtime data and intentionally ignored by Git.

Initial monitors should be added manually through the Uptime Kuma UI:

| Monitor | URL |
| --- | --- |
| Homepage | `https://homepage.home.arpa` |
| DNS Web UI | `https://dns.home.arpa` |
| OpenSpeedTest | `https://speedtest.home.arpa` |
| Glances | `https://glances.home.arpa` |

Use simple HTTP monitors with HTTPS URLs after TLS works and the Caddy root CA is trusted where needed. Notifications and public status pages are intentionally not configured yet.

## Jellyfin

Jellyfin is reachable at:

```text
https://jellyfin.home.arpa
```

Caddy routes `jellyfin.home.arpa` to the `jellyfin` Docker service on port `8096`. The Jellyfin container does not publish port `8096` directly to the LAN and is reachable only through Caddy.

Jellyfin stores runtime state under `${HOMELAB_STATE_DIR}/jellyfin/config` and `${HOMELAB_STATE_DIR}/jellyfin/cache`. It mounts media read-only from `${HOMELAB_STORAGE_DIR}/media` so the existing `Movies` and `Series` layout remains the source of truth.

## Monitoring

Grafana is reachable at:

```text
https://grafana.home.arpa
```

Caddy routes `grafana.home.arpa` to the `grafana` Docker service on port `3000`. Grafana does not publish port `3000` directly to the LAN and is reachable only through Caddy.

Prometheus and node-exporter stay internal on the Docker `proxy` network. Prometheus scrapes itself at `prometheus:9090` and node-exporter at `node-exporter:9100`. Grafana reads Prometheus at `http://prometheus:9090`.

Grafana stores runtime state under `${HOMELAB_STATE_DIR}/grafana/data`. Prometheus stores its time-series database under `${HOMELAB_STATE_DIR}/prometheus/data` with an initial retention period of 15 days.

Desired monitoring configuration lives in Git under `applications/monitoring/config/`. Grafana provisioning creates the Prometheus datasource and loads committed dashboards. Dashboards created through the Grafana UI live in Grafana runtime state unless they are exported and committed.

node-exporter is configured to report Ubuntu host metrics while running as a container. It uses host PID visibility, mounts the host root filesystem read-only at `/host`, uses `--path.rootfs=/host`, and excludes pseudo-filesystems, Docker overlay mounts, Ubuntu Snap mounts, and container runtime paths from filesystem metrics. It does not use `privileged: true`, host networking, or the Docker socket.
