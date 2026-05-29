"""Tests for silk_transpile — IR parser and framework transpilers.

Pure-function tests (no HTTP) plus one HTTP-level integration test that
exercises the Silk record/start wiring without spawning a real npx process.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("THERIDION_HOME", str(tmp_path))
    from theridion_sidecar.main import create_app

    return TestClient(create_app())


# ---------------------------------------------------------------------------
# Sample Playwright-test output used across tests
# ---------------------------------------------------------------------------

_SAMPLE_PW = """\
import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://example.com/');
  await page.getByRole('button', { name: 'Login' }).click();
  await page.getByLabel('Email').fill('a@b.com');
  await page.getByPlaceholder('Search').press('Enter');
  await page.getByRole('checkbox').check();
  await page.getByRole('checkbox').uncheck();
  await page.getByRole('combobox').selectOption('opt1');
  await expect(page.getByText('Welcome')).toBeVisible();
  await expect(page.getByText('Welcome')).toHaveText('Welcome');
  await expect(page).toHaveTitle(/Home/);
  await expect(page).toHaveURL('https://example.com/home');
});
"""

# ---------------------------------------------------------------------------
# 1. parse_playwright_spec
# ---------------------------------------------------------------------------


def test_parse_navigate() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec("  await page.goto('https://example.com/');\n")
    assert len(actions) == 1
    assert actions[0].kind == "navigate"
    assert actions[0].url == "https://example.com/"


def test_parse_click() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec(
        "  await page.getByRole('button', { name: 'Login' }).click();\n"
    )
    assert len(actions) == 1
    assert actions[0].kind == "click"
    assert actions[0].selector is not None
    assert "getByRole" in actions[0].selector


def test_parse_fill() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec("  await page.getByLabel('Email').fill('a@b.com');\n")
    assert len(actions) == 1
    assert actions[0].kind == "fill"
    assert actions[0].value == "a@b.com"


def test_parse_press() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec(
        "  await page.getByPlaceholder('Search').press('Enter');\n"
    )
    assert len(actions) == 1
    assert actions[0].kind == "press"
    assert actions[0].key == "Enter"


def test_parse_check() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec("  await page.getByRole('checkbox').check();\n")
    assert len(actions) == 1
    assert actions[0].kind == "check"


def test_parse_uncheck() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec("  await page.getByRole('checkbox').uncheck();\n")
    assert len(actions) == 1
    assert actions[0].kind == "uncheck"


def test_parse_select_option() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec(
        "  await page.getByRole('combobox').selectOption('opt1');\n"
    )
    assert len(actions) == 1
    assert actions[0].kind == "select"
    assert actions[0].value == "opt1"


def test_parse_assert_visible() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec(
        "  await expect(page.getByText('Welcome')).toBeVisible();\n"
    )
    assert len(actions) == 1
    assert actions[0].kind == "assert_visible"


def test_parse_assert_text() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec(
        "  await expect(page.getByText('Welcome')).toHaveText('Welcome');\n"
    )
    assert len(actions) == 1
    assert actions[0].kind == "assert_text"
    assert actions[0].value == "Welcome"


def test_parse_assert_title() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec("  await expect(page).toHaveTitle(/Home/);\n")
    assert len(actions) == 1
    assert actions[0].kind == "assert_title"
    assert actions[0].value == "Home"


def test_parse_assert_url() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec(
        "  await expect(page).toHaveURL('https://example.com/home');\n"
    )
    assert len(actions) == 1
    assert actions[0].kind == "assert_url"
    assert actions[0].url == "https://example.com/home"


def test_parse_full_sample_action_count() -> None:
    """Full sample yields the expected number of actions (no import/wrapper lines)."""
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    actions = parse_playwright_spec(_SAMPLE_PW)
    # navigate + click + fill + press + check + uncheck + select
    # + assert_visible + assert_text + assert_title + assert_url = 11
    assert len(actions) == 11


def test_parse_unknown_lines_skipped() -> None:
    """Unrecognised lines are silently ignored rather than causing an error."""
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    weird = "  // some comment\n  someUnknownCall();\n  await page.goto('http://x.com/');\n"
    actions = parse_playwright_spec(weird)
    assert len(actions) == 1
    assert actions[0].kind == "navigate"


def test_parse_empty_string_returns_empty_list() -> None:
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    assert parse_playwright_spec("") == []


# ---------------------------------------------------------------------------
# 2. Transpilers — idiom token checks
# ---------------------------------------------------------------------------


def _parsed() -> list:  # type: ignore[return]
    from theridion_sidecar.silk_transpile import parse_playwright_spec

    return parse_playwright_spec(_SAMPLE_PW)


def test_to_cypress_tokens() -> None:
    from theridion_sidecar.silk_transpile import to_cypress

    out = to_cypress(_parsed())
    assert "cy.visit(" in out
    assert "describe(" in out
    assert "it(" in out
    assert ".click()" in out
    assert ".clear().type(" in out
    assert "cy.title().should(" in out
    assert "cy.url().should(" in out


def test_to_cypress_leading_comment() -> None:
    from theridion_sidecar.silk_transpile import to_cypress

    out = to_cypress([])
    assert "Transpiled from Playwright recording" in out


def test_to_selenium_python_tokens() -> None:
    from theridion_sidecar.silk_transpile import to_selenium_python

    out = to_selenium_python(_parsed())
    assert "driver.get(" in out
    assert "send_keys" in out
    assert "def test_recorded" in out
    assert "driver.quit()" in out
    assert "is_displayed()" in out


def test_to_selenium_python_leading_comment() -> None:
    from theridion_sidecar.silk_transpile import to_selenium_python

    out = to_selenium_python([])
    assert "Transpiled from Playwright recording" in out


def test_to_selenium_java_tokens() -> None:
    from theridion_sidecar.silk_transpile import to_selenium_java

    out = to_selenium_java(_parsed())
    assert "WebDriver" in out
    assert "driver.get(" in out
    assert "ChromeDriver" in out
    assert "driver.quit()" in out
    assert "isDisplayed()" in out


def test_to_selenium_java_leading_comment() -> None:
    from theridion_sidecar.silk_transpile import to_selenium_java

    out = to_selenium_java([])
    assert "Transpiled from Playwright recording" in out


def test_to_webdriverio_tokens() -> None:
    from theridion_sidecar.silk_transpile import to_webdriverio

    out = to_webdriverio(_parsed())
    assert "browser.url(" in out
    assert "describe(" in out
    assert "it(" in out
    assert ".click()" in out
    assert "setValue(" in out
    assert "toBeDisplayed()" in out


def test_to_webdriverio_leading_comment() -> None:
    from theridion_sidecar.silk_transpile import to_webdriverio

    out = to_webdriverio([])
    assert "Transpiled from Playwright recording" in out


# ---------------------------------------------------------------------------
# 3. transpile() dispatch
# ---------------------------------------------------------------------------


def test_transpile_unknown_id_raises() -> None:
    from theridion_sidecar.silk_transpile import transpile

    with pytest.raises(ValueError, match="unsupported transpile target"):
        transpile("no-such-framework", [])


def test_transpile_cypress_dispatch() -> None:
    from theridion_sidecar.silk_transpile import transpile

    out = transpile("cypress", _parsed())
    assert "cy.visit(" in out


def test_transpile_selenium_python_dispatch() -> None:
    from theridion_sidecar.silk_transpile import transpile

    out = transpile("selenium-python", _parsed())
    assert "driver.get(" in out


def test_transpile_selenium_java_dispatch() -> None:
    from theridion_sidecar.silk_transpile import transpile

    out = transpile("selenium-java", _parsed())
    assert "WebDriver" in out


def test_transpile_webdriverio_dispatch() -> None:
    from theridion_sidecar.silk_transpile import transpile

    out = transpile("webdriverio", _parsed())
    assert "browser.url(" in out


# ---------------------------------------------------------------------------
# 4. transpile_playwright_spec() convenience wrapper
# ---------------------------------------------------------------------------


def test_transpile_playwright_spec_round_trip_cypress() -> None:
    from theridion_sidecar.silk_transpile import transpile_playwright_spec

    out = transpile_playwright_spec("cypress", _SAMPLE_PW)
    assert "cy.visit('https://example.com/')" in out
    assert "cy.title().should('include', 'Home')" in out


def test_transpile_playwright_spec_round_trip_selenium_python() -> None:
    from theridion_sidecar.silk_transpile import transpile_playwright_spec

    out = transpile_playwright_spec("selenium-python", _SAMPLE_PW)
    assert 'driver.get("https://example.com/")' in out


def test_transpile_playwright_spec_round_trip_selenium_java() -> None:
    from theridion_sidecar.silk_transpile import transpile_playwright_spec

    out = transpile_playwright_spec("selenium-java", _SAMPLE_PW)
    assert 'driver.get("https://example.com/")' in out


def test_transpile_playwright_spec_round_trip_webdriverio() -> None:
    from theridion_sidecar.silk_transpile import transpile_playwright_spec

    out = transpile_playwright_spec("webdriverio", _SAMPLE_PW)
    assert "browser.url('https://example.com/')" in out


# ---------------------------------------------------------------------------
# 5. Round-trip: action count reflected in output
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "framework_id", ["cypress", "selenium-python", "selenium-java", "webdriverio"]
)
def test_round_trip_action_count(framework_id: str) -> None:
    """Generated output must contain at least as many non-blank lines as there are actions."""
    from theridion_sidecar.silk_transpile import parse_playwright_spec, transpile

    actions = parse_playwright_spec(_SAMPLE_PW)
    out = transpile(framework_id, actions)
    non_blank = [ln for ln in out.splitlines() if ln.strip()]
    # Each action should produce at least one statement in the output.
    assert len(non_blank) >= len(actions), (
        f"{framework_id}: expected >= {len(actions)} non-blank lines, got {len(non_blank)}"
    )


# ---------------------------------------------------------------------------
# 6. HTTP-level wiring: record/start with cypress
#    (no real npx — mirrors test_silk.py mock pattern)
# ---------------------------------------------------------------------------


def test_record_start_cypress_framework_accepted(client: TestClient) -> None:
    """POST /api/silk/record/start with cypress is accepted (recordable_via_transpile).

    We mock asyncio.create_subprocess_exec to avoid spawning a real npx process.
    """
    mock_proc = MagicMock()
    mock_proc.returncode = None
    mock_proc.stdout = AsyncMock()

    with patch("shutil.which", return_value="/usr/bin/npx"), \
         patch(
             "asyncio.create_subprocess_exec",
             new_callable=lambda: lambda *a, **kw: _async_return(mock_proc),
         ):
        res = client.post(
            "/api/silk/record/start",
            json={"url": "http://localhost:3000", "framework": "cypress"},
        )

    assert res.status_code == 200, res.text
    data = res.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0


def _async_return(value: object):  # type: ignore[return]
    """Return a coroutine that resolves to *value*."""

    async def _inner(*args: object, **kwargs: object) -> object:
        return value

    return _inner()


def test_record_start_selenium_python_accepted(client: TestClient) -> None:
    """selenium-python is also recordable via transpile."""
    mock_proc = MagicMock()
    mock_proc.returncode = None
    mock_proc.stdout = AsyncMock()

    with patch("shutil.which", return_value="/usr/bin/npx"), \
         patch(
             "asyncio.create_subprocess_exec",
             new_callable=lambda: lambda *a, **kw: _async_return(mock_proc),
         ):
        res = client.post(
            "/api/silk/record/start",
            json={"url": "http://localhost:3000", "framework": "selenium-python"},
        )

    assert res.status_code == 200, res.text


def test_record_start_webdriverio_accepted(client: TestClient) -> None:
    """webdriverio is also recordable via transpile."""
    mock_proc = MagicMock()
    mock_proc.returncode = None
    mock_proc.stdout = AsyncMock()

    with patch("shutil.which", return_value="/usr/bin/npx"), \
         patch(
             "asyncio.create_subprocess_exec",
             new_callable=lambda: lambda *a, **kw: _async_return(mock_proc),
         ):
        res = client.post(
            "/api/silk/record/start",
            json={"url": "http://localhost:3000", "framework": "webdriverio"},
        )

    assert res.status_code == 200, res.text


# ---------------------------------------------------------------------------
# 7. Frameworks endpoint exposes recordable_via_transpile
# ---------------------------------------------------------------------------


def test_frameworks_exposes_recordable_via_transpile(client: TestClient) -> None:
    """GET /api/silk/frameworks includes recordable_via_transpile field for cypress."""
    res = client.get("/api/silk/frameworks")
    assert res.status_code == 200
    fws = {fw["id"]: fw for fw in res.json()["frameworks"]}
    for fw_id in ("cypress", "selenium-python", "selenium-java", "webdriverio"):
        assert fw_id in fws, f"{fw_id} missing from framework list"
        assert fws[fw_id]["recordable_via_transpile"] is True, (
            f"{fw_id} should have recordable_via_transpile=True"
        )
        assert fws[fw_id]["recordable"] is True, f"{fw_id} should be recordable"


def test_frameworks_native_playwright_not_transpile(client: TestClient) -> None:
    """Native Playwright frameworks have recordable_via_transpile=False."""
    res = client.get("/api/silk/frameworks")
    assert res.status_code == 200
    fws = {fw["id"]: fw for fw in res.json()["frameworks"]}
    assert fws["playwright-ts"]["recordable_via_transpile"] is False
    assert fws["playwright-ts"]["recordable"] is True


# ---------------------------------------------------------------------------
# 8. RecordedAction is frozen (immutable)
# ---------------------------------------------------------------------------


def test_recorded_action_is_frozen() -> None:
    from theridion_sidecar.silk_transpile import RecordedAction

    action = RecordedAction(kind="navigate", url="https://example.com")
    with pytest.raises((AttributeError, TypeError)):
        action.url = "https://other.com"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 9. Locator conversion spot-checks
# ---------------------------------------------------------------------------


def test_cypress_getby_label_uses_aria_label() -> None:
    from theridion_sidecar.silk_transpile import RecordedAction, to_cypress

    actions = [RecordedAction(kind="click", selector="getByLabel('Email')")]
    out = to_cypress(actions)
    assert "aria-label" in out


def test_selenium_python_getby_text_uses_xpath() -> None:
    from theridion_sidecar.silk_transpile import RecordedAction, to_selenium_python

    actions = [RecordedAction(kind="click", selector="getByText('Submit')")]
    out = to_selenium_python(actions)
    assert "normalize-space" in out


def test_wdio_getby_role_name_uses_text_strategy() -> None:
    from theridion_sidecar.silk_transpile import RecordedAction, to_webdriverio

    actions = [
        RecordedAction(kind="click", selector="getByRole('button', { name: 'Save' })")
    ]
    out = to_webdriverio(actions)
    assert "'=Save'" in out


def test_selenium_java_getby_placeholder() -> None:
    from theridion_sidecar.silk_transpile import RecordedAction, to_selenium_java

    actions = [RecordedAction(kind="fill", selector="getByPlaceholder('Search')", value="hello")]
    out = to_selenium_java(actions)
    assert "placeholder" in out
