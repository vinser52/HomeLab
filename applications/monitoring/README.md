# Monitoring

Monitoring provides historical host, container, Intel GPU, reverse proxy, DNS, and gateway metrics for the HomeLab using Prometheus, Grafana, node-exporter, cAdvisor, intel-gpu-exporter, Caddy's built-in metrics endpoint, technitium-exporter, and fritz-exporter.

Public URL:

```text
https://grafana.home.arpa
```

Only Grafana is exposed through Caddy. Prometheus, cAdvisor, intel-gpu-exporter, technitium-exporter, and fritz-exporter stay internal on the Docker `proxy` network and do not publish ports directly to the LAN. Caddy metrics are exposed only on an internal metrics handler at `caddy:2019`. node-exporter uses the host network namespace so it can report the Ubuntu host's real network interfaces; as a result, its read-only metrics endpoint listens on the HomeLab server at port `9100`.

## Components

| Service | Purpose | Internal endpoint |
| --- | --- | --- |
| Grafana | Dashboards and metrics UI | `grafana:3000` |
| Prometheus | Metrics database and scraper | `prometheus:9090` |
| node-exporter | Ubuntu host metrics exporter | `homelab-server.home.arpa:9100` |
| cAdvisor | Container metrics exporter | `cadvisor:8080` |
| intel-gpu-exporter | Intel i915 GPU performance exporter | `intel-gpu-exporter:9100` |
| Caddy metrics | Reverse proxy metrics endpoint | `caddy:2019` |
| technitium-exporter | Technitium DNS metrics exporter | `technitium-exporter:9105` |
| fritz-exporter | FritzBox gateway metrics exporter | `fritz-exporter:9787` |

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
| `Intel GPU Overview` | Intel GPU engine utilization, frequency, power, wait state, and memory bandwidth. |
| `Reverse Proxy Overview` | Caddy request rate, response status, latency, in-flight requests, and process resource usage. |
| `DNS Server Overview` | Technitium DNS health, realtime query counters, cache/block ratios, zones, DHCP, protocols, query types, and top clients/domains. |
| `Network Gateway Overview` | FritzBox exporter health, WAN link state, current download/upload speed, link capacity, router uptime, Wi-Fi clients, and WAN traffic accounting. |
| `Monitoring Health` | Prometheus scrape health, scrape behavior, active series, DB size, and Prometheus process resource usage. |

`Network Gateway Overview` is adapted from Grafana dashboard `17751` for `pdreker/fritz_exporter`. The upstream dashboard expects DSL and per-host metrics, so the HomeLab version keeps the upstream layout and WAN/Wi-Fi panels but replaces DSL/PPP/host-info-dependent panels with cable-compatible FritzBox metrics. The 24-hour, 30-day, and hourly traffic panels use observed deltas from FritzBox WAN byte counters and stay empty until Prometheus has enough history for the requested time window.

## Host Metrics

node-exporter runs in a container but reports Ubuntu host metrics by using host network and PID visibility, mounting the host root filesystem read-only at `/host`, and using:

```text
--path.rootfs=/host
```

The container does not use `privileged: true` or the Docker socket. Host networking is an explicit exception for node-exporter because Linux network counters are network-namespace scoped; without host networking, node-exporter reports the container's `eth0` instead of the Ubuntu host's physical interfaces. Filesystem collector exclusions remove noisy pseudo-filesystems, Docker overlay mounts, Ubuntu Snap mounts, and container runtime paths so dashboard storage metrics focus on real host filesystems.

Prometheus preserves the public `homelab-server.home.arpa` scrape contract with
an explicit Docker `host-gateway` mapping. This avoids depending on Docker's
upstream DNS selection when the Ubuntu host has multiple resolvers and only
Technitium serves the local `home.arpa` zone. No LAN IP is hardcoded in the
monitoring stack.

## Container Metrics

cAdvisor reports per-container CPU, memory, network, filesystem usage, and filesystem I/O. It stays internal on the Docker `proxy` network and is scraped by Prometheus at `cadvisor:8080`.

cAdvisor does not use `privileged: true` or the Docker socket. It receives read-only access to the host root, `/var/run`, `/sys`, Docker runtime data, and disk metadata so it can inspect running containers.

## Intel GPU Metrics

intel-gpu-exporter wraps `intel_gpu_top` and exports i915 performance counters
to Prometheus. It receives the `/dev/dri` devices and only the Linux
`CAP_PERFMON` capability required to read performance counters. All other
capabilities are dropped, the container filesystem is read-only, and
`no-new-privileges` is enabled. The exporter does not use privileged mode, host
PID visibility, host networking, or the Docker socket.

The image is pinned by immutable linux/amd64 manifest digest because the
upstream project does not publish versioned releases. Prometheus scrapes the
exporter at `intel-gpu-exporter:9100`. The `Intel GPU Overview` dashboard shows
engine busy/wait/semaphore activity, actual and requested frequency, GPU and
package power where the platform exposes those counters, and integrated memory
controller bandwidth. Some power or bandwidth series may be absent when the
hardware or kernel does not expose the corresponding PMU counters.

## Reverse Proxy Metrics

