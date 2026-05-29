# Theridion — průřezový roadmap zlepšení (4 aplikace)

> Konsolidace 40 bodů na zlepšení napříč **Studio FE**, **Studio BE**, **Hub** a **Runner**.
> Detailní implementační kroky, soubory a rizika jsou v `docs/improvements-plan.md` v každém z repozitářů
> (`theridion-fe`, `theridion-be`, `theridion-hub`, `theridion-runner`).
>
> Tento dokument je **sekvenční roadmap** — řadí body napříč všemi aplikacemi do 4 vln
> podle pravidla **bezpečnost → korektnost/důvěra → architektura → UX/polish**.

## Legenda přínosu

| Ikona | Dimenze | Co znamená |
|---|---|---|
| 🎨 | Grafický | vizuální vzhled, layout, grafy, design konzistence |
| ⚙️ | Funkční | nová/opravená funkcionalita, korektnost chování |
| 👤 | UX | plynulost, srozumitelnost, ovládání, a11y, DX |
| 🙋 | Pro uživatele | dopad na reálnou práci uživatele (QA/CI inženýr) |

Náročnost: **S** ≈ ≤1 den · **M** ≈ 1–4 dny · **L** ≈ 5+ dní.

---

## 🌊 Vlna 0 — Bezpečnost & integrita (udělat první)

Většinou levné, ale chrání data, tokeny a release. Bezpečnostní dluh = nejvyšší priorita.

| App | # | Bod | Náro. | Hlavní přínos |
|---|---|---|---|---|
| Hub | 3 | Session expirace — `decode()` nekontroluje `issuedAt` vs MAX_AGE → replay navždy | S | 🙋 ochrana přístupu · ⚙️ vynucení TTL |
| Hub | 4 | Hand-rolled SQL (`rate-limit.ts`, `db-schema.ts`) → tagged template | S | ⚙️ SQL injection prevence |
| BE | 5 | Sjednotit `{{secret:NAME}}` s vaultem — tokeny dnes plaintext v `environments/*.json` | M | 🙋 žádné tajné tokeny v git-friendly souborech |
| Hub | 2 | Multi-tenant scoping ingest tokenu + RBAC (tabulka `ingest_tokens`) | L | 🙋 izolace dat mezi týmy/projekty |
| Runner | 7 | Verze single-source-of-truth + oprava release race (Docker job bez `needs:` na PyPI) | M | ⚙️ reprodukovatelný a spolehlivý release |

**Konflikt řešení:** bezpečnost > rychlost dodání — Vlna 0 jde před každou feature prací, i když zdrží UX body.

---

## 🌊 Vlna 1 — Korektnost & důvěra (rozbité/zavádějící chování)

Funkce, které dnes tiše lžou nebo nefungují. Bez nich uživatel ztrácí důvěru v nástroj.

| App | # | Bod | Náro. | Hlavní přínos |
|---|---|---|---|---|
| Runner | 8 | Exit-code sémantika ("no files" 0 vs 3, config error = traceback místo exit 2) | S | ⚙️ pravdivý CI kontrakt · 🙋 spolehlivé gates |
| Runner | 1 | `--workers`/`--watch` jsou no-op — implementovat nebo failnout exit 2 | S–M | ⚙️ konec false-paralelizace |
| Runner | 2 | `--filter <tag>` se tiše ignoruje → gate běží na jiné sadě | S | 🙋 gate testuje to, co uživatel čeká |
| FE | 1 | Async multi-browser run — `run_spec` sync `def` + blokující `subprocess.run` blokuje event loop | M | ⚙️ paralelní běh · 👤 sidecar nezamrzne |
| FE | 5 | `getSidecarBaseUrl` bez timeoutu → trvalý "connecting"; přidat timeout + retry | S | 👤 konec nekonečného loaderu |
| FE | 2 | SSE live recording stream — `/record/stream` se nikdy nepřipojí (Tauri → fetch-SSE, ne EventSource) | S | 🎨 živé řádky · 👤 viditelný průběh nahrávání |
| FE | 3 | Použití nahraného specu — most "Otevřít v editoru"/"Spustit hned" (dnes se spec zahodí) | M | ⚙️ uzavře record→run flow · 🙋 recorder má smysl |
| BE | 4 | Response guard na obří payloady (>1 MB → raw/download, parse ve workeru) | M | ⚙️ UI nezamrzne · 👤 stabilita |
| Runner | 4 + Hub | 7 | Idempotency-Key na uploadu + dedup okno na ingestu (pár) | S+M | ⚙️ žádné duplicitní běhy v dashboardu |
| Runner | 10 | Testy kritických cest + PR CI workflow (dnes testy jen na tagu) | M | ⚙️ regrese se chytí dřív · 👤 DX |

---

## 🌊 Vlna 2 — Architektura & pokrytí (předpoklad dlouhodobé rychlosti)

Refaktory a coverage, které odblokují plynulou další práci.

