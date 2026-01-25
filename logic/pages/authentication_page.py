from __future__ import annotations
from logic.base_page import BasePage
from logic.locators import AuthPageLocators


class AuthenticationPage(BasePage):
    """
    Page Object handling Login and Registration forms.

    Key QA Concepts Implemented:
    - Atomic Actions: Separates data entry (filling fields) from submission triggers, allowing flexible test flows.
    - Stability: Uses JavaScript clicks for submission to avoid 'element intercepted' errors common in React forms.
    - Observability: Provides dedicated methods to retrieve error messages for negative testing validation.
    """

    # ==========================================================
    # LOGIN ACTIONS
    # ==========================================================

    def fill_login_email(self, email: str) -> None:
        """Enters email into the login form."""
        self.type(AuthPageLocators.LOGIN_EMAIL, email)

    def fill_login_password(self, password: str) -> None:
        """Enters password into the login form."""
        self.type(AuthPageLocators.LOGIN_PASSWORD, password)

    def submit_login(self) -> None:
        """
        Triggers the login submission.
        Uses JS click to bypass potential UI overlays and waits for React state transition.
        """
        self.browser.click_using_javascript(AuthPageLocators.LOGIN_SUBMIT)
        self.handle_react_sync(1.5)

    # ==========================================================
    # REGISTRATION ACTIONS
    # ==========================================================

    def fill_register_username(self, username: str) -> None:
        """Enters username into the registration form."""
        self.type(AuthPageLocators.REGISTER_USERNAME, username)

    def fill_register_email(self, email: str) -> None:
        """Enters email into the registration form."""
        self.type(AuthPageLocators.REGISTER_EMAIL, email)

    def fill_register_password(self, password: str) -> None:
        """Enters password into the registration form."""
        self.type(AuthPageLocators.REGISTER_PASSWORD, password)

    def submit_register(self) -> None:
        """
        Triggers the registration submission.
        Includes a slightly longer sync wait (2.0s) to account for the heavier backend process of user creation.
        """
        self.browser.click_using_javascript(AuthPageLocators.REGISTER_SUBMIT)
        self.handle_react_sync(2.0)

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def get_error_message(self) -> str:
        """Extracts error text displayed by the app (e.g., 'Email already taken') for assertion."""
        return self.get_text(AuthPageLocators.ERROR_MESSAGES)