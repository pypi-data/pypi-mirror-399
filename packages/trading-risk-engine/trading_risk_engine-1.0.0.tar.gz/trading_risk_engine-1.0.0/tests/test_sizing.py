"""
Tests for Position Sizing
"""

import pytest
from risk_engine.core.config import RiskConfig
from risk_engine.sizing.fixed_risk import FixedRiskSizer


class TestFixedRiskSizing:
    """Test fixed risk position sizing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(
            risk_per_trade=0.01,  # 1% risk
            min_position_size=0.0001,
            max_position_size=0.25,
        )
        self.sizer = FixedRiskSizer(self.config)
    
    def test_basic_calculation(self):
        """Test basic position size calculation."""
        # Equity: $10,000
        # Risk: 1% = $100
        # Entry: $50,000
        # Stop: $49,000
        # Stop distance: $1,000
        # Expected size: $100 / $1,000 = 0.1
        
        result = self.sizer.calculate(
            equity=10000,
            entry_price=50000,
            stop_loss_price=49000,
        )
        
        assert result.is_valid
        # Note: max_position_size (25%) caps at (10000 * 0.25) / 50000 = 0.05
        # Uncapped would be (10000 * 0.01) / 1000 = 0.1, but capped to 0.05
        assert result.position_size == pytest.approx(0.05, rel=0.01)
        # When capped, risk_amount is recalculated: 0.05 * 1000 = 50
        assert result.risk_amount == pytest.approx(50.0, rel=0.01)
    
    def test_smaller_stop_larger_size(self):
        """Smaller stop distance = larger position (but capped)."""
        # Stop distance: $500
        # Uncapped size: $100 / $500 = 0.2
        # But max_position_size caps at 0.05
        
        result = self.sizer.calculate(
            equity=10000,
            entry_price=50000,
            stop_loss_price=49500,
        )
        
        # Capped at max_position_size
        assert result.position_size == pytest.approx(0.05, rel=0.01)
        assert "capped" in result.reason.lower()
    
    def test_larger_stop_smaller_size(self):
        """Larger stop distance = smaller position."""
        # Stop distance: $2,000
        # Expected size: $100 / $2,000 = 0.05
        
        result = self.sizer.calculate(
            equity=10000,
            entry_price=50000,
            stop_loss_price=48000,
        )
        
        assert result.position_size == pytest.approx(0.05, rel=0.01)
    
    def test_short_position(self):
        """Test short position sizing."""
        # Entry: $50,000
        # Stop: $51,000 (above for short)
        # Stop distance: $1,000
        # Uncapped: 0.1, but capped at 0.05
        
        result = self.sizer.calculate(
            equity=10000,
            entry_price=50000,
            stop_loss_price=51000,
        )
        
        assert result.is_valid
        assert result.position_size == pytest.approx(0.05, rel=0.01)
    
    def test_invalid_zero_equity(self):
        """Zero equity should return invalid result."""
        result = self.sizer.calculate(
            equity=0,
            entry_price=50000,
            stop_loss_price=49000,
        )
        
        assert not result.is_valid
        assert "equity" in result.reason.lower()
    
    def test_invalid_zero_stop_distance(self):
        """Stop = entry should return invalid result."""
        result = self.sizer.calculate(
            equity=10000,
            entry_price=50000,
            stop_loss_price=50000,
        )
        
        assert not result.is_valid
        assert "stop loss" in result.reason.lower()
    
    def test_min_position_size_enforced(self):
        """Position below minimum should be rejected."""
        # Very small equity = tiny position
        result = self.sizer.calculate(
            equity=1,  # $1 equity
            entry_price=50000,
            stop_loss_price=49000,
        )
        
        assert not result.is_valid
        assert "minimum" in result.reason.lower()
    
    def test_max_position_size_capped(self):
        """Position above maximum should be capped."""
        # Very small stop = very large position
        # Max position = 25% of equity / price
        
        result = self.sizer.calculate(
            equity=100000,
            entry_price=50000,
            stop_loss_price=49990,  # Tiny $10 stop
        )
        
        # Max size = (100000 * 0.25) / 50000 = 0.5
        assert result.is_valid
        assert result.position_size <= 0.5
        assert "capped" in result.reason.lower()
    
    def test_risk_stays_constant(self):
        """Verify risk amount calculation (note: actual risk may be capped)."""
        equity = 10000
        
        # Different stop distances - both may be capped
        result_tight = self.sizer.calculate(equity, 50000, 49500)
        result_wide = self.sizer.calculate(equity, 50000, 48000)
        
        # When capped, tight stop has higher effective risk per unit
        # When not capped, risk_amount = 100 for both
        # Here: tight is capped (0.2 -> 0.05), wide is not capped (0.05)
        assert result_wide.risk_amount == 100.0  # uncapped
        assert result_wide.position_size == 0.05


class TestRiskSummary:
    """Test risk calculation summary."""
    
    def test_summary_contains_all_fields(self):
        """Summary should have all expected fields."""
        config = RiskConfig(risk_per_trade=0.01)
        sizer = FixedRiskSizer(config)
        
        summary = sizer.get_risk_summary(
            equity=10000,
            entry_price=50000,
            stop_loss_price=49000,
        )
        
        assert "equity" in summary
        assert "risk_per_trade" in summary
        assert "risk_amount" in summary
        assert "stop_percent" in summary
        assert "position_size" in summary
        assert "notional_value" in summary
        assert summary["is_valid"] is True
