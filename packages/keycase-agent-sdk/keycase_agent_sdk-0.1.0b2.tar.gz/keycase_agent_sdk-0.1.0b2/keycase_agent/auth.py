"""Authentication service with token refresh and retry logic."""

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from .utils.auth_helper import (
    authenticate_agent,
    refresh_access_token,
)

logger = logging.getLogger(__name__)

# Constants
DEFAULT_TOKEN_VALIDITY_HOURS = 24
DEFAULT_TOKEN_REFRESH_THRESHOLD_SECONDS = 3600  # 1 hour before expiry
DEFAULT_MAX_RETRY_ATTEMPTS = 3
MAX_RETRY_DELAY_SECONDS = 30
TOKEN_CHECK_INTERVAL_SECONDS = 300  # 5 minutes


@dataclass
class AuthCredentials:
    """Authentication credentials and connection info."""

    agent_id: int
    organization_id: int
    access_token: str
    refresh_token: str
    session_id: str
    ws_url: str
    token_expires_at: Optional[datetime] = None


class AuthService:
    """Authentication service using AgentToken-based authentication."""

    def __init__(
        self,
        http_url: str,
        agent_token: str,
        agent_name: str,
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        token_refresh_threshold: int = DEFAULT_TOKEN_REFRESH_THRESHOLD_SECONDS,
        max_retry_attempts: int = DEFAULT_MAX_RETRY_ATTEMPTS,
    ) -> None:
        """Initialize authentication service.

        Args:
            http_url: HTTP API base URL
            agent_token: AgentToken (must start with 'agt_')
            agent_name: Unique agent name within organization
            version: Agent version
            capabilities: List of capabilities the agent supports
            tags: List of labels for categorization
            token_refresh_threshold: Seconds before expiry to refresh token
            max_retry_attempts: Maximum authentication retry attempts
        """
        self.http_url = http_url
        self.agent_token = agent_token
        self.agent_name = agent_name
        self.version = version
        self.capabilities = capabilities or []
        self.tags = tags or []
        self.token_refresh_threshold = token_refresh_threshold
        self.max_retry_attempts = max_retry_attempts

        self._credentials: Optional[AuthCredentials] = None
        self._token_lock = threading.Lock()
        self._refresh_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()

    def authenticate(self) -> AuthCredentials:
        """Authenticate with AgentToken and get credentials.

        Returns:
            AuthCredentials with access token, agent ID, ws URL, etc.

        Raises:
            SystemExit: If all authentication attempts fail
        """
        with self._token_lock:
            for attempt in range(1, self.max_retry_attempts + 1):
                try:
                    logger.info(
                        f"Attempting authentication "
                        f"(attempt {attempt}/{self.max_retry_attempts})"
                    )

                    auth_response = authenticate_agent(
                        http_url=self.http_url,
                        agent_token=self.agent_token,
                        agent_name=self.agent_name,
                        version=self.version,
                        capabilities=self.capabilities,
                        tags=self.tags,
                    )

                    self._credentials = AuthCredentials(
                        agent_id=auth_response.agent_id,
                        organization_id=auth_response.organization_id,
                        access_token=auth_response.access_token,
                        refresh_token=auth_response.refresh_token,
                        session_id=auth_response.session_id,
                        ws_url=auth_response.ws_url,
                        token_expires_at=datetime.now()
                        + timedelta(hours=DEFAULT_TOKEN_VALIDITY_HOURS),
                    )

                    logger.info(
                        "Authentication successful, "
                        f"agent ID: {self._credentials.agent_id}"
                    )
                    logger.info(f"WebSocket URL: {self._credentials.ws_url}")
                    logger.info(
                        f"Token expires at: {self._credentials.token_expires_at}"
                    )

                    self._start_token_refresh_monitor()
                    return self._credentials

                except Exception as e:
                    logger.error(f"Authentication attempt {attempt} failed: {e}")

                if attempt < self.max_retry_attempts:
                    delay = min(MAX_RETRY_DELAY_SECONDS, 2**attempt)
                    logger.info(f"Retrying authentication in {delay} seconds...")
                    time.sleep(delay)

            logger.critical("All authentication attempts failed")
            raise SystemExit("Authentication failed after all attempts")

    def get_token(self) -> Optional[str]:
        """Get current access token, refreshing if necessary.

        Returns:
            Current valid access token or None if authentication failed
        """
        with self._token_lock:
            if self._should_refresh_token():
                try:
                    self._refresh_token()
                except Exception as e:
                    logger.error(f"Token refresh failed: {e}")
                    return None
            return self._credentials.access_token if self._credentials else None

    def get_credentials(self) -> Optional[AuthCredentials]:
        """Get full credentials including agent ID, ws URL, etc."""
        return self._credentials

    def get_agent_id(self) -> Optional[int]:
        """Get the agent ID assigned by server."""
        return self._credentials.agent_id if self._credentials else None

    def get_ws_url(self) -> Optional[str]:
        """Get the WebSocket URL to connect to."""
        return self._credentials.ws_url if self._credentials else None

    def get_session_id(self) -> Optional[str]:
        """Get the session ID for tracking."""
        return self._credentials.session_id if self._credentials else None

    def _should_refresh_token(self) -> bool:
        """Check if token should be refreshed."""
        if not self._credentials or not self._credentials.access_token:
            return True

        if not self._credentials.token_expires_at:
            return False

        time_until_expiry = (
            self._credentials.token_expires_at - datetime.now()
        ).total_seconds()
        return time_until_expiry <= self.token_refresh_threshold

    def _refresh_token(self) -> None:
        """Refresh the authentication token using refresh token."""
        if not self._credentials or not self._credentials.refresh_token:
            logger.warning("No refresh token available, re-authenticating")
            self.authenticate()
            return

        logger.info("Refreshing access token")

        try:
            tokens = refresh_access_token(
                http_url=self.http_url,
                refresh_token=self._credentials.refresh_token,
            )

            self._credentials.access_token = tokens["accessToken"]
            self._credentials.refresh_token = tokens["refreshToken"]
            self._credentials.token_expires_at = datetime.now() + timedelta(
                hours=DEFAULT_TOKEN_VALIDITY_HOURS
            )

            logger.info(
                f"Token refreshed, expires at: {self._credentials.token_expires_at}"
            )

        except Exception as e:
            logger.warning(f"Token refresh failed: {e}, re-authenticating")
            # Clear credentials and re-authenticate with AgentToken
            self._credentials = None
            self.authenticate()

    def _start_token_refresh_monitor(self) -> None:
        """Start background token refresh monitoring."""
        if self._refresh_thread and self._refresh_thread.is_alive():
            return

        self._refresh_thread = threading.Thread(
            target=self._token_refresh_worker,
            name="TokenRefreshWorker",
            daemon=True,
        )
        self._refresh_thread.start()

    def _token_refresh_worker(self) -> None:
        """Background worker for token refresh."""
        while not self._shutdown_event.is_set():
            try:
                if self._should_refresh_token():
                    with self._token_lock:
                        if self._should_refresh_token():  # Double-check with lock
                            self._refresh_token()

                # Check periodically
                time.sleep(TOKEN_CHECK_INTERVAL_SECONDS)

            except Exception as e:
                logger.error(f"Token refresh worker error: {e}")
                time.sleep(TOKEN_CHECK_INTERVAL_SECONDS)

    def is_token_valid(self) -> bool:
        """Check if current token is valid."""
        if not self._credentials or not self._credentials.access_token:
            return False
        if not self._credentials.token_expires_at:
            return True
        return datetime.now() < self._credentials.token_expires_at

    def get_token_info(self) -> dict:
        """Get token information for debugging."""
        return {
            "has_token": bool(self._credentials and self._credentials.access_token),
            "agent_id": self._credentials.agent_id if self._credentials else None,
            "session_id": self._credentials.session_id if self._credentials else None,
            "ws_url": self._credentials.ws_url if self._credentials else None,
            "expires_at": (
                self._credentials.token_expires_at.isoformat()
                if self._credentials and self._credentials.token_expires_at
                else None
            ),
            "is_valid": self.is_token_valid(),
            "should_refresh": self._should_refresh_token(),
        }

    def stop(self) -> None:
        """Stop the authentication service."""
        logger.info("Stopping authentication service")
        self._shutdown_event.set()

        if self._refresh_thread and self._refresh_thread.is_alive():
            self._refresh_thread.join(timeout=5)
