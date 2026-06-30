# DNS

The local DNS domain is `home.arpa`. The current DNS service implementation is Technitium DNS Server, but the architecture treats DNS as a contract so another service, such as AdGuard Home, could replace it later.

## Why `home.arpa`

`home.arpa` is intended for non-unique residential home networks. It is preferred over informal names such as `.home` or `.lan` because those names are not reserved in the same way and can conflict with real or future DNS usage.

## DNS Service Contract

| Name | Type | Value | Purpose |
| --- | --- | --- | --- |
| `router.home.arpa` | `A` | `192.168.178.1` | Stable name for the FritzBox. |
| `homelab-server.home.arpa` | `A` | `192.168.178.2` | Stable name for the HomeLab server. |
| `*.home.arpa` | `A` | `192.168.178.2` | Routes future service names to the HomeLab server. |

`dns.home.arpa` does not need a dedicated `A` record because it is covered by `*.home.arpa`. Caddy routes HTTP requests for `dns.home.arpa` to the Technitium Web UI.

DNS protocol traffic itself still goes directly to the DNS service on TCP/UDP port `53`. It cannot be routed through Caddy. Only the Technitium Web UI and other HTTP/HTTPS services belong behind Caddy.

## Technitium Setup Notes

In Technitium, create a primary zone:

```text
home.arpa
```

Add these records:

| Name | Type | Value |
| --- | --- | --- |
| `router` | `A` | `192.168.178.1` |
| `homelab-server` | `A` | `192.168.178.2` |
| `*` | `A` | `192.168.178.2` |

## FritzBox DNS Decision

Two FritzBox DNS approaches were tested.

| Scenario | Setup | Result | Decision |
| --- | --- | --- | --- |
| 1 | FritzBox DHCP announces `192.168.178.2` as local DNS. | `google.com` worked and `test.home.arpa` worked. When Technitium stopped, public DNS continued on macOS via FritzBox IPv6 DNS fallback, but `home.arpa` failed. | Used. |
| 2 | Clients used FritzBox as DNS; FritzBox used Technitium as upstream DNS. | `google.com` worked, but `test.home.arpa` returned `NXDOMAIN`. | Not used. |

The macOS fallback observed in scenario 1 should not be treated as guaranteed behavior for every client. If the DNS service is stopped, expect `home.arpa` names to stop resolving.

## Test Commands

Run these from a client or from the server:

```bash
nslookup google.com 192.168.178.2
nslookup router.home.arpa 192.168.178.2
nslookup homelab-server.home.arpa 192.168.178.2
nslookup dns.home.arpa 192.168.178.2
nslookup jellyfin.home.arpa 192.168.178.2
dig @192.168.178.2 +short jellyfin.home.arpa
```

Expected results:

| Query | Expected answer |
| --- | --- |
| `google.com` | Public DNS answer. |
| `router.home.arpa` | `192.168.178.1` |
| `homelab-server.home.arpa` | `192.168.178.2` |
| `dns.home.arpa` | `192.168.178.2`, resolved through the `*.home.arpa` wildcard record. |
| `jellyfin.home.arpa` | `192.168.178.2`, resolved through the `*.home.arpa` wildcard record. |

## Technitium Web UI

The Technitium Web UI is available through Caddy:

```text
https://dns.home.arpa
```

Direct access to `http://192.168.178.2:5380` is no longer expected once Caddy is running. The Technitium Web UI is published through Caddy over LAN-only HTTPS using Caddy's internal CA.

## Homepage Widget Token

Homepage can show Technitium DNS statistics on the `dns.home.arpa` card using Technitium's HTTP API.

Create a dedicated Technitium user for Homepage and generate an API token for that user instead of reusing the main administrator account. Store the token only in local `.env` as `HOMEPAGE_VAR_TECHNITIUM_API_KEY`.

This keeps Homepage configuration committed to Git while keeping credentials local to the deployment.

## `fritz.box`

`fritz.box` may not resolve through Technitium unless a specific record or forwarder is added. Prefer `router.home.arpa` as the stable local router name in HomeLab documentation and scripts.
