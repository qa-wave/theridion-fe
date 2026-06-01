// ─── i18n types ───────────────────────────────────────────────────────────────

export type Locale = "en" | "cs";
export const LOCALE_STORAGE_KEY = "theridion_eyes_locale";
export const DEFAULT_LOCALE: Locale = "en";
export const SUPPORTED_LOCALES: Locale[] = ["en", "cs"];

export interface Messages {
  // ── App / footer ──────────────────────────────────────────────────────────
  "app.version": string;

  // ── ActivityBar ───────────────────────────────────────────────────────────
  "activityBar.aria": string;
  "activityBar.silk": string;
  "activityBar.monitors": string;
  "activityBar.hubOverview": string;
  "activityBar.mobile": string;

  // ── EmptyState — monitors ─────────────────────────────────────────────────
  "monitors.title": string;
  "monitors.description": string;

  // ── SilkPanel — toolbar ───────────────────────────────────────────────────
  "silk.toolbar.record": string;
  "silk.toolbar.record.title": string;
  "silk.toolbar.record.titleNoBrowsers": string;
  "silk.toolbar.newTest": string;
  "silk.toolbar.newTest.title": string;
  "silk.toolbar.installBrowsers": string;
  "silk.toolbar.refreshBrowserCheck": string;
  "silk.toolbar.refreshHistory": string;

  // ── SilkPanel — history sidebar ───────────────────────────────────────────
  "silk.history.title": string;
  "silk.history.newRun.title": string;
  "silk.history.empty.title": string;
  "silk.history.empty.description": string;
  "silk.history.previousRuns": string;

  // ── SilkPanel — run form ──────────────────────────────────────────────────
  "silk.runForm.title": string;
  "silk.runForm.specPath.label": string;
  "silk.runForm.specPath.placeholder": string;
  "silk.runForm.workspaceDir.label": string;
  "silk.runForm.workspaceDir.placeholder": string;
  "silk.runForm.browsers.label": string;
  "silk.runForm.run": string;
  "silk.runForm.running": string;

  // ── SilkPanel — stats ─────────────────────────────────────────────────────
  "silk.stats.passed": string;
  "silk.stats.failed": string;
  "silk.stats.errors": string;
  "silk.stats.duration": string;
  "silk.stats.stderr": string;
  "silk.stats.selectRun": string;

  // ── SilkPanel — tabs ──────────────────────────────────────────────────────
  "silk.tabs.timeline": string;
  "silk.tabs.network": string;
  "silk.tabs.screenshots": string;
  "silk.tabs.console": string;

  // ── SilkPanel — timeline ──────────────────────────────────────────────────
  "silk.timeline.noReport": string;
  "silk.timeline.noSteps": string;

  // ── SilkPanel — a11y ──────────────────────────────────────────────────────
  "silk.a11y.noViolations": string;
  "silk.a11y.affectedElements": string;

  // ── SilkPanel — network ───────────────────────────────────────────────────
  "silk.network.noEntries.noReport": string;
  "silk.network.noEntries.inTrace": string;
  "silk.network.downloadTrace": string;
  "silk.network.requestCount": string;

  // ── SilkPanel — screenshots ───────────────────────────────────────────────
  "silk.screenshots.none.noReport": string;
  "silk.screenshots.none.captured": string;

  // ── SilkPanel — console ───────────────────────────────────────────────────
  "silk.console.noOutput": string;

  // ── SilkPanel — install dialog ────────────────────────────────────────────
  "silk.install.title": string;
  "silk.install.log.start": string;
  "silk.install.chromiumReady": string;
  "silk.install.error": string;
  "silk.install.close": string;
  "silk.install.cancel": string;

  // ── SilkPanel — record dialog ─────────────────────────────────────────────
  "silk.record.title": string;
  "silk.record.framework.label": string;
  "silk.record.framework.loading": string;
  "silk.record.framework.transpileNote": string;
  "silk.record.framework.noRecord": string;
  "silk.record.targetUrl.label": string;
  "silk.record.cancel": string;
  "silk.record.startRecording": string;
  "silk.record.inProgress": string;
  "silk.record.recording": string;
  "silk.record.stopRecording": string;
  "silk.record.captured": string;
  "silk.record.discard": string;
  "silk.record.keep": string;
  "silk.record.runNow": string;

