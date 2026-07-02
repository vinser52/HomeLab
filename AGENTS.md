# HomeLab AI Development Guide

## Mission

This repository is the single source of truth for the HomeLab.

It describes the intended architecture, deployment structure, and operational conventions. Runtime state, secrets, generated data, and user data are not part of Git.

## Current Architecture Snapshot

Current platform:

- Router: FritzBox
- HomeLab server: Ubuntu Server
- Hostname: homelab-server.home.arpa
- Local domain: home.arpa

Infrastructure:

- DNS: Technitium DNS Server
- HTTP Reverse Proxy: Caddy

Networking:

- Docker shared network: proxy
- Caddy is the only HTTP entrypoint.
- DNS protocol uses TCP/UDP port 53 directly.

Current applications:

- Homepage
- OpenSpeedTest
- Glances
- Uptime Kuma

## Project Philosophy

- Infrastructure before applications.
- Prefer simple and maintainable solutions.
- Prefer explicit configuration over magic.
- Contracts are more important than implementations.
- Minimize operational complexity.
- Keep the HomeLab understandable after several years.

The HomeLab should be easy to reason about, easy to recover, and boring in the best possible way.

## Design Priorities

Architectural decisions should use this priority order:

1. Correctness
2. Simplicity
3. Maintainability
4. Consistency
5. Performance
6. Convenience

Performance optimizations should never unnecessarily increase architectural complexity for a HomeLab.

## Architecture Principles

The repository is organized by responsibility: infrastructure services live in `infrastructure/`, applications live in `applications/`, and documentation lives in `docs/`.

Every architectural decision should reinforce this separation. Platform services should not be mixed with user-facing applications, and application-specific concerns should not leak into shared infrastructure unless there is a clear architectural reason.

## Infrastructure vs Applications

Infrastructure provides shared platform capabilities. Examples include Technitium and Caddy.

Applications provide user-facing functionality. Examples include Homepage, OpenSpeedTest, Jellyfin, Immich, and Paperless.

Keep this boundary clear. Infrastructure should make applications easier to run; applications should not redefine the platform.

## Monitoring Philosophy

Homepage is the HomeLab landing page.

Glances provides live operational status.

Uptime Kuma provides service availability monitoring.

Prometheus and Grafana are future historical monitoring tools and should be added only when history, alerting, or dashboards are needed.

## Contracts vs Implementations

The architecture depends on stable contracts, not specific implementations.

For example, `speedtest.home.arpa` is a public service contract. Today the implementation may be OpenSpeedTest. Tomorrow it could become another application. Clients should keep using the same name and should not need to know what implementation serves it.

Likewise, `dns.home.arpa` is a service contract. Technitium is the current implementation, but another DNS service could fulfill the same contract later.

Prefer documenting and preserving the contract first. Treat implementations as replaceable unless there is a strong reason not to.

## Networking Rules

- `home.arpa` is the only local domain.
- Prefer DNS names instead of IP addresses.
- Do not hardcode LAN IPs unless absolutely required.
- Use Docker service names for container-to-container communication.
- Caddy is the single HTTP entrypoint.
- DNS traffic always goes directly to the DNS server.

Caddy proxies HTTP traffic. It does not proxy DNS protocol traffic.

## Networking Philosophy

- DNS names are preferred over IP addresses.
- Host names identify machines.
- Service names identify capabilities.
- Applications should never depend on which machine hosts them.
- Docker service names should be used for internal communication.
- `home.arpa` is the stable public namespace of the HomeLab.

## Reverse Proxy Rules

- Caddy is the only HTTP reverse proxy.
- HTTP applications should not publish ports directly to the LAN.
- Applications should be reachable through Caddy.
- Docker containers should communicate using Docker networking and service names.
- DNS is the only infrastructure service that publishes TCP/UDP port `53` directly.
- HTTPS/TLS will be terminated by Caddy when enabled.

## Docker Compose Rules

Every application should:

- have its own `compose.yaml`
- live in its own directory
- avoid publishing HTTP ports directly
- join the shared `proxy` network
- be reachable through Caddy

