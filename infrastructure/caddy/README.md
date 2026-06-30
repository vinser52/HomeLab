# Caddy

Caddy is the HomeLab HTTP/HTTPS reverse proxy.

It publishes HTTP on `192.168.178.2:80/tcp` and HTTPS on `192.168.178.2:443/tcp`. HTTPS uses Caddy's internal CA for LAN-only TLS. Let's Encrypt is not used.

The first route is:

```text
https://dns.home.arpa -> technitium:5380
```

The first application route is:

```text
https://homepage.home.arpa -> homepage:3000
https://speedtest.home.arpa -> openspeedtest:3000
https://glances.home.arpa -> glances:61208
https://status.home.arpa -> uptime-kuma:3001
```

DNS protocol traffic on TCP/UDP port `53` continues to go directly to Technitium. Caddy only routes HTTP traffic such as `dns.home.arpa`, `homepage.home.arpa`, `speedtest.home.arpa`, `glances.home.arpa`, `status.home.arpa`, `jellyfin.home.arpa`, and future application names.

Caddy's internal CA material lives under `infrastructure/caddy/data/`, which is runtime data and must not be committed.