| App | # | Bod | Náro. | Hlavní přínos |
|---|---|---|---|---|
| BE | 1 | Rozbít App.tsx (1587 ř., 31 useState) + panely → Zustand store | L | 👤 plynulost (re-render izolace) · ⚙️ udržitelnost |
| BE | 2 | Load test: env proměnné + auth (převzít pipeline z `requests.py`) | M | ⚙️ load test funguje s env/tokenem |
| BE | 3 | Load test: live progress přes WS/SSE (infra už existuje) | M | 🎨 RPS/latency graf v čase · 👤 real-time feedback |
| Hub | 1 | Overview KPI na reálná ingestovaná data (dnes mocky `src/data/*`) | M | ⚙️ dashboard ukazuje skutečnost · 🙋 hodnota Hubu |
| Hub | 6 | Keyset pagination + index `(started_at DESC)` | S | ⚙️ výkon při růstu dat |
| FE | 6 | SilkPanel vitest (jádro, 1112 ř., dnes bez testu) | M | ⚙️ regresní jistota |
| BE | 6 | Test coverage: request-build / response / substituce | M | ⚙️ regresní jistota |
| Hub | 10 | CSP nonce (místo `'unsafe-inline'`) + route testy + smazat mrtvé root stuby | M | 🙋 XSS hardening · ⚙️ úklid |
| Hub | 9 / Runner | 9 | Strukturovaná observabilita ingest/DB + `--log-format json` + retry metriky | M | 👤 diagnostika místo černé skříňky |
| Runner | 5 | Docker multi-stage + non-root `USER` | M | 🙋 menší/bezpečnější image, soubory ne jako root |

---

## 🌊 Vlna 3 — UX & polish (grafický a zážitkový přínos)

Body s největším 🎨/👤 dopadem — dělat až stojí základ.

| App | # | Bod | Náro. | Hlavní přínos |
|---|---|---|---|---|
| Hub | 5 | `/runs` observability view — time-range, bar-chart pass/fail, filtry (Mobbin: Snowflake/Modal/Cloudflare) | L | 🎨 grafy · 👤 analýza trendů |
| Hub | 8 | Onboarding empty-state "Connect your first Runner" (token + curl) | M | 🎨 first-run obrazovka · 🙋 rychlý start |
| FE | 4 | Network & Screenshots taby — parsovat attachments z `json_report` | M | 🎨 reálná data místo placeholderů |
| FE | 10 | A11y modaly (focus-trap/Escape/aria) + first-run onboarding | M | 👤 klávesnicová dostupnost |
| FE | 9 | Mobile boot/start back-off polling stavu | M | 👤 status doběhne sám (10–30s) |
| FE | 7 | Nativní Tauri file picker (pozor: `plugin-dialog` není nainstalován) | M | 👤 konec ručních absolutních cest |
| FE | 8 | "Test monitors" mód — skrýt z ActivityBaru (dnes slepá ulička) | S | 👤 žádné kliknutí naprázdno |
| FE | B | axe a11y audit reálně spustit (`_build_a11y_wrapper` je no-op) | M | ⚙️ A11y tab ukáže pravdu |
| BE | 7 | Bulk-edit key/value tabulka pro headers/params (rozšíření, model už má `enabled`) | S | 👤 rychlejší editace (Mobbin: Postman) |
| BE | 8 | Inline preview/autocomplete `{{var}}` — highlight nedefinovaných + hover hodnota | M | 👤 konec záhadných 404 (Mobbin: Retool) |
| BE | 9 | i18n CS/EN provider + locale toggle (dnes mix) | M | 👤 konzistentní jazyk |
| BE | 10 | Guided empty states (žádná collection/response/env) | S | 🎨 first-run · 👤 navigace |
| Runner | 3 | GitHub-native výstup: annotations + SARIF + step outputs | M–L | 👤 inline faily v PR · ⚙️ navazující stepy |
| Runner | 6 | Action digest pin místo floating `:1` tagu | S | ⚙️ reprodukovatelnost |

---

## Průřezová témata (vyřešit jednou, profituje víc apps)

- **Idempotence** — Runner #4 (`Idempotency-Key`) ↔ Hub #7 (dedup) řešit jako jeden pár.
- **Observabilita** — Runner #9 + Hub #9 sdílí formát strukturovaného logu.
- **Live progress** — FE #2 (recording SSE), FE #1 (async run), BE #3 (loadtest stream) sdílí WS/SSE vzor.
- **Empty/onboarding states** — FE #10, BE #10, Hub #8 mají společný design pattern.
- **Test coverage jádra** — FE #6, BE #6, Hub #10, Runner #10: nejrizikovější moduly jsou nejméně pokryté.

## Top 5 napříč platformou (kdyby byl čas jen na pět)

1. **Hub #4** SQL → tagged template (S) — injection prevence
2. **Hub #3** session expirace (S) — replay prevence
3. **BE #5** `{{secret:NAME}}` (M) — žádné plaintext tokeny
4. **Runner #7** verze + release race (M) — spolehlivý release všeho ostatního
5. **FE #1** async multi-browser run (M) — odblokuje sidecar event loop
