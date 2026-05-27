# Theridion FE

Frontend automation desktop app — Playwright multi-browser runner with visual regression,
accessibility audit (axe-core), network interception, and run history. One file-based
workspace, no cloud dependency.

## Architecture

- **Shell:** Tauri 2.11 (Rust) + WebView
- **UI:** React 18 + TypeScript + Tailwind
- **Sidecar:** Python FastAPI (apps/sidecar-fe) bundled with PyInstaller, spawned by
  the Tauri shell over loopback HTTP. Slim deps — no gRPC/Kafka/JMS/SOAP (those live
  in the Theridion BE sidecar).
- **Test orchestration:** sidecar shells out to `npx playwright test` (Playwright is
  not a pip dep — `npx` lazily resolves it from the runner's `node_modules`).

## First-time setup

```bash
cd apps/studio-fe
pnpm install
pnpm sidecar:bundle    # builds Python sidecar → src-tauri/binaries/theridion-sidecar-fe-<triple>
pnpm tauri:dev         # opens the FE app window
```

Dev port: 1430 (so BE 1420 + FE 1430 can run concurrently).

## Build for distribution

```bash
pnpm sidecar:bundle
pnpm tauri:build       # produces dmg/deb/AppImage/msi in src-tauri/target/release/bundle/
```

## CI release pipeline

Tag-triggered build via [`.github/workflows/desktop-release.yml`](../../.github/workflows/desktop-release.yml).
Matrix: 4 OS × 2 apps (BE + FE) = 8 artifacts uploaded to GitHub Releases.

Required secrets (all optional — missing = unsigned artifact):

| Secret | Used for |
|---|---|
| `APPLE_CERTIFICATE` + `APPLE_CERTIFICATE_PASSWORD` + `APPLE_SIGNING_IDENTITY` | macOS code signing |
| `APPLE_ID` + `APPLE_PASSWORD` + `APPLE_TEAM_ID` | macOS notarization |
| `WINDOWS_CERTIFICATE_PFX_BASE64` + `WINDOWS_CERTIFICATE_PASSWORD` | Windows code signing |
| `TAURI_SIGNING_PRIVATE_KEY` + `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | Tauri auto-updater signature |

## Auto-updater

`tauri.conf.json` points at:
```
https://github.com/qa-wave/theridion/releases/latest/download/latest-fe.json
```

On each release, CI uploads `latest-fe.json` to the GitHub Release. The Tauri updater
fetches it on app start, compares versions, and prompts the user to install. Set
`TAURI_SIGNING_PRIVATE_KEY` + `pubkey` in the config before enabling the updater in
production — otherwise updates are unsigned and Tauri will refuse them.
