# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Binding Registry
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Binding Registry for Runtime Dependency Resolution.

This module provides the BindingRegistry that tracks resolved dependencies
for framework execution. Bindings are the actual instances of connectors,
toolkit methods, and model zoo models that satisfy declared capabilities.

Design Principles:
    1. Bindings are resolved before execution, not during
    2. Missing bindings cause validation failures, not runtime errors
    3. Bindings are inspectable for audit and debugging
    4. Bindings are immutable once set (for the execution scope)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Protocol, runtime_checkable

import pandas as pd

if TYPE_CHECKING:
    pass

__all__ = [
    "BindingRegistry",
    "ConnectorBinding",
    "ToolkitBinding",
    "ModelZooBinding",
    "ConnectorProtocol",
    "ToolkitMethodProtocol",
    "ModelProtocol",
]


# ════════════════════════════════════════════════════════════════════════════════
# Protocols for Type Safety
# ════════════════════════════════════════════════════════════════════════════════


@runtime_checkable
class ConnectorProtocol(Protocol):
    """Protocol for data connectors."""
    
    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """Fetch data from the connector."""
        ...


@runtime_checkable
class ToolkitMethodProtocol(Protocol):
    """Protocol for toolkit methods (causal, geospatial, network)."""
    
    def fit(self, data: pd.DataFrame, **kwargs: Any) -> Any:
        """Fit the method to data."""
        ...


@runtime_checkable
class ModelProtocol(Protocol):
    """Protocol for model zoo models."""
    
    def predict(self, data: Any, **kwargs: Any) -> Any:
        """Generate predictions."""
        ...


# ════════════════════════════════════════════════════════════════════════════════
# Binding Data Classes
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ConnectorBinding:
    """
    A resolved connector binding for a data domain.
    
    Attributes:
        domain: Data domain (e.g., "health", "education").
        connector: The connector instance.
        connector_type: Type identifier (e.g., "fred", "census").
        config: Connector-specific configuration.
        is_synthetic: Whether this produces synthetic data.
    """
    domain: str
    connector: ConnectorProtocol | None
    connector_type: str = "unknown"
    config: dict[str, Any] = field(default_factory=dict)
    is_synthetic: bool = False
    
    @property
    def is_bound(self) -> bool:
        """Whether a real connector is bound."""
        return self.connector is not None and not self.is_synthetic
    
    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch data using the bound connector.
        
        Raises:
            RuntimeError: If no connector is bound.
        """
        if self.connector is None:
            raise RuntimeError(
                f"Cannot fetch data: no connector bound for domain '{self.domain}'"
            )
        merged_kwargs = {**self.config, **kwargs}
        return self.connector.fetch(**merged_kwargs)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "domain": self.domain,
            "connector_type": self.connector_type,
            "is_bound": self.is_bound,
            "is_synthetic": self.is_synthetic,
            "config": self.config,
        }


@dataclass
class ToolkitBinding:
    """
    A resolved toolkit method binding.
    
    Attributes:
        toolkit: Toolkit identifier (e.g., "causal", "geospatial").
        method: Method identifier (e.g., "did", "scm", "queen_weights").
        instance: The toolkit method instance.
        package: Package name for reference.
        version: Package version.
    """
    toolkit: str
    method: str | None
    instance: ToolkitMethodProtocol | Callable[..., Any] | None
    package: str = ""
    version: str = ""
    
    @property
    def is_bound(self) -> bool:
        """Whether a real method is bound."""
        return self.instance is not None
    
    @property
    def full_name(self) -> str:
        """Full method name (toolkit.method)."""
        if self.method:
            return f"{self.toolkit}.{self.method}"
        return self.toolkit
    
    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke the bound toolkit method.
        
        Raises:
            RuntimeError: If no method is bound.
        """
        if self.instance is None:
            raise RuntimeError(
                f"Cannot invoke: no method bound for '{self.full_name}'"
            )
        if hasattr(self.instance, "fit"):
            return self.instance.fit(*args, **kwargs)
        elif callable(self.instance):
            return self.instance(*args, **kwargs)
        else:
            raise RuntimeError(
                f"Bound instance for '{self.full_name}' is not callable"
            )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "toolkit": self.toolkit,
            "method": self.method,
            "full_name": self.full_name,
            "is_bound": self.is_bound,
            "package": self.package,
            "version": self.version,
        }


