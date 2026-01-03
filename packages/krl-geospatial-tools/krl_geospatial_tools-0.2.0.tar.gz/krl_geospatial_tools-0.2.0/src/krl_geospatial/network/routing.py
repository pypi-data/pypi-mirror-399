"""
Routing and shortest path algorithms for spatial networks.

© 2025 KR-Labs. All rights reserved.

References
----------
Dijkstra, E. W. (1959). A note on two problems in connexion with graphs.
    Numerische Mathematik, 1(1), 269-271.
Floyd, R. W. (1962). Algorithm 97: shortest path.
    Communications of the ACM, 5(6), 345.
"""

from typing import Dict, List, Optional, Tuple, Union

import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path as sp_shortest_path


def shortest_path(
    gdf, weights, source: int, target: Optional[int] = None, method: str = "dijkstra"
) -> Union[List[int], Dict[int, List[int]]]:
    """
    Find shortest path(s) from source node.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    source : int
        Source node index
    target : int, optional
        Target node index. If None, returns paths to all nodes
    method : str, default='dijkstra'
        Algorithm: 'dijkstra' or 'bellman-ford'

    Returns
    -------
    path : list or dict
        If target specified: list of node indices in path
        If target is None: dict mapping node -> path

    Examples
    --------
    >>> from krl_geospatial.network import shortest_path
    >>> path = shortest_path(gdf, w, source=0, target=10)
    >>> print(f"Path length: {len(path)}")
    """
    G = _weights_to_graph(weights)

    if target is not None:
        # Single target
        try:
            path = nx.shortest_path(G, source=source, target=target, weight="weight", method=method)
            return path
        except nx.NetworkXNoPath:
            return []
    else:
        # All targets
        try:
            paths = nx.shortest_path(G, source=source, weight="weight", method=method)
            return paths
        except nx.NetworkXNoPath:
            return {}


def all_pairs_shortest_path(gdf, weights, method: str = "auto") -> np.ndarray:
    """
    Compute shortest path distances between all pairs of nodes.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    method : str, default='auto'
        Algorithm: 'dijkstra', 'floyd-warshall', or 'auto'

    Returns
    -------
    distances : ndarray (n, n)
        Matrix of shortest path distances

    Examples
    --------
    >>> distances = all_pairs_shortest_path(gdf, w)
    >>> print(f"Max distance: {distances.max():.2f}")
    """
    W = weights.to_sparse()
    if not isinstance(W, csr_matrix):
        W = csr_matrix(W)

    # Convert to distance matrix (inverse of weights)
    # Handle zeros by setting to large value
    data = W.data.copy()
    data[data == 0] = 1e-10
    distance_data = 1.0 / data

    distance_matrix = csr_matrix((distance_data, W.indices, W.indptr), shape=W.shape)

    # Compute shortest paths
    if method == "auto":
        # Choose based on density
        density = W.nnz / (W.shape[0] ** 2)
        method = "floyd-warshall" if density > 0.1 else "dijkstra"

    if method == "floyd-warshall":
        distances = sp_shortest_path(distance_matrix, method="FW", directed=False)
    else:  # dijkstra
        distances = sp_shortest_path(distance_matrix, method="D", directed=False)

    return distances


def network_distance_matrix(gdf, weights, metric: str = "shortest_path") -> np.ndarray:
    """
    Compute distance matrix for spatial network.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    metric : str, default='shortest_path'
        Distance metric: 'shortest_path', 'resistance', or 'commute_time'

    Returns
    -------
    distances : ndarray (n, n)
        Distance matrix

    Examples
    --------
    >>> dist_matrix = network_distance_matrix(gdf, w, metric='shortest_path')
    """
    if metric == "shortest_path":
        return all_pairs_shortest_path(gdf, weights)

    elif metric == "resistance":
        return _resistance_distance(weights)

    elif metric == "commute_time":
        return _commute_time_distance(weights)

    else:
        raise ValueError(f"Unknown metric: {metric}")


def _resistance_distance(weights) -> np.ndarray:
    """
    Compute resistance distance (effective resistance).

    Resistance distance is the electrical resistance between nodes
    when edges are resistors.
    """
    W = weights.to_sparse()
    if not isinstance(W, csr_matrix):
        W = csr_matrix(W)

    n = W.shape[0]

    # Compute Laplacian
    degrees = np.array(W.sum(axis=1)).flatten()
    D = csr_matrix((degrees, (range(n), range(n))), shape=(n, n))
    L = D - W

    # Moore-Penrose pseudoinverse
    from scipy.linalg import pinv

    L_dense = L.toarray()
    L_pinv = pinv(L_dense)

    # Resistance distance: r_ij = L+_ii + L+_jj - 2*L+_ij
    diag = np.diag(L_pinv)
    resistance = diag[:, None] + diag[None, :] - 2 * L_pinv

    return resistance


def _commute_time_distance(weights) -> np.ndarray:
    """
    Compute commute time distance.

    Commute time is the expected number of steps in a random walk
    to go from i to j and back.
    """
    W = weights.to_sparse()
    if not isinstance(W, csr_matrix):
        W = csr_matrix(W)

    n = W.shape[0]

    # Volume of graph
    vol = W.sum()

    # Resistance distance
    resistance = _resistance_distance(weights)

    # Commute time = volume * resistance
    commute_time = vol * resistance

    return commute_time


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
