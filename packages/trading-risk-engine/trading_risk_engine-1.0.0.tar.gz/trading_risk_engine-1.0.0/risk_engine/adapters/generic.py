"""
GenericAdapter - Plain Python integration.

For use without any trading framework - direct Python usage.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from ..core.config import RiskConfig
from ..core.state import RiskState
from ..core.engine import RiskEngine, TradeDecision, DecisionType
from ..interfaces.position import TradeRequest, PositionSide


class GenericAdapter:
    """
    Generic Python adapter for the Risk Engine.
    
    Provides a simple interface for using the Risk Engine
    without any specific trading framework.
    
    Usage:
        adapter = GenericAdapter(
            initial_equity=10000,
            max_drawdown=0.15,
            risk_per_trade=0.01,
        )
        
        # Evaluate a trade
        decision = adapter.evaluate_trade(
            symbol="BTC/USDT",
            side="long",
            entry_price=50000,
            stop_loss=49000,
        )
        
        if decision.is_approved:
            execute_order(decision.position_size)
    """
    
    def __init__(
        self,
        initial_equity: float,
        max_drawdown: float = 0.15,
        risk_per_trade: float = 0.01,
        max_leverage: float = 3.0,
        max_positions: int = 3,
        session_drawdown: float = 0.05,
    ) -> None:
        """
        Initialize the generic adapter.
        
        Args:
            initial_equity: Starting account equity.
            max_drawdown: Maximum allowed drawdown (0.15 = 15%).
            risk_per_trade: Risk per trade (0.01 = 1%).
            max_leverage: Maximum allowed leverage.
            max_positions: Maximum concurrent positions.
            session_drawdown: Session drawdown limit.
        """
        self.config = RiskConfig(
            max_account_drawdown=max_drawdown,
            risk_per_trade=risk_per_trade,
            max_leverage=max_leverage,
            max_open_positions=max_positions,
            session_drawdown=session_drawdown,
        )
        
        self.state = RiskState(
            current_equity=initial_equity,
            equity_peak=initial_equity,
        )
        
        self.engine = RiskEngine(self.config, self.state)
    
    def evaluate_trade(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        stop_loss: float,
        take_profit: Optional[float] = None,
        leverage: float = 1.0,
    ) -> TradeDecision:
        """
        Evaluate a potential trade.
        
        Args:
            symbol: Trading pair (e.g., "BTC/USDT").
            side: "long" or "short".
            entry_price: Expected entry price.
            stop_loss: Stop loss price.
            take_profit: Optional take profit price.
            leverage: Requested leverage.
            
        Returns:
            TradeDecision with the result.
        """
        position_side = PositionSide.LONG if side.lower() == "long" else PositionSide.SHORT
        
        request = TradeRequest(
            symbol=symbol,
            side=position_side,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            leverage=leverage,
        )
        
        return self.engine.evaluate_trade(request)
    
    def update_equity(self, new_equity: float) -> None:
        """
        Update current equity.
        
        Call this regularly to keep drawdown monitoring accurate.
        
        Args:
            new_equity: Current account equity.
        """
        self.engine.update_state(new_equity)
    
    def on_trade_open(self) -> None:
        """Record that a trade has been opened."""
        self.engine.record_trade_open()
    
    def on_trade_close(self, pnl_percent: float) -> None:
        """
        Record that a trade has been closed.
        
        Args:
            pnl_percent: Profit/loss as decimal (-0.02 = 2% loss).
        """
        self.engine.record_trade_close(pnl_percent)
    
    def reset_session(self) -> None:
        """Reset session metrics (call at start of new trading day)."""
        self.engine.reset_session()
    
    def emergency_stop(self, reason: str = "Manual emergency stop") -> None:
        """
        Trigger emergency stop - disable all trading.
        
        Args:
            reason: Reason for emergency stop.
        """
        self.engine.emergency_shutdown(reason)
    
    def manual_reset(self) -> None:
        """
        Manually reset the kill switch.
        
        WARNING: Only call after understanding why trading was stopped.
        """
        self.engine.manual_reset()
    
    def is_trading_enabled(self) -> bool:
        """Check if trading is currently enabled."""
        return self.state.trading_enabled
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return self.engine.get_status()
    
    def __str__(self) -> str:
        """Human-readable status."""
        return str(self.engine)
