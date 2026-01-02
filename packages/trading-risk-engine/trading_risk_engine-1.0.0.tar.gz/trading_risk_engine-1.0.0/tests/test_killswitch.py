"""
Tests for Kill Switch and Overall Engine Behavior
"""

import pytest
from risk_engine.core.config import RiskConfig
from risk_engine.core.state import RiskState
from risk_engine.core.engine import RiskEngine, DecisionType
from risk_engine.interfaces.position import TradeRequest, PositionSide


class TestKillSwitchIntegration:
    """Test kill switch integration in engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(
            max_account_drawdown=0.10,  # 10% max DD
            risk_per_trade=0.01,
            max_leverage=3.0,
            max_open_positions=2,
        )
    
    def test_trading_blocked_when_disabled(self):
        """Trading should be blocked when kill switch active."""
        state = RiskState(
            current_equity=10000,
            equity_peak=10000,
            trading_enabled=False,
            kill_switch_reason="Test shutdown",
        )
        engine = RiskEngine(self.config, state)
        
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=50000,
            stop_loss=49000,
        )
        
        decision = engine.evaluate_trade(request)
        
        assert decision.decision == DecisionType.SHUTDOWN
        assert decision.guard_triggered == "kill_switch"
    
    def test_drawdown_triggers_shutdown(self):
        """Hitting drawdown limit should trigger shutdown."""
        state = RiskState(
            current_equity=8900,   # 11% drawdown
            equity_peak=10000,
        )
        engine = RiskEngine(self.config, state)
        
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=50000,
            stop_loss=49000,
        )
        
        decision = engine.evaluate_trade(request)
        
        assert decision.decision == DecisionType.SHUTDOWN
        assert decision.guard_triggered == "drawdown"
        assert not state.trading_enabled  # Kill switch should be activated
    
    def test_manual_reset_required(self):
        """After shutdown, manual reset should be required."""
        state = RiskState(
            current_equity=8900,
            equity_peak=10000,
        )
        engine = RiskEngine(self.config, state)
        
        # Trigger shutdown
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=50000,
            stop_loss=49000,
        )
        engine.evaluate_trade(request)
        
        # Even if equity improves, still blocked
        state.update_equity(9500)
        decision = engine.evaluate_trade(request)
        assert decision.decision == DecisionType.SHUTDOWN
        
        # Manual reset required
        engine.manual_reset()
        state.update_equity(10000)  # Reset peak
        
        decision = engine.evaluate_trade(request)
        assert decision.is_approved
    
    def test_emergency_shutdown(self):
        """Emergency shutdown should immediately block trading."""
        state = RiskState(current_equity=10000, equity_peak=10000)
        engine = RiskEngine(self.config, state)
        
        engine.emergency_shutdown("Market crash detected")
        
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=50000,
            stop_loss=49000,
        )
        
        decision = engine.evaluate_trade(request)
        
        assert decision.decision == DecisionType.SHUTDOWN
        assert "EMERGENCY" in state.kill_switch_reason


class TestFailClosed:
    """Test fail-closed behavior."""
    
    def test_error_results_in_rejection(self):
        """Any internal error should result in trade rejection."""
        config = RiskConfig()
        state = RiskState(current_equity=10000, equity_peak=10000)
        engine = RiskEngine(config, state)
        
        # Create a request that might cause calculation issues
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=-1,  # Invalid price
            stop_loss=49000,
        )
        
        # Should not raise, should return REJECT
        decision = engine.evaluate_trade(request)
        
        # Either rejected by validation or fail-closed
        assert decision.decision in [DecisionType.REJECT, DecisionType.SHUTDOWN]
        assert decision.position_size == 0.0


class TestEdgeCases:
    """Test edge cases in engine behavior."""
    
    def test_zero_equity(self):
        """Zero equity should block trading."""
        config = RiskConfig()
        state = RiskState(current_equity=0, equity_peak=10000)
        engine = RiskEngine(config, state)
        
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=50000,
            stop_loss=49000,
        )
        
        decision = engine.evaluate_trade(request)
        assert not decision.is_approved
    
    def test_position_limit_reached(self):
        """Should reject when at position limit."""
        config = RiskConfig(max_open_positions=2)
        state = RiskState(
            current_equity=10000,
            equity_peak=10000,
            open_positions=2,  # Already at limit
        )
        engine = RiskEngine(config, state)
        
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=50000,
            stop_loss=49000,
        )
        
        decision = engine.evaluate_trade(request)
        
        assert decision.decision == DecisionType.REJECT
        assert decision.guard_triggered == "exposure"
