import logging
import platform
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from ..exceptions import LoginError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentAuthResponse:
    """Response from agent authentication."""

    agent_id: int
    organization_id: int
    access_token: str
    refresh_token: str
    session_id: str
    ws_url: str


def authenticate_agent(
    http_url: str,
    agent_token: str,
    agent_name: str,
    version: str = "1.0.0",
    capabilities: Optional[list] = None,
    tags: Optional[list] = None,
) -> AgentAuthResponse:
    """Authenticate agent with AgentToken and get access credentials.

    Args:
        http_url: Base HTTP API URL
        agent_token: AgentToken (must start with 'agt_')
        agent_name: Unique agent name within organization
        version: Agent version
        capabilities: List of capabilities the agent supports
        tags: List of labels for categorization

    Returns:
        AgentAuthResponse with credentials and connection info

    Raises:
        LoginError: If authentication fails
    """
    url = f"{http_url}/agents/authenticate"

    payload = {
        "token": agent_token,
        "name": agent_name,
        "version": version,
        "os": platform.system().lower(),
        "osVersion": platform.release(),
        "architecture": platform.machine(),
        "runtime": (
            f"python-{sys.version_info.major}."
            f"{sys.version_info.minor}.{sys.version_info.micro}"
        ),
        "capabilities": capabilities or [],
        "tags": tags or [],
    }

    response = None
    try:
        logger.info(f"Authenticating agent '{agent_name}' at {url}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        auth_response = AgentAuthResponse(
            agent_id=data["agentId"],
            organization_id=data["organizationId"],
            access_token=data["token"],
            refresh_token=data["refreshToken"],
            session_id=data["sessionId"],
            ws_url=data["wsUrl"],
        )

        logger.info(
            f"Authentication successful for agent '{agent_name}' "
            f"(ID: {auth_response.agent_id})"
        )
        return auth_response

    except requests.exceptions.HTTPError as e:
        status_code = response.status_code if response else None
        logger.error(f"Agent authentication failed: {e}")
        raise LoginError(f"Agent authentication failed: {e}", status_code=status_code)
    except Exception as e:
        logger.error(f"Agent authentication failed: {e}")
        raise LoginError(f"Agent authentication failed: {e}", status_code=None)


def refresh_access_token(http_url: str, refresh_token: str) -> Dict[str, str]:
    """Refresh an expired access token.

    Args:
        http_url: Base HTTP API URL
        refresh_token: The refresh token

    Returns:
        Dict with new accessToken and refreshToken

    Raises:
        LoginError: If refresh fails
    """
    url = f"{http_url}/auth/refresh"
    payload = {"refreshToken": refresh_token}

    response = None
    try:
        logger.info("Refreshing access token")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        logger.info("Token refresh successful")
        return {
            "accessToken": data["accessToken"],
            "refreshToken": data["refreshToken"],
        }

    except requests.exceptions.HTTPError as e:
        status_code = response.status_code if response else None
        logger.error(f"Token refresh failed: {e}")
        raise LoginError(f"Token refresh failed: {e}", status_code=status_code)
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise LoginError(f"Token refresh failed: {e}", status_code=None)


# Legacy login function - kept for backward compatibility
def login(username: str, password: str, url: str = "http://localhost:3000/api/login"):
    """Legacy login with username/password. Use authenticate_agent() instead."""
    global auth_token
    payload = {"username": username, "password": password}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        auth_token = data["token"]
        logger.info("Login successful")
        return auth_token
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise LoginError(
            f"Login failed: {e}", status_code=response.status_code if response else None
        )


@dataclass
class ApiResponse:
    """Response from API request with error details."""

    success: bool
    data: Any = None
    status_code: Optional[int] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None


def auth_request_with_details(
    method: str, url: str, auth_token: str, data=None, params=None
) -> ApiResponse:
    """Make authenticated API request with detailed response.

    Returns:
        ApiResponse with success status, data, and error details if failed
    """
    if not auth_token:
        return ApiResponse(
            success=False, error_message="No token found. You must login first."
        )

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    response = None
    try:
        response = requests.request(
            method, url, headers=headers, json=data, params=params
        )

        # Parse response body
        response_data = None
        if response.content and response.headers.get("Content-Type", "").startswith(
            "application/json"
        ):
            response_data = response.json()
        else:
            response_data = response.text

        # Check for success
        if 200 <= response.status_code < 300:
            return ApiResponse(
                success=True, data=response_data, status_code=response.status_code
            )
        else:
            # Extract error details from response
            error_code = None
            error_message = str(response_data)
            if isinstance(response_data, dict):
                error_code = response_data.get("code")
                error_message = response_data.get("message", str(response_data))

            logger.warning(
                f"Request failed with status {response.status_code}: {error_message}"
            )
            return ApiResponse(
                success=False,
                data=response_data,
                status_code=response.status_code,
                error_code=error_code,
                error_message=error_message,
            )

    except Exception as e:
        logger.error(f"Request exception: {e}")
        status_code = response.status_code if response is not None else None
        return ApiResponse(success=False, status_code=status_code, error_message=str(e))


# 2. Function to make authenticated API requests (legacy, returns None on error)
def auth_request(method: str, url: str, auth_token: str, data=None, params=None):
    if not auth_token:
        raise Exception("No token found. You must login first.")

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    response = None
    try:
        response = requests.request(
            method, url, headers=headers, json=data, params=params
        )
        response.raise_for_status()

        # Try parsing JSON only if content is not empty
        if response.content and response.headers.get("Content-Type", "").startswith(
            "application/json"
        ):
            return response.json()
        else:
            return response.text  # fallback: return raw text
    except Exception as e:
        logger.error(f"Request failed: {e}")
        if response is not None:
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
        return None
