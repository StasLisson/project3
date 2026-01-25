from __future__ import annotations
import os
from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait



# Constant for fallback timeout
DEFAULT_TIMEOUT = 10


class BrowserWrapper:
    """
    Core UI engine for Selenium WebDriver management.

    Key QA Concepts Implemented:
    - Test Isolation: Manages browser lifecycle to ensure a clean state for every test.
    - Explicit Synchronization: Disables implicit waits in favor of deterministic `WebDriverWait`.
    - Stability over Cleverness: Encapsulates complex Selenium interactions into reliable, high-level methods.
    - Cross-Platform Compatibility: Configured for headless execution and CI/CD environments (Docker/Linux).
    """

    def __init__(self, *, headless: bool = False) -> None:
        """Initialize browser state and trigger driver creation."""
        self.headless = headless
        self.driver = self._create_driver()

    # ==========================================================
    # 1. BROWSER LIFECYCLE
    # ==========================================================

    def _create_driver(self) -> webdriver.Chrome:
        """
        Creates a Chrome instance with optimized arguments for stability and speed.
        Enforces 'No Sandbox' and 'Disable GPU' for dockerized CI/CD pipelines.
        """
        options = ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")

        # Support for custom binary locations (e.g., in specific CI agents)
        chrome_bin = os.environ.get("CHROME_BINARY")
        if chrome_bin:
            options.binary_location = chrome_bin

        driver = webdriver.Chrome(options=options)

        # QA Principle: Explicit Synchronization.
        # We disable implicit waits to avoid "ghost" behaviors and race conditions.
        driver.implicitly_wait(0)
        return driver

    def quit(self) -> None:
        """Terminate the browser session and release all system resources."""
        if self.driver:
            self.driver.quit()

    def close_browser(self) -> None:
        """Alias for session termination to match external framework calls."""
        self.quit()

    # ==========================================================
    # 2. NAVIGATION & FIXTURE SUPPORT
    # ==========================================================

    def get_driver(self, url: str) -> webdriver.Chrome:
        """
        Navigates to a URL and returns the driver instance.
        Used primarily by pytest fixtures to hand off control to Page Objects.
        """
        self.driver.get(url)
        return self.driver

    # ==========================================================
    # 3. SYNCHRONIZATION ENGINE
    # ==========================================================

    def wait_for_visible(self, locator: Tuple[str, str], timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        """
        Waits specifically for an element to be present in the DOM and visible on screen.
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def find_element(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """
        Standard explicit wait wrapper.
        Ensures elements are ready before interaction, reducing 'ElementNotInteractable' errors.
        """
        wait_time = timeout or DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(
            EC.visibility_of_element_located(locator)
        )

    def find_clickable(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """
        Waits for an element to be visible and enabled for user input.
        Critical for avoiding race conditions on buttons and inputs.
        """
        wait_time = timeout or DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable(locator)
        )

    # ==========================================================
    # 4. INTERACTION LOGIC
    # ==========================================================

    def click(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> None:
        """Safe click operation with pre-validation of element state."""
        element = self.find_clickable(locator, timeout)
        element.click()

    def type(self, locator: Tuple[str, str], text: str, clear: bool = True, timeout: Optional[int] = None) -> None:
        """Safe typing operation. Clears the field by default to ensure data integrity."""
        element = self.find_element(locator, timeout)
        if clear:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> str:
        """Extracts visible text content from a verified element."""
        element = self.find_element(locator, timeout)
        return element.text

    # ==========================================================
    # 5. ADVANCED OVERRIDES
    # ==========================================================

    def click_using_javascript(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> None:
        """
        Executes a force-click via JavaScript.
        Use Case: Bypassing UI overlays or difficult elements where standard Selenium click fails.
        """
        element = self.find_element(locator, timeout)
        self.driver.execute_script("arguments[0].click();", element)