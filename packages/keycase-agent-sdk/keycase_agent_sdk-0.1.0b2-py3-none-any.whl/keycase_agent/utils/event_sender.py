# event_sender.py
# utils/event_sender.py
import json
import logging
import threading
import time

logger = logging.getLogger(__name__)

# Internal queue and control variables
event_queue = []
queue_lock = threading.Lock()
_ws = None
_flush_interval = 10.0
_flushing = False


def configure_batching(ws, flush_interval: float = 10.0):
    """
    Initialize batching with a WebSocket connection and interval in seconds.
    Must be called once (e.g. in KeycaseAgent.on_open).
    """
    global _ws, _flush_interval, _flushing
    _ws = ws
    _flush_interval = flush_interval
    if not _flushing:
        _flushing = True
        thread = threading.Thread(target=_flush_loop, name="EventBatcher", daemon=True)
        thread.start()
        logger.info(f"Event batching started with interval={_flush_interval}s")


def _flush_loop():
    while _flushing:
        time.sleep(_flush_interval)
        flush_events()


def flush_events():
    """
    Flush queued events as a batch. Sends {"events": [ ... ]} over the websocket.
    """
    global event_queue  # noqa: F824
    with queue_lock:
        if not event_queue:
            return
        batch = list(event_queue)
        event_queue.clear()
    try:
        if _ws is None:
            logger.warning("WebSocket not configured, skipping batch send")
            return
        packet = {"events": batch}
        logger.info(f"Flushing {len(batch)} events as a batch as {packet}")
        _ws.send(json.dumps(packet))
    except Exception as e:
        logger.error(f"Error sending batch: {e}")


def send_event(event_type, payload, immediate: bool = False):
    """
    Queue an event for batching, or send immediately if requested.
    Requires that configure_batching(ws, interval) has been called first.

    :param event_type: enum or raw event string
    :param payload: dict
    :param immediate: bool, if True send directly without batching
    """
    raw = event_type.value if hasattr(event_type, "value") else event_type
    packet = {"event": raw, "payload": payload}
    if immediate:
        if _ws is None:
            logger.warning("WebSocket not configured, skipping immediate send")
            return
        logger.info(f"Immediate send: {packet}")
        _ws.send(json.dumps(packet))
    else:
        with queue_lock:
            event_queue.append(packet)


def accepted_execution(event_type, run_id):
    send_event(event_type, {"runId": run_id}, immediate=True)


def completed_execution(event_type, run_id, tracker):
    send_event(event_type, {"runId": run_id})
    tracker.pop(run_id, None)


def progress_event(event_type, run_id, flow_result):
    payload = {
        "runId": run_id,
        "id": flow_result.id,
        "name": flow_result.name,
        "status": flow_result.status.value if flow_result.status else None,
        "runAt": flow_result.runAt.isoformat() if flow_result.runAt else None,
        "failedOnStepId": flow_result.failedOnStepId,
        "completedAt": (
            flow_result.completedAt.isoformat() if flow_result.completedAt else None
        ),
        "message": flow_result.message,
    }
    send_event(event_type, payload)


def status_update(event_type, status):
    send_event(event_type, {"status": status})


def busy_message(event_type, run_id, reason="Agent is currently busy"):
    send_event(event_type, {"runId": run_id, "reason": reason})


def auth_request(event_type, payload):
    """
    Send an authentication request event.
    """
    send_event(event_type, payload)
