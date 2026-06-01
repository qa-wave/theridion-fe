import type { Messages } from "./types";

export const en: Messages = {
  // ── App / footer ──────────────────────────────────────────────────────────
  "app.version": "Theridion FE v0.0.1",

  // ── ActivityBar ───────────────────────────────────────────────────────────
  "activityBar.aria": "Module switcher",
  "activityBar.silk": "Silk (Frontend tests)",
  "activityBar.monitors": "Test monitors",
  "activityBar.hubOverview": "Hub Overview",
  "activityBar.mobile": "Mobile devices",

  // ── EmptyState — monitors ─────────────────────────────────────────────────
  "monitors.title": "Test monitors",
  "monitors.description": "Scheduled Playwright run monitoring (synthetic FE checks). Create a monitor in the Silk panel via the 'Schedule run' button.",

  // ── SilkPanel — toolbar ───────────────────────────────────────────────────
  "silk.toolbar.record": "Record",
  "silk.toolbar.record.title": "Record new spec via Playwright codegen",
  "silk.toolbar.record.titleNoBrowsers": "Install browsers first",
  "silk.toolbar.newTest": "New test",
  "silk.toolbar.newTest.title": "Create a new test manually in the editor",
  "silk.toolbar.installBrowsers": "Install browsers",
  "silk.toolbar.refreshBrowserCheck": "Refresh browser check",
  "silk.toolbar.refreshHistory": "Refresh run history",

  // ── SilkPanel — history sidebar ───────────────────────────────────────────
  "silk.history.title": "History",
  "silk.history.newRun.title": "New run",
  "silk.history.empty.title": "No runs yet",
  "silk.history.empty.description": "Run a spec to see results here",
  "silk.history.previousRuns": "Previous runs",

  // ── SilkPanel — run form ──────────────────────────────────────────────────
  "silk.runForm.title": "Run spec",
  "silk.runForm.specPath.label": "Spec file path",
  "silk.runForm.specPath.placeholder": "/path/to/my.spec.ts",
  "silk.runForm.workspaceDir.label": "Workspace dir (optional)",
  "silk.runForm.workspaceDir.placeholder": "/path/to/project",
  "silk.runForm.browsers.label": "Browsers",
  "silk.runForm.run": "Run",
  "silk.runForm.running": "Running…",

  // ── SilkPanel — stats ─────────────────────────────────────────────────────
  "silk.stats.passed": "Passed",
  "silk.stats.failed": "Failed",
  "silk.stats.errors": "Errors",
  "silk.stats.duration": "Duration",
  "silk.stats.stderr": "stderr (last 20 lines)",
  "silk.stats.selectRun": "Select a run from the history to view results",

  // ── SilkPanel — tabs ──────────────────────────────────────────────────────
  "silk.tabs.timeline": "Timeline",
  "silk.tabs.network": "Network",
  "silk.tabs.screenshots": "Screenshots",
  "silk.tabs.console": "Console",

  // ── SilkPanel — timeline ──────────────────────────────────────────────────
  "silk.timeline.noReport": "No report data",
  "silk.timeline.noSteps": "No test steps found",

  // ── SilkPanel — a11y ──────────────────────────────────────────────────────
  "silk.a11y.noViolations": "No accessibility violations",
  "silk.a11y.affectedElements": "{n} affected element(s)",

  // ── SilkPanel — network ───────────────────────────────────────────────────
  "silk.network.noEntries.noReport": "No network entries in report",
  "silk.network.noEntries.inTrace": "Network log available in Playwright trace",
  "silk.network.downloadTrace": "Download trace",
  "silk.network.requestCount": "{n} request(s)",

  // ── SilkPanel — screenshots ───────────────────────────────────────────────
  "silk.screenshots.none.noReport": "No screenshots in report",
  "silk.screenshots.none.captured": "Screenshots captured during run",

  // ── SilkPanel — console ───────────────────────────────────────────────────
  "silk.console.noOutput": "No console output",

  // ── SilkPanel — install dialog ────────────────────────────────────────────
  "silk.install.title": "Install Playwright Chromium",
  "silk.install.log.start": "Starting download (~150 MB)…",
  "silk.install.chromiumReady": "Chromium ready.",
  "silk.install.error": "Error: {msg}",
  "silk.install.close": "Close",
  "silk.install.cancel": "Cancel",

  // ── SilkPanel — record dialog ─────────────────────────────────────────────
  "silk.record.title": "Record new spec",
  "silk.record.framework.label": "Framework",
  "silk.record.framework.loading": "Loading…",
  "silk.record.framework.transpileNote": "Recorded via Playwright and converted to {label}.",
  "silk.record.framework.noRecord": "Recording is not yet supported for {label} — use New test.",
  "silk.record.targetUrl.label": "Target URL",
  "silk.record.cancel": "Cancel",
  "silk.record.startRecording": "Start recording",
  "silk.record.inProgress": "Playwright codegen is open in a browser window. Interact with your app, then click Stop recording to capture the generated spec.",
  "silk.record.recording": "Recording…",
  "silk.record.stopRecording": "Stop recording",
  "silk.record.captured": "Spec captured successfully. Run Now saves it and immediately executes it, or Keep saves it for later.",
  "silk.record.discard": "Discard",
  "silk.record.keep": "Keep",
  "silk.record.runNow": "Run Now",

  // ── NewTestDialog ─────────────────────────────────────────────────────────
  "newTest.title": "New test (manual authoring)",
  "newTest.close.aria": "Close",
  "newTest.framework.label": "Framework",
  "newTest.framework.loading": "Loading…",
  "newTest.framework.loadError": "Could not load framework list",
  "newTest.filename.label": "Filename",
  "newTest.filename.placeholder": "my_test.spec.ts",
  "newTest.workspaceDir.label": "Workspace dir (optional)",
  "newTest.workspaceDir.placeholder": "/path/to/project",
  "newTest.code.label": "Test code",
  "newTest.code.resetTemplate": "Reset template",
  "newTest.saved.prefix": "Saved: ",
  "newTest.close": "Close",
  "newTest.save": "Save",
  "newTest.saving": "Saving…",
  "newTest.fallbackTemplate": "// Framework templates not available — write your test manually",

  // ── MobilePanel ───────────────────────────────────────────────────────────
  "mobile.title": "Mobile devices",
  "mobile.refresh": "Refresh",
  "mobile.refresh.title": "Refresh device list",
  "mobile.tooling.title": "Tools",
  "mobile.tooling.loading": "Loading…",
  "mobile.tooling.empty": "No tools found",
  "mobile.tooling.notFound": "not found",
  "mobile.tooling.dot.available": "Available",
  "mobile.tooling.dot.unavailable": "Unavailable",
  "mobile.devices.title": "Devices",
  "mobile.devices.loading": "Loading devices…",
  "mobile.devices.empty.title": "No devices",
  "mobile.devices.empty.description": "Connect a device or start a simulator / emulator",
  "mobile.devices.action.boot": "Boot",
  "mobile.devices.action.start": "Start",
  "mobile.appium.title": "Appium server",
  "mobile.appium.loading": "Loading status…",
  "mobile.appium.running": "Running — port {port}",
  "mobile.appium.stopped": "Stopped",
  "mobile.appium.start": "Start",
  "mobile.appium.stop": "Stop",

  // ── HubOverviewPanel ──────────────────────────────────────────────────────
  "hub.title": "Hub Overview",
  "hub.notConfigured.title": "Hub not configured",
  "hub.notConfigured.description": "Connect to a Theridion Hub to see run trends, incidents, and quality gate statuses without leaving Studio.",
  "hub.notConfigured.openSettings": "Open Settings",
  "hub.refresh.title": "Refresh (Ctrl+R)",
  "hub.category.runs": "Runs",
  "hub.category.incidents": "Incidents",
  "hub.category.gates": "Quality Gates",
  "hub.kpi.avgPassRate": "Avg pass rate",
  "hub.kpi.openIncidents": "Open incidents",
  "hub.kpi.gatesFailing": "Gates failing",
  "hub.runs.col.collection": "Collection",
  "hub.runs.col.passRate": "Pass rate",
  "hub.runs.col.duration": "Duration",
  "hub.runs.col.started": "Started",
  "hub.runs.empty": "No runs recorded yet",
  "hub.runs.clickToOpen.title": "Click to open collection",
  "hub.runs.openInHub": "Open in Hub",
  "hub.incidents.empty": "No incidents",
  "hub.incidents.allClear": "All clear.",
  "hub.incidents.detail.title": "Incident",
  "hub.incidents.detail.severity": "Severity",
  "hub.incidents.detail.status": "Status",
  "hub.incidents.detail.collection": "Collection",
  "hub.incidents.detail.opened": "Opened",
  "hub.incidents.detail.close": "Close",
  "hub.incidents.detail.openInHub": "Open in Hub",
  "hub.gates.empty": "No quality gates defined",
  "hub.gates.threshold": "Threshold",
  "hub.gates.current": "Current",

  // ── SettingsModal — navigation ────────────────────────────────────────────
  "settings.title": "Settings",
  "settings.tab.general": "General",
  "settings.tab.ai": "AI",
  "settings.tab.editor": "Editor",
  "settings.tab.proxy": "Proxy",
  "settings.tab.hub": "Hub",
  "settings.tab.publish": "Publishing",
  "settings.tab.shortcuts": "Shortcuts",
  "settings.tab.about": "About",

  // ── SettingsModal — footer ────────────────────────────────────────────────
  "settings.cancel": "Cancel",
  "settings.save": "Save",
  "settings.saved": "Saved",

  // ── Settings — general ────────────────────────────────────────────────────
  "settings.general.theme": "Theme",
  "settings.general.requestDefaults": "Request Defaults",
  "settings.general.timeout": "Timeout (seconds)",
  "settings.general.followRedirects": "Follow redirects",
  "settings.general.http2": "Enable HTTP/2",
  "settings.general.globalVars": "Global Variables",
  "settings.general.data": "Data",
  "settings.general.dataPath": "Data is stored locally at",

  // ── Settings — global vars ────────────────────────────────────────────────
  "settings.globalVars.description": "Variables available in all requests, lowest priority in the resolution chain.",
  "settings.globalVars.col.enabled": "On",
  "settings.globalVars.col.name": "Name",
  "settings.globalVars.col.value": "Value",
  "settings.globalVars.name.placeholder": "name",
  "settings.globalVars.value.placeholder": "value",
  "settings.globalVars.remove.title": "Remove",
  "settings.globalVars.add": "Add variable",
  "settings.globalVars.saveGlobals": "Save globals",
  "settings.globalVars.saved": "Saved",
  "settings.globalVars.loading": "Loading...",

  // ── Settings — AI ─────────────────────────────────────────────────────────
  "settings.ai.provider": "Provider",
  "settings.ai.ollamaUrl": "Ollama Base URL",
  "settings.ai.ping": "Ping",
  "settings.ai.model": "Model",
  "settings.ai.modelRefresh": "Refresh",
  "settings.ai.localNote": "Ollama runs locally — your data never leaves your machine. Cloud providers send request/response data to external servers.",
  "settings.ai.connected": "Connected (v{version})",

  // ── Settings — Editor ─────────────────────────────────────────────────────
  "settings.editor.fontSize": "Font Size",
  "settings.editor.options": "Options",
  "settings.editor.wordWrap": "Word wrap",
  "settings.editor.minimap": "Show minimap",
  "settings.editor.lineNumbers": "Show line numbers",

  // ── Settings — Proxy ──────────────────────────────────────────────────────
  "settings.proxy.title": "HTTP Proxy",
  "settings.proxy.description": "Configure an upstream proxy for all outgoing requests.",
  "settings.proxy.url.label": "Proxy URL (optional)",
  "settings.proxy.url.placeholder": "http://proxy.corp:8080",
  "settings.proxy.bypassLocalhost": "Bypass proxy for localhost",
  "settings.proxy.ssl": "SSL / TLS",
  "settings.proxy.sslVerify": "Verify SSL certificates",
  "settings.proxy.caBundle.label": "CA Bundle (optional)",
  "settings.proxy.caBundle.placeholder": "/path/to/ca-bundle.crt",

  // ── Settings — Hub ────────────────────────────────────────────────────────
  "settings.hub.section": "Theridion Hub",
  "settings.hub.description": "Connect to a running Theridion Hub instance to see run trends, incidents and quality gate statuses in Studio.",
  "settings.hub.url.label": "Hub URL",
  "settings.hub.url.placeholder": "https://hub.theridion.dev",
  "settings.hub.token.label": "Ingest Token",
  "settings.hub.testConnection": "Test connection",
  "settings.hub.testing": "Testing…",
  "settings.hub.connected": "Connected (v{version})",
  "settings.hub.tokenNote": "The Hub token is stored locally in your browser. It is never sent to any server other than the Hub URL above.",

  // ── Settings — Publish ────────────────────────────────────────────────────
  "settings.publish.section": "Publish results",
  "settings.publish.description": "After each test run, results are automatically sent to Weave (or Hub). Copy the Ingest URL and token from the Weave settings and paste them here.",
  "settings.publish.enable": "Enable result publishing",
  "settings.publish.weave.section": "Weave Ingest",
  "settings.publish.weaveUrl.label": "Ingest URL",
  "settings.publish.weaveUrl.placeholder": "https://weave.example.com/api/runs/ingest",
  "settings.publish.weaveToken.label": "Token",
  "settings.publish.weaveToken.placeholder.set": "Paste token from Weave Settings",
  "settings.publish.weaveToken.placeholder.empty": "Paste token from Weave Settings",
  "settings.publish.weaveToken.kept": "Token saved. Leave empty to keep existing.",
  "settings.publish.hub.section": "Hub Ingest (optional)",
  "settings.publish.hubUrl.label": "Hub URL",
  "settings.publish.hubUrl.placeholder": "https://hub.example.com/api/ingest",
  "settings.publish.hubToken.label": "Token",
  "settings.publish.hubToken.placeholder.set": "Paste Hub token (optional)",
  "settings.publish.hubToken.placeholder.empty": "Paste Hub token (optional)",
  "settings.publish.hubToken.kept": "Token saved. Leave empty to keep existing.",
  "settings.publish.save": "Save",
  "settings.publish.saving": "Saving…",
  "settings.publish.saved": "Saved",
  "settings.publish.loading": "Loading...",
  "settings.publish.storageNote": "Tokens are stored locally in the sidecar's encrypted storage. They are never logged or sent anywhere other than the configured URL.",

  // ── Settings — Shortcuts ──────────────────────────────────────────────────
  "settings.shortcuts.send": "Send request",
  "settings.shortcuts.save": "Save request",
  "settings.shortcuts.saveAs": "Save As...",
  "settings.shortcuts.newTab": "New tab",
  "settings.shortcuts.closeTab": "Close tab",
  "settings.shortcuts.commandPalette": "Command palette",
  "settings.shortcuts.settings": "Settings",
  "settings.shortcuts.close": "Close modal / cancel",

  // ── Settings — About ──────────────────────────────────────────────────────
  "settings.about.tagline": "Modern API testing platform",
  "settings.about.description": "Bruno UI/file-based ops + SoapUI WS-* strength + Playwright-style test runner.",
  "settings.about.protocols": "Protocols: REST, GraphQL, WebSocket, SOAP, Kafka, gRPC",
  "settings.about.stack": "Stack: Tauri 2 + React 18 + Python FastAPI",
  "settings.about.named": "Named after the Theridion genus of cobweb spiders — a metaphor for tangled API dependencies.",

  // ── Language switcher ─────────────────────────────────────────────────────
  "lang.en": "EN",
  "lang.cs": "CS",
  "lang.switcher.aria": "Switch language",
};
