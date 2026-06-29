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
| Paperless | `paperless.home.arpa` |

The wildcard DNS record `*.home.arpa -> 192.168.178.2` means new application names should not require DNS changes. Caddy decides which container receives each HTTP request.

Machine names such as `homelab-server.home.arpa` belong to infrastructure hosts, not this service naming table.

`homepage.home.arpa` is the stable public contract for the HomeLab dashboard. Homepage is the current implementation and can be replaced later without changing the client-facing URL.

`speedtest.home.arpa` is the stable public contract. OpenSpeedTest is the current implementation and can be replaced later without changing the client-facing URL.

`glances.home.arpa` is the stable public contract for live host monitoring. Glances is the current implementation and can be replaced later without changing the client-facing URL.

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

For now, Caddy publishes HTTP only on port `80`. HTTPS/TLS will be handled later as a separate step.

## Homepage

Homepage is reachable at:

```text
http://homepage.home.arpa
```

Caddy routes `homepage.home.arpa` to the `homepage` Docker service on port `3000`. The Homepage container does not publish ports directly to the LAN and is reachable only through Caddy.

Homepage configuration is stored in `applications/homepage/config/` and committed to Git. It intentionally contains no secrets. Widgets requiring authentication should be added incrementally once a token strategy exists.

Homepage gets live host metrics from Glances over the internal Docker `proxy` network.

## OpenSpeedTest

OpenSpeedTest is reachable at:

```text
http://speedtest.home.arpa
```

Caddy routes `speedtest.home.arpa` to the `openspeedtest` Docker service on port `3000`. The OpenSpeedTest container does not publish ports directly to the LAN and is reachable only through Caddy.

## Glances

Glances is reachable at:

```text
http://glances.home.arpa
```

Caddy routes `glances.home.arpa` to the `glances` Docker service on port `61208`. The Glances container does not publish ports directly to the LAN and is reachable only through Caddy.

Glances provides lightweight live monitoring for the HomeLab server. It is used by Homepage for current host metrics. Prometheus and Grafana are intentionally deferred until historical metrics or alerting become necessary.
