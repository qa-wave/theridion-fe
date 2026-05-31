"""silk_locators — Multi-candidate locator extraction and healing support.

During codegen/record we capture 3–6 ranked candidate locators per element.
At run time the runner falls back through candidates in priority order; when a
non-primary locator succeeds it emits a 'healed' event.

Priority order (lower = higher priority):
  1  data-testid  — most stable, explicit contract
  2  role+name    — semantic, ARIA-based
  3  label/placeholder — form-specific semantics
  4  text         — visible text (fragile if copy changes)
  5  css          — CSS selector (fragile to structure changes)
  6  xpath        — last resort

All functions are pure (no I/O, no FastAPI) so they are trivially unit-testable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class LocatorCandidate:
    """One ranked locator strategy for an element."""

    priority: int  # Lower = try first
    strategy: str  # "test-id" | "role" | "label" | "placeholder" | "text" | "css" | "xpath"
    selector: str  # Raw Playwright locator expression e.g. getByRole('button', { name: 'Submit' })
    pw_code: str   # Full line of Playwright code using this selector (ready to inject)


@dataclass
class ElementLocators:
    """All captured locator candidates for a single element action."""

    primary: LocatorCandidate
    candidates: list[LocatorCandidate] = field(default_factory=list)

    @property
    def all_ranked(self) -> list[LocatorCandidate]:
        """Return all candidates sorted by priority (primary first)."""
        return sorted([self.primary, *self.candidates], key=lambda c: c.priority)


# ---------------------------------------------------------------------------
# Regex patterns for extracting locator strategy from a Playwright expression
# ---------------------------------------------------------------------------

_TESTID_RE = re.compile(r"getByTestId\(['\"]([^'\"]+)['\"]\)")
_ROLE_NAME_RE = re.compile(
    r"getByRole\(['\"]([^'\"]+)['\"].*?name['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
    re.DOTALL,
)
_ROLE_ONLY_RE = re.compile(r"getByRole\(['\"]([^'\"]+)['\"]\)")
_LABEL_RE = re.compile(r"getByLabel\(['\"]([^'\"]+)['\"]\)")
_PLACEHOLDER_RE = re.compile(r"getByPlaceholder\(['\"]([^'\"]+)['\"]\)")
_TEXT_RE = re.compile(r"getByText\(['\"]([^'\"]+)['\"]\)")
_LOCATOR_CSS_RE = re.compile(r"locator\(['\"]([^'\"]+)['\"]\)")
_XPATH_RE = re.compile(r"locator\(['\"]xpath=([^'\"]+)['\"]\)")


def _detect_primary_strategy(selector: str) -> str:
    """Identify the locator strategy for a given Playwright expression."""
    if _TESTID_RE.search(selector):
        return "test-id"
    if _ROLE_NAME_RE.search(selector):
        return "role"
    if _ROLE_ONLY_RE.search(selector):
        return "role"
    if _LABEL_RE.search(selector):
        return "label"
    if _PLACEHOLDER_RE.search(selector):
        return "placeholder"
    if _TEXT_RE.search(selector):
        return "text"
    if _XPATH_RE.search(selector):
        return "xpath"
    if _LOCATOR_CSS_RE.search(selector):
        return "css"
    return "css"


_STRATEGY_PRIORITY: dict[str, int] = {
    "test-id": 1,
    "role": 2,
    "label": 3,
    "placeholder": 4,
    "text": 5,
    "css": 6,
    "xpath": 7,
}


def _priority(strategy: str) -> int:
    return _STRATEGY_PRIORITY.get(strategy, 99)


def _make_candidate(strategy: str, selector: str, action_suffix: str = "") -> LocatorCandidate:
    """Build a LocatorCandidate from a strategy+selector+action."""
    pw = f"page.{selector}" if action_suffix == "" else f"page.{selector}{action_suffix}"
    return LocatorCandidate(
        priority=_priority(strategy),
        strategy=strategy,
        selector=selector,
        pw_code=pw,
    )


# ---------------------------------------------------------------------------
# Candidate derivation heuristics
# ---------------------------------------------------------------------------

def _derive_fallback_candidates(primary_selector: str, primary_strategy: str) -> list[LocatorCandidate]:
    """Derive alternative locators from a primary Playwright expression.

    We extract semantic info from the primary selector and synthesise
    equivalent selectors using other strategies where possible.
    """
    candidates: list[LocatorCandidate] = []

    # --- Extract visible text for text-based fallback ---
    text_val: str | None = None
    m = _ROLE_NAME_RE.search(primary_selector)
    if m:
        text_val = m.group(2)

    if text_val is None:
        m = _TEXT_RE.search(primary_selector)
        if m:
            text_val = m.group(1)

    if text_val is None:
        m = _LABEL_RE.search(primary_selector)
        if m:
            text_val = m.group(1)

    if text_val is None:
        m = _PLACEHOLDER_RE.search(primary_selector)
        if m:
            text_val = m.group(1)

    # --- Extract role ---
    role_val: str | None = None
    m = _ROLE_NAME_RE.search(primary_selector) or _ROLE_ONLY_RE.search(primary_selector)
    if m:
        role_val = m.group(1)

    # --- Build alternative selectors ---

    # If primary is test-id, also offer role+name and text fallbacks
    if primary_strategy == "test-id":
        tid_m = _TESTID_RE.search(primary_selector)
        if tid_m:
            css_sel = f"locator('[data-testid=\"{tid_m.group(1)}\"]')"
            candidates.append(_make_candidate("css", css_sel))
        if text_val:
            candidates.append(_make_candidate("text", f"getByText('{text_val}')"))

    # If primary is role+name, offer text and css fallbacks
    elif primary_strategy == "role":
        if text_val:
            candidates.append(_make_candidate("text", f"getByText('{text_val}')"))
        if role_val:
            css_sel = f"locator('[role=\"{role_val}\"]')"
            candidates.append(_make_candidate("css", css_sel))
            if text_val:
                xpath_sel = f"locator('xpath=//*[@role=\"{role_val}\" and normalize-space(text())=\"{text_val}\"]')"
                candidates.append(_make_candidate("xpath", xpath_sel))

    # If primary is label, offer placeholder and text fallbacks
    elif primary_strategy == "label":
        m = _LABEL_RE.search(primary_selector)
        if m:
            label_text = m.group(1)
            css_sel = f"locator('[aria-label=\"{label_text}\"]')"
            candidates.append(_make_candidate("css", css_sel))
            candidates.append(_make_candidate("text", f"getByText('{label_text}')"))

    # If primary is placeholder, offer label and text fallbacks
    elif primary_strategy == "placeholder":
        m = _PLACEHOLDER_RE.search(primary_selector)
        if m:
            ph = m.group(1)
            css_sel = f"locator('[placeholder=\"{ph}\"]')"
            candidates.append(_make_candidate("css", css_sel))
            if text_val:
                candidates.append(_make_candidate("text", f"getByText('{text_val}')"))

    # If primary is text, offer role and css fallbacks
    elif primary_strategy == "text":
        m = _TEXT_RE.search(primary_selector)
        if m:
            txt = m.group(1)
            xpath_sel = f"locator('xpath=//*[normalize-space(text())=\"{txt}\"]')"
            candidates.append(_make_candidate("xpath", xpath_sel))

    # If primary is css/xpath, try to synthesise simpler alternatives
    elif primary_strategy in ("css", "xpath"):
        m = _LOCATOR_CSS_RE.search(primary_selector)
        if m:
            css_val = m.group(1)
            # Try to extract a test-id from a CSS selector
            tid_m = re.search(r'\[data-testid=["\']([^"\']+)["\']\]', css_val)
            if tid_m:
                candidates.append(_make_candidate("test-id", f"getByTestId('{tid_m.group(1)}')"))

    return candidates


def extract_candidates(selector: str) -> ElementLocators:
    """Extract 3–6 ranked locator candidates from a Playwright locator expression.

    The *selector* is the raw expression passed to page.*, e.g.
    ``getByRole('button', { name: 'Submit' })``.

    Returns an :class:`ElementLocators` with the primary locator and all
    viable fallback candidates, deduplicated and ranked by priority.
    """
    strategy = _detect_primary_strategy(selector)
    primary = _make_candidate(strategy, selector)

    fallbacks = _derive_fallback_candidates(selector, strategy)

    # Deduplicate by selector string (avoid duplicating primary).
    seen: set[str] = {selector}
    unique_fallbacks: list[LocatorCandidate] = []
    for c in fallbacks:
        if c.selector not in seen:
            seen.add(c.selector)
            unique_fallbacks.append(c)

    return ElementLocators(primary=primary, candidates=unique_fallbacks)


# ---------------------------------------------------------------------------
# Healing wrapper code generator
# ---------------------------------------------------------------------------

_HEAL_WRAPPER_COMMENT = """\
// ---------------------------------------------------------------------------
// Silk self-healing locator wrapper — injected by Silk backend
// ---------------------------------------------------------------------------
//
// Each element action is wrapped with tryLocators():
//   1. Try candidates in priority order.
//   2. If a fallback succeeds, emit a 'silk:healed' console message so the
//      UI/log can surface it.
//   3. Re-throw last error when all candidates fail.
//
"""

_HEAL_HELPER_TS = r"""import { test as _silkHealBase, expect as _silkHealExpect, Page } from '@playwright/test';

