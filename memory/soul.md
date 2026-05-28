# Theridion FE — identita

Frontend automation desktop app — multi-framework runner s built-in recorderem. **Co děláme**: necháváme uživatele zvolit Playwright / Cypress / Selenium / WebdriverIO / Puppeteer a publikovat výsledky do Hub.

## Mantinely

- **Boring tech.** Tauri 2 + React + slim Python sidecar. Žádné novelty.
- **Multi-framework adapter.** Theridion runner normalizuje assertion DSL napříč backendy.
- **Recorder = Codegen + selector picker.** Žádný custom recorder engine — Playwright Codegen ve wrapperu.
- **Cross-framework export.** Spec napsaný v Theridion → export do Playwright TS / Cypress JS / Selenium Python / WebdriverIO.

## Nedělej

- ❌ Nepřidávej nové frameworky bez adapter testů
- ❌ Necommituj test artefakty (screenshots/videos)
- ❌ Subprocess Playwright bez auth tokenu — security gate
- ❌ Bundle Playwright deps do sidecar (lazy `npx` resolve)

## Out of scope (zatím)

- Visual baseline cloud review
- Distributed run grid
- Mobile native automation (Appium) — odloženo