  // ── NewTestDialog ─────────────────────────────────────────────────────────
  "newTest.title": string;
  "newTest.close.aria": string;
  "newTest.framework.label": string;
  "newTest.framework.loading": string;
  "newTest.framework.loadError": string;
  "newTest.filename.label": string;
  "newTest.filename.placeholder": string;
  "newTest.workspaceDir.label": string;
  "newTest.workspaceDir.placeholder": string;
  "newTest.code.label": string;
  "newTest.code.resetTemplate": string;
  "newTest.saved.prefix": string;
  "newTest.close": string;
  "newTest.save": string;
  "newTest.saving": string;
  "newTest.fallbackTemplate": string;

  // ── MobilePanel ───────────────────────────────────────────────────────────
  "mobile.title": string;
  "mobile.refresh": string;
  "mobile.refresh.title": string;
  "mobile.tooling.title": string;
  "mobile.tooling.loading": string;
  "mobile.tooling.empty": string;
  "mobile.tooling.notFound": string;
  "mobile.tooling.dot.available": string;
  "mobile.tooling.dot.unavailable": string;
  "mobile.devices.title": string;
  "mobile.devices.loading": string;
  "mobile.devices.empty.title": string;
  "mobile.devices.empty.description": string;
  "mobile.devices.action.boot": string;
  "mobile.devices.action.start": string;
  "mobile.appium.title": string;
  "mobile.appium.loading": string;
  "mobile.appium.running": string;
  "mobile.appium.stopped": string;
  "mobile.appium.start": string;
  "mobile.appium.stop": string;

  // ── HubOverviewPanel ──────────────────────────────────────────────────────
  "hub.title": string;
  "hub.notConfigured.title": string;
  "hub.notConfigured.description": string;
  "hub.notConfigured.openSettings": string;
  "hub.refresh.title": string;
  "hub.category.runs": string;
  "hub.category.incidents": string;
  "hub.category.gates": string;
  "hub.kpi.avgPassRate": string;
  "hub.kpi.openIncidents": string;
  "hub.kpi.gatesFailing": string;
  "hub.runs.col.collection": string;
  "hub.runs.col.passRate": string;
  "hub.runs.col.duration": string;
  "hub.runs.col.started": string;
  "hub.runs.empty": string;
  "hub.runs.clickToOpen.title": string;
  "hub.runs.openInHub": string;
  "hub.incidents.empty": string;
  "hub.incidents.allClear": string;
  "hub.incidents.detail.title": string;
  "hub.incidents.detail.severity": string;
  "hub.incidents.detail.status": string;
  "hub.incidents.detail.collection": string;
  "hub.incidents.detail.opened": string;
  "hub.incidents.detail.close": string;
  "hub.incidents.detail.openInHub": string;
  "hub.gates.empty": string;
  "hub.gates.threshold": string;
  "hub.gates.current": string;

  // ── SettingsModal — navigation ────────────────────────────────────────────
  "settings.title": string;
  "settings.tab.general": string;
  "settings.tab.ai": string;
  "settings.tab.editor": string;
  "settings.tab.proxy": string;
  "settings.tab.hub": string;
  "settings.tab.publish": string;
  "settings.tab.shortcuts": string;
  "settings.tab.about": string;

  // ── SettingsModal — footer ────────────────────────────────────────────────
  "settings.cancel": string;
  "settings.save": string;
  "settings.saved": string;

  // ── Settings — general ────────────────────────────────────────────────────
  "settings.general.theme": string;
  "settings.general.requestDefaults": string;
  "settings.general.timeout": string;
  "settings.general.followRedirects": string;
  "settings.general.http2": string;
  "settings.general.globalVars": string;
  "settings.general.data": string;
  "settings.general.dataPath": string;

