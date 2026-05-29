"""silk_transpile — Framework-agnostic IR + transpilers for Playwright codegen output.

Converts ``playwright codegen --target=playwright-test`` TypeScript output into
Cypress, Selenium-Python, Selenium-Java, and WebdriverIO specs.

All functions are pure (no I/O, no FastAPI) so they are trivially unit-testable.

Transpiled code is a *strong starting point* — locator conversion is best-effort
and the result may need manual touch-up before it runs against a real project.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# IR
# ---------------------------------------------------------------------------

_SUPPORTED_KINDS = frozenset(
    {
        "navigate",
        "click",
        "fill",
        "press",
        "check",
        "uncheck",
        "select",
        "assert_visible",
        "assert_text",
        "assert_title",
        "assert_url",
    }
)


@dataclass(frozen=True)
class RecordedAction:
    """Framework-agnostic representation of a single recorded browser action."""

    kind: str
    selector: str | None = None  # Raw Playwright locator expression, e.g. getByRole(...)
    value: str | None = None  # Fill text, pressed key, assertion value
    url: str | None = None  # navigate / assert_url
    key: str | None = None  # press key name


# ---------------------------------------------------------------------------
# Parser: Playwright-test TypeScript → list[RecordedAction]
# ---------------------------------------------------------------------------

# Matches:  await page.goto('https://...');
_GOTO_RE = re.compile(r"await page\.goto\(['\"]([^'\"]+)['\"]\)")

# Matches:  await page.<locator_chain>.click();
# Captures the locator chain (everything between page. and the final .action())
_PAGE_ACTION_RE = re.compile(
    r"await page\.(?P<locator>.+?)\.(?P<action>click|fill|press|check|uncheck|selectOption)"
    r"\((?P<args>.*?)\);?\s*$"
)

# Matches: await expect(page.getByXxx(...)).toBeVisible();
_EXPECT_LOCATOR_RE = re.compile(
    r"await expect\(page\.(?P<locator>[^\)]+(?:\([^)]*\))*)\)"
    r"\.(?P<assertion>toBeVisible|toHaveText|toContainText)\((?P<args>.*?)\)"
)

# Matches: await expect(page).toHaveTitle(...) / toHaveURL(...)
_EXPECT_PAGE_RE = re.compile(
    r"await expect\(page\)\.(?P<assertion>toHaveTitle|toHaveURL)\((?P<args>.*?)\)"
)

# For extracting a string value from JS args like ('foo') or ("foo") or (/re/)
_QUOTED_STR_RE = re.compile(r"""['"](.*?)['"]""")
_REGEX_LITERAL_RE = re.compile(r"/(.+?)/[gimsuy]*")


def _extract_string(args: str) -> str | None:
    """Extract first quoted or regex string from an argument substring."""
    m = _QUOTED_STR_RE.search(args)
    if m:
        return m.group(1)
    m = _REGEX_LITERAL_RE.search(args)
    if m:
        return m.group(1)
    return None


def _parse_line(line: str) -> RecordedAction | None:
    """Parse a single codegen output line into a RecordedAction, or None to skip."""
    line = line.strip()

    # navigate
    m = _GOTO_RE.search(line)
    if m:
        return RecordedAction(kind="navigate", url=m.group(1))

    # assert on page (title / url)
    m = _EXPECT_PAGE_RE.search(line)
    if m:
        assertion = m.group("assertion")
        val = _extract_string(m.group("args"))
        if assertion == "toHaveTitle":
            return RecordedAction(kind="assert_title", value=val)
        if assertion == "toHaveURL":
            return RecordedAction(kind="assert_url", url=val)

    # assert on locator (visible / text)
    m = _EXPECT_LOCATOR_RE.search(line)
    if m:
        locator = m.group("locator")
        assertion = m.group("assertion")
        if assertion == "toBeVisible":
            return RecordedAction(kind="assert_visible", selector=locator)
        if assertion in ("toHaveText", "toContainText"):
            val = _extract_string(m.group("args"))
            return RecordedAction(kind="assert_text", selector=locator, value=val)

    # page.locator.action
    m = _PAGE_ACTION_RE.search(line)
    if m:
        locator = m.group("locator")
        action = m.group("action")
        args = m.group("args")
        if action == "click":
            return RecordedAction(kind="click", selector=locator)
        if action == "fill":
            val = _extract_string(args)
            return RecordedAction(kind="fill", selector=locator, value=val or "")
        if action == "press":
            key = _extract_string(args)
            return RecordedAction(kind="press", selector=locator, key=key)
        if action == "check":
            return RecordedAction(kind="check", selector=locator)
        if action == "uncheck":
            return RecordedAction(kind="uncheck", selector=locator)
        if action == "selectOption":
            val = _extract_string(args)
            return RecordedAction(kind="select", selector=locator, value=val or "")

    return None


