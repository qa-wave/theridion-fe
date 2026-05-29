# Theridion Studio FE — implementační plán 10 zlepšení

> Stav: 2026-05-30. Autor: senior product engineer (pro Tomáše, QA lead).
> Rozsah: `apps/studio-fe` (Vite+React+TS) + `apps/sidecar-fe` (`theridion_sidecar`).
> Pozn.: pre-existing ruff debt v `silk.py` NEŘEŠIT. Cesty ověřené proti repu
> (FE komponenty jsou v `src/components/`, ne `src/modules/silk/`).

## Legenda
- **Priorita**: P0 = blokuje core flow / korektnost; P1 = výrazná hodnota, ne blokující; P2 = polish.
- **Náročnost**: S ≈ ≤0.5 d, M ≈ 1 d, L ≈ 2–3 d.
- **Přínos (4 dimenze)**: 🎨 Grafický | ⚙️ Funkční | 👤 UX | 🙋 Pro uživatele.

## Doporučené pořadí realizace
1. **#1** (async multi-browser) — korektnost backendu, odblokuje paralelní runy.
2. **#5** (sidecar timeout/retry) — odstraní trvalý „connecting…", platí pro celé UI.
3. **#2 + #3** (SSE live recording + použití nahraného specu) — zavírá hlavní Silk flow.

---

## 1. Multi-browser runy běží sériově a blokují event loop

- **Priorita**: P0 — `run_spec` je `sync def` s blokujícím `subprocess.run` ve `for`-loopu; pod ASGI to blokuje event loop a serializuje i jinak nezávislé runy.
- **Náročnost**: M (~1 d).
- **Soubory**: `apps/sidecar-fe/theridion_sidecar/api/silk.py` (`run_spec` ř. 632, `_run_single_browser` ř. 537), vzor `apps/sidecar-fe/theridion_sidecar/api/mobile.py:67 _run`. Testy: `apps/sidecar-fe/tests/test_silk.py`.
- **Implementační detail**:
  1. Zaveď patchovatelný seam `async def _run_browser_proc(cmd, *, timeout_s, env, cwd) -> tuple[int,str,str]` po vzoru `mobile._run` (`asyncio.create_subprocess_exec` + `await proc.communicate()`), s `asyncio.wait_for(..., timeout=timeout_s)` pro timeout.
  2. Přepiš `_run_single_browser` na `async def` — nahraď `subprocess.run` voláním `await _run_browser_proc(...)`; `subprocess.TimeoutExpired` → `asyncio.TimeoutError`.
  3. Přepiš `run_spec` na `async def`. Sestav coroutiny per browser a spusť `results = await asyncio.gather(*[_run_single_browser(...) for b in browsers], return_exceptions=True)`.
  4. Po `gather` zpracuj s `return_exceptions`: pokud položka je `HTTPException(504)` (timeout), re-raise; jinak agreguj jako dnes (ř. 698–708).
  5. Zachovej `total_start_ns`/`total_duration_ms` (ř. 676, 695) — teď měří wall-clock paralelního běhu (správně).
  6. Uprav testy v `test_silk.py`, aby patchovaly nový async seam (ne `subprocess.run`); přidej test že 2 browsery běží konkurentně (mock se sleepem → celková doba < součet).
- **Na co dát pozor**: `PLAYWRIGHT_TRACE_DEST` a `--output` per browser už směřují do oddělených `browser_dir` (ř. 548–568) → bezpečné pro paralelismus, žádná kolize artefaktů. Sjednoť `env_copy` jako per-task kopii. Ruff debt v souboru NEřešit.
- **Přínos**:
  - 🎨 n/a
  - ⚙️ Multi-browser run skutečně paralelní; event loop neblokuje další requesty (health, record stream).
  - 👤 3-browser run trvá ~čas nejpomalejšího místo součtu → výrazně kratší čekání.
  - 🙋 Rychlejší výsledky cross-browser testů; UI zůstává responzivní během runu.
