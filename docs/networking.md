# Networking

This document describes the current physical and IP network assumptions for the HomeLab.

## Current Layout

| Item | Value | Notes |
| --- | --- | --- |
| Router / FritzBox | `192.168.178.1` | Gateway, NAT, Wi-Fi, and DHCP. |
| HomeLab server | `192.168.178.2` | NUC-like Ubuntu server; stable hostname is `homelab-server.home.arpa`. |
| DHCP client range | starts at `192.168.178.20` | Normal clients should receive addresses from this range upward. |
| Local domain | `home.arpa` | Stable local naming independent of the current subnet. |

## Address Assignment

The HomeLab server IP is assigned by a FritzBox DHCP reservation / fixed lease. Ubuntu should normally use DHCP on the Ethernet interface rather than a manually configured static IP.

DHCP reservation is preferred because:

| Benefit | Why it matters |
| --- | --- |
| Single source of truth | The FritzBox remains responsible for LAN addressing. |
| Easier relocation | Router or subnet changes can be handled centrally. |
| Fewer host-level surprises | Ubuntu network configuration stays simple. |
| Stable service address | The server still keeps a predictable IP for DNS and future reverse proxy traffic. |

## Network Interfaces

Ethernet is the primary and preferred interface for the HomeLab server. DNS and future application traffic should assume the server is reachable over wired LAN.

The server also has Wi-Fi, but Wi-Fi is intentionally not part of the current architecture. It should normally remain unused or disabled unless a future use case is defined, documented, and tested.

## Deployment-Specific Values

Deployment-specific network values live in `.env` on the server:

```env
FRITZBOX_ROUTER_IP=192.168.178.1
HOMELAB_SERVER_IP=192.168.178.2
LOCAL_DOMAIN=home.arpa
```

`.env` is ignored by Git. The repository records expected defaults, but each runtime environment owns its actual values.

## Moving Or Relocating The HomeLab

When moving to another router, apartment, ISP, or subnet, expect the environment layer to change first.

IP addresses may change in the future when moving to another network, but hostnames should remain stable wherever possible.

Likely changes:

| Item | May change? | Notes |
| --- | --- | --- |
| Router IP | Yes | A new router may use a different subnet. |
| HomeLab server IP | Yes | Update the FritzBox or new router fixed lease and `.env`. |
| DHCP range | Yes | Keep infrastructure addresses outside the client pool where possible. |
| `home.arpa` names | Ideally no | Host and service naming should stay stable across moves. |
| Docker service layout | Ideally no | Application and platform compose files should not need subnet-specific edits. |

The goal is that only the environment layer needs reconfiguration after moving. Host names such as `homelab-server.home.arpa` and service names such as `dns.home.arpa` should remain stable.
