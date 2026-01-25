from selenium.webdriver.common.by import By


class BasePageLocators:
    """
    Locators shared across the entire application (Navbar, Footer).
    Centralized here to adhere to the DRY principle and ease maintenance.
    """

    # ==========================================================
    # 1. NAVIGATION BAR
    # ==========================================================
    NAV_BAR = (By.CSS_SELECTOR, "nav.navbar")
    NAV_BRAND = (By.CSS_SELECTOR, ".navbar .navbar-brand")
    NAV_HOME = (By.XPATH, "//a[contains(., 'Home')]")
    FOOTER = (By.TAG_NAME, "footer")

    # ==========================================================
    # 2. GUEST NAVIGATION
    # ==========================================================
    NAV_SIGN_IN = (By.CSS_SELECTOR, "a.nav-link[href='#/login']")
    NAV_SIGN_UP = (By.XPATH, "//a[contains(., 'Sign up')]")

    # ==========================================================
    # 3. USER NAVIGATION
    # ==========================================================
    NAV_NEW_ARTICLE = (By.CSS_SELECTOR, "a.nav-link[href='#/editor']")
    NAV_USER_DROPDOWN = (By.CSS_SELECTOR, ".dropdown-toggle")

    # Items INSIDE the User Dropdown
    NAV_PROFILE = (By.XPATH, "//a[contains(@href,'#/profile/')]")
    NAV_SETTINGS = (By.XPATH, "//a[contains(@href,'#/settings')]")
    NAV_LOGOUT = (By.XPATH, "//a[contains(., 'Logout')]")


class AuthPageLocators:
    """Locators for Login and Registration pages."""

    # ==========================================================
    # SHARED & FORMS
    # ==========================================================
    AUTH_PAGE = (By.CSS_SELECTOR, ".auth-page")
    ERROR_MESSAGES = (By.CSS_SELECTOR, "ul.error-messages > li")

    REGISTER_USERNAME = (By.CSS_SELECTOR, "input[placeholder='Your Name']")
    REGISTER_EMAIL = (By.CSS_SELECTOR, "input[placeholder='Email']")
    REGISTER_PASSWORD = (By.CSS_SELECTOR, "input[placeholder='Password']")
    REGISTER_SUBMIT = (By.CSS_SELECTOR, "button.btn-primary")

    LOGIN_EMAIL = (By.CSS_SELECTOR, "input[placeholder='Email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "input[placeholder='Password']")
    LOGIN_SUBMIT = (By.CSS_SELECTOR, "button.btn-primary")


class HomePageLocators:
    """Locators for the Home Page feeds and lists."""

    # ==========================================================
    # FEEDS & LISTS
    # ==========================================================
    HOME_PAGE = (By.CSS_SELECTOR, ".home-page")
    FEED_TOGGLE_CONTAINER = (By.CSS_SELECTOR, ".feed-toggle .nav-pills")

    TAB_YOUR_FEED = (By.XPATH, "//button[contains(., 'Your Feed')]")
    TAB_GLOBAL_FEED = (By.XPATH, "//button[contains(., 'Global Feed')]")

    ARTICLE_LIST = (By.CSS_SELECTOR, ".home-page .col-md-9")
    PREVIEW_CARD = (By.CSS_SELECTOR, ".article-preview")
    PREVIEW_TITLE = (By.CSS_SELECTOR, ".article-preview h1")
    PREVIEW_AUTHOR = (By.CSS_SELECTOR, ".article-preview .author")
    PREVIEW_LINK = (By.CSS_SELECTOR, ".article-preview .preview-link")

    PREVIEW_FAV_BTN = (By.CSS_SELECTOR, ".article-preview .btn-outline-primary")
    PREVIEW_FAV_COUNT = (By.CSS_SELECTOR, ".article-preview .counter")

    SIDEBAR = (By.CSS_SELECTOR, ".sidebar")
    TAG_LIST = (By.CSS_SELECTOR, ".tag-list")
    TAG_PILL = (By.CSS_SELECTOR, ".tag-pill")


class EditorPageLocators:
    """Locators for the Article Editor (Create/Edit)."""

    EDITOR_PAGE = (By.CSS_SELECTOR, ".editor-page")
    TITLE_INPUT = (By.CSS_SELECTOR, "input[placeholder='Article Title']")
    ABOUT_INPUT = (By.CSS_SELECTOR, "input[placeholder^='What']")
    BODY_INPUT = (By.CSS_SELECTOR, "textarea[placeholder^='Write']")
    TAGS_INPUT = (By.CSS_SELECTOR, "input[placeholder='Enter tags']")
    TAG_PILL = (By.CSS_SELECTOR, ".tag-list .tag-pill")
    PUBLISH_BTN = (By.CSS_SELECTOR, "button.btn-primary")


class ArticlePageLocators:
    """Locators for a Single Article View."""

    ARTICLE_PAGE = (By.CLASS_NAME, "article-page")
    ARTICLE_TITLE = (By.TAG_NAME, "h1")
    BANNER_TITLE = (By.TAG_NAME, "h1")

    ARTICLE_BODY = (By.CSS_SELECTOR, ".article-content p")
    ARTICLE_AUTHOR = (By.CSS_SELECTOR, "a.author")
    ARTICLE_DATE = (By.CSS_SELECTOR, "span.date")

    DELETE_ARTICLE_BTN = (By.XPATH, "//button[contains(., 'Delete Article')]")
    EDIT_ARTICLE_BTN = (By.XPATH, "//a[contains(., 'Edit Article')]")

    FOLLOW_BTN = (By.CSS_SELECTOR, "button.action-btn")
    FAVORITE_BTN = (By.CSS_SELECTOR, "button.btn-outline-primary")

    COMMENT_TEXTAREA = (By.CSS_SELECTOR, "textarea.form-control")
    POST_COMMENT_BTN = (By.CSS_SELECTOR, "button.btn-primary")
    COMMENT_TEXT = (By.CSS_SELECTOR, "p.card-text")
    COMMENT_CARD = (By.CSS_SELECTOR, "p.card-text")
    DELETE_COMMENT_BTN = (By.CSS_SELECTOR, "button.btn-outline-secondary .ion-trash-a")


class ProfilePageLocators:
    """Locators for User Profile."""

    PROFILE_PAGE = (By.CSS_SELECTOR, ".profile-page")
    USERNAME = (By.CSS_SELECTOR, ".user-info h4")
    BIO = (By.CSS_SELECTOR, ".user-info p")
    USER_IMAGE = (By.CSS_SELECTOR, ".user-info img")
    FOLLOW_BTN = (By.CSS_SELECTOR, ".user-info button")

    TAB_MY_ARTICLES = (By.XPATH, "//a[contains(@class, 'nav-link') and contains(@href, '/profile/')]")
    TAB_FAVORITED = (By.XPATH, "//a[contains(@class, 'nav-link') and contains(@href, '/favorites')]")
    ARTICLE_PREVIEW = (By.CSS_SELECTOR, ".profile-page .article-preview")


class SettingsPageLocators:
    """Locators for Settings Page."""

    SETTINGS_PAGE = (By.CSS_SELECTOR, ".settings-page")
    IMAGE_URL_INPUT = (By.CSS_SELECTOR, "input[placeholder='URL of profile picture']")
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='Your Name']")
    BIO_TEXTAREA = (By.CSS_SELECTOR, "textarea[placeholder*='bio']")
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[placeholder='Email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[placeholder='Password']")

    UPDATE_BTN = (By.CSS_SELECTOR, "button.btn-primary")
    LOGOUT_BTN = (By.CSS_SELECTOR, "button.btn-outline-danger")