# Security

## Reporting

Report security issues privately to the project maintainers. Do not open public issues for unfixed vulnerabilities.

## Local mpv IPC

The JSON IPC socket is a **local privileged control interface**. It is not authenticated.

- Socket lives in a private per-user runtime directory
- The app terminates only the mpv process it started
- Never expose the socket over the network

## Untrusted playlists

M3U files may contain arbitrary URLs. Treat third-party playlists as untrusted input.

## External executables

`mpv` and `yt-dlp` are discovered via PATH or explicit environment overrides. Only point overrides at trusted binaries.

## Privacy

No analytics or telemetry. History and title caches stay on the local machine. Personal playlists and media must not be committed to the repository.
