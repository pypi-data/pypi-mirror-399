# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Connector Adapters
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Connector adapters for explicit data injection.

krl-frameworks never instantiates connectors directly.
All data enters via DataBundle. This factory provides
explicit invocation when caller chooses to use krl-data-connectors.

Design Principles:
    - Determinism: No auto-discovery of data sources
    - Auditability: Explicit invocation paths
    - Tier enforcement: Caller controls access
    - Air-gapped deployments: No network calls without explicit request
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

import pandas as pd

if TYPE_CHECKING:
    from krl_frameworks.core.data_bundle import DataBundle

__all__ = [
    "ConnectorProtocol",
    "DataBundleFactory",
]


@runtime_checkable
class ConnectorProtocol(Protocol):
    """
    Protocol for krl-data-connectors compatibility.
    
    Any connector implementing a `fetch` method can be used
    with the DataBundleFactory.
    """
    
    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch data from the connector source.
        
        Args:
            **kwargs: Connector-specific parameters.
        
        Returns:
            DataFrame with fetched data.
        """
        ...


class DataBundleFactory:
    """
    Create DataBundles from explicit connector invocations.
    
    This factory wraps krl-data-connectors but only when
    explicitly invoked by the caller. No auto-discovery.
    
    Example:
        >>> from krl_data_connectors.community import FREDBasicConnector
        >>> factory = DataBundleFactory()
        >>> factory.add_connector("economic", FREDBasicConnector())
        >>> bundle = factory.build(economic={"series_id": "UNRATE"})
    
    Example (one-shot):
        >>> bundle = DataBundleFactory.from_connectors(
        ...     connectors={"economic": FREDBasicConnector()},
        ...     economic={"series_id": "UNRATE"},
        ... )
    """
    
    def __init__(self) -> None:
        """Initialize empty factory."""
        self._connectors: dict[str, ConnectorProtocol] = {}
    
    def add_connector(
        self,
        domain: str,
        connector: ConnectorProtocol,
    ) -> DataBundleFactory:
        """
        Register a connector for a domain.
        
        Args:
            domain: Domain name (e.g., "economic", "health", "spatial").
            connector: Connector instance implementing ConnectorProtocol.
        
        Returns:
            Self for method chaining.
        
        Raises:
            TypeError: If connector doesn't implement fetch method.
        """
        if not isinstance(connector, ConnectorProtocol):
            raise TypeError(
                f"Connector must implement ConnectorProtocol (have fetch method). "
                f"Got: {type(connector).__name__}"
            )
        self._connectors[domain] = connector
        return self
    
    def remove_connector(self, domain: str) -> DataBundleFactory:
        """
        Remove a connector for a domain.
        
        Args:
            domain: Domain name to remove.
        
        Returns:
            Self for method chaining.
        """
        self._connectors.pop(domain, None)
        return self
    
    def list_domains(self) -> list[str]:
        """List registered domain names."""
        return list(self._connectors.keys())
    
    def build(self, **domain_params: dict[str, Any]) -> DataBundle:
        """
        Build DataBundle by fetching from registered connectors.
        
        Args:
            **domain_params: Keyword args where key is domain name
                and value is dict of fetch parameters for that connector.
        
        Returns:
            DataBundle with fetched data.
        
        Example:
            >>> factory.add_connector("economic", FREDBasicConnector())
            >>> factory.add_connector("health", CDCConnector())
            >>> bundle = factory.build(
            ...     economic={"series_id": "UNRATE"},
            ...     health={"indicator": "mortality"},
            ... )
        """
        from krl_frameworks.core.data_bundle import DataBundle
        
        dataframes: dict[str, pd.DataFrame] = {}
        
        for domain, connector in self._connectors.items():
            params = domain_params.get(domain, {})
            try:
                dataframes[domain] = connector.fetch(**params)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to fetch data for domain '{domain}': {e}"
                ) from e
        
        return DataBundle.from_dataframes(dataframes)
    
    @classmethod
    def from_connectors(
        cls,
        connectors: dict[str, ConnectorProtocol],
        **fetch_params: dict[str, Any],
    ) -> DataBundle:
        """
        One-shot factory method to build DataBundle from connectors.
        
        Args:
            connectors: Dict mapping domain names to connector instances.
            **fetch_params: Parameters for each connector's fetch method.
        
        Returns:
            DataBundle with fetched data.
        
        Example:
            >>> bundle = DataBundleFactory.from_connectors(
            ...     connectors={
            ...         "economic": FREDBasicConnector(),
            ...         "demographic": CensusConnector(),
            ...     },
            ...     economic={"series_id": "GDP"},
            ...     demographic={"table": "B01001"},
            ... )
        """
        factory = cls()
        for domain, connector in connectors.items():
            factory.add_connector(domain, connector)
        return factory.build(**fetch_params)
