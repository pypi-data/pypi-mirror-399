"""
DrawdownGuard - Maximum drawdown logic and kill switch.

This is the MOST IMPORTANT guard in the system.
When drawdown limit is breached, trading is DISABLED.
No discussion. No override. No automatic re-enable.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.config import RiskConfig
    from ..core.state import RiskState


@dataclass(frozen=True)
class GuardResult:
    """
    Result of a guard check.
    
    Attributes:
        triggered: Whether the guard was triggered (limit breached).
        reason: Explanation of the result.
        value: Current value of the monitored metric.
        limit: The limit that was checked against.
    """
    triggered: bool
    reason: str
    value: float = 0.0
    limit: float = 0.0


class DrawdownGuard:
    """
    Monitors account drawdown and triggers kill switch when limit breached.
    
    Key behaviors:
    1. Calculates drawdown from equity peak
    2. Triggers at EXACT limit (not above)
    3. NO automatic re-enable - requires manual reset
    4. Separate session drawdown check
    
    Usage:
        guard = DrawdownGuard(config, state)
        result = guard.check()
        if result.triggered:
            shutdown_trading()
    """
    
    def __init__(self, config: "RiskConfig", state: "RiskState") -> None:
        """
        Initialize drawdown guard.
        
        Args:
            config: Risk configuration with drawdown limits.
            state: Runtime state with equity tracking.
        """
        self.config = config
        self.state = state
    
    def check(self) -> GuardResult:
        """
        Check if account drawdown limit is breached.
        
        This is the PRIMARY drawdown check. If triggered,
        the kill switch should be activated.
        
        Returns:
            GuardResult indicating if limit is breached.
        """
        current_dd = self.state.current_drawdown
        max_dd = self.config.max_account_drawdown
        
        if current_dd >= max_dd:
            return GuardResult(
                triggered=True,
                reason=(
                    f"KILL SWITCH: Account drawdown {current_dd:.2%} "
                    f"exceeds limit {max_dd:.2%}"
                ),
                value=current_dd,
                limit=max_dd,
            )
        
        return GuardResult(
            triggered=False,
            reason=f"Drawdown {current_dd:.2%} within limit {max_dd:.2%}",
            value=current_dd,
            limit=max_dd,
        )
    
    def check_session(self) -> GuardResult:
        """
        Check if session drawdown limit is breached.
        
        Session drawdown is more lenient - it just rejects
        new trades, doesn't trigger the kill switch.
        
        Returns:
            GuardResult indicating if session limit is breached.
        """
        session_loss = self.state.session_loss
        session_limit = self.config.session_drawdown
        
        if session_loss >= session_limit:
            return GuardResult(
                triggered=True,
                reason=(
                    f"Session loss {session_loss:.2%} "
                    f"exceeds limit {session_limit:.2%}"
                ),
                value=session_loss,
                limit=session_limit,
            )
        
        return GuardResult(
            triggered=False,
            reason=f"Session loss {session_loss:.2%} within limit {session_limit:.2%}",
            value=session_loss,
            limit=session_limit,
        )
    
    def get_remaining_drawdown(self) -> float:
        """
        Calculate remaining drawdown before limit.
        
        Returns:
            Remaining drawdown as decimal (0.05 = 5% remaining).
        """
        return max(0, self.config.max_account_drawdown - self.state.current_drawdown)
    
    def get_remaining_session_loss(self) -> float:
        """
        Calculate remaining session loss before limit.
        
        Returns:
            Remaining session loss as decimal.
        """
        return max(0, self.config.session_drawdown - self.state.session_loss)
    
    def would_breach(self, potential_loss: float) -> bool:
        """
        Check if a potential loss would breach the drawdown limit.
        
        Args:
            potential_loss: Potential loss as decimal (0.02 = 2% loss).
            
        Returns:
            True if this loss would trigger the kill switch.
        """
        projected_dd = self.state.current_drawdown + potential_loss
        return projected_dd >= self.config.max_account_drawdown
    
    def calculate_max_loss(self) -> float:
        """
        Calculate maximum loss allowed before kill switch.
        
        Returns:
            Maximum loss as absolute value in equity terms.
        """
        remaining_dd = self.get_remaining_drawdown()
        return self.state.current_equity * remaining_dd
    
    def __str__(self) -> str:
        """Human-readable status."""
        result = self.check()
        session = self.check_session()
        status = "⚠️ TRIGGERED" if result.triggered else "✓ OK"
        session_status = "⚠️ TRIGGERED" if session.triggered else "✓ OK"
        
        return (
            f"DrawdownGuard:\n"
            f"  Account: {result.value:.2%} / {result.limit:.2%} [{status}]\n"
            f"  Session: {session.value:.2%} / {session.limit:.2%} [{session_status}]\n"
            f"  Remaining: {self.get_remaining_drawdown():.2%}"
        )
