import json
import logging
import queue
import random
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional

import websocket

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection state enumeration."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


class WebSocketClient:
    """Robust WebSocket client with reconnection, heartbeat, and message queuing."""

    def __init__(
        self,
        url: str,
        on_open: Callable,
        on_message: Callable,
        on_error: Callable,
        on_close: Callable,
        max_reconnect_attempts: int = 10,
        initial_retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
        heartbeat_interval: float = 30.0,
        heartbeat_timeout: float = 10.0,
        connection_timeout: float = 10.0,
        max_queue_size: int = 1000,
    ):
        """Initialize robust WebSocket client.

        Args:
            url: WebSocket URL
            on_open: Callback for connection open
            on_message: Callback for incoming messages
            on_error: Callback for errors
            on_close: Callback for connection close
            max_reconnect_attempts: Maximum reconnection attempts
            initial_retry_delay: Initial retry delay in seconds
            max_retry_delay: Maximum retry delay in seconds
            heartbeat_interval: Heartbeat ping interval in seconds
            heartbeat_timeout: Heartbeat response timeout in seconds
            connection_timeout: Connection timeout in seconds
            max_queue_size: Maximum message queue size
        """
        self.url = url
        self.on_open = on_open
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close

        # Connection settings
        self.max_reconnect_attempts = max_reconnect_attempts
        self.initial_retry_delay = initial_retry_delay
        self.max_retry_delay = max_retry_delay
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.connection_timeout = connection_timeout

        # State management
        self.ws: Optional[websocket.WebSocketApp] = None
        self.state = ConnectionState.DISCONNECTED
        self.reconnect_attempts = 0
        self.consecutive_failures = 0
        self.last_pong_time = datetime.now()

        # Threading
        self._shutdown_event = threading.Event()
        self._state_lock = threading.Lock()
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._connection_thread: Optional[threading.Thread] = None

        # Message queuing
        self.message_queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self.pending_messages: queue.Queue = queue.Queue(maxsize=max_queue_size)

        # Connection metrics
        self.connection_start_time: Optional[datetime] = None
        self.total_connections = 0
        self.total_disconnections = 0
        self.last_error: Optional[str] = None

        logger.info(f"WebSocket client initialized for {url}")

    def _set_state(self, new_state: ConnectionState) -> None:
        """Thread-safe state setter."""
        with self._state_lock:
            if self.state != new_state:
                logger.debug(f"State change: {self.state.value} -> {new_state.value}")
                self.state = new_state

    def _calculate_retry_delay(self) -> float:
        """Calculate exponential backoff delay with jitter."""
        base_delay = min(
            self.max_retry_delay,
            self.initial_retry_delay * (2**self.reconnect_attempts),
        )
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, 0.1 * base_delay)
        return base_delay + jitter

    def _should_reconnect(self) -> bool:
        """Check if should attempt reconnection."""
        if self._shutdown_event.is_set():
            return False

        if (
            self.max_reconnect_attempts > 0
            and self.reconnect_attempts >= self.max_reconnect_attempts
        ):
            logger.error(
                f"Max reconnect attempts ({self.max_reconnect_attempts}) reached"
            )
            return False

        # Circuit breaker: if too many consecutive failures, wait longer
        if self.consecutive_failures > 5:
            logger.warning(
                f"Circuit breaker: {self.consecutive_failures} consecutive failures"
            )
            return False

        return True

    def _on_open_wrapper(self, ws) -> None:
        """Wrapper for on_open callback with connection setup."""
        logger.info("WebSocket connection opened")
        self._set_state(ConnectionState.CONNECTED)
        self.connection_start_time = datetime.now()
        self.total_connections += 1
        self.reconnect_attempts = 0
        self.consecutive_failures = 0
        self.last_pong_time = datetime.now()

        # Note: Heartbeat is handled by websocket-client's ping_interval parameter
        # in run_forever(). Custom heartbeat can be enabled after authentication
        # by calling _start_heartbeat() from the on_open callback if needed.

        # Process queued messages
        self._process_queued_messages()

        # Call original callback
        try:
            self.on_open(ws)
        except Exception as e:
            logger.error(f"Error in on_open callback: {e}")

    def _on_message_wrapper(self, ws, message: str) -> None:
        """Wrapper for on_message callback with heartbeat handling."""
        try:
            # Handle pong responses
            if message == "pong":
                self.last_pong_time = datetime.now()
                logger.debug("Received pong response")
                return

            # Call original callback
            self.on_message(ws, message)
        except Exception as e:
            logger.error(f"Error in on_message callback: {e}")

    def _on_error_wrapper(self, ws, error) -> None:
        """Wrapper for on_error callback with error tracking."""
        self.last_error = str(error)
        self.consecutive_failures += 1
        logger.error(f"WebSocket error: {error}")

        # Call original callback
        try:
            self.on_error(ws, error)
        except Exception as e:
            logger.error(f"Error in on_error callback: {e}")

    def _on_close_wrapper(self, ws, code: Optional[int], msg: Optional[str]) -> None:
        """Wrapper for on_close callback with cleanup."""
        logger.info(f"WebSocket closed with code={code}, msg={msg}")
        self._set_state(ConnectionState.DISCONNECTED)
        self.total_disconnections += 1

        # Stop heartbeat
        self._stop_heartbeat()

        # Call original callback
        try:
            self.on_close(ws, code, msg)
        except Exception as e:
            logger.error(f"Error in on_close callback: {e}")

    def _start_heartbeat(self) -> None:
        """Start heartbeat monitoring thread."""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            return

        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_worker, name="WebSocket-Heartbeat", daemon=True
        )
        self._heartbeat_thread.start()

    def _stop_heartbeat(self) -> None:
        """Stop heartbeat monitoring thread."""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            # Thread will stop when connection state changes
            pass

    def _heartbeat_worker(self) -> None:
        """Heartbeat worker thread."""
        while (
            not self._shutdown_event.is_set()
            and self.state == ConnectionState.CONNECTED
        ):
            try:
                # Send ping
                if self.ws and self.ws.sock and self.ws.sock.connected:
                    self.ws.send("ping")
                    logger.debug("Sent heartbeat ping")

                # Wait for heartbeat interval
                time.sleep(self.heartbeat_interval)

                # Check if pong was received within timeout
                if datetime.now() - self.last_pong_time > timedelta(
                    seconds=self.heartbeat_timeout
                ):
                    logger.warning("Heartbeat timeout - connection may be stale")
                    if self.ws:
                        self.ws.close()
                    break

            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                break

    def _process_queued_messages(self) -> None:
        """Process messages queued during disconnection."""
        processed = 0
        while not self.pending_messages.empty() and self.is_connected():
            try:
                message = self.pending_messages.get_nowait()
                self._send_direct(message)
                processed += 1
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error processing queued message: {e}")

        if processed > 0:
            logger.info(f"Processed {processed} queued messages")

    def _send_direct(self, data: str) -> bool:
        """Send data directly without queuing."""
        if self.ws and self.ws.sock and self.ws.sock.connected:
            try:
                self.ws.send(data)
                logger.debug(f"Sent data: {data}")
                return True
            except Exception as e:
                logger.error(f"Failed to send data: {e}")
                return False
        return False

    def run_forever(self) -> None:
        """Run WebSocket client with robust reconnection."""
        logger.info(f"Starting WebSocket client for {self.url}")

        while not self._shutdown_event.is_set():
            if not self._should_reconnect():
                break

            try:
                self._set_state(ConnectionState.CONNECTING)
                logger.info(
                    f"Connecting to WebSocket at {self.url} "
                    f"(attempt {self.reconnect_attempts + 1})"
                )

                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_open=self._on_open_wrapper,
                    on_message=self._on_message_wrapper,
                    on_error=self._on_error_wrapper,
                    on_close=self._on_close_wrapper,
                )

                # Set socket options for better reliability
                self.ws.run_forever(
                    ping_interval=self.heartbeat_interval,
                    ping_timeout=self.heartbeat_timeout,
                    reconnect=False,  # We handle reconnection ourselves
                )

            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, stopping WebSocket client")
                self._shutdown_event.set()
                break
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                self.consecutive_failures += 1

            if not self._shutdown_event.is_set():
                self._set_state(ConnectionState.RECONNECTING)
                self.reconnect_attempts += 1

                if self._should_reconnect():
                    delay = self._calculate_retry_delay()
                    logger.info(
                        f"Reconnecting in {delay:.1f}s... "
                        f"(attempt {self.reconnect_attempts})"
                    )
                    time.sleep(delay)
                else:
                    self._set_state(ConnectionState.FAILED)
                    logger.error(
                        "Max reconnection attempts reached or circuit breaker triggered"
                    )
                    break

    def send(self, data: str, priority: bool = False) -> bool:
        """Send data with queuing support.

        Args:
            data: Data to send
            priority: If True, add to front of queue

        Returns:
            True if sent immediately, False if queued
        """
        if self.is_connected():
            return self._send_direct(data)
        else:
            # Queue message for later delivery
            try:
                if priority:
                    # Add to front of queue
                    temp_queue = queue.Queue()
                    temp_queue.put(data)
                    while not self.pending_messages.empty():
                        temp_queue.put(self.pending_messages.get_nowait())
                    self.pending_messages = temp_queue
                else:
                    self.pending_messages.put(data, block=False)

                logger.debug(f"Queued message for later delivery: {data}")
                return False
            except queue.Full:
                logger.warning("Message queue full, dropping message")
                return False

    def send_json(self, data: Dict[str, Any], priority: bool = False) -> bool:
        """Send JSON data."""
        return self.send(json.dumps(data), priority)

    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return bool(
            self.state == ConnectionState.CONNECTED
            and self.ws
            and self.ws.sock
            and self.ws.sock.connected
        )

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        uptime = None
        if self.connection_start_time and self.is_connected():
            uptime = (datetime.now() - self.connection_start_time).total_seconds()

        return {
            "state": self.state.value,
            "total_connections": self.total_connections,
            "total_disconnections": self.total_disconnections,
            "reconnect_attempts": self.reconnect_attempts,
            "consecutive_failures": self.consecutive_failures,
            "uptime_seconds": uptime,
            "queued_messages": self.pending_messages.qsize(),
            "last_error": self.last_error,
            "last_pong": (
                self.last_pong_time.isoformat() if self.last_pong_time else None
            ),
        }

    def reset_connection(self) -> None:
        """Reset connection state and retry counters."""
        logger.info("Resetting connection state")
        self.reconnect_attempts = 0
        self.consecutive_failures = 0
        self.last_error = None

        if self.state == ConnectionState.FAILED:
            self._set_state(ConnectionState.DISCONNECTED)

    def stop(self) -> None:
        """Gracefully stop WebSocket client."""
        logger.info("Stopping WebSocket client")
        self._shutdown_event.set()

        # Stop heartbeat
        self._stop_heartbeat()

        # Close WebSocket connection
        if self.ws:
            try:
                self.ws.keep_running = False
                self.ws.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {e}")

        # Wait for threads to finish
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=5)

        self._set_state(ConnectionState.DISCONNECTED)
        logger.info("WebSocket client stopped")
