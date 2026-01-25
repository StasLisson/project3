from __future__ import annotations
from logic.base_page import BasePage
from logic.locators import ArticlePageLocators

class ArticlePage(BasePage):
    """
    Page Object representing the Article View page.
    Encapsulates interactions with article content, comments, and action buttons.

    Key QA Concepts Implemented:
    - Page Object Model (POM): Segregates UI logic from test scripts.
    - Atomic Actions: Each method performs a single, distinct user interaction.
    - Resilience: Handles native browser alerts and React Virtual DOM state changes explicitely.
    """

    def get_article_title(self) -> str:
        """Extracts the article headline for validation."""
        return self.get_text(ArticlePageLocators.ARTICLE_TITLE)

    def delete_article(self) -> None:
        """
        Performs the delete workflow.
        Handles the native browser confirmation alert common in this application.
        """
        self.click(ArticlePageLocators.DELETE_ARTICLE_BTN)
        try:
            # Accessing driver via wrapper for alert handling
            self.browser.driver.switch_to.alert.accept()
            # Wait for React to process the deletion and redirect
            self.handle_react_sync(1.5)
        except Exception:
            # Fail-safe: If no alert appears, assume deletion proceeded or button state changed
            pass

    def favorite_article(self) -> None:
        """Toggles the favorite (Heart) button."""
        self.click(ArticlePageLocators.FAVORITE_BTN)
        self.handle_react_sync(0.8)

    def post_comment(self, text: str) -> None:
        """
        Submits a comment on the article.
        Uses JavaScript click to bypass potential UI overlays (e.g., footers/overlays).
        """
        self.type(ArticlePageLocators.COMMENT_TEXTAREA, text)
        self.browser.click_using_javascript(ArticlePageLocators.POST_COMMENT_BTN)
        self.handle_react_sync(1.0)