"""
Network topology analysis for spatial networks.

© 2025 KR-Labs. All rights reserved.

References
----------
Freeman, L. C. (1977). A set of measures of centrality based on betweenness.
    Sociometry, 40(1), 35-41.
Brandes, U. (2001). A faster algorithm for betweenness centrality.
    Journal of Mathematical Sociology, 25(2), 163-177.
"""

from typing import Dict, Optional, Union

import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix


def network_centrality(
    gdf, weights, measure: str = "betweenness", normalized: bool = True
) -> np.ndarray:
    """
    Compute network centrality measures for spatial network.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    measure : str, default='betweenness'
        Centrality measure: 'betweenness', 'closeness', 'degree', 'eigenvector'
    normalized : bool, default=True
        Whether to normalize centrality scores

    Returns
    -------
    centrality : ndarray
        Centrality scores for each node

    Examples
    --------
    >>> from krl_geospatial.network import network_centrality
    >>> from krl_geospatial.weights import KNNWeights
    >>>
    >>> w = KNNWeights(k=8)
    >>> w.fit(gdf)
    >>> centrality = network_centrality(gdf, w, measure='betweenness')
    """
    if measure == "betweenness":
        return betweenness_centrality(gdf, weights, normalized=normalized)
    elif measure == "closeness":
        return closeness_centrality(gdf, weights, normalized=normalized)
    elif measure == "degree":
        return degree_centrality(gdf, weights, normalized=normalized)
    elif measure == "eigenvector":
        return eigenvector_centrality(gdf, weights, normalized=normalized)
    else:
        raise ValueError(f"Unknown centrality measure: {measure}")


def betweenness_centrality(
    gdf, weights, normalized: bool = True, endpoints: bool = False
) -> np.ndarray:
    """
    Compute betweenness centrality for spatial network.

    Betweenness measures how often a node lies on shortest paths between
    other nodes.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    normalized : bool, default=True
        Normalize by (n-1)(n-2)/2
    endpoints : bool, default=False
        Include endpoints in path counts

    Returns
    -------
    betweenness : ndarray
        Betweenness centrality scores

    Examples
    --------
    >>> centrality = betweenness_centrality(gdf, w)
    """
    # Convert weights to NetworkX graph
    G = _weights_to_graph(weights)

    # Compute betweenness centrality
    bc = nx.betweenness_centrality(G, normalized=normalized, endpoints=endpoints)

    # Convert dict to array
    n = len(gdf)
    result = np.zeros(n)
    for i in range(n):
        result[i] = bc.get(i, 0.0)

    return result


def closeness_centrality(gdf, weights, normalized: bool = True) -> np.ndarray:
    """
    Compute closeness centrality for spatial network.

    Closeness measures how close a node is to all other nodes
    (inverse of average shortest path length).

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    normalized : bool, default=True
        Normalize by (n-1)

    Returns
    -------
    closeness : ndarray
        Closeness centrality scores

    Examples
    --------
    >>> centrality = closeness_centrality(gdf, w)
    """
    G = _weights_to_graph(weights)

    # Compute closeness centrality
    cc = nx.closeness_centrality(G, distance="weight")

    n = len(gdf)
    result = np.zeros(n)
    for i in range(n):
        result[i] = cc.get(i, 0.0)

    if not normalized:
        result = result * (n - 1)

    return result


def degree_centrality(gdf, weights, normalized: bool = True) -> np.ndarray:
    """
    Compute degree centrality for spatial network.

    Degree centrality is simply the number of neighbors.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    normalized : bool, default=True
        Normalize by (n-1)

    Returns
    -------
    degree : ndarray
        Degree centrality scores

    Examples
    --------
    >>> centrality = degree_centrality(gdf, w)
    """
    G = _weights_to_graph(weights)

    # Compute degree centrality
    dc = nx.degree_centrality(G)

    n = len(gdf)
    result = np.zeros(n)
    for i in range(n):
        result[i] = dc.get(i, 0.0)

    if not normalized:
        result = result * (n - 1)

    return result


def eigenvector_centrality(
    gdf, weights, normalized: bool = True, max_iter: int = 100, tol: float = 1e-6
) -> np.ndarray:
    """
    Compute eigenvector centrality for spatial network.

    Eigenvector centrality measures node importance based on
    having high-centrality neighbors.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    normalized : bool, default=True
        Normalize scores to sum to 1
    max_iter : int, default=100
        Maximum iterations for power method
    tol : float, default=1e-6
        Tolerance for convergence

    Returns
    -------
    eigenvector : ndarray
        Eigenvector centrality scores

    Examples
    --------
    >>> centrality = eigenvector_centrality(gdf, w)
    """
    G = _weights_to_graph(weights)

    try:
        # Compute eigenvector centrality
        ec = nx.eigenvector_centrality(G, max_iter=max_iter, tol=tol)

        n = len(gdf)
        result = np.zeros(n)
        for i in range(n):
            result[i] = ec.get(i, 0.0)

        if normalized:
            norm = np.linalg.norm(result)
            if norm > 0:
                result = result / norm

        return result

    except nx.PowerIterationFailedConvergence:
        # Fallback to pagerank if eigenvector doesn't converge
        pr = nx.pagerank(G, max_iter=max_iter, tol=tol)

        n = len(gdf)
        result = np.zeros(n)
        for i in range(n):
            result[i] = pr.get(i, 0.0)

        return result


def _weights_to_graph(weights) -> nx.Graph:
    """Convert spatial weights to NetworkX graph."""
    n = weights.n
    G = nx.Graph()

    # Add nodes
    G.add_nodes_from(range(n))

    # Add edges from weights matrix
    W = weights.to_sparse()
    if not isinstance(W, csr_matrix):
        W = csr_matrix(W)

    rows, cols = W.nonzero()
    for i, j in zip(rows, cols):
        if i < j:  # Undirected graph, add each edge once
            weight = W[i, j]
            G.add_edge(i, j, weight=weight)

    return G
