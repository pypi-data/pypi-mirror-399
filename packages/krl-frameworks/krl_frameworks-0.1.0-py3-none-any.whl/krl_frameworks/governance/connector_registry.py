# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Connector Factory Registry
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Connector Factory Registry for Runtime Governance.

Manages connector factories with tier-based access control. Factories are
registered explicitly—there is no auto-discovery. Each factory is gated
by the minimum tier required to use it.

Design Principles:
    1. Explicit registration over magic discovery
    2. Tier enforcement at factory access time
    3. Fallback chains for graceful degradation (in TEST mode only)
    4. Configuration validation before instantiation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Protocol, runtime_checkable

import pandas as pd

if TYPE_CHECKING:
    from krl_frameworks.core.tier import Tier

__all__ = [
    "ConnectorProtocol",
    "ConnectorFactory",
    "ConnectorFactoryRegistry",
    "get_global_connector_registry",
    "register_connector_factory",
    "TierAccessDeniedError",
    "ConnectorNotFoundError",
]


# ════════════════════════════════════════════════════════════════════════════════
# Protocols and Types
# ════════════════════════════════════════════════════════════════════════════════


@runtime_checkable
class ConnectorProtocol(Protocol):
    """Protocol that all connectors must satisfy."""
    
    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """Fetch data from the connector source."""
        ...


# Type alias for connector factory functions
ConnectorFactoryFn = Callable[[dict[str, Any]], ConnectorProtocol]


# ════════════════════════════════════════════════════════════════════════════════
# Exceptions
# ════════════════════════════════════════════════════════════════════════════════


class ConnectorNotFoundError(KeyError):
    """Raised when a requested connector type is not registered."""
    
    def __init__(self, connector_type: str, available: list[str] | None = None) -> None:
        self.connector_type = connector_type
        self.available = available or []
        message = f"Connector type '{connector_type}' not registered"
        if self.available:
            message += f". Available: {', '.join(self.available)}"
        super().__init__(message)


class TierAccessDeniedError(PermissionError):
    """Raised when user tier is insufficient for connector access."""
    
    def __init__(
        self,
        connector_type: str,
        user_tier: str,
        required_tier: str,
    ) -> None:
        self.connector_type = connector_type
        self.user_tier = user_tier
        self.required_tier = required_tier
        super().__init__(
            f"Connector '{connector_type}' requires tier '{required_tier}' "
            f"but user has tier '{user_tier}'"
        )


