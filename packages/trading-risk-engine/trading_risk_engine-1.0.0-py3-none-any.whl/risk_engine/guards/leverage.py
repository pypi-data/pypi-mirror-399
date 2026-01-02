"""
LeverageGuard - Prevents excessive leverage and liquidation risk.

Calculates effective leverage and rejects trades that would
exceed the maximum allowed leverage.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .drawdown import GuardResult

if TYPE_CHECKING:
    from ..core.config import RiskConfig


class LeverageGuard:
    """
    Monitors and limits effective leverage.
    
    Key behaviors:
    1. Calculates effective leverage from position size and equity
    2. Estimates liquidation distance
    3. Rejects trades that exceed max_leverage
    
    Usage:
        guard = LeverageGuard(config)
        result = guard.check(position_size=1.0, entry_price=50000, equity=10000)
        if result.triggered:
            reject_trade()
    """
    
    def __init__(self, config: "RiskConfig") -> None:
        """
        Initialize leverage guard.
        
        Args:
            config: Risk configuration with leverage limits.
        """
        self.config = config
    
    def check(
        self,
        position_size: float,
        entry_price: float,
        equity: float,
    ) -> GuardResult:
        """
        Check if a position would exceed leverage limits.
        
        Args:
            position_size: Position size in base currency.
            entry_price: Entry price per unit.
            equity: Current account equity.
            
        Returns:
            GuardResult indicating if leverage is exceeded.
        """
        if equity <= 0:
            return GuardResult(
                triggered=True,
                reason="Cannot check leverage: equity is zero or negative",
                value=0.0,
                limit=self.config.max_leverage,
            )
        
        # Calculate notional value
        notional_value = abs(position_size) * entry_price
        
        # Calculate effective leverage
        effective_leverage = notional_value / equity
        
        if effective_leverage > self.config.max_leverage:
            return GuardResult(
                triggered=True,
                reason=(
                    f"Leverage {effective_leverage:.2f}x exceeds "
                    f"limit {self.config.max_leverage:.2f}x"
                ),
                value=effective_leverage,
                limit=self.config.max_leverage,
            )
        
        return GuardResult(
            triggered=False,
            reason=f"Leverage {effective_leverage:.2f}x within limit {self.config.max_leverage:.2f}x",
            value=effective_leverage,
            limit=self.config.max_leverage,
        )
    
    def calculate_max_position_size(
        self,
        entry_price: float,
        equity: float,
    ) -> float:
        """
        Calculate maximum position size for given leverage limit.
        
        Args:
            entry_price: Entry price per unit.
            equity: Current account equity.
            
        Returns:
            Maximum position size in base currency.
        """
        if entry_price <= 0:
            return 0.0
        
        max_notional = equity * self.config.max_leverage
        return max_notional / entry_price
    
    def estimate_liquidation_price(
        self,
        entry_price: float,
        leverage: float,
        is_long: bool,
        maintenance_margin: float = 0.005,
    ) -> float:
        """
        Estimate liquidation price for a leveraged position.
        
        Args:
            entry_price: Entry price.
            leverage: Applied leverage.
            is_long: True for long, False for short.
            maintenance_margin: Maintenance margin rate (default 0.5%).
            
        Returns:
            Estimated liquidation price.
        """
        # Simplified liquidation calculation
        # Liquidation occurs when losses exceed (1 / leverage) minus maintenance margin
        liquidation_threshold = (1 / leverage) - maintenance_margin
        
        if is_long:
            return entry_price * (1 - liquidation_threshold)
        else:
            return entry_price * (1 + liquidation_threshold)
    
    def get_liquidation_distance(
        self,
        current_price: float,
        liquidation_price: float,
        is_long: bool,
    ) -> float:
        """
        Calculate distance to liquidation as percentage.
        
        Args:
            current_price: Current market price.
            liquidation_price: Liquidation price.
            is_long: True for long, False for short.
            
        Returns:
            Distance to liquidation as decimal (0.1 = 10% away).
        """
        if current_price <= 0:
            return 0.0
        
        if is_long:
            distance = (current_price - liquidation_price) / current_price
        else:
            distance = (liquidation_price - current_price) / current_price
        
        return max(0, distance)
    
    def is_liquidation_risk_high(
        self,
        current_price: float,
        liquidation_price: float,
        is_long: bool,
        threshold: float = 0.10,
    ) -> bool:
        """
        Check if liquidation risk is dangerously high.
        
        Args:
            current_price: Current market price.
            liquidation_price: Liquidation price.
            is_long: True for long, False for short.
            threshold: Distance threshold (default 10%).
            
        Returns:
            True if liquidation is within threshold distance.
        """
        distance = self.get_liquidation_distance(current_price, liquidation_price, is_long)
        return distance < threshold
    
    def __str__(self) -> str:
        """Human-readable status."""
        return f"LeverageGuard(max_leverage={self.config.max_leverage}x)"
