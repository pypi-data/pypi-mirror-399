from time import monotonic
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Stopwatch:
    """Core logic for a stopwatch."""

    _start_time: Optional[float] = None
    _accumulated_time: float = 0.0
    _running: bool = False

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def elapsed(self) -> float:
        """Return the total elapsed time in seconds."""
        if self._running:
            return self._accumulated_time + (monotonic() - self._start_time)
        return self._accumulated_time

    def start(self):
        if not self._running:
            self._start_time = monotonic()
            self._running = True

    def stop(self):
        if self._running:
            self._accumulated_time += monotonic() - self._start_time
            self._start_time = None
            self._running = False

    def reset(self):
        self._running = False
        self._accumulated_time = 0.0
        self._start_time = None

    def toggle(self):
        if self._running:
            self.stop()
        else:
            self.start()


@dataclass
class Countdown:
    """Core logic for a countdown timer."""

    initial_seconds: int
    _time_left: float = field(init=False)
    _last_tick: Optional[float] = field(init=False, default=None)
    _running: bool = field(init=False, default=True)

    def __post_init__(self):
        self._time_left = float(self.initial_seconds)
        self._last_tick = monotonic()

    @property
    def time_left(self) -> float:
        return max(0.0, self._time_left)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_finished(self) -> bool:
        return self._time_left <= 0

    def tick(self):
        """Update the timer based on elapsed real time."""
        if self._running and self._time_left > 0:
            now = monotonic()
            if self._last_tick:
                delta = now - self._last_tick
                self._time_left -= delta
            self._last_tick = now
        else:
            self._last_tick = monotonic()

    def pause(self):
        self._running = False
        self._last_tick = None

    def resume(self):
        if not self._running:
            self._running = True
            self._last_tick = monotonic()

    def toggle(self):
        if self._running:
            self.pause()
        else:
            self.resume()
