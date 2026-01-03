"""
Community detection algorithms for spatial networks.

© 2025 KR-Labs. All rights reserved.

References
----------
Blondel, V. D., et al. (2008). Fast unfolding of communities in large networks.
    Journal of Statistical Mechanics: Theory and Experiment, 2008(10), P10008.
Girvan, M., & Newman, M. E. (2002). Community structure in social and biological
    networks. PNAS, 99(12), 7821-7826.
"""

from typing import Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix


def louvain_communities(
    gdf, weights, resolution: float = 1.0, seed: Optional[int] = None
) -> np.ndarray:
    """
    Detect communities using Louvain algorithm.

    Fast algorithm that optimizes modularity by hierarchically
    merging communities.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    resolution : float, default=1.0
        Resolution parameter (higher = more communities)
    seed : int, optional
        Random seed for reproducibility

    Returns
    -------
    communities : ndarray
        Community labels for each node

    Examples
    --------
    >>> from krl_geospatial.network import louvain_communities
    >>> communities = louvain_communities(gdf, w, resolution=1.0)
    """
    G = _weights_to_graph(weights)

    # Compute Louvain communities
    import networkx.algorithms.community as nx_comm

    communities_list = nx_comm.louvain_communities(G, resolution=resolution, seed=seed)

    # Convert to labels
    n = len(gdf)
    labels = np.zeros(n, dtype=int)
    for community_id, nodes in enumerate(communities_list):
        for node in nodes:
            labels[node] = community_id

    return labels


def label_propagation(gdf, weights, max_iter: int = 100, seed: Optional[int] = None) -> np.ndarray:
    """
    Detect communities using label propagation.

    Simple algorithm where each node adopts the most common
    label among its neighbors.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    max_iter : int, default=100
        Maximum iterations
    seed : int, optional
        Random seed for reproducibility

    Returns
    -------
    communities : ndarray
        Community labels for each node

    Examples
    --------
    >>> communities = label_propagation(gdf, w)
    """
    G = _weights_to_graph(weights)

    # Label propagation
    import networkx.algorithms.community as nx_comm

    communities_gen = nx_comm.label_propagation_communities(G)
    communities_list = list(communities_gen)

    # Convert to labels
    n = len(gdf)
    labels = np.zeros(n, dtype=int)
    for community_id, nodes in enumerate(communities_list):
        for node in nodes:
            labels[node] = community_id

    return labels


def girvan_newman(gdf, weights, k: Optional[int] = None) -> np.ndarray:
    """
    Detect communities using Girvan-Newman algorithm.

    Hierarchical algorithm that iteratively removes edges with
    highest betweenness centrality.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    k : int, optional
        Number of communities to find. If None, uses modularity
        to determine optimal number.

    Returns
    -------
    communities : ndarray
        Community labels for each node

    Examples
    --------
    >>> communities = girvan_newman(gdf, w, k=5)
    """
    G = _weights_to_graph(weights)

    # Run Girvan-Newman
    import networkx.algorithms.community as nx_comm

    comp = nx_comm.girvan_newman(G)

    if k is None:
        # Find optimal number of communities by modularity
        best_modularity = -1
        best_communities = None

        for communities_tuple in comp:
            communities_list = list(communities_tuple)
            mod = nx_comm.modularity(G, communities_list)

            if mod > best_modularity:
                best_modularity = mod
                best_communities = communities_list

            # Stop if modularity starts decreasing significantly
            if best_modularity - mod > 0.01:
                break

        communities_list = best_communities
    else:
        # Get k communities
        for _ in range(k - 1):
            communities_tuple = next(comp)
        communities_list = list(communities_tuple)

    # Convert to labels
    n = len(gdf)
    labels = np.zeros(n, dtype=int)
    for community_id, nodes in enumerate(communities_list):
        for node in nodes:
            labels[node] = community_id

    return labels


def modularity_score(gdf, weights, communities: np.ndarray, resolution: float = 1.0) -> float:
    """
    Compute modularity for a community partition.

    Modularity measures the strength of division of a network
    into communities. Values range from -0.5 to 1.0, with higher
    values indicating better community structure.

    Parameters
    ----------
    gdf : GeoDataFrame
        Spatial data
    weights : SpatialWeights
        Spatial weights matrix
    communities : ndarray
        Community labels for each node
    resolution : float, default=1.0
        Resolution parameter

    Returns
    -------
    modularity : float
        Modularity score (higher is better)

    Examples
    --------
    >>> from krl_geospatial.network import modularity_score
    >>> mod = modularity_score(gdf, w, communities)
    >>> print(f"Modularity: {mod:.3f}")
    """
    G = _weights_to_graph(weights)

    # Convert labels to list of sets
    unique_labels = np.unique(communities)
    communities_list = []
    for label in unique_labels:
        nodes = set(np.where(communities == label)[0])
        communities_list.append(nodes)

    # Compute modularity
    import networkx.algorithms.community as nx_comm

    mod = nx_comm.modularity(G, communities_list, resolution=resolution)

    return mod


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
