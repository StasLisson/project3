from __future__ import annotations
import json
import logging
import threading
from datetime import datetime, timezone
from typing import Optional, List, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from infra.config import config
from utils.faker_helper import random_article, random_email, random_username


class APIClient:
    """
    Infrastructure layer component responsible for all HTTP interactions with the application.

    Key QA Concepts Implemented:
    - Layering: Acts as a facade, decoupling test logic from raw API communication details.
    - Parallelism by Design: Utilizes `threading.local` to ensure thread-safe sessions, critical for parallel execution (xdist).
    - Stability over Cleverness: Implements automatic resilience patterns (Retries) via HTTPAdapter to handle transient network failures.
    - Observability First: Includes a centralized error logging mechanism (`_log_error`) to capture and format failures for rapid debugging.
    """

    def __init__(self):
        self.base_url = config.api_base_url.rstrip('/')
        self._local = threading.local()
        self.default_headers = {"Content-Type": "application/json"}

    # ==========================================================
    # 1. SESSION MANAGEMENT
    # ==========================================================

    @property
    def session(self) -> requests.Session:
        """
        Provides a thread-local session with built-in resilience policies.
        Ensures that each test worker maintains its own connection pool and state.
        """
        if not hasattr(self._local, "session"):
            session = requests.Session()

            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)

            session.headers.update(self.default_headers)
            self._local.session = session
            self._local.token = None

        return self._local.session

    def set_token(self, token: str) -> None:
        """
        Manually injects an authentication token into the current thread's session.
        Useful for sharing state between threads in stress tests.
        """
        self._local.token = token
        self.session.headers["Authorization"] = f"Token {token}"

    def get_token(self) -> Optional[str]:
        """
        Retrieves the current authentication token from thread-local storage.
        """
        return getattr(self._local, "token", None)

    def _update_auth_header(self, token: str) -> None:
        """Updates the session headers with the new token."""
        self.set_token(token)

    # ==========================================================
    # 2. BUSINESS LOGIC
    # ==========================================================

    def create_article(self, title: str = None, description: str = None, body: str = None, tags: List[str] = None) -> requests.Response:
        """
        Creates a new article via API.
        Supports both specific data (Functional Testing) and random generation (Stress Testing).
        """
        data = random_article()
        payload = {
            "article": {
                "title": title or data.title,
                "description": description or data.description,
                "body": body or data.body,
                "tagList": tags if tags is not None else data.tags
            }
        }
        return self._request("POST", "/api/articles", json=payload)

    def login(self, email: str, password: str) -> requests.Response:
        """Authenticates a user and updates the session token upon success."""
        payload = {"user": {"email": email, "password": password}}
        response = self._request("POST", "/api/users/login", json=payload)
        if response.status_code == 200:
            self._update_auth_header(response.json()["user"]["token"])
        return response

    def register(self, username: str = None, email: str = None, password: str = "Password123!") -> requests.Response:
        """Registers a new user and automatically logs them in (updates token)."""
        payload = {
            "user": {
                "username": username or random_username(),
                "email": email or random_email(),
                "password": password
            }
        }
        response = self._request("POST", "/api/users", json=payload)
        if response.status_code in [200, 201]:
            self._update_auth_header(response.json()["user"]["token"])
        return response

    # ==========================================================
    # 3. REQUEST ENGINE
    # ==========================================================
    @staticmethod
    def _log_error(method: str, endpoint: str, response: requests.Response, request_data: Any = None) -> None:
        """Logs detailed information about failed API requests for observability."""
        error_log = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'method': method,
            'endpoint': endpoint,
            'status_code': response.status_code,
            'request_payload': request_data,
            'response_body': response.text,
            'elapsed_ms': round(response.elapsed.total_seconds() * 1000, 2)
        }
        logging.error(f"API FAILURE: {json.dumps(error_log, indent=2)}")

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Central wrapper for all HTTP requests.
        Handles URL construction, execution, and error logging.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            if response.status_code >= 400:
                self._log_error(method, endpoint, response, kwargs.get('json'))
            return response
        except requests.RequestException as e:
            logging.critical(f"NETWORK FAILURE: {str(e)}")
            raise

    # HTTP Wrappers

    def get(self, endpoint: str) -> requests.Response:
        return self._request("GET", endpoint)

    def post(self, endpoint: str, payload: Any = None) -> requests.Response:
        return self._request("POST", endpoint, json=payload)

    def put(self, endpoint: str, payload: Any = None) -> requests.Response:
        return self._request("PUT", endpoint, json=payload)

    def patch(self, endpoint: str, payload: Any = None) -> requests.Response:
        return self._request("PATCH", endpoint, json=payload)

    def delete(self, endpoint: str) -> requests.Response:
        return self._request("DELETE", endpoint)