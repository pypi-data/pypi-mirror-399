"""
FreqtradeRiskAdapter - Integration with Freqtrade.

This adapter hooks into Freqtrade's lifecycle to provide
risk management without modifying the trading strategy.

Key integration points:
- bot_start: Initialize state
- custom_stake_amount: Override stake with risk-based sizing
- confirm_trade_entry: Gate entry based on risk checks
- confirm_trade_exit: Optional exit validation
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass
import logging

from ..core.config import RiskConfig
from ..core.state import RiskState
from ..core.engine import RiskEngine, TradeDecision, DecisionType
from ..interfaces.position import TradeRequest, PositionSide

if TYPE_CHECKING:
    # These would be Freqtrade types - we use Any for now
    pass


logger = logging.getLogger(__name__)


@dataclass
class FreqtradeConfig:
    """
    Freqtrade-specific configuration.
    
    Attributes:
        max_account_drawdown: Maximum allowed account drawdown.
        risk_per_trade: Risk per trade as decimal.
        max_leverage: Maximum allowed leverage.
        max_open_trades: Maximum concurrent trades (maps to max_open_positions).
        session_drawdown: Session drawdown limit.
        use_custom_stoploss: Whether to use custom stoploss from strategy.
        default_stoploss_pct: Default stoploss if not provided (0.02 = 2%).
    """
    max_account_drawdown: float = 0.15
    risk_per_trade: float = 0.01
    max_leverage: float = 3.0
    max_open_trades: int = 3
    session_drawdown: float = 0.05
    use_custom_stoploss: bool = True
    default_stoploss_pct: float = 0.02


class FreqtradeRiskAdapter:
    """
    Risk Engine adapter for Freqtrade integration.
    
    This adapter is designed to be used within a Freqtrade strategy.
    It intercepts trade decisions to apply risk management.
    
    Integration Methods:
    
    1. In strategy __init__:
        self.risk_adapter = FreqtradeRiskAdapter(config)
    
    2. In bot_start():
        self.risk_adapter.on_bot_start(account_balance)
    
    3. In custom_stake_amount():
        return self.risk_adapter.get_stake_amount(...)
    
    4. In confirm_trade_entry():
        return self.risk_adapter.confirm_trade_entry(...)
    
    Example Strategy Integration:
    
        from risk_engine.adapters.freqtrade import FreqtradeRiskAdapter, FreqtradeConfig
        
        class MyStrategy(IStrategy):
            def __init__(self, config):
                super().__init__(config)
                self.risk_adapter = FreqtradeRiskAdapter(
                    FreqtradeConfig(
                        max_account_drawdown=0.15,
                        risk_per_trade=0.01,
                    )
                )
            
            def bot_start(self, **kwargs):
                balance = self.wallets.get_total_stake_amount()
                self.risk_adapter.on_bot_start(balance)
            
            def custom_stake_amount(self, pair, current_time, current_rate,
                                    proposed_stake, min_stake, max_stake,
                                    leverage, entry_tag, side, **kwargs):
                return self.risk_adapter.get_stake_amount(
                    pair=pair,
                    entry_price=current_rate,
                    stoploss_price=current_rate * (1 - abs(self.stoploss)),
                    proposed_stake=proposed_stake,
                    side=side,
                )
            
            def confirm_trade_entry(self, pair, order_type, amount, rate,
                                    time_in_force, current_time, entry_tag,
                                    side, **kwargs):
                return self.risk_adapter.confirm_trade_entry(
                    pair=pair,
                    entry_price=rate,
                    side=side,
                )
    """
    
    def __init__(self, config: FreqtradeConfig) -> None:
        """
        Initialize the Freqtrade adapter.
        
        Args:
            config: Freqtrade-specific configuration.
        """
        self.ft_config = config
        
        self.risk_config = RiskConfig(
            max_account_drawdown=config.max_account_drawdown,
            risk_per_trade=config.risk_per_trade,
            max_leverage=config.max_leverage,
            max_open_positions=config.max_open_trades,
            session_drawdown=config.session_drawdown,
        )
        
        # State will be initialized in on_bot_start
        self.state: Optional[RiskState] = None
        self.engine: Optional[RiskEngine] = None
        
        self._initialized = False
    
    def on_bot_start(self, initial_balance: float) -> None:
        """
        Initialize risk state when bot starts.
        
        Call this from strategy's bot_start() callback.
        
        Args:
            initial_balance: Current account balance/equity.
        """
        self.state = RiskState(
            current_equity=initial_balance,
            equity_peak=initial_balance,
        )
        
        self.engine = RiskEngine(self.risk_config, self.state)
        self._initialized = True
        
        logger.info(
            f"RiskEngine initialized: equity={initial_balance}, "
            f"max_dd={self.risk_config.max_account_drawdown:.1%}, "
            f"risk_per_trade={self.risk_config.risk_per_trade:.1%}"
        )
    
    def update_equity(self, current_equity: float) -> None:
        """
        Update current equity.
        
        Call this regularly (e.g., in bot_loop_start) to keep
        drawdown monitoring accurate.
        
        Args:
            current_equity: Current account equity.
        """
        if not self._check_initialized():
            return
        
        self.engine.update_state(current_equity)
    
    def get_stake_amount(
        self,
        pair: str,
        entry_price: float,
        stoploss_price: float,
        proposed_stake: float,
        side: str = "long",
        leverage: float = 1.0,
    ) -> Optional[float]:
        """
        Calculate risk-based stake amount.
        
        Call this from custom_stake_amount() callback.
        
        Args:
            pair: Trading pair.
            entry_price: Expected entry price.
            stoploss_price: Stop loss price.
            proposed_stake: Freqtrade's proposed stake.
            side: "long" or "short".
            leverage: Applied leverage.
            
        Returns:
            Risk-adjusted stake amount, or None to reject trade.
        """
        if not self._check_initialized():
            return None
        
        position_side = PositionSide.LONG if side.lower() == "long" else PositionSide.SHORT
        
        request = TradeRequest(
            symbol=pair,
            side=position_side,
            entry_price=entry_price,
            stop_loss=stoploss_price,
            leverage=leverage,
        )
        
        decision = self.engine.evaluate_trade(request)
        
        if decision.decision == DecisionType.SHUTDOWN:
            logger.warning(f"KILL SWITCH ACTIVATED: {decision.reason}")
            return None
        
        if decision.decision == DecisionType.REJECT:
            logger.info(f"Trade rejected: {decision.reason}")
            return None
        
        # Calculate stake from position size
        stake = decision.position_size * entry_price
        
        logger.debug(
            f"Risk-sized trade: {pair} size={decision.position_size:.6f}, "
            f"stake={stake:.2f} (proposed: {proposed_stake:.2f})"
        )
        
        return stake
    
    def confirm_trade_entry(
        self,
        pair: str,
        entry_price: float,
        side: str = "long",
        stoploss_pct: Optional[float] = None,
    ) -> bool:
        """
        Confirm trade entry is allowed.
        
        Call this from confirm_trade_entry() callback for an additional
        safety gate (if not using custom_stake_amount).
        
        Args:
            pair: Trading pair.
            entry_price: Entry price.
            side: "long" or "short".
            stoploss_pct: Optional stoploss percentage.
            
        Returns:
            True if trade is allowed, False to reject.
        """
        if not self._check_initialized():
            return False
        
        # Check if trading is enabled
        if not self.state.trading_enabled:
            logger.warning(f"Trade blocked - trading disabled: {self.state.kill_switch_reason}")
            return False
        
        # Use provided or default stoploss
        sl_pct = stoploss_pct or self.ft_config.default_stoploss_pct
        
        if side.lower() == "long":
            stop_loss = entry_price * (1 - sl_pct)
        else:
            stop_loss = entry_price * (1 + sl_pct)
        
        position_side = PositionSide.LONG if side.lower() == "long" else PositionSide.SHORT
        
        request = TradeRequest(
            symbol=pair,
            side=position_side,
            entry_price=entry_price,
            stop_loss=stop_loss,
        )
        
        decision = self.engine.evaluate_trade(request)
        
        if decision.decision == DecisionType.SHUTDOWN:
            logger.warning(f"KILL SWITCH: {decision.reason}")
            return False
        
        if decision.decision == DecisionType.REJECT:
            logger.info(f"Trade rejected: {decision.reason}")
            return False
        
        return True
    
    def on_trade_entry(self, trade_info: Dict[str, Any]) -> None:
        """
        Record trade entry.
        
        Call this when a trade is actually opened.
        
        Args:
            trade_info: Trade information dictionary.
        """
        if not self._check_initialized():
            return
        
        self.engine.record_trade_open()
        logger.debug(f"Trade opened, positions: {self.state.open_positions}")
    
    def on_trade_exit(self, trade_info: Dict[str, Any], profit_ratio: float) -> None:
        """
        Record trade exit.
        
        Call this when a trade is closed.
        
        Args:
            trade_info: Trade information dictionary.
            profit_ratio: Profit as decimal (-0.02 = 2% loss).
        """
        if not self._check_initialized():
            return
        
        self.engine.record_trade_close(profit_ratio)
        logger.debug(
            f"Trade closed with {profit_ratio:.2%}, "
            f"positions: {self.state.open_positions}"
        )
    
    def is_trading_enabled(self) -> bool:
        """Check if trading is currently enabled."""
        if not self._initialized or self.state is None:
            return False
        return self.state.trading_enabled
    
    def get_status(self) -> Dict[str, Any]:
        """Get current risk engine status."""
        if not self._initialized or self.engine is None:
            return {"initialized": False}
        
        status = self.engine.get_status()
        status["initialized"] = True
        return status
    
    def emergency_shutdown(self, reason: str) -> None:
        """
        Trigger emergency shutdown.
        
        Args:
            reason: Reason for shutdown.
        """
        if self._check_initialized():
            self.engine.emergency_shutdown(reason)
            logger.critical(f"EMERGENCY SHUTDOWN: {reason}")
    
    def manual_reset(self) -> None:
        """
        Manually reset the kill switch.
        
        WARNING: Only call after understanding why trading was stopped.
        """
        if self._check_initialized():
            self.engine.manual_reset()
            logger.info("Kill switch manually reset")
    
    def _check_initialized(self) -> bool:
        """Check if adapter is properly initialized."""
        if not self._initialized:
            logger.error(
                "RiskAdapter not initialized! Call on_bot_start() first."
            )
            return False
        return True
    
    def __str__(self) -> str:
        """Human-readable status."""
        if not self._initialized:
            return "FreqtradeRiskAdapter(not initialized)"
        return f"FreqtradeRiskAdapter:\n{self.engine}"
