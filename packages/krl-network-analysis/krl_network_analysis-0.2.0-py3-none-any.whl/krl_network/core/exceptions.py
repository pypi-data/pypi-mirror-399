# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Custom exceptions for network analysis.
"""


class NetworkError(Exception):
    """Base exception for network analysis errors."""

    pass


class InvalidNetworkError(NetworkError):
    """Exception raised when network structure is invalid."""

    pass


class ComputationError(NetworkError):
    """Exception raised when network computation fails."""

    pass


class DataError(NetworkError):
    """Exception raised when input data is invalid or incompatible."""

    pass
