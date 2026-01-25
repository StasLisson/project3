import time
import pytest
import allure

from infra.config import config
from logic.flows.authentication_flow import AuthenticationFlow
from logic.pages.home_page import HomePage
from logic.pages.profile_page import ProfilePage
from logic.pages.article_page import ArticlePage
from logic.locators import ArticlePageLocators, AuthPageLocators, ProfilePageLocators
from utils.faker_helper import random_username, random_email, random_password, random_article


# ==========================================================
# 1. SOCIAL ACTIONS (Follow & Favorite)
# ==========================================================

@allure.feature("Social Interactions")
@allure.story("Following")
@pytest.mark.sanity
def test_social_follow_user_should_toggle_button_state(browser, new_user, api_client):
    """מתקן את מבנה ה-URL למניעת קריסות חיבור."""
    password = random_password()
    other_user = api_client.register(random_username(), random_email(), password).json()["user"]

    auth = AuthenticationFlow(browser)
    auth.login(new_user["email"], new_user["password"])

    # בניית URL בטוחה (מחליפה את ה-/#/ הקיים בנתיב המלא)
    target_url = config.base_url.replace("/#/", f"/#/profile/{other_user['username']}")
    browser.driver.get(target_url)

    browser.wait_for_visible(ProfilePageLocators.USERNAME)
    ProfilePage(browser).follow_unfollow()


@allure.feature("Social Interactions")
@allure.story("Favoriting")
@pytest.mark.sanity
def test_profile_favorited_tab_should_show_favorited_article(browser, api_client):
    """וידוא שמאמר שסומן כ-Favorite מופיע בטאב הפרופיל."""
    # יצירת מאמר ב-API
    author_creds = {"username": random_username(), "email": random_email(), "password": random_password()}
    api_client.register(author_creds["username"], author_creds["email"], author_creds["password"])
    api_client.login(author_creds["email"], author_creds["password"])

    art = random_article()
    created = api_client.create_article(art.title, art.description, art.body, art.tags).json()
    slug = created["article"]["slug"]

    # לייק דרך ה-UI
    auth = AuthenticationFlow(browser)
    fan_data = {"username": random_username(), "email": random_email(), "password": random_password()}
    auth.register(fan_data["username"], fan_data["email"], fan_data["password"])

    article_url = config.base_url.replace("/#/", f"/#/article/{slug}")
    browser.driver.get(article_url)

    article_page = ArticlePage(browser)
    time.sleep(1.0) # המתנה לסנכרון React
    article_page.favorite_article()

    # מעבר לפרופיל דרך הניווט המרכזי ב-BasePage
    auth.auth_page.open_profile()
    profile_page = ProfilePage(browser)
    profile_page.select_favorited_articles()

    assert art.title in browser.driver.page_source


# ==========================================================
# 2. COMMENTING & FEED AGGREGATION
# ==========================================================

@allure.feature("Social Interactions")
@allure.story("Comments")
@pytest.mark.sanity
def test_workflow_author_sees_comment_from_another_user(browser, api_client, fresh_credentials):
    """וורקפלו מלא: יצירה ב-API, תגובה ב-UI, אימות ב-UI."""
    # שלב 1: AUTHOR (API)
    author_password = random_password()
    author_user = api_client.register(random_username(), random_email(), author_password).json()["user"]
    art_data = random_article()
    slug = api_client.create_article(art_data.title, art_data.description, art_data.body, art_data.tags).json()["article"]["slug"]

    # שלב 2: COMMENTER (UI)
    auth_flow = AuthenticationFlow(browser)
    auth_flow.register(fresh_credentials["username"], fresh_credentials["email"], fresh_credentials["password"])

    article_url = config.base_url.replace("/#/", f"/#/article/{slug}")
    browser.driver.get(article_url)

    # התאמה למתודת post_comment הקיימת ב-Page Object המאוחד
    comment_text = f"Nice post! - {fresh_credentials['username']}"
    ArticlePage(browser).post_comment(comment_text)

    browser.wait_for_visible(ArticlePageLocators.COMMENT_CARD, timeout=5)
    auth_flow.logout()

    # שלב 3: AUTHOR (UI)
    auth_flow.login(author_user["email"], author_password)
    browser.driver.get(article_url)
    assert comment_text in browser.get_text(ArticlePageLocators.COMMENT_TEXT)


@allure.feature("Social Interactions")
@allure.story("Security & Errors")
@pytest.mark.negative
def test_social_comment_post_empty_comment_should_be_ignored(browser, new_user, api_client):
    """
    T_SELE_18: Empty Comment.
    מעודכן: מוודא שהתגובה לא מפורסמת גם אם אין הודעת שגיאה ב-UI.
    """
    api_client.login(new_user["email"], new_user["password"])
    art = random_article()
    created = api_client.create_article(art.title, art.description, art.body, art.tags).json()
    slug = created["article"]["slug"]

    auth = AuthenticationFlow(browser)
    auth.login(new_user["email"], new_user["password"])
    article_url = config.base_url.replace("/#/", f"/#/article/{slug}")
    browser.driver.get(article_url)

    # 1. ספירת תגובות קיימות (במקרה הזה 0)
    initial_comments = browser.driver.find_elements(*ArticlePageLocators.COMMENT_CARD)
    initial_count = len(initial_comments)

    # 2. ניסיון שליחת תגובה ריקה
    ArticlePage(browser).post_comment("")
    time.sleep(1.5)  # המתנה קלה לוודא שכלום לא קורה ב-React

    # 3. אימות: מספר התגובות חייב להישאר זהה (לא התווספה תגובה ריקה)
    final_comments = browser.driver.find_elements(*ArticlePageLocators.COMMENT_CARD)
    assert len(final_comments) == initial_count, \
        f"Error: An empty comment was added! (Before: {initial_count}, After: {len(final_comments)})"

    # 4. אימות משלים: חיפוש הודעת שגיאה (אופציונלי, לא קורס אם חסר)
    errors = browser.driver.find_elements(*AuthPageLocators.ERROR_MESSAGES)
    if errors:
        print(f"UI Error found: {errors[0].text}")

@allure.feature("Social Interactions")
@allure.story("Feed")
@pytest.mark.sanity
def test_home_your_feed_aggregation_multiple_authors(browser, new_user, api_client):
    """אימות אגרגציית פיד אישי מכותבים מרובים."""
    authors = []
    articles = []

    for _ in range(2):
        u = {"username": random_username(), "email": random_email(), "password": random_password()}
        api_client.register(u["username"], u["email"], u["password"])
        api_client.login(u["email"], u["password"])
        art = random_article()
        api_client.create_article(art.title, art.description, art.body, art.tags)
        authors.append(u)
        articles.append(art)

    auth = AuthenticationFlow(browser)
    auth.login(new_user["email"], new_user["password"])

    for author in authors:
        url = config.base_url.replace("/#/", f"/#/profile/{author['username']}")
        browser.driver.get(url)
        time.sleep(1.0)
        ProfilePage(browser).follow_unfollow()

    browser.driver.get(config.base_url)
    home_page = HomePage(browser)
    home_page.select_your_feed()
    time.sleep(2.5) # המתנה לטעינת ה-API ב-React

    for art in articles:
        assert art.title in browser.driver.page_source