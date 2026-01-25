import pytest
import allure
from logic.flows.authentication_flow import AuthenticationFlow
from logic.locators import AuthPageLocators, BasePageLocators
from utils.faker_helper import random_username, random_password

# ==========================================================
# 1. SANITY TESTS
# ==========================================================

@allure.feature("Authentication")
@allure.story("User Registration")
@pytest.mark.sanity
def test_authentication_register_new_user_with_valid_data_should_succeed(browser, fresh_credentials):
    with allure.step("Initialize Authentication Flow"):
        auth = AuthenticationFlow(browser)
    with allure.step(f"Register with email: {fresh_credentials['email']}"):
        auth.register(
            fresh_credentials["username"],
            fresh_credentials["email"],
            fresh_credentials["password"]
        )
    with allure.step("Verify user is logged in"):
        assert auth.auth_page.is_user_logged_in(), "User dropdown not found after registration"

@allure.feature("Authentication")
@allure.story("User Login")
@pytest.mark.sanity
def test_authentication_login_with_valid_credentials_should_succeed(browser, new_user):
    auth = AuthenticationFlow(browser)
    with allure.step(f"Login with pre-created user: {new_user['email']}"):
        auth.login(new_user["email"], new_user["password"])
    with allure.step("Verify user is logged in"):
        assert auth.auth_page.is_user_logged_in(), "User dropdown not found after login"

@allure.feature("Authentication")
@allure.story("User Logout")
@pytest.mark.sanity
def test_authentication_logout_should_redirect_to_guest_view(browser, new_user):
    auth = AuthenticationFlow(browser)
    auth.login(new_user["email"], new_user["password"])
    with allure.step("Perform Logout"):
        auth.logout()
    with allure.step("Verify 'Sign in' link is visible"):
        assert browser.wait_for_visible(BasePageLocators.NAV_SIGN_IN).is_displayed()

@allure.feature("Profile")
@allure.story("Update Bio")
@pytest.mark.sanity
def test_user_account_update_profile_bio_should_persist(browser, new_user):
    auth = AuthenticationFlow(browser)
    auth.login(new_user["email"], new_user["password"])

    with allure.step("Navigate to Settings"):
        auth.auth_page.open_settings()

    with allure.step("Update Bio text"):
        from logic.pages.settings_page import SettingsPage
        settings = SettingsPage(browser)
        settings.update_profile(bio="Updated bio from automated test")

# ==========================================================
# 2. NEGATIVE TESTS
# ==========================================================

@allure.feature("Authentication")
@allure.story("Duplicate Registration")
@pytest.mark.negative
def test_authentication_register_with_existing_email_should_show_error(browser, new_user):
    auth = AuthenticationFlow(browser)
    with allure.step(f"Attempt registration with existing email: {new_user['email']}"):
        auth.register(
            username=random_username(),
            email=new_user["email"],
            password=random_password(),
            expect_success=False
        )
    with allure.step("Verify error message"):
        error_text = auth.auth_page.get_error_message().lower()
        assert "email already exists" in error_text or "email has already been taken" in error_text

@allure.feature("Authentication")
@allure.story("Invalid Login")
@pytest.mark.negative
def test_authentication_login_with_wrong_password_should_show_error(browser, api_client):
    user_data = {"username": random_username(), "email": f"test_{random_username()}@example.com",
                 "password": "ValidPass123!"}
    api_client.register(user_data["username"], user_data["email"], user_data["password"])

    auth_flow = AuthenticationFlow(browser)
    with allure.step("Attempt login with wrong password"):
        auth_flow.login(user_data["email"], "IncorrectPassword!", expect_success=False)

    with allure.step("Verify error message"):
        error_text = browser.get_text(AuthPageLocators.ERROR_MESSAGES)
        assert "email/password" in error_text.lower() or "not found" in error_text.lower()