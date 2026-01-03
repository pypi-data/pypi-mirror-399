"""Tests for Agent retry functionality."""

import pytest
import json
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from keycase_agent.agent import KeycaseAgent
from keycase_agent.auth import AuthService, AuthCredentials
from keycase_agent.utils.auth_helper import ApiResponse
from datetime import datetime, timedelta


class TestAgentRetry:
    """Test suite for Agent retry functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for test
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create mock auth credentials
        self.mock_credentials = AuthCredentials(
            agent_id=123,
            organization_id=1,
            access_token='test_token',
            refresh_token='test_refresh_token',
            session_id='test_session_id',
            ws_url='ws://localhost:8080/websocket',
            token_expires_at=datetime.now() + timedelta(hours=24)
        )

        # Mock dependencies
        self.mock_auth_service = Mock(spec=AuthService)
        self.mock_auth_service.get_token.return_value = "test_token"
        self.mock_auth_service.authenticate.return_value = self.mock_credentials

        config = {
            "HTTP_URL": "http://localhost:8080/api",
            "AGENT_TOKEN": "agt_test_token_123456789",
            "AGENT_NAME": "test-agent-01",
            "AGENT_VERSION": "1.0.0",
            "AGENT_CAPABILITIES": [],
            "AGENT_TAGS": []
        }

        # Patch the AuthService to avoid actual authentication
        with patch.object(AuthService, '__init__', lambda self, **kwargs: None):
            self.agent = KeycaseAgent(config)

        self.agent.auth_service = self.mock_auth_service
        self.agent.agent_id = 123
        self.agent.agent_name = "test-agent-01"

    def teardown_method(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_result_locally_success(self):
        """Test successful local result saving."""
        project_id = 123
        run_id = 456
        result = {"status": "success", "data": "test_result"}
        reason = "Test reason"

        # Execute
        self.agent._save_result_locally(project_id, run_id, result, reason)

        # Verify directory was created
        results_dir = os.path.join(self.test_dir, "failed_results")
        assert os.path.exists(results_dir)

        # Verify result file was created
        result_files = [f for f in os.listdir(results_dir) if f.startswith(f"result_p{project_id}_r{run_id}")]
        assert len(result_files) == 1

        # Verify file content
        result_file = os.path.join(results_dir, result_files[0])
        with open(result_file, 'r') as f:
            saved_data = json.load(f)

        assert saved_data["metadata"]["project_id"] == project_id
        assert saved_data["metadata"]["run_id"] == run_id
        assert saved_data["metadata"]["reason"] == reason
        assert saved_data["metadata"]["agent_id"] == 123
        assert saved_data["metadata"]["agent_name"] == "test-agent-01"
        assert saved_data["result"] == result

        # Verify summary file was created
        summary_file = os.path.join(results_dir, "failed_results_summary.json")
        assert os.path.exists(summary_file)

        with open(summary_file, 'r') as f:
            summary_data = json.load(f)

        assert len(summary_data["failed_results"]) == 1
        assert summary_data["failed_results"][0]["project_id"] == project_id
        assert summary_data["failed_results"][0]["run_id"] == run_id

    @patch('keycase_agent.agent.auth_request_with_details')
    def test_send_result_success_first_attempt(self, mock_auth_request):
        """Test successful result sending on first attempt."""
        # Setup mocks - successful response
        mock_auth_request.return_value = ApiResponse(
            success=True,
            data={"status": "saved"},
            status_code=200
        )

        project_id = 123
        run_id = 456
        result = {"status": "success"}

        # Execute
        response = self.agent._send_result(project_id, run_id, result)

        # Verify
        assert response == {"status": "saved"}
        mock_auth_request.assert_called_once()

        # Verify no local file was created
        results_dir = os.path.join(self.test_dir, "failed_results")
        assert not os.path.exists(results_dir)

    @patch('keycase_agent.agent.auth_request_with_details')
    @patch('time.sleep')
    def test_send_result_success_after_retry(self, mock_sleep, mock_auth_request):
        """Test successful result sending after retries."""
        # Setup mocks - fail first 2 attempts, succeed on 3rd
        mock_auth_request.side_effect = [
            ApiResponse(success=False, error_code=500, error_message="Server error"),
            ApiResponse(success=False, error_code=500, error_message="Server error"),
            ApiResponse(success=True, data={"status": "saved"}, status_code=200)
        ]

        project_id = 123
        run_id = 456
        result = {"status": "success"}

        # Execute
        response = self.agent._send_result(project_id, run_id, result)

        # Verify
        assert response == {"status": "saved"}
        assert mock_auth_request.call_count == 3
        assert mock_sleep.call_count == 2  # Sleep between retries

        # Verify no local file was created
        results_dir = os.path.join(self.test_dir, "failed_results")
        assert not os.path.exists(results_dir)

    @patch('keycase_agent.agent.auth_request_with_details')
    @patch('time.sleep')
    def test_send_result_all_attempts_fail_saves_locally(self, mock_sleep, mock_auth_request):
        """Test all attempts fail and result is saved locally."""
        # Setup mocks - all attempts fail
        mock_auth_request.return_value = ApiResponse(
            success=False,
            error_code=500,
            error_message="Server error"
        )

        project_id = 123
        run_id = 456
        result = {"status": "success"}

        # Execute
        response = self.agent._send_result(project_id, run_id, result)

        # Verify
        assert response is None
        assert mock_auth_request.call_count == 3  # All 3 attempts
        assert mock_sleep.call_count == 2  # Sleep between retries

        # Verify local file was created
        results_dir = os.path.join(self.test_dir, "failed_results")
        assert os.path.exists(results_dir)

        result_files = [f for f in os.listdir(results_dir) if f.startswith(f"result_p{project_id}_r{run_id}")]
        assert len(result_files) == 1

    def test_send_result_no_token_saves_locally(self):
        """Test no token available saves result locally."""
        # Setup - no token
        self.mock_auth_service.get_token.return_value = None

        project_id = 123
        run_id = 456
        result = {"status": "success"}

        # Execute
        response = self.agent._send_result(project_id, run_id, result)

        # Verify
        assert response is None

        # Verify local file was created
        results_dir = os.path.join(self.test_dir, "failed_results")
        assert os.path.exists(results_dir)

        # Verify the reason is correct
        summary_file = os.path.join(results_dir, "failed_results_summary.json")
        with open(summary_file, 'r') as f:
            summary_data = json.load(f)

        assert summary_data["failed_results"][0]["reason"] == "No authentication token"

    @patch('keycase_agent.agent.auth_request_with_details')
    @patch('time.sleep')
    def test_send_result_exception_during_request(self, mock_sleep, mock_auth_request):
        """Test exception during request is handled."""
        # Setup mocks - exception on all attempts
        mock_auth_request.side_effect = Exception("Network error")

        project_id = 123
        run_id = 456
        result = {"status": "success"}

        # Execute
        response = self.agent._send_result(project_id, run_id, result)

        # Verify
        assert response is None
        assert mock_auth_request.call_count == 3  # All 3 attempts

        # Verify local file was created
        results_dir = os.path.join(self.test_dir, "failed_results")
        assert os.path.exists(results_dir)

    @patch('keycase_agent.agent.auth_request_with_details')
    def test_send_result_already_completed_treated_as_success(self, mock_auth_request):
        """Test 'already completed' error (code 5002) is treated as success."""
        # Setup mocks - already completed error
        mock_auth_request.return_value = ApiResponse(
            success=False,
            data={"code": 5002, "message": "Execution run is already completed"},
            status_code=400,
            error_code=5002,
            error_message="Execution run is already completed"
        )

        project_id = 123
        run_id = 456
        result = {"status": "success"}

        # Execute
        response = self.agent._send_result(project_id, run_id, result)

        # Verify - should be treated as success
        assert response is not None
        mock_auth_request.assert_called_once()  # No retries needed

        # Verify no local file was created
        results_dir = os.path.join(self.test_dir, "failed_results")
        assert not os.path.exists(results_dir)
