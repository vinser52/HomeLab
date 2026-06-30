# Uptime Kuma

Uptime Kuma provides service availability monitoring for the HomeLab.

Public URL:

```text
https://status.home.arpa
```

The container does not publish HTTP ports directly to the LAN. Caddy reaches it over Docker networking at:

```text
uptime-kuma:3001
```

Uptime Kuma complements the other monitoring tools:

- Homepage is the HomeLab landing page.
- Glances provides live host metrics.
- Uptime Kuma tracks service availability, response time, uptime history, and status.
- Prometheus and Grafana remain future tools for historical metrics if that need appears later.

## Data

Persistent data lives in:

```text
applications/uptime-kuma/data/
```

This directory contains Uptime Kuma configuration, monitor definitions, uptime history, and status data. It is intentionally ignored by Git because it is runtime state.

## Initial Monitoring Plan

After deployment, create simple HTTP monitors manually in the Uptime Kuma UI:

| Monitor | URL |
| --- | --- |
| Homepage | `https://homepage.home.arpa` |
| DNS Web UI | `https://dns.home.arpa` |
| OpenSpeedTest | `https://speedtest.home.arpa` |
| Glances | `https://glances.home.arpa` |

Do not configure notifications yet.

Do not configure public status pages yet.

Docker socket access is intentionally not enabled. Uptime Kuma only needs to make HTTPS requests to service URLs for the current HomeLab availability checks.
