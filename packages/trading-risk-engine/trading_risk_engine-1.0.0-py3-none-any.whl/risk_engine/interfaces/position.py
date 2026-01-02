"""
Position - Abstraction for trading positions and trade requests.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class PositionSide(Enum):
    """Position direction."""
    LONG = auto()
    SHORT = auto()


@dataclass(frozen=True)
class Position:
    """
    Represents an open trading position.
    
    Attributes:
        symbol: Trading pair symbol (e.g., "BTC/USDT").
        side: Position direction (LONG or SHORT).
        size: Position size in base currency.
        entry_price: Average entry price.
        current_price: Current market price.
        leverage: Applied leverage.
        unrealized_pnl: Current unrealized P&L.
        liquidation_price: Estimated liquidation price.
    """
    
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    current_price: float = 0.0
    leverage: float = 1.0
    unrealized_pnl: float = 0.0
    liquidation_price: Optional[float] = None
    
    @property
    def notional_value(self) -> float:
        """Calculate notional value of position."""
        price = self.current_price if self.current_price > 0 else self.entry_price
        return abs(self.size) * price
    
    @property
    def margin_used(self) -> float:
        """Calculate margin used for this position."""
        return self.notional_value / self.leverage
    
    @property
    def pnl_percent(self) -> float:
        """Calculate P&L as percentage of margin."""
        if self.margin_used <= 0:
            return 0.0
        return self.unrealized_pnl / self.margin_used
    
    @property
    def distance_to_liquidation(self) -> Optional[float]:
        """
        Calculate distance to liquidation as percentage.
        
        Returns:
            Percentage distance to liquidation, or None if unknown.
        """
        if self.liquidation_price is None or self.current_price <= 0:
            return None
        
        if self.side == PositionSide.LONG:
            return (self.current_price - self.liquidation_price) / self.current_price
        else:
            return (self.liquidation_price - self.current_price) / self.current_price


@dataclass(frozen=True)
class TradeRequest:
    """
    Represents a request to open a new trade.
    
    This is the input to the Risk Engine for evaluation.
    
    Attributes:
        symbol: Trading pair symbol.
        side: Desired position side.
        entry_price: Expected entry price.
        stop_loss: Stop loss price (REQUIRED for risk calculation).
        take_profit: Take profit price (optional).
        leverage: Requested leverage.
        reason: Optional reason/signal name for the trade.
    """
    
    symbol: str
    side: PositionSide
    entry_price: float
    stop_loss: float
    take_profit: Optional[float] = None
    leverage: float = 1.0
    reason: str = ""
    
    @property
    def stop_loss_distance(self) -> float:
        """
        Calculate stop loss distance as absolute value.
        
        Returns:
            Absolute distance between entry and stop loss.
        """
        return abs(self.entry_price - self.stop_loss)
    
    @property
    def stop_loss_percent(self) -> float:
        """
        Calculate stop loss distance as percentage of entry price.
        
        Returns:
            Stop loss distance as decimal (0.02 = 2%).
        """
        if self.entry_price <= 0:
            return 0.0
        return self.stop_loss_distance / self.entry_price
    
    @property
    def risk_reward_ratio(self) -> Optional[float]:
        """
        Calculate risk/reward ratio if take profit is set.
        
        Returns:
            R:R ratio or None if no take profit.
        """
        if self.take_profit is None:
            return None
        
        stop_dist = self.stop_loss_distance
        if stop_dist <= 0:
            return None
        
        tp_distance = abs(self.take_profit - self.entry_price)
        return tp_distance / stop_dist
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate the trade request.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        errors = []
        
        if self.entry_price <= 0:
            errors.append("Entry price must be positive")
        
        if self.stop_loss <= 0:
            errors.append("Stop loss must be positive")
        
        if self.leverage < 1:
            errors.append("Leverage must be at least 1")
        
        # Validate stop loss direction
        if self.side == PositionSide.LONG:
            if self.stop_loss >= self.entry_price:
                errors.append("Long stop loss must be below entry price")
            if self.take_profit is not None and self.take_profit <= self.entry_price:
                errors.append("Long take profit must be above entry price")
        else:
            if self.stop_loss <= self.entry_price:
                errors.append("Short stop loss must be above entry price")
            if self.take_profit is not None and self.take_profit >= self.entry_price:
                errors.append("Short take profit must be below entry price")
        
        if errors:
            return False, "; ".join(errors)
        return True, ""
