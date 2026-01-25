from __future__ import annotations
import time
from typing import Tuple, Optional

from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from infra.browser_wrapper import BrowserWrapper
from infra.config import config
from logic.locators import BasePageLocators


class BasePage:
    """
    The root Page Object for the entire framework.

    Key QA Concepts Implemented:
    - Page Object Model (POM): Acts as the parent class for all pages, providing shared functionality.
    - DRY (Don't Repeat Yourself): Centralizes global interactions like Navbar navigation and Synchronization.
    - Facade Pattern: Wraps the underlying BrowserWrapper to provide a simplified interface for Page classes.
    """

    def __init__(self, browser: BrowserWrapper) -> None:
        """Initialize the page with the shared browser instance."""
        self.browser = browser
        # Direct driver access is preserved for edge cases (e.g., Alerts), but use with caution.
        self._driver = browser.driver

    def navigate_to(self, path: str = "") -> None:
        """
        Navigates to a specific path using the global base URL from configuration.
        Ensures clean URL construction (prevents double slashes).
        """
        target_url = f"{config.base_url.rstrip('/')}/{path.lstrip('/')}"
        self.browser.get_driver(target_url)

    # ==========================================================
    # GLOBAL NAVBAR ACTIONS
    # ==========================================================

    def logout(self) -> None:
        """Performs the logout sequence via the Navbar."""
        self.browser.click(BasePageLocators.NAV_USER_DROPDOWN)
        self.browser.click(BasePageLocators.NAV_LOGOUT)
        self.handle_react_sync(1.5)

    def is_user_logged_in(self) -> bool:
        """
        Checks if the user is logged in by verifying the visibility of the user dropdown.
        Returns False immediately if the element is not found within the timeout.
        """
        try:
            return self.browser.wait_for_visible(BasePageLocators.NAV_USER_DROPDOWN, timeout=5).is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def open_settings(self) -> None:
        """Navigates to the Settings page via Navbar interactions."""
        self.browser.click(BasePageLocators.NAV_USER_DROPDOWN)
        self.browser.click(BasePageLocators.NAV_SETTINGS)
        self.handle_react_sync(1.0)

    def open_profile(self) -> None:
        """Navigates to the User Profile page via Navbar interactions."""
        self.browser.click(BasePageLocators.NAV_USER_DROPDOWN)
        self.browser.click(BasePageLocators.NAV_PROFILE)
        self.handle_react_sync(1.0)

    # ==========================================================
    # INTERACTION WRAPPERS (Proxy Methods)
    # ==========================================================

    def find_element(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """Proxy for browser.find_element with BasePage context."""
        return self.browser.find_element(locator, timeout)

    def click(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> None:
        """Proxy for browser.click with BasePage context."""
        self.browser.click(locator, timeout)

    def type(self, locator: Tuple[str, str], text: str, clear: bool = True, timeout: Optional[int] = None) -> None:
        """Proxy for browser.type with BasePage context."""
        self.browser.type(locator, text, clear=clear, timeout=timeout)

    def get_text(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> str:
        """Proxy for browser.get_text with BasePage context."""
        return self.browser.get_text(locator, timeout)

    @staticmethod
    def handle_react_sync(duration: float = 1.0) -> None:
        """
        Heuristic Synchronization for React Virtual DOM.

        QA Concept - Stability:
        While typically discouraged, explicit sleeps are sometimes necessary in React apps
        when the DOM exists but the Virtual DOM is not yet ready to receive events,
        or during rapid state transitions where no visible element indicates completion.
        """
        time.sleep(duration)