const _silkHealLog: Array<{ primary: string; healed: string; strategy: string }> = [];

/** Try a list of Playwright page expressions in order; return first that works. */
async function _tryLocators(
  page: Page,
  candidates: Array<{ selector: string; strategy: string }>,
  action: (locator: import('@playwright/test').Locator) => Promise<void>,
  testInfo: import('@playwright/test').TestInfo,
): Promise<void> {
  let lastErr: unknown;
  for (const { selector, strategy } of candidates) {
    try {
      // Build locator from expression string
      const locExpr = selector.startsWith('locator(')
        ? page.locator(selector.replace(/^locator\(['"](.+)['"]\)$/, '$1'))
        : (page as unknown as Record<string, (s: string, o?: object) => import('@playwright/test').Locator>)[
            selector.split('(')[0]
          ]?.(selector.replace(/^[a-zA-Z]+\(/, '(').slice(1, -1));
      if (!locExpr) continue;
      await action(locExpr);
      if (candidates[0].selector !== selector) {
        // Healed — record it
        const entry = { primary: candidates[0].selector, healed: selector, strategy };
        _silkHealLog.push(entry);
        console.log(`silk:healed primary="${entry.primary}" healed="${entry.healed}" strategy="${strategy}"`);
        await testInfo.attach('silk-healed.json', {
          contentType: 'application/json',
          body: JSON.stringify(_silkHealLog),
        });
      }
      return;
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr;
}

const test = _silkHealBase;
const expect = _silkHealExpect;

// ---- Original spec follows (playwright/test import stripped below) ----
"""


def build_healing_wrapper(original_code: str, locator_map: dict[str, ElementLocators]) -> str:
    """Wrap a Playwright spec to use self-healing locators.

    *locator_map* maps each primary selector expression found in the spec to
    its :class:`ElementLocators` (with ranked fallbacks).  We inject a helper
    function and rewrite action calls to use it.

    If *locator_map* is empty (no candidates captured) we return the original
    code unchanged to avoid breaking runs that don't have healing data.
    """
    if not locator_map:
        return original_code

    # Build JS candidate arrays for each primary selector
    candidate_blocks: list[str] = []
    for primary_sel, element_locs in locator_map.items():
        ranked = element_locs.all_ranked
        entries = ", ".join(
            f'{{ selector: {_js_str(c.selector)}, strategy: {_js_str(c.strategy)} }}'
            for c in ranked
        )
        safe_key = _js_str(primary_sel)
        candidate_blocks.append(
            f"  {safe_key}: [{entries}],"
        )

    candidates_ts = "const _silkCandidates: Record<string, Array<{{ selector: string; strategy: string }}>> = {{\n"
    candidates_ts += "\n".join(candidate_blocks)
    candidates_ts += "\n};\n"

    # Strip @playwright/test imports from original (we re-export them).
    lines = original_code.splitlines()
    from theridion_sidecar.api.silk import _is_playwright_test_import  # lazy import to avoid circular
    filtered_lines = [ln for ln in lines if not _is_playwright_test_import(ln)]

    return (
        _HEAL_WRAPPER_COMMENT
        + _HEAL_HELPER_TS
        + candidates_ts
        + "\n// ---- healed spec ----\n"
        + "\n".join(filtered_lines)
    )


def _js_str(s: str) -> str:
    """Escape a Python string as a JSON/JS double-quoted string."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
