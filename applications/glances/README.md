# Glances

Glances provides lightweight live host monitoring for the HomeLab.

Public URL:

```text
https://glances.home.arpa
```

The container does not publish HTTP ports directly to the LAN. Caddy reaches it over Docker networking at:

```text
glances:61208
```

Glances was chosen because it provides a simple live view of CPU, memory, disk, network, uptime, and load information without introducing a historical monitoring stack.

Homepage remains the HomeLab landing page. Glances provides the live operational status behind the Homepage widgets and the standalone monitoring UI.

## Host Access

The container uses only the host access currently needed for lightweight monitoring:

- `pid: host` lets Glances show host processes instead of only the Glances container process.
- `/:/host:ro` lets Glances report host disk usage without write access.
- `/etc/os-release:/etc/os-release:ro` lets the UI show host OS details instead of only the container image.

Docker socket access is intentionally not enabled. `privileged: true` and host networking are intentionally not used. Network interface visibility may be less complete than a privileged host-network deployment, but this keeps the service aligned with the HomeLab least-privilege posture.

Prometheus and Grafana are intentionally deferred until historical metrics, alerting, or long-term dashboards become necessary.