Application containers should communicate over Docker networks and use Docker DNS service names internally.

Host port publishing should be avoided unless the protocol requires direct LAN access. Only infrastructure services, such as DNS and the reverse proxy, should normally publish ports to the host.

Infrastructure services may expose ports only when required by their protocols. For example, DNS must publish TCP/UDP port `53` directly because DNS is not HTTP traffic.

## Image Versioning

- Never use mutable image tags such as `latest`.
- Pin every infrastructure and application image to explicit versions.
- Image upgrades should always be deliberate Git commits.
- Reproducible deployments are preferred over automatic upgrades.

## Repository Rules

Infrastructure belongs under `infrastructure/`.

Applications belong under `applications/`.

Every application should contain `compose.yaml` and `README.md`.

Persistent runtime data belongs outside the Git repository. Runtime data must never be committed.

## Runtime Data Layout

- Git repository contains desired configuration only.
- Runtime service state lives under `${HOMELAB_STATE_DIR}`.
- User storage lives under `${HOMELAB_STORAGE_DIR}`.
- Do not add persistent runtime bind mounts inside the Git repository.
- Keep Git-managed static config in Git when it is truly desired configuration.
- Use environment variables for host-specific base paths.

## Security Rules

Never commit `.env`, passwords, API keys, runtime data, or generated databases.

Prefer environment variables for configuration.

Do not expose services to the Internet unless explicitly requested.

## Least Privilege

AI agents should avoid giving containers unnecessary privileges.

- Do not mount `/var/run/docker.sock` into application containers unless there is a clear architectural justification.
- Prefer least-privilege integrations.
- Avoid `privileged: true`.
- Avoid unnecessary Linux capabilities.
- Avoid host networking unless required.
- Prefer read-only mounts whenever practical.

## Documentation Rules

Whenever architecture changes, update:

- `README.md`
- relevant files in `docs/`

Do not leave documentation outdated. Architecture documentation is part of the implementation.

Documentation should explain why a design decision exists, not only what was configured. Architectural rationale is more valuable than implementation details.

## Backwards Compatibility

When changing architecture:

- Preserve existing public contracts whenever possible.
- Existing DNS names should continue working.
- Existing URLs should continue working.
- Existing directory layouts should remain stable unless there is a compelling architectural reason.

Favor incremental evolution over disruptive redesign.

## Change Strategy

Before introducing a new pattern, check whether an existing pattern can be reused.

Prefer consistency over novelty.

When adding a new application, follow the structure of existing applications. Do not invent new directory layouts without strong justification.

## Repository Evolution

New architectural patterns should emerge only after at least two real use cases.

Avoid introducing abstractions for hypothetical future needs.

## Preferred Development Workflow

When implementing a feature:

1. Understand the existing architecture.
2. Reuse existing conventions.
3. Keep changes small.
4. Update documentation.
5. Validate Docker Compose configuration.
6. Explain architectural decisions in the final summary.

## Long-Term Goals

The HomeLab is expected to grow.

Future services may include:

- Jellyfin
- Immich
- Paperless
- Grafana
- Prometheus

The architecture should remain stable as the number of services increases.

## Decision Making

When multiple valid solutions exist:

- Prefer the one already used elsewhere in the repository.
- Prefer explicit configuration over automation.
- Prefer fewer technologies over introducing a new dependency.
- Avoid solving hypothetical future problems unless there is evidence they are needed.
- Keep the repository approachable for someone reading it years later.

## AI Expectations

An AI agent should optimize for:

- simplicity
- maintainability
- consistency
- reproducibility
- clear documentation

Avoid introducing unnecessary complexity.

Avoid changing architecture without justification.

When uncertain, extend the existing architecture instead of replacing it.

## Guiding Principle

Every change should make the HomeLab:

- easier to understand
- easier to operate
- easier to recover
- easier to extend

If a proposed solution makes the architecture more complex without providing significant long-term value, prefer the simpler solution.
