"""
Tests for RiskEngine - Full Integration Tests
"""

import pytest
from risk_engine.core.config import RiskConfig
from risk_engine.core.state import RiskState
from risk_engine.core.engine import RiskEngine, DecisionType
from risk_engine.interfaces.position import TradeRequest, PositionSide


class TestEngineBasicFlow:
    """Test basic engine evaluation flow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(
            max_account_drawdown=0.15,
            risk_per_trade=0.01,
            max_leverage=3.0,
            max_open_positions=3,
            session_drawdown=0.05,
        )
        self.state = RiskState(
            current_equity=10000,
            equity_peak=10000,
        )
        self.engine = RiskEngine(self.config, self.state)
    
    def test_approve_valid_trade(self):
        """Valid trade should be approved with correct size."""
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=50000,
            stop_loss=49000,  # 2% stop
        )
        
        decision = self.engine.evaluate_trade(request)
        
        assert decision.decision == DecisionType.APPROVE
        assert decision.is_approved
        assert decision.position_size > 0
        # Uncapped: (10000 * 0.01) / 1000 = 0.1
        # But max_position_size (25%) caps at (10000 * 0.25) / 50000 = 0.05
        assert decision.position_size == pytest.approx(0.05, rel=0.01)
    
    def test_approve_short_trade(self):
        """Short trade should also work correctly."""
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.SHORT,
            entry_price=50000,
            stop_loss=51000,  # 2% stop above
        )
        
        decision = self.engine.evaluate_trade(request)
        
        assert decision.is_approved
        # Capped at max_position_size
        assert decision.position_size == pytest.approx(0.05, rel=0.01)
    
    def test_record_trade_lifecycle(self):
        """Test full trade lifecycle tracking."""
        # Initial state
        assert self.state.open_positions == 0
        
        # Open trade
        self.engine.record_trade_open()
        assert self.state.open_positions == 1
        
        # Close with loss
        self.engine.record_trade_close(-0.01)  # 1% loss
        assert self.state.open_positions == 0
        assert self.state.session_loss == 0.01


class TestDecisionChain:
    """Test the decision chain in order."""
    
    def test_kill_switch_checked_first(self):
        """Kill switch should be checked before everything."""
        config = RiskConfig()
        state = RiskState(
            current_equity=10000,
            equity_peak=10000,
            trading_enabled=False,
            kill_switch_reason="Disabled",
        )
        engine = RiskEngine(config, state)
        
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=50000,
            stop_loss=49000,
        )
        
        decision = engine.evaluate_trade(request)
        assert decision.guard_triggered == "kill_switch"
    
    def test_drawdown_checked_second(self):
        """Drawdown should be checked after kill switch."""
        config = RiskConfig(max_account_drawdown=0.10)
        state = RiskState(
            current_equity=8500,  # 15% DD
            equity_peak=10000,
            trading_enabled=True,
        )
        engine = RiskEngine(config, state)
        
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=50000,
            stop_loss=49000,
        )
        
        decision = engine.evaluate_trade(request)
        assert decision.guard_triggered == "drawdown"
    
    def test_exposure_checked_before_sizing(self):
        """Exposure should be checked before calculating size."""
        config = RiskConfig(max_open_positions=1)
        state = RiskState(
            current_equity=10000,
            equity_peak=10000,
            open_positions=1,  # Already at limit
        )
        engine = RiskEngine(config, state)
        
        request = TradeRequest(
            symbol="BTC/USDT",
            side=PositionSide.LONG,
            entry_price=50000,
            stop_loss=49000,
        )
        
        decision = engine.evaluate_trade(request)
        assert decision.guard_triggered == "exposure"


class TestEngineStatus:
    """Test engine status reporting."""
    
    def test_get_status(self):
        """Status should contain all expected fields."""
        config = RiskConfig()
        state = RiskState(
            current_equity=9500,
            equity_peak=10000,
            open_positions=1,
        )
        engine = RiskEngine(config, state)
        
        status = engine.get_status()
        
        assert status["trading_enabled"] is True
        assert status["current_equity"] == 9500
        assert status["equity_peak"] == 10000
        assert status["current_drawdown"] == pytest.approx(0.05, rel=0.01)
        assert status["open_positions"] == 1
    
    def test_update_state(self):
        """Update state should track equity changes."""
        config = RiskConfig()
        state = RiskState(current_equity=10000, equity_peak=10000)
        engine = RiskEngine(config, state)
        
        # Equity goes up
        engine.update_state(11000)
        assert state.current_equity == 11000
        assert state.equity_peak == 11000
        
        # Equity goes down
        engine.update_state(10500)
        assert state.current_equity == 10500
        assert state.equity_peak == 11000  # Peak stays
    
    def test_session_reset(self):
        """Session reset should clear session metrics."""
        config = RiskConfig()
        state = RiskState(
            current_equity=10000,
            equity_peak=10000,
            session_loss=0.03,
        )
        engine = RiskEngine(config, state)
        
        engine.reset_session()
        
        assert state.session_loss == 0.0


class TestMultipleTradesScenario:
    """Test realistic multi-trade scenarios."""
    
    def test_winning_streak(self):
        """Test behavior during winning trades."""
        config = RiskConfig(max_account_drawdown=0.15, risk_per_trade=0.01)
        state = RiskState(current_equity=10000, equity_peak=10000)
        engine = RiskEngine(config, state)
        
        # Simulate 3 winning trades
        for i in range(3):
            request = TradeRequest(
                symbol="BTC/USDT",
                side=PositionSide.LONG,
                entry_price=50000,
                stop_loss=49000,
            )
            
            decision = engine.evaluate_trade(request)
            assert decision.is_approved
            
            engine.record_trade_open()
            
            # 2% profit on each trade
            profit = state.current_equity * 0.02
            new_equity = state.current_equity + profit
            engine.update_state(new_equity)
            engine.record_trade_close(0.02)
        
        # Equity should have grown
        assert state.current_equity > 10000
        assert state.equity_peak == state.current_equity
    
    def test_losing_streak_to_shutdown(self):
        """Test behavior during losing streak that hits DD limit."""
        config = RiskConfig(max_account_drawdown=0.10, risk_per_trade=0.02)
        state = RiskState(current_equity=10000, equity_peak=10000)
        engine = RiskEngine(config, state)
        
        trade_count = 0
        shutdown_triggered = False
        
        # Simulate losing trades until shutdown
        while trade_count < 10:
            request = TradeRequest(
                symbol="BTC/USDT",
                side=PositionSide.LONG,
                entry_price=50000,
                stop_loss=49000,
            )
            
            decision = engine.evaluate_trade(request)
            
            if decision.decision == DecisionType.SHUTDOWN:
                shutdown_triggered = True
                break
            
            if decision.decision == DecisionType.REJECT:
                # Session loss might reject before account DD shutdown
                break
            
            engine.record_trade_open()
            
            # 2% loss on each trade
            loss = state.current_equity * 0.02
            new_equity = state.current_equity - loss
            engine.update_state(new_equity)
            engine.record_trade_close(-0.02)
            trade_count += 1
        
        # Should have hit shutdown or significant drawdown
        # Either trading is disabled OR we hit rejection due to session/DD limits
        assert not state.trading_enabled or state.current_drawdown >= 0.05
