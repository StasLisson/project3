from __future__ import annotations
from typing import List

from infra.browser_wrapper import BrowserWrapper
from logic.pages.article_page import ArticlePage
from logic.pages.editor_page import EditorPage


class ArticleFlow:
    """
    Business Logic Layer for Article Management scenarios.

    Key QA Concepts Implemented:
    - Layering: Orchestrates multiple Page Objects (EditorPage, ArticlePage) to fulfill complex user stories.
    - Test Architecture: Encapsulates end-to-end workflows (Create, Update, Delete) to reduce code duplication in test files.
    """

    def __init__(self, browser: BrowserWrapper) -> None:
        """Initialize the flow with the necessary Page Objects."""
        self.browser = browser
        self.editor = EditorPage(browser)
        self.article = ArticlePage(browser)

    # ==========================================================
    # 1. CONTENT CREATION
    # ==========================================================

    def create_article(self, title: str, description: str, body: str, tags: List[str]) -> None:
        """
        Executes the full End-to-End article creation lifecycle.
        Navigates to the editor, fills the form, and publishes the content.
        """
        self.editor.navigate_to("editor")

        self.editor.fill_title(title)
        self.editor.fill_description(description)
        self.editor.fill_body(body)

        # QA Optimization: Join tags here to keep the Page Object method generic
        self.editor.fill_tags(" ".join(tags))

        self.editor.publish_article()

    # ==========================================================
    # 2. CONTENT MAINTENANCE
    # ==========================================================

    def update_article(self, new_title: str) -> None:
        """
        Updates the title of an existing article.

        QA Concept - Stability over Cleverness:
        Uses a 'brute force' update method to handle React's Virtual DOM state synchronization issues
        often found in input fields during rapid automation.
        """
        self.editor.brute_force_update_title(new_title)
        self.editor.publish_article()

    # ==========================================================
    # 3. RESOURCE TERMINATION
    # ==========================================================

    def delete_article_by_slug(self, slug: str) -> None:
        """
        Navigates directly to a specific article and executes the deletion process.

        QA Concept - Determinism:
        Uses direct URL navigation (Deep Linking) instead of traversing the UI feed.
        This reduces flakiness caused by feed rendering delays or ordering shifts.
        """
        self.article.navigate_to(f"article/{slug}")
        self.article.delete_article()