def parse_playwright_spec(code: str) -> list[RecordedAction]:
    """Parse ``playwright codegen --target=playwright-test`` output into IR.

    Unknown / unrecognised lines are silently skipped rather than raising.
    """
    actions: list[RecordedAction] = []
    for line in code.splitlines():
        action = _parse_line(line)
        if action is not None:
            actions.append(action)
    return actions


# ---------------------------------------------------------------------------
# Locator helpers shared across transpilers
# ---------------------------------------------------------------------------

# Patterns for extracting semantic info from Playwright locator expressions
_GETBY_ROLE_NAME_RE = re.compile(
    r"getByRole\(['\"]([^'\"]+)['\"].*?name['\"]?\s*:\s*['\"]([^'\"]+)['\"]", re.DOTALL
)
_GETBY_TEXT_RE = re.compile(r"getByText\(['\"]([^'\"]+)['\"]\)")
_GETBY_LABEL_RE = re.compile(r"getByLabel\(['\"]([^'\"]+)['\"]\)")
_GETBY_PLACEHOLDER_RE = re.compile(r"getByPlaceholder\(['\"]([^'\"]+)['\"]\)")
_GETBY_TESTID_RE = re.compile(r"getByTestId\(['\"]([^'\"]+)['\"]\)")
_GETBY_ROLE_ONLY_RE = re.compile(r"getByRole\(['\"]([^'\"]+)['\"]")


def _locator_to_cypress(locator: str | None) -> str:
    """Best-effort conversion of a Playwright locator to a Cypress chain start."""
    if not locator:
        return "cy.get('body')"

    m = _GETBY_ROLE_NAME_RE.search(locator)
    if m:
        return f"cy.contains('{m.group(2)}')"

    m = _GETBY_TEXT_RE.search(locator)
    if m:
        return f"cy.contains('{m.group(1)}')"

    m = _GETBY_LABEL_RE.search(locator)
    if m:
        return f"cy.get('[aria-label=\"{m.group(1)}\"]')"

    m = _GETBY_PLACEHOLDER_RE.search(locator)
    if m:
        return f"cy.get('[placeholder=\"{m.group(1)}\"]')"

    m = _GETBY_TESTID_RE.search(locator)
    if m:
        return f"cy.get('[data-testid=\"{m.group(1)}\"]')"

    m = _GETBY_ROLE_ONLY_RE.search(locator)
    if m:
        return f"cy.get('[role=\"{m.group(1)}\"]')"

    # Fallback: wrap raw locator in a comment
    return f"cy.get(/* {locator} */ 'body')"


