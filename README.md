# HomeLab

Docker Compose setup for a small HomeLab DNS stack with Technitium DNS Server.

Network assumptions:

- FritzBox router: `192.168.178.1`
- HomeLab server: `192.168.178.188`
- Local domain: `home.arpa`
- Technitium web UI: `http://192.168.178.188:5380`
- DNS service: `192.168.178.188:53` over TCP and UDP

## Repository Layout

```text
HomeLab/
|-- compose.yaml
|-- .env.example
|-- .gitignore
|-- README.md
|-- docs/
|   |-- architecture.md
|   |-- dns.md
|   `-- networking.md
|-- infrastructure/
|   |-- caddy/
|   |   `-- README.md
|   `-- technitium/
|       |-- compose.yaml
|       `-- data/
`-- applications/
```

`infrastructure/` is for shared platform services that other workloads depend on.
`applications/` is reserved for app stacks that will sit on top of that base later.

Technitium belongs under `infrastructure/` because DNS is foundational for the rest of the HomeLab.
DNS cannot be fully hidden behind Caddy later, since DNS traffic uses TCP/UDP port `53` rather than HTTP/HTTPS.
Only the Technitium Web UI will later move behind Caddy, while the DNS service itself will continue to publish port `53`.

## Setup

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Review `.env` and change `DNS_SERVER_ADMIN_PASSWORD` before first start.

3. Start the stack:

   ```bash
   docker compose up -d
   ```

4. Open the Technitium web UI:

   [http://192.168.178.188:5380](http://192.168.178.188:5380)

Technitium data persists under `infrastructure/technitium/data/` and is ignored by git.

## Initial Technitium DNS Configuration

1. Sign in to the Technitium web UI with the admin password from `.env`.
2. Create a primary zone named `home.arpa`.
3. Add a wildcard `A` record:

   - Name: `*`
   - Type: `A`
   - Value: `192.168.178.188`

4. Optionally add an apex `A` record for `home.arpa` pointing to `192.168.178.188` if you also want the root name to resolve.

## DNS Testing

Use either `nslookup` or `dig` from a client that is pointed at `192.168.178.188`.

```bash
nslookup test.home.arpa 192.168.178.188
dig @192.168.178.188 test.home.arpa
dig @192.168.178.188 anything.home.arpa +short
```

Expected result: wildcard names under `home.arpa` should resolve to `192.168.178.188`.

## FritzBox DNS Test Scenarios

### Scenario 1: FritzBox DHCP announces Technitium as local DNS

Goal: clients receive `192.168.178.188` directly as their DNS server via DHCP.

1. In FritzBox LAN/DHCP settings, configure the local DNS server handed to clients as `192.168.178.188` if your FritzBox model and firmware expose that option.
2. Renew DHCP leases on one or more test clients.
3. Confirm the client now uses `192.168.178.188` for DNS.
4. Test:

   ```bash
   nslookup test.home.arpa
   dig test.home.arpa
   ```

If the client shows `192.168.178.188` as its resolver and the queries succeed, DHCP distribution is working.

### Scenario 2: FritzBox uses Technitium upstream, Cloudflare as fallback

Goal: FritzBox stays the client-facing resolver, but forwards upstream queries to Technitium first.

1. In FritzBox internet or DNS settings, configure the custom DNS server to `192.168.178.188` where supported.
2. Configure Cloudflare as fallback or secondary DNS using:

   - `1.1.1.1`
   - `1.0.0.1`

3. Leave clients using the FritzBox as their normal DNS server.
4. Test from a client:

   ```bash
   nslookup test.home.arpa
   dig test.home.arpa
   ```

5. Verify that local names still resolve and that general internet DNS continues working if Technitium is unavailable.

Note: FritzBox DNS options vary by hardware model and FRITZ!OS version. If your router cannot advertise a custom LAN DNS server or cannot use a LAN host as upstream DNS, keep clients pointed directly at `192.168.178.188` instead.
