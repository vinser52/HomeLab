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

Homepage intentionally contains no secrets. Widgets requiring authentication should be added incrementally once a token strategy exists.

Enabled widgets:

- Glances: CPU, memory, disk usage, and uptime from the Glances API.
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

Manual setup after deployment:

1. Open `https://status.home.arpa`.
2. Create the simple HTTP monitors for the HomeLab services.
3. Create a local status page with slug `homelab`, or set `HOMEPAGE_VAR_UPTIME_KUMA_STATUS_SLUG` in `.env` to match your chosen slug.
4. Add the monitors to that status page.

Do not configure notifications or public/external status publishing yet.

The previous read-only host filesystem mount is no longer needed by Homepage because disk metrics now come from Glances.

Docker socket access is intentionally not enabled. Docker integration can be added later if there is a real operational need.
