"""Adapters module - Framework integrations."""

from .generic import GenericAdapter
from .freqtrade import FreqtradeRiskAdapter

__all__ = ["GenericAdapter", "FreqtradeRiskAdapter"]