# ════════════════════════════════════════════════════════════════════════════════
# Connector Factory
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ConnectorFactory:
    """
    Registered connector factory with tier gating.
    
    Attributes:
        connector_type: Unique identifier (e.g., "fred", "census", "bls").
        factory_fn: Callable that creates connector instances.
        min_tier: Minimum subscription tier required.
        description: Human-readable description.
        domains: List of data domains this connector serves.
        requires_api_key: Whether an API key is required.
        config_schema: JSON Schema for configuration validation.
    """
    connector_type: str
    factory_fn: ConnectorFactoryFn
    min_tier: str = "community"
    description: str = ""
    domains: list[str] = field(default_factory=list)
    requires_api_key: bool = False
    config_schema: dict[str, Any] | None = None
    
    def create(self, config: dict[str, Any] | None = None) -> ConnectorProtocol:
        """
        Create a connector instance.
        
        Args:
            config: Configuration dictionary for the connector.
        
        Returns:
            Instantiated connector.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        config = config or {}
        
        # Validate config against schema if provided
        if self.config_schema:
            self._validate_config(config)
        
        return self.factory_fn(config)
    
    def _validate_config(self, config: dict[str, Any]) -> None:
        """Validate configuration against schema."""
        # Basic validation - check required keys
        schema = self.config_schema or {}
        required = schema.get("required", [])
        
        for key in required:
            if key not in config:
                raise ValueError(
                    f"Connector '{self.connector_type}' requires config key '{key}'"
                )
    
    def can_access(self, user_tier: str) -> bool:
        """
        Check if user tier can access this connector.
        
        Args:
            user_tier: User's subscription tier.
        
        Returns:
            True if access is permitted.
        """
        tier_order = ["community", "professional", "enterprise"]
        
        try:
            user_idx = tier_order.index(user_tier.lower())
            required_idx = tier_order.index(self.min_tier.lower())
            return user_idx >= required_idx
        except ValueError:
            # Unknown tier - deny access
            return False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "connector_type": self.connector_type,
            "min_tier": self.min_tier,
            "description": self.description,
            "domains": self.domains,
            "requires_api_key": self.requires_api_key,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Connector Factory Registry
# ════════════════════════════════════════════════════════════════════════════════


class ConnectorFactoryRegistry:
    """
    Central registry for connector factories.
    
    The registry manages connector factory registration and access with
    tier-based gating. It supports:
    
    - Explicit factory registration
    - Tier-based access control
    - Domain-based connector lookup
    - Fallback chain resolution
    
    Example:
        >>> registry = ConnectorFactoryRegistry()
        >>> 
        >>> # Register a factory
        >>> registry.register(
        ...     connector_type="fred",
        ...     factory_fn=lambda cfg: FREDConnector(**cfg),
        ...     min_tier="community",
        ...     domains=["economic", "labor", "financial"],
        ... )
        >>> 
        >>> # Get a factory (with tier check)
        >>> factory = registry.get_factory("fred", user_tier="community")
        >>> connector = factory.create({"api_key": "..."})
    """
    
    def __init__(self) -> None:
        """Initialize empty registry."""
        self._factories: dict[str, ConnectorFactory] = {}
        self._domain_index: dict[str, list[str]] = {}  # domain → [connector_types]
    
    def register(
        self,
        connector_type: str,
        factory_fn: ConnectorFactoryFn,
        *,
        min_tier: str = "community",
        description: str = "",
        domains: list[str] | None = None,
        requires_api_key: bool = False,
        config_schema: dict[str, Any] | None = None,
    ) -> "ConnectorFactoryRegistry":
        """
        Register a connector factory.
        
        Args:
            connector_type: Unique identifier for this connector.
            factory_fn: Callable that creates connector instances.
            min_tier: Minimum subscription tier required.
            description: Human-readable description.
            domains: Data domains this connector serves.
            requires_api_key: Whether an API key is required.
            config_schema: JSON Schema for config validation.
        
        Returns:
            Self for method chaining.
        
        Raises:
            ValueError: If connector_type is already registered.
        """
        if connector_type in self._factories:
            raise ValueError(
                f"Connector type '{connector_type}' is already registered"
            )
        
        factory = ConnectorFactory(
            connector_type=connector_type,
            factory_fn=factory_fn,
            min_tier=min_tier,
            description=description,
            domains=domains or [],
            requires_api_key=requires_api_key,
            config_schema=config_schema,
        )
        
        self._factories[connector_type] = factory
        
        # Index by domain
        for domain in factory.domains:
            if domain not in self._domain_index:
                self._domain_index[domain] = []
            self._domain_index[domain].append(connector_type)
        
        return self
    
    def unregister(self, connector_type: str) -> bool:
        """
        Unregister a connector factory.
        
        Args:
            connector_type: The connector type to remove.
        
        Returns:
            True if removed, False if not found.
        """
        factory = self._factories.pop(connector_type, None)
        if factory:
            # Remove from domain index
            for domain in factory.domains:
                if domain in self._domain_index:
                    self._domain_index[domain] = [
                        ct for ct in self._domain_index[domain]
                        if ct != connector_type
                    ]
            return True
        return False
    
    def get_factory(
        self,
        connector_type: str,
        user_tier: str = "community",
    ) -> ConnectorFactory:
        """
        Get a connector factory with tier access check.
        
        Args:
            connector_type: The connector type to retrieve.
            user_tier: User's subscription tier.
        
        Returns:
            The connector factory.
        
        Raises:
            ConnectorNotFoundError: If connector type not registered.
            TierAccessDeniedError: If user tier insufficient.
        """
        if connector_type not in self._factories:
            raise ConnectorNotFoundError(
                connector_type,
                available=list(self._factories.keys()),
            )
        
        factory = self._factories[connector_type]
        
        if not factory.can_access(user_tier):
            raise TierAccessDeniedError(
                connector_type=connector_type,
                user_tier=user_tier,
                required_tier=factory.min_tier,
            )
        
        return factory
    
    def get_factory_for_domain(
        self,
        domain: str,
        user_tier: str = "community",
        *,
        preferred_type: str | None = None,
    ) -> ConnectorFactory | None:
        """
        Get the best available connector factory for a domain.
        
        Args:
            domain: The data domain.
            user_tier: User's subscription tier.
            preferred_type: Preferred connector type (if available).
        
        Returns:
            Best available factory, or None if none accessible.
        """
        # Try preferred type first
        if preferred_type and preferred_type in self._factories:
            factory = self._factories[preferred_type]
            if factory.can_access(user_tier) and domain in factory.domains:
                return factory
        
        # Find any accessible factory for domain
        connector_types = self._domain_index.get(domain, [])
        for connector_type in connector_types:
            factory = self._factories[connector_type]
            if factory.can_access(user_tier):
                return factory
        
        return None
    
    def list_connectors(
        self,
        user_tier: str | None = None,
        domain: str | None = None,
    ) -> list[str]:
        """
        List available connector types.
        
        Args:
            user_tier: Filter by accessible tier.
            domain: Filter by domain.
        
        Returns:
            List of connector type identifiers.
        """
        result = []
        
        for connector_type, factory in self._factories.items():
            # Tier filter
            if user_tier and not factory.can_access(user_tier):
                continue
            
            # Domain filter
            if domain and domain not in factory.domains:
                continue
            
            result.append(connector_type)
        
        return result
    
    def list_domains(self) -> list[str]:
        """List all registered domains."""
        return list(self._domain_index.keys())
    
    def has_connector(self, connector_type: str) -> bool:
        """Check if a connector type is registered."""
        return connector_type in self._factories
    
    def has_domain(self, domain: str) -> bool:
        """Check if a domain has any connectors."""
        return domain in self._domain_index and len(self._domain_index[domain]) > 0
    
    def get_info(self, connector_type: str) -> dict[str, Any] | None:
        """Get information about a connector type."""
        factory = self._factories.get(connector_type)
        return factory.to_dict() if factory else None
    
    def clear(self) -> None:
        """Clear all registrations."""
        self._factories.clear()
        self._domain_index.clear()


# ════════════════════════════════════════════════════════════════════════════════
# Global Registry
# ════════════════════════════════════════════════════════════════════════════════

_global_registry: ConnectorFactoryRegistry | None = None


def get_global_connector_registry() -> ConnectorFactoryRegistry:
    """
    Get the global connector factory registry.
    
    Creates the registry on first access and populates it with
    default connector factories.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ConnectorFactoryRegistry()
        _populate_default_factories(_global_registry)
    return _global_registry


