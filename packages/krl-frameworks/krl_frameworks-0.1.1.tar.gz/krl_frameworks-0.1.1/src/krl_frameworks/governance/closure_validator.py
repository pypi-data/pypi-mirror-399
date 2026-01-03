# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Capability Closure Validator
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Capability Closure Validation for Multi-Framework Pipelines.

When frameworks are chained in a pipeline, the closure validator ensures
that the combined capability requirements are satisfiable before execution
begins, preventing mid-pipeline failures.

Closure = Union of all framework CAPABILITIES with conflict detection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from krl_frameworks.core.capabilities import (
    CapabilityDeclaration,
    CapabilityScope,
    ConnectorRequirement,
    ToolkitRequirement,
    ModelZooRequirement,
)

if TYPE_CHECKING:
    from krl_frameworks.core.base import BaseMetaFramework

__all__ = [
    "CapabilityClosure",
    "ClosureValidator",
    "ClosureValidationError",
    "ClosureConflict",
]


@dataclass
class ClosureConflict:
    """
    A conflict detected between framework requirements.
    
    Attributes:
        requirement_name: Name of the conflicting requirement.
        framework_a: First framework name.
        framework_b: Second framework name.
        conflict_type: Type of conflict (version, scope, config).
        message: Human-readable conflict description.
    """
    requirement_name: str
    framework_a: str
    framework_b: str
    conflict_type: str
    message: str


class ClosureValidationError(Exception):
    """Raised when closure validation fails."""
    
    def __init__(self, message: str, conflicts: list[ClosureConflict]) -> None:
        self.conflicts = conflicts
        details = "\n".join(
            f"  - {c.requirement_name}: {c.message}" for c in conflicts
        )
        super().__init__(f"{message}\n{details}")


@dataclass
class CapabilityClosure:
    """
    Union of capabilities across multiple frameworks.
    
    Attributes:
        frameworks: List of framework names in the pipeline.
        connectors: Merged connector requirements.
        toolkits: Merged toolkit requirements.
        models: Merged model requirements.
        conflicts: Any detected conflicts.
    """
    frameworks: list[str] = field(default_factory=list)
    connectors: dict[str, ConnectorRequirement] = field(default_factory=dict)
    toolkits: dict[str, ToolkitRequirement] = field(default_factory=dict)
    models: dict[str, ModelZooRequirement] = field(default_factory=dict)
    conflicts: list[ClosureConflict] = field(default_factory=list)
    
    @property
    def has_conflicts(self) -> bool:
        """Whether the closure has any conflicts."""
        return len(self.conflicts) > 0
    
    @property
    def all_required_connectors(self) -> list[str]:
        """Get all REQUIRED connector types."""
        return [
            name for name, req in self.connectors.items()
            if req.scope == CapabilityScope.REQUIRED
        ]
    
    @property
    def all_required_toolkits(self) -> list[str]:
        """Get all REQUIRED toolkit names."""
        return [
            name for name, req in self.toolkits.items()
            if req.scope == CapabilityScope.REQUIRED
        ]
    
    @property
    def total_requirements(self) -> int:
        """Total number of unique requirements."""
        return len(self.connectors) + len(self.toolkits) + len(self.models)
    
    def to_capability_declaration(self) -> CapabilityDeclaration:
        """Convert closure to a single CapabilityDeclaration."""
        return CapabilityDeclaration(
            connectors=list(self.connectors.values()),
            toolkits=list(self.toolkits.values()),
            models=list(self.models.values()),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "frameworks": self.frameworks,
            "connectors": {
                name: {
                    "scope": req.scope.value,
                    "domains": req.domains,
                }
                for name, req in self.connectors.items()
            },
            "toolkits": {
                name: {
                    "scope": req.scope.value,
                }
                for name, req in self.toolkits.items()
            },
            "models": {
                name: {
                    "scope": req.scope.value,
                }
                for name, req in self.models.items()
            },
            "has_conflicts": self.has_conflicts,
            "conflicts": [
                {
                    "requirement": c.requirement_name,
                    "frameworks": [c.framework_a, c.framework_b],
                    "type": c.conflict_type,
                    "message": c.message,
                }
                for c in self.conflicts
            ],
        }


