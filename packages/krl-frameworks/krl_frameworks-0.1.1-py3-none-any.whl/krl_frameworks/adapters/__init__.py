# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Adapters for Ecosystem Integration
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Adapters for KRL ecosystem package integration.

krl-frameworks is the orchestration layer. It delegates to:
- krl-data-connectors (explicit data injection)
- krl-causal-policy-toolkit (causal estimation)
- krl-geospatial-tools (spatial analysis, optional)
- krl-network-analysis (network analysis, optional)

All adapters are thin wrappers providing:
- Explicit invocation (no auto-discovery)
- Lazy loading (no hard dependencies for optional packages)
- Result normalization to framework schemas

Design Principles:
    1. krl-frameworks never instantiates connectors directly
    2. All data enters via DataBundle
    3. Causal methods are delegated, not duplicated
    4. Spatial/network are optional, adapter-based, lazy-loaded
"""

from __future__ import annotations

from krl_frameworks.adapters.connectors import (
    ConnectorProtocol,
    DataBundleFactory,
)
from krl_frameworks.adapters.causal import (
    CausalAdapter,
    CausalMethod,
    get_causal_estimator,
)

__all__ = [
    # Connector adapters
    "ConnectorProtocol",
    "DataBundleFactory",
    # Causal adapters
    "CausalAdapter",
    "CausalMethod",
    "get_causal_estimator",
    # Factory functions for optional adapters
    "get_spatial_adapter",
    "get_network_adapter",
    # Spatial econometric adapters (for REMSOM v2)
    "get_spatial_lag_adapter",
    "get_spatial_error_adapter",
    "get_gwr_adapter",
]


def get_spatial_adapter():
    """
    Get spatial adapter (requires krl-geospatial-tools).
    
    Returns:
        SpatialAdapter instance.
    
    Raises:
        ImportError: If krl-geospatial-tools not installed.
    
    Example:
        >>> spatial = get_spatial_adapter()
        >>> weights = spatial.compute_spatial_weights(gdf, method="queen")
    """
    from krl_frameworks.adapters.spatial import SpatialAdapter
    return SpatialAdapter()


def get_network_adapter():
    """
    Get network adapter (requires krl-network-analysis).
    
    Returns:
        NetworkAdapter instance.
    
    Raises:
        ImportError: If krl-network-analysis not installed.
    
    Example:
        >>> network = get_network_adapter()
        >>> graph = network.build_exposure_graph(transactions, "from", "to", "amount")
    """
    from krl_frameworks.adapters.network import NetworkAdapter
    return NetworkAdapter()


def get_spatial_lag_adapter():
    """
    Get Spatial Lag (SAR) model adapter for REMSOM v2.
    
    SAR models spatial spillover effects where the dependent variable
    is influenced by spatially weighted neighbors: y = ρWy + Xβ + ε
    
    Returns:
        SpatialLagAdapter instance.
    
    Example:
        >>> sar = get_spatial_lag_adapter()
        >>> result = sar.fit(y, X, weights)
        >>> print(f"Spatial autoregressive coefficient: {result['rho']}")
    """
    from krl_frameworks.adapters.spatial import SpatialLagAdapter
    return SpatialLagAdapter()


def get_spatial_error_adapter():
    """
    Get Spatial Error Model (SEM) adapter for REMSOM v2.
    
    SEM models spatially correlated error terms: y = Xβ + u, u = λWu + ε
    
    Returns:
        SpatialErrorAdapter instance.
    
    Example:
        >>> sem = get_spatial_error_adapter()
        >>> result = sem.fit(y, X, weights)
        >>> print(f"Spatial error coefficient: {result['lambda']}")
    """
    from krl_frameworks.adapters.spatial import SpatialErrorAdapter
    return SpatialErrorAdapter()


def get_gwr_adapter(bandwidth: float = None):
    """
    Get Geographically Weighted Regression (GWR) adapter for REMSOM v2.
    
    GWR estimates local regression models where coefficients vary spatially,
    detecting heterogeneity in opportunity drivers across geography.
    
    Args:
        bandwidth: Fixed bandwidth for kernel weighting. If None, uses adaptive.
    
    Returns:
        GWRAdapter instance.
    
    Example:
        >>> gwr = get_gwr_adapter()
        >>> result = gwr.fit(y, X, coordinates)
        >>> local_r2 = result['local_r_squared']
    """
    from krl_frameworks.adapters.spatial import GWRAdapter
    return GWRAdapter(bandwidth=bandwidth)
