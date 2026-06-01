import type { Messages } from "./types";

export const cs: Messages = {
  // ── App / footer ──────────────────────────────────────────────────────────
  "app.version": "Theridion FE v0.0.1",

  // ── ActivityBar ───────────────────────────────────────────────────────────
  "activityBar.aria": "Přepínač modulů",
  "activityBar.silk": "Silk (FE testy)",
  "activityBar.monitors": "Testovací monitory",
  "activityBar.hubOverview": "Přehled Hubu",
  "activityBar.mobile": "Mobilní zařízení",

  // ── EmptyState — monitors ─────────────────────────────────────────────────
  "monitors.title": "Testovací monitory",
  "monitors.description": "Plánované Playwright běhy (syntetické FE kontroly). Vytvoř monitor v Silk panelu přes tlačítko 'Schedule run'.",

  // ── SilkPanel — toolbar ───────────────────────────────────────────────────
  "silk.toolbar.record": "Nahrát",
  "silk.toolbar.record.title": "Nahrát nový spec přes Playwright codegen",
  "silk.toolbar.record.titleNoBrowsers": "Nejprve nainstaluj prohlížeče",
  "silk.toolbar.newTest": "Nový test",
  "silk.toolbar.newTest.title": "Vytvoř nový test ručně v editoru",
  "silk.toolbar.installBrowsers": "Nainstalovat prohlížeče",
  "silk.toolbar.refreshBrowserCheck": "Obnovit kontrolu prohlížečů",
  "silk.toolbar.refreshHistory": "Obnovit historii běhů",

  // ── SilkPanel — history sidebar ───────────────────────────────────────────
  "silk.history.title": "Historie",
  "silk.history.newRun.title": "Nový běh",
  "silk.history.empty.title": "Zatím žádné běhy",
  "silk.history.empty.description": "Spusť spec a výsledky se zobrazí zde",
  "silk.history.previousRuns": "Předchozí běhy",

  // ── SilkPanel — run form ──────────────────────────────────────────────────
  "silk.runForm.title": "Spustit spec",
  "silk.runForm.specPath.label": "Cesta ke spec souboru",
  "silk.runForm.specPath.placeholder": "/cesta/k/muj.spec.ts",
  "silk.runForm.workspaceDir.label": "Workspace adresář (volitelné)",
  "silk.runForm.workspaceDir.placeholder": "/cesta/k/projektu",
  "silk.runForm.browsers.label": "Prohlížeče",
  "silk.runForm.run": "Spustit",
  "silk.runForm.running": "Běží…",

  // ── SilkPanel — stats ─────────────────────────────────────────────────────
  "silk.stats.passed": "Prošlo",
  "silk.stats.failed": "Selhalo",
  "silk.stats.errors": "Chyby",
  "silk.stats.duration": "Trvání",
  "silk.stats.stderr": "stderr (posledních 20 řádků)",
  "silk.stats.selectRun": "Vyber běh z historie pro zobrazení výsledků",

  // ── SilkPanel — tabs ──────────────────────────────────────────────────────
  "silk.tabs.timeline": "Časová osa",
  "silk.tabs.network": "Síť",
  "silk.tabs.screenshots": "Snímky",
  "silk.tabs.console": "Konzole",

  // ── SilkPanel — timeline ──────────────────────────────────────────────────
  "silk.timeline.noReport": "Žádná data reportu",
  "silk.timeline.noSteps": "Žádné testovací kroky",

  // ── SilkPanel — a11y ──────────────────────────────────────────────────────
  "silk.a11y.noViolations": "Žádná porušení přístupnosti",
  "silk.a11y.affectedElements": "{n} zasažený prvek/prvků",

  // ── SilkPanel — network ───────────────────────────────────────────────────
  "silk.network.noEntries.noReport": "Žádné síťové záznamy v reportu",
  "silk.network.noEntries.inTrace": "Síťový log je dostupný v Playwright trace",
  "silk.network.downloadTrace": "Stáhnout trace",
  "silk.network.requestCount": "{n} požadavek/ů",

  // ── SilkPanel — screenshots ───────────────────────────────────────────────
  "silk.screenshots.none.noReport": "Žádné snímky v reportu",
  "silk.screenshots.none.captured": "Snímky pořízené během běhu",

  // ── SilkPanel — console ───────────────────────────────────────────────────
  "silk.console.noOutput": "Žádný výstup konzole",

  // ── SilkPanel — install dialog ────────────────────────────────────────────
  "silk.install.title": "Instalace Playwright Chromium",
  "silk.install.log.start": "Spouštím stahování (~150 MB)…",
  "silk.install.chromiumReady": "Chromium je připraven.",
  "silk.install.error": "Chyba: {msg}",
  "silk.install.close": "Zavřít",
  "silk.install.cancel": "Zrušit",

  // ── SilkPanel — record dialog ─────────────────────────────────────────────
  "silk.record.title": "Nahrát nový spec",
  "silk.record.framework.label": "Framework",
  "silk.record.framework.loading": "Načítám…",
  "silk.record.framework.transpileNote": "Nahráno přes Playwright a převedeno do {label}.",
  "silk.record.framework.noRecord": "Nahrávání zatím není podporováno pro {label} — použij Nový test.",
  "silk.record.targetUrl.label": "Cílová URL",
  "silk.record.cancel": "Zrušit",
  "silk.record.startRecording": "Spustit nahrávání",
  "silk.record.inProgress": "Playwright codegen je otevřen v okně prohlížeče. Interaguj s aplikací, pak klikni na Zastavit nahrávání pro zachycení vygenerovaného specu.",
  "silk.record.recording": "Nahrávám…",
  "silk.record.stopRecording": "Zastavit nahrávání",
  "silk.record.captured": "Spec úspěšně zachycen. Spustit hned uloží a okamžitě spustí, nebo Ponechat uloží pro pozdější použití.",
  "silk.record.discard": "Zahodit",
  "silk.record.keep": "Ponechat",
  "silk.record.runNow": "Spustit hned",

  // ── NewTestDialog ─────────────────────────────────────────────────────────
  "newTest.title": "Nový test (ruční tvorba)",
  "newTest.close.aria": "Zavřít",
  "newTest.framework.label": "Framework",
  "newTest.framework.loading": "Načítám…",
  "newTest.framework.loadError": "Nelze načíst seznam frameworků",
  "newTest.filename.label": "Název souboru",
  "newTest.filename.placeholder": "my_test.spec.ts",
  "newTest.workspaceDir.label": "Workspace adresář (volitelné)",
  "newTest.workspaceDir.placeholder": "/cesta/k/projektu",
  "newTest.code.label": "Kód testu",
  "newTest.code.resetTemplate": "Obnovit template",
  "newTest.saved.prefix": "Uloženo: ",
  "newTest.close": "Zavřít",
  "newTest.save": "Uložit",
  "newTest.saving": "Ukládám…",
  "newTest.fallbackTemplate": "// Framework templates not available — write your test manually",

  // ── MobilePanel ───────────────────────────────────────────────────────────
  "mobile.title": "Mobilní zařízení",
  "mobile.refresh": "Obnovit",
  "mobile.refresh.title": "Obnovit seznam zařízení",
  "mobile.tooling.title": "Nástroje",
  "mobile.tooling.loading": "Načítám…",
  "mobile.tooling.empty": "Žádné nástroje nenalezeny",
  "mobile.tooling.notFound": "nenalezeno",
  "mobile.tooling.dot.available": "Dostupný",
  "mobile.tooling.dot.unavailable": "Nedostupný",
  "mobile.devices.title": "Zařízení",
  "mobile.devices.loading": "Načítám zařízení…",
  "mobile.devices.empty.title": "Žádná zařízení",
  "mobile.devices.empty.description": "Připoj zařízení nebo spusť simulátor / emulátor",
  "mobile.devices.action.boot": "Boot",
  "mobile.devices.action.start": "Start",
  "mobile.appium.title": "Appium server",
  "mobile.appium.loading": "Načítám stav…",
  "mobile.appium.running": "Běží — port {port}",
  "mobile.appium.stopped": "Zastaveno",
  "mobile.appium.start": "Spustit",
  "mobile.appium.stop": "Zastavit",

  // ── HubOverviewPanel ──────────────────────────────────────────────────────
  "hub.title": "Přehled Hubu",
  "hub.notConfigured.title": "Hub není nakonfigurován",
  "hub.notConfigured.description": "Připoj se k Theridion Hubu pro zobrazení trendů běhů, incidentů a stavů quality gates bez opuštění Studia.",
  "hub.notConfigured.openSettings": "Otevřít nastavení",
  "hub.refresh.title": "Obnovit (Ctrl+R)",
  "hub.category.runs": "Běhy",
  "hub.category.incidents": "Incidenty",
  "hub.category.gates": "Quality Gates",
  "hub.kpi.avgPassRate": "Průměrná úspěšnost",
  "hub.kpi.openIncidents": "Otevřené incidenty",
  "hub.kpi.gatesFailing": "Selhávající brány",
  "hub.runs.col.collection": "Kolekce",
  "hub.runs.col.passRate": "Úspěšnost",
  "hub.runs.col.duration": "Trvání",
  "hub.runs.col.started": "Spuštěno",
  "hub.runs.empty": "Zatím žádné záznamy běhů",
  "hub.runs.clickToOpen.title": "Kliknutím otevřeš kolekci",
  "hub.runs.openInHub": "Otevřít v Hubu",
  "hub.incidents.empty": "Žádné incidenty",
  "hub.incidents.allClear": "Vše v pořádku.",
  "hub.incidents.detail.title": "Incident",
  "hub.incidents.detail.severity": "Závažnost",
  "hub.incidents.detail.status": "Stav",
  "hub.incidents.detail.collection": "Kolekce",
  "hub.incidents.detail.opened": "Otevřen",
  "hub.incidents.detail.close": "Zavřít",
  "hub.incidents.detail.openInHub": "Otevřít v Hubu",
  "hub.gates.empty": "Žádné quality gates nejsou definovány",
  "hub.gates.threshold": "Práh",
  "hub.gates.current": "Aktuální",

  // ── SettingsModal — navigation ────────────────────────────────────────────
  "settings.title": "Nastavení",
  "settings.tab.general": "Obecné",
  "settings.tab.ai": "AI",
  "settings.tab.editor": "Editor",
  "settings.tab.proxy": "Proxy",
  "settings.tab.hub": "Hub",
  "settings.tab.publish": "Publikování",
  "settings.tab.shortcuts": "Klávesové zkratky",
  "settings.tab.about": "O aplikaci",

  // ── SettingsModal — footer ────────────────────────────────────────────────
  "settings.cancel": "Zrušit",
  "settings.save": "Uložit",
  "settings.saved": "Uloženo",

  // ── Settings — general ────────────────────────────────────────────────────
  "settings.general.theme": "Motiv",
  "settings.general.requestDefaults": "Výchozí nastavení požadavků",
  "settings.general.timeout": "Timeout (sekundy)",
  "settings.general.followRedirects": "Sledovat přesměrování",
  "settings.general.http2": "Povolit HTTP/2",
  "settings.general.globalVars": "Globální proměnné",
  "settings.general.data": "Data",
  "settings.general.dataPath": "Data jsou uložena lokálně v",

  // ── Settings — global vars ────────────────────────────────────────────────
  "settings.globalVars.description": "Proměnné dostupné ve všech požadavcích, nejnižší priorita v řetězci.",
  "settings.globalVars.col.enabled": "Zap",
  "settings.globalVars.col.name": "Název",
  "settings.globalVars.col.value": "Hodnota",
  "settings.globalVars.name.placeholder": "název",
  "settings.globalVars.value.placeholder": "hodnota",
  "settings.globalVars.remove.title": "Odebrat",
  "settings.globalVars.add": "Přidat proměnnou",
  "settings.globalVars.saveGlobals": "Uložit globální proměnné",
  "settings.globalVars.saved": "Uloženo",
  "settings.globalVars.loading": "Načítám...",

  // ── Settings — AI ─────────────────────────────────────────────────────────
  "settings.ai.provider": "Poskytovatel",
  "settings.ai.ollamaUrl": "Ollama Base URL",
  "settings.ai.ping": "Ping",
  "settings.ai.model": "Model",
  "settings.ai.modelRefresh": "Obnovit",
  "settings.ai.localNote": "Ollama běží lokálně — tvá data nikdy neopustí tvůj počítač. Cloudoví poskytovatelé odesílají data požadavků a odpovědí na externí servery.",
  "settings.ai.connected": "Připojeno (v{version})",

  // ── Settings — Editor ─────────────────────────────────────────────────────
  "settings.editor.fontSize": "Velikost písma",
  "settings.editor.options": "Možnosti",
  "settings.editor.wordWrap": "Zalamování řádků",
  "settings.editor.minimap": "Zobrazit minimapu",
  "settings.editor.lineNumbers": "Zobrazit čísla řádků",

  // ── Settings — Proxy ──────────────────────────────────────────────────────
  "settings.proxy.title": "HTTP Proxy",
  "settings.proxy.description": "Nastav upstream proxy pro všechny odchozí požadavky.",
  "settings.proxy.url.label": "Proxy URL (volitelné)",
  "settings.proxy.url.placeholder": "http://proxy.corp:8080",
  "settings.proxy.bypassLocalhost": "Obejít proxy pro localhost",
  "settings.proxy.ssl": "SSL / TLS",
  "settings.proxy.sslVerify": "Ověřovat SSL certifikáty",
  "settings.proxy.caBundle.label": "CA Bundle (volitelné)",
  "settings.proxy.caBundle.placeholder": "/cesta/k/ca-bundle.crt",

  // ── Settings — Hub ────────────────────────────────────────────────────────
  "settings.hub.section": "Theridion Hub",
  "settings.hub.description": "Připoj se k běžící instanci Theridion Hub pro zobrazení trendů, incidentů a quality gate stavů přímo ve Studiu.",
  "settings.hub.url.label": "Hub URL",
  "settings.hub.url.placeholder": "https://hub.theridion.dev",
  "settings.hub.token.label": "Ingest Token",
  "settings.hub.testConnection": "Otestovat připojení",
  "settings.hub.testing": "Testuji…",
  "settings.hub.connected": "Připojeno (v{version})",
  "settings.hub.tokenNote": "Hub token je uložen lokálně v prohlížeči. Nikdy není odesílán na jiný server než výše uvedenou Hub URL.",

  // ── Settings — Publish ────────────────────────────────────────────────────
  "settings.publish.section": "Publikování výsledků",
  "settings.publish.description": "Po každém spuštění testu jsou výsledky automaticky odesílány na Weave (nebo Hub). Zkopírujte Ingest URL a token z nastavení Weave a vložte je sem.",
  "settings.publish.enable": "Povolit publikování výsledků",
  "settings.publish.weave.section": "Weave Ingest",
  "settings.publish.weaveUrl.label": "Ingest URL",
  "settings.publish.weaveUrl.placeholder": "https://weave.example.com/api/runs/ingest",
  "settings.publish.weaveToken.label": "Token",
  "settings.publish.weaveToken.placeholder.set": "Vložte token z Weave Settings",
  "settings.publish.weaveToken.placeholder.empty": "Vložte token z Weave Settings",
  "settings.publish.weaveToken.kept": "Token je uložen. Ponechte prázdné pro zachování stávajícího.",
  "settings.publish.hub.section": "Hub Ingest (volitelné)",
  "settings.publish.hubUrl.label": "Hub URL",
  "settings.publish.hubUrl.placeholder": "https://hub.example.com/api/ingest",
  "settings.publish.hubToken.label": "Token",
  "settings.publish.hubToken.placeholder.set": "Vložte Hub token (volitelné)",
  "settings.publish.hubToken.placeholder.empty": "Vložte Hub token (volitelné)",
  "settings.publish.hubToken.kept": "Token je uložen. Ponechte prázdné pro zachování stávajícího.",
  "settings.publish.save": "Uložit",
  "settings.publish.saving": "Ukládám…",
  "settings.publish.saved": "Uloženo",
  "settings.publish.loading": "Načítání...",
  "settings.publish.storageNote": "Tokeny jsou ukládány lokálně v zašifrovaném úložišti sidecaru. Nikdy nejsou logovány ani odesílány jinam než na nakonfigurované URL.",

  // ── Settings — Shortcuts ──────────────────────────────────────────────────
  "settings.shortcuts.send": "Odeslat požadavek",
  "settings.shortcuts.save": "Uložit požadavek",
  "settings.shortcuts.saveAs": "Uložit jako...",
  "settings.shortcuts.newTab": "Nová záložka",
  "settings.shortcuts.closeTab": "Zavřít záložku",
  "settings.shortcuts.commandPalette": "Paleta příkazů",
  "settings.shortcuts.settings": "Nastavení",
  "settings.shortcuts.close": "Zavřít modal / zrušit",

  // ── Settings — About ──────────────────────────────────────────────────────
  "settings.about.tagline": "Moderní platforma pro testování API",
  "settings.about.description": "Bruno UI/file-based ops + SoapUI WS-* síla + Playwright-style test runner.",
  "settings.about.protocols": "Protokoly: REST, GraphQL, WebSocket, SOAP, Kafka, gRPC",
  "settings.about.stack": "Stack: Tauri 2 + React 18 + Python FastAPI",
  "settings.about.named": "Pojmenováno po rodu Theridion pavouků — metafora pro zamotané API závislosti.",

  // ── Language switcher ─────────────────────────────────────────────────────
  "lang.en": "EN",
  "lang.cs": "CS",
  "lang.switcher.aria": "Přepnout jazyk",
};