class ClosureValidator:
    """
    Validates capability closure for framework pipelines.
    
    When multiple frameworks are composed into a pipeline, the ClosureValidator
    computes the union of all capability requirements and detects conflicts
    before execution begins.
    
    Usage:
        >>> validator = ClosureValidator()
        >>> closure = validator.compute_closure([mpi, gini, theil])
        >>> if closure.has_conflicts:
        ...     raise ClosureValidationError("Conflicts", closure.conflicts)
        >>> 
        >>> # Validate against available bindings
        >>> validator.validate(closure, user_tier="professional")
    
    Conflict Types:
        - version: Incompatible version requirements
        - scope: Conflicting scope (rare, logged as warning)
        - config: Incompatible configuration requirements
    """
    
    def compute_closure(
        self,
        frameworks: list["BaseMetaFramework"] | list[type["BaseMetaFramework"]],
    ) -> CapabilityClosure:
        """
        Compute capability closure from multiple frameworks.
        
        Args:
            frameworks: List of framework instances or classes.
        
        Returns:
            Merged CapabilityClosure with conflict detection.
        """
        closure = CapabilityClosure()
        framework_sources: dict[str, str] = {}  # requirement_name → first framework
        
        for framework in frameworks:
            # Get framework name and capabilities
            if isinstance(framework, type):
                name = framework.__name__
                capabilities = getattr(framework, "CAPABILITIES", None)
            else:
                name = framework.__class__.__name__
                capabilities = framework.capabilities
            
            closure.frameworks.append(name)
            
            if not capabilities:
                continue
            
            # Merge connector requirements
            for req in capabilities.connectors:
                self._merge_connector(
                    closure=closure,
                    requirement=req,
                    framework_name=name,
                    framework_sources=framework_sources,
                )
            
            # Merge toolkit requirements
            for req in capabilities.toolkits:
                self._merge_toolkit(
                    closure=closure,
                    requirement=req,
                    framework_name=name,
                    framework_sources=framework_sources,
                )
            
            # Merge model requirements
            for req in capabilities.models:
                self._merge_model(
                    closure=closure,
                    requirement=req,
                    framework_name=name,
                    framework_sources=framework_sources,
                )
        
        return closure
    
    def _merge_connector(
        self,
        closure: CapabilityClosure,
        requirement: ConnectorRequirement,
        framework_name: str,
        framework_sources: dict[str, str],
    ) -> None:
        """Merge a connector requirement into the closure."""
        key = requirement.connector_type
        
        if key in closure.connectors:
            existing = closure.connectors[key]
            source_framework = framework_sources.get(key, framework_name)
            
            # Check for version conflict
            if (
                requirement.version
                and existing.version
                and requirement.version != existing.version
            ):
                closure.conflicts.append(
                    ClosureConflict(
                        requirement_name=key,
                        framework_a=source_framework,
                        framework_b=framework_name,
                        conflict_type="version",
                        message=(
                            f"Version conflict: {source_framework} requires "
                            f"'{existing.version}' but {framework_name} requires "
                            f"'{requirement.version}'"
                        ),
                    )
                )
            
            # Upgrade scope if new is stricter (REQUIRED > OPTIONAL > ENHANCING)
            if self._scope_priority(requirement.scope) > self._scope_priority(existing.scope):
                closure.connectors[key] = requirement
                framework_sources[key] = framework_name
            
            # Merge domains
            existing_domains = set(existing.domains)
            new_domains = set(requirement.domains)
            if existing_domains != new_domains:
                # Create merged requirement with combined domains
                merged = ConnectorRequirement(
                    connector_type=key,
                    scope=closure.connectors[key].scope,
                    domains=list(existing_domains | new_domains),
                    version=closure.connectors[key].version,
                )
                closure.connectors[key] = merged
        else:
            closure.connectors[key] = requirement
            framework_sources[key] = framework_name
    
    def _merge_toolkit(
        self,
        closure: CapabilityClosure,
        requirement: ToolkitRequirement,
        framework_name: str,
        framework_sources: dict[str, str],
    ) -> None:
        """Merge a toolkit requirement into the closure."""
        key = requirement.toolkit_name
        
        if key in closure.toolkits:
            existing = closure.toolkits[key]
            source_framework = framework_sources.get(key, framework_name)
            
            # Check for version conflict
            if (
                requirement.version
                and existing.version
                and requirement.version != existing.version
            ):
                closure.conflicts.append(
                    ClosureConflict(
                        requirement_name=key,
                        framework_a=source_framework,
                        framework_b=framework_name,
                        conflict_type="version",
                        message=(
                            f"Version conflict: {source_framework} requires "
                            f"'{existing.version}' but {framework_name} requires "
                            f"'{requirement.version}'"
                        ),
                    )
                )
            
            # Upgrade scope if stricter
            if self._scope_priority(requirement.scope) > self._scope_priority(existing.scope):
                closure.toolkits[key] = requirement
                framework_sources[key] = framework_name
        else:
            closure.toolkits[key] = requirement
            framework_sources[key] = framework_name
    
    def _merge_model(
        self,
        closure: CapabilityClosure,
        requirement: ModelZooRequirement,
        framework_name: str,
        framework_sources: dict[str, str],
    ) -> None:
        """Merge a model requirement into the closure."""
        key = requirement.model_name
        
        if key in closure.models:
            existing = closure.models[key]
            source_framework = framework_sources.get(key, framework_name)
            
            # Check for version conflict
            if (
                requirement.version
                and existing.version
                and requirement.version != existing.version
            ):
                closure.conflicts.append(
                    ClosureConflict(
                        requirement_name=key,
                        framework_a=source_framework,
                        framework_b=framework_name,
                        conflict_type="version",
                        message=(
                            f"Version conflict: {source_framework} requires "
                            f"'{existing.version}' but {framework_name} requires "
                            f"'{requirement.version}'"
                        ),
                    )
                )
            
            # Upgrade scope if stricter
            if self._scope_priority(requirement.scope) > self._scope_priority(existing.scope):
                closure.models[key] = requirement
                framework_sources[key] = framework_name
        else:
            closure.models[key] = requirement
            framework_sources[key] = framework_name
    
    def _scope_priority(self, scope: CapabilityScope) -> int:
        """Get priority for scope (higher = stricter)."""
        return {
            CapabilityScope.ENHANCING: 0,
            CapabilityScope.OPTIONAL: 1,
            CapabilityScope.REQUIRED: 2,
        }.get(scope, 0)
    
    def validate(
        self,
        closure: CapabilityClosure,
        user_tier: str,
        raise_on_conflict: bool = True,
    ) -> bool:
        """
        Validate that closure can be satisfied.
        
        Args:
            closure: The capability closure to validate.
            user_tier: User's subscription tier.
            raise_on_conflict: Whether to raise on conflicts.
        
        Returns:
            True if valid.
        
        Raises:
            ClosureValidationError: If conflicts and raise_on_conflict.
        """
        if closure.has_conflicts and raise_on_conflict:
            raise ClosureValidationError(
                f"Pipeline closure has {len(closure.conflicts)} conflicts",
                closure.conflicts,
            )
        
        return not closure.has_conflicts
    
    def validate_with_registry(
        self,
        closure: CapabilityClosure,
        user_tier: str,
    ) -> tuple[bool, list[str]]:
        """
        Validate closure against connector registry.
        
        Args:
            closure: The capability closure to validate.
            user_tier: User's subscription tier.
        
        Returns:
            Tuple of (is_valid, list of missing requirements).
        """
        from krl_frameworks.governance.connector_registry import get_global_connector_registry
        
        registry = get_global_connector_registry()
        missing: list[str] = []
        
        for name, req in closure.connectors.items():
            if req.scope != CapabilityScope.REQUIRED:
                continue
            
            if not registry.has_connector(name):
                # Try domain fallback
                found = False
                for domain in req.domains:
                    if registry.get_factory_for_domain(domain, user_tier):
                        found = True
                        break
                if not found:
                    missing.append(f"connector:{name}")
        
        return len(missing) == 0, missing
