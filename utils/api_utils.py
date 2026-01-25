import time
from typing import Dict

from infra.api_client import APIClient
from utils.faker_helper import random_username, random_email, random_password


def register_user_via_api(api_client: APIClient) -> Dict[str, str]:
    """
    Registers a new user directly via API and returns credentials + token.

    QA Concept - Setup Optimization:
    Bypasses the slow UI registration process to set up test preconditions instantly.
    """
    pwd = random_password()
    resp = api_client.register(random_username(), random_email(), pwd)
    user_data = resp.json()["user"]
    return {
        "email": user_data["email"],
        "username": user_data["username"],
        "password": pwd,
        "token": user_data["token"]
    }


def register_and_login_with_retry(api_client: APIClient, max_retries: int = 3) -> Dict[str, str]:
    """
    Performs registration and login with a resilience mechanism.

    QA Concept - Flakiness Mitigation:
    Solves 401 Unauthorized issues seen during high-load stress tests by
    retrying the login handshake with exponential backoff.
    Also injects the token into the current thread session.
    """
    creds = register_user_via_api(api_client)

    for i in range(max_retries):
        resp = api_client.login(creds["email"], creds["password"])
        if resp.status_code == 200:
            # Inject token into the current ThreadLocal session
            api_client.set_token(creds["token"])
            return creds

        # Exponential backoff wait
        time.sleep(0.5 * (i + 1))

    return creds