- **Závislosti/rizika**: vyšší souběžná zátěž CPU/RAM (3× Playwright naráz) — případně omezit `asyncio.Semaphore(n)` při >3 browserech. Riziko regrese v parsování JSON reportu → pokryto testy.

---

## 2. RecordDialog otevírá SSE stream, ale nepřipojí se

- **Priorita**: P0 — recording flow je hlavní feature Silk; uživatel teď nevidí žádný live feedback (`esRef` deklarovaný ř. 359, jen cleanup ř. 389–393, nikdy se nepřipojí).
- **Náročnost**: S (~0.5 d).
- **Soubory**: `apps/studio-fe/src/components/SilkPanel.tsx` (`RecordDialog`, `handleStart` ř. 401, `esRef` ř. 359). Endpoint je hotový: `silk.py:1008 /record/stream/{session_id}` (SSE, `text/event-stream`).
- **Implementační detail**:
  1. V `handleStart` po `setSessionId(res.session_id)` otevři stream. EventSource neumí custom hlavičky (token) → použij `getSidecarBaseUrl()` z `lib/sidecar/client.ts` a sestav URL; pokud token vyžadován, raději `fetch` + `ReadableStream` reader (token přes `X-Theridion-Token`), jinak `new EventSource(\`${baseUrl}/silk/record/stream/${id}\`)`.
  2. `es.onmessage = (e) => { if (e.data === "DONE") { es.close(); return; } setLiveLines(prev => [...prev, e.data]); }`.
  3. `es.onerror` → zaloguj do `liveLines` a `es.close()`. Ulož instanci do `esRef.current`.
  4. V `handleStop` (ř. 412) `esRef.current?.close()` už je — ponech.
  5. Auto-scroll log už existuje (ř. 385–387) přes `liveLines`.
- **Na co dát pozor**: pokud běží s tokenem (Tauri build), `EventSource` token neposílá → preferuj `fetch`-based SSE čtečku (sjednoť s `sidecar.call`). Stream emituje `DONE` na konci (silk.py:1026) — neopomenout close, jinak retry loop.
- **Přínos**:
  - 🎨 Živě plnící se mono-log v dialogu (vizuální feedback místo statického hlášení).
  - ⚙️ Propojí už existující, ale mrtvý backend SSE endpoint.
  - 👤 Uživatel vidí, že codegen běží a co zaznamenává v reálném čase.
  - 🙋 Důvěra, že recording funguje; rychlejší diagnostika, když se nic neděje.
- **Závislosti/rizika**: token handling (viz výše). Nízké riziko — endpoint hotový.

---

## 3. Nahraný spec se zahodí

