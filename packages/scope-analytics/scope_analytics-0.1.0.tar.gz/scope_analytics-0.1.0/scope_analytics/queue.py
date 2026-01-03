"""
Event queue with batch flushing for Scope Analytics
Manages in-memory event storage and batch processing
"""

import threading
import time
from collections import deque
from typing import Dict, Any, Callable, Optional


class EventQueue:
    """
    Thread-safe event queue with automatic batch flushing

    Features:
    - Batches events by size (batch_size)
    - Flushes automatically after timeout (batch_timeout_seconds)
    - Drops oldest events if max_queue_size exceeded
    - Thread-safe for concurrent access
    """

    def __init__(
        self,
        batch_size: int,
        batch_timeout_seconds: int,
        max_queue_size: int,
        flush_callback: Callable[[list], None],
        config,
    ):
        """
        Initialize event queue

        Args:
            batch_size: Number of events to batch before flushing
            batch_timeout_seconds: Max seconds to wait before flushing partial batch
            max_queue_size: Maximum events to queue (oldest dropped if exceeded)
            flush_callback: Function to call when flushing batch
            config: SDK configuration for logging
        """
        self.batch_size = batch_size
        self.batch_timeout_seconds = batch_timeout_seconds
        self.max_queue_size = max_queue_size
        self.flush_callback = flush_callback
        self.config = config

        self.queue = deque(maxlen=max_queue_size)
        self.lock = threading.Lock()
        self.last_flush_time = time.time()

        # Background thread for periodic flushing
        self.running = False
        self.flush_thread: Optional[threading.Thread] = None

    def start(self):
        """Start background flush thread"""
        if self.running:
            return

        self.running = True
        self.flush_thread = threading.Thread(
            target=self._flush_loop,
            daemon=True,
            name="ScopeAnalytics-FlushThread"
        )
        self.flush_thread.start()
        self.config.log("Event queue started")

    def stop(self):
        """Stop background thread and flush remaining events"""
        self.config.log("Stopping event queue...")
        self.running = False

        if self.flush_thread:
            self.flush_thread.join(timeout=5)

        # Flush any remaining events
        self.flush()
        self.config.log("Event queue stopped")

    def enqueue(self, event: Dict[str, Any]):
        """
        Add event to queue

        Args:
            event: Event dictionary to queue
        """
        with self.lock:
            # Check if queue is full
            if len(self.queue) >= self.max_queue_size:
                self.config.log(
                    f"Queue full ({self.max_queue_size}), dropping oldest event"
                )

            self.queue.append(event)

            # Check if we should flush due to batch size
            if len(self.queue) >= self.batch_size:
                self.config.log(
                    f"Batch size ({self.batch_size}) reached, flushing..."
                )
                self._flush_batch()

    def flush(self):
        """Manually flush all queued events"""
        with self.lock:
            if len(self.queue) > 0:
                self.config.log(f"Manual flush: {len(self.queue)} events")
                self._flush_batch()

    def _flush_loop(self):
        """Background thread that periodically flushes events"""
        while self.running:
            time.sleep(1)  # Check every second

            with self.lock:
                time_since_flush = time.time() - self.last_flush_time

                # Flush if timeout reached and we have events
                if time_since_flush >= self.batch_timeout_seconds and len(self.queue) > 0:
                    self.config.log(
                        f"Timeout ({self.batch_timeout_seconds}s) reached, flushing {len(self.queue)} events"
                    )
                    self._flush_batch()

    def _flush_batch(self):
        """
        Flush current batch of events
        NOTE: Must be called with lock held
        """
        if len(self.queue) == 0:
            return

        # Copy batch and clear queue while holding lock
        batch = list(self.queue)
        self.queue.clear()
        self.last_flush_time = time.time()

        # We'll flush outside the lock in a separate thread
        # This prevents blocking the queue during I/O
        import threading
        def flush_in_background():
            try:
                self.flush_callback(batch)
            except Exception as e:
                self.config.log(f"Error flushing batch: {e}")
                # Re-queue events on failure
                with self.lock:
                    self.queue.extendleft(reversed(batch))

        # Start flush in background
        thread = threading.Thread(target=flush_in_background, daemon=True)
        thread.start()

    def size(self) -> int:
        """Get current queue size"""
        with self.lock:
            return len(self.queue)