def _locator_to_selenium_py(locator: str | None) -> str:
    """Return (By.XXX, 'value') expression string for Selenium-Python."""
    if not locator:
        return "(By.TAG_NAME, 'body')"

    m = _GETBY_ROLE_NAME_RE.search(locator)
    if m:
        name = m.group(2).replace("'", "\\'")
        return f"(By.XPATH, \"//*[normalize-space(text())='{name}']\")"

    m = _GETBY_TEXT_RE.search(locator)
    if m:
        text = m.group(1).replace("'", "\\'")
        return f"(By.XPATH, \"//*[normalize-space(text())='{text}']\")"

    m = _GETBY_LABEL_RE.search(locator)
    if m:
        label = m.group(1).replace('"', '\\"')
        return f"(By.CSS_SELECTOR, '[aria-label=\"{label}\"]')"

    m = _GETBY_PLACEHOLDER_RE.search(locator)
    if m:
        ph = m.group(1).replace('"', '\\"')
        return f"(By.CSS_SELECTOR, '[placeholder=\"{ph}\"]')"

    m = _GETBY_TESTID_RE.search(locator)
    if m:
        tid = m.group(1).replace('"', '\\"')
        return f"(By.CSS_SELECTOR, '[data-testid=\"{tid}\"]')"

    m = _GETBY_ROLE_ONLY_RE.search(locator)
    if m:
        role = m.group(1).replace('"', '\\"')
        return f"(By.CSS_SELECTOR, '[role=\"{role}\"]')"

    return "(By.TAG_NAME, 'body')  # TODO: refine locator"


def _locator_to_selenium_java(locator: str | None) -> str:
    """Return By.xxx(...) expression for Selenium Java."""
    if not locator:
        return 'By.tagName("body")'

    m = _GETBY_ROLE_NAME_RE.search(locator)
    if m:
        name = m.group(2).replace('"', '\\"')
        return f'By.xpath("//*[normalize-space(text())=\\"{name}\\"]")'

    m = _GETBY_TEXT_RE.search(locator)
    if m:
        text = m.group(1).replace('"', '\\"')
        return f'By.xpath("//*[normalize-space(text())=\\"{text}\\"]")'

    m = _GETBY_LABEL_RE.search(locator)
    if m:
        label = m.group(1).replace('"', '\\"')
        return f'By.cssSelector("[aria-label=\\"{label}\\"]")'

    m = _GETBY_PLACEHOLDER_RE.search(locator)
    if m:
        ph = m.group(1).replace('"', '\\"')
        return f'By.cssSelector("[placeholder=\\"{ph}\\"]")'

    m = _GETBY_TESTID_RE.search(locator)
    if m:
        tid = m.group(1).replace('"', '\\"')
        return f'By.cssSelector("[data-testid=\\"{tid}\\"]")'

    m = _GETBY_ROLE_ONLY_RE.search(locator)
    if m:
        role = m.group(1).replace('"', '\\"')
        return f'By.cssSelector("[role=\\"{role}\\"]")'

    return 'By.tagName("body") // TODO: refine locator'


def _locator_to_wdio(locator: str | None) -> str:
    """Return a WebdriverIO selector string (CSS / text strategy)."""
    if not locator:
        return "'body'"

    m = _GETBY_ROLE_NAME_RE.search(locator)
    if m:
        return f"'={m.group(2)}'"

    m = _GETBY_TEXT_RE.search(locator)
    if m:
        return f"'={m.group(1)}'"

    m = _GETBY_LABEL_RE.search(locator)
    if m:
        label = m.group(1).replace("'", "\\'")
        return f"'[aria-label=\"{label}\"]'"

    m = _GETBY_PLACEHOLDER_RE.search(locator)
    if m:
        ph = m.group(1).replace("'", "\\'")
        return f"'[placeholder=\"{ph}\"]'"

    m = _GETBY_TESTID_RE.search(locator)
    if m:
        tid = m.group(1).replace("'", "\\'")
        return f"'[data-testid=\"{tid}\"]'"

    m = _GETBY_ROLE_ONLY_RE.search(locator)
    if m:
        role = m.group(1).replace("'", "\\'")
        return f"'[role=\"{role}\"]'"

    return "'body' /* TODO: refine locator */"


# ---------------------------------------------------------------------------
# Transpilers
# ---------------------------------------------------------------------------

