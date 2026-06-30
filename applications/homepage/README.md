# Homepage

Homepage is the landing page of the HomeLab.

Public URL:

```text
https://homepage.home.arpa
```

The container does not publish HTTP ports directly to the LAN. Caddy reaches it over Docker networking at:

```text
homepage:3000
```

`HOMEPAGE_ALLOWED_HOSTS` is set to `homepage.home.arpa` so Homepage accepts requests routed through Caddy.

Configuration is stored as YAML in `applications/homepage/config/` and committed to Git.

Service cards in `services.yaml` use explicit icon names so the HomeLab landing page stays visually scannable without changing any public service contracts.

Homepage intentionally contains no committed secrets. Authenticated widgets use `.env` placeholders so tokens stay local to the deployment.

Enabled widgets:

- Glances: CPU, memory, disk usage, and uptime from the Glances API.
- Technitium: DNS query and cache statistics from the Technitium API.
- Date & Time.

Homepage gets live host metrics from Glances at `http://glances:61208` over the shared Docker `proxy` network. The standalone Glances UI provides deeper live details such as network throughput and load average.

The Uptime Kuma card uses Homepage's built-in Uptime Kuma widget. Homepage connects to Uptime Kuma over Docker networking at:

```text
http://uptime-kuma:3001
```

The card opens the user-facing Uptime Kuma UI at:

```text
https://status.home.arpa
```

The widget does not use an API key. It reads from a Uptime Kuma status page identified by `HOMEPAGE_VAR_UPTIME_KUMA_STATUS_SLUG`, which defaults to `homelab`.

The DNS card uses Homepage's built-in Technitium widget. Homepage connects to Technitium over Docker networking at:

```text
http://technitium:5380
```

The widget uses `HOMEPAGE_VAR_TECHNITIUM_API_KEY` from `.env`. Leave the token out of Git.

Manual setup after deployment:

1. Open `https://status.home.arpa`.
2. Create the simple HTTP monitors for the HomeLab services.
3. Create a local status page with slug `homelab`, or set `HOMEPAGE_VAR_UPTIME_KUMA_STATUS_SLUG` in `.env` to match your chosen slug.
4. Add the monitors to that status page.
5. Open `https://dns.home.arpa`.
6. Create a dedicated Technitium user for Homepage with the minimum dashboard permissions needed for read-only statistics.
7. Generate an API token for that user and set `HOMEPAGE_VAR_TECHNITIUM_API_KEY` in `.env`.

Do not configure notifications or public/external status publishing yet.

The previous read-only host filesystem mount is no longer needed by Homepage because disk metrics now come from Glances.

Docker socket access is intentionally not enabled. Docker integration can be added later if there is a real operational need.
