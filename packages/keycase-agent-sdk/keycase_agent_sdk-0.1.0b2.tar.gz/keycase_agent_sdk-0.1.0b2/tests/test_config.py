"""Tests for configuration module."""

import pytest
import os
from unittest.mock import patch
from keycase_agent.config import require_env, load_config, validate_agent_token, parse_list


class TestRequireEnv:
    """Test suite for require_env function."""

    def test_require_env_success(self):
        """Test require_env returns value when environment variable exists."""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = require_env('TEST_VAR')
            assert result == 'test_value'

    def test_require_env_missing_raises_error(self):
        """Test require_env raises error when environment variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(EnvironmentError, match="Missing required environment variable: MISSING_VAR"):
                require_env('MISSING_VAR')

    def test_require_env_empty_string_is_allowed(self):
        """Test require_env returns empty string when variable is empty."""
        with patch.dict(os.environ, {'EMPTY_VAR': ''}):
            result = require_env('EMPTY_VAR')
            assert result == ''


class TestValidateAgentToken:
    """Test suite for validate_agent_token function."""

    def test_valid_token(self):
        """Test valid token passes validation."""
        token = 'agt_abc123xyz789'
        result = validate_agent_token(token)
        assert result == token

    def test_invalid_prefix(self):
        """Test token without agt_ prefix fails."""
        with pytest.raises(ValueError, match="AGENT_TOKEN must start with 'agt_'"):
            validate_agent_token('invalid_token')

    def test_token_too_short(self):
        """Test token that is too short fails."""
        with pytest.raises(ValueError, match="AGENT_TOKEN is too short"):
            validate_agent_token('agt_abc')


class TestParseList:
    """Test suite for parse_list function."""

    def test_parse_comma_separated(self):
        """Test parsing comma-separated values."""
        result = parse_list('selenium,api,web')
        assert result == ['selenium', 'api', 'web']

    def test_parse_with_spaces(self):
        """Test parsing with extra spaces."""
        result = parse_list('selenium , api , web')
        assert result == ['selenium', 'api', 'web']

    def test_parse_empty_string(self):
        """Test parsing empty string returns empty list."""
        result = parse_list('')
        assert result == []

    def test_parse_none(self):
        """Test parsing None returns empty list."""
        result = parse_list(None)
        assert result == []

    def test_parse_single_value(self):
        """Test parsing single value."""
        result = parse_list('selenium')
        assert result == ['selenium']


class TestLoadConfig:
    """Test suite for load_config function."""

    def test_load_config_success(self):
        """Test load_config returns proper configuration when all vars exist."""
        env_vars = {
            'HTTP_URL': 'http://test.com/api',
            'AGENT_TOKEN': 'agt_test_token_123456789',
            'AGENT_NAME': 'test-agent-01'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()

            assert config['HTTP_URL'] == 'http://test.com/api'
            assert config['AGENT_TOKEN'] == 'agt_test_token_123456789'
            assert config['AGENT_NAME'] == 'test-agent-01'
            assert config['AGENT_VERSION'] == '1.0.0'  # Default value
            assert config['AGENT_CAPABILITIES'] == []  # Default value
            assert config['AGENT_TAGS'] == []  # Default value

    def test_load_config_with_optional_vars(self):
        """Test load_config includes optional variables when set."""
        env_vars = {
            'HTTP_URL': 'http://test.com/api',
            'AGENT_TOKEN': 'agt_test_token_123456789',
            'AGENT_NAME': 'test-agent-01',
            'AGENT_VERSION': '2.0.0',
            'AGENT_CAPABILITIES': 'selenium,api',
            'AGENT_TAGS': 'production,windows'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()

            assert config['AGENT_VERSION'] == '2.0.0'
            assert config['AGENT_CAPABILITIES'] == ['selenium', 'api']
            assert config['AGENT_TAGS'] == ['production', 'windows']

    def test_load_config_missing_http_url(self):
        """Test load_config raises error when HTTP_URL is missing."""
        env_vars = {
            'AGENT_TOKEN': 'agt_test_token_123456789',
            'AGENT_NAME': 'test-agent-01'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(EnvironmentError, match="Missing required environment variable: HTTP_URL"):
                load_config()

    def test_load_config_missing_agent_token(self):
        """Test load_config raises error when AGENT_TOKEN is missing."""
        env_vars = {
            'HTTP_URL': 'http://test.com/api',
            'AGENT_NAME': 'test-agent-01'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(EnvironmentError, match="Missing required environment variable: AGENT_TOKEN"):
                load_config()

    def test_load_config_missing_agent_name(self):
        """Test load_config raises error when AGENT_NAME is missing."""
        env_vars = {
            'HTTP_URL': 'http://test.com/api',
            'AGENT_TOKEN': 'agt_test_token_123456789'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(EnvironmentError, match="Missing required environment variable: AGENT_NAME"):
                load_config()

    def test_load_config_invalid_agent_token(self):
        """Test load_config raises error when AGENT_TOKEN is invalid."""
        env_vars = {
            'HTTP_URL': 'http://test.com/api',
            'AGENT_TOKEN': 'invalid_token',
            'AGENT_NAME': 'test-agent-01'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="AGENT_TOKEN must start with 'agt_'"):
                load_config()

    def test_load_config_empty_agent_name(self):
        """Test load_config raises error when AGENT_NAME is empty."""
        env_vars = {
            'HTTP_URL': 'http://test.com/api',
            'AGENT_TOKEN': 'agt_test_token_123456789',
            'AGENT_NAME': '   '
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="AGENT_NAME cannot be empty"):
                load_config()

    def test_load_config_returns_dict(self):
        """Test load_config returns a dictionary."""
        env_vars = {
            'HTTP_URL': 'http://test.com/api',
            'AGENT_TOKEN': 'agt_test_token_123456789',
            'AGENT_NAME': 'test-agent-01'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()
            assert isinstance(config, dict)
            assert len(config) == 6  # HTTP_URL, AGENT_TOKEN, AGENT_NAME, AGENT_VERSION, AGENT_CAPABILITIES, AGENT_TAGS