def register_connector_factory(
    connector_type: str,
    factory_fn: ConnectorFactoryFn,
    **kwargs: Any,
) -> None:
    """
    Register a connector factory in the global registry.
    
    Convenience function for registering factories.
    """
    get_global_connector_registry().register(
        connector_type=connector_type,
        factory_fn=factory_fn,
        **kwargs,
    )


def _populate_default_factories(registry: ConnectorFactoryRegistry) -> None:
    """
    Populate registry with default connector factories.
    
    This registers factories for known connector types from krl-data-connectors.
    Each factory is a thin wrapper that imports and instantiates on demand.
    """
    # FRED Connector (Community tier)
    def _create_fred(config: dict[str, Any]) -> ConnectorProtocol:
        try:
            from krl_data_connectors.community import FREDBasicConnector
            return FREDBasicConnector(**config)
        except ImportError:
            # Return a stub that raises on fetch
            return _create_stub_connector("fred", config)
    
    registry.register(
        connector_type="fred",
        factory_fn=_create_fred,
        min_tier="community",
        description="Federal Reserve Economic Data (FRED)",
        domains=["economic", "labor", "financial", "housing"],
        requires_api_key=True,
    )
    
    # Census Connector (Community tier)
    def _create_census(config: dict[str, Any]) -> ConnectorProtocol:
        try:
            from krl_data_connectors.community import CensusConnector
            return CensusConnector(**config)
        except ImportError:
            return _create_stub_connector("census", config)
    
    registry.register(
        connector_type="census",
        factory_fn=_create_census,
        min_tier="community",
        description="U.S. Census Bureau API",
        domains=["health", "education", "housing", "demographic"],
        requires_api_key=True,
    )
    
    # BLS Connector (Community tier)
    def _create_bls(config: dict[str, Any]) -> ConnectorProtocol:
        try:
            from krl_data_connectors.community import BLSConnector
            return BLSConnector(**config)
        except ImportError:
            return _create_stub_connector("bls", config)
    
    registry.register(
        connector_type="bls",
        factory_fn=_create_bls,
        min_tier="community",
        description="Bureau of Labor Statistics",
        domains=["labor", "economic", "employment"],
        requires_api_key=False,
    )
    
    # World Bank Connector (Community tier)
    def _create_worldbank(config: dict[str, Any]) -> ConnectorProtocol:
        try:
            from krl_data_connectors.community import WorldBankConnector
            return WorldBankConnector(**config)
        except ImportError:
            return _create_stub_connector("worldbank", config)
    
    registry.register(
        connector_type="worldbank",
        factory_fn=_create_worldbank,
        min_tier="community",
        description="World Bank Open Data",
        domains=["health", "education", "economic", "demographic", "development"],
        requires_api_key=False,
    )


class _StubConnector:
    """Stub connector that raises on fetch."""
    
    def __init__(self, connector_type: str, config: dict[str, Any]) -> None:
        self.connector_type = connector_type
        self.config = config
    
    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        raise ImportError(
            f"Connector '{self.connector_type}' requires krl-data-connectors. "
            f"Install with: pip install krl-data-connectors"
        )


def _create_stub_connector(connector_type: str, config: dict[str, Any]) -> _StubConnector:
    """Create a stub connector for when real connector is not installed."""
    return _StubConnector(connector_type, config)
