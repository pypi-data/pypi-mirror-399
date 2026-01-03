# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Result containers for network analysis.

This module now uses the centralized Pydantic-based NetworkResult from
krl-model-zoo-pro for consistency and automatic validation.
"""

from typing import Any, Dict, List, Optional, Union

import pandas as pd

# Import centralized Pydantic NetworkResult
try:
    from krl_models.core.results import NetworkResult
except ImportError:
    # Fallback for development/testing without krl-model-zoo-pro
    import warnings
    from dataclasses import dataclass, field

    warnings.warn(
        "krl-model-zoo-pro not installed. Using legacy dataclass NetworkResult. "
        "Install krl-model-zoo-pro for Pydantic validation: pip install krl-model-zoo-pro",
        ImportWarning,
    )

    @dataclass
    class NetworkResult:  # type: ignore[no-redef]
        """
        Legacy dataclass fallback for NetworkResult.

        This is only used when krl-model-zoo-pro is not installed.
        For production, install krl-model-zoo-pro to get the Pydantic version.
        """

        # BaseResult fields for compatibility
        model_name: str = "NetworkAnalysis"
        timestamp: Optional[str] = None
        metadata: Dict[str, Any] = field(default_factory=dict)

        # NetworkResult-specific fields
        metrics: Dict[str, Union[float, int, str]] = field(default_factory=dict)
        nodes: Optional[pd.DataFrame] = None
        edges: Optional[pd.DataFrame] = None
        communities: Optional[Dict[str, List[str]]] = None
        visualization_data: Optional[Dict[str, Any]] = None

        def __post_init__(self) -> None:
            """Set timestamp if not provided."""
            if self.timestamp is None:
                from datetime import datetime, UTC
                self.timestamp = datetime.now(UTC).isoformat()

        def to_dict(self) -> Dict[str, Any]:
            """Convert result to dictionary format."""
            return {
                "model_name": self.model_name,
                "timestamp": self.timestamp,
                "metadata": self.metadata,
                "metrics": self.metrics,
                "nodes": self.nodes.to_dict() if self.nodes is not None else None,
                "edges": self.edges.to_dict() if self.edges is not None else None,
                "communities": self.communities,
                "visualization_data": self.visualization_data,
            }

        def summary(self) -> str:
            """Generate a text summary of the results."""
            lines = ["Network Analysis Results", "=" * 40, ""]

            if self.metrics:
                lines.append("Metrics:")
                for key, value in self.metrics.items():
                    if isinstance(value, float):
                        lines.append(f"  {key}: {value:.4f}")
                    else:
                        lines.append(f"  {key}: {value}")
                lines.append("")

            if self.nodes is not None:
                lines.append(f"Nodes: {len(self.nodes)} total")
            if self.edges is not None:
                lines.append(f"Edges: {len(self.edges)} total")
            if self.communities:
                lines.append(f"Communities: {len(self.communities)} detected")

            return "\n".join(lines)


# Utility functions for backwards compatibility
def get_metric(result: NetworkResult, name: str, default: Any = None) -> Any:
    """Get a specific metric value from NetworkResult."""
    return result.metrics.get(name, default)


def add_metric(result: NetworkResult, name: str, value: Union[float, int, str]) -> None:
    """Add or update a metric in NetworkResult."""
    result.metrics[name] = value


def get_top_nodes(result: NetworkResult, metric: str, n: int = 10) -> pd.DataFrame:
    """
    Get top N nodes by a specific metric.

    Args:
        result: NetworkResult instance
        metric: Column name in nodes DataFrame
        n: Number of top nodes to return

    Returns:
        DataFrame of top nodes sorted by metric
    """
    if result.nodes is None or result.nodes.empty:
        return pd.DataFrame()

    if metric not in result.nodes.columns:
        raise KeyError(f"Metric '{metric}' not found in nodes")

    return result.nodes.nlargest(n, metric)


# Export the centralized NetworkResult
__all__ = ["NetworkResult", "get_metric", "add_metric", "get_top_nodes"]
