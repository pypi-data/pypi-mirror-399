import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


def require_env(name: str) -> str:
    """Get required environment variable or raise error.

    Args:
        name: Environment variable name

    Returns:
        Environment variable value

    Raises:
        EnvironmentError: If variable is not set
    """
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get optional environment variable with default.

    Args:
        name: Environment variable name
        default: Default value if not set

    Returns:
        Environment variable value or default
    """
    return os.getenv(name, default)


def validate_url(url: str, name: str) -> str:
    """Validate URL format.

    Args:
        url: URL to validate
        name: Name of the URL for error messages

    Returns:
        Validated URL

    Raises:
        ValueError: If URL is invalid
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid {name}: missing scheme or netloc")
        return url
    except Exception as e:
        raise ValueError(f"Invalid {name}: {e}")


def validate_agent_token(token: str) -> str:
    """Validate AgentToken format.

    Args:
        token: AgentToken to validate

    Returns:
        Validated token

    Raises:
        ValueError: If token format is invalid
    """
    if not token.startswith("agt_"):
        raise ValueError("AGENT_TOKEN must start with 'agt_'")
    if len(token) < 10:
        raise ValueError("AGENT_TOKEN is too short")
    return token


def parse_list(value: Optional[str]) -> List[str]:
    """Parse comma-separated string into list.

    Args:
        value: Comma-separated string or None

    Returns:
        List of strings (empty if value is None)
    """
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables.

    Required:
        HTTP_URL: Base HTTP API URL
        AGENT_TOKEN: AgentToken (must start with 'agt_')
        AGENT_NAME: Unique agent name within organization

    Optional:
        AGENT_VERSION: Agent version (default: "1.0.0")
        AGENT_CAPABILITIES: Comma-separated list of capabilities
        AGENT_TAGS: Comma-separated list of tags

    Returns:
        Configuration dictionary

    Raises:
        EnvironmentError: If required variables are missing
        ValueError: If configuration values are invalid
    """
    http_url = require_env("HTTP_URL")
    agent_token = require_env("AGENT_TOKEN")
    agent_name = require_env("AGENT_NAME")

    # Optional configuration
    agent_version = get_env("AGENT_VERSION", "1.0.0")
    capabilities_str = get_env("AGENT_CAPABILITIES", "")
    tags_str = get_env("AGENT_TAGS", "")

    # Validate configuration
    validate_url(http_url, "HTTP_URL")
    validate_agent_token(agent_token)

    if not agent_name.strip():
        raise ValueError("AGENT_NAME cannot be empty")

    return {
        "HTTP_URL": http_url,
        "AGENT_TOKEN": agent_token,
        "AGENT_NAME": agent_name,
        "AGENT_VERSION": agent_version,
        "AGENT_CAPABILITIES": parse_list(capabilities_str),
        "AGENT_TAGS": parse_list(tags_str),
    }
