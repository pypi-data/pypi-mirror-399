"""
RiskEngine - The main orchestrator.

Pure logic, no side effects, no orders.
Only decisions: APPROVE, REJECT, or SHUTDOWN.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

from .config import RiskConfig
from .state import RiskState
from ..guards.drawdown import DrawdownGuard
from ..guards.leverage import LeverageGuard
from ..guards.exposure import ExposureGuard
from ..sizing.fixed_risk import FixedRiskSizer
from ..interfaces.position import TradeRequest


class DecisionType(Enum):
    """Possible trade decision outcomes."""
    APPROVE = auto()   # Trade allowed with calculated size
    REJECT = auto()    # Trade rejected due to risk limits
    SHUTDOWN = auto()  # Trading disabled - kill switch activated


@dataclass(frozen=True)
class TradeDecision:
    """
    Immutable result of a trade evaluation.
    
    Attributes:
        decision: The decision type (APPROVE/REJECT/SHUTDOWN).
        position_size: Calculated position size (0 if rejected).
        reason: Human-readable explanation for the decision.
        guard_triggered: Name of the guard that triggered rejection (if any).
    """
    decision: DecisionType
    position_size: float = 0.0
    reason: str = ""
    guard_triggered: Optional[str] = None
    
    @property
    def is_approved(self) -> bool:
        """Check if trade is approved."""
        return self.decision == DecisionType.APPROVE
    
    @property
    def is_rejected(self) -> bool:
        """Check if trade is rejected."""
        return self.decision == DecisionType.REJECT
    
    @property
    def is_shutdown(self) -> bool:
        """Check if this triggered a shutdown."""
        return self.decision == DecisionType.SHUTDOWN


class RiskEngine:
    """
    Main Risk Management Engine.
    
    Coordinates all guards and sizing logic to produce trade decisions.
    
    Design Principles:
    1. Fail Closed: Any error results in trade rejection
    2. Pure Logic: No side effects, no order execution
    3. Strategy Agnostic: No knowledge of indicators or signals
    
    Usage:
        config = RiskConfig(max_account_drawdown=0.15, risk_per_trade=0.01)
        state = RiskState(current_equity=10000, equity_peak=10000)
        engine = RiskEngine(config, state)
        
        decision = engine.evaluate_trade(trade_request)
        if decision.is_approved:
            execute_trade(decision.position_size)
    """
    
    def __init__(self, config: RiskConfig, state: RiskState) -> None:
        """
        Initialize the Risk Engine.
        
        Args:
            config: Risk configuration parameters.
            state: Current runtime state.
        """
        self.config = config
        self.state = state
        
        # Initialize guards
        self.drawdown_guard = DrawdownGuard(config, state)
        self.leverage_guard = LeverageGuard(config)
        self.exposure_guard = ExposureGuard(config, state)
        
        # Initialize sizer
        self.sizer = FixedRiskSizer(config)
    
    def evaluate_trade(
        self,
        request: TradeRequest,
        current_price: Optional[float] = None,
    ) -> TradeDecision:
        """
        Evaluate a trade request against all risk controls.
        
        This is the main entry point. Order of checks:
        1. Kill switch check (is trading enabled?)
        2. Drawdown check (are we within limits?)
        3. Exposure check (position limits)
        4. Calculate position size
        5. Leverage check (is resulting leverage acceptable?)
        
        Args:
            request: The trade request to evaluate.
            current_price: Current market price (optional, defaults to request.entry_price).
            
        Returns:
            TradeDecision with the result.
        """
        try:
            return self._evaluate_trade_internal(request, current_price)
        except Exception as e:
            # FAIL CLOSED: Any error = reject trade
            return TradeDecision(
                decision=DecisionType.REJECT,
                position_size=0.0,
                reason=f"Internal error (fail closed): {str(e)}",
                guard_triggered="error_handler",
            )
    
    def _evaluate_trade_internal(
        self,
        request: TradeRequest,
        current_price: Optional[float],
    ) -> TradeDecision:
        """Internal trade evaluation logic."""
        
        # Step 1: Check kill switch
        if not self.state.is_trading_allowed:
            return TradeDecision(
                decision=DecisionType.SHUTDOWN,
                position_size=0.0,
                reason=f"Trading disabled: {self.state.kill_switch_reason}",
                guard_triggered="kill_switch",
            )
        
        # Step 2: Check drawdown
        drawdown_check = self.drawdown_guard.check()
        if drawdown_check.triggered:
            # This is a shutdown, not just a rejection
            self.state.disable_trading(drawdown_check.reason)
            return TradeDecision(
                decision=DecisionType.SHUTDOWN,
                position_size=0.0,
                reason=drawdown_check.reason,
                guard_triggered="drawdown",
            )
        
        # Step 3: Check session drawdown
        session_check = self.drawdown_guard.check_session()
        if session_check.triggered:
            return TradeDecision(
                decision=DecisionType.REJECT,
                position_size=0.0,
                reason=session_check.reason,
                guard_triggered="session_drawdown",
            )
        
        # Step 4: Check exposure (position limits)
        exposure_check = self.exposure_guard.check()
        if exposure_check.triggered:
            return TradeDecision(
                decision=DecisionType.REJECT,
                position_size=0.0,
                reason=exposure_check.reason,
                guard_triggered="exposure",
            )
        
        # Step 5: Calculate position size
        price = current_price or request.entry_price
        size_result = self.sizer.calculate(
            equity=self.state.current_equity,
            entry_price=price,
            stop_loss_price=request.stop_loss,
        )
        
        if size_result.position_size <= 0:
            return TradeDecision(
                decision=DecisionType.REJECT,
                position_size=0.0,
                reason=size_result.reason,
                guard_triggered="sizing",
            )
        
        # Step 6: Check leverage
        leverage_check = self.leverage_guard.check(
            position_size=size_result.position_size,
            entry_price=price,
            equity=self.state.current_equity,
        )
        if leverage_check.triggered:
            return TradeDecision(
                decision=DecisionType.REJECT,
                position_size=0.0,
                reason=leverage_check.reason,
                guard_triggered="leverage",
            )
        
        # All checks passed - APPROVE
        return TradeDecision(
            decision=DecisionType.APPROVE,
            position_size=size_result.position_size,
            reason=f"Trade approved with size {size_result.position_size:.6f}",
        )
    
    def update_state(self, new_equity: float) -> None:
        """
        Update engine state with new equity value.
        
        This should be called regularly to keep drawdown monitoring accurate.
        
        Args:
            new_equity: Current account equity.
        """
        self.state.update_equity(new_equity)
        
        # Check if this update triggers drawdown limit
        check = self.drawdown_guard.check()
        if check.triggered:
            self.state.disable_trading(check.reason)
    
    def record_trade_open(self) -> None:
        """Record that a new trade has been opened."""
        self.state.increment_positions()
    
    def record_trade_close(self, pnl_percent: float) -> None:
        """
        Record that a trade has been closed.
        
        Args:
            pnl_percent: Profit/loss as decimal (-0.02 = 2% loss).
        """
        self.state.decrement_positions()
        if pnl_percent < 0:
            self.state.record_loss(abs(pnl_percent))
    
    def reset_session(self) -> None:
        """Reset session-specific metrics (typically done daily)."""
        self.state.reset_session()
    
    def emergency_shutdown(self, reason: str) -> None:
        """
        Trigger emergency shutdown.
        
        Args:
            reason: Reason for emergency shutdown.
        """
        self.state.disable_trading(f"EMERGENCY: {reason}")
    
    def manual_reset(self) -> None:
        """
        Manually reset the kill switch.
        
        WARNING: This should only be called by explicit user action.
        """
        self.state.enable_trading()
    
    def get_status(self) -> dict:
        """
        Get current engine status.
        
        Returns:
            Dictionary with current risk metrics.
        """
        return {
            "trading_enabled": self.state.trading_enabled,
            "kill_switch_reason": self.state.kill_switch_reason,
            "current_equity": self.state.current_equity,
            "equity_peak": self.state.equity_peak,
            "current_drawdown": self.state.current_drawdown,
            "max_drawdown_limit": self.config.max_account_drawdown,
            "session_loss": self.state.session_loss,
            "session_limit": self.config.session_drawdown,
            "open_positions": self.state.open_positions,
            "max_positions": self.config.max_open_positions,
            "drawdown_remaining": self.config.max_account_drawdown - self.state.current_drawdown,
        }
    
    def __str__(self) -> str:
        """Human-readable engine status."""
        status = self.get_status()
        return (
            f"RiskEngine Status:\n"
            f"  Trading: {'ENABLED' if status['trading_enabled'] else 'DISABLED'}\n"
            f"  Drawdown: {status['current_drawdown']:.2%} / {status['max_drawdown_limit']:.2%}\n"
            f"  Session Loss: {status['session_loss']:.2%} / {status['session_limit']:.2%}\n"
            f"  Positions: {status['open_positions']} / {status['max_positions']}\n"
        )
