"""
FixedRiskSizer - Fixed percentage risk per trade.

The classic position sizing formula:
position_size = (equity * risk_percent) / stop_loss_distance

This ensures each trade risks a fixed percentage of account equity.
No surprises.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.config import RiskConfig


@dataclass(frozen=True)
class SizingResult:
    """
    Result of position size calculation.
    
    Attributes:
        position_size: Calculated position size (0 if invalid).
        risk_amount: Absolute risk amount in quote currency.
        reason: Explanation of the calculation.
    """
    position_size: float
    risk_amount: float
    reason: str
    
    @property
    def is_valid(self) -> bool:
        """Check if calculated size is valid for trading."""
        return self.position_size > 0


class FixedRiskSizer:
    """
    Fixed percentage risk position sizing.
    
    Formula:
        position_size = (equity * risk_per_trade) / stop_loss_distance
    
    Where:
        - risk_per_trade is from config (e.g., 0.01 = 1%)
        - stop_loss_distance is entry_price - stop_loss_price
    
    This ensures that IF the stop loss is hit, the loss equals
    exactly the configured risk percentage.
    
    Example:
        - Equity: $10,000
        - Risk per trade: 1% = $100
        - Entry: $50,000
        - Stop loss: $49,000
        - Stop distance: $1,000
        
        Position size = $100 / $1,000 = 0.1 BTC
        If BTC drops to $49,000: loss = 0.1 * $1,000 = $100 = 1%
    
    Usage:
        sizer = FixedRiskSizer(config)
        result = sizer.calculate(equity=10000, entry_price=50000, stop_loss_price=49000)
        if result.is_valid:
            execute_trade(result.position_size)
    """
    
    def __init__(self, config: "RiskConfig") -> None:
        """
        Initialize fixed risk sizer.
        
        Args:
            config: Risk configuration with risk_per_trade setting.
        """
        self.config = config
    
    def calculate(
        self,
        equity: float,
        entry_price: float,
        stop_loss_price: float,
    ) -> SizingResult:
        """
        Calculate position size based on fixed risk.
        
        Args:
            equity: Current account equity.
            entry_price: Expected entry price.
            stop_loss_price: Stop loss price.
            
        Returns:
            SizingResult with calculated position size.
        """
        # Validate inputs
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
        
        if stop_loss_price <= 0:
            return SizingResult(
                position_size=0.0,
                risk_amount=0.0,
                reason="Invalid stop loss price: must be positive",
            )
        
        # Calculate stop loss distance
        stop_loss_distance = abs(entry_price - stop_loss_price)
        
        if stop_loss_distance == 0:
            return SizingResult(
                position_size=0.0,
                risk_amount=0.0,
                reason="Invalid stop loss: same as entry price",
            )
        
        # Calculate risk amount
        risk_amount = equity * self.config.risk_per_trade
        
        # Calculate position size
        # position_size = risk_amount / stop_loss_distance
        position_size = risk_amount / stop_loss_distance
        
        # Apply position size limits
        min_size = self.config.min_position_size
        max_size = (equity * self.config.max_position_size) / entry_price
        
        if position_size < min_size:
            return SizingResult(
                position_size=0.0,
                risk_amount=risk_amount,
                reason=f"Calculated size {position_size:.8f} below minimum {min_size}",
            )
        
        if position_size > max_size:
            # Cap at maximum, recalculate risk
            capped_risk = max_size * stop_loss_distance
            return SizingResult(
                position_size=max_size,
                risk_amount=capped_risk,
                reason=f"Size capped at maximum: {max_size:.8f} (risk: {capped_risk:.2f})",
            )
        
        return SizingResult(
            position_size=position_size,
            risk_amount=risk_amount,
            reason=f"Size calculated: {position_size:.8f} (risk: {risk_amount:.2f})",
        )
    
    def calculate_from_percent(
        self,
        equity: float,
        entry_price: float,
        stop_loss_percent: float,
    ) -> SizingResult:
        """
        Calculate position size from percentage stop loss.
        
        Args:
            equity: Current account equity.
            entry_price: Expected entry price.
            stop_loss_percent: Stop loss as percentage (0.02 = 2% from entry).
            
        Returns:
            SizingResult with calculated position size.
        """
        stop_loss_price = entry_price * (1 - stop_loss_percent)
        return self.calculate(equity, entry_price, stop_loss_price)
    
    def reverse_calculate_stop_loss(
        self,
        equity: float,
        entry_price: float,
        position_size: float,
    ) -> float:
        """
        Calculate required stop loss distance for a given position size.
        
        Useful for validating trades or determining where stop should be.
        
        Args:
            equity: Current account equity.
            entry_price: Entry price.
            position_size: Desired position size.
            
        Returns:
            Required stop loss distance (absolute value).
        """
        if position_size <= 0:
            return 0.0
        
        risk_amount = equity * self.config.risk_per_trade
        return risk_amount / position_size
    
    def get_risk_summary(
        self,
        equity: float,
        entry_price: float,
        stop_loss_price: float,
    ) -> dict:
        """
        Get detailed risk calculation summary.
        
        Args:
            equity: Current account equity.
            entry_price: Entry price.
            stop_loss_price: Stop loss price.
            
        Returns:
            Dictionary with calculation details.
        """
        result = self.calculate(equity, entry_price, stop_loss_price)
        stop_distance = abs(entry_price - stop_loss_price)
        stop_percent = stop_distance / entry_price if entry_price > 0 else 0
        
        return {
            "equity": equity,
            "risk_per_trade": self.config.risk_per_trade,
            "risk_amount": result.risk_amount,
            "entry_price": entry_price,
            "stop_loss_price": stop_loss_price,
            "stop_distance": stop_distance,
            "stop_percent": stop_percent,
            "position_size": result.position_size,
            "notional_value": result.position_size * entry_price if result.is_valid else 0,
            "is_valid": result.is_valid,
            "reason": result.reason,
        }
    
    def __str__(self) -> str:
        """Human-readable configuration."""
        return f"FixedRiskSizer(risk_per_trade={self.config.risk_per_trade:.2%})"
