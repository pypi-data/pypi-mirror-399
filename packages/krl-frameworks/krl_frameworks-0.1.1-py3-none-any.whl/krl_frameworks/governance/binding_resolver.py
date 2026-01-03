# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Binding Resolver
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Automatic Binding Resolution for Runtime Governance.

The BindingResolver bridges CapabilityDeclaration → BindingRegistry by
automatically resolving declared requirements to concrete factory bindings.

Resolution Strategy:
    1. Parse CAPABILITIES from framework class
    2. For each ConnectorRequirement:
       - Try registered factory for exact connector type
       - Fall back to domain-based factory lookup
       - Fail if REQUIRED and no factory available
    3. For each ToolkitRequirement:
       - Look up in toolkit registry (analogous to connector registry)
    4. For each ModelZooRequirement:
       - Look up in model zoo registry (optional, never required)

Design Principles:
    - Fail-fast on REQUIRED capabilities (no silent fallback)
    - Warn on missing OPTIONAL capabilities (non-blocking)
    - Log all resolution attempts for auditability
    - Respect explicit bindings (no override)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from krl_frameworks.core.bindings import BindingRegistry
from krl_frameworks.core.capabilities import (
    CapabilityDeclaration,
    CapabilityScope,
    ConnectorRequirement,
    ModelZooRequirement,
    ToolkitRequirement,
)
from krl_frameworks.core.execution_context import ExecutionMode
from krl_frameworks.governance.connector_registry import (
    ConnectorFactoryRegistry,
    ConnectorNotFoundError,
    TierAccessDeniedError,
    get_global_connector_registry,
)

if TYPE_CHECKING:
    from krl_frameworks.core.execution_context import ExecutionContext

__all__ = [
    "BindingResolver",
    "ResolutionResult",
    "ResolutionFailure",
    "BindingResolutionError",
    "get_binding_resolver",
]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Exceptions
# ════════════════════════════════════════════════════════════════════════════════


class BindingResolutionError(Exception):
    """Raised when required bindings cannot be resolved."""
    
    def __init__(
        self,
        message: str,
        failures: list["ResolutionFailure"],
    ) -> None:
        self.failures = failures
        details = "\n".join(f"  - {f.requirement_name}: {f.reason}" for f in failures)
        super().__init__(f"{message}\n{details}")


# ════════════════════════════════════════════════════════════════════════════════
# Resolution Results
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ResolutionFailure:
    """
    Represents a failed resolution attempt.
    
    Attributes:
        requirement_name: Name of the requirement that failed.
        requirement_type: Type of requirement (connector, toolkit, model).
        scope: Capability scope (REQUIRED, OPTIONAL, ENHANCING).
        reason: Human-readable failure reason.
        exception: Original exception if any.
    """
    requirement_name: str
    requirement_type: str
    scope: CapabilityScope
    reason: str
    exception: Exception | None = None
    
    @property
    def is_fatal(self) -> bool:
        """Whether this failure is fatal (REQUIRED scope)."""
        return self.scope == CapabilityScope.REQUIRED


