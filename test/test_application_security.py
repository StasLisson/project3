import time
import pytest
import allure
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from infra.api_client import APIClient
from infra.config import config
from logic.flows.authentication_flow import AuthenticationFlow
from logic.pages.authentication_page import AuthenticationPage
from logic.pages.settings_page import SettingsPage
from logic.locators import BasePageLocators, AuthPageLocators
from utils.faker_helper import random_password


@allure.feature("Security")
@allure.story("Access Control")
@pytest.mark.negative
def test_security_access_protected_editor_page_without_auth_should_redirect(browser):
    """
    Test Case: Unauthenticated Access Control (T_SELE_25).

    QA Concept - Broken Access Control:
    Verifies that a guest user cannot access protected routes (like the Editor)
    by directly manipulating the URL. The system must redirect them to the home page or login.
    """
    # 1. Secure Session Cleanup (Cookies only)
    browser.driver.get(config.base_url)
    browser.driver.delete_all_cookies()
    browser.driver.refresh()

    # 2. Attempt Direct Navigation to Protected Resource
    editor_url = config.base_url.replace("/#/", "/#/editor")
    browser.driver.get(editor_url)

    # 3. Validation: Verify Redirect (User is kicked out)
    WebDriverWait(browser.driver, 10).until(
        lambda d: "/editor" not in d.current_url
    )
    assert "#/editor" not in browser.driver.current_url, "Security Breach: Unauthenticated user accessed Editor!"

    # 4. Deep Layer Validation: API Access Control (401 check)
    unauth_api = APIClient()
    payload = {
        "article": {
            "title": "unauth-should-fail",
            "description": "unauth-should-fail",
            "body": "unauth-should-fail",
            "tagList": []
        }
    }
    resp = unauth_api.post("/api/articles", payload)
    assert resp.status_code == 401, "API Security Breach: Unauthenticated POST request was accepted!"


@allure.feature("Security")
@allure.story("XSS Protection")
@pytest.mark.negative
def test_security_xss_injection_in_bio_should_be_sanitized(browser, new_user):
    """
    Test Case: Stored XSS in Profile Bio (T_SELE_26).

    QA Concept - Input Sanitization:
    Attempts to inject a malicious JavaScript payload (<script>alert...</script>) into the user bio.
    Verifies that the browser does not execute the script upon rendering.
    """
    # 1. Login
    auth_flow = AuthenticationFlow(browser)
    auth_flow.login(new_user["email"], new_user["password"])

    # 2. Navigate to Settings
    browser.click(BasePageLocators.NAV_USER_DROPDOWN)
    browser.click(BasePageLocators.NAV_SETTINGS)

    # 3. Inject XSS Payload
    xss_payload = "<script>alert('XSS')</script>"

    settings = SettingsPage(browser)
    settings.update_profile(bio=xss_payload)

    # 4. Trigger Rendering (Refresh Page)
    browser.driver.refresh()
    time.sleep(1)  # Allow browser time to parse/execute scripts if vulnerable

    # 5. Validation: Ensure no Alert popped up
    try:
        browser.driver.switch_to.alert.accept()
        pytest.fail("CRITICAL: XSS Vulnerability found! Malicious script executed.")
    except NoAlertPresentException:
        pass  # Test Passed: No alert found


@allure.feature("Security")
@allure.story("SQL Injection")
@pytest.mark.negative
def test_security_sql_injection_login_attempt_should_fail(browser):
    """
    Test Case: SQL Injection on Login (T_SELE_31).

    QA Concept - Input Validation:
    Attempts to bypass authentication using a classic SQL injection payload (' OR '1'='1).
    Verifies that the system handles the input as a string literal and denies access.
    """
    # 1. Navigate to Login
    auth_page = AuthenticationPage(browser)
    auth_page.navigate_to("login")

    # 2. Wait for UI to be ready
    browser.wait_for_visible(AuthPageLocators.LOGIN_EMAIL)

    # 3. Inject SQL Payload
    sql_payload = "' OR '1'='1"
    auth_page.fill_login_email(sql_payload)
    auth_page.fill_login_password(random_password())
    auth_page.submit_login()

    # 4. Validation: Verify Access Denied
    # We expect to stay on the login page (Sign In link still visible)
    WebDriverWait(browser.driver, 10).until(
        EC.visibility_of_element_located(BasePageLocators.NAV_SIGN_IN)
    )

    sign_in_text = browser.get_text(BasePageLocators.NAV_SIGN_IN).lower()
    assert "login" in sign_in_text or "sign in" in sign_in_text, "Security Breach: SQL Injection likely bypassed authentication!"