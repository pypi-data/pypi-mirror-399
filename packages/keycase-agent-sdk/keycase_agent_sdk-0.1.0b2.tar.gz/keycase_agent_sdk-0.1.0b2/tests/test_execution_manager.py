"""Tests for ExecutionManager class."""

import pytest
import json
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from keycase_agent.execution_manager import ExecutionManager
from keycase_agent.models.execution_result import ExecutionResultData, FlowResult, StatusEnum


class TestExecutionManager:
    """Test suite for ExecutionManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.send_result_callback = Mock()
        self.update_status_callback = Mock()
        self.manager = ExecutionManager(
            send_result_callback=self.send_result_callback,
            update_status_callback=self.update_status_callback
        )

    def test_init(self):
        """Test ExecutionManager initialization."""
        assert self.manager.execution_tracker == {}
        assert self.manager.execution_thread is None
        assert not self.manager.stop_execution.is_set()
        assert self.manager.send_result_callback == self.send_result_callback
        assert self.manager.update_status_callback == self.update_status_callback

    def test_is_running_false_initially(self):
        """Test is_running returns False initially."""
        assert not self.manager.is_running()

    def test_is_running_true_when_thread_active(self):
        """Test is_running returns True when thread is active."""
        # Create a mock thread that appears to be alive
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        self.manager.execution_thread = mock_thread

        assert self.manager.is_running()

    def test_stop_sets_stop_event(self):
        """Test stop method sets stop event."""
        self.manager.stop()
        assert self.manager.stop_execution.is_set()

    def test_stop_waits_for_thread(self):
        """Test stop method waits for thread to finish."""
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        self.manager.execution_thread = mock_thread

        self.manager.stop()

        mock_thread.join.assert_called_once_with(timeout=10)

    @patch('keycase_agent.execution_manager.execute_plan_from_json')
    @patch('keycase_agent.execution_manager.set_context')
    @patch('keycase_agent.execution_manager.clear_context')
    def test_process_plan_basic_flow(self, mock_clear_context, mock_set_context, mock_execute_plan):
        """Test basic execution flow processing."""
        # Mock the execution plan parsing
        mock_keyword_instance = Mock()
        mock_keyword_instance.id = 1
        mock_keyword_instance.keywordName = "test_keyword"
        mock_keyword_instance.params = []

        mock_flow = Mock()
        mock_flow.id = 1
        mock_flow.name = "test_flow"
        mock_flow.steps = []

        mock_execute_plan.return_value = ([mock_keyword_instance], [mock_flow])

        # Execute
        self.manager._process_plan(1, 100, '{"test": "plan"}')

        # Verify context management
        mock_set_context.assert_called_once_with(100, 1)
        mock_clear_context.assert_called_once()

        # Verify status callback
        self.update_status_callback.assert_called_with(False)

    def test_process_plan_handles_empty_plan(self):
        """Test processing handles empty execution plan by logging error."""
        # Empty plan should be handled gracefully (error logged, not raised)
        # The method catches exceptions and logs them
        self.manager._process_plan(1, 100, "")

        # Verify status callback was still called (in finally block)
        self.update_status_callback.assert_called_with(False)

    @patch('keycase_agent.decorators.keyword_registry')
    def test_execute_flow_success(self, mock_registry):
        """Test successful flow execution."""
        # Setup mocks - create a proper mock function with metadata
        mock_func = Mock(return_value={})
        mock_func.keyword_params = []  # No param metadata (must match getattr in code)
        mock_registry.get.return_value = mock_func

        # Create a proper KeywordInstance-like mock
        mock_instance = Mock()
        mock_instance.id = 1
        mock_instance.keywordName = "test_keyword"
        mock_instance.params = []  # Empty list, not Mock
        mock_instance.name = "Test Keyword"

        mock_step = Mock()
        mock_step.instanceId = 1
        mock_step.sequenceOrder = 1
        mock_step.connections = []  # Empty connections list

        mock_flow = Mock()
        mock_flow.id = 1
        mock_flow.name = "test_flow"
        mock_flow.steps = [mock_step]
        mock_flow.runMode = None
        mock_flow.connections = []  # Empty connections list

        keyword_instances = [mock_instance]
        executed_steps = set()

        # Setup execution tracker
        self.manager.execution_tracker["100"] = {
            "startDateTime": "2024-01-01T00:00:00Z",
            "endDateTime": None,
            "flowResults": []
        }

        # Execute
        result = self.manager._execute_flow(100, mock_flow, keyword_instances, executed_steps)

        # Verify result
        assert result.status == StatusEnum.PASSED
        assert result.id == 1
        assert result.name == "test_flow"
        assert (1, 1) in executed_steps

    @patch('keycase_agent.decorators.keyword_registry')
    def test_execute_flow_keyword_not_found(self, mock_registry):
        """Test flow execution when keyword function not found."""
        # Setup mocks
        mock_registry.get.return_value = None

        mock_instance = Mock()
        mock_instance.id = 1
        mock_instance.keywordName = "missing_keyword"
        mock_instance.params = []
        mock_instance.name = "Missing Keyword"

        mock_step = Mock()
        mock_step.instanceId = 1
        mock_step.sequenceOrder = 1
        mock_step.connections = []

        mock_flow = Mock()
        mock_flow.id = 1
        mock_flow.name = "test_flow"
        mock_flow.steps = [mock_step]
        mock_flow.runMode = None
        mock_flow.connections = []  # Empty connections list

        keyword_instances = [mock_instance]
        executed_steps = set()

        # Setup execution tracker
        self.manager.execution_tracker["100"] = {
            "startDateTime": "2024-01-01T00:00:00Z",
            "endDateTime": None,
            "flowResults": []
        }

        # Execute
        result = self.manager._execute_flow(100, mock_flow, keyword_instances, executed_steps)

        # Verify result
        assert result.status == StatusEnum.FAILED
        assert result.message is not None
        assert "Function for missing_keyword not found" in result.message
        assert result.failedOnStepId == 1

    @patch('keycase_agent.decorators.keyword_registry')
    def test_execute_flow_keyword_exception(self, mock_registry):
        """Test flow execution when keyword raises exception."""
        # Setup mocks
        mock_func = Mock()
        mock_func.keyword_params = []  # No param metadata (must match getattr in code)
        mock_func.side_effect = Exception("Keyword execution failed")
        mock_registry.get.return_value = mock_func

        mock_instance = Mock()
        mock_instance.id = 1
        mock_instance.keywordName = "failing_keyword"
        mock_instance.params = []
        mock_instance.name = "Failing Keyword"

        mock_step = Mock()
        mock_step.instanceId = 1
        mock_step.sequenceOrder = 1
        mock_step.connections = []

        mock_flow = Mock()
        mock_flow.id = 1
        mock_flow.name = "test_flow"
        mock_flow.steps = [mock_step]
        mock_flow.runMode = None
        mock_flow.connections = []  # Empty connections list

        keyword_instances = [mock_instance]
        executed_steps = set()

        # Setup execution tracker
        self.manager.execution_tracker["100"] = {
            "startDateTime": "2024-01-01T00:00:00Z",
            "endDateTime": None,
            "flowResults": []
        }

        # Execute
        result = self.manager._execute_flow(100, mock_flow, keyword_instances, executed_steps)

        # Verify result
        assert result.status == StatusEnum.FAILED
        assert result.message == "Keyword execution failed"
        assert result.failedOnStepId == 1

    def test_record_flow_result(self):
        """Test recording flow result in execution tracker."""
        # Setup
        run_id = 100
        flow_result = FlowResult(1, "test_flow")
        flow_result.set_status(StatusEnum.PASSED)
        flow_result.started_execution()
        flow_result.completed_execution()

        # Initialize tracker with string key (as used by the implementation)
        self.manager.execution_tracker[str(run_id)] = {
            "startDateTime": "2024-01-01T00:00:00Z",
            "endDateTime": None,
            "flowResults": []
        }

        # Execute
        self.manager._record_flow_result(run_id, flow_result)

        # Verify
        flow_results = self.manager.execution_tracker[str(run_id)]["flowResults"]
        assert len(flow_results) == 1
        assert flow_results[0]["id"] == 1
        assert flow_results[0]["name"] == "test_flow"
        assert flow_results[0]["status"] == "PASSED"

    def test_mark_aborted_steps(self):
        """Test marking unexecuted steps as aborted."""
        # Setup
        run_id = 100
        executed_steps = {(1, 1)}  # Only step 1 of flow 1 was executed

        mock_step1 = Mock()
        mock_step1.instanceId = 1
        mock_step2 = Mock()
        mock_step2.instanceId = 2

        mock_flow = Mock()
        mock_flow.id = 1
        mock_flow.name = "test_flow"
        mock_flow.steps = [mock_step1, mock_step2]

        flows = [mock_flow]
        result_data = ExecutionResultData(run_id)

        # Initialize tracker with string key
        self.manager.execution_tracker[str(run_id)] = {
            "startDateTime": "2024-01-01T00:00:00Z",
            "endDateTime": None,
            "flowResults": []
        }

        # Execute
        self.manager._mark_aborted_steps(run_id, flows, executed_steps, result_data)

        # Verify
        assert len(result_data.flowResults) == 1
        aborted_result = result_data.flowResults[0]
        assert aborted_result.status == StatusEnum.ABORTED
        assert aborted_result.message == "Execution aborted"

    def test_start_execution_creates_thread(self):
        """Test start_execution creates and starts a thread."""
        project_id = 1
        run_id = 100
        plan_json = '{"test": "plan"}'

        # Execute
        self.manager.start_execution(project_id, run_id, plan_json)

        # Verify thread is created and started
        assert self.manager.execution_thread is not None
        assert self.manager.execution_thread.name == f"ExecutionThread-{run_id}"
        assert not self.manager.stop_execution.is_set()

        # Clean up
        self.manager.stop()

    def test_create_skipped_flow_result(self):
        """Test creating a skipped flow result."""
        # Setup
        mock_flow = Mock()
        mock_flow.id = 1
        mock_flow.name = "test_flow"

        # Execute
        result = self.manager._create_skipped_flow_result(mock_flow)

        # Verify result
        assert result.status == StatusEnum.SKIPPED
        assert result.id == 1
        assert result.name == "test_flow"
        assert result.message == "Flow skipped due to Skip run mode"
        assert result.runAt is not None
        assert result.completedAt is not None

    @patch('keycase_agent.execution_manager.execute_plan_from_json')
    @patch('keycase_agent.execution_manager.set_context')
    @patch('keycase_agent.execution_manager.clear_context')
    def test_process_plan_skip_mode(self, mock_clear_context, mock_set_context, mock_execute_plan):
        """Test processing execution plan with Skip mode flow."""
        from keycase_agent.models.execution_run_mode_types import ExecutionPlanRunMode

        # Setup mocks
        mock_flow = Mock()
        mock_flow.id = 1
        mock_flow.name = "skipped_flow"
        mock_flow.runMode = ExecutionPlanRunMode.Skip.value
        mock_flow.steps = []

        mock_execute_plan.return_value = ([], [mock_flow])

        # Execute
        self.manager._process_plan(1, 100, '{"test": "plan"}')

        # Verify skipped flow was recorded
        self.send_result_callback.assert_called_once()
        call_args = self.send_result_callback.call_args[0]

        # Check the result data
        result_data = call_args[2]
        assert len(result_data['flowResults']) == 1

        flow_result = result_data['flowResults'][0]
        assert flow_result['status'] == 'SKIPPED'
        assert flow_result['name'] == 'skipped_flow'
