"""
Tests for DrawdownGuard and Kill Switch
"""

import pytest
from risk_engine.core.config import RiskConfig
from risk_engine.core.state import RiskState
from risk_engine.guards.drawdown import DrawdownGuard


class TestDrawdownCalculation:
    """Test drawdown calculation logic."""
    
    def test_no_drawdown_at_peak(self):
        """No drawdown when at equity peak."""
        state = RiskState(equity_peak=10000, current_equity=10000)
        assert state.current_drawdown == 0.0
    
    def test_drawdown_calculation(self):
        """Correct drawdown calculation."""
        state = RiskState(equity_peak=10000, current_equity=9000)
        assert state.current_drawdown == 0.10  # 10% drawdown
    
    def test_drawdown_at_new_high(self):
        """Drawdown is 0 when above peak."""
        state = RiskState(equity_peak=10000, current_equity=11000)
        assert state.current_drawdown == 0.0
    
    def test_equity_update_raises_peak(self):
        """New equity high should raise peak."""
        state = RiskState(equity_peak=10000, current_equity=10000)
        state.update_equity(11000)
        assert state.equity_peak == 11000
        assert state.current_drawdown == 0.0


class TestDrawdownGuard:
    """Test DrawdownGuard checks."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(
            max_account_drawdown=0.15,
            session_drawdown=0.05,
        )
    
    def test_guard_not_triggered_within_limit(self):
        """Guard should not trigger when within limits."""
        state = RiskState(equity_peak=10000, current_equity=9000)  # 10% DD
        guard = DrawdownGuard(self.config, state)
        
        result = guard.check()
        assert not result.triggered
        assert result.value == 0.10
        assert result.limit == 0.15
    
    def test_guard_triggered_at_limit(self):
        """Guard should trigger at exact limit."""
        state = RiskState(equity_peak=10000, current_equity=8500)  # 15% DD
        guard = DrawdownGuard(self.config, state)
        
        result = guard.check()
        assert result.triggered
        assert "KILL SWITCH" in result.reason
    
    def test_guard_triggered_beyond_limit(self):
        """Guard should trigger when beyond limit."""
        state = RiskState(equity_peak=10000, current_equity=8000)  # 20% DD
        guard = DrawdownGuard(self.config, state)
        
        result = guard.check()
        assert result.triggered
    
    def test_session_drawdown_check(self):
        """Session drawdown should work independently."""
        state = RiskState(
            equity_peak=10000,
            current_equity=9500,  # 5% DD (within account limit)
            session_loss=0.06,    # 6% session loss (exceeds limit)
        )
        guard = DrawdownGuard(self.config, state)
        
        # Account check should pass
        account_result = guard.check()
        assert not account_result.triggered
        
        # Session check should fail
        session_result = guard.check_session()
        assert session_result.triggered
    
    def test_remaining_drawdown(self):
        """Calculate remaining drawdown correctly."""
        state = RiskState(equity_peak=10000, current_equity=9000)  # 10% DD
        guard = DrawdownGuard(self.config, state)
        
        assert guard.get_remaining_drawdown() == pytest.approx(0.05, rel=0.01)
    
    def test_would_breach(self):
        """Test hypothetical breach check."""
        state = RiskState(equity_peak=10000, current_equity=9000)  # 10% DD
        guard = DrawdownGuard(self.config, state)
        
        # 5% more would trigger (10% + 5% = 15%)
        assert guard.would_breach(0.05) is True
        assert guard.would_breach(0.03) is False


class TestKillSwitch:
    """Test kill switch behavior."""
    
    def test_kill_switch_disabled_by_default(self):
        """Trading should be enabled by default."""
        state = RiskState()
        assert state.trading_enabled is True
        assert state.kill_switch_reason is None
    
    def test_disable_trading(self):
        """Disable trading with reason."""
        state = RiskState()
        state.disable_trading("Max drawdown exceeded")
        
        assert state.trading_enabled is False
        assert state.kill_switch_reason == "Max drawdown exceeded"
    
    def test_manual_enable(self):
        """Enable trading (manual reset)."""
        state = RiskState()
        state.disable_trading("Test")
        state.enable_trading()
        
        assert state.trading_enabled is True
        assert state.kill_switch_reason is None
    
    def test_is_trading_allowed(self):
        """Test is_trading_allowed property."""
        state = RiskState()
        assert state.is_trading_allowed is True
        
        state.disable_trading("Test")
        assert state.is_trading_allowed is False
