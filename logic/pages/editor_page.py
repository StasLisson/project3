from __future__ import annotations
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from logic.base_page import BasePage
from logic.locators import EditorPageLocators


class EditorPage(BasePage):
    """
    Page Object handling the Article Editor lifecycle (Create/Update).

    Key QA Concepts Implemented:
    - Field Mapping: Ensures UI inputs strictly map to the backend data model.
    - React Resilience: Implements 'Brute Force' strategies to handle Virtual DOM lag in input fields.
    - Atomic State Handling: Verifies specific DOM states (e.g., empty field) before injecting new data.
    """

    # ==========================================================
    # 1. CORE ARTICLE INPUTS
    # ==========================================================

    def fill_title(self, title: str) -> None:
        """Input text into the article title field."""
        self.type(EditorPageLocators.TITLE_INPUT, title)

    def fill_description(self, description: str) -> None:
        """Input text into the article description (About) field."""
        self.type(EditorPageLocators.ABOUT_INPUT, description)

    def fill_body(self, body: str) -> None:
        """Input the main content into the article body textarea."""
        self.type(EditorPageLocators.BODY_INPUT, body)

    def fill_tags(self, tags: str) -> None:
        """Input tags into the specialized tag field."""
        self.type(EditorPageLocators.TAGS_INPUT, tags)

    def publish_article(self) -> None:
        """
        Submits the article.
        Uses a JavaScript click to bypass potential React overlays or animation lags on the button.
        """
        self.browser.click_using_javascript(EditorPageLocators.PUBLISH_BTN)
        # Internal sync point: waits for the redirect to the article view to complete
        self.handle_react_sync(1.5)

    # ==========================================================
    # 2. STABLE UPDATE METHODS
    # ==========================================================

    def brute_force_update_title(self, new_title: str) -> None:
        """
        Aggressively clears and verifies the title field to ensure React state synchronization.

        QA Concept - Determinism:
        Standard .clear() methods often fail in modern JS frameworks because the internal state
        doesn't catch the rapid change. We use OS-level keys and explicit value validation.
        """
        element = self.find_element(EditorPageLocators.TITLE_INPUT)
        self.handle_react_sync(0.5)

        # 1. Trigger OS-level selection and deletion to force React 'onChange' event
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)

        # 2. Verification: Ensure field is strictly empty in the DOM before proceeding
        WebDriverWait(self.browser.driver, 5).until(lambda d: element.get_attribute("value") == "")
        self.handle_react_sync(0.5)

        # 3. Input new data
        element.send_keys(new_title)

        # 4. Final Verification: Ensure React state successfully captured the new input
        WebDriverWait(self.browser.driver, 5).until(lambda d: element.get_attribute("value") == new_title)
        self.handle_react_sync(0.5)