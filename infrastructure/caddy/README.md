# Caddy

This directory is reserved for the future Caddy reverse proxy setup.

Caddy is planned to become the single HTTP/HTTPS entrypoint for HomeLab Web UIs and application services. It is not added yet, and this directory intentionally contains no Compose service at this stage.

DNS protocol traffic on TCP/UDP port `53` will continue to go directly to the DNS service. Caddy will only route HTTP/HTTPS traffic such as `dns.home.arpa`, `jellyfin.home.arpa`, and future application names.
