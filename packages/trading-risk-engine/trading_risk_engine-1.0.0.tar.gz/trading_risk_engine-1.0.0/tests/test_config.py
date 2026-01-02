"""
Tests for RiskConfig
"""

import pytest
from risk_engine.core.config import RiskConfig, CONSERVATIVE_CONFIG, MODERATE_CONFIG


class TestRiskConfigValidation:
    """Test configuration validation."""
    
    def test_default_config_valid(self):
        """Default config should be valid."""
        config = RiskConfig()
        assert config.max_account_drawdown == 0.15
        assert config.risk_per_trade == 0.01
        assert config.max_leverage == 3.0
        assert config.max_open_positions == 3
    
    def test_invalid_drawdown_too_high(self):
        """Drawdown > 1 should raise error."""
        with pytest.raises(ValueError, match="max_account_drawdown"):
            RiskConfig(max_account_drawdown=1.5)
    
    def test_invalid_drawdown_zero(self):
        """Drawdown = 0 should raise error."""
        with pytest.raises(ValueError, match="max_account_drawdown"):
            RiskConfig(max_account_drawdown=0)
    
    def test_invalid_risk_per_trade_too_high(self):
        """Risk > 10% should raise error."""
        with pytest.raises(ValueError, match="risk_per_trade"):
            RiskConfig(risk_per_trade=0.15)
    
    def test_invalid_session_exceeds_account(self):
        """Session drawdown > account drawdown should raise error."""
        with pytest.raises(ValueError, match="session_drawdown"):
            RiskConfig(max_account_drawdown=0.10, session_drawdown=0.15)
    
    def test_invalid_leverage_zero(self):
        """Leverage = 0 should raise error."""
        with pytest.raises(ValueError, match="max_leverage"):
            RiskConfig(max_leverage=0)
    
    def test_invalid_max_positions(self):
        """Max positions < 1 should raise error."""
        with pytest.raises(ValueError, match="max_open_positions"):
            RiskConfig(max_open_positions=0)
    
    def test_with_updates(self):
        """Test creating new config with updates."""
        config = RiskConfig()
        new_config = config.with_updates(risk_per_trade=0.02)
        
        assert config.risk_per_trade == 0.01  # Original unchanged
        assert new_config.risk_per_trade == 0.02  # New value applied
    
    def test_preset_configs(self):
        """Test preset configurations are valid."""
        assert CONSERVATIVE_CONFIG.max_account_drawdown == 0.10
        assert MODERATE_CONFIG.max_account_drawdown == 0.15


class TestRiskConfigImmutability:
    """Test that config is immutable."""
    
    def test_frozen_dataclass(self):
        """Config should be immutable."""
        config = RiskConfig()
        with pytest.raises(Exception):  # FrozenInstanceError
            config.max_account_drawdown = 0.5
