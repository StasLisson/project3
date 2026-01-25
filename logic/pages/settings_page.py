from __future__ import annotations
from typing import Optional

from logic.base_page import BasePage
from logic.locators import SettingsPageLocators


class SettingsPage(BasePage):
    """
    Page Object handling user configuration and profile updates.

    Key QA Concepts Implemented:
    - Data Integrity: Supports partial updates (e.g., changing only the bio without wiping the password).
    - Field Validation: Maps UI inputs directly to the backend's update schema.
    - React Synchronization: Handles the asynchronous nature of form submissions in Single Page Applications.
    """

    def update_profile(self,
                       username: Optional[str] = None,
                       email: Optional[str] = None,
                       password: Optional[str] = None,
                       image: Optional[str] = None,
                       bio: Optional[str] = None) -> None:
        """
        Updates profile fields based on provided arguments.
        Only fields that are explicitly passed (not None) will be modified.
        """
        if image:
            self.type(SettingsPageLocators.IMAGE_URL_INPUT, image)
        if username:
            self.type(SettingsPageLocators.USERNAME_INPUT, username)
        if bio:
            self.type(SettingsPageLocators.BIO_TEXTAREA, bio)
        if email:
            self.type(SettingsPageLocators.EMAIL_INPUT, email)
        if password:
            self.type(SettingsPageLocators.PASSWORD_INPUT, password)

        self.click(SettingsPageLocators.UPDATE_BTN)

        # Internal sync: Wait for the React application to process the PUT request
        # and update the local state/redirect.
        self.handle_react_sync(1.5)