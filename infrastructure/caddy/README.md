# Caddy

Caddy is the HomeLab HTTP reverse proxy.

It currently publishes HTTP only on `192.168.178.2:80/tcp`. HTTPS/TLS is not configured yet and will be handled later as a separate step.

The first route is:

```text
http://dns.home.arpa -> technitium:5380
```

DNS protocol traffic on TCP/UDP port `53` continues to go directly to Technitium. Caddy only routes HTTP traffic such as `dns.home.arpa`, `jellyfin.home.arpa`, and future application names.
