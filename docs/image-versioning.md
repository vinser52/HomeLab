# Image Versioning

This document defines how Docker image tags should be managed in the HomeLab repository.

## Why Explicit Versions Are Preferred

Explicit image tags make deployments reproducible.

When a compose file pins a specific version, the repository describes the exact software that should run. This improves correctness, makes rollbacks easier, and keeps operational changes visible in Git history.

Explicit versions are especially important for infrastructure services such as DNS and reverse proxy components. These services define platform behavior for everything else in the HomeLab and should not change unexpectedly.

## Why `latest` Is Discouraged

The `latest` tag is mutable. The same compose file can deploy different software on different days without any Git change.

That makes troubleshooting harder, weakens rollback confidence, and breaks the repository's role as the source of truth. It also makes upgrades less deliberate because version changes can arrive implicitly during routine pulls or redeploys.

For the HomeLab, `latest` should be treated as an exception that requires a documented reason.

## Policy

- Infrastructure services must use explicit immutable version tags.
- Applications should use explicit version tags whenever practical.
- Avoid `latest` unless there is a documented reason.
- Avoid floating tags such as `2`, `15`, `stable`, or `main` unless there is a documented justification.
- Prefer fully qualified image names where that improves clarity, such as `docker.io/library/caddy` or `ghcr.io/gethomepage/homepage`.

## Recommended Repository Pattern

The repository should keep image versions directly in Git-managed Compose files:

```yaml
image: docker.io/example/service:1.2.3
```

This keeps the intended infrastructure state explicit and avoids version drift caused by runtime overrides.

## How DIUN Will Fit

DIUN should inform the update workflow, not replace it.

Its role will be to notify when a new upstream image version is available. DIUN should not silently advance running versions and should not bypass Git-controlled compose updates.

The HomeLab source of truth should remain:

1. version notice
2. release note review
3. compose update
4. Git commit
5. deploy

## Expected Update Process

```text
New version available
↓
Read release notes
↓
Update compose.yaml
↓
Commit
↓
Push
↓
Auto Deploy
```

## Practical Rules

- Check upstream release notes before changing an image tag.
- Upgrade one logical service at a time unless multiple upgrades are intentionally grouped.
- Keep version bumps as explicit Git commits.
- If an image must temporarily stay on `latest`, document why in the compose file and revisit it during future audits.
- Prefer replacing an image with a tag like `v2.0.6` over keeping `latest` when the upstream publishes versioned tags.