- **Priorita**: P0 — `handleCaptureSpec` (ř. 734) jen ukáže toast „paste code into your spec file"; výstup recordingu se nikam nepropíše. Bez tohoto je recording bezúčelný.
- **Náročnost**: M (~1 d).
- **Soubory**: `apps/studio-fe/src/components/SilkPanel.tsx` (`handleCaptureSpec` ř. 734, `RunForm` ř. 539, run handler kolem ř. 700–732).
- **Implementační detail**:
  1. Rozšiř `handleCaptureSpec(specCode, specPath)` o stav: `setCapturedSpec({ code, path })`.
  2. Pokud `specPath` (silk.py vrací cestu výstupního souboru z `/record/stop`) → nabídni 2 akce v toastu/panelu: **„Spustit hned"** (předvyplní `RunForm.specPath` a zavolá `handleRun(specPath, workspaceDir, ["chromium"])`) a **„Otevřít v editoru"**.
  3. Přidej lehký code-preview blok (read-only `<pre>` s mono fontem + tlačítko „Kopírovat") pro `specCode`, když není `specPath` (inline recording).
  4. „Spustit hned" zavolá existující run flow (handler kolem ř. 700) — nevolat nový endpoint.
  5. „Otevřít v editoru": MVP = kopírovat do schránky + toast; plnohodnotný editor je mimo scope (samostatný ticket).
- **Na co dát pozor**: stav recordingu žije v `RecordDialog`; po `onCapture` se dialog zavírá (ř. 736) — captured spec proto drž v `SilkPanel` parent stavu, ne v dialogu.
- **Přínos**:
  - 🎨 Náhled kódu + akční tlačítka místo mizícího toastu.
  - ⚙️ Uzavře smyčku record → run; spec se reálně použije.
  - 👤 Žádné ruční kopírování cest; „nahraj a hned spusť" na jeden klik.
  - 🙋 Reálná úspora času QA — recording je konečně produktivní.
- **Závislosti/rizika**: ideálně po #2 (SSE) kvůli kompletnímu flow. Závisí na tom, že `/record/stop` vrací `spec_path` (ověřeno, silk.py:1057).

---

## 4. Network & Screenshots taby = prázdné placeholdery

- **Priorita**: P1 — funkční mezera; trace download existuje, ale strukturovaná data ne. Hodnotné, ne blokující.
- **Náročnost**: M (~1 d).
- **Soubory**: `apps/studio-fe/src/components/SilkPanel.tsx` (taby ř. 1083–1105), parsování z `selectedRun.per_browser_results[browser].json_report`. Případně backend `silk.py` `_run_single_browser` (ř. 596–612) pro extrakci attachments.
- **Implementační detail**:
  1. Playwright JSON reporter ukládá screenshoty jako `attachments` na úrovni test result (`suites[].specs[].tests[].results[].attachments` s `name`/`contentType`/`path`). V `_run_single_browser` po parse `json_report` (ř. 606) projdi a posbírej attachmenty s `contentType` `image/png` (screenshots) a případně `video`/`trace`.
  2. Rozšiř `BrowserRunResult`/`SilkBrowserRunResult` o `screenshots: list[{name, path}]` (a volitelně `attachments`). Servíruj soubory přes existující artefakt endpoint (stejný mechanismus jako trace download, ř. 1087) nebo data-URL pro malé PNG.
  3. **Screenshots tab**: grid náhledů (`<img>` z artefakt URL) + jméno testu; klik = lightbox/nová karta.
  4. **Network tab**: Playwright JSON reporter network requesty nenese — pravdivá zpráva. MVP: ponech „Network log v Playwright trace" + prominentní „Download trace" (už existuje ř. 1087–1096). Plné HAR vyžaduje `--har` flag (samostatný ticket) — neimplementovat naslepo.
  5. Empty-state ponech, když `screenshots.length === 0`.
- **Na co dát pozor**: cesty k attachmentům jsou absolutní v `run_d/<browser>/results` — servírovat jen z whitelistovaného run adresáře (path traversal). Reuse existující artefakt-serving auth.
- **Přínos**:
  - 🎨 Vizuální galerie screenshotů místo prázdné ikony.
  - ⚙️ Screenshots tab funkční; Network tab čestně odkazuje na trace.
  - 👤 Rychlá vizuální kontrola výsledku bez stahování trace.
  - 🙋 QA vidí failure screenshot okamžitě v appce.
- **Závislosti/rizika**: závisí na tvaru Playwright JSON reportu (verze PW). Network = vědomě jen trace odkaz, ne full HAR.

---

## 5. `getSidecarBaseUrl` bez timeoutu → trvalý „connecting"

- **Priorita**: P0 — `resolveSidecarBaseUrl` (client.ts ř. 52–74) čeká na `sidecar://ready` event bez timeoutu (komentář ř. 66–68 to přiznává); když sidecar nenaběhne, UI visí navždy bez chyby.
- **Náročnost**: S (~0.5 d).
- **Soubory**: `apps/studio-fe/src/lib/sidecar/client.ts` (`resolveSidecarBaseUrl` ř. 52, cache `_urlPromise` ř. 40).
- **Implementační detail**:
  1. Obal `listen<number>("sidecar://ready")` Promise do `Promise.race` s timeoutem (~20 s — pokrývá ~10 s onefile cold start + rezerva).
  2. Před čekáním na event přidej retry poll `get_sidecar_port` (back-off 250 ms → 2 s, ~10 pokusů) — port se může objevit, i když event utekl před `listen`.
  3. Při timeoutu **resetuj cache** (`_urlPromise = null`), aby další `getSidecarBaseUrl()` zkusil znovu, a `throw new Error("sidecar nenaběhl (timeout)")`.
  4. V UI (SilkPanel/health indikátor) odchyť chybu a zobraz stav „Sidecar nedostupný — Zkusit znovu" s retry tlačítkem (volá `getSidecarBaseUrl` po reset cache).
- **Na co dát pozor**: cache `_urlPromise` (ř. 40) drží i odmítnutou promise → při chybě MUSÍŠ vynulovat, jinak permanentní fail. `unlisten` po vyřešení/timeoutu (leak listeneru).
- **Přínos**:
  - 🎨 Jasný error/retry stav místo nekonečného spinneru.
  - ⚙️ Bounded resolve; ozdravná retry cesta.
  - 👤 Uživatel ví, že je problém, a má tlačítko k akci.
  - 🙋 Žádné „appka zamrzla" — diagnostikovatelné selhání startu.
- **Závislosti/rizika**: timeout musí být > nejhorší cold start, jinak false negatives na pomalých strojích → konzervativních 20 s.

---

## 6. SilkPanel (1112 ř., jádro) bez testu

- **Priorita**: P1 — největší a nejdůležitější FE komponenta bez vitest pokrytí; regrese hrozí hlavně po #1–#4.
- **Náročnost**: M (~1 d).
- **Soubory**: nový `apps/studio-fe/src/components/SilkPanel.test.tsx`. Vzor: existující vitest setup (`vitest` v package.json), mock `sidecar` z `lib/sidecar/client.ts`.
- **Implementační detail**:
  1. Setup: `@testing-library/react` + `vitest`; mockuj modul `../lib/sidecar/client` (`silkFrameworks`, `silkRecordStart/Stop`, run, history).
  2. Testy (priorita podle rizika):
     - render + výchozí stav (RunForm, prázdná historie/empty-state).
     - browser toggle: nelze odznačit poslední browser (logika ř. 550–554).
     - submit `RunForm` volá `onRun` s trimnutým specPath + vybranými browsery.
     - po #3: „Spustit hned" po captured specu volá run handler.
     - po #2: SSE live lines se renderují (mock EventSource/fetch reader).
     - tab switching (console/network/screenshots) renderuje správný obsah.
  3. Přidej `data-testid` jen kde DOM dotaz křehký.
- **Na co dát pozor**: EventSource/fetch-SSE potřebuje mock (jsdom je nemá) — `vi.stubGlobal("EventSource", ...)`. Async run flow → `await screen.findBy...`.
- **Přínos**:
  - 🎨 n/a
  - ⚙️ Regresní síť pro jádro Silk; chrání #1–#4.
  - 👤 n/a (nepřímo: méně regresí = stabilnější UX).
  - 🙋 Vyšší důvěra Q
- **Závislosti/rizika**: psát PO #2/#3, ať se testy nepřepisují. Riziko křehkých DOM dotazů → testid.

---

## 7. Ruční psaní absolutních cest → nativní Tauri file picker

- **Priorita**: P1 — `RunForm` (ř. 546) i workspaceDir se píší ručně; chybové a otravné. `@tauri-apps/plugin-dialog` NENÍ nainstalován (jen plugin-shell) → vyžaduje setup.
- **Náročnost**: M (~1 d, kvůli Rust plugin registraci + capabilities).
- **Soubory**: `apps/studio-fe/package.json` (dep), `apps/studio-fe/src-tauri/Cargo.toml`, `src-tauri/src/lib.rs` (plugin init), `src-tauri/capabilities/*.json` (dialog perms), `apps/studio-fe/src/components/SilkPanel.tsx` (`RunForm` ř. 539–559).
- **Implementační detail**:
  1. FE: `pnpm add @tauri-apps/plugin-dialog` (verze ^2). Rust: `cargo add tauri-plugin-dialog` v `src-tauri`.
  2. Registruj v Tauri builderu: `.plugin(tauri_plugin_dialog::init())` (v `lib.rs`/`main.rs`).
  3. Capabilities: přidej `dialog:allow-open` (a `dialog:default`) do `src-tauri/capabilities/default.json`.
  4. V `RunForm` přidej „Procházet…" tlačítko vedle Spec file path: `import { open } from "@tauri-apps/plugin-dialog"; const path = await open({ filters: [{ name: "Spec", extensions: ["ts","js"] }] }); if (path) setSpecPath(path as string);`. Pro workspaceDir `open({ directory: true })`.
  5. Fallback mimo Tauri (`isTauri()` z client.ts) → ponech textový input (web/dev).
- **Na co dát pozor**: input ponech editovatelný i s pickerem (CI/Playwright zadává cesty programově). Bez capabilities entry picker tiše selže.
- **Přínos**:
  - 🎨 Nativní OS dialog místo holého text fieldu.
  - ⚙️ Picker pro soubor i adresář; validní cesty.
  - 👤 Konec překlepů v absolutních cestách; rychlejší výběr.
  - 🙋 Méně frustrace, méně „spec not found" chyb.
- **Závislosti/rizika**: nová Rust dependency → rebuild Tauri; capabilities musí sednout, jinak runtime deny. Web fallback nutný kvůli E2E.

---

## 8. „Test monitors" mód = slepá ulička

- **Priorita**: P2 — `monitors` mód (App.tsx ř. 26–32, ActivityBar ř. 19) ukazuje jen EmptyState odkazující na neexistující „Schedule run" tlačítko v Silku → matoucí mrtvá cesta.
- **Náročnost**: S (~0.5 d pro skrytí; L pokud plná implementace scheduleru).
- **Soubory**: `apps/studio-fe/src/components/ActivityBar.tsx` (ř. 17–22, `AppMode` ř. 4), `apps/studio-fe/src/App.tsx` (ř. 11, 26–32).
- **Implementační detail (doporučeno: skrýt do doby implementace)**:
  1. Odstraň `monitors` z pole `modes` v ActivityBar (ř. 19) — ikona zmizí z lišty.
  2. Ponech `"monitors"` v typu `AppMode` (zpětná kompat) nebo odstraň a sjednom místě uprav App.tsx větev.
  3. V App.tsx odstraň/zakomentuj `mode === "monitors"` blok (ř. 26–32) nebo nech jako mrtvý kód za odstraněním z lišty.
  4. Alternativa „označit jako brzy": ponech ikonu, přidej `disabled` styl + tooltip „Brzy" (žádný klik na slepou stránku).
- **Na co dát pozor**: pokud existuje deep-link/persist módu, ošetři neznámou hodnotu → fallback `silk`.
- **Přínos**:
  - 🎨 Čistší ActivityBar bez mrtvé ikony.
  - ⚙️ Odstraní cestu vedoucí nikam.
  - 👤 Žádné matení falešnou featurou.
  - 🙋 Důvěra — co je v UI, to funguje.
- **Závislosti/rizika**: nízké. Když se v budoucnu monitory implementují, znovu odkrýt.

---

## 9. Mobile boot/start bez pollingu

- **Priorita**: P1 — `handleBoot` (MobilePanel.tsx ř. 280) udělá `refreshDevices()` jednou hned po startu; simulator/emulator naběhne až za desítky sekund → stav v UI je zastaralý.
- **Náročnost**: M (~1 d).
- **Soubory**: `apps/studio-fe/src/components/MobilePanel.tsx` (`handleBoot` ř. 280–303, `refreshDevices` ř. ~250, `refreshAppiumStatus` ř. 263).
- **Implementační detail**:
  1. Přidej helper `pollUntil(predicate, { intervalsMs: [1000,2000,3000,5000,5000,8000], }) ` s back-off — po každém intervalu zavolej `mobileDevices()` a zkontroluj, zda `device.state === "booted"/"running"`.
  2. V `handleBoot` po úspěšném `mobileSimulatorBoot/EmulatorStart` spusť poll místo jednorázového `refreshDevices`; aktualizuj `setDevices` po každém kroku (živý stav).
  3. Drž `bootingId` dokud poll nedosáhne booted stavu nebo nevyprší (~60 s cap) → pak toast „spuštěno" / „timeout".
  4. Cleanup: zruš poll v `useEffect` cleanup a při unmountu (AbortController/`cancelled` flag).
- **Na co dát pozor**: paralelní boot více zařízení → poll keyovat per `device.id`. Nepřekrývej s `useEffect` auto-refreshem (ř. 275–278).
- **Přínos**:
  - 🎨 Spinner/„spouští se…" stav se sám přepne na „běží".
  - ⚙️ Reálné sledování stavu zařízení místo jednorázového snapshotu.
  - 👤 Uživatel nemusí ručně refreshovat; vidí, kdy je zařízení připravené.
  - 🙋 Méně klikání; jistota, kdy lze spustit mobilní test.
- **Závislosti/rizika**: závisí na tom, že `mobileDevices()` vrací stav (booted/running). Back-off, ať nezahltí adb/simctl.

---

## 10. A11y modaly bez focus-trap/Escape/aria + chybí first-run onboarding

- **Priorita**: P1 — přístupnost (Tomáš = QA, a11y je doménová hodnota) + onboarding pro nové uživatele. Modaly (RecordDialog ř. 425, Install dialog ř. ~320, New test) bez focus-trapu/Escape/`role="dialog"`.
- **Náročnost**: M (~1 d a11y; +S onboarding).
- **Soubory**: `apps/studio-fe/src/components/SilkPanel.tsx` (modaly), nový sdílený `apps/studio-fe/src/components/Modal.tsx`, případně onboarding `apps/studio-fe/src/components/FirstRunOnboarding.tsx` + flag v `localStorage`.
- **Implementační detail**:
  1. Vytvoř sdílený `<Modal>`: `role="dialog"`, `aria-modal="true"`, `aria-labelledby` (na titulek), Escape → `onClose`, focus-trap (focus na první focusovatelný prvek při mountu, cyklení Tab v rámci dialogu, návrat focusu na trigger po zavření).
  2. Refaktoruj RecordDialog (ř. 425), Install dialog a New test dialog na `<Modal>`.
  3. Overlay klik mimo obsah → `onClose` (volitelně, ne během recordingu/install — guard).
  4. **Onboarding**: při prvním spuštění (`localStorage.getItem("theridion.onboarded")` prázdné) zobraz 3–4 krokový průvodce: co je Silk, jak nahrát spec, jak spustit, kde je Hub/Mobile. Po dokončení set flag.
  5. Lokalizace CZ (konzistentní s existující CZ copy).
- **Na co dát pozor**: focus-trap nesmí zablokovat živý log scroll v RecordDialogu. Nepoužívat těžkou knihovnu, pokud stačí ~40 ř. hooku (`useFocusTrap`). Onboarding nesmí blokovat E2E (skip přes env/flag).
- **Přínos**:
  - 🎨 Konzistentní modal chrome + onboarding obrazovky.
  - ⚙️ Escape/overlay zavírání, správné aria role.
  - 👤 Klávesnicová ovladatelnost; noví uživatelé vědí, kde začít.
  - 🙋 Přístupné i pro power-usery (klávesnice); rychlejší první úspěch.
- **Závislosti/rizika**: refaktor modalů se dotkne #2/#3 (RecordDialog) → koordinovat pořadí (ideálně po #2/#3 nebo zároveň). E2E skip onboardingu nutný.

---

## Bonus. `_build_a11y_wrapper` axe audit nikdy nespustí

- **Priorita**: P2 — `_build_a11y_wrapper` (silk.py ř. 525–534) jen vloží `import AxeBuilder` na začátek souboru, ale NIKDY nezavolá `new AxeBuilder({ page }).analyze()` → audit se reálně neprovede; `run_accessibility_audit` flag je no-op.
- **Náročnost**: M (~1 d — vyžaduje injekci do test body, ne jen importu).
- **Soubory**: `apps/sidecar-fe/theridion_sidecar/api/silk.py` (`_build_a11y_wrapper` ř. 525, `_build_mock_wrapper` jako vzor ř. ~480–514), parsování výsledku v `_run_single_browser`. Testy `test_silk.py`.
- **Implementační detail**:
  1. Místo pouhého importu wrapuj tělo testu: po `await page.goto(...)` (nebo na konci testu) injektuj `const a11y = await new AxeBuilder({ page }).analyze(); await testInfo.attach('axe', { body: JSON.stringify(a11y.violations), contentType: 'application/json' });`.
  2. Spolehlivý přístup: použij Playwright `test.afterEach(async ({ page }, testInfo) => { ... })` přidaný wrapperem — nevyžaduje parsovat tělo uživatelského testu (robustní vůči libovolnému specu).
  3. Po runu vyzvedni `axe` attachment z `json_report` (stejný mechanismus jako #4) a vrať `a11y_violations` v `BrowserRunResult`.
  4. FE (po #4): nový tab/sekce „A11y" se seznamem violations (impact, help, nodes).
  5. Ověř, že `@axe-core/playwright` je v Playwright projektu dostupný (jinak jasná chyba „nainstaluj @axe-core/playwright").
- **Na co dát pozor**: `afterEach` hook musí přežít, i když test selže (audit se má pokusit i tak). NEparsovat tělo uživatelského kódu regexem (křehké). Ruff debt NEřešit.
- **Přínos**:
  - 🎨 n/a (FE tab až v navazujícím kroku).
  - ⚙️ A11y audit konečně reálně běží; flag přestane být no-op.
  - 👤 n/a přímo (hodnota přes FE prezentaci violations).
  - 🙋 QA dostane reálné a11y nálezy z runů — silný diferenciátor produktu.
- **Závislosti/rizika**: závisí na `@axe-core/playwright` v projektu. Prezentace výsledků staví na #4 (attachment parsing). Bez FE části je hodnota skrytá.

---

## Souhrnná tabulka

| # | Bod | Priorita | Náročnost |
|---|-----|----------|-----------|
| 1 | Async multi-browser run | P0 | M (~1 d) |
| 2 | SSE live recording stream | P0 | S (~0.5 d) |
| 3 | Použití nahraného specu | P0 | M (~1 d) |
| 4 | Network & Screenshots taby | P1 | M (~1 d) |
| 5 | Sidecar URL timeout/retry | P0 | S (~0.5 d) |
| 6 | SilkPanel vitest | P1 | M (~1 d) |
| 7 | Nativní Tauri file picker | P1 | M (~1 d) |
| 8 | „Test monitors" skrýt/řešit | P2 | S (~0.5 d) |
| 9 | Mobile back-off polling | P1 | M (~1 d) |
| 10 | A11y modaly + onboarding | P1 | M (~1 d) |
| B | axe a11y audit reálně spustit | P2 | M (~1 d) |
