"""Dev-mode seed data for Theridion Eyes sidecar.

Seeds the local storage on first run so the History panel and trace tabs are
populated without executing any real tests.  Idempotent: if silk_runs already
has rows, or collections already exist, nothing is written.

Call ``maybe_seed()`` from the FastAPI lifespan after the DB schema is
initialised.  The seed is gated to the real home directory (``~/.theridion``);
when tests override ``THERIDION_HOME`` via env-var the fake tmp_path is always
empty so this code is never reached (``maybe_seed()`` returns immediately when
the DB already has rows or when it detects a non-default home).
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SEED_MARKER = ".silk_seed_v1"  # Written to silk dir after first seed run.


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _silk_db_path() -> Path:
    """Return the silk/history.db path, *without* triggering module import loops."""
    from . import storage as _storage
    d = _storage.home_dir() / "silk"
    d.mkdir(parents=True, exist_ok=True)
    return d / "history.db"


def _silk_dir() -> Path:
    from . import storage as _storage
    d = _storage.home_dir() / "silk"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _has_existing_runs() -> bool:
    db = _silk_db_path()
    if not db.exists():
        return False
    try:
        with sqlite3.connect(str(db)) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM silk_runs"
            ).fetchone()
            return bool(row and row[0] > 0)
    except sqlite3.OperationalError:
        # Table does not exist yet — DB is blank.
        return False


def _ts(days_ago: float, hour: int = 10, minute: int = 0) -> str:
    """Return an ISO-8601 UTC timestamp n days in the past."""
    base = datetime.now(tz=timezone.utc).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    return (base - timedelta(days=days_ago)).isoformat()


# ---------------------------------------------------------------------------
# Seed data definitions
# ---------------------------------------------------------------------------

# Stable UUIDs so idempotency is trivially checkable.
_RUN_IDS = [
    "a1b2c3d4-0001-0001-0001-000000000001",
    "a1b2c3d4-0001-0001-0001-000000000002",
    "a1b2c3d4-0001-0001-0001-000000000003",
    "a1b2c3d4-0001-0001-0001-000000000004",
    "a1b2c3d4-0001-0001-0001-000000000005",
    "a1b2c3d4-0001-0001-0001-000000000006",
    "a1b2c3d4-0001-0001-0001-000000000007",
    "a1b2c3d4-0001-0001-0001-000000000008",
    "a1b2c3d4-0001-0001-0001-000000000009",
    "a1b2c3d4-0001-0001-0001-000000000010",
]

_SPECS = [
    "tests/auth/login.spec.ts",
    "tests/auth/logout.spec.ts",
    "tests/dashboard/overview.spec.ts",
    "tests/dashboard/overview.spec.ts",
    "tests/checkout/payment-flow.spec.ts",
    "tests/checkout/payment-flow.spec.ts",
    "tests/profile/settings.spec.ts",
    "tests/a11y/homepage-axe.spec.ts",
    "tests/a11y/homepage-axe.spec.ts",
    "tests/auth/login.spec.ts",
]


def _make_json_report(
    spec_title: str,
    test_cases: list[dict],
    browser: str = "chromium",
) -> dict:
    """Build a minimal Playwright JSON report compatible with StepTimeline."""
    specs = []
    for tc in test_cases:
        specs.append({
            "title": tc["title"],
            "ok": tc.get("ok", True),
            "tests": [
                {
                    "status": "passed" if tc.get("ok", True) else "failed",
                    "results": [
                        {
                            "duration": tc.get("duration", 500),
                            **({"error": {"message": tc["error"]}} if not tc.get("ok", True) else {}),
                            "attachments": tc.get("attachments", []),
                        }
                    ],
                }
            ],
        })
    return {
        "stats": {
            "expected": sum(1 for t in test_cases if t.get("ok", True)),
            "unexpected": sum(1 for t in test_cases if not t.get("ok", True)),
            "skipped": 0,
            "duration": sum(t.get("duration", 500) for t in test_cases),
        },
        "suites": [
            {
                "title": spec_title,
                "specs": specs,
                "suites": [],
            }
        ],
    }


def _axe_attachment(violations: list[dict]) -> dict:
    """Build an axe-results.json attachment payload."""
    return {
        "name": "axe-results.json",
        "contentType": "application/json",
        "body": json.dumps({"violations": violations}),
    }


def _network_attachment(entries: list[dict]) -> dict:
    """Build a network.json HAR-style attachment payload."""
    return {
        "name": "network.json",
        "contentType": "application/json",
        "body": json.dumps({"log": {"entries": entries}}),
    }


# ---------------------------------------------------------------------------
# The actual seed rows
# ---------------------------------------------------------------------------

def _build_seed_runs() -> list[dict]:
    """Return ordered list of run dicts (newest first matches DB ordering)."""

    # Run 10 — today (just now): login.spec.ts, chromium, passed
    run10 = {
        "id": _RUN_IDS[9],
        "spec_path": "tests/auth/login.spec.ts",
        "exit_code": 0,
        "duration_ms": 3240,
        "started_at": _ts(0.02, hour=9, minute=15),
        "browsers": ["chromium"],
        "trace_path": None,
        "screenshot_paths": [],
        "a11y_violations_count": 0,
        "stderr_tail": "",
        "json_report": _make_json_report(
            "Login spec",
            [
                {"title": "displays login form", "ok": True, "duration": 480},
                {"title": "logs in with valid credentials", "ok": True, "duration": 1200},
                {"title": "shows error on invalid password", "ok": True, "duration": 860},
                {"title": "redirects to dashboard after login", "ok": True, "duration": 700},
            ],
        ),
    }

    # Run 9 — today: homepage a11y, chromium+firefox, passed with 2 a11y violations
    axe_violations = [
        {
            "id": "color-contrast",
            "impact": "serious",
            "description": "Elements must have sufficient color contrast",
            "nodes": [{"target": [".hero-subtitle"]}],
        },
        {
            "id": "image-alt",
            "impact": "critical",
            "description": "Images must have alternative text",
            "nodes": [{"target": ["img.logo"]}],
        },
    ]
    run9 = {
        "id": _RUN_IDS[8],
        "spec_path": "tests/a11y/homepage-axe.spec.ts",
        "exit_code": 0,
        "duration_ms": 5180,
        "started_at": _ts(0.1, hour=8, minute=42),
        "browsers": ["chromium", "firefox"],
        "trace_path": None,
        "screenshot_paths": [],
        "a11y_violations_count": 2,
        "stderr_tail": "",
        "json_report": _make_json_report(
            "Homepage accessibility audit",
            [
                {
                    "title": "homepage passes axe audit",
                    "ok": True,
                    "duration": 2100,
                    "attachments": [_axe_attachment(axe_violations)],
                },
                {"title": "nav links are keyboard-accessible", "ok": True, "duration": 880},
            ],
        ),
    }

    # Run 8 — yesterday: payment flow, chromium, FAILED (1 test failed)
    run8 = {
        "id": _RUN_IDS[7],
        "spec_path": "tests/checkout/payment-flow.spec.ts",
        "exit_code": 1,
        "duration_ms": 8650,
        "started_at": _ts(1.0, hour=16, minute=5),
        "browsers": ["chromium"],
        "trace_path": None,
        "screenshot_paths": [],
        "a11y_violations_count": 0,
        "stderr_tail": (
            "  1 failed\n"
            "  ● checkout › payment-flow › completes Stripe checkout\n"
            "\n"
            "    TimeoutError: waiting for selector '.stripe-success' failed\n"
            "    at Object.waitForSelector (playwright-core/lib/client/page.ts:123)\n"
            "    Expected: visible\n"
            "    Received: hidden after 10000ms"
        ),
        "json_report": _make_json_report(
            "Payment flow",
            [
                {"title": "loads checkout page", "ok": True, "duration": 920},
                {"title": "fills in card details", "ok": True, "duration": 1380},
                {
                    "title": "completes Stripe checkout",
                    "ok": False,
                    "duration": 10000,
                    "error": "TimeoutError: waiting for selector '.stripe-success' failed: timeout 10000ms exceeded",
                },
                {"title": "shows order confirmation", "ok": True, "duration": 350},
            ],
        ),
    }

    # Run 7 — yesterday: profile settings, chromium, passed
    run7 = {
        "id": _RUN_IDS[6],
        "spec_path": "tests/profile/settings.spec.ts",
        "exit_code": 0,
        "duration_ms": 4120,
        "started_at": _ts(1.0, hour=14, minute=22),
        "browsers": ["chromium"],
        "trace_path": None,
        "screenshot_paths": [],
        "a11y_violations_count": 0,
        "stderr_tail": "",
        "json_report": _make_json_report(
            "Profile settings",
            [
                {"title": "renders settings page", "ok": True, "duration": 610},
                {"title": "updates display name", "ok": True, "duration": 1050},
                {"title": "changes email address", "ok": True, "duration": 980},
                {"title": "saves notification preferences", "ok": True, "duration": 780},
            ],
        ),
    }

    # Run 6 — 2 days ago: payment flow, chromium+firefox+webkit, passed (after fix)
    run6 = {
        "id": _RUN_IDS[5],
        "spec_path": "tests/checkout/payment-flow.spec.ts",
        "exit_code": 0,
        "duration_ms": 22410,
        "started_at": _ts(2.0, hour=11, minute=30),
        "browsers": ["chromium", "firefox", "webkit"],
        "trace_path": None,
        "screenshot_paths": [],
        "a11y_violations_count": 0,
        "stderr_tail": "",
        "json_report": _make_json_report(
            "Payment flow (all browsers)",
            [
                {"title": "loads checkout page", "ok": True, "duration": 880},
                {"title": "fills in card details", "ok": True, "duration": 1220},
                {"title": "completes Stripe checkout", "ok": True, "duration": 2950},
                {"title": "shows order confirmation", "ok": True, "duration": 410},
            ],
        ),
    }

    # Run 5 — 3 days ago: dashboard, chromium+firefox, passed
    network_entries = [
        {"request": {"method": "GET", "url": "https://app.example.com/api/metrics"},
         "response": {"status": 200, "content": {"mimeType": "application/json"}}},
        {"request": {"method": "GET", "url": "https://app.example.com/api/notifications"},
         "response": {"status": 200, "content": {"mimeType": "application/json"}}},
        {"request": {"method": "POST", "url": "https://app.example.com/api/analytics/pageview"},
         "response": {"status": 204, "content": {"mimeType": "text/plain"}}},
    ]
    run5 = {
        "id": _RUN_IDS[4],
        "spec_path": "tests/dashboard/overview.spec.ts",
        "exit_code": 0,
        "duration_ms": 6730,
        "started_at": _ts(3.0, hour=10, minute=0),
        "browsers": ["chromium", "firefox"],
        "trace_path": None,
        "screenshot_paths": [],
        "a11y_violations_count": 0,
        "stderr_tail": "",
        "json_report": _make_json_report(
            "Dashboard overview",
            [
                {"title": "loads dashboard for authenticated user", "ok": True, "duration": 1100,
                 "attachments": [_network_attachment(network_entries)]},
                {"title": "displays metric cards", "ok": True, "duration": 640},
                {"title": "chart renders with data", "ok": True, "duration": 820},
                {"title": "notifications bell shows count", "ok": True, "duration": 390},
            ],
        ),
    }

    # Run 4 — 5 days ago: logout, chromium, passed
    run4 = {
        "id": _RUN_IDS[3],
        "spec_path": "tests/auth/logout.spec.ts",
        "exit_code": 0,
        "duration_ms": 2180,
        "started_at": _ts(5.0, hour=15, minute=48),
        "browsers": ["chromium"],
        "trace_path": None,
        "screenshot_paths": [],
        "a11y_violations_count": 0,
        "stderr_tail": "",
        "json_report": _make_json_report(
            "Logout flow",
            [
                {"title": "clicking logout clears session", "ok": True, "duration": 850},
                {"title": "redirects to login page", "ok": True, "duration": 620},
                {"title": "protected pages require re-login", "ok": True, "duration": 710},
            ],
        ),
    }

    # Run 3 — 7 days ago: dashboard, chromium, FAILED (2 tests)
    run3 = {
        "id": _RUN_IDS[2],
        "spec_path": "tests/dashboard/overview.spec.ts",
        "exit_code": 1,
        "duration_ms": 9200,
        "started_at": _ts(7.0, hour=9, minute=5),
        "browsers": ["chromium"],
        "trace_path": None,
        "screenshot_paths": [],
        "a11y_violations_count": 0,
        "stderr_tail": (
            "  2 failed\n"
            "  ● dashboard › chart renders with data\n"
            "    Error: expect(received).toBeVisible()\n"
            "    Expected: visible\n"
            "    Received: <div class='chart-container' style='display: none'>\n"
            "\n"
            "  ● dashboard › notifications bell shows count\n"
            "    Error: expected '0' to equal '3'"
        ),
        "json_report": _make_json_report(
            "Dashboard overview",
            [
                {"title": "loads dashboard for authenticated user", "ok": True, "duration": 980},
                {"title": "displays metric cards", "ok": True, "duration": 590},
                {
                    "title": "chart renders with data",
                    "ok": False,
                    "duration": 5000,
                    "error": "Error: expect(received).toBeVisible() — element not visible",
                },
                {
                    "title": "notifications bell shows count",
                    "ok": False,
                    "duration": 1200,
                    "error": "Error: expected '0' to equal '3'",
                },
            ],
        ),
    }

    # Run 2 — 10 days ago: a11y homepage, chromium, passed, 1 violation
    axe_violations_v2 = [
        {
            "id": "aria-required-attr",
            "impact": "critical",
            "description": "Required ARIA attributes must be provided",
            "nodes": [{"target": ["[role=progressbar]"]}],
        },
    ]
    run2 = {
        "id": _RUN_IDS[1],
        "spec_path": "tests/a11y/homepage-axe.spec.ts",
        "exit_code": 0,
        "duration_ms": 3870,
        "started_at": _ts(10.0, hour=11, minute=20),
        "browsers": ["chromium"],
        "trace_path": None,
        "screenshot_paths": [],
        "a11y_violations_count": 1,
        "stderr_tail": "",
        "json_report": _make_json_report(
            "Homepage accessibility audit",
            [
                {
                    "title": "homepage passes axe audit",
                    "ok": True,
                    "duration": 1800,
                    "attachments": [_axe_attachment(axe_violations_v2)],
                },
            ],
        ),
    }

    # Run 1 — 14 days ago: login, chromium, passed (baseline run)
    run1 = {
        "id": _RUN_IDS[0],
        "spec_path": "tests/auth/login.spec.ts",
        "exit_code": 0,
        "duration_ms": 3050,
        "started_at": _ts(14.0, hour=10, minute=0),
        "browsers": ["chromium"],
        "trace_path": None,
        "screenshot_paths": [],
        "a11y_violations_count": 0,
        "stderr_tail": "",
        "json_report": _make_json_report(
            "Login spec",
            [
                {"title": "displays login form", "ok": True, "duration": 420},
                {"title": "logs in with valid credentials", "ok": True, "duration": 1100},
                {"title": "shows error on invalid password", "ok": True, "duration": 790},
                {"title": "redirects to dashboard after login", "ok": True, "duration": 740},
            ],
        ),
    }

    # Return newest-first so INSERT order produces correct DESC ordering.
    return [run10, run9, run8, run7, run6, run5, run4, run3, run2, run1]


# ---------------------------------------------------------------------------
# Seed: spec files
# ---------------------------------------------------------------------------

_SPEC_SOURCES: dict[str, str] = {
    "tests/auth/login.spec.ts": """\
