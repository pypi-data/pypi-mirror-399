"""
RiskState - Runtime state representing the current risk situation.

This is the "conscience" of the trading bot.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import time


@dataclass
class RiskState:
    """
    Mutable runtime state for risk management.
    
    Tracks the current state of:
    - Account equity and peak (for drawdown calculation)
    - Number of open positions
    - Session-specific metrics
    - Kill switch status
    
    Attributes:
        equity_peak: High watermark of account equity.
        current_equity: Current account equity value.
        open_positions: Number of currently open positions.
        session_loss: Accumulated loss in current session (as decimal).
        trading_enabled: Master kill switch state.
        session_start: Timestamp when current session started.
        last_update: Timestamp of last state update.
        kill_switch_reason: Reason for kill switch activation (if any).
    """
    
    # Equity tracking
    equity_peak: float = 0.0
    current_equity: float = 0.0
    
    # Position tracking
    open_positions: int = 0
    
    # Session tracking
    session_loss: float = 0.0
    session_start: float = field(default_factory=time.time)
    
    # Kill switch
    trading_enabled: bool = True
    kill_switch_reason: Optional[str] = None
    
    # Metadata
    last_update: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Initialize peak if not set."""
        if self.equity_peak == 0 and self.current_equity > 0:
            self.equity_peak = self.current_equity
    
    @property
    def current_drawdown(self) -> float:
        """
        Calculate current drawdown from peak.
        
        Returns:
            Drawdown as a decimal (0.15 = 15% drawdown).
            Returns 0 if equity_peak is 0 or current is at/above peak.
        """
        if self.equity_peak <= 0:
            return 0.0
        if self.current_equity >= self.equity_peak:
            return 0.0
        return (self.equity_peak - self.current_equity) / self.equity_peak
    
    @property
    def is_trading_allowed(self) -> bool:
        """Check if trading is currently allowed."""
        return self.trading_enabled
    
    def update_equity(self, new_equity: float) -> None:
        """
        Update current equity and peak if new high.
        
        Args:
            new_equity: New equity value.
        """
        self.current_equity = new_equity
        if new_equity > self.equity_peak:
            self.equity_peak = new_equity
        self.last_update = time.time()
    
    def record_loss(self, loss_amount: float) -> None:
        """
        Record a loss in the current session.
        
        Args:
            loss_amount: Loss amount as positive decimal (0.02 = 2% loss).
        """
        self.session_loss += abs(loss_amount)
        self.last_update = time.time()
    
    def increment_positions(self) -> None:
        """Increment open position count."""
        self.open_positions += 1
        self.last_update = time.time()
    
    def decrement_positions(self) -> None:
        """Decrement open position count (cannot go below 0)."""
        self.open_positions = max(0, self.open_positions - 1)
        self.last_update = time.time()
    
    def disable_trading(self, reason: str) -> None:
        """
        Activate kill switch - disable all trading.
        
        Args:
            reason: Reason for disabling trading.
        """
        self.trading_enabled = False
        self.kill_switch_reason = reason
        self.last_update = time.time()
    
    def enable_trading(self) -> None:
        """
        Re-enable trading (manual reset).
        
        WARNING: This should only be called by explicit user action,
        never automatically.
        """
        self.trading_enabled = True
        self.kill_switch_reason = None
        self.last_update = time.time()
    
    def reset_session(self) -> None:
        """Reset session-specific metrics."""
        self.session_loss = 0.0
        self.session_start = time.time()
        self.last_update = time.time()
    
    def reset_peak(self, new_peak: Optional[float] = None) -> None:
        """
        Reset equity peak (for manual intervention).
        
        Args:
            new_peak: Optional new peak value. If None, uses current equity.
        """
        self.equity_peak = new_peak if new_peak is not None else self.current_equity
        self.last_update = time.time()
    
    def to_dict(self) -> dict:
        """Export state as dictionary for persistence."""
        return {
            "equity_peak": self.equity_peak,
            "current_equity": self.current_equity,
            "open_positions": self.open_positions,
            "session_loss": self.session_loss,
            "session_start": self.session_start,
            "trading_enabled": self.trading_enabled,
            "kill_switch_reason": self.kill_switch_reason,
            "last_update": self.last_update,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RiskState":
        """Create state from dictionary."""
        return cls(
            equity_peak=data.get("equity_peak", 0.0),
            current_equity=data.get("current_equity", 0.0),
            open_positions=data.get("open_positions", 0),
            session_loss=data.get("session_loss", 0.0),
            session_start=data.get("session_start", time.time()),
            trading_enabled=data.get("trading_enabled", True),
            kill_switch_reason=data.get("kill_switch_reason"),
            last_update=data.get("last_update", time.time()),
        )
    
    def __str__(self) -> str:
        """Human-readable state representation."""
        status = "ENABLED" if self.trading_enabled else f"DISABLED ({self.kill_switch_reason})"
        return (
            f"RiskState(\n"
            f"  equity: {self.current_equity:.2f} (peak: {self.equity_peak:.2f})\n"
            f"  drawdown: {self.current_drawdown:.2%}\n"
            f"  positions: {self.open_positions}\n"
            f"  session_loss: {self.session_loss:.2%}\n"
            f"  trading: {status}\n"
            f")"
        )
