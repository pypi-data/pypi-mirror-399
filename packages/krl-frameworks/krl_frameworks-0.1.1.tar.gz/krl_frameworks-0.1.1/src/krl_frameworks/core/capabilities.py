# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Capability Declaration Schema
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Capability Declaration for Framework Runtime Integration.

This module defines the CapabilityDeclaration schema that every framework
must satisfy. It enforces explicit dependency declaration at the framework
level, enabling the runtime to validate bindings before execution.

Terminology Clarification:
    - InferenceModel (Model Zoo): ML/DL models for prediction (BERT, LSTM, etc.)
    - Methodology (Framework Logic): Computation rules (Alkire-Foster, UNDP HDI)
    - DataShapeStrategy (Matrix): Statistical profile hints for data routing

Design Principles:
    1. Frameworks declare, they do not decide
    2. All dependencies are explicit, not discovered
    3. Missing dependencies cause hard failures, not fallbacks
    4. Capabilities are inspectable at registration time
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from krl_frameworks.core.bindings import BindingRegistry

__all__ = [
    "CapabilityDeclaration",
    "ConnectorRequirement",
    "ToolkitRequirement",
    "ModelZooRequirement",
    "CapabilityScope",
]


class CapabilityScope(str, Enum):
    """
    Scope of a capability requirement.
    
    REQUIRED: Framework cannot execute without this capability.
    OPTIONAL: Framework can degrade gracefully if unavailable.
    ENHANCING: Adds features but core functionality unaffected.
    """
    REQUIRED = "required"
    OPTIONAL = "optional"
    ENHANCING = "enhancing"


@dataclass(frozen=True)
class ConnectorRequirement:
    """
    Declares a connector dependency for a data domain.
    
    Attributes:
        domain: Data domain (e.g., "health", "education", "economic").
        connector_type: Preferred connector type (e.g., "fred", "census", "bls").
        scope: Whether this connector is required, optional, or enhancing.
        min_observations: Minimum required data points.
        temporal_coverage: Required years of historical data.
        fallback_connectors: Ordered list of fallback connector types.
    """
    domain: str
    connector_type: str | None = None
    scope: CapabilityScope = CapabilityScope.REQUIRED
    min_observations: int = 10
    temporal_coverage: int = 1  # years
    fallback_connectors: tuple[str, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "domain": self.domain,
            "connector_type": self.connector_type,
            "scope": self.scope.value,
            "min_observations": self.min_observations,
            "temporal_coverage": self.temporal_coverage,
            "fallback_connectors": list(self.fallback_connectors),
        }


@dataclass(frozen=True)
class ToolkitRequirement:
    """
    Declares a toolkit dependency (causal, geospatial, network).
    
    Attributes:
        toolkit: Toolkit identifier (e.g., "causal", "geospatial", "network").
        method: Specific method within toolkit (e.g., "did", "scm", "queen_weights").
        scope: Whether this toolkit method is required, optional, or enhancing.
        package: Python package name for installation hint.
    """
    toolkit: str
    method: str | None = None
    scope: CapabilityScope = CapabilityScope.REQUIRED
    package: str = ""
    
    def __post_init__(self) -> None:
        """Set default package name based on toolkit."""
        if not self.package:
            packages = {
                "causal": "krl-causal-policy-toolkit",
                "geospatial": "krl-geospatial-tools",
                "network": "krl-network-analysis",
            }
            object.__setattr__(self, "package", packages.get(self.toolkit, ""))
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "toolkit": self.toolkit,
            "method": self.method,
            "scope": self.scope.value,
            "package": self.package,
        }


@dataclass(frozen=True)
class ModelZooRequirement:
    """
    Declares a model zoo dependency for inference augmentation.
    
    Model zoo integration is ALWAYS optional for frameworks.
    Frameworks produce deterministic outputs; ML models enhance.
    
    Attributes:
        category: Model category (e.g., "econometric", "time_series", "nlp").
        model_type: Specific model (e.g., "sarima", "arima", "bert_base").
        purpose: What the model is used for (e.g., "forecasting", "classification").
        scope: Always OPTIONAL or ENHANCING, never REQUIRED.
    """
    category: str
    model_type: str
    purpose: str = ""
    scope: CapabilityScope = CapabilityScope.OPTIONAL
    
    def __post_init__(self) -> None:
        """Enforce that model zoo is never required."""
        if self.scope == CapabilityScope.REQUIRED:
            raise ValueError(
                "Model zoo capabilities cannot be REQUIRED. "
                "Frameworks must be deterministic without ML inference. "
                "Use OPTIONAL or ENHANCING scope."
            )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category,
            "model_type": self.model_type,
            "purpose": self.purpose,
            "scope": self.scope.value,
        }


