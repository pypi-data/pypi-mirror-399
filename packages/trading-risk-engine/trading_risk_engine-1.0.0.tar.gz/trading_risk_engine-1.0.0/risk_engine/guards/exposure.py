"""
ExposureGuard - Controls position count and exposure limits.

Prevents over-concentration and limits concurrent positions.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from .drawdown import GuardResult

if TYPE_CHECKING:
    from ..core.config import RiskConfig
    from ..core.state import RiskState
    from ..interfaces.position import Position


class ExposureGuard:
    """
    Monitors and limits exposure across positions.
    
    Key behaviors:
    1. Limits number of concurrent open positions
    2. Tracks exposure per symbol (future enhancement)
    3. Monitors concentration risk
    
    Usage:
        guard = ExposureGuard(config, state)
        result = guard.check()
        if result.triggered:
            reject_trade()
    """
    
    def __init__(self, config: "RiskConfig", state: "RiskState") -> None:
        """
        Initialize exposure guard.
        
        Args:
            config: Risk configuration with exposure limits.
            state: Runtime state with position tracking.
        """
        self.config = config
        self.state = state
    
    def check(self) -> GuardResult:
        """
        Check if position limits allow a new trade.
        
        Returns:
            GuardResult indicating if limit is reached.
        """
        current = self.state.open_positions
        maximum = self.config.max_open_positions
        
        if current >= maximum:
            return GuardResult(
                triggered=True,
                reason=(
                    f"Position limit reached: {current}/{maximum} positions open"
                ),
                value=float(current),
                limit=float(maximum),
            )
        
        return GuardResult(
            triggered=False,
            reason=f"Position count {current}/{maximum} within limit",
            value=float(current),
            limit=float(maximum),
        )
    
    def can_open_positions(self, count: int = 1) -> bool:
        """
        Check if N new positions can be opened.
        
        Args:
            count: Number of positions to open.
            
        Returns:
            True if there's room for N more positions.
        """
        return (self.state.open_positions + count) <= self.config.max_open_positions
    
    def get_available_slots(self) -> int:
        """
        Get number of available position slots.
        
        Returns:
            Number of positions that can still be opened.
        """
        return max(0, self.config.max_open_positions - self.state.open_positions)
    
    def check_concentration(
        self,
        positions: List["Position"],
        new_symbol: str,
        max_per_symbol: int = 1,
    ) -> GuardResult:
        """
        Check concentration risk for a symbol.
        
        Args:
            positions: List of current positions.
            new_symbol: Symbol for the new trade.
            max_per_symbol: Maximum positions per symbol.
            
        Returns:
            GuardResult indicating if concentration is too high.
        """
        symbol_count = sum(1 for p in positions if p.symbol == new_symbol)
        
        if symbol_count >= max_per_symbol:
            return GuardResult(
                triggered=True,
                reason=(
                    f"Concentration limit: {symbol_count} positions "
                    f"already open for {new_symbol}"
                ),
                value=float(symbol_count),
                limit=float(max_per_symbol),
            )
        
        return GuardResult(
            triggered=False,
            reason=f"Symbol concentration {symbol_count}/{max_per_symbol} OK",
            value=float(symbol_count),
            limit=float(max_per_symbol),
        )
    
    def check_notional_exposure(
        self,
        positions: List["Position"],
        equity: float,
        max_exposure: float = 3.0,
    ) -> GuardResult:
        """
        Check total notional exposure as multiple of equity.
        
        Args:
            positions: List of current positions.
            equity: Current account equity.
            max_exposure: Maximum total exposure as equity multiple.
            
        Returns:
            GuardResult indicating if exposure is too high.
        """
        if equity <= 0:
            return GuardResult(
                triggered=True,
                reason="Cannot check exposure: equity is zero or negative",
                value=0.0,
                limit=max_exposure,
            )
        
        total_notional = sum(p.notional_value for p in positions)
        exposure_ratio = total_notional / equity
        
        if exposure_ratio >= max_exposure:
            return GuardResult(
                triggered=True,
                reason=(
                    f"Total exposure {exposure_ratio:.2f}x exceeds "
                    f"limit {max_exposure:.2f}x"
                ),
                value=exposure_ratio,
                limit=max_exposure,
            )
        
        return GuardResult(
            triggered=False,
            reason=f"Total exposure {exposure_ratio:.2f}x within limit",
            value=exposure_ratio,
            limit=max_exposure,
        )
    
    def __str__(self) -> str:
        """Human-readable status."""
        result = self.check()
        status = "⚠️ AT LIMIT" if result.triggered else "✓ OK"
        return (
            f"ExposureGuard:\n"
            f"  Positions: {int(result.value)}/{int(result.limit)} [{status}]\n"
            f"  Available slots: {self.get_available_slots()}"
        )
