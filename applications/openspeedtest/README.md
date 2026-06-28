# OpenSpeedTest

OpenSpeedTest is the current implementation for the `speedtest.home.arpa` service contract.

Public URL:

```text
http://speedtest.home.arpa
```

The container does not publish HTTP ports directly to the LAN. Caddy reaches it over Docker networking at:

```text
openspeedtest:3000
```

DNS does not need a dedicated record for this service because `*.home.arpa` already points to the HomeLab server.
