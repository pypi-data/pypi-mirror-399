import logging
import threading

logger = logging.getLogger(__name__)


class AgentStateTracker:
    def __init__(self):
        self._is_busy = False
        self._lock = threading.Lock()
        self._shutdown_event = threading.Event()

    def set_busy(self, busy: bool):
        with self._lock:
            self._is_busy = busy
        status = "BUSY" if busy else "AVAILABLE"
        logger.info(f"Agent status set to: {status}")
        return status

    def is_busy(self) -> bool:
        with self._lock:
            return self._is_busy

    def try_set_busy(self) -> bool:
        """Atomically check if available and set busy if so.

        Returns:
            True if successfully set to busy, False if already busy
        """
        with self._lock:
            if self._is_busy:
                return False
            self._is_busy = True
            return True

    def shutdown_requested(self) -> bool:
        return self._shutdown_event.is_set()

    def request_shutdown(self):
        logger.info("Shutdown requested for agent")
        self._shutdown_event.set()

    def clear_shutdown(self):
        self._shutdown_event.clear()

    def wait_for_shutdown(self, timeout=None):
        return self._shutdown_event.wait(timeout=timeout)
