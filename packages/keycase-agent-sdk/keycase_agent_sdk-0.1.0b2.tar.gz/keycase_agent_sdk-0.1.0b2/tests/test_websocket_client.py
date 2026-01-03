"""Tests for robust WebSocket client."""

import pytest
import time
import json
import queue
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from keycase_agent.websocket_client import WebSocketClient, ConnectionState


class TestWebSocketClient:
    """Test suite for WebSocket client."""

    def setup_method(self):
        """Set up test fixtures."""
        self.on_open = Mock()
        self.on_message = Mock()
        self.on_error = Mock()
        self.on_close = Mock()
        
        self.client = WebSocketClient(
            url="ws://test.example.com/ws",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            max_reconnect_attempts=3,
            initial_retry_delay=0.1,
            max_retry_delay=1.0,
            heartbeat_interval=1.0,
            heartbeat_timeout=0.5
        )

    def test_init(self):
        """Test WebSocket client initialization."""
        assert self.client.url == "ws://test.example.com/ws"
        assert self.client.state == ConnectionState.DISCONNECTED
        assert self.client.max_reconnect_attempts == 3
        assert self.client.reconnect_attempts == 0
        assert self.client.consecutive_failures == 0
        assert not self.client.is_connected()

    def test_calculate_retry_delay(self):
        """Test exponential backoff calculation."""
        # Test exponential backoff
        self.client.reconnect_attempts = 0
        delay = self.client._calculate_retry_delay()
        assert 0.1 <= delay <= 0.11  # 0.1 + 10% jitter
        
        self.client.reconnect_attempts = 2
        delay = self.client._calculate_retry_delay()
        assert 0.4 <= delay <= 0.44  # 0.4 + 10% jitter
        
        # Test max delay
        self.client.reconnect_attempts = 10
        delay = self.client._calculate_retry_delay()
        assert delay <= 1.1  # Max delay + jitter

    def test_should_reconnect_shutdown(self):
        """Test should_reconnect returns False when shutdown."""
        self.client._shutdown_event.set()
        assert not self.client._should_reconnect()

    def test_should_reconnect_max_attempts(self):
        """Test should_reconnect returns False after max attempts."""
        self.client.reconnect_attempts = 3
        assert not self.client._should_reconnect()

    def test_should_reconnect_circuit_breaker(self):
        """Test should_reconnect returns False for circuit breaker."""
        self.client.consecutive_failures = 6
        assert not self.client._should_reconnect()

    def test_should_reconnect_normal(self):
        """Test should_reconnect returns True in normal conditions."""
        assert self.client._should_reconnect()

    def test_set_state_thread_safe(self):
        """Test state setting is thread-safe."""
        self.client._set_state(ConnectionState.CONNECTING)
        assert self.client.state == ConnectionState.CONNECTING
        
        self.client._set_state(ConnectionState.CONNECTED)
        assert self.client.state == ConnectionState.CONNECTED

    def test_on_open_wrapper(self):
        """Test on_open wrapper functionality."""
        mock_ws = Mock()

        with patch.object(self.client, '_process_queued_messages') as mock_queue:
            self.client._on_open_wrapper(mock_ws)

        # Verify state changes
        assert self.client.state == ConnectionState.CONNECTED
        assert self.client.total_connections == 1
        assert self.client.reconnect_attempts == 0
        assert self.client.consecutive_failures == 0

        # Verify methods called
        # Note: _start_heartbeat is no longer called here - heartbeat is handled
        # by websocket-client's ping_interval parameter in run_forever()
        mock_queue.assert_called_once()
        self.on_open.assert_called_once_with(mock_ws)

    def test_on_message_wrapper_pong(self):
        """Test on_message wrapper handles pong messages."""
        mock_ws = Mock()
        
        self.client._on_message_wrapper(mock_ws, "pong")
        
        # Should not call original callback for pong
        self.on_message.assert_not_called()
        
        # Should update last_pong_time
        assert isinstance(self.client.last_pong_time, datetime)

    def test_on_message_wrapper_normal(self):
        """Test on_message wrapper handles normal messages."""
        mock_ws = Mock()
        
        self.client._on_message_wrapper(mock_ws, "test message")
        
        # Should call original callback
        self.on_message.assert_called_once_with(mock_ws, "test message")

    def test_on_error_wrapper(self):
        """Test on_error wrapper functionality."""
        mock_ws = Mock()
        error = Exception("Test error")
        
        self.client._on_error_wrapper(mock_ws, error)
        
        # Verify error tracking
        assert self.client.last_error == "Test error"
        assert self.client.consecutive_failures == 1
        
        # Verify callback called
        self.on_error.assert_called_once_with(mock_ws, error)

    def test_on_close_wrapper(self):
        """Test on_close wrapper functionality."""
        mock_ws = Mock()
        
        with patch.object(self.client, '_stop_heartbeat') as mock_stop:
            self.client._on_close_wrapper(mock_ws, 1000, "Normal close")
        
        # Verify state changes
        assert self.client.state == ConnectionState.DISCONNECTED
        assert self.client.total_disconnections == 1
        
        # Verify methods called
        mock_stop.assert_called_once()
        self.on_close.assert_called_once_with(mock_ws, 1000, "Normal close")

    def test_send_connected(self):
        """Test send when connected."""
        mock_ws = Mock()
        mock_ws.sock.connected = True
        self.client.ws = mock_ws
        self.client.state = ConnectionState.CONNECTED
        
        result = self.client.send("test message")
        
        assert result is True
        mock_ws.send.assert_called_once_with("test message")

    def test_send_disconnected_queued(self):
        """Test send when disconnected queues message."""
        self.client.state = ConnectionState.DISCONNECTED
        
        result = self.client.send("test message")
        
        assert result is False
        assert self.client.pending_messages.qsize() == 1
        assert self.client.pending_messages.get() == "test message"

    def test_send_priority_message(self):
        """Test send with priority queuing."""
        self.client.state = ConnectionState.DISCONNECTED
        
        # Send normal message first
        self.client.send("normal message")
        # Send priority message
        self.client.send("priority message", priority=True)
        
        # Priority message should be first
        assert self.client.pending_messages.get() == "priority message"
        assert self.client.pending_messages.get() == "normal message"

    def test_send_json(self):
        """Test send_json method."""
        mock_ws = Mock()
        mock_ws.sock.connected = True
        self.client.ws = mock_ws
        self.client.state = ConnectionState.CONNECTED
        
        data = {"type": "test", "data": "value"}
        result = self.client.send_json(data)
        
        assert result is True
        mock_ws.send.assert_called_once_with(json.dumps(data))

    def test_is_connected_true(self):
        """Test is_connected returns True when connected."""
        mock_ws = Mock()
        mock_ws.sock.connected = True
        self.client.ws = mock_ws
        self.client.state = ConnectionState.CONNECTED
        
        assert self.client.is_connected() is True

    def test_is_connected_false(self):
        """Test is_connected returns False when disconnected."""
        assert self.client.is_connected() is False

    def test_get_connection_stats(self):
        """Test get_connection_stats method."""
        self.client.total_connections = 5
        self.client.total_disconnections = 3
        self.client.reconnect_attempts = 2
        self.client.consecutive_failures = 1
        self.client.last_error = "Test error"
        
        stats = self.client.get_connection_stats()
        
        assert stats["state"] == "disconnected"
        assert stats["total_connections"] == 5
        assert stats["total_disconnections"] == 3
        assert stats["reconnect_attempts"] == 2
        assert stats["consecutive_failures"] == 1
        assert stats["last_error"] == "Test error"
        assert stats["queued_messages"] == 0

    def test_get_connection_stats_with_uptime(self):
        """Test get_connection_stats with uptime calculation."""
        mock_ws = Mock()
        mock_ws.sock.connected = True
        self.client.ws = mock_ws
        self.client.state = ConnectionState.CONNECTED
        self.client.connection_start_time = datetime.now() - timedelta(seconds=10)
        
        stats = self.client.get_connection_stats()
        
        assert stats["uptime_seconds"] is not None
        assert stats["uptime_seconds"] >= 10

    def test_reset_connection(self):
        """Test reset_connection method."""
        self.client.reconnect_attempts = 5
        self.client.consecutive_failures = 3
        self.client.last_error = "Test error"
        self.client.state = ConnectionState.FAILED
        
        self.client.reset_connection()
        
        assert self.client.reconnect_attempts == 0
        assert self.client.consecutive_failures == 0
        assert self.client.last_error is None
        assert self.client.state == ConnectionState.DISCONNECTED

    def test_process_queued_messages(self):
        """Test processing of queued messages."""
        # Setup connected state
        mock_ws = Mock()
        mock_ws.sock.connected = True
        self.client.ws = mock_ws
        self.client.state = ConnectionState.CONNECTED
        
        # Add messages to queue
        self.client.pending_messages.put("message1")
        self.client.pending_messages.put("message2")
        
        self.client._process_queued_messages()
        
        # Verify messages were sent
        assert mock_ws.send.call_count == 2
        mock_ws.send.assert_any_call("message1")
        mock_ws.send.assert_any_call("message2")
        
        # Verify queue is empty
        assert self.client.pending_messages.empty()

    def test_stop_graceful_shutdown(self):
        """Test graceful stop functionality."""
        # Setup heartbeat thread
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        self.client._heartbeat_thread = mock_thread
        
        # Setup WebSocket
        mock_ws = Mock()
        self.client.ws = mock_ws
        
        self.client.stop()
        
        # Verify shutdown event is set
        assert self.client._shutdown_event.is_set()
        
        # Verify WebSocket is closed
        mock_ws.close.assert_called_once()
        
        # Verify thread join is called
        mock_thread.join.assert_called_once_with(timeout=5)
        
        # Verify final state
        assert self.client.state == ConnectionState.DISCONNECTED

    @patch('keycase_agent.websocket_client.websocket.WebSocketApp')
    def test_run_forever_success(self, mock_websocket_app):
        """Test successful run_forever execution."""
        mock_ws = Mock()
        mock_websocket_app.return_value = mock_ws

        # Make run_forever return after one iteration and set shutdown
        def side_effect(**kwargs):
            self.client._shutdown_event.set()

        mock_ws.run_forever.side_effect = side_effect

        self.client.run_forever()

        # Verify WebSocket was created and started
        mock_websocket_app.assert_called_once()
        mock_ws.run_forever.assert_called_once()
        # Verify run_forever was called with ping parameters
        call_kwargs = mock_ws.run_forever.call_args[1]
        assert 'ping_interval' in call_kwargs
        assert 'ping_timeout' in call_kwargs
        assert call_kwargs['reconnect'] is False

    @patch('keycase_agent.websocket_client.websocket.WebSocketApp')
    @patch('keycase_agent.websocket_client.time.sleep')
    def test_run_forever_with_retry(self, mock_sleep, mock_websocket_app):
        """Test run_forever with retry logic."""
        mock_ws = Mock()
        mock_websocket_app.return_value = mock_ws

        call_count = 0

        def side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Connection failed")
            else:
                self.client._shutdown_event.set()

        mock_ws.run_forever.side_effect = side_effect

        self.client.run_forever()

        # Verify retry occurred
        assert mock_websocket_app.call_count == 2
        assert mock_ws.run_forever.call_count == 2
        mock_sleep.assert_called_once()

    def test_heartbeat_worker_timeout(self):
        """Test heartbeat worker timeout detection."""
        # Setup connected state
        mock_ws = Mock()
        mock_ws.sock.connected = True
        self.client.ws = mock_ws
        self.client.state = ConnectionState.CONNECTED
        
        # Set old pong time to trigger timeout
        self.client.last_pong_time = datetime.now() - timedelta(seconds=10)
        
        # Start heartbeat worker in thread
        heartbeat_thread = threading.Thread(target=self.client._heartbeat_worker)
        heartbeat_thread.start()
        
        # Wait for heartbeat timeout
        time.sleep(0.6)  # Slightly longer than heartbeat_timeout
        
        # Stop the worker
        self.client._shutdown_event.set()
        heartbeat_thread.join(timeout=2)
        
        # Verify WebSocket was closed due to timeout
        mock_ws.close.assert_called_once()

    def test_queue_overflow_handling(self):
        """Test handling of queue overflow."""
        # Fill the queue to capacity
        small_client = WebSocketClient(
            url="ws://test.example.com/ws",
            on_open=Mock(),
            on_message=Mock(),
            on_error=Mock(),
            on_close=Mock(),
            max_queue_size=2
        )
        
        # Fill queue to capacity
        assert small_client.send("msg1") is False  # Queued
        assert small_client.send("msg2") is False  # Queued
        assert small_client.send("msg3") is False  # Should be dropped
        
        # Verify only 2 messages are queued
        assert small_client.pending_messages.qsize() == 2