Caddy exposes Prometheus metrics on an internal metrics handler at `caddy:2019/metrics`. Prometheus scrapes that endpoint from the Docker `proxy` network. The endpoint is not routed through Caddy, does not use Caddy's admin API, and is not published directly to the LAN.

The `Reverse Proxy Overview` dashboard shows request rate, response status, request duration, requests in flight, and Caddy process CPU and memory usage. These metrics observe the HomeLab HTTP contract boundary because Caddy is the only public HTTP/HTTPS entrypoint.

## DNS Metrics

technitium-exporter reports Technitium DNS metrics through the Technitium HTTP API. It stays internal on the Docker `proxy` network and is scraped by Prometheus at `technitium-exporter:9105`.

The exporter authenticates with the shared Technitium monitoring API token. Create a read-only Technitium user for monitoring, generate an API token for that user, and store it only in local `.env`:

```env
TECHNITIUM_API_TOKEN=
```

The exporter is configured for a single Technitium DNS server at `http://technitium:5380`, uses the Prometheus label `server="technitium"`, and reads Technitium dashboard-window metrics for `LastHour`. Its realtime metrics use Technitium v15 lifetime counters where available, which are better suited for Prometheus rates.

## Gateway Metrics

fritz-exporter reports FritzBox metrics over the local TR-064 API. It stays internal on the Docker `proxy` network and is scraped by Prometheus at `fritz-exporter:9787`.

The exporter authenticates with a dedicated FritzBox monitoring user. Store the credentials only in local `.env`:

```env
FRITZ_EXPORTER_USERNAME=homelab-monitoring
FRITZ_EXPORTER_PASSWORD=
```

fritz-exporter v3 listens on `127.0.0.1` by default, so the Compose service explicitly sets `FRITZ_LISTEN_ADDRESS=0.0.0.0` for Prometheus scraping over Docker networking. Extended per-host information is disabled because it can take 20+ seconds on busy networks. The Prometheus scrape interval is 15 seconds so short WAN bursts, such as speed tests, are more likely to be visible without enabling expensive per-host polling.

## Validation

Run Compose validation locally on the MacBook before deployment:

```bash
docker compose config --quiet
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
docker compose logs --tail=100 intel-gpu-exporter
docker compose logs --tail=100 caddy
docker compose logs --tail=100 technitium-exporter
docker compose logs --tail=100 fritz-exporter
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="node-exporter"}'
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="cadvisor"}'
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="intel-gpu-exporter"}'
docker compose exec prometheus promtool query instant http://localhost:9090 'gpumon_engine_usage{job="intel-gpu-exporter",attrib="busy"}'
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="caddy"}'
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="technitium-exporter"}'
docker compose exec prometheus promtool query instant http://localhost:9090 'technitium_up'
docker compose exec prometheus promtool query instant http://localhost:9090 'up{job="fritz-exporter"}'
docker compose exec prometheus promtool query instant http://localhost:9090 'fritz_wan_data_bytes_total'
```

`up{job="fritz-exporter"}` only confirms that Prometheus can scrape the exporter process. If fritz-exporter logs `Action Not Authorized`, the exporter is reachable but the FritzBox user lacks the rights needed for TR-064 metric calls. Expand the dedicated FritzBox monitoring user's local rights, restart fritz-exporter, and confirm that FritzBox metrics such as `fritz_wan_data_bytes_total` return data.

From a LAN client, validate the public service contract:

```bash
nslookup grafana.home.arpa
curl -k -I https://grafana.home.arpa
```

In Grafana, confirm that the Prometheus datasource is healthy and that these PromQL queries return data:

```promql
up{job="node-exporter"}
up{job="intel-gpu-exporter"}
gpumon_engine_usage{attrib="busy"}
gpumon_frequency
node_uname_info
node_memory_MemAvailable_bytes
rate(node_cpu_seconds_total[5m])
node_filesystem_avail_bytes
rate(node_network_receive_bytes_total{device!~"lo|docker.*|br-.*|veth.*"}[5m])
container_memory_working_set_bytes
caddy_http_requests_total
technitium_up
rate(technitium_dns_realtime_queries_total[5m])
technitium_dns_queries_window
fritz_wan_data_bytes_total
fritz_wan_datarate_bytes
prometheus_tsdb_head_series
prometheus_tsdb_storage_blocks_bytes
```

The MVP is working when Grafana loads through Caddy, Prometheus reports the node-exporter, cAdvisor, intel-gpu-exporter, Caddy, technitium-exporter, and fritz-exporter targets as up, `Host Metrics Overview` shows Ubuntu host CPU, memory, filesystem, load, network throughput, packet rate, errors, drops, and interface state without noisy container filesystems or virtual network interfaces dominating the view, `Container Metrics Overview` shows per-container resource usage, `Intel GPU Overview` shows i915 engine utilization and frequency, `Reverse Proxy Overview` shows Caddy traffic and latency, `DNS Server Overview` shows Technitium DNS health and query metrics, `Network Gateway Overview` shows FritzBox WAN speed, capacity, traffic accounting, Wi-Fi, and router health metrics, and `Monitoring Health` shows the monitoring targets and Prometheus itself as healthy.
