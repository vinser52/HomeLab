# Monitoring

Monitoring provides historical host, container, and reverse proxy metrics for the HomeLab using Prometheus, Grafana, node-exporter, cAdvisor, and Caddy's built-in metrics endpoint.

Public URL:

```text
https://grafana.home.arpa
```

Only Grafana is exposed through Caddy. Prometheus and cAdvisor stay internal on the Docker `proxy` network and do not publish ports directly to the LAN. Caddy metrics are exposed only on an internal metrics handler at `caddy:2019`. node-exporter uses the host network namespace so it can report the Ubuntu host's real network interfaces; as a result, its read-only metrics endpoint listens on the HomeLab server at port `9100`.

## Components

| Service | Purpose | Internal endpoint |
| --- | --- | --- |
| Grafana | Dashboards and metrics UI | `grafana:3000` |
| Prometheus | Metrics database and scraper | `prometheus:9090` |
| node-exporter | Ubuntu host metrics exporter | `homelab-server.home.arpa:9100` |
| cAdvisor | Container metrics exporter | `cadvisor:8080` |
| Caddy metrics | Reverse proxy metrics endpoint | `caddy:2019` |

## Runtime Data

Runtime state lives outside Git:

```text
${HOMELAB_STATE_DIR}/grafana/data
${HOMELAB_STATE_DIR}/prometheus/data
```

Grafana's runtime database stores local users, sessions, preferences, and dashboards created through the UI. Prometheus stores its time-series database under its state directory.

Before first start on the Ubuntu HomeLab server, create the state directories with the same owner used by the containers:

```bash
set -a
. ./.env
set +a
sudo install -d -o "${HOMELAB_UID:-1000}" -g "${HOMELAB_GID:-1000}" "${HOMELAB_STATE_DIR:-/homelab/state}/grafana/data"
sudo install -d -o "${HOMELAB_UID:-1000}" -g "${HOMELAB_GID:-1000}" "${HOMELAB_STATE_DIR:-/homelab/state}/prometheus/data"
```

If Docker already created these directories as `root`, fix ownership before restarting the services:

```bash
set -a
. ./.env
set +a
sudo chown -R "${HOMELAB_UID:-1000}:${HOMELAB_GID:-1000}" "${HOMELAB_STATE_DIR:-/homelab/state}/grafana/data"
sudo chown -R "${HOMELAB_UID:-1000}:${HOMELAB_GID:-1000}" "${HOMELAB_STATE_DIR:-/homelab/state}/prometheus/data"
docker compose up -d grafana prometheus
```

Git-managed desired configuration lives under:

```text
applications/monitoring/config/
```

Grafana provisioning config creates the Prometheus datasource and loads committed dashboards from `applications/monitoring/config/grafana/dashboards/`.

Initial dashboards:

| Dashboard | Purpose |
| --- | --- |
| `Host Metrics Overview` | Ubuntu host CPU, memory, filesystem, load, and network metrics. |
| `Container Metrics Overview` | Docker container CPU, memory, network, filesystem usage, and filesystem I/O. |
| `Reverse Proxy Overview` | Caddy request rate, response status, latency, in-flight requests, and process resource usage. |
| `Monitoring Health` | Prometheus scrape health, scrape behavior, active series, DB size, and Prometheus process resource usage. |

## Host Metrics

node-exporter runs in a container but reports Ubuntu host metrics by using host network and PID visibility, mounting the host root filesystem read-only at `/host`, and using:

```text
--path.rootfs=/host
```

The container does not use `privileged: true` or the Docker socket. Host networking is an explicit exception for node-exporter because Linux network counters are network-namespace scoped; without host networking, node-exporter reports the container's `eth0` instead of the Ubuntu host's physical interfaces. Filesystem collector exclusions remove noisy pseudo-filesystems, Docker overlay mounts, Ubuntu Snap mounts, and container runtime paths so dashboard storage metrics focus on real host filesystems.

## Container Metrics

cAdvisor reports per-container CPU, memory, network, filesystem usage, and filesystem I/O. It stays internal on the Docker `proxy` network and is scraped by Prometheus at `cadvisor:8080`.

cAdvisor does not use `privileged: true` or the Docker socket. It receives read-only access to the host root, `/var/run`, `/sys`, Docker runtime data, and disk metadata so it can inspect running containers.

## Reverse Proxy Metrics

Caddy exposes Prometheus metrics on an internal metrics handler at `caddy:2019/metrics`. Prometheus scrapes that endpoint from the Docker `proxy` network. The endpoint is not routed through Caddy, does not use Caddy's admin API, and is not published directly to the LAN.

The `Reverse Proxy Overview` dashboard shows request rate, response status, request duration, requests in flight, and Caddy process CPU and memory usage. These metrics observe the HomeLab HTTP contract boundary because Caddy is the only public HTTP/HTTPS entrypoint.

## Validation

Run Compose validation locally on the MacBook before deployment:

```bash
docker compose config
```

Runtime validation should be run on the Ubuntu HomeLab server after pulling the updated repository:

```bash
docker compose up -d
docker compose up -d --force-recreate caddy
docker compose up -d --force-recreate prometheus
docker compose ps
docker compose logs --tail=100 prometheus
docker compose logs --tail=100 grafana
docker compose logs --tail=100 node-exporter
docker compose logs --tail=100 cadvisor
docker compose logs --tail=100 caddy
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="node-exporter"}'
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="cadvisor"}'
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="caddy"}'
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
rate(node_network_receive_bytes_total{device!~"lo|docker.*|br-.*|veth.*"}[5m])
container_memory_working_set_bytes
caddy_http_requests_total
prometheus_tsdb_head_series
prometheus_tsdb_storage_blocks_bytes
```

The MVP is working when Grafana loads through Caddy, Prometheus reports the node-exporter, cAdvisor, and Caddy targets as up, `Host Metrics Overview` shows Ubuntu host CPU, memory, filesystem, load, network throughput, packet rate, errors, drops, and interface state without noisy container filesystems or virtual network interfaces dominating the view, `Container Metrics Overview` shows per-container resource usage, `Reverse Proxy Overview` shows Caddy traffic and latency, and `Monitoring Health` shows Prometheus, node-exporter, cAdvisor, and Caddy scrape health.
