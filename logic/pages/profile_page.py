from __future__ import annotations
from logic.base_page import BasePage
from logic.locators import ProfilePageLocators


class ProfilePage(BasePage):
    """
    Page Object for the User Profile view.
    Handles social graph interactions (Follow/Unfollow) and feed filtering.

    Key QA Concepts Implemented:
    - State Persistence: Verifies that UI toggles (Follow button) accurately reflect backend relationship states.
    - Asynchronous Rendering: Manages the latency between tab switching and API data population.
    """

    # ==========================================================
    # 1. SOCIAL ACTIONS
    # ==========================================================

    def follow_unfollow(self) -> None:
        """
        Toggles the follow status of the user.
        Includes a synchronization step to ensure the button text updates (e.g., 'Follow' -> 'Unfollow').
        """
        self.click(ProfilePageLocators.FOLLOW_BTN)
        self.handle_react_sync(1.0)

    # ==========================================================
    # 2. TAB NAVIGATION
    # ==========================================================

    def select_my_articles(self) -> None:
        """
        Switches to the 'My Articles' tab.
        Waits for the asynchronous fetch of the user's authored content.
        """
        self.click(ProfilePageLocators.TAB_MY_ARTICLES)
        self.handle_react_sync(1.5)

    def select_favorited_articles(self) -> None:
        """
        Switches to the 'Favorited Articles' tab.
        Waits for the asynchronous fetch of the liked content list.
        """
        self.click(ProfilePageLocators.TAB_FAVORITED)
        self.handle_react_sync(1.5)