_TRANSPILE_HEADER_CYPRESS = (
    "// Transpiled from Playwright recording — may need manual touch-up.\n"
)
_TRANSPILE_HEADER_PY = (
    "# Transpiled from Playwright recording — may need manual touch-up.\n"
)
_TRANSPILE_HEADER_JAVA = (
    "// Transpiled from Playwright recording — may need manual touch-up.\n"
)
_TRANSPILE_HEADER_WDIO = (
    "// Transpiled from Playwright recording — may need manual touch-up.\n"
)


def to_cypress(actions: list[RecordedAction]) -> str:
    """Emit a Cypress describe/it block from IR actions."""
    lines: list[str] = [
        _TRANSPILE_HEADER_CYPRESS,
        "describe('recorded test', () => {",
        "  it('plays back recording', () => {",
    ]

    for action in actions:
        if action.kind == "navigate":
            lines.append(f"    cy.visit('{action.url}');")
        elif action.kind == "click":
            cy = _locator_to_cypress(action.selector)
            lines.append(f"    {cy}.click();")
        elif action.kind == "fill":
            cy = _locator_to_cypress(action.selector)
            val = (action.value or "").replace("'", "\\'")
            lines.append(f"    {cy}.clear().type('{val}');")
        elif action.kind == "press":
            cy = _locator_to_cypress(action.selector)
            key = action.key or ""
            if key.lower() == "enter":
                lines.append(f"    {cy}.type('{{enter}}');")
            else:
                lines.append(f"    {cy}.type('{{{key}}}');")
        elif action.kind == "check":
            cy = _locator_to_cypress(action.selector)
            lines.append(f"    {cy}.check();")
        elif action.kind == "uncheck":
            cy = _locator_to_cypress(action.selector)
            lines.append(f"    {cy}.uncheck();")
        elif action.kind == "select":
            cy = _locator_to_cypress(action.selector)
            val = action.value or ""
            lines.append(f"    {cy}.select('{val}');")
        elif action.kind == "assert_visible":
            cy = _locator_to_cypress(action.selector)
            lines.append(f"    {cy}.should('be.visible');")
        elif action.kind == "assert_text":
            cy = _locator_to_cypress(action.selector)
            val = action.value or ""
            lines.append(f"    {cy}.should('contain.text', '{val}');")
        elif action.kind == "assert_title":
            val = action.value or ""
            lines.append(f"    cy.title().should('include', '{val}');")
        elif action.kind == "assert_url":
            url = action.url or ""
            lines.append(f"    cy.url().should('include', '{url}');")

    lines += ["  });", "});", ""]
    return "\n".join(lines)


def to_selenium_python(actions: list[RecordedAction]) -> str:
    """Emit a pytest function using selenium.webdriver + By from IR actions."""
    lines: list[str] = [
        _TRANSPILE_HEADER_PY,
        "from selenium import webdriver",
        "from selenium.webdriver.common.by import By",
        "from selenium.webdriver.common.keys import Keys",
        "",
        "",
        "def test_recorded() -> None:",
        "    driver = webdriver.Chrome()",
        "    try:",
    ]

    for action in actions:
        if action.kind == "navigate":
            lines.append(f'        driver.get("{action.url}")')
        elif action.kind == "click":
            by = _locator_to_selenium_py(action.selector)
            lines.append(f"        driver.find_element{by}.click()")
        elif action.kind == "fill":
            by = _locator_to_selenium_py(action.selector)
            val = (action.value or "").replace('"', '\\"')
            lines.append(f'        el = driver.find_element{by}')
            lines.append("        el.clear()")
            lines.append(f'        el.send_keys("{val}")')
        elif action.kind == "press":
            by = _locator_to_selenium_py(action.selector)
            key = (action.key or "").upper()
            lines.append(f"        driver.find_element{by}.send_keys(Keys.{key})")
        elif action.kind == "check":
            by = _locator_to_selenium_py(action.selector)
            lines.append(f"        el = driver.find_element{by}")
            lines.append("        if not el.is_selected():")
            lines.append("            el.click()")
        elif action.kind == "uncheck":
            by = _locator_to_selenium_py(action.selector)
            lines.append(f"        el = driver.find_element{by}")
            lines.append("        if el.is_selected():")
            lines.append("            el.click()")
        elif action.kind == "select":
            by = _locator_to_selenium_py(action.selector)
            val = (action.value or "").replace('"', '\\"')
            lines.append("        from selenium.webdriver.support.ui import Select")
            lines.append(f'        Select(driver.find_element{by}).select_by_visible_text("{val}")')
        elif action.kind == "assert_visible":
            by = _locator_to_selenium_py(action.selector)
            lines.append(f"        assert driver.find_element{by}.is_displayed()")
        elif action.kind == "assert_text":
            by = _locator_to_selenium_py(action.selector)
            val = action.value or ""
            lines.append(f'        assert "{val}" in driver.find_element{by}.text')
        elif action.kind == "assert_title":
            val = action.value or ""
            lines.append(f'        assert "{val}" in driver.title')
        elif action.kind == "assert_url":
            url = action.url or ""
            lines.append(f'        assert "{url}" in driver.current_url')

    lines += [
        "    finally:",
        "        driver.quit()",
        "",
    ]
    return "\n".join(lines)


