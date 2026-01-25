from __future__ import annotations
from infra.browser_wrapper import BrowserWrapper
from logic.pages.authentication_page import AuthenticationPage
from logic.pages.home_page import HomePage


class AuthenticationFlow:
    """
    Business Logic Layer for Authentication scenarios.
    Orchestrates Login, Registration, and Logout workflows.

    Key QA Concepts Implemented:
    - Layering: Decouples atomic UI actions (Page Objects) from business processes.
    - Verification Strategy: Includes optional 'expect_success' assertions to validate state transitions immediately within the flow.
    - Reusability: Centralizes the login sequence so it can be reused by Setup fixtures and Tests alike.
    """

    def __init__(self, browser: BrowserWrapper) -> None:
        """Initialize the flow with the necessary Page Objects."""
        self.browser = browser
        self.auth_page = AuthenticationPage(browser)
        self.home_page = HomePage(browser)

    def login(self, email: str, password: str, expect_success: bool = True) -> None:
        """
        Executes the full Login workflow.
        """
        self.auth_page.navigate_to("login")
        self.auth_page.fill_login_email(email)
        self.auth_page.fill_login_password(password)
        self.auth_page.submit_login()

        if expect_success:
            # QA Verification: Ensure we landed on the Home Page and are authenticated
            if not self.home_page.is_user_logged_in():
                raise AssertionError(f"Login failed for user {email} - User dropdown not visible.")

    def register(self, username: str, email: str, password: str, expect_success: bool = True) -> None:
        """
        Executes the full Registration workflow.
        """
        self.auth_page.navigate_to("register")
        self.auth_page.fill_register_username(username)
        self.auth_page.fill_register_email(email)
        self.auth_page.fill_register_password(password)
        self.auth_page.submit_register()

        if expect_success:
            # QA Verification: Ensure registration automatically logged the user in
            if not self.home_page.is_user_logged_in():
                raise AssertionError("Registration failed - User not logged in after sign up.")

    def logout(self) -> None:
        """
        Executes the Logout sequence via the global Navbar.
        """
        self.home_page.logout()