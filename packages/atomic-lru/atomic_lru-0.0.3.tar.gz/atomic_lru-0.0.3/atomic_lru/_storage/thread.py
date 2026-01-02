import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property


@dataclass
class ExpirationThread:
    """A background thread for periodically cleaning expired cache entries.

    This class manages a daemon thread that periodically checks and removes expired
    items from the cache. It uses a round-robin approach, checking a limited number
    of items per iteration to avoid blocking the main thread for extended periods.

    The thread runs in a loop, checking items starting from a tracked index position.
    After each iteration, it waits for a specified delay before continuing. The
    thread can be gracefully stopped using the `stop()` method.

    Args:
        clean_callback: A callable that performs the actual expiration check and
            deletion. Should accept two optional integer arguments (start and stop
            indices) and return a tuple of (tested_count, deleted_count). The
            callback is responsible for checking items in the range [start, stop)
            and removing expired entries.
        delay: The delay in seconds between expiration check iterations. The thread
            will wait this duration (or until stopped) before starting the next
            iteration. Must be non-negative.
        max_checks_per_iteration: Maximum number of cache items to check in a single
            iteration. This limits the work done per iteration to avoid blocking.
            If 0, no checks are performed. If positive, the callback will be invoked
            with a range of indices to check.
        log: Whether to enable debug logging for expiration operations. If True,
            debug messages will be logged when items are checked and deleted.

    Attributes:
        clean_callback: The callback function for cleaning expired entries.
        delay: Delay between iterations in seconds.
        max_checks_per_iteration: Maximum items to check per iteration.
        log: Whether debug logging is enabled.

    Example:
        >>> from atomic_lru._storage import _ExpirationThread
        >>> def clean_func(start, stop):
        ...     # Check items from start to stop
        ...     return (10, 2)  # tested 10, deleted 2
        >>> thread = _ExpirationThread(
        ...     clean_callback=clean_func,
        ...     delay=5.0,
        ...     max_checks_per_iteration=1000
        ... )
        >>> thread.start()  # Start the background thread
        >>> # Thread runs in background, checking every 5 seconds
        >>> thread.stop(wait=True)  # Stop and wait for completion
    """

    clean_callback: Callable[[int | None, int | None], tuple[int, int]]
    delay: float
    max_checks_per_iteration: int
    log: bool = False

    # Internal threading event used to signal thread termination
    _stop_event: threading.Event = field(default_factory=threading.Event)

    # Internal thread instance
    _thread: threading.Thread | None = None

    @cached_property
    def logger(self) -> logging.Logger:
        """Get the logger instance for this expiration thread.

        Returns:
            A logger instance with the name "atomic_lru.ExpirationThread".
            The logger is cached after first access for efficiency.
        """
        return logging.getLogger("atomic_lru.ExpirationThread")

    def _debug(self, message: str, *args, **kwargs) -> None:
        if self.log:
            self.logger.debug(message, *args, **kwargs)

    def start(self) -> None:
        """Start the expiration thread.

        Creates and starts a daemon thread that runs the expiration loop. If the
        thread is already running, this method does nothing. The thread will
        automatically terminate when the main process exits (daemon thread).

        Note:
            The thread is started as a daemon thread, meaning it will not prevent
            the program from exiting if it's still running.
        """
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self.loop, daemon=True)
        self._thread.start()
        self._debug("Expiration thread started")

    def stop(self, wait: bool = False) -> None:
        """Stop the expiration thread.

        Signals the thread to stop by setting the stop event. If the thread is not
        running, this method does nothing.

        Args:
            wait: If True, blocks until the thread has fully terminated. If False,
                returns immediately after signaling the thread to stop. Defaults to
                False.

        Note:
            When `wait=False`, the thread may continue running briefly after this
            method returns. Use `wait=True` to ensure the thread has fully stopped
            before proceeding.
        """
        if self._thread is None:
            return
        self._stop_event.set()
        if wait:
            self._thread.join()
            self._debug("Expiration thread stopped")
        else:
            self._debug("Stop event set for expiration thread")

    def loop(self) -> None:
        """Main loop executed by the expiration thread.

        Continuously checks for expired cache entries in a round-robin fashion.
        The loop:
        1. Checks a batch of items (up to `max_checks_per_iteration`) starting from
           a tracked index position
        2. Calls the `clean_callback` to test and delete expired items
        3. Updates the start index for the next iteration (or resets to 0 if all
           items have been checked)
        4. Waits for `delay` seconds before the next iteration

        The loop terminates when the stop event is set via `stop()`. If
        `max_checks_per_iteration` is 0, no checks are performed but the loop
        continues to wait, allowing the thread to be stopped gracefully.

        Note:
            This method is intended to be run in a separate thread and should not
            be called directly. Use `start()` to begin the thread execution.
        """
        start_index: int = 0
        while not self._stop_event.is_set():
            if self.max_checks_per_iteration > 0:
                tested, deleted = self.clean_callback(
                    start_index, start_index + self.max_checks_per_iteration
                )
                if tested == 0:
                    start_index = 0  # restart from the beginning
                else:
                    start_index += tested
                if deleted > 0:
                    self._debug("Checked %d items, deleted %d items", tested, deleted)
            # Wait until self.delay seconds (or until the stop event is set)
            self._stop_event.wait(self.delay)