def to_selenium_java(actions: list[RecordedAction]) -> str:
    """Emit a JUnit 5 class using Selenium WebDriver + By from IR actions."""
    body: list[str] = []

    for action in actions:
        if action.kind == "navigate":
            body.append(f'        driver.get("{action.url}");')
        elif action.kind == "click":
            by = _locator_to_selenium_java(action.selector)
            body.append(f"        driver.findElement({by}).click();")
        elif action.kind == "fill":
            by = _locator_to_selenium_java(action.selector)
            val = (action.value or "").replace('"', '\\"')
            body.append(f"        WebElement el = driver.findElement({by});")
            body.append("        el.clear();")
            body.append(f'        el.sendKeys("{val}");')
        elif action.kind == "press":
            by = _locator_to_selenium_java(action.selector)
            key = (action.key or "").upper()
            body.append(f"        driver.findElement({by}).sendKeys(Keys.{key});")
        elif action.kind == "check":
            by = _locator_to_selenium_java(action.selector)
            body.append(f"        WebElement cb = driver.findElement({by});")
            body.append("        if (!cb.isSelected()) cb.click();")
        elif action.kind == "uncheck":
            by = _locator_to_selenium_java(action.selector)
            body.append(f"        WebElement cb = driver.findElement({by});")
            body.append("        if (cb.isSelected()) cb.click();")
        elif action.kind == "select":
            by = _locator_to_selenium_java(action.selector)
            val = (action.value or "").replace('"', '\\"')
            sel_stmt = f'new Select(driver.findElement({by})).selectByVisibleText("{val}");'
            body.append(f"        {sel_stmt}")
        elif action.kind == "assert_visible":
            by = _locator_to_selenium_java(action.selector)
            body.append(f"        assertTrue(driver.findElement({by}).isDisplayed());")
        elif action.kind == "assert_text":
            by = _locator_to_selenium_java(action.selector)
            val = (action.value or "").replace('"', '\\"')
            text_stmt = f'driver.findElement({by}).getText().contains("{val}")'
            body.append(f"        assertTrue({text_stmt});")
        elif action.kind == "assert_title":
            val = (action.value or "").replace('"', '\\"')
            body.append(f'        assertTrue(driver.getTitle().contains("{val}"));')
        elif action.kind == "assert_url":
            url = (action.url or "").replace('"', '\\"')
            body.append(f'        assertTrue(driver.getCurrentUrl().contains("{url}"));')

    lines: list[str] = [
        _TRANSPILE_HEADER_JAVA,
        "import org.openqa.selenium.By;",
        "import org.openqa.selenium.Keys;",
        "import org.openqa.selenium.WebDriver;",
        "import org.openqa.selenium.WebElement;",
        "import org.openqa.selenium.chrome.ChromeDriver;",
        "import org.openqa.selenium.support.ui.Select;",
        "import org.junit.jupiter.api.*;",
        "import static org.junit.jupiter.api.Assertions.*;",
        "",
        "public class RecordedTest {",
        "    @Test",
        "    void recordedTest() {",
        "        WebDriver driver = new ChromeDriver();",
        "        try {",
        *body,
        "        } finally {",
        "            driver.quit();",
        "        }",
        "    }",
        "}",
        "",
    ]
    return "\n".join(lines)


