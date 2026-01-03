"""Execution manager for running keyword-based automation flows."""

import inspect
import json
import logging
import re
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from .decorators import ParamDirection, after_run_hooks, before_run_hooks
from .exceptions import ParameterValidationError
from .execution_context import clear_context, set_context
from .models.execute_plan import (
    Flow,
    FlowConnection,
    KeywordInstance,
    execute_plan_from_json,
)
from .models.execution_result import ExecutionResultData, FlowResult, StatusEnum
from .models.execution_run_mode_types import ExecutionPlanRunMode
from .models.websocket_event_types import WebSocketEventType
from .utils.event_sender import completed_execution, progress_event

logger = logging.getLogger(__name__)

# Type aliases
ResultCallback = Callable[[int, int, Dict[str, Any]], Optional[Any]]
StatusCallback = Callable[[bool], None]
StepOutputs = Dict[int, Dict[int, Any]]


class ExecutionManager:
    """Manages threaded execution of keyword-based automation flows.

    Supports two modes:
    - 'websocket': Connected to server, sends results via callbacks
    - 'local': Standalone execution, stores results locally
    """

    def __init__(
        self,
        send_result_callback: Optional[ResultCallback] = None,
        update_status_callback: Optional[StatusCallback] = None,
        mode: str = "websocket",
    ) -> None:
        """Initialize ExecutionManager with configurable mode.

        Args:
            send_result_callback: Callback for sending results (websocket mode)
            update_status_callback: Callback for status updates (websocket mode)
            mode: 'websocket' or 'local' - determines how results are handled

        Raises:
            ValueError: If websocket mode is selected without required callbacks
        """
        self.execution_tracker: Dict[str, Dict[str, Any]] = {}
        self.execution_tracker_lock = threading.Lock()
        self.execution_thread: Optional[threading.Thread] = None
        self.stop_execution = threading.Event()
        self.mode = mode
        self.local_results: Dict[str, Dict[str, Any]] = {}

        if mode == "websocket":
            if not send_result_callback or not update_status_callback:
                raise ValueError("Callbacks required for websocket mode")
            self.send_result_callback = send_result_callback
            self.update_status_callback = update_status_callback
        else:
            self.send_result_callback = self._store_local_result
            self.update_status_callback = lambda status: None

    def start_execution(
        self,
        project_id: Union[int, str],
        run_id: Union[int, str],
        execution_plan_json: str,
    ) -> None:
        """Start execution of a plan in a background thread.

        Args:
            project_id: Project identifier
            run_id: Run identifier
            execution_plan_json: JSON string of the execution plan
        """
        self.stop_execution.clear()
        self.execution_thread = threading.Thread(
            target=self._process_plan,
            args=(project_id, run_id, execution_plan_json),
            name=f"ExecutionThread-{run_id}",
        )
        self.execution_thread.start()

    def execute_local(
        self,
        execution_plan_json: Union[str, Dict[str, Any]],
        project_id: str = "local",
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a plan locally and return results synchronously.

        Args:
            execution_plan_json: JSON string or dict of execution plan
            project_id: Project ID (defaults to "local")
            run_id: Run ID (auto-generated if not provided)

        Returns:
            Dict containing execution results
        """
        if run_id is None:
            run_id = str(uuid.uuid4())

        # Convert dict to JSON string if needed
        if isinstance(execution_plan_json, dict):
            execution_plan_json = json.dumps(execution_plan_json)

        self.start_execution(project_id, run_id, execution_plan_json)

        if self.execution_thread:
            self.execution_thread.join()

        return self.local_results.get(run_id, {})

    def _store_local_result(
        self,
        project_id: Union[int, str],
        run_id: Union[int, str],
        result: Dict[str, Any],
    ) -> None:
        """Store results locally instead of sending via callback."""
        self.local_results[str(run_id)] = {
            "project_id": project_id,
            "run_id": run_id,
            "result": result,
        }

    def stop(self) -> None:
        """Stop the current execution."""
        self.stop_execution.set()
        if self.execution_thread and self.execution_thread.is_alive():
            logger.info("Waiting for execution thread to stop...")
            self.execution_thread.join(timeout=10)

    def is_running(self) -> bool:
        """Check if execution is currently running."""
        return bool(self.execution_thread and self.execution_thread.is_alive())

    def _process_plan(
        self,
        project_id: Union[int, str],
        run_id: Union[int, str],
        execution_plan_json: str,
    ) -> None:
        """Process and execute an execution plan.

        Args:
            project_id: Project identifier
            run_id: Run identifier
            execution_plan_json: JSON string of the execution plan
        """
        logger.info(
            f"Processing execution plan for run {run_id} in project {project_id}"
        )
        set_context(run_id, project_id)
        result_data = ExecutionResultData(run_id)

        executed_steps: Set[Tuple[int, int]] = set()

        try:
            # Run before hooks
            for hook in before_run_hooks:
                try:
                    logger.info(f"Running before hook: {hook.__name__}")
                    hook()
                except Exception as e:
                    logger.error(f"Before hook {hook.__name__} failed: {e}")
                    raise

            if not execution_plan_json:
                raise ValueError("Empty execution plan JSON")

            keyword_instances, flows = execute_plan_from_json(execution_plan_json)

            result_data.start_execution()

            with self.execution_tracker_lock:
                self.execution_tracker[str(run_id)] = {
                    "startDateTime": datetime.now(timezone.utc).isoformat(),
                    "endDateTime": None,
                    "flowResults": [],
                }

            execution_aborted = False
            for flow in flows:
                if self.stop_execution.is_set() or execution_aborted:
                    break

                # Check if flow should be skipped
                if flow.runMode == ExecutionPlanRunMode.Skip.value:
                    flow_result = self._create_skipped_flow_result(flow)
                    result_data.add_flow_result(flow_result)
                    self._record_flow_result(run_id, flow_result)
                    logger.info(f"Flow {flow.name} skipped due to Skip mode.")
                    continue

                flow_result = self._execute_flow(
                    run_id, flow, keyword_instances, executed_steps
                )
                result_data.add_flow_result(flow_result)
                self._record_flow_result(run_id, flow_result)

                # Check if this flow failed and has AbortOnFailure mode
                if (
                    flow_result.status == StatusEnum.FAILED
                    and flow.runMode == ExecutionPlanRunMode.AbortOnFailure.value
                ):
                    execution_aborted = True
                    logger.info(
                        f"Flow {flow.name} failed with AbortOnFailure mode. "
                        "Aborting remaining flows."
                    )
                    break

            # Handle aborted steps
            if self.stop_execution.is_set() or execution_aborted:
                self._mark_aborted_steps(run_id, flows, executed_steps, result_data)

            result_data.end_execution()
            with self.execution_tracker_lock:
                self.execution_tracker[str(run_id)]["endDateTime"] = datetime.now(
                    timezone.utc
                ).isoformat()

            self.send_result_callback(project_id, run_id, result_data.to_dict())
            with self.execution_tracker_lock:
                if self.mode == "websocket":
                    completed_execution(
                        WebSocketEventType.AGENT_EXECUTION_COMPLETED_NOTIFY,
                        run_id,
                        self.execution_tracker,
                    )
                self.execution_tracker.pop(str(run_id), None)
        except Exception as e:
            logger.error(f"Execution failed: {e}")
        finally:
            # Run after hooks
            for hook in after_run_hooks:
                try:
                    logger.info(f"Running after hook: {hook.__name__}")
                    hook()
                except Exception as e:
                    logger.error(f"After hook {hook.__name__} failed: {e}")
            clear_context()
            self.update_status_callback(False)

    def _execute_flow(
        self,
        run_id: Union[int, str],
        flow: Flow,
        keyword_instances: List[KeywordInstance],
        executed_steps: Set[Tuple[int, int]],
    ) -> FlowResult:
        """Execute a single flow.

        Args:
            run_id: Run identifier
            flow: Flow to execute
            keyword_instances: List of keyword instances
            executed_steps: Set of already executed steps

        Returns:
            FlowResult containing execution outcome
        """
        from .decorators import keyword_registry

        flow_result = FlowResult(flow.id, flow.name)
        flow_result.started_execution()
        flow_result.set_status(StatusEnum.RUNNING)

        if self.mode == "websocket":
            progress_event(
                WebSocketEventType.AGENT_EXECUTION_PROGRESS_NOTIFY, run_id, flow_result
            )

        flow_failed = False
        step_outputs: StepOutputs = {}

        for step in flow.steps:
            if self.stop_execution.is_set():
                break

            executed_steps.add((flow.id, step.instanceId))
            instance = next(
                (i for i in keyword_instances if i.id == step.instanceId), None
            )

            if not instance:
                flow_result.set_failed_on_step_id(step.sequenceOrder)
                flow_result.set_message("Keyword instance not found")
                flow_result.set_status(StatusEnum.FAILED)
                flow_failed = True
                break

            func = keyword_registry.get(instance.keywordName)
            if not func:
                flow_result.set_failed_on_step_id(step.sequenceOrder)
                flow_result.set_message(
                    f"Function for {instance.keywordName} not found"
                )
                flow_result.set_status(StatusEnum.FAILED)
                flow_failed = True
                break

            try:
                # Strict validation: Check JSON params match keyword definition
                self._validate_parameters(
                    keyword_name=instance.keywordName,
                    func=func,
                    json_params=instance.params,
                )
                # Build kwargs for function call - only include input parameters
                kwargs: Dict[str, Any] = {}
                input_params = []
                output_params = []

                for param in instance.params:
                    # Handle case-insensitive direction
                    param_direction = getattr(param, "direction", "input")
                    param_direction = (
                        param_direction.lower() if param_direction else "input"
                    )

                    if param_direction == "input":
                        input_params.append(param)
                        # Check if this input has a connection from a previous step
                        param_value = self._get_connected_value(
                            flow.connections, step.id, param.id, step_outputs
                        )

                        # Use connected value if available, otherwise use default
                        if param_value is None:
                            param_value = param.value
                        else:
                            logger.info(
                                f"Step {instance.keywordName}: Using connected value "
                                f"for param '{param.name}': {param_value}"
                            )

                        # Validate mandatory parameters
                        if param.isMandatory and param_value is None:
                            raise ValueError(
                                f"Mandatory parameter '{param.name}' has no value"
                            )

                        kwargs[param.name] = param_value
                    else:
                        output_params.append(param)

                # Validate function signature before execution
                sig = inspect.signature(func)
                func_params = list(sig.parameters.keys())

                logger.info(
                    f"Executing step {instance.keywordName} with parameters: "
                    f"{kwargs}, expected: {func_params}"
                )

                # Check if all required function parameters are provided
                for func_param in func_params:
                    param_obj = sig.parameters[func_param]
                    if param_obj.kind in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    ):
                        continue
                    if (
                        param_obj.default == inspect.Parameter.empty
                        and func_param not in kwargs
                    ):
                        logger.warning(
                            f"Function '{instance.keywordName}' expects parameter "
                            f"'{func_param}' but it was not provided"
                        )

                # Check for unexpected parameters
                unexpected_params = set(kwargs.keys()) - set(func_params)
                has_var_kwargs = any(
                    p.kind == inspect.Parameter.VAR_KEYWORD
                    for p in sig.parameters.values()
                )
                if unexpected_params and not has_var_kwargs:
                    logger.warning(
                        f"Function '{instance.keywordName}' received unexpected "
                        f"parameters: {unexpected_params}"
                    )

                # Execute the keyword function
                logger.info(
                    f"Executing step {instance.keywordName} with kwargs: {kwargs}"
                )
                result = func(**kwargs)

                logger.debug(f"Output params: {output_params}")

                # Store and validate output parameters
                self._process_output_params(
                    step, instance, output_params, result, step_outputs
                )

            except ParameterValidationError as e:
                # Strict validation failure - parameter mismatch
                logger.error(f"Parameter validation failed: {e.detailed_message}")
                flow_result.set_failed_on_step_id(step.sequenceOrder)
                flow_result.set_message(e.detailed_message)
                flow_result.set_status(StatusEnum.FAILED)
                flow_failed = True
                break

            except Exception as e:
                error_msg = self._enhance_error_message(str(e), func)
                flow_result.set_failed_on_step_id(step.sequenceOrder)
                flow_result.set_message(error_msg)
                flow_result.set_status(StatusEnum.FAILED)
                flow_failed = True
                break

        if not flow_failed:
            flow_result.set_status(StatusEnum.PASSED)

        flow_result.completed_execution()
        if self.mode == "websocket":
            progress_event(
                WebSocketEventType.AGENT_EXECUTION_PROGRESS_NOTIFY, run_id, flow_result
            )

        return flow_result

    def _process_output_params(
        self,
        step: Any,
        instance: KeywordInstance,
        output_params: List[Any],
        result: Any,
        step_outputs: StepOutputs,
    ) -> None:
        """Process and store output parameters from a step execution.

        Args:
            step: The executed step
            instance: Keyword instance
            output_params: List of output parameters
            result: Result from keyword execution
            step_outputs: Dictionary to store outputs
        """
        if not output_params:
            if result is not None:
                logger.debug(
                    f"Function '{instance.keywordName}' returned a value "
                    "but has no output parameters defined"
                )
            return

        if result is None:
            mandatory_outputs = [p for p in output_params if p.isMandatory]
            if mandatory_outputs:
                logger.warning(
                    f"Function '{instance.keywordName}' has mandatory output "
                    "parameters but returned None"
                )
            return

        # Initialize step outputs if needed
        if step.id not in step_outputs:
            step_outputs[step.id] = {}

        if isinstance(result, dict):
            # Handle dict return value
            for param in output_params:
                if param.name in result:
                    step_outputs[step.id][param.id] = result[param.name]
                    logger.info(
                        f"Step {step.id}: Stored output '{param.name}' "
                        f"(id={param.id}): {result[param.name]}"
                    )
                elif param.isMandatory:
                    logger.warning(
                        f"Mandatory output parameter '{param.name}' not found "
                        f"in returned dict from '{instance.keywordName}'"
                    )

            # Warn about unexpected outputs
            expected_output_names = {p.name for p in output_params}
            unexpected_outputs = set(result.keys()) - expected_output_names
            if unexpected_outputs:
                logger.warning(
                    f"Function '{instance.keywordName}' returned unexpected "
                    f"outputs: {unexpected_outputs}"
                )
        else:
            # Handle single value return
            if len(output_params) == 1:
                step_outputs[step.id][output_params[0].id] = result
                logger.info(
                    f"Step {step.id}: Stored output '{output_params[0].name}' "
                    f"(id={output_params[0].id}): {result}"
                )
            else:
                logger.warning(
                    f"Function '{instance.keywordName}' has {len(output_params)} "
                    "output parameters but returned a single value"
                )
                for param in output_params:
                    if param.isMandatory:
                        step_outputs[step.id][param.id] = result
                        logger.info(
                            f"Step {step.id}: Stored output '{param.name}' "
                            f"(id={param.id}): {result}"
                        )

    def _enhance_error_message(self, error_msg: str, func: Callable) -> str:
        """Enhance error messages with helpful suggestions.

        Args:
            error_msg: Original error message
            func: The function that raised the error

        Returns:
            Enhanced error message
        """
        if "got an unexpected keyword argument" in error_msg:
            match = re.search(r"got an unexpected keyword argument '(\w+)'", error_msg)
            if match:
                wrong_param = match.group(1)
                sig = inspect.signature(func)
                func_params = list(sig.parameters.keys())

                for correct_param in func_params:
                    if correct_param.lower() == wrong_param.lower():
                        return f"{error_msg}. Did you mean '{correct_param}'?"

        return error_msg

    def _create_skipped_flow_result(self, flow: Flow) -> FlowResult:
        """Create a FlowResult for a skipped flow.

        Args:
            flow: The flow that was skipped

        Returns:
            FlowResult with SKIPPED status
        """
        flow_result = FlowResult(flow.id, flow.name)
        flow_result.started_execution()
        flow_result.set_status(StatusEnum.SKIPPED)
        flow_result.set_message("Flow skipped due to Skip run mode")
        flow_result.completed_execution()
        return flow_result

    def _get_connected_value(
        self,
        connections: List[FlowConnection],
        to_step_id: int,
        to_param_id: int,
        step_outputs: StepOutputs,
    ) -> Optional[Any]:
        """Get the value for an input parameter from a connected output parameter.

        Args:
            connections: List of FlowConnection objects
            to_step_id: The step ID that needs the input value
            to_param_id: The parameter ID that needs the input value
            step_outputs: Dictionary of stored outputs {step_id: {param_id: value}}

        Returns:
            The connected value if found, None otherwise
        """
        if not connections:
            return None

        for connection in connections:
            if (
                connection.toStepId == to_step_id
                and connection.toParamId == to_param_id
            ):
                from_step_id = connection.fromStepId
                from_param_id = connection.fromParamId

                if (
                    from_step_id in step_outputs
                    and from_param_id in step_outputs[from_step_id]
                ):
                    value = step_outputs[from_step_id][from_param_id]
                    logger.debug(
                        f"Connection found: Step {from_step_id} param {from_param_id} "
                        f"-> Step {to_step_id} param {to_param_id}, value: {value}"
                    )
                    return value
                else:
                    logger.warning(
                        f"Connection exists but no output value found for "
                        f"Step {from_step_id} param {from_param_id}"
                    )

        return None

    def _record_flow_result(
        self, run_id: Union[int, str], flow_result: FlowResult
    ) -> None:
        """Record a flow result in the execution tracker.

        Args:
            run_id: Run identifier
            flow_result: The flow result to record
        """
        with self.execution_tracker_lock:
            self.execution_tracker[str(run_id)]["flowResults"].append(
                {
                    "id": flow_result.id,
                    "name": flow_result.name,
                    "status": (
                        flow_result.status.value if flow_result.status else None
                    ),
                    "runAt": (
                        flow_result.runAt.isoformat() if flow_result.runAt else None
                    ),
                    "completedAt": (
                        flow_result.completedAt.isoformat()
                        if flow_result.completedAt
                        else None
                    ),
                    "failedOnStepId": flow_result.failedOnStepId,
                    "message": flow_result.message,
                }
            )

    def _mark_aborted_steps(
        self,
        run_id: Union[int, str],
        flows: List[Flow],
        executed_steps: Set[Tuple[int, int]],
        result_data: ExecutionResultData,
    ) -> None:
        """Mark unexecuted steps as aborted.

        Args:
            run_id: Run identifier
            flows: List of flows
            executed_steps: Set of already executed steps
            result_data: Execution result data to update
        """
        for flow in flows:
            for step in flow.steps:
                if (flow.id, step.instanceId) not in executed_steps:
                    flow_result = FlowResult(flow.id, flow.name)
                    flow_result.set_status(StatusEnum.ABORTED)
                    flow_result.set_message("Execution aborted")
                    flow_result.started_execution()
                    flow_result.completed_execution()
                    result_data.add_flow_result(flow_result)
                    self._record_flow_result(run_id, flow_result)

    def _validate_parameters(
        self,
        keyword_name: str,
        func: Callable,
        json_params: List[Any],
    ) -> None:
        """Validate incoming JSON parameters against keyword definition.

        Performs strict validation to ensure:
        1. All required @input_param parameters are present in JSON
        2. No unknown parameters are sent in JSON
        3. Parameter names match exactly

        Args:
            keyword_name: Name of the keyword being validated
            func: The keyword function with parameter metadata
            json_params: Parameters from the execution plan JSON

        Raises:
            ParameterValidationError: If validation fails
        """
        # Get keyword param definitions from decorator metadata
        keyword_params = getattr(func, "keyword_params", [])

        # Separate input and output params from keyword definition
        defined_input_params = {
            p.name: p for p in keyword_params if p.direction == ParamDirection.INPUT
        }

        # Separate input and output params from JSON
        json_input_params = {}
        json_output_params = set()

        for param in json_params:
            param_direction = getattr(param, "direction", "input")
            param_direction = param_direction.lower() if param_direction else "input"
            param_name = param.name

            if param_direction == "input":
                json_input_params[param_name] = param
            else:
                json_output_params.add(param_name)

        # Get sets for comparison
        defined_input_names = set(defined_input_params.keys())
        json_input_names = set(json_input_params.keys())

        # Check for unknown parameters (in JSON but not in definition)
        unknown_params = json_input_names - defined_input_names

        # Check for missing required parameters
        missing_required = set()
        for param_name, param_def in defined_input_params.items():
            if param_def.required and param_name not in json_input_names:
                # Check if parameter has a value in JSON (even if not in defined names)
                json_param = json_input_params.get(param_name)
                if json_param is None or getattr(json_param, "value", None) is None:
                    missing_required.add(param_name)

        # Build validation errors
        errors = []

        if unknown_params:
            errors.append(
                f"Unknown input parameters: {sorted(unknown_params)}. "
                f"Defined: {sorted(defined_input_names)}"
            )

        if missing_required:
            errors.append(f"Missing required parameters: {sorted(missing_required)}")

        # Raise error if any validation failed
        if errors:
            raise ParameterValidationError(
                keyword_name=keyword_name,
                message="Parameter validation failed. " + " | ".join(errors),
                missing_params=missing_required,
                unknown_params=unknown_params,
                expected_params=defined_input_names,
                received_params=json_input_names,
            )