import { test, expect } from '@playwright/test';

test.describe('Login flow', () => {
  test('displays login form', async ({ page }) => {
    await page.goto('https://app.example.com/login');
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
  });

  test('logs in with valid credentials', async ({ page }) => {
    await page.goto('https://app.example.com/login');
    await page.getByLabel('Email').fill('alice@example.com');
    await page.getByLabel('Password').fill('correct-password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page).toHaveURL(/\\/dashboard/);
  });

  test('shows error on invalid password', async ({ page }) => {
    await page.goto('https://app.example.com/login');
    await page.getByLabel('Email').fill('alice@example.com');
    await page.getByLabel('Password').fill('wrong-password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page.getByTestId('error-banner')).toHaveText(/invalid credentials/i);
  });

  test('redirects to dashboard after login', async ({ page }) => {
    await page.goto('https://app.example.com/login?returnTo=/dashboard/analytics');
    await page.getByLabel('Email').fill('alice@example.com');
    await page.getByLabel('Password').fill('correct-password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page).toHaveURL(/\\/dashboard\\/analytics/);
  });
});
""",
    "tests/auth/logout.spec.ts": """\
import { test, expect } from '@playwright/test';

test.describe('Logout flow', () => {
  test('clicking logout clears session', async ({ page }) => {
    await page.goto('https://app.example.com/dashboard');
    await page.getByRole('button', { name: 'Account menu' }).click();
    await page.getByRole('menuitem', { name: 'Sign out' }).click();
    await expect(page).toHaveURL(/\\/login/);
  });

  test('redirects to login page', async ({ page }) => {
    await page.goto('https://app.example.com/login');
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });

  test('protected pages require re-login', async ({ page }) => {
    await page.goto('https://app.example.com/dashboard');
    await expect(page).toHaveURL(/\\/login/);
  });
});
""",
    "tests/dashboard/overview.spec.ts": """\
import { test, expect } from '@playwright/test';

test.describe('Dashboard overview', () => {
  test('loads dashboard for authenticated user', async ({ page }) => {
    await page.goto('https://app.example.com/dashboard');
    await expect(page.getByTestId('dashboard-root')).toBeVisible();
  });

  test('displays metric cards', async ({ page }) => {
    await page.goto('https://app.example.com/dashboard');
    await expect(page.getByTestId('metric-total-users')).toBeVisible();
    await expect(page.getByTestId('metric-revenue')).toBeVisible();
    await expect(page.getByTestId('metric-conversions')).toBeVisible();
  });

  test('chart renders with data', async ({ page }) => {
    await page.goto('https://app.example.com/dashboard');
    await expect(page.getByTestId('revenue-chart')).toBeVisible();
    const bars = page.locator('[data-testid="chart-bar"]');
    await expect(bars).toHaveCount(7);
  });

  test('notifications bell shows count', async ({ page }) => {
    await page.goto('https://app.example.com/dashboard');
    const badge = page.getByTestId('notification-badge');
    await expect(badge).toHaveText('3');
  });
});
""",
    "tests/checkout/payment-flow.spec.ts": """\
import { test, expect } from '@playwright/test';

test.describe('Payment flow', () => {
  test('loads checkout page', async ({ page }) => {
    await page.goto('https://app.example.com/checkout');
    await expect(page.getByRole('heading', { name: 'Checkout' })).toBeVisible();
    await expect(page.getByTestId('order-summary')).toBeVisible();
  });

  test('fills in card details', async ({ page }) => {
    await page.goto('https://app.example.com/checkout');
    const stripe = page.frameLocator('iframe[name="stripe-card"]');
    await stripe.getByPlaceholder('Card number').fill('4242 4242 4242 4242');
    await stripe.getByPlaceholder('MM / YY').fill('12 / 28');
    await stripe.getByPlaceholder('CVC').fill('123');
  });

  test('completes Stripe checkout', async ({ page }) => {
    await page.goto('https://app.example.com/checkout?demo=1');
    await page.getByRole('button', { name: 'Pay now' }).click();
    await expect(page.locator('.stripe-success')).toBeVisible({ timeout: 10_000 });
  });

  test('shows order confirmation', async ({ page }) => {
    await page.goto('https://app.example.com/checkout/confirmation');
    await expect(page.getByTestId('order-id')).toBeVisible();
    await expect(page.getByRole('heading', { name: /order confirmed/i })).toBeVisible();
  });
});
""",
    "tests/profile/settings.spec.ts": """\
import { test, expect } from '@playwright/test';

test.describe('Profile settings', () => {
  test('renders settings page', async ({ page }) => {
    await page.goto('https://app.example.com/settings');
    await expect(page.getByRole('heading', { name: 'Account settings' })).toBeVisible();
  });

  test('updates display name', async ({ page }) => {
    await page.goto('https://app.example.com/settings');
    await page.getByLabel('Display name').fill('Alice Doe');
    await page.getByRole('button', { name: 'Save changes' }).click();
    await expect(page.getByTestId('toast-success')).toHaveText(/saved/i);
  });

  test('changes email address', async ({ page }) => {
    await page.goto('https://app.example.com/settings');
    await page.getByLabel('Email').fill('alice.new@example.com');
    await page.getByRole('button', { name: 'Save changes' }).click();
    await expect(page.getByTestId('toast-success')).toBeVisible();
  });

  test('saves notification preferences', async ({ page }) => {
    await page.goto('https://app.example.com/settings/notifications');
    await page.getByLabel('Email digest').check();
    await page.getByRole('button', { name: 'Save' }).click();
    await expect(page.getByTestId('toast-success')).toBeVisible();
  });
});
""",
    "tests/a11y/homepage-axe.spec.ts": """\
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Homepage accessibility audit', () => {
  test('homepage passes axe audit', async ({ page }) => {
    await page.goto('https://app.example.com');
    const results = await new AxeBuilder({ page }).analyze();
    // Report violations as a JSON attachment for Silk's a11y tab.
    await test.info().attach('axe-results.json', {
      contentType: 'application/json',
      body: JSON.stringify({ violations: results.violations }),
    });
    // Check that no critical violations are present.
    const critical = results.violations.filter((v) => v.impact === 'critical');
    expect(critical).toHaveLength(0);
  });

  test('nav links are keyboard-accessible', async ({ page }) => {
    await page.goto('https://app.example.com');
    await page.keyboard.press('Tab');
    const focused = page.locator(':focus');
    await expect(focused).toHaveAttribute('href');
  });
});
""",
}


# ---------------------------------------------------------------------------
# Seed: collections (spec entries)
# ---------------------------------------------------------------------------

def _build_seed_collections() -> list[dict]:
    """Return a list of Collection JSON dicts to persist as files."""
    _coll_id = "b2c3d4e5-0001-0001-0001-000000000001"

    items = []
    for i, (spec_path, _) in enumerate(_SPEC_SOURCES.items()):
        # Create a playwright_spec entry for each spec file.
        items.append({
            "id": f"item-{i + 1:04d}-0001-0001-0001-000000000001",
            "name": spec_path.split("/")[-1],
            "is_folder": False,
            "kind": "playwright_spec",
            "spec_path": f"~/.theridion/silk/specs/{spec_path}",
            "method": None,
            "url": None,
            "headers": {},
            "body": None,
            "auth": None,
            "assertions": [],
            "pre_request_script": None,
            "post_response_script": None,
            "notes": None,
            "examples": [],
            "captures": [],
            "tags": ["e2e"],
            "items": [],
        })

    return [
        {
            "id": _coll_id,
            "name": "Example App — E2E Tests",
            "version": 1,
            "items": items,
            "variables": [
                {"name": "BASE_URL", "value": "https://app.example.com", "enabled": True},
                {"name": "TEST_USER", "value": "alice@example.com", "enabled": True},
            ],
        }
    ]


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def _write_silk_runs(runs: list[dict]) -> None:
    """Insert seed runs directly into SQLite (bypasses save_run to control started_at)."""
    from . import silk_storage as _ss

    # Ensure schema exists.
    conn = _ss._connect()
    conn.close()

    db = _silk_db_path()
    with sqlite3.connect(str(db)) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        for run in runs:
            report_json = json.dumps(run["json_report"]) if run.get("json_report") else None
            screenshots_json = json.dumps(run.get("screenshot_paths") or [])
            browsers_json = json.dumps(run.get("browsers") or ["chromium"])

            if run["exit_code"] == 0:
                status = "passed"
            elif run["exit_code"] == 1:
                status = "failed"
            else:
                status = "error"

            conn.execute(
                """
                INSERT OR IGNORE INTO silk_runs
                  (id, spec_path, status, duration_ms, started_at, browsers,
                   trace_path, screenshot_paths, a11y_violations_count,
                   stderr_tail, json_report)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run["id"],
                    run["spec_path"],
                    status,
                    run["duration_ms"],
                    run["started_at"],
                    browsers_json,
                    run.get("trace_path"),
                    screenshots_json,
                    run.get("a11y_violations_count", 0),
                    run.get("stderr_tail", ""),
                    report_json,
                ),
            )


