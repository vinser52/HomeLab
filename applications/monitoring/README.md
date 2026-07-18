# Monitoring

Monitoring provides historical host metrics for the HomeLab using Prometheus, Grafana, and node-exporter.

Public URL:

```text
https://grafana.home.arpa
```

Only Grafana is exposed through Caddy. Prometheus and node-exporter stay internal on the Docker `proxy` network and do not publish ports directly to the LAN.

## Components

| Service | Purpose | Internal endpoint |
| --- | --- | --- |
| Grafana | Dashboards and metrics UI | `grafana:3000` |
| Prometheus | Metrics database and scraper | `prometheus:9090` |
| node-exporter | Ubuntu host metrics exporter | `node-exporter:9100` |

## Runtime Data

Runtime state lives outside Git:

```text
${HOMELAB_STATE_DIR}/grafana/data
${HOMELAB_STATE_DIR}/prometheus/data
```

Grafana's runtime database stores local users, sessions, preferences, and dashboards created through the UI. Prometheus stores its time-series database under its state directory.

Git-managed desired configuration lives under:

```text
applications/monitoring/config/
```

Grafana provisioning config creates the Prometheus datasource and loads committed dashboards from `applications/monitoring/config/grafana/dashboards/`.

## Host Metrics

node-exporter runs in a container but reports Ubuntu host metrics by using host PID visibility, mounting the host root filesystem read-only at `/host`, and using:

```text
--path.rootfs=/host
```

The container does not use `privileged: true`, host networking, or the Docker socket. Filesystem collector exclusions remove noisy pseudo-filesystems, Docker overlay mounts, and container runtime paths so dashboard storage metrics focus on real host filesystems.

## Validation

Run Compose validation locally on the MacBook before deployment:

```bash
docker compose config
```

Runtime validation should be run on the Ubuntu HomeLab server after pulling the updated repository:

```bash
docker compose up -d
docker compose ps
docker compose logs --tail=100 prometheus
docker compose logs --tail=100 grafana
docker compose logs --tail=100 node-exporter
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="node-exporter"}'
```

From a LAN client, validate the public service contract:

```bash
nslookup grafana.home.arpa
curl -k -I https://grafana.home.arpa
```

In Grafana, confirm that the Prometheus datasource is healthy and that these PromQL queries return data:

```promql
up{job="node-exporter"}
node_uname_info
node_memory_MemAvailable_bytes
rate(node_cpu_seconds_total[5m])
node_filesystem_avail_bytes
```

The MVP is working when Grafana loads through Caddy, Prometheus reports the node-exporter target as up, and the `Host Metrics Overview` dashboard shows Ubuntu host CPU, memory, filesystem, and load metrics without noisy container filesystems dominating the view.