@dataclass
class CapabilityDeclaration:
    """
    Complete capability declaration for a framework.
    
    This is the central artifact that binds a framework to the runtime
    integration spine. Every framework must declare its capabilities,
    and the runtime must validate them before allowing execution.
    
    Attributes:
        connectors: Required/optional data connector dependencies.
        toolkits: Required/optional toolkit dependencies.
        model_zoo: Optional model zoo dependencies.
        custom_validators: Additional validation callables.
    
    Example:
        >>> capabilities = CapabilityDeclaration(
        ...     connectors=[
        ...         ConnectorRequirement("health", scope=CapabilityScope.REQUIRED),
        ...         ConnectorRequirement("education", scope=CapabilityScope.REQUIRED),
        ...         ConnectorRequirement("housing", scope=CapabilityScope.REQUIRED),
        ...     ],
        ...     toolkits=[],  # MPI uses Alkire-Foster methodology, not causal toolkit
        ...     model_zoo=[
        ...         ModelZooRequirement("time_series", "arima", "trend forecasting"),
        ...     ],
        ... )
    """
    connectors: list[ConnectorRequirement] = field(default_factory=list)
    toolkits: list[ToolkitRequirement] = field(default_factory=list)
    model_zoo: list[ModelZooRequirement] = field(default_factory=list)
    custom_validators: list[Any] = field(default_factory=list)
    
    @property
    def required_connectors(self) -> list[ConnectorRequirement]:
        """Get connectors with REQUIRED scope."""
        return [c for c in self.connectors if c.scope == CapabilityScope.REQUIRED]
    
    @property
    def required_toolkits(self) -> list[ToolkitRequirement]:
        """Get toolkits with REQUIRED scope."""
        return [t for t in self.toolkits if t.scope == CapabilityScope.REQUIRED]
    
    @property
    def required_domains(self) -> list[str]:
        """Get domain names that are required."""
        return [c.domain for c in self.required_connectors]
    
    def validate(self, bindings: "BindingRegistry") -> list[str]:
        """
        Validate that all required capabilities are bound.
        
        Args:
            bindings: Current binding registry with resolved dependencies.
        
        Returns:
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []
        
        # Validate required connectors
        for connector in self.required_connectors:
            if not bindings.has_connector(connector.domain):
                errors.append(
                    f"Missing required connector for domain '{connector.domain}'. "
                    f"Expected: {connector.connector_type or 'any connector'}"
                )
        
        # Validate required toolkits
        for toolkit in self.required_toolkits:
            if not bindings.has_toolkit(toolkit.toolkit, toolkit.method):
                method_str = f".{toolkit.method}" if toolkit.method else ""
                errors.append(
                    f"Missing required toolkit '{toolkit.toolkit}{method_str}'. "
                    f"Install with: pip install {toolkit.package}"
                )
        
        # Run custom validators
        for validator in self.custom_validators:
            try:
                result = validator(bindings)
                if isinstance(result, str):
                    errors.append(result)
                elif isinstance(result, list):
                    errors.extend(result)
            except Exception as e:
                errors.append(f"Custom validator failed: {e}")
        
        return errors
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "connectors": [c.to_dict() for c in self.connectors],
            "toolkits": [t.to_dict() for t in self.toolkits],
            "model_zoo": [m.to_dict() for m in self.model_zoo],
        }
    
    @classmethod
    def empty(cls) -> "CapabilityDeclaration":
        """Create an empty capability declaration (no dependencies)."""
        return cls()
    
    @classmethod
    def from_domains(
        cls,
        required_domains: list[str],
        optional_domains: list[str] | None = None,
    ) -> "CapabilityDeclaration":
        """
        Create capability declaration from domain lists.
        
        Convenience factory for frameworks that only need data domains.
        
        Args:
            required_domains: List of required data domain names.
            optional_domains: List of optional data domain names.
        
        Returns:
            CapabilityDeclaration with connector requirements.
        """
        connectors = [
            ConnectorRequirement(domain, scope=CapabilityScope.REQUIRED)
            for domain in required_domains
        ]
        if optional_domains:
            connectors.extend(
                ConnectorRequirement(domain, scope=CapabilityScope.OPTIONAL)
                for domain in optional_domains
            )
        return cls(connectors=connectors)
