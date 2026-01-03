# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Validation utilities for network data.
"""

from typing import List, Optional

import networkx as nx
import pandas as pd

from krl_network.core.exceptions import DataError, InvalidNetworkError


def validate_network(
    graph: nx.Graph,
    allow_self_loops: bool = False,
    allow_negative_weights: bool = False,
    require_connected: bool = False,
) -> bool:
    """
    Validate network structure.

    Args:
        graph: NetworkX graph to validate
        allow_self_loops: Whether to allow self-loops
        allow_negative_weights: Whether to allow negative edge weights
        require_connected: Whether network must be connected

    Returns:
        True if network is valid

    Raises:
        InvalidNetworkError: If network structure is invalid
    """
    # Check for empty network
    if graph.number_of_nodes() == 0:
        raise InvalidNetworkError("Network has no nodes")

    # Check for self-loops
    if not allow_self_loops:
        self_loops = list(nx.selfloop_edges(graph))
        if self_loops:
            raise InvalidNetworkError(
                f"Network contains {len(self_loops)} self-loops but they are not allowed"
            )

    # Check for negative weights
    if not allow_negative_weights:
        for _, _, data in graph.edges(data=True):
            if "weight" in data and data["weight"] < 0:
                raise InvalidNetworkError("Network contains negative edge weights")

    # Check connectivity
    if require_connected:
        is_directed = isinstance(graph, nx.DiGraph)
        if is_directed:
            if not nx.is_weakly_connected(graph):
                raise InvalidNetworkError("Network is not weakly connected")
        else:
            if not nx.is_connected(graph):
                raise InvalidNetworkError("Network is not connected")

    return True


def validate_dataframe(
    df: pd.DataFrame,
    source_col: str,
    target_col: str,
    weight_col: Optional[str] = None,
    required_columns: Optional[List[str]] = None,
) -> bool:
    """
    Validate DataFrame for network construction.

    Args:
        df: DataFrame to validate
        source_col: Column name for source nodes
        target_col: Column name for target nodes
        weight_col: Column name for weights (optional)
        required_columns: Additional required columns

    Returns:
        True if DataFrame is valid

    Raises:
        DataError: If DataFrame is invalid
    """
    # Check if DataFrame is empty
    if df.empty:
        raise DataError("DataFrame is empty")

    # Check required columns exist
    missing_cols = []

    if source_col not in df.columns:
        missing_cols.append(source_col)
    if target_col not in df.columns:
        missing_cols.append(target_col)
    if weight_col and weight_col not in df.columns:
        missing_cols.append(weight_col)
    if required_columns:
        missing_cols.extend([col for col in required_columns if col not in df.columns])

    if missing_cols:
        raise DataError(f"DataFrame missing required columns: {missing_cols}")

    # Check for null values in key columns
    key_cols = [source_col, target_col]
    if weight_col:
        key_cols.append(weight_col)

    for col in key_cols:
        if df[col].isnull().any():
            null_count = df[col].isnull().sum()
            raise DataError(f"Column '{col}' contains {null_count} null values")

    # Check for valid weights
    if weight_col:
        if not pd.api.types.is_numeric_dtype(df[weight_col]):
            raise DataError(f"Weight column '{weight_col}' must be numeric")

        # Check for negative weights
        if (df[weight_col] < 0).any():
            negative_count = (df[weight_col] < 0).sum()
            raise DataError(
                f"Weight column '{weight_col}' contains {negative_count} negative values"
            )

    return True
