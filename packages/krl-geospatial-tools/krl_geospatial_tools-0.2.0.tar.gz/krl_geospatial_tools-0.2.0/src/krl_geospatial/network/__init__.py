"""
Network analysis module for spatial networks.

© 2025 KR-Labs. All rights reserved.
"""

from krl_geospatial.network.community import (
    girvan_newman,
    label_propagation,
    louvain_communities,
    modularity_score,
)
from krl_geospatial.network.routing import (
    all_pairs_shortest_path,
    network_distance_matrix,
    shortest_path,
)
from krl_geospatial.network.topology import (
    betweenness_centrality,
    closeness_centrality,
    degree_centrality,
    eigenvector_centrality,
    network_centrality,
)

__all__ = [
    # Topology
    "network_centrality",
    "betweenness_centrality",
    "closeness_centrality",
    "degree_centrality",
    "eigenvector_centrality",
    # Community detection
    "louvain_communities",
    "label_propagation",
    "modularity_score",
    "girvan_newman",
    # Routing
    "shortest_path",
    "all_pairs_shortest_path",
    "network_distance_matrix",
]
