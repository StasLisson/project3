import json
import os
from datetime import datetime
from typing import Generator, Dict

import allure
import pytest

from infra.api_client import APIClient
from infra.browser_wrapper import BrowserWrapper
from infra.config import config as global_config
from utils.faker_helper import random_username, random_email, random_password


# ==========================================
# 0. RUN CONFIGURATION (Artifact Management)
# ==========================================

def _get_run_id() -> str:
    """Generates a timestamped ID for the current test run."""
    return datetime.now().strftime("%d.%m_%H-%M")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """
    Auto-configures the environment before test collection.

    QA Concept - Artifact Management:
    Dynamically creates a dedicated folder for this specific execution run.
    Uses 'setattr' to inject paths into the config object, avoiding linting errors about protected members.
    """
    run_id = _get_run_id()
    base_path = os.path.join("artifacts", f"run_{run_id}")

    paths = {
        "root": base_path,
        "screenshots": os.path.join(base_path, "screenshots"),
        "logs": os.path.join(base_path, "logs"),
        "allure": os.path.join(base_path, "allure-results")
    }

    for path in paths.values():
        os.makedirs(path, exist_ok=True)

    # Instruct Allure to write into our organized folder
    config.option.allure_report_dir = paths["allure"]

    # Store paths in the config object using dynamic injection (Avoids 'Protected Member' warnings)
    setattr(config, "run_paths", paths)


# ==========================================
# 1. REPORTING HOOK (Observability)
# ==========================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """
    A Hook to intercept test results.
    Captures screenshots and logs upon failure.
    Note: 'call' argument is required by pytest hook signature even if unused.
    """
    outcome = yield
    report = outcome.get_result()

    # Check if the test failed during the 'call' phase (execution)
    if report.when == "call" and report.failed:
        # Safely access the 'browser' fixture from the item
        # We use getattr because 'funcargs' is dynamic on the Item class
        funcargs = getattr(item, "funcargs", {})
        browser_wrapper = funcargs.get("browser")

        if browser_wrapper:
            # Retrieve the paths we stored earlier in pytest_configure
            # Using getattr to avoid 'Unresolved attribute' linter warning
            paths = getattr(item.config, "run_paths", {})

            # 1. Attach to Allure (Visual Report)
            try:
                allure.attach(
                    browser_wrapper.driver.get_screenshot_as_png(),
                    name="Failure Screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception:
                pass  # Fail silently if screenshot capture fails to avoid masking original error

            # 2. Save Physical File (Artifact Archival)
            if "screenshots" in paths:
                shot_path = os.path.join(paths["screenshots"], f"{item.name}.png")
                try:
                    browser_wrapper.driver.save_screenshot(shot_path)
                except Exception:
                    pass

            # 3. Save JSON Log (Data Analysis)
            if "logs" in paths:
                log_entry = {"test": item.name, "error": str(report.longrepr)}
                with open(os.path.join(paths["logs"], f"{item.name}.json"), "w") as f:
                    json.dump(log_entry, f, indent=4)


# ==========================================
# 2. FIXTURES (Setup & Teardown)
# ==========================================

@pytest.fixture(scope="session")
def api_client() -> APIClient:
    """
    Session-scoped API Client.
    Initialized once per run.
    """
    return APIClient()


@pytest.fixture(scope="function")
def browser(request: pytest.FixtureRequest) -> Generator[BrowserWrapper, None, None]:
    """
    Function-scoped Browser fixture.
    Handles Setup (Launching driver) and Teardown (Closing driver).
    """
    # Check for CLI override, otherwise default to False
    headless_option = request.config.getoption("--headless", default=False)

    wrapper = BrowserWrapper(headless=headless_option)
    # Use the renamed global config import to avoid shadowing
    wrapper.get_driver(global_config.base_url)

    yield wrapper

    wrapper.close_browser()


@pytest.fixture(scope="function")
def new_user(api_client: APIClient) -> Dict[str, str]:
    """
    Creates a user via API immediately before the test logic runs.
    """
    u = {"username": random_username(), "email": random_email(), "password": random_password()}
    api_client.register(u["username"], u["email"], u["password"])
    return u


@pytest.fixture(scope="function")
def fresh_credentials() -> Dict[str, str]:
    """
    Generates raw credentials without creating the user in the backend.
    """
    return {
        "username": random_username(),
        "email": random_email(),
        "password": random_password()
    }