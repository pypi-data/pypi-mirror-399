# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Framework Registry
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Framework Registry for peer framework discovery and management.

This module provides the FrameworkRegistry class, which manages
registration, discovery, and instantiation of all meta-frameworks
across the 6 vertical layers.

Key Design Principles:
- All frameworks are registered as equals (peer architecture)
- REMSOM has no special status over other meta-frameworks
- Discovery supports filtering by layer, tier, and tags
- Lazy instantiation with optional dependency injection
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from krl_frameworks.core.base import (
    BaseMetaFramework,
    FrameworkMetadata,
    VerticalLayer,
)
from krl_frameworks.core.config import FrameworkConfig
from krl_frameworks.core.exceptions import (
    DuplicateFrameworkError,
    FrameworkNotFoundError,
    TierAccessError,
)
from krl_frameworks.core.tier import Tier, get_current_tier

if TYPE_CHECKING:
    pass


# Type variable for framework classes
F = TypeVar("F", bound=BaseMetaFramework)


# ════════════════════════════════════════════════════════════════════════════════
# Registry Entry
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class RegistryEntry:
    """
    Entry in the framework registry.
    
    Contains the framework class and metadata needed for discovery
    and instantiation.
    
    Attributes:
        framework_class: The framework class (not instance).
        metadata: Framework metadata extracted from class.
        factory: Optional custom factory function.
        registered_at: When this entry was registered.
        enabled: Whether the framework is currently enabled.
    """
    
    framework_class: type[BaseMetaFramework]
    metadata: FrameworkMetadata
    factory: Callable[..., BaseMetaFramework] | None = None
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    enabled: bool = True
    
    @property
    def slug(self) -> str:
        """Framework unique identifier."""
        return self.metadata.slug
    
    @property
    def layer(self) -> VerticalLayer:
        """Vertical layer this framework belongs to."""
        return self.metadata.layer
    
    @property
    def tier(self) -> Tier:
        """Minimum tier required for access."""
        return self.metadata.tier
    
    def create_instance(
        self,
        config: FrameworkConfig | None = None,
        **kwargs: Any,
    ) -> BaseMetaFramework:
        """
        Create a framework instance.
        
        Uses custom factory if provided, otherwise direct instantiation.
        
        Note: Frameworks may use different parameter names for config
        (e.g., 'mpi_config', 'params', 'config'). This method inspects
        the constructor signature and passes config appropriately.
        
        Args:
            config: Optional framework configuration.
            **kwargs: Additional arguments passed to constructor.
        
        Returns:
            New framework instance.
        """
        import inspect
        
        if self.factory is not None:
            return self.factory(config=config, **kwargs)
        
        # Inspect constructor to find the config parameter name
        sig = inspect.signature(self.framework_class.__init__)
        params = list(sig.parameters.keys())
        
        # Check if the constructor accepts 'config' parameter
        if 'config' in params:
            return self.framework_class(config=config, **kwargs)
        
        # Look for framework-specific config params (e.g., mpi_config, params)
        config_param_suffixes = ['_config', 'config', '_params', 'params']
        for param_name in params:
            if param_name == 'self':
                continue
            for suffix in config_param_suffixes:
                if param_name.endswith(suffix) or param_name == suffix:
                    # Pass config to the framework-specific parameter
                    if config is not None:
                        return self.framework_class(**{param_name: config}, **kwargs)
                    break
        
        # No config parameter found - instantiate without config
        return self.framework_class(**kwargs)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "slug": self.slug,
            "metadata": self.metadata.to_dict(),
            "registered_at": self.registered_at.isoformat(),
            "enabled": self.enabled,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Framework Registry
# ════════════════════════════════════════════════════════════════════════════════


