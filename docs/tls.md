# TLS

The HomeLab uses Caddy's internal CA for local HTTPS.

This is LAN-only TLS:

- No public CA is used.
- Let's Encrypt is not used.
- No ports are opened to the Internet.
- DNS names stay under `home.arpa`.

Caddy issues certificates for HomeLab service names such as `homepage.home.arpa`, `dns.home.arpa`, `speedtest.home.arpa`, `glances.home.arpa`, and `status.home.arpa`.

Browsers and operating systems will warn until Caddy's root CA is trusted on each client device. After the root CA is trusted once, certificates issued by this Caddy instance are trusted automatically.

Do not commit Caddy certificates, private keys, or CA material to Git. Caddy stores this runtime material under:

```text
${HOMELAB_STATE_DIR}/caddy/data
```

The expected root certificate path is:

```text
${HOMELAB_STATE_DIR}/caddy/data/caddy/pki/authorities/local/root.crt
```

Find it on the HomeLab server with:

```bash
find "${HOMELAB_STATE_DIR:-/homelab/state}/caddy/data" -name root.crt
```

## macOS Trust Setup

1. Copy `root.crt` from the HomeLab server to the Mac.
2. Open Keychain Access.
3. Import `root.crt` into the System keychain.
4. Open the imported certificate.
5. Set Trust to Always Trust.
6. Close the certificate window and approve the change.

After trusting the CA, this should work without `-k`:

```bash
curl -I https://homepage.home.arpa
```

## iOS And iPadOS Trust Setup

1. Transfer or open `root.crt` on the device.
2. Install the downloaded configuration profile.
3. Open Settings.
4. Go to General > About > Certificate Trust Settings.
5. Enable full trust for the Caddy root certificate.

After this, Safari and apps that use the system trust store should trust HomeLab HTTPS certificates issued by Caddy.