def to_webdriverio(actions: list[RecordedAction]) -> str:
    """Emit a WebdriverIO describe/it block from IR actions."""
    lines: list[str] = [
        _TRANSPILE_HEADER_WDIO,
        "describe('recorded test', () => {",
        "  it('plays back recording', async () => {",
    ]

    for action in actions:
        if action.kind == "navigate":
            lines.append(f"    await browser.url('{action.url}');")
        elif action.kind == "click":
            sel = _locator_to_wdio(action.selector)
            lines.append(f"    await $({sel}).click();")
        elif action.kind == "fill":
            sel = _locator_to_wdio(action.selector)
            val = (action.value or "").replace("'", "\\'")
            lines.append(f"    await $({sel}).setValue('{val}');")
        elif action.kind == "press":
            sel = _locator_to_wdio(action.selector)
            key = action.key or ""
            lines.append(f"    await $({sel}).keys(['{key}']);")
        elif action.kind == "check":
            sel = _locator_to_wdio(action.selector)
            lines.append(f"    await $({sel}).click(); // check")
        elif action.kind == "uncheck":
            sel = _locator_to_wdio(action.selector)
            lines.append(f"    await $({sel}).click(); // uncheck")
        elif action.kind == "select":
            sel = _locator_to_wdio(action.selector)
            val = (action.value or "").replace("'", "\\'")
            lines.append(f"    await $({sel}).selectByVisibleText('{val}');")
        elif action.kind == "assert_visible":
            sel = _locator_to_wdio(action.selector)
            lines.append(f"    await expect($({sel})).toBeDisplayed();")
        elif action.kind == "assert_text":
            sel = _locator_to_wdio(action.selector)
            val = (action.value or "").replace("'", "\\'")
            lines.append(f"    await expect($({sel})).toHaveText('{val}');")
        elif action.kind == "assert_title":
            val = (action.value or "").replace("'", "\\'")
            title_stmt = f"expect.stringContaining('{val}')"
            lines.append(f"    await expect(browser).toHaveTitle({title_stmt});")
        elif action.kind == "assert_url":
            url = (action.url or "").replace("'", "\\'")
            lines.append(f"    await expect(browser).toHaveUrl(expect.stringContaining('{url}'));")

    lines += ["  });", "});", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_TRANSPILERS = {
    "cypress": to_cypress,
    "selenium-python": to_selenium_python,
    "selenium-java": to_selenium_java,
    "webdriverio": to_webdriverio,
}

#: IDs of frameworks that are recordable via Playwright → transpile pipeline.
TRANSPILE_FRAMEWORK_IDS: frozenset[str] = frozenset(_TRANSPILERS)


def transpile(framework_id: str, actions: list[RecordedAction]) -> str:
    """Dispatch to the correct transpiler by framework id.

    Raises:
        ValueError: when *framework_id* is not a known transpile target.
    """
    fn = _TRANSPILERS.get(framework_id)
    if fn is None:
        raise ValueError(
            f"unsupported transpile target {framework_id!r}; "
            f"expected one of {sorted(_TRANSPILERS)}"
        )
    return fn(actions)


def transpile_playwright_spec(framework_id: str, pw_code: str) -> str:
    """Parse Playwright-test TypeScript then transpile to *framework_id*.

    Convenience wrapper around :func:`parse_playwright_spec` + :func:`transpile`.
    """
    actions = parse_playwright_spec(pw_code)
    return transpile(framework_id, actions)
