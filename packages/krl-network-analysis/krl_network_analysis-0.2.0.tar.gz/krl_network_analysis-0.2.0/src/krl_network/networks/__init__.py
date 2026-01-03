"""
Economic network implementations.

This module contains domain-specific network classes for economic analysis:
- SupplyChainNetwork: Supply chain analysis and risk assessment
- RegionalNetwork: Regional economic integration and spillovers
- InputOutputNetwork: Input-output analysis and multipliers
- TradeNetwork: International trade and comparative advantage
"""

from krl_network.networks.input_output import InputOutputNetwork
from krl_network.networks.regional import RegionalNetwork
from krl_network.networks.supply_chain import SupplyChainNetwork
from krl_network.networks.trade import TradeNetwork

__all__ = [
    "SupplyChainNetwork",
    "RegionalNetwork",
    "InputOutputNetwork",
    "TradeNetwork",
]
