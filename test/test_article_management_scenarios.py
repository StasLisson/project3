import pytest
import allure
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from infra.config import config
from infra.api_client import APIClient
from logic.flows.authentication_flow import AuthenticationFlow
from logic.flows.article_flow import ArticleFlow
from logic.pages.article_page import ArticlePage
from logic.pages.editor_page import EditorPage
from logic.locators import ArticlePageLocators, EditorPageLocators
from utils.faker_helper import random_article, random_username, random_email, random_password


# ==========================================================
# 1. SANITY TESTS (Article Lifecycle)
# ==========================================================

@allure.feature("Article Management")
@allure.story("Creation")
@pytest.mark.sanity
def test_article_creation_publish_new_article_with_valid_data_should_succeed(browser, new_user):
    """Verify that a user can publish a new article via the UI."""
    auth = AuthenticationFlow(browser)
    auth.login(new_user["email"], new_user["password"])

    article_flow = ArticleFlow(browser)
    article = random_article()

    with allure.step(f"Create article: {article.title}"):
        article_flow.create_article(article.title, article.description, article.body, article.tags)

    # Explicit wait for React redirect to article view
    WebDriverWait(browser.driver, 10).until(EC.url_contains("/article/"))

    article_page = ArticlePage(browser)
    assert article_page.get_article_title() == article.title


@allure.feature("Article Management")
@allure.story("Viewing")
@pytest.mark.sanity
def test_article_viewing_verify_content_matches_creation_data(browser, new_user, api_client):
    """Verify that viewing an article correctly displays its data."""
    api_client.login(new_user["email"], new_user["password"])
    art = random_article()
    created = api_client.create_article(art.title, art.description, art.body, art.tags).json()
    slug = created["article"]["slug"]

    auth = AuthenticationFlow(browser)
    auth.login(new_user["email"], new_user["password"])

    # Construct URL safely to avoid ERR_CONNECTION_RESET
    target_url = config.base_url.replace("/#/", f"/#/article/{slug}")
    browser.driver.get(target_url)

    article_page = ArticlePage(browser)
    assert article_page.get_text(ArticlePageLocators.BANNER_TITLE) == art.title


@allure.feature("Article Management")
@allure.story("Editing")
@pytest.mark.sanity
def test_article_editing_update_title_should_publish_successfully(browser, new_user, api_client):
    """Verify that editing an existing article updates the title."""
    api_client.login(new_user["email"], new_user["password"])
    art = random_article()
    created = api_client.create_article(art.title, art.description, art.body, art.tags).json()
    slug = created["article"]["slug"]

    auth = AuthenticationFlow(browser)
    auth.login(new_user["email"], new_user["password"])

    # Construct editor URL safely
    editor_url = config.base_url.replace("/#/", f"/#/editor/{slug}")
    browser.driver.get(editor_url)

    editor = EditorPage(browser)
    new_title = art.title + " updated"

    with allure.step("Perform brute-force title update"):
        editor.brute_force_update_title(new_title)
        editor.publish_article()

    WebDriverWait(browser.driver, 10).until(EC.url_contains("/article/"))
    article_page = ArticlePage(browser)
    assert article_page.get_article_title() == new_title


# ==========================================================
# 2. NEGATIVE TESTS & EDGE CASES
# ==========================================================

@allure.feature("Article Management")
@allure.story("Validation")
@pytest.mark.negative
def test_article_creation_publish_with_missing_title_should_be_blocked(browser, new_user):
    """Verify browser-level validation prevents publishing without a title."""
    auth = AuthenticationFlow(browser)
    auth.login(new_user["email"], new_user["password"])

    # Direct navigation to editor route
    editor_url = config.base_url.replace("/#/", "/#/editor")
    browser.driver.get(editor_url)

    title_input = browser.driver.find_element(*EditorPageLocators.TITLE_INPUT)
    assert title_input.get_attribute("required") is not None

    editor_page = EditorPage(browser)
    editor_page.fill_description("Automated Desc")
    editor_page.fill_body("Automated Body")
    editor_page.publish_article()

    # User should remain on editor page due to validation
    assert "editor" in browser.driver.current_url


@allure.feature("Article Management")
@allure.story("Permissions")
@pytest.mark.negative
def test_article_access_edit_someone_elses_article_should_hide_edit_button(browser, api_client):
    """Verify that unauthorized users cannot see the 'Edit' button."""
    # User A creates article
    password_a = random_password()
    user_a = api_client.register(random_username(), random_email(), password_a).json()["user"]
    api_client.login(user_a["email"], password_a)

    art = random_article()
    created = api_client.create_article(art.title, art.description, art.body, []).json()
    slug = created["article"]["slug"]

    # User B logs in
    user_b_creds = {"username": random_username(), "email": random_email(), "password": random_password()}
    api_client.register(user_b_creds["username"], user_b_creds["email"], user_b_creds["password"])

    auth = AuthenticationFlow(browser)
    auth.login(user_b_creds["email"], user_b_creds["password"])

    target_url = config.base_url.replace("/#/", f"/#/article/{slug}")
    browser.driver.get(target_url)

    # Verify edit button is hidden for non-author
    edit_buttons = browser.driver.find_elements(*ArticlePageLocators.EDIT_ARTICLE_BTN)
    assert len(edit_buttons) == 0, "Edit button should NOT be visible for non-author"


@allure.feature("Article Management")
@allure.story("Deletion")
@pytest.mark.sanity
def test_article_deletion_author_can_delete_article_and_article_becomes_inaccessible(browser, new_user, api_client):
    """Verify that deleting an article removes it from the system."""
    # --- Arrange ---
    api_client.login(new_user["email"], new_user["password"])
    art = random_article()
    created = api_client.create_article(art.title, art.description, art.body, art.tags).json()
    slug = created["article"]["slug"]

    # --- Act ---
    auth = AuthenticationFlow(browser)
    auth.login(new_user["email"], new_user["password"])

    # Construct URL safely to avoid connection resets
    article_url = config.base_url.replace("/#/", f"/#/article/{slug}")
    browser.driver.get(article_url)

    with allure.step("Trigger article deletion"):
        ArticlePage(browser).delete_article()

    # --- Assert 1: UI Redirect ---
    # Smart Wait: Verify redirect to home page
    WebDriverWait(browser.driver, 10).until(EC.url_to_be(config.base_url))

    # --- Assert 2: Backend Verification ---
    resp = APIClient().get(f"/api/articles/{slug}")
    assert resp.status_code == 404, f"The article {slug} was still found in the database!"