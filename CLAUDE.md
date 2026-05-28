## Project metadata

| Klíč | Hodnota |
|---|---|
| **Name** | `theridion-fe` |
| **Group** | `qa-tooling` |
| **GitHub** | [qa-wave/theridion-fe](https://github.com/qa-wave/theridion-fe) |
| **Type** | Desktop (Tauri 2.11) — distributed Win/macOS/Linux binárka |

## Session start

1. `memory/soul.md` — identita projektu
2. `memory/memory.md` — index paměti
3. `apps/studio-fe/README.md` — supported frameworks + recorder
4. `CHANGELOG.md`

---

# Theridion FE — kontext

Frontend automation desktop app — multi-framework runner s built-in recorderem.

## Podporované frameworky

| Framework | Recorder | Multi-browser | Status |
|---|---|---|---|
| Playwright | Codegen built-in | Chromium/Firefox/WebKit | GA |
| Cypress | `cypress open` integration | Chromium-only | Beta |
| WebdriverIO | Selenium-IDE replay | Selenium browsers | Beta |
| Selenium WebDriver | Selenium-IDE import | Chrome/Firefox/Edge/Safari | Beta |
| Puppeteer | Codegen kompatibilní | Chromium-only | Alpha |

## Layout

```
theridion-fe/
├── apps/
│   ├── studio-fe/         Tauri shell + React/TS frontend (port 1430)
│   │   ├── src/           SilkPanel, ActivityBar, HubOverviewPanel
│   │   ├── src-tauri/     Rust shell (com.theridion.fe)
│   │   └── tests/e2e/
│   └── sidecar-fe/        Slim Python sidecar — silk + health + env + history
│       └── theridion_sidecar/  routers (Playwright orchestration only)
├── .github/workflows/
├── CHANGELOG.md
└── README.md
```

## Časté příkazy

```bash
cd apps/sidecar-fe && uv run pytest -q
cd apps/studio-fe && pnpm typecheck && pnpm build
cd apps/studio-fe && pnpm sidecar:bundle
cd apps/studio-fe && pnpm tauri:dev
```

## Příbuzné projekty

- **theridion-be** — sourozenecký projekt pro BE testing
- **theridion-hub** — agreguje Silk run history přes Runner ingest

---

Pokud potřebuješ upravit, edituj přímo `CLAUDE.md`.
