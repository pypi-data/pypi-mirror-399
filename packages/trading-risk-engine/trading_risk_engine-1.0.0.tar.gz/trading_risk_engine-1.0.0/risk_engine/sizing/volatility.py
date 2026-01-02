"""
VolatilitySizer - ATR/volatility-based position sizing.

Placeholder for V1.1 - Basic structure only.

The idea: use Average True Range (ATR) or other volatility measures
to dynamically adjust position sizes. More volatile markets = smaller positions.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, List

from .fixed_risk import SizingResult

if TYPE_CHECKING:
    from ..core.config import RiskConfig


class VolatilitySizer:
    """
    Volatility-based position sizing (V1.1 placeholder).
    
    Formula:
        position_size = (equity * risk_percent) / (ATR * multiplier)
    
    Where:
        - ATR is the Average True Range
        - multiplier adjusts stop distance based on ATR
    
    Benefits:
        - Automatically trades smaller during high volatility
        - Normalizes risk across different market conditions
        - Adapts to changing market regimes
    
    Future Implementation:
        - Accept OHLC data to calculate ATR internally
        - Support configurable ATR period
        - Support multiple volatility measures (ATR, std dev, etc.)
    
    Usage (planned):
        sizer = VolatilitySizer(config)
        sizer.update_volatility(atr_14=500)  # Current ATR value
        result = sizer.calculate(equity=10000, entry_price=50000)
    """
    
    def __init__(
        self,
        config: "RiskConfig",
        atr_multiplier: float = 2.0,
    ) -> None:
        """
        Initialize volatility sizer.
        
        Args:
            config: Risk configuration.
            atr_multiplier: Multiplier for ATR-based stop (default 2x ATR).
        """
        self.config = config
        self.atr_multiplier = atr_multiplier
        self._current_atr: Optional[float] = None
    
    def update_volatility(self, atr: float) -> None:
        """
        Update current ATR value.
        
        Args:
            atr: Current ATR value.
        """
        self._current_atr = atr
    
    def calculate(
        self,
        equity: float,
        entry_price: float,
        atr: Optional[float] = None,
    ) -> SizingResult:
        """
        Calculate position size based on volatility.
        
        Args:
            equity: Current account equity.
            entry_price: Expected entry price.
            atr: ATR value (uses stored value if not provided).
            
        Returns:
            SizingResult with calculated position size.
        """
        current_atr = atr or self._current_atr
        
        if current_atr is None or current_atr <= 0:
            return SizingResult(
                position_size=0.0,
                risk_amount=0.0,
                reason="ATR not available - cannot calculate volatility-based size",
            )
        
        if equity <= 0:
            return SizingResult(
                position_size=0.0,
                risk_amount=0.0,
                reason="Invalid equity: must be positive",
            )
        
        if entry_price <= 0:
            return SizingResult(
                position_size=0.0,
                risk_amount=0.0,
                reason="Invalid entry price: must be positive",
            )
        
        # Stop distance = ATR * multiplier
        stop_distance = current_atr * self.atr_multiplier
        
        # Risk amount
        risk_amount = equity * self.config.risk_per_trade
        
        # Position size
        position_size = risk_amount / stop_distance
        
        # Apply limits
        min_size = self.config.min_position_size
        max_size = (equity * self.config.max_position_size) / entry_price
        
        if position_size < min_size:
            return SizingResult(
                position_size=0.0,
                risk_amount=risk_amount,
                reason=f"ATR-based size {position_size:.8f} below minimum {min_size}",
            )
        
        if position_size > max_size:
            capped_risk = max_size * stop_distance
            return SizingResult(
                position_size=max_size,
                risk_amount=capped_risk,
                reason=f"ATR-based size capped at maximum: {max_size:.8f}",
            )
        
        return SizingResult(
            position_size=position_size,
            risk_amount=risk_amount,
            reason=f"ATR-based size: {position_size:.8f} (ATR: {current_atr}, stop: {stop_distance:.2f})",
        )
    
    def calculate_atr(self, high: List[float], low: List[float], close: List[float], period: int = 14) -> float:
        """
        Calculate ATR from OHLC data.
        
        Args:
            high: List of high prices.
            low: List of low prices.
            close: List of close prices.
            period: ATR period (default 14).
            
        Returns:
            Calculated ATR value.
        """
        if len(high) < period + 1 or len(low) < period + 1 or len(close) < period + 1:
            return 0.0
        
        true_ranges = []
        
        for i in range(1, len(high)):
            tr = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )
            true_ranges.append(tr)
        
        if len(true_ranges) < period:
            return sum(true_ranges) / len(true_ranges) if true_ranges else 0.0
        
        # Simple moving average of true ranges
        return sum(true_ranges[-period:]) / period
    
    def get_implied_stop(self, entry_price: float, atr: Optional[float] = None, is_long: bool = True) -> float:
        """
        Calculate implied stop loss price based on ATR.
        
        Args:
            entry_price: Entry price.
            atr: ATR value (uses stored if not provided).
            is_long: True for long, False for short.
            
        Returns:
            Implied stop loss price.
        """
        current_atr = atr or self._current_atr
        if current_atr is None:
            return 0.0
        
        stop_distance = current_atr * self.atr_multiplier
        
        if is_long:
            return entry_price - stop_distance
        else:
            return entry_price + stop_distance
    
    def __str__(self) -> str:
        """Human-readable configuration."""
        atr_status = f"{self._current_atr:.2f}" if self._current_atr else "Not set"
        return f"VolatilitySizer(multiplier={self.atr_multiplier}x, ATR={atr_status})"
