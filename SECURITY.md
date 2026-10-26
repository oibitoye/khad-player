# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x (main) | Yes |

## Reporting a vulnerability

**Do not open a public GitHub issue for exploitable vulnerabilities.**

Use GitHub’s private advisory form:

https://github.com/oibitoye/khad-player/security/advisories/new

Include:

- Affected version or commit
- Platform and architecture
- Impact assessment
- Reproduction steps (without publishing exploit payloads to public channels)

You should receive an acknowledgement when the maintainer reviews the advisory. Please allow reasonable time for investigation before any disclosure.

## Application security notes

See also [docs/SECURITY.md](docs/SECURITY.md) for runtime risks (local mpv IPC, untrusted playlists, external executables) and privacy expectations.

## Supply chain

- Dependabot monitors GitHub Actions and Python dependencies
- Pull request CI must pass before dependency updates are merged
- Releases are maintainer-controlled; package registries are not published automatically
