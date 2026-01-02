"""
TradingClock - Time and session abstraction.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Callable


@dataclass
class TradingClock:
    """
    Abstraction for time and trading sessions.
    
    Allows for custom session definitions and time providers
    (useful for backtesting with simulated time).
    
    Attributes:
        session_duration_hours: Duration of a trading session in hours.
        time_provider: Optional custom time provider function.
    """
    
    session_duration_hours: float = 24.0
    time_provider: Optional[Callable[[], float]] = None
    _session_start: float = field(default_factory=time.time, init=False)
    
    def __post_init__(self) -> None:
        """Initialize session start time."""
        self._session_start = self.now()
    
    def now(self) -> float:
        """
        Get current timestamp.
        
        Returns:
            Current Unix timestamp.
        """
        if self.time_provider:
            return self.time_provider()
        return time.time()
    
    def now_datetime(self) -> datetime:
        """
        Get current time as datetime.
        
        Returns:
            Current time as UTC datetime.
        """
        return datetime.fromtimestamp(self.now(), tz=timezone.utc)
    
    @property
    def session_start(self) -> float:
        """Get session start timestamp."""
        return self._session_start
    
    @property
    def session_elapsed_hours(self) -> float:
        """Get hours elapsed since session start."""
        return (self.now() - self._session_start) / 3600
    
    def is_session_active(self) -> bool:
        """
        Check if current session is still active.
        
        Returns:
            True if session is active, False if expired.
        """
        return self.session_elapsed_hours < self.session_duration_hours
    
    def reset_session(self) -> None:
        """Start a new session."""
        self._session_start = self.now()
    
    def time_until_session_end(self) -> float:
        """
        Get time remaining in current session.
        
        Returns:
            Remaining time in hours.
        """
        remaining = self.session_duration_hours - self.session_elapsed_hours
        return max(0, remaining)
    
    def is_within_hours(self, start_hour: int, end_hour: int) -> bool:
        """
        Check if current time is within specified hours (UTC).
        
        Args:
            start_hour: Start hour (0-23).
            end_hour: End hour (0-23).
            
        Returns:
            True if current hour is within range.
        """
        current_hour = self.now_datetime().hour
        
        if start_hour <= end_hour:
            return start_hour <= current_hour < end_hour
        else:
            # Handles overnight ranges like 22:00 - 06:00
            return current_hour >= start_hour or current_hour < end_hour
    
    def is_weekday(self) -> bool:
        """
        Check if current day is a weekday.
        
        Returns:
            True if Monday-Friday.
        """
        return self.now_datetime().weekday() < 5
    
    def is_weekend(self) -> bool:
        """
        Check if current day is weekend.
        
        Returns:
            True if Saturday or Sunday.
        """
        return self.now_datetime().weekday() >= 5


class SimulatedClock(TradingClock):
    """
    Clock with simulated time for backtesting.
    
    Attributes:
        simulated_time: The simulated Unix timestamp.
    """
    
    def __init__(
        self,
        start_time: float = None,
        session_duration_hours: float = 24.0,
    ) -> None:
        """
        Initialize simulated clock.
        
        Args:
            start_time: Starting timestamp (defaults to current time).
            session_duration_hours: Session duration in hours.
        """
        self._simulated_time = start_time or time.time()
        super().__init__(
            session_duration_hours=session_duration_hours,
            time_provider=self._get_simulated_time,
        )
    
    def _get_simulated_time(self) -> float:
        """Return simulated time."""
        return self._simulated_time
    
    def set_time(self, timestamp: float) -> None:
        """Set simulated time to specific timestamp."""
        self._simulated_time = timestamp
    
    def advance(self, seconds: float) -> None:
        """Advance simulated time by specified seconds."""
        self._simulated_time += seconds
    
    def advance_hours(self, hours: float) -> None:
        """Advance simulated time by hours."""
        self.advance(hours * 3600)
    
    def advance_days(self, days: float) -> None:
        """Advance simulated time by days."""
        self.advance(days * 86400)
