"""Execution plan models for parsing and representing workflow structures."""

import json
from typing import Any, Dict, List, Optional, Tuple


class Param:
    """Keyword parameter definition."""

    def __init__(
        self,
        id: int,
        name: str,
        direction: str,
        type: str,
        is_mandatory: bool,
        value: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.direction = direction
        self.type = type
        self.is_mandatory = is_mandatory
        self.value = value

    # Legacy property alias for backward compatibility
    @property
    def isMandatory(self) -> bool:
        return self.is_mandatory


class KeywordInstance:
    """Instance of a keyword with its parameters."""

    def __init__(
        self,
        id: int,
        keyword_name: str,
        keyword_id: int,
        name: str,
        params: List[Param],
    ) -> None:
        self.id = id
        self.keyword_name = keyword_name
        self.keyword_id = keyword_id
        self.name = name
        self.params = params

    # Legacy property alias for backward compatibility
    @property
    def keywordName(self) -> str:
        return self.keyword_name

    @property
    def keywordId(self) -> int:
        return self.keyword_id


class FlowConnection:
    """Connection between flow steps for parameter passing."""

    def __init__(
        self,
        id: int,
        from_step_id: int,
        to_step_id: int,
        from_param_id: int,
        to_param_id: int,
    ) -> None:
        self.id = id
        self.from_step_id = from_step_id
        self.to_step_id = to_step_id
        self.from_param_id = from_param_id
        self.to_param_id = to_param_id

    # Legacy property aliases for backward compatibility
    @property
    def fromStepId(self) -> int:
        return self.from_step_id

    @property
    def toStepId(self) -> int:
        return self.to_step_id

    @property
    def fromParamId(self) -> int:
        return self.from_param_id

    @property
    def toParamId(self) -> int:
        return self.to_param_id


class FlowStep:
    """Single step within a flow."""

    def __init__(self, id: int, instance_id: int, sequence_order: int) -> None:
        self.id = id
        self.instance_id = instance_id
        self.sequence_order = sequence_order

    # Legacy property aliases for backward compatibility
    @property
    def instanceId(self) -> int:
        return self.instance_id

    @property
    def sequenceOrder(self) -> int:
        return self.sequence_order


class Flow:
    """Workflow containing steps and connections."""

    def __init__(
        self,
        id: int,
        flow_id: int,
        run_mode: str,
        name: str,
        steps: List[FlowStep],
        connections: Optional[List[FlowConnection]] = None,
    ) -> None:
        self.id = id
        self.flow_id = flow_id
        self.run_mode = run_mode
        self.name = name
        self.steps = steps
        self.connections = connections if connections is not None else []

    # Legacy property aliases for backward compatibility
    @property
    def flowId(self) -> int:
        return self.flow_id

    @property
    def runMode(self) -> str:
        return self.run_mode


def parse_param(param_data: Dict[str, Any]) -> Param:
    """Parse parameter data from JSON."""
    return Param(
        id=param_data["id"],
        name=param_data["name"],
        direction=param_data["direction"],
        type=param_data["type"],
        is_mandatory=param_data["isMandatory"],
        value=param_data["value"],
    )


def parse_keyword_instance(instance_data: Dict[str, Any]) -> KeywordInstance:
    """Parse keyword instance data from JSON."""
    params = [parse_param(param) for param in instance_data["params"]]
    return KeywordInstance(
        id=instance_data["id"],
        keyword_name=instance_data["keywordName"],
        keyword_id=instance_data["keywordId"],
        name=instance_data["name"],
        params=params,
    )


def parse_step(step_data: Dict[str, Any]) -> FlowStep:
    """Parse flow step data from JSON."""
    return FlowStep(
        id=step_data["id"],
        instance_id=step_data["instanceId"],
        sequence_order=step_data["sequenceOrder"],
    )


def parse_connection(connection_data: Dict[str, Any]) -> FlowConnection:
    """Parse flow connection data from JSON."""
    return FlowConnection(
        id=connection_data["id"],
        from_step_id=connection_data["fromStepId"],
        to_step_id=connection_data["toStepId"],
        from_param_id=connection_data["fromParamId"],
        to_param_id=connection_data["toParamId"],
    )


def parse_flow(flow_data: Dict[str, Any]) -> Flow:
    """Parse flow data from JSON."""
    if "id" not in flow_data or "name" not in flow_data:
        raise ValueError("Flow data must contain 'id' and 'name'")

    flow_id = flow_data["id"]
    run_mode = flow_data.get("runMode", "default")
    flow_id_value = flow_data.get("flowId", flow_id)
    name = flow_data["name"]

    steps = (
        [parse_step(step) for step in flow_data["steps"]]
        if "steps" in flow_data
        else []
    )
    connections = (
        [parse_connection(conn) for conn in flow_data["connections"]]
        if "connections" in flow_data
        else []
    )

    return Flow(
        id=flow_id,
        flow_id=flow_id_value,
        run_mode=run_mode,
        name=name,
        steps=steps,
        connections=connections,
    )


def parse_execution_plan(
    json_data: Dict[str, Any],
) -> Tuple[List[KeywordInstance], List[Flow]]:
    """Parse complete execution plan from JSON data."""
    keyword_instances = [
        parse_keyword_instance(instance) for instance in json_data["keywordInstances"]
    ]
    flows = [parse_flow(flow) for flow in json_data["flows"]]
    return keyword_instances, flows


def execute_plan_from_json(
    json_str: str,
) -> Tuple[List[KeywordInstance], List[Flow]]:
    """Parse execution plan from JSON string."""
    json_data = json.loads(json_str)
    return parse_execution_plan(json_data)