@dataclass
class ModelZooBinding:
    """
    A resolved model zoo model binding.
    
    Attributes:
        category: Model category (e.g., "econometric", "time_series").
        model_type: Model type (e.g., "sarima", "arima").
        instance: The model instance.
        purpose: What the model is used for.
        is_loaded: Whether the model weights are loaded.
    """
    category: str
    model_type: str
    instance: ModelProtocol | Any | None
    purpose: str = ""
    is_loaded: bool = False
    
    @property
    def is_bound(self) -> bool:
        """Whether a model is bound."""
        return self.instance is not None
    
    @property
    def full_name(self) -> str:
        """Full model name (category.model_type)."""
        return f"{self.category}.{self.model_type}"
    
    def predict(self, data: Any, **kwargs: Any) -> Any:
        """
        Generate predictions using the bound model.
        
        Raises:
            RuntimeError: If no model is bound.
        """
        if self.instance is None:
            raise RuntimeError(
                f"Cannot predict: no model bound for '{self.full_name}'"
            )
        if hasattr(self.instance, "predict"):
            return self.instance.predict(data, **kwargs)
        elif hasattr(self.instance, "forecast"):
            return self.instance.forecast(data, **kwargs)
        elif callable(self.instance):
            return self.instance(data, **kwargs)
        else:
            raise RuntimeError(
                f"Bound model for '{self.full_name}' has no predict/forecast method"
            )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category,
            "model_type": self.model_type,
            "full_name": self.full_name,
            "is_bound": self.is_bound,
            "is_loaded": self.is_loaded,
            "purpose": self.purpose,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Binding Registry
# ════════════════════════════════════════════════════════════════════════════════


