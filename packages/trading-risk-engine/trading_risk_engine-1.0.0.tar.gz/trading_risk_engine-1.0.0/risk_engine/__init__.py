"""
Risk Engine - A Strategy-Agnostic Risk Management System

This engine sits between trading strategies and execution layers,
providing independent risk controls including:
- Position Sizing
- Drawdown Monitoring  
- Kill Switch
- Leverage Guards

Core Principle: Fail Closed - Any error = prevent trading
"""

from .core.config import RiskConfig
from .core.state import RiskState
from .core.engine import RiskEngine, TradeDecision, DecisionType

__version__ = "1.0.0"
__all__ = [
    "RiskConfig",
    "RiskState", 
    "RiskEngine",
    "TradeDecision",
    "DecisionType",
]
