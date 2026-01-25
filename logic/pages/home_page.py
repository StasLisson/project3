from __future__ import annotations
from logic.base_page import BasePage
from logic.locators import HomePageLocators


class HomePage(BasePage):
    """
    Page Object handling the Home Page feeds and navigation.

    Key QA Concepts Implemented:
    - Asynchronous UI Logic: Manages state transitions when switching feeds (API Fetch + DOM Render).
    - Inheritance: Inherits global navigation capabilities from BasePage while adding context-specific logic.
    """

    # ==========================================================
    # 1. FEED MANAGEMENT
    # ==========================================================

    def select_global_feed(self) -> None:
        """
        Switches to the 'Global Feed' tab.
        Includes a sync wait to allow the React application to fetch new data and update the DOM.
        """
        self.click(HomePageLocators.TAB_GLOBAL_FEED)
        self.handle_react_sync(1.5)

    def select_your_feed(self) -> None:
        """
        Switches to the personalized 'Your Feed'.
        Includes a sync wait for the authenticated API response and rendering.
        """
        self.click(HomePageLocators.TAB_YOUR_FEED)
        self.handle_react_sync(1.5)

    # ==========================================================
    # 2. QUICK NAVIGATION
    # ==========================================================

    def open(self) -> None:
        """
        Directly navigates to the application root URL.
        Useful for Sanity tests or resetting state.
        """
        self.navigate_to("")