@dataclass
class ResolutionResult:
    """
    Complete result of a binding resolution attempt.
    
    Attributes:
        bindings: The resolved BindingRegistry.
        resolved: List of successfully resolved requirement names.
        skipped: List of explicitly bound requirements (not resolved).
        failures: List of failed resolution attempts.
        warnings: List of warning messages.
    """
    bindings: BindingRegistry
    resolved: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failures: list[ResolutionFailure] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Whether resolution succeeded (no fatal failures)."""
        return not any(f.is_fatal for f in self.failures)
    
    @property
    def fatal_failures(self) -> list[ResolutionFailure]:
        """Get only fatal failures."""
        return [f for f in self.failures if f.is_fatal]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for audit logging."""
        return {
            "success": self.success,
            "resolved_count": len(self.resolved),
            "skipped_count": len(self.skipped),
            "failure_count": len(self.failures),
            "fatal_failure_count": len(self.fatal_failures),
            "resolved": self.resolved,
            "skipped": self.skipped,
            "failures": [
                {
                    "name": f.requirement_name,
                    "type": f.requirement_type,
                    "scope": f.scope.value,
                    "reason": f.reason,
                }
                for f in self.failures
            ],
            "warnings": self.warnings,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Binding Resolver
# ════════════════════════════════════════════════════════════════════════════════


class BindingResolver:
    """
    Automatic binding resolver for framework capabilities.
    
    The resolver takes a CapabilityDeclaration and produces a BindingRegistry
    by looking up registered factories in the connector/toolkit/model registries.
    
    Resolution follows these rules:
        1. Explicit bindings are never overwritten
        2. REQUIRED capabilities must resolve or resolution fails
        3. OPTIONAL capabilities log warnings if unresolved
        4. ENHANCING capabilities are silently skipped if unresolved
        5. In LIVE mode, all REQUIRED must resolve
        6. In TEST mode, failures are collected but non-fatal
    
    Example:
        >>> resolver = BindingResolver()
        >>> result = resolver.resolve(
        ...     capabilities=MyFramework.CAPABILITIES,
        ...     user_tier="professional",
        ...     mode=ExecutionMode.LIVE,
        ... )
        >>> if result.success:
        ...     # Use result.bindings
        ...     pass
        >>> else:
        ...     raise BindingResolutionError("Failed", result.fatal_failures)
    """
    
    def __init__(
        self,
        connector_registry: ConnectorFactoryRegistry | None = None,
        toolkit_registry: Any | None = None,  # Future: ToolkitFactoryRegistry
        model_registry: Any | None = None,    # Future: ModelZooRegistry
    ) -> None:
        """
        Initialize the resolver with registries.
        
        Args:
            connector_registry: Connector factory registry.
            toolkit_registry: Toolkit factory registry (future).
            model_registry: Model zoo registry (future).
        """
        self._connector_registry = connector_registry
        self._toolkit_registry = toolkit_registry
        self._model_registry = model_registry
    
    @property
    def connector_registry(self) -> ConnectorFactoryRegistry:
        """Get connector registry (lazy initialization)."""
        if self._connector_registry is None:
            self._connector_registry = get_global_connector_registry()
        return self._connector_registry
    
    def resolve(
        self,
        capabilities: CapabilityDeclaration,
        user_tier: str = "community",
        mode: ExecutionMode = ExecutionMode.LIVE,
        existing_bindings: BindingRegistry | None = None,
        connector_config: dict[str, dict[str, Any]] | None = None,
    ) -> ResolutionResult:
        """
        Resolve capabilities to bindings.
        
        Args:
            capabilities: The capability declaration to resolve.
            user_tier: User's subscription tier.
            mode: Execution mode (LIVE/TEST/DEBUG).
            existing_bindings: Pre-existing bindings to respect.
            connector_config: Configuration per connector type.
        
        Returns:
            ResolutionResult with bindings and status.
        
        Raises:
            BindingResolutionError: In LIVE mode if REQUIRED capabilities fail.
        """
        bindings = existing_bindings or BindingRegistry()
        connector_config = connector_config or {}
        
        result = ResolutionResult(bindings=bindings)
        
        # Resolve connectors
        for requirement in capabilities.connectors:
            self._resolve_connector(
                requirement=requirement,
                bindings=bindings,
                user_tier=user_tier,
                config=connector_config.get(requirement.connector_type or "", {}),
                result=result,
            )
        
        # Resolve toolkits
        for requirement in capabilities.toolkits:
            self._resolve_toolkit(
                requirement=requirement,
                bindings=bindings,
                user_tier=user_tier,
                result=result,
            )
        
        # Resolve model zoo
        for requirement in capabilities.model_zoo:
            self._resolve_model(
                requirement=requirement,
                bindings=bindings,
                user_tier=user_tier,
                result=result,
            )
        
        # In LIVE mode, any fatal failure is an exception
        if mode == ExecutionMode.LIVE and result.fatal_failures:
            raise BindingResolutionError(
                "Required capabilities could not be resolved in LIVE mode",
                result.fatal_failures,
            )
        
        # Log warnings for non-fatal failures
        for failure in result.failures:
            if not failure.is_fatal:
                logger.warning(
                    "Optional capability '%s' not resolved: %s",
                    failure.requirement_name,
                    failure.reason,
                )
                result.warnings.append(
                    f"Optional '{failure.requirement_name}' not resolved: {failure.reason}"
                )
        
        return result
    
    def _resolve_connector(
        self,
        requirement: ConnectorRequirement,
        bindings: BindingRegistry,
        user_tier: str,
        config: dict[str, Any],
        result: ResolutionResult,
    ) -> None:
        """Resolve a single connector requirement."""
        # ConnectorRequirement has 'domain' as primary identifier
        # and 'connector_type' as preferred factory type
        domain = requirement.domain
        preferred_connector = requirement.connector_type
        
        # Check if domain already bound
        if domain in bindings.connectors:
            result.skipped.append(domain)
            logger.debug(
                "Domain '%s' already bound, skipping resolution",
                domain,
            )
            return
        
        try:
            # Try preferred connector type first, or use domain as fallback
            lookup_type = preferred_connector or domain
            
            factory = self.connector_registry.get_factory(
                connector_type=lookup_type,
                user_tier=user_tier,
            )
            
            # Create connector instance
            connector = factory.create(config)
            
            # Add to bindings using BindingRegistry's method
            bindings.bind_connector(
                domain=domain,
                connector=connector,
                connector_type=factory.connector_type,
                config=config,
            )
            
            result.resolved.append(domain)
            logger.info(
                "Resolved connector for domain '%s' using '%s' for tier '%s'",
                domain,
                factory.connector_type,
                user_tier,
            )
            
        except ConnectorNotFoundError as e:
            # Try domain-based fallback using fallback_connectors
            fallback_types = list(requirement.fallback_connectors) if requirement.fallback_connectors else []
            # Also try domain itself
            fallback_types.append(domain)
            
            for fallback_type in fallback_types:
                fallback = self.connector_registry.get_factory_for_domain(
                    domain=fallback_type,
                    user_tier=user_tier,
                )
                if fallback:
                    try:
                        connector = fallback.create(config)
                        bindings.bind_connector(
                            domain=domain,
                            connector=connector,
                            connector_type=fallback.connector_type,
                            config=config,
                        )
                        
                        result.resolved.append(domain)
                        result.warnings.append(
                            f"Domain '{domain}' resolved via fallback using '{fallback.connector_type}'"
                        )
                        logger.info(
                            "Domain '%s' resolved via fallback using '%s'",
                            domain,
                            fallback.connector_type,
                        )
                        return
                    except Exception as ex:
                        logger.debug(
                            "Domain fallback for '%s' failed: %s",
                            domain,
                            ex,
                        )
            
            # No fallback succeeded
            result.failures.append(
                ResolutionFailure(
                    requirement_name=domain,
                    requirement_type="connector",
                    scope=requirement.scope,
                    reason=str(e),
                    exception=e,
                )
            )
            
        except TierAccessDeniedError as e:
            result.failures.append(
                ResolutionFailure(
                    requirement_name=domain,
                    requirement_type="connector",
                    scope=requirement.scope,
                    reason=str(e),
                    exception=e,
                )
            )
            
        except Exception as e:
            result.failures.append(
                ResolutionFailure(
                    requirement_name=domain,
                    requirement_type="connector",
                    scope=requirement.scope,
                    reason=f"Factory creation failed: {e}",
                    exception=e,
                )
            )
    
    def _resolve_toolkit(
        self,
        requirement: ToolkitRequirement,
        bindings: BindingRegistry,
        user_tier: str,
        result: ResolutionResult,
    ) -> None:
        """Resolve a single toolkit requirement."""
        toolkit_name = requirement.toolkit_name
        
        # Check if already bound
        if toolkit_name in bindings.toolkits:
            result.skipped.append(toolkit_name)
            return
        
        # Future: Implement toolkit registry lookup
        # For now, try direct import
        try:
            toolkit = self._import_toolkit(toolkit_name, requirement.module_path)
            
            # Parse toolkit.method format
            parts = toolkit_name.split(".", 1)
            toolkit_id = parts[0]
            method_id = parts[1] if len(parts) > 1 else None
            
            bindings.bind_toolkit(
                toolkit=toolkit_id,
                method=method_id,
                instance=toolkit,
                version=requirement.version or "",
            )
            
            result.resolved.append(toolkit_name)
            logger.info("Resolved toolkit '%s'", toolkit_name)
            
        except ImportError as e:
            result.failures.append(
                ResolutionFailure(
                    requirement_name=toolkit_name,
                    requirement_type="toolkit",
                    scope=requirement.scope,
                    reason=f"Toolkit not installed: {e}",
                    exception=e,
                )
            )
        except Exception as e:
            result.failures.append(
                ResolutionFailure(
                    requirement_name=toolkit_name,
                    requirement_type="toolkit",
                    scope=requirement.scope,
                    reason=f"Toolkit resolution failed: {e}",
                    exception=e,
                )
            )
    
    def _resolve_model(
        self,
        requirement: ModelZooRequirement,
        bindings: BindingRegistry,
        user_tier: str,
        result: ResolutionResult,
    ) -> None:
        """Resolve a single model zoo requirement."""
        model_name = requirement.model_name
        
        # Check if already bound
        if model_name in bindings.models:
            result.skipped.append(model_name)
            return
        
        # Future: Implement model zoo registry lookup
        # For now, try direct import from krl-model-zoo
        try:
            model = self._import_model(model_name, requirement.module_path)
            
            # Parse category.model_type format
            parts = model_name.split(".", 1)
            category = parts[0]
            model_type = parts[1] if len(parts) > 1 else "default"
            
            bindings.bind_model(
                category=category,
                model_type=model_type,
                instance=model,
            )
            
            result.resolved.append(model_name)
            logger.info("Resolved model '%s'", model_name)
            
        except ImportError as e:
            # Model Zoo is always optional, so this is never fatal
            result.failures.append(
                ResolutionFailure(
                    requirement_name=model_name,
                    requirement_type="model",
                    scope=requirement.scope,  # Always OPTIONAL or ENHANCING
                    reason=f"Model not available: {e}",
                    exception=e,
                )
            )
        except Exception as e:
            result.failures.append(
                ResolutionFailure(
                    requirement_name=model_name,
                    requirement_type="model",
                    scope=requirement.scope,
                    reason=f"Model resolution failed: {e}",
                    exception=e,
                )
            )
    
    def _import_toolkit(self, name: str, module_path: str | None) -> Any:
        """Import a toolkit by name or module path."""
        if module_path:
            import importlib
            module = importlib.import_module(module_path)
            return module
        
        # Try standard toolkit locations
        toolkit_modules = [
            f"krl_geospatial_tools.{name}",
            f"krl_network_analysis.{name}",
            f"krl_causal_policy_toolkit.{name}",
        ]
        
        import importlib
        for mod_path in toolkit_modules:
            try:
                return importlib.import_module(mod_path)
            except ImportError:
                continue
        
        raise ImportError(f"Toolkit '{name}' not found in standard locations")
    
    def _import_model(self, name: str, module_path: str | None) -> Any:
        """Import a model by name or module path."""
        if module_path:
            import importlib
            module = importlib.import_module(module_path)
            return module
        
        # Parse model category (e.g., "time_series.arima" → "time_series", "arima")
        parts = name.split(".")
        if len(parts) == 2:
            category, model = parts
            model_modules = [
                f"krl_model_zoo.{category}.{model}",
                f"krl_model_zoo_pro.{category}.{model}",
            ]
        else:
            model_modules = [
                f"krl_model_zoo.{name}",
                f"krl_model_zoo_pro.{name}",
            ]
        
        import importlib
        for mod_path in model_modules:
            try:
                return importlib.import_module(mod_path)
            except ImportError:
                continue
        
        raise ImportError(f"Model '{name}' not found in model zoo")


# ════════════════════════════════════════════════════════════════════════════════
# Global Resolver
# ════════════════════════════════════════════════════════════════════════════════

_global_resolver: BindingResolver | None = None


def get_binding_resolver() -> BindingResolver:
    """Get the global binding resolver."""
    global _global_resolver
    if _global_resolver is None:
        _global_resolver = BindingResolver()
    return _global_resolver
