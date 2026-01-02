"""
RiskConfig - User-defined risk limits and parameters.

All values are explicit numbers. No heuristics, no magic.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class RiskConfig:
    """
    Immutable configuration for risk management.
    
    All percentages are expressed as decimals (0.15 = 15%).
    
    Attributes:
        max_account_drawdown: Maximum allowed account drawdown before kill switch.
                              Example: 0.15 means 15% max drawdown.
        risk_per_trade: Maximum risk per individual trade.
                        Example: 0.01 means 1% of equity risked per trade.
        max_leverage: Maximum allowed effective leverage.
                      Example: 3.0 means 3x leverage maximum.
        max_open_positions: Maximum number of concurrent open positions.
        session_drawdown: Maximum drawdown allowed per trading session.
                          Example: 0.05 means 5% session drawdown limit.
        min_position_size: Minimum position size (prevents dust trades).
        max_position_size: Maximum position size as fraction of equity.
    """
    
    # Primary limits
    max_account_drawdown: float = 0.15
    risk_per_trade: float = 0.01
    max_leverage: float = 3.0
    max_open_positions: int = 3
    session_drawdown: float = 0.05
    
    # Position size constraints
    min_position_size: float = 0.0001
    max_position_size: float = 0.25  # 25% of equity max
    
    def __post_init__(self) -> None:
        """Validate configuration values."""
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate all configuration parameters.
        
        Raises:
            ValueError: If any parameter is invalid.
        """
        errors = []
        
        # Drawdown checks
        if not 0 < self.max_account_drawdown <= 1:
            errors.append(
                f"max_account_drawdown must be between 0 and 1, got {self.max_account_drawdown}"
            )
        
        if not 0 < self.session_drawdown <= 1:
            errors.append(
                f"session_drawdown must be between 0 and 1, got {self.session_drawdown}"
            )
        
        if self.session_drawdown > self.max_account_drawdown:
            errors.append(
                f"session_drawdown ({self.session_drawdown}) cannot exceed "
                f"max_account_drawdown ({self.max_account_drawdown})"
            )
        
        # Risk per trade check
        if not 0 < self.risk_per_trade <= 0.1:
            errors.append(
                f"risk_per_trade must be between 0 and 0.1 (10%), got {self.risk_per_trade}"
            )
        
        # Leverage check
        if not 0 < self.max_leverage <= 125:
            errors.append(
                f"max_leverage must be between 0 and 125, got {self.max_leverage}"
            )
        
        # Position limits
        if self.max_open_positions < 1:
            errors.append(
                f"max_open_positions must be at least 1, got {self.max_open_positions}"
            )
        
        if self.min_position_size < 0:
            errors.append(
                f"min_position_size cannot be negative, got {self.min_position_size}"
            )
        
        if not 0 < self.max_position_size <= 1:
            errors.append(
                f"max_position_size must be between 0 and 1, got {self.max_position_size}"
            )
        
        if errors:
            raise ValueError("Invalid RiskConfig:\n" + "\n".join(f"  - {e}" for e in errors))
    
    def with_updates(self, **kwargs) -> "RiskConfig":
        """
        Create a new config with updated values.
        
        Args:
            **kwargs: Configuration parameters to update.
            
        Returns:
            New RiskConfig with updated values.
        """
        current = {
            "max_account_drawdown": self.max_account_drawdown,
            "risk_per_trade": self.risk_per_trade,
            "max_leverage": self.max_leverage,
            "max_open_positions": self.max_open_positions,
            "session_drawdown": self.session_drawdown,
            "min_position_size": self.min_position_size,
            "max_position_size": self.max_position_size,
        }
        current.update(kwargs)
        return RiskConfig(**current)


# Preset configurations for common use cases
CONSERVATIVE_CONFIG = RiskConfig(
    max_account_drawdown=0.10,
    risk_per_trade=0.005,
    max_leverage=2.0,
    max_open_positions=2,
    session_drawdown=0.03,
)

MODERATE_CONFIG = RiskConfig(
    max_account_drawdown=0.15,
    risk_per_trade=0.01,
    max_leverage=3.0,
    max_open_positions=3,
    session_drawdown=0.05,
)

AGGRESSIVE_CONFIG = RiskConfig(
    max_account_drawdown=0.25,
    risk_per_trade=0.02,
    max_leverage=5.0,
    max_open_positions=5,
    session_drawdown=0.10,
)