def _write_spec_files(specs_dir: Path) -> None:
    """Write example spec files into ~/.theridion/silk/specs/."""
    for rel_path, source in _SPEC_SOURCES.items():
        dest = specs_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_text(source, encoding="utf-8")


def _write_collections(collections: list[dict]) -> None:
    """Write collection JSON files (only if the collection file does not exist)."""
    from . import storage as _storage
    import os
    import tempfile

    coll_dir = _storage.collections_dir()
    for coll in collections:
        dest = coll_dir / f"{coll['id']}.json"
        if dest.exists():
            continue
        # Atomic write.
        fd, tmp = tempfile.mkstemp(prefix=coll["id"] + ".", suffix=".json.tmp",
                                   dir=str(coll_dir))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(coll, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, dest)
        except Exception:
            try:
                Path(tmp).unlink(missing_ok=True)
            except OSError:
                pass
            raise


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def maybe_seed() -> None:
    """Seed local storage when empty.  Safe to call on every startup.

    Skips seeding when:
    - The silk DB already contains runs (idempotent guard).
    - The silk-seed marker file is present (belt-and-suspenders).
    """
    silk_dir = _silk_dir()
    marker = silk_dir / _SEED_MARKER

    if marker.exists():
        return  # Already seeded in a previous run.

    if _has_existing_runs():
        # DB already populated — write marker so we skip faster next time.
        marker.touch()
        return

    logger.info("theridion-eyes: seeding demo history data...")
    try:
        runs = _build_seed_runs()
        _write_silk_runs(runs)

        specs_dir = silk_dir / "specs"
        _write_spec_files(specs_dir)

        collections = _build_seed_collections()
        _write_collections(collections)

        marker.touch()
        logger.info("theridion-eyes: seed complete (%d runs, %d specs, %d collections).",
                    len(runs), len(_SPEC_SOURCES), len(collections))
    except Exception as exc:
        # Seed failures must never crash the sidecar.
        logger.warning("theridion-eyes: seed failed (non-fatal): %s", exc, exc_info=True)
