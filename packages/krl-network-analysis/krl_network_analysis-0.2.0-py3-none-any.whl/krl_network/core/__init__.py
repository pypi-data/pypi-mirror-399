# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Core infrastructure for network analysis.

This module provides the foundational classes and utilities for building
and analyzing economic networks.
"""

from krl_network.core.base import BaseNetwork, NetworkConfig
from krl_network.core.exceptions import (
    ComputationError,
    DataError,
    InvalidNetworkError,
    NetworkError,
)
from krl_network.core.result import NetworkResult

__all__ = [
    "BaseNetwork",
    "NetworkConfig",
    "NetworkResult",
    "NetworkError",
    "InvalidNetworkError",
    "ComputationError",
    "DataError",
]
