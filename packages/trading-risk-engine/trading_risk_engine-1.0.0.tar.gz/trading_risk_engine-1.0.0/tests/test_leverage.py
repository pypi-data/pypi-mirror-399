"""
Tests for LeverageGuard
"""

import pytest
from risk_engine.core.config import RiskConfig
from risk_engine.guards.leverage import LeverageGuard


class TestLeverageGuard:
    """Test leverage guard checks."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(max_leverage=3.0)
        self.guard = LeverageGuard(self.config)
    
    def test_within_leverage_limit(self):
        """Leverage within limit should pass."""
        # Position notional: 1.0 * 50000 = 50,000
        # Equity: 20,000
        # Effective leverage: 2.5x
        
        result = self.guard.check(
            position_size=1.0,
            entry_price=50000,
            equity=20000,
        )
        
        assert not result.triggered
        assert result.value == pytest.approx(2.5, rel=0.01)
    
    def test_at_leverage_limit(self):
        """Leverage at exact limit should pass."""
        # Position notional: 60,000
        # Equity: 20,000
        # Effective leverage: 3.0x (at limit)
        
        result = self.guard.check(
            position_size=1.2,
            entry_price=50000,
            equity=20000,
        )
        
        assert not result.triggered
        assert result.value == 3.0
    
    def test_exceeds_leverage_limit(self):
        """Leverage exceeding limit should fail."""
        # Position notional: 80,000
        # Equity: 20,000
        # Effective leverage: 4.0x (exceeds 3.0x)
        
        result = self.guard.check(
            position_size=1.6,
            entry_price=50000,
            equity=20000,
        )
        
        assert result.triggered
        assert "exceeds" in result.reason.lower()
    
    def test_zero_equity(self):
        """Zero equity should trigger guard."""
        result = self.guard.check(
            position_size=1.0,
            entry_price=50000,
            equity=0,
        )
        
        assert result.triggered
    
    def test_max_position_calculation(self):
        """Calculate maximum position size."""
        # Max leverage: 3.0x
        # Equity: 20,000
        # Max notional: 60,000
        # Price: 50,000
        # Max size: 1.2
        
        max_size = self.guard.calculate_max_position_size(
            entry_price=50000,
            equity=20000,
        )
        
        assert max_size == pytest.approx(1.2, rel=0.01)


class TestLiquidationEstimation:
    """Test liquidation price estimation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(max_leverage=10.0)
        self.guard = LeverageGuard(self.config)
    
    def test_liquidation_price_long(self):
        """Estimate liquidation price for long position."""
        liq_price = self.guard.estimate_liquidation_price(
            entry_price=50000,
            leverage=10.0,
            is_long=True,
        )
        
        # At 10x, liquidation ~ 9.5% below entry
        assert liq_price < 50000
        assert liq_price > 45000
    
    def test_liquidation_price_short(self):
        """Estimate liquidation price for short position."""
        liq_price = self.guard.estimate_liquidation_price(
            entry_price=50000,
            leverage=10.0,
            is_long=False,
        )
        
        # At 10x, liquidation ~ 9.5% above entry
        assert liq_price > 50000
        assert liq_price < 55000
    
    def test_liquidation_distance(self):
        """Calculate distance to liquidation."""
        distance = self.guard.get_liquidation_distance(
            current_price=50000,
            liquidation_price=45000,
            is_long=True,
        )
        
        assert distance == pytest.approx(0.10, rel=0.01)  # 10% away
    
    def test_high_liquidation_risk(self):
        """Detect high liquidation risk."""
        # Long at 50000, liquidation at 48000
        # Current price 48500 = only 1% away from liquidation
        
        is_risky = self.guard.is_liquidation_risk_high(
            current_price=48500,
            liquidation_price=48000,
            is_long=True,
            threshold=0.10,
        )
        
        assert is_risky is True