  // ── Settings — global vars ────────────────────────────────────────────────
  "settings.globalVars.description": string;
  "settings.globalVars.col.enabled": string;
  "settings.globalVars.col.name": string;
  "settings.globalVars.col.value": string;
  "settings.globalVars.name.placeholder": string;
  "settings.globalVars.value.placeholder": string;
  "settings.globalVars.remove.title": string;
  "settings.globalVars.add": string;
  "settings.globalVars.saveGlobals": string;
  "settings.globalVars.saved": string;
  "settings.globalVars.loading": string;

  // ── Settings — AI ─────────────────────────────────────────────────────────
  "settings.ai.provider": string;
  "settings.ai.ollamaUrl": string;
  "settings.ai.ping": string;
  "settings.ai.model": string;
  "settings.ai.modelRefresh": string;
  "settings.ai.localNote": string;
  "settings.ai.connected": string;

  // ── Settings — Editor ─────────────────────────────────────────────────────
  "settings.editor.fontSize": string;
  "settings.editor.options": string;
  "settings.editor.wordWrap": string;
  "settings.editor.minimap": string;
  "settings.editor.lineNumbers": string;

  // ── Settings — Proxy ──────────────────────────────────────────────────────
  "settings.proxy.title": string;
  "settings.proxy.description": string;
  "settings.proxy.url.label": string;
  "settings.proxy.url.placeholder": string;
  "settings.proxy.bypassLocalhost": string;
  "settings.proxy.ssl": string;
  "settings.proxy.sslVerify": string;
  "settings.proxy.caBundle.label": string;
  "settings.proxy.caBundle.placeholder": string;

  // ── Settings — Hub ────────────────────────────────────────────────────────
  "settings.hub.section": string;
  "settings.hub.description": string;
  "settings.hub.url.label": string;
  "settings.hub.url.placeholder": string;
  "settings.hub.token.label": string;
  "settings.hub.testConnection": string;
  "settings.hub.testing": string;
  "settings.hub.connected": string;
  "settings.hub.tokenNote": string;

  // ── Settings — Publish ────────────────────────────────────────────────────
  "settings.publish.section": string;
  "settings.publish.description": string;
  "settings.publish.enable": string;
  "settings.publish.weave.section": string;
  "settings.publish.weaveUrl.label": string;
  "settings.publish.weaveUrl.placeholder": string;
  "settings.publish.weaveToken.label": string;
  "settings.publish.weaveToken.placeholder.set": string;
  "settings.publish.weaveToken.placeholder.empty": string;
  "settings.publish.weaveToken.kept": string;
  "settings.publish.hub.section": string;
  "settings.publish.hubUrl.label": string;
  "settings.publish.hubUrl.placeholder": string;
  "settings.publish.hubToken.label": string;
  "settings.publish.hubToken.placeholder.set": string;
  "settings.publish.hubToken.placeholder.empty": string;
  "settings.publish.hubToken.kept": string;
  "settings.publish.save": string;
  "settings.publish.saving": string;
  "settings.publish.saved": string;
  "settings.publish.loading": string;
  "settings.publish.storageNote": string;

  // ── Settings — Shortcuts ──────────────────────────────────────────────────
  "settings.shortcuts.send": string;
  "settings.shortcuts.save": string;
  "settings.shortcuts.saveAs": string;
  "settings.shortcuts.newTab": string;
  "settings.shortcuts.closeTab": string;
  "settings.shortcuts.commandPalette": string;
  "settings.shortcuts.settings": string;
  "settings.shortcuts.close": string;

  // ── Settings — About ──────────────────────────────────────────────────────
  "settings.about.tagline": string;
  "settings.about.description": string;
  "settings.about.protocols": string;
  "settings.about.stack": string;
  "settings.about.named": string;

  // ── Language switcher ─────────────────────────────────────────────────────
  "lang.en": string;
  "lang.cs": string;
  "lang.switcher.aria": string;
}
