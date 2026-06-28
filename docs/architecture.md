# Architecture

This HomeLab is organized around contracts first and implementations second. The repository describes the intended platform behavior, while `.env` and runtime data describe one specific deployment.

## Layers

| Layer | Responsibility | Current implementation |
| --- | --- | --- |
| Environment | Physical network, router, DHCP, fixed leases, Wi-Fi, Ethernet. | FritzBox plus a fixed lease for the Ubuntu HomeLab server. |
| Platform | Shared services that applications rely on. | Docker Compose, Technitium DNS Server, planned Caddy. |
| Application | User-facing services. | Future Jellyfin, Immich, OpenSpeedTest, Paperless, and similar apps. |

## Environment Layer

The FritzBox owns routing, NAT, Wi-Fi, and DHCP. The HomeLab server receives `192.168.178.2` through a FritzBox DHCP reservation / fixed lease. This keeps the address stable while keeping the authoritative network configuration in the router.

The HomeLab server should use Ethernet as its primary and preferred network interface. Wi-Fi exists on the server but is not part of the current architecture and should normally remain unused or disabled unless a future use case is defined.

## Platform Layer

Docker Compose is the deployment mechanism. The root `compose.yaml` includes platform and application compose files from subdirectories.

Current platform service:

| Service contract | Current implementation | Path |
| --- | --- | --- |
| DNS resolver and authoritative local zone | Technitium DNS Server | `infrastructure/technitium/` |

Planned platform service:

| Service contract | Planned implementation | Path |
| --- | --- | --- |
| HTTP/HTTPS reverse proxy | Caddy | `infrastructure/caddy/` |

## Application Layer

Applications are planned for `applications/<service>/`. Each app should have its own compose file and should be reachable through Caddy once the reverse proxy exists.

After Caddy is in place, applications should not publish HTTP ports directly to the LAN except during short-lived testing. Caddy should reach application containers through Docker networks and service names.

## Contracts Over Implementations

The architecture should depend on service contracts rather than specific products. For example, applications need local DNS names to resolve and HTTP requests to route correctly; they should not need to know whether the DNS contract is fulfilled by Technitium, AdGuard Home, or another DNS service.

Technitium is the current DNS implementation. A future migration to AdGuard Home should preserve the same DNS contract:

| Contract item | Expected behavior |
| --- | --- |
| Local domain | `home.arpa` resolves only inside the local network. |
| Router record | `router.home.arpa` points to `192.168.178.1`. |
| HomeLab record | `homelab.home.arpa` points to `192.168.178.2`. |
| Wildcard record | `*.home.arpa` points to `192.168.178.2`. |
| Client DNS | FritzBox DHCP announces `192.168.178.2` as the local DNS server. |

## DNS And Caddy Boundaries

Caddy will be the single HTTP/HTTPS entrypoint in the future. It can route names such as `dns.home.arpa`, `jellyfin.home.arpa`, or `immich.home.arpa` to the right container once a client has already resolved the name.

Caddy does not proxy DNS protocol traffic. DNS uses TCP/UDP port `53`, not HTTP/HTTPS, so DNS clients must reach the DNS service directly on the HomeLab server. Only Web UIs and application HTTP/HTTPS traffic belong behind Caddy.

## Request Flow

```text
Client
  |
  | DNS query for jellyfin.home.arpa
  v
DNS service on HomeLab server
  |
  | returns 192.168.178.2 from *.home.arpa
  v
HomeLab IP: 192.168.178.2
  |
  | HTTP/HTTPS request for jellyfin.home.arpa
  v
Caddy reverse proxy (planned)
  |
  | Docker network + service name
  v
Application container
```
