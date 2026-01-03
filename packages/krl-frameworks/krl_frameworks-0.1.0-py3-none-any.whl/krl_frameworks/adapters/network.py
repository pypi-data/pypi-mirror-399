# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Network Analysis Adapters
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Network analysis adapters delegating to krl-network-analysis.

Optional, adapter-based, lazy-loaded.
Imported only if framework declares requires_network=True
and extras are installed. No hard dependency.

Provides access to:
    - Exposure graph construction from transaction data
    - Centrality measures (degree, betweenness, eigenvector, PageRank)
    - Shock propagation simulation
    - Economic network metrics
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd
    
    # Use string annotations to avoid import errors
    Graph = Any  # networkx.Graph or networkx.DiGraph

__all__ = [
    "NetworkAdapter",
    "check_network_analysis_installed",
]


class NetworkAnalysisNotInstalledError(ImportError):
    """Raised when krl-network-analysis is not installed."""
    
    def __init__(self) -> None:
        super().__init__(
            "Network analysis requires krl-network-analysis. "
            "Install with: pip install krl-frameworks[network]"
        )


def check_network_analysis_installed() -> bool:
    """
    Check if krl-network-analysis is installed.
    
    Returns:
        True if installed, False otherwise.
    """
    try:
        import krl_network  # noqa: F401
        return True
    except ImportError:
        return False


def _require_network_analysis() -> None:
    """Verify krl-network-analysis is installed, raise if not."""
    if not check_network_analysis_installed():
        raise NetworkAnalysisNotInstalledError()


