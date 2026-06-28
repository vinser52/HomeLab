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

Configuration is stored as YAML in `applications/homepage/config/` and committed to Git.

Homepage intentionally contains no secrets. Widgets requiring authentication should be added incrementally once a token strategy exists.
