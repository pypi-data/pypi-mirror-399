"""
Freqtrade Full Integration Example

A complete example showing how to integrate Trading Risk Engine
with a Freqtrade strategy for risk-controlled live trading.

Features:
- Automatic position sizing based on risk percentage
- Drawdown monitoring with kill switch
- Leverage guards
- Session-based exposure limits

Usage:
    1. Copy this file to your Freqtrade strategy directory
    2. Adjust RiskConfig parameters to your preferences
    3. Run with: freqtrade trade --strategy RiskManagedStrategy
"""

from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

from risk_engine import RiskConfig, RiskState
from risk_engine.adapters.freqtrade import FreqtradeRiskAdapter, FreqtradeConfig


class RiskManagedStrategy(IStrategy):
    """
    Example Freqtrade strategy with full Risk Engine integration.
    
    The Risk Engine controls:
    - Position sizing (fixed % risk per trade)
    - Drawdown limits (kill switch at max DD)
    - Leverage caps
    - Concurrent position limits
    """
    
    # Strategy parameters
    timeframe = '5m'
    stoploss = -0.02  # 2% stop loss
    minimal_roi = {"0": 0.01}  # 1% ROI target
    
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        
        # Initialize Risk Engine with your limits
        self.risk_adapter = FreqtradeRiskAdapter(
            FreqtradeConfig(
                max_account_drawdown=0.15,  # 15% max DD -> kill switch
                risk_per_trade=0.01,        # 1% risk per trade
                max_leverage=3.0,           # Max 3x leverage
                max_open_trades=3,          # Max 3 concurrent trades
                session_drawdown=0.05,      # 5% session loss limit
            )
        )
    
    def bot_start(self, **kwargs) -> None:
        """Initialize risk state when bot starts."""
        balance = self.wallets.get_total_stake_amount()
        self.risk_adapter.on_bot_start(balance)
    
    def bot_loop_start(self, current_time, **kwargs) -> None:
        """Update equity at start of each loop."""
        current_equity = self.wallets.get_total_stake_amount()
        self.risk_adapter.update_equity(current_equity)
    
    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float,
        max_stake: float,
        leverage: float,
        entry_tag: str,
        side: str,
        **kwargs,
    ) -> float:
        """
        Risk Engine controls position sizing.
        
        Returns the risk-calculated stake amount,
        or 0 to reject the trade entirely.
        """
        # Calculate stop loss price based on side
        stoploss_pct = abs(self.stoploss)
        if side == "long":
            stoploss_price = current_rate * (1 - stoploss_pct)
        else:
            stoploss_price = current_rate * (1 + stoploss_pct)
        
        # Get risk-adjusted stake from Risk Engine
        stake = self.risk_adapter.get_stake_amount(
            pair=pair,
            entry_price=current_rate,
            stoploss_price=stoploss_price,
            proposed_stake=proposed_stake,
            side=side,
            leverage=leverage,
        )
        
        if stake is None:
            return 0  # Trade rejected by Risk Engine
        
        # Ensure within Freqtrade's limits
        if min_stake and stake < min_stake:
            return min_stake
        if stake > max_stake:
            return max_stake
        
        return stake
    
    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time,
        entry_tag: str,
        side: str,
        **kwargs,
    ) -> bool:
        """Final confirmation gate from Risk Engine."""
        return self.risk_adapter.confirm_trade_entry(
            pair=pair,
            entry_price=rate,
            side=side,
            stoploss_pct=abs(self.stoploss),
        )
    
    def confirm_trade_exit(
        self,
        pair: str,
        trade,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        exit_reason: str,
        current_time,
        **kwargs,
    ) -> bool:
        """Record trade exit for risk tracking."""
        profit_ratio = trade.calc_profit_ratio(rate)
        self.risk_adapter.on_trade_exit(
            trade_info={"pair": pair, "exit_reason": exit_reason},
            profit_ratio=profit_ratio,
        )
        return True
    
    # --- Strategy Logic (Replace with your own) ---
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Add your indicators here."""
        # Example: RSI, MACD, Bollinger Bands, etc.
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Define your entry conditions here."""
        dataframe['enter_long'] = 0
        dataframe['enter_short'] = 0
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Define your exit conditions here."""
        dataframe['exit_long'] = 0
        dataframe['exit_short'] = 0
        return dataframe
