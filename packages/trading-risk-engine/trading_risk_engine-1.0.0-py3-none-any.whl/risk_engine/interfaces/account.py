"""
Account - Abstraction for account balance and equity.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class Account(Protocol):
    """
    Protocol for account data abstraction.
    
    Implementations should provide real-time account data
    from the exchange or broker.
    """
    
    def get_balance(self) -> float:
        """
        Get the total account balance (without unrealized P&L).
        
        Returns:
            Total balance in quote currency.
        """
        ...
    
    def get_equity(self) -> float:
        """
        Get the current account equity (balance + unrealized P&L).
        
        Returns:
            Current equity in quote currency.
        """
        ...
    
    def get_available_margin(self) -> float:
        """
        Get available margin for new trades.
        
        Returns:
            Available margin in quote currency.
        """
        ...
    
    def get_used_margin(self) -> float:
        """
        Get currently used margin.
        
        Returns:
            Used margin in quote currency.
        """
        ...


@dataclass
class SimpleAccount:
    """
    Simple account implementation for testing and basic usage.
    
    Attributes:
        balance: Total account balance.
        unrealized_pnl: Current unrealized profit/loss.
        used_margin: Currently used margin.
    """
    
    balance: float
    unrealized_pnl: float = 0.0
    used_margin: float = 0.0
    
    def get_balance(self) -> float:
        """Get total balance."""
        return self.balance
    
    def get_equity(self) -> float:
        """Get equity (balance + unrealized P&L)."""
        return self.balance + self.unrealized_pnl
    
    def get_available_margin(self) -> float:
        """Get available margin."""
        return max(0, self.get_equity() - self.used_margin)
    
    def get_used_margin(self) -> float:
        """Get used margin."""
        return self.used_margin
    
    def update(
        self,
        balance: float = None,
        unrealized_pnl: float = None,
        used_margin: float = None,
    ) -> None:
        """Update account values."""
        if balance is not None:
            self.balance = balance
        if unrealized_pnl is not None:
            self.unrealized_pnl = unrealized_pnl
        if used_margin is not None:
            self.used_margin = used_margin
