# Services

This document records naming and folder conventions for current and future HomeLab services.

## Naming Convention

Services should use names under `home.arpa`:

| Service | Planned name |
| --- | --- |
| HomeLab server | `homelab.home.arpa` |
| DNS Web UI | `dns.home.arpa` |
| Jellyfin | `jellyfin.home.arpa` |
| Immich | `immich.home.arpa` |
| OpenSpeedTest | `speedtest.home.arpa` |
| Paperless | `paperless.home.arpa` |

The wildcard DNS record `*.home.arpa -> 192.168.178.2` means new application names should not require DNS changes. Caddy will later decide which container receives each HTTP/HTTPS request.

## Folder Convention

| Path | Purpose |
| --- | --- |
| `infrastructure/<implementation>/` | Platform services such as DNS and reverse proxy implementations. |
| `applications/<service>/` | User-facing application stacks. |

Current infrastructure:

| Path | Status |
| --- | --- |
| `infrastructure/technitium/` | Current DNS implementation. |
| `infrastructure/caddy/` | Planned reverse proxy placeholder. |

Current applications:

| Path | Status |
| --- | --- |
| `applications/` | Empty and reserved for future services. |

## Future Application Onboarding

Planned flow for adding an application:

1. Add a folder under `applications/<service>/`.
2. Add an application-specific `compose.yaml`.
3. Attach the application service to the Caddy/proxy Docker network.
4. Add a Caddy route for `service.home.arpa`.
5. Start the updated stack with Docker Compose.

No DNS change should be needed for normal application names because `*.home.arpa` already points to the HomeLab server.

## Port Publishing Rule

Once Caddy is used, application HTTP ports should not be published directly to the LAN. Caddy should be the single HTTP/HTTPS entrypoint, and it should reach application containers through Docker networks and service names.

Direct application port publishing is acceptable only for short-lived testing or troubleshooting, and should be removed once the service is routed through Caddy.