class BindingRegistry:
    """
    Registry for resolved runtime bindings.
    
    The BindingRegistry is the central repository for all resolved
    dependencies. It is populated before framework execution and
    validated against the framework's CapabilityDeclaration.
    
    Example:
        >>> registry = BindingRegistry()
        >>> registry.bind_connector("health", fred_connector, "fred")
        >>> registry.bind_toolkit("causal", "did", did_estimator)
        >>> 
        >>> # Validate against capabilities
        >>> errors = capabilities.validate(registry)
        >>> if errors:
        ...     raise MissingCapabilityError(...)
    """
    
    def __init__(self) -> None:
        """Initialize empty registry."""
        self._connectors: dict[str, ConnectorBinding] = {}
        self._toolkits: dict[str, ToolkitBinding] = {}
        self._models: dict[str, ModelZooBinding] = {}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Properties for Direct Access
    # ═══════════════════════════════════════════════════════════════════════════
    
    @property
    def connectors(self) -> dict[str, ConnectorBinding]:
        """Direct access to connector bindings dictionary."""
        return self._connectors
    
    @property
    def toolkits(self) -> dict[str, ToolkitBinding]:
        """Direct access to toolkit bindings dictionary."""
        return self._toolkits
    
    @property
    def models(self) -> dict[str, ModelZooBinding]:
        """Direct access to model bindings dictionary."""
        return self._models
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Connector Bindings
    # ═══════════════════════════════════════════════════════════════════════════
    
    def bind_connector(
        self,
        domain: str,
        connector: ConnectorProtocol | None,
        connector_type: str = "unknown",
        *,
        config: dict[str, Any] | None = None,
        is_synthetic: bool = False,
    ) -> "BindingRegistry":
        """
        Bind a connector for a data domain.
        
        Args:
            domain: Data domain name.
            connector: Connector instance (or None for placeholder).
            connector_type: Connector type identifier.
            config: Connector configuration.
            is_synthetic: Whether this is a synthetic data source.
        
        Returns:
            Self for method chaining.
        """
        self._connectors[domain] = ConnectorBinding(
            domain=domain,
            connector=connector,
            connector_type=connector_type,
            config=config or {},
            is_synthetic=is_synthetic,
        )
        return self
    
    def has_connector(self, domain: str) -> bool:
        """Check if a connector is bound for a domain."""
        binding = self._connectors.get(domain)
        return binding is not None and binding.is_bound
    
    def get_connector(self, domain: str) -> ConnectorBinding | None:
        """Get the connector binding for a domain."""
        return self._connectors.get(domain)
    
    def list_connectors(self) -> list[str]:
        """List all bound connector domains."""
        return [d for d, b in self._connectors.items() if b.is_bound]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Toolkit Bindings
    # ═══════════════════════════════════════════════════════════════════════════
    
    def bind_toolkit(
        self,
        toolkit: str,
        method: str | None,
        instance: ToolkitMethodProtocol | Callable[..., Any] | None,
        *,
        package: str = "",
        version: str = "",
    ) -> "BindingRegistry":
        """
        Bind a toolkit method.
        
        Args:
            toolkit: Toolkit identifier.
            method: Method identifier (or None for entire toolkit).
            instance: Method instance or callable.
            package: Package name.
            version: Package version.
        
        Returns:
            Self for method chaining.
        """
        key = f"{toolkit}.{method}" if method else toolkit
        self._toolkits[key] = ToolkitBinding(
            toolkit=toolkit,
            method=method,
            instance=instance,
            package=package,
            version=version,
        )
        return self
    
    def has_toolkit(self, toolkit: str, method: str | None = None) -> bool:
        """Check if a toolkit (or method) is bound."""
        key = f"{toolkit}.{method}" if method else toolkit
        binding = self._toolkits.get(key)
        if binding and binding.is_bound:
            return True
        # Also check if toolkit root is bound
        if method:
            root_binding = self._toolkits.get(toolkit)
            return root_binding is not None and root_binding.is_bound
        return False
    
    def get_toolkit(self, toolkit: str, method: str | None = None) -> ToolkitBinding | None:
        """Get the toolkit binding."""
        key = f"{toolkit}.{method}" if method else toolkit
        return self._toolkits.get(key) or self._toolkits.get(toolkit)
    
    def list_toolkits(self) -> list[str]:
        """List all bound toolkit methods."""
        return [k for k, b in self._toolkits.items() if b.is_bound]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Model Zoo Bindings
    # ═══════════════════════════════════════════════════════════════════════════
    
    def bind_model(
        self,
        category: str,
        model_type: str,
        instance: ModelProtocol | Any | None,
        *,
        purpose: str = "",
        is_loaded: bool = False,
    ) -> "BindingRegistry":
        """
        Bind a model zoo model.
        
        Args:
            category: Model category.
            model_type: Model type.
            instance: Model instance.
            purpose: What the model is used for.
            is_loaded: Whether weights are loaded.
        
        Returns:
            Self for method chaining.
        """
        key = f"{category}.{model_type}"
        self._models[key] = ModelZooBinding(
            category=category,
            model_type=model_type,
            instance=instance,
            purpose=purpose,
            is_loaded=is_loaded,
        )
        return self
    
    def has_model(self, category: str, model_type: str) -> bool:
        """Check if a model is bound."""
        key = f"{category}.{model_type}"
        binding = self._models.get(key)
        return binding is not None and binding.is_bound
    
    def get_model(self, category: str, model_type: str) -> ModelZooBinding | None:
        """Get the model binding."""
        key = f"{category}.{model_type}"
        return self._models.get(key)
    
    def list_models(self) -> list[str]:
        """List all bound models."""
        return [k for k, b in self._models.items() if b.is_bound]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Bulk Operations
    # ═══════════════════════════════════════════════════════════════════════════
    
    def clear(self) -> None:
        """Clear all bindings."""
        self._connectors.clear()
        self._toolkits.clear()
        self._models.clear()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert all bindings to dictionary."""
        return {
            "connectors": {d: b.to_dict() for d, b in self._connectors.items()},
            "toolkits": {k: b.to_dict() for k, b in self._toolkits.items()},
            "models": {k: b.to_dict() for k, b in self._models.items()},
        }
    
    def summary(self) -> dict[str, list[str]]:
        """Get a summary of all bound dependencies."""
        return {
            "connectors": self.list_connectors(),
            "toolkits": self.list_toolkits(),
            "models": self.list_models(),
        }
    
    @classmethod
    def from_data_bundle(
        cls,
        bundle: Any,
        *,
        connector_type: str = "data_bundle",
    ) -> "BindingRegistry":
        """
        Create registry from a DataBundle.
        
        Creates synthetic connector bindings for each domain in the bundle.
        This is useful for TEST mode where data is already loaded.
        
        Args:
            bundle: DataBundle instance.
            connector_type: Type to assign to bindings.
        
        Returns:
            BindingRegistry with connector bindings.
        """
        registry = cls()
        
        # Extract domains from bundle
        if hasattr(bundle, "domains") and bundle.domains:
            for domain in bundle.domains:
                registry.bind_connector(
                    domain=domain,
                    connector=None,  # No connector, data already in bundle
                    connector_type=connector_type,
                    is_synthetic=True,
                )
        
        return registry
