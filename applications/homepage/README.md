# Homepage

Homepage is the landing page of the HomeLab.

Public URL:

```text
http://homepage.home.arpa
```

The container does not publish HTTP ports directly to the LAN. Caddy reaches it over Docker networking at:

```text
homepage:3000
```

`HOMEPAGE_ALLOWED_HOSTS` is set to `homepage.home.arpa` so Homepage accepts requests routed through Caddy.

Configuration is stored as YAML in `applications/homepage/config/` and committed to Git.

Homepage intentionally contains no secrets. Widgets requiring authentication should be added incrementally once a token strategy exists.

Enabled widgets:

- Resources: CPU, memory, and disk usage.
- Date & Time.

The Resources widget uses a read-only host filesystem mount at `/host` so disk usage reflects the HomeLab server instead of only the container filesystem.

Docker socket access is intentionally not enabled. Docker integration can be added later if there is a real operational need.