class FrameworkRegistry:
    """
    Central registry for all KRL meta-frameworks.
    
    The registry provides:
    - Framework registration and discovery
    - Tier-based access control
    - Layer and tag filtering
    - Lazy instantiation with configuration
    
    This implements the "peer architecture" where all frameworks
    (including REMSOM) are treated as equals with no hierarchy.
    
    Example:
        >>> registry = FrameworkRegistry()
        >>> registry.register(MPIFramework)
        >>> registry.register(HDIFramework)
        >>> registry.register(REMSOMFramework)
        
        >>> # List all frameworks in Layer 1
        >>> for fw in registry.list_by_layer(VerticalLayer.SOCIOECONOMIC_ACADEMIC):
        ...     print(fw.name)
        
        >>> # Get a specific framework
        >>> mpi = registry.get("mpi")
        >>> mpi.fit(data)
    """
    
    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._entries: dict[str, RegistryEntry] = {}
        self._logger = logging.getLogger("krl_frameworks.registry")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Registration
    # ═══════════════════════════════════════════════════════════════════════════
    
    def register(
        self,
        framework_class: type[BaseMetaFramework],
        *,
        factory: Callable[..., BaseMetaFramework] | None = None,
        overwrite: bool = False,
    ) -> None:
        """
        Register a framework class with the registry.
        
        The framework class must have a METADATA class attribute
        defining its FrameworkMetadata.
        
        Args:
            framework_class: The framework class to register.
            factory: Optional custom factory function for instantiation.
            overwrite: If True, overwrite existing registration.
        
        Raises:
            DuplicateFrameworkError: If slug already registered and not overwrite.
            ValueError: If framework class lacks METADATA.
        """
        # Validate metadata exists
        if not hasattr(framework_class, "METADATA"):
            raise ValueError(
                f"Framework class {framework_class.__name__} must have METADATA attribute"
            )
        
        metadata = framework_class.METADATA
        slug = metadata.slug
        
        # Check for duplicate
        if slug in self._entries and not overwrite:
            raise DuplicateFrameworkError(slug)
        
        # ═══════════════════════════════════════════════════════════════════════
        # GOVERNANCE VALIDATION: Validate dashboard_spec at registration time
        # ═══════════════════════════════════════════════════════════════════════
        # This is constitutional enforcement - if a framework violates governance
        # constraints, it CANNOT be registered. This prevents analytical malpractice
        # at the source rather than at runtime.
        self._validate_dashboard_spec(framework_class, slug)
        
        # Create entry
        entry = RegistryEntry(
            framework_class=framework_class,
            metadata=metadata,
            factory=factory,
        )
        
        self._entries[slug] = entry
        self._logger.info(
            "Registered framework: %s (layer=%s, tier=%s)",
            slug,
            metadata.layer.abbreviation,
            metadata.tier.name,
        )
    
    def register_decorator(
        self,
        *,
        factory: Callable[..., BaseMetaFramework] | None = None,
    ) -> Callable[[type[F]], type[F]]:
        """
        Decorator for registering framework classes.
        
        Example:
            >>> @registry.register_decorator()
            ... class MyFramework(BaseMetaFramework):
            ...     METADATA = FrameworkMetadata(slug="my-fw", ...)
        
        Args:
            factory: Optional custom factory function.
        
        Returns:
            Class decorator.
        """
        def decorator(cls: type[F]) -> type[F]:
            self.register(cls, factory=factory)
            return cls
        return decorator
    
    def unregister(self, slug: str) -> bool:
        """
        Remove a framework from the registry.
        
        Args:
            slug: Framework slug to remove.
        
        Returns:
            True if removed, False if not found.
        """
        if slug in self._entries:
            del self._entries[slug]
            self._logger.info("Unregistered framework: %s", slug)
            return True
        return False
    
    def enable(self, slug: str) -> None:
        """Enable a disabled framework."""
        if slug in self._entries:
            self._entries[slug].enabled = True
    
    def disable(self, slug: str) -> None:
        """Disable a framework (won't appear in listings)."""
        if slug in self._entries:
            self._entries[slug].enabled = False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Governance Validation
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _validate_dashboard_spec(
        self,
        framework_class: type[BaseMetaFramework],
        slug: str,
    ) -> None:
        """
        Validate framework's dashboard_spec against governance constraints.
        
        This is CONSTITUTIONAL ENFORCEMENT at registration time.
        If the dashboard_spec violates governance rules (e.g., TIMESERIES for
        cross-sectional frameworks, wrong view type for result class), the
        framework CANNOT be registered.
        
        This prevents analytical malpractice at the source.
        
        Args:
            framework_class: The framework class being registered.
            slug: Framework slug (for error messages).
        
        Raises:
            ValueError: If governance violations are found.
        """
        # Skip validation if no dashboard_spec method
        if not hasattr(framework_class, "dashboard_spec"):
            self._logger.debug(
                "Framework %s has no dashboard_spec, skipping governance validation",
                slug,
            )
            return
        
        try:
            # Get the dashboard spec (it's a classmethod)
            spec = framework_class.dashboard_spec()
            
            if spec is None:
                return
            
            # Validate governance constraints
            errors = spec.validate_governance()
            
            if errors:
                error_list = "\n  - ".join(errors)
                raise ValueError(
                    f"Framework '{slug}' FAILED governance validation. "
                    f"Dashboard spec violates constraints:\n  - {error_list}\n\n"
                    f"FIX: Update the dashboard_spec() to comply with "
                    f"RESULT_CLASS_RENDERER_CONSTRAINTS and SemanticConstraints."
                )
            
            self._logger.info(
                "Framework %s passed governance validation (%d views validated)",
                slug,
                len(spec.output_views),
            )
            
        except Exception as e:
            if "FAILED governance validation" in str(e):
                # Re-raise governance violations
                raise
            # Log but don't fail on other errors (e.g., spec generation issues)
            self._logger.warning(
                "Could not validate dashboard_spec for %s: %s",
                slug,
                str(e),
            )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Discovery
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_entry(self, slug: str) -> RegistryEntry:
        """
        Get a registry entry by slug.
        
        Args:
            slug: Framework unique identifier.
        
        Returns:
            RegistryEntry for the framework.
        
        Raises:
            FrameworkNotFoundError: If slug not found.
        """
        if slug not in self._entries:
            raise FrameworkNotFoundError(
                slug,
                available_frameworks=list(self._entries.keys()),
            )
        return self._entries[slug]
    
    def get(
        self,
        slug: str,
        *,
        config: FrameworkConfig | None = None,
        check_tier: bool = True,
        **kwargs: Any,
    ) -> BaseMetaFramework:
        """
        Get an instantiated framework by slug.
        
        This creates a new instance of the framework with the
        provided configuration.
        
        Args:
            slug: Framework unique identifier.
            config: Optional framework configuration.
            check_tier: Whether to check tier access (default True).
            **kwargs: Additional arguments passed to constructor.
        
        Returns:
            New framework instance.
        
        Raises:
            FrameworkNotFoundError: If slug not found.
            TierAccessError: If current tier lacks access and check_tier=True.
        """
        entry = self.get_entry(slug)
        
        # Check tier access
        if check_tier:
            current_tier = get_current_tier()
            if not current_tier.can_access(entry.tier):
                raise TierAccessError(
                    f"Framework '{slug}' requires {entry.tier.display_name} tier",
                    required_tier=entry.tier.name,
                    current_tier=current_tier.name,
                    framework_slug=slug,
                )
        
        return entry.create_instance(config=config, **kwargs)
    
    def has(self, slug: str) -> bool:
        """Check if a framework is registered."""
        return slug in self._entries
    
    def __contains__(self, slug: str) -> bool:
        """Support `slug in registry` syntax."""
        return self.has(slug)
    
    def __getitem__(self, slug: str) -> BaseMetaFramework:
        """Support `registry[slug]` syntax."""
        return self.get(slug)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Listing & Filtering
    # ═══════════════════════════════════════════════════════════════════════════
    
    def list_all(
        self,
        *,
        enabled_only: bool = True,
        respect_tier: bool = True,
    ) -> list[FrameworkMetadata]:
        """
        List all registered frameworks.
        
        Args:
            enabled_only: Only include enabled frameworks.
            respect_tier: Only include frameworks accessible to current tier.
        
        Returns:
            List of FrameworkMetadata for matching frameworks.
        """
        current_tier = get_current_tier()
        results = []
        
        for entry in self._entries.values():
            if enabled_only and not entry.enabled:
                continue
            if respect_tier and not current_tier.can_access(entry.tier):
                continue
            results.append(entry.metadata)
        
        return results
    
    def list_by_layer(
        self,
        layer: VerticalLayer | int,
        *,
        enabled_only: bool = True,
        respect_tier: bool = True,
    ) -> list[FrameworkMetadata]:
        """
        List frameworks in a specific vertical layer.
        
        Args:
            layer: Vertical layer to filter by.
            enabled_only: Only include enabled frameworks.
            respect_tier: Only include frameworks accessible to current tier.
        
        Returns:
            List of FrameworkMetadata in the specified layer.
        """
        if isinstance(layer, int):
            layer = VerticalLayer(layer)
        
        return [
            m for m in self.list_all(enabled_only=enabled_only, respect_tier=respect_tier)
            if m.layer == layer
        ]
    
    def list_by_tier(
        self,
        tier: Tier | str,
        *,
        exact: bool = False,
        enabled_only: bool = True,
    ) -> list[FrameworkMetadata]:
        """
        List frameworks by tier.
        
        Args:
            tier: Tier to filter by.
            exact: If True, only exact tier match. If False, include lower tiers.
            enabled_only: Only include enabled frameworks.
        
        Returns:
            List of FrameworkMetadata matching tier criteria.
        """
        if isinstance(tier, str):
            tier = Tier.from_string(tier)
        
        results = []
        for entry in self._entries.values():
            if enabled_only and not entry.enabled:
                continue
            if exact:
                if entry.tier == tier:
                    results.append(entry.metadata)
            else:
                if entry.tier <= tier:
                    results.append(entry.metadata)
        
        return results
    
    def list_by_tags(
        self,
        tags: list[str],
        *,
        match_all: bool = False,
        enabled_only: bool = True,
        respect_tier: bool = True,
    ) -> list[FrameworkMetadata]:
        """
        List frameworks matching specified tags.
        
        Args:
            tags: Tags to search for.
            match_all: If True, framework must have all tags. If False, any tag.
            enabled_only: Only include enabled frameworks.
            respect_tier: Only include frameworks accessible to current tier.
        
        Returns:
            List of FrameworkMetadata matching tag criteria.
        """
        current_tier = get_current_tier()
        tags_set = set(t.lower() for t in tags)
        results = []
        
        for entry in self._entries.values():
            if enabled_only and not entry.enabled:
                continue
            if respect_tier and not current_tier.can_access(entry.tier):
                continue
            
            entry_tags = set(t.lower() for t in entry.metadata.tags)
            
            if match_all:
                if tags_set.issubset(entry_tags):
                    results.append(entry.metadata)
            else:
                if tags_set.intersection(entry_tags):
                    results.append(entry.metadata)
        
        return results
    
    def search(
        self,
        query: str,
        *,
        enabled_only: bool = True,
        respect_tier: bool = True,
    ) -> list[FrameworkMetadata]:
        """
        Search frameworks by name, description, or tags.
        
        Args:
            query: Search query (case-insensitive).
            enabled_only: Only include enabled frameworks.
            respect_tier: Only include frameworks accessible to current tier.
        
        Returns:
            List of matching FrameworkMetadata.
        """
        query_lower = query.lower()
        current_tier = get_current_tier()
        results = []
        
        for entry in self._entries.values():
            if enabled_only and not entry.enabled:
                continue
            if respect_tier and not current_tier.can_access(entry.tier):
                continue
            
            # Search in name, description, and tags
            m = entry.metadata
            searchable = f"{m.name} {m.description} {' '.join(m.tags)}".lower()
            
            if query_lower in searchable:
                results.append(m)
        
        return results
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Statistics
    # ═══════════════════════════════════════════════════════════════════════════
    
    @property
    def count(self) -> int:
        """Total number of registered frameworks."""
        return len(self._entries)
    
    def count_by_layer(self) -> dict[str, int]:
        """Count frameworks per layer."""
        counts: dict[str, int] = {}
        for entry in self._entries.values():
            layer_name = entry.layer.display_name
            counts[layer_name] = counts.get(layer_name, 0) + 1
        return counts
    
    def count_by_tier(self) -> dict[str, int]:
        """Count frameworks per tier."""
        counts: dict[str, int] = {}
        for entry in self._entries.values():
            tier_name = entry.tier.name
            counts[tier_name] = counts.get(tier_name, 0) + 1
        return counts
    
    def summary(self) -> dict[str, Any]:
        """Get registry summary statistics."""
        return {
            "total_frameworks": self.count,
            "by_layer": self.count_by_layer(),
            "by_tier": self.count_by_tier(),
            "enabled": sum(1 for e in self._entries.values() if e.enabled),
            "disabled": sum(1 for e in self._entries.values() if not e.enabled),
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Peer Architecture Helpers
    # ═══════════════════════════════════════════════════════════════════════════
    
    def list_peer_frameworks(
        self,
        *,
        enabled_only: bool = True,
        respect_tier: bool = True,
    ) -> list[FrameworkMetadata]:
        """
        List all meta-layer (peer hub) frameworks.
        
        This returns frameworks in Layer 6 (Meta/Peer Frameworks),
        which includes REMSOM and other meta-frameworks that can
        orchestrate cross-layer compositions.
        
        Note: All returned frameworks are peers with equal status.
        
        Args:
            enabled_only: Only include enabled frameworks.
            respect_tier: Only include frameworks accessible to current tier.
        
        Returns:
            List of peer framework metadata.
        """
        return self.list_by_layer(
            VerticalLayer.META_PEER_FRAMEWORKS,
            enabled_only=enabled_only,
            respect_tier=respect_tier,
        )
    
    def get_compatible_frameworks(
        self,
        source_slug: str,
    ) -> list[FrameworkMetadata]:
        """
        Get frameworks compatible with a given source framework.
        
        Compatibility is determined by:
        - Overlapping output/input domains
        - Layer ordering constraints
        
        Args:
            source_slug: Slug of the source framework.
        
        Returns:
            List of compatible framework metadata.
        """
        source_entry = self.get_entry(source_slug)
        source_outputs = set(source_entry.metadata.output_domains)
        
        compatible = []
        for entry in self._entries.values():
            if entry.slug == source_slug:
                continue
            
            # Check domain compatibility
            target_inputs = set(entry.metadata.required_domains)
            if source_outputs.intersection(target_inputs):
                compatible.append(entry.metadata)
        
        return compatible
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Utilities
    # ═══════════════════════════════════════════════════════════════════════════
    
    def clear(self) -> None:
        """Remove all registered frameworks."""
        self._entries.clear()
        self._logger.info("Registry cleared")
    
    def to_dict(self) -> dict[str, Any]:
        """Convert registry to dictionary for serialization."""
        return {
            "summary": self.summary(),
            "frameworks": [e.to_dict() for e in self._entries.values()],
        }
    
    def __len__(self) -> int:
        """Number of registered frameworks."""
        return len(self._entries)
    
    def __iter__(self):
        """Iterate over framework slugs."""
        return iter(self._entries)
    
    def __repr__(self) -> str:
        return f"FrameworkRegistry(count={self.count})"


# ════════════════════════════════════════════════════════════════════════════════
# Global Registry Instance
# ════════════════════════════════════════════════════════════════════════════════

# Singleton global registry
_global_registry: FrameworkRegistry | None = None


def get_global_registry() -> FrameworkRegistry:
    """
    Get the global framework registry singleton.
    
    Creates the registry on first access.
    
    Returns:
        Global FrameworkRegistry instance.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = FrameworkRegistry()
    return _global_registry


def register_framework(
    framework_class: type[BaseMetaFramework],
    *,
    factory: Callable[..., BaseMetaFramework] | None = None,
) -> None:
    """
    Register a framework with the global registry.
    
    Convenience function for global registration.
    
    Args:
        framework_class: The framework class to register.
        factory: Optional custom factory function.
    """
    get_global_registry().register(framework_class, factory=factory)


def get_framework(
    slug: str,
    *,
    config: FrameworkConfig | None = None,
    **kwargs: Any,
) -> BaseMetaFramework:
    """
    Get a framework instance from the global registry.
    
    Convenience function for global access.
    
    Args:
        slug: Framework unique identifier.
        config: Optional framework configuration.
        **kwargs: Additional arguments.
    
    Returns:
        Framework instance.
    """
    return get_global_registry().get(slug, config=config, **kwargs)


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "FrameworkRegistry",
    "RegistryEntry",
    "get_global_registry",
    "register_framework",
    "get_framework",
]