class NetworkAdapter:
    """
    Thin adapter for network analysis within frameworks.
    
    Provides access to exposure graphs, centrality measures,
    and shock propagation from krl-network-analysis.
    
    Example:
        >>> adapter = NetworkAdapter()
        >>> graph = adapter.build_exposure_graph(
        ...     transactions, "bank_from", "bank_to", "exposure"
        ... )
        >>> centrality = adapter.compute_centrality(graph, method="betweenness")
        >>> shock_result = adapter.simulate_shock_propagation(
        ...     graph, initial_shock={"bank_A": 0.5}
        ... )
    """
    
    def __init__(self) -> None:
        """Initialize adapter, verifying toolkit availability."""
        _require_network_analysis()
    
    @staticmethod
    def is_available() -> bool:
        """Check if the network analysis toolkit is available."""
        return check_network_analysis_installed()
    
    def build_exposure_graph(
        self,
        transactions: pd.DataFrame,
        source_col: str,
        target_col: str,
        weight_col: str | None = None,
        *,
        directed: bool = True,
    ) -> Graph:
        """
        Build exposure network from transaction data.
        
        Args:
            transactions: DataFrame with transaction records.
            source_col: Column name for source node.
            target_col: Column name for target node.
            weight_col: Optional column for edge weights.
            directed: If True, create directed graph.
        
        Returns:
            NetworkX Graph or DiGraph representing exposure network.
        
        Example:
            >>> graph = adapter.build_exposure_graph(
            ...     df, "lender", "borrower", "loan_amount"
            ... )
        """
        # Cohesion Note: krl-network-analysis doesn't have a build_network function.
        # Use networkx directly or BaseNetwork.from_dataframe() pattern.
        # For flexibility, we build directly with networkx.
        import networkx as nx
        
        if directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()
        
        # Add edges from DataFrame
        for _, row in transactions.iterrows():
            source = row[source_col]
            target = row[target_col]
            weight = row[weight_col] if weight_col else 1.0
            
            if G.has_edge(source, target):
                # Aggregate multiple edges
                G[source][target]['weight'] += weight
            else:
                G.add_edge(source, target, weight=weight)
        
        return G
    
    def compute_centrality(
        self,
        graph: Graph,
        method: str = "betweenness",
        *,
        normalized: bool = True,
    ) -> dict[Any, float]:
        """
        Compute node centrality measures.
        
        Args:
            graph: NetworkX graph.
            method: Centrality type - one of:
                - 'degree': Degree centrality
                - 'betweenness': Betweenness centrality
                - 'eigenvector': Eigenvector centrality
                - 'pagerank': PageRank centrality
                - 'closeness': Closeness centrality
            normalized: If True, normalize centrality scores.
        
        Returns:
            Dict mapping node IDs to centrality scores.
        """
        from krl_network.metrics import (
            degree_centrality,
            betweenness_centrality,
            eigenvector_centrality,
            pagerank,
            closeness_centrality,
        )
        
        centrality_functions = {
            "degree": degree_centrality,
            "betweenness": betweenness_centrality,
            "eigenvector": eigenvector_centrality,
            "pagerank": pagerank,
            "closeness": closeness_centrality,
        }
        
        if method not in centrality_functions:
            raise ValueError(
                f"Unknown centrality method '{method}'. "
                f"Available: {list(centrality_functions.keys())}"
            )
        
        # Cohesion Note: Only degree and betweenness support the 'normalized' parameter.
        # eigenvector, pagerank, and closeness have different signatures.
        supports_normalized = {"degree", "betweenness"}
        
        if method in supports_normalized:
            return centrality_functions[method](graph, normalized=normalized)
        else:
            return centrality_functions[method](graph)
    
    def simulate_shock_propagation(
        self,
        graph: Graph,
        initial_shock: dict[Any, float],
        *,
        propagation_rate: float = 0.5,
        recovery_rate: float = 0.0,
        max_iterations: int = 100,
        convergence_threshold: float = 1e-6,
    ) -> dict[str, Any]:
        """
        Simulate shock propagation through network.
        
        Models how an initial shock to certain nodes cascades
        through the network via connected edges.
        
        Args:
            graph: NetworkX graph.
            initial_shock: Dict mapping nodes to initial shock values (0-1).
            propagation_rate: Rate at which shocks propagate along edges (0-1).
            recovery_rate: Rate at which nodes recover per iteration (0-1).
            max_iterations: Maximum simulation steps.
            convergence_threshold: Stop if max change < threshold.
        
        Returns:
            Dict with:
            - 'final_state': Dict of final shock levels per node
            - 'affected_nodes': Count of nodes with shock > 0
            - 'cascade_depth': Number of iterations until convergence
            - 'total_impact': Sum of all final shock levels
            - 'trajectory': List of states per iteration (if verbose)
        """
        # Cohesion Note: krl-network-analysis doesn't have ShockPropagator yet.
        # Implement shock propagation directly using standard contagion dynamics.
        import numpy as np
        
        nodes = list(graph.nodes())
        n = len(nodes)
        node_idx = {node: i for i, node in enumerate(nodes)}
        
        # Initialize shock state
        state = np.zeros(n)
        for node, shock in initial_shock.items():
            if node in node_idx:
                state[node_idx[node]] = shock
        
        # Build adjacency matrix with weights
        adj_matrix = np.zeros((n, n))
        for u, v, data in graph.edges(data=True):
            weight = data.get('weight', 1.0)
            i, j = node_idx[u], node_idx[v]
            adj_matrix[i, j] = weight
            if not graph.is_directed():
                adj_matrix[j, i] = weight
        
        # Normalize by max weight to get propagation factors
        max_weight = adj_matrix.max() if adj_matrix.max() > 0 else 1.0
        adj_matrix = adj_matrix / max_weight
        
        # Simulate propagation
        trajectory = [state.copy()]
        for iteration in range(max_iterations):
            # Propagate shocks: neighbors receive fraction of shock
            incoming_shock = (adj_matrix.T @ state) * propagation_rate
            
            # New state: current + incoming - recovery
            new_state = state + incoming_shock - (state * recovery_rate)
            
            # Clip to [0, 1]
            new_state = np.clip(new_state, 0, 1)
            
            # Check convergence
            max_change = np.abs(new_state - state).max()
            state = new_state
            trajectory.append(state.copy())
            
            if max_change < convergence_threshold:
                break
        
        # Build results
        final_state = {node: float(state[i]) for node, i in node_idx.items()}
        affected = sum(1 for s in state if s > 0)
        total_impact = float(state.sum())
        max_impact = float(state.max())
        
        return {
            "final_state": final_state,
            "affected_nodes": affected,
            "cascade_depth": iteration + 1,
            "total_impact": total_impact,
            "max_node_impact": max_impact,
        }
    
    def compute_network_metrics(
        self,
        graph: Graph,
    ) -> dict[str, float]:
        """
        Compute comprehensive network statistics.
        
        Args:
            graph: NetworkX graph.
        
        Returns:
            Dict with network metrics:
            - 'nodes': Number of nodes
            - 'edges': Number of edges
            - 'density': Graph density
            - 'avg_clustering': Average clustering coefficient
            - 'avg_path_length': Average shortest path length (if connected)
            - 'diameter': Graph diameter (if connected)
        """
        # Cohesion Note: Use individual metric functions from krl_network.metrics
        from krl_network.metrics import (
            density,
            average_clustering,
            diameter,
            average_shortest_path_length,
        )
        import networkx as nx
        
        # Basic stats
        num_nodes = graph.number_of_nodes()
        num_edges = graph.number_of_edges()
        
        # Density
        graph_density = density(graph)
        
        # Clustering
        avg_cluster = average_clustering(graph)
        
        # Check connectivity for path-based metrics
        if graph.is_directed():
            is_connected = nx.is_weakly_connected(graph)
        else:
            is_connected = nx.is_connected(graph)
        
        # Path metrics (only if connected)
        avg_path = None
        graph_diameter = None
        if is_connected:
            try:
                avg_path = average_shortest_path_length(graph)
                graph_diameter = diameter(graph)
            except Exception:
                pass  # May fail on very large or disconnected graphs
        
        return {
            "nodes": num_nodes,
            "edges": num_edges,
            "density": graph_density,
            "avg_clustering": avg_cluster,
            "avg_path_length": avg_path,
            "diameter": graph_diameter,
            "is_connected": is_connected,
        }
    
    def identify_systemically_important(
        self,
        graph: Graph,
        *,
        top_k: int = 10,
        method: str = "betweenness",
    ) -> list[tuple[Any, float]]:
        """
        Identify systemically important nodes.
        
        Args:
            graph: NetworkX graph.
            top_k: Number of top nodes to return.
            method: Centrality method for ranking.
        
        Returns:
            List of (node_id, centrality_score) tuples, sorted descending.
        """
        centrality = self.compute_centrality(graph, method=method)
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:top_k]
    
    def compute_community_structure(
        self,
        graph: Graph,
        *,
        method: str = "louvain",
    ) -> dict[str, Any]:
        """
        Detect community structure in network.
        
        Args:
            graph: NetworkX graph.
            method: Community detection algorithm ('louvain', 'label_propagation').
        
        Returns:
            Dict with:
            - 'communities': Dict mapping node to community ID
            - 'num_communities': Number of detected communities
            - 'modularity': Modularity score
        """
        # Cohesion Note: Use specific functions from krl_network.community
        from krl_network.community import (
            louvain_communities,
            label_propagation,
            calculate_modularity,
        )
        
        if method == "louvain":
            partition = louvain_communities(graph)
        elif method == "label_propagation":
            partition = label_propagation(graph)
        else:
            raise ValueError(f"Unknown method '{method}'. Use 'louvain' or 'label_propagation'.")
        
        # Convert partition to node->community mapping
        # Handle both list-of-sets and dict formats
        if isinstance(partition, dict):
            membership = partition
        else:
            # List of sets format
            membership = {}
            for comm_id, members in enumerate(partition):
                for node in members:
                    membership[node] = comm_id
        
        num_communities = len(set(membership.values()))
        modularity = calculate_modularity(graph, membership)
        
        return {
            "communities": membership,
            "num_communities": num_communities,
            "modularity": modularity,
        }
