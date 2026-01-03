# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Input/output utilities for network data.
"""

from pathlib import Path
from typing import Optional, Union

import networkx as nx
import pandas as pd

from krl_network.core.exceptions import DataError


def load_network(
    filepath: Union[str, Path],
    format: Optional[str] = None,
    **kwargs,
) -> nx.Graph:
    """
    Load network from file.

    Args:
        filepath: Path to network file
        format: File format ('graphml', 'gexf', 'gml', 'edgelist', 'adjlist')
                If None, inferred from file extension
        **kwargs: Additional arguments passed to NetworkX loader

    Returns:
        NetworkX graph

    Raises:
        DataError: If file format is unsupported or file cannot be read
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise DataError(f"File not found: {filepath}")

    # Infer format from extension if not provided
    if format is None:
        format = filepath.suffix.lower().lstrip(".")

    try:
        if format == "graphml":
            return nx.read_graphml(filepath, **kwargs)
        elif format == "gexf":
            return nx.read_gexf(filepath, **kwargs)
        elif format == "gml":
            return nx.read_gml(filepath, **kwargs)
        elif format == "edgelist":
            return nx.read_edgelist(filepath, **kwargs)
        elif format == "adjlist":
            return nx.read_adjlist(filepath, **kwargs)
        elif format == "json":
            return nx.node_link_graph(nx.read_json(filepath))
        elif format in ["csv", "xlsx", "xls"]:
            # Load as DataFrame and convert to network
            if format == "csv":
                df = pd.read_csv(filepath, **kwargs)
            else:
                df = pd.read_excel(filepath, **kwargs)

            # Assume first two columns are source and target
            if len(df.columns) < 2:
                raise DataError("CSV/Excel must have at least 2 columns (source, target)")

            source_col = df.columns[0]
            target_col = df.columns[1]
            weight_col = df.columns[2] if len(df.columns) > 2 else None

            return _dataframe_to_graph(df, source_col, target_col, weight_col)
        else:
            raise DataError(f"Unsupported format: {format}")
    except Exception as e:
        raise DataError(f"Failed to load network from {filepath}: {e}")


def export_network(
    graph: nx.Graph,
    filepath: Union[str, Path],
    format: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Export network to file.

    Args:
        graph: NetworkX graph
        filepath: Output file path
        format: File format ('graphml', 'gexf', 'gml', 'edgelist', 'adjlist')
                If None, inferred from file extension
        **kwargs: Additional arguments passed to NetworkX writer

    Raises:
        DataError: If file format is unsupported or write fails
    """
    filepath = Path(filepath)

    # Create parent directory if it doesn't exist
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Infer format from extension if not provided
    if format is None:
        format = filepath.suffix.lower().lstrip(".")

    try:
        if format == "graphml":
            nx.write_graphml(graph, filepath, **kwargs)
        elif format == "gexf":
            nx.write_gexf(graph, filepath, **kwargs)
        elif format == "gml":
            nx.write_gml(graph, filepath, **kwargs)
        elif format == "edgelist":
            nx.write_edgelist(graph, filepath, **kwargs)
        elif format == "adjlist":
            nx.write_adjlist(graph, filepath, **kwargs)
        elif format == "json":
            nx.write_json(graph, filepath)
        elif format == "csv":
            # Convert to DataFrame and save
            edges_data = []
            for source, target, data in graph.edges(data=True):
                edge_dict = {"source": source, "target": target}
                edge_dict.update(data)
                edges_data.append(edge_dict)
            df = pd.DataFrame(edges_data)
            df.to_csv(filepath, index=False, **kwargs)
        else:
            raise DataError(f"Unsupported format: {format}")
    except Exception as e:
        raise DataError(f"Failed to export network to {filepath}: {e}")


def _dataframe_to_graph(
    df: pd.DataFrame,
    source_col: str,
    target_col: str,
    weight_col: Optional[str] = None,
) -> nx.Graph:
    """Convert DataFrame to NetworkX graph."""
    # Create graph
    G = nx.DiGraph() if "directed" in df.columns else nx.Graph()

    # Add edges
    for _, row in df.iterrows():
        source = row[source_col]
        target = row[target_col]

        attrs = {}
        if weight_col and weight_col in df.columns:
            attrs["weight"] = row[weight_col]

        # Add other columns as edge attributes
        for col in df.columns:
            if col not in [source_col, target_col, weight_col]:
                attrs[col] = row[col]

        G.add_edge(source, target, **attrs)

    return G
