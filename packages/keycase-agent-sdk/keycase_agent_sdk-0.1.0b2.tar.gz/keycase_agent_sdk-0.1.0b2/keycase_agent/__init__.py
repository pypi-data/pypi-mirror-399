"""Keycase Agent SDK - Python SDK for Keycase automation platform.

This package provides a robust agent for executing keyword-based automation
flows, with support for both WebSocket (server-connected) and local execution modes.

Basic Usage:
    # WebSocket mode (connects to Keycase server)
    from keycase_agent import KeycaseAgent, load_config, load_keywords

    load_keywords('my_keywords')  # Load your keyword files
    config = load_config()
    agent = KeycaseAgent(config)
    agent.start()

    # Local mode (standalone execution)
    from keycase_agent import ExecutionManager, load_keywords

    load_keywords('my_keywords')  # Load your keyword files
    manager = ExecutionManager(mode='local')
    results = manager.execute_local(execution_plan)
"""

from .agent import KeycaseAgent
from .auth import AuthService
from .config import load_config
from .decorators import (
    AfterRun,
    BeforeRun,
    ParamDirection,
    ParamType,
    get_all_keyword_schemas,
    get_keyword_schema,
    input_param,
    keyword,
    output_param,
    param,
)
from .exceptions import (
    AuthenticationError,
    ExecutionError,
    KeycaseError,
    KeywordDefinitionError,
    ParameterValidationError,
)
from .execution_manager import ExecutionManager
from .loader import load_keywords
from .models.execution_result import ExecutionResultData, FlowResult, StatusEnum
from .state_tracker import AgentStateTracker
from .websocket_client import ConnectionState, WebSocketClient

__version__ = "0.1.0"
__author__ = "Keycase Team"

__all__ = [
    # Main classes
    "KeycaseAgent",
    "ExecutionManager",
    "AuthService",
    "WebSocketClient",
    "AgentStateTracker",
    # Configuration
    "load_config",
    "load_keywords",
    # Keyword decorators
    "keyword",
    "param",
    "input_param",
    "output_param",
    # Hook decorators
    "BeforeRun",
    "AfterRun",
    # Parameter types
    "ParamType",
    "ParamDirection",
    # Schema utilities
    "get_keyword_schema",
    "get_all_keyword_schemas",
    # Exceptions
    "KeycaseError",
    "KeywordDefinitionError",
    "ParameterValidationError",
    "ExecutionError",
    "AuthenticationError",
    # Models
    "ExecutionResultData",
    "FlowResult",
    "StatusEnum",
    "ConnectionState",
    # Version info
    "__version__",
]


def start_agent() -> None:
    """Entry point for starting the Keycase agent from command line."""
    load_keywords()
    config = load_config()
    agent = KeycaseAgent(config)
    agent.start()
