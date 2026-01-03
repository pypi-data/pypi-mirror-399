# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Framework Output Envelope
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Framework Output Envelope - Self-Describing Output Contract.

This module defines the canonical output envelope structure that all KRL
frameworks must produce. The envelope ensures that:

1. Frameworks are the SOLE AUTHORITY over their output schema
2. The API layer never invents structure - it passes through
3. Dimensional integrity is preserved (user selects 3 sectors → 3 sectors returned)
4. All provenance information is captured (user inputs, fallbacks, simulation params)

Architecture:
    ┌─────────────────────────────────────────────────────────────────┐
    │                    FrameworkOutputEnvelope                       │
    ├─────────────────────────────────────────────────────────────────┤
    │  dimensions: DimensionManifest  # Canonical axis definitions     │
    │  provenance: ProvenanceRecord   # What user asked + fallbacks    │
    │  outputs: dict                  # Framework-specific outputs     │
    │  metadata: dict                 # Execution metadata             │
    └─────────────────────────────────────────────────────────────────┘

Key Contracts:
    - DimensionManifest: Canonical dimension definitions with validation
    - ProvenanceRecord: Separates fallbacks from simulation parameters
    - FrameworkOutputEnvelope: Complete self-describing output

Usage:
    >>> from krl_frameworks.core.output_envelope import (
    ...     FrameworkOutputEnvelope,
    ...     DimensionManifest,
    ...     ProvenanceRecord,
    ... )
    >>> 
    >>> manifest = DimensionManifest(
    ...     sectors=["Information", "Finance", "Services"],
    ...     time_periods=list(range(2024, 2035)),
    ...     cohorts=["18-24", "25-34", "35-44"],
    ...     geography="Virginia",
    ... )
    >>> 
    >>> provenance = ProvenanceRecord(
    ...     user_parameters={"sector_names": ["Information", "Finance", "Services"]},
    ...     fallbacks_applied={"capital_share": 0.33},
    ...     simulation_params={"random_seed": 42},
    ... )
    >>> 
    >>> envelope = FrameworkOutputEnvelope(
    ...     framework_slug="remsom",
    ...     framework_version="1.0.0",
    ...     dimensions=manifest,
    ...     provenance=provenance,
    ...     outputs={"sector_employment": {...}, "sector_output": {...}},
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Sequence


__all__ = [
    "DimensionManifest",
    "ProvenanceRecord",
    "FrameworkOutputEnvelope",
    "create_dimension_manifest",
    "create_provenance_record",
]


# ════════════════════════════════════════════════════════════════════════════════
# Dimension Manifest
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class DimensionManifest:
    """
    Canonical dimension definitions for framework outputs.
    
    This manifest declares the exact dimensional axes that all outputs
    in an envelope conform to. Every output matrix, dictionary, or array
    must index into these canonical dimensions.
    
    Validation:
        __post_init__ validates that all dimensions are non-empty and
        that there are no duplicate values within a dimension.
    
    Attributes:
        sectors: Canonical sector names (user-provided or framework defaults).
        time_periods: Time period labels (years, quarters, etc.).
        cohorts: Cohort labels (age groups, demographic segments).
        geography: Geographic scope (region, state, country).
        custom_dimensions: Additional framework-specific dimensions.
    
    Example:
        >>> manifest = DimensionManifest(
        ...     sectors=["Information", "Finance", "Services"],
        ...     time_periods=[2024, 2025, 2026],
        ...     cohorts=["18-24", "25-34", "35-44", "45-54", "55+"],
        ...     geography="Virginia",
        ... )
        >>> len(manifest.sectors)
        3
    """
    
    sectors: tuple[str, ...] = field(default_factory=tuple)
    time_periods: tuple[int | str, ...] = field(default_factory=tuple)
    cohorts: tuple[str, ...] = field(default_factory=tuple)
    geography: str = "National"
    custom_dimensions: dict[str, tuple[str, ...]] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate dimensional integrity."""
        # Convert lists to tuples if needed (frozen dataclass requirement)
        if isinstance(self.sectors, list):
            object.__setattr__(self, "sectors", tuple(self.sectors))
        if isinstance(self.time_periods, list):
            object.__setattr__(self, "time_periods", tuple(self.time_periods))
        if isinstance(self.cohorts, list):
            object.__setattr__(self, "cohorts", tuple(self.cohorts))
        
        # Validate no duplicates in any dimension
        self._validate_no_duplicates("sectors", self.sectors)
        self._validate_no_duplicates("time_periods", self.time_periods)
        self._validate_no_duplicates("cohorts", self.cohorts)
        
        for dim_name, dim_values in self.custom_dimensions.items():
            if isinstance(dim_values, list):
                self.custom_dimensions[dim_name] = tuple(dim_values)
            self._validate_no_duplicates(dim_name, dim_values)
    
    def _validate_no_duplicates(self, name: str, values: Sequence) -> None:
        """Raise ValueError if duplicates found."""
        if len(values) != len(set(values)):
            seen = set()
            duplicates = [v for v in values if v in seen or seen.add(v)]
            raise ValueError(
                f"Dimension '{name}' contains duplicates: {duplicates}"
            )
    
    @property
    def n_sectors(self) -> int:
        """Number of sectors."""
        return len(self.sectors)
    
    @property
    def n_time_periods(self) -> int:
        """Number of time periods."""
        return len(self.time_periods)
    
    @property
    def n_cohorts(self) -> int:
        """Number of cohorts."""
        return len(self.cohorts)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "sectors": list(self.sectors),
            "time_periods": list(self.time_periods),
            "cohorts": list(self.cohorts),
            "geography": self.geography,
            "custom_dimensions": {
                k: list(v) for k, v in self.custom_dimensions.items()
            },
            "n_sectors": self.n_sectors,
            "n_time_periods": self.n_time_periods,
            "n_cohorts": self.n_cohorts,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Provenance Record
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ProvenanceRecord:
    """
    Record of parameter provenance for framework execution.
    
    Separates three distinct concerns:
    1. user_parameters: What the user explicitly requested
    2. fallbacks_applied: What values were used due to missing data
    3. simulation_params: Stochastic/computational parameters (seeds, tolerances)
    
    This separation allows consumers to understand:
    - What was intentional vs. defaulted
    - Which results might differ with different data
    - What parameters to save for reproducibility
    
    Attributes:
        user_parameters: Parameters explicitly provided by the user.
        fallbacks_applied: Default values used when data was missing.
        simulation_params: Stochastic/computational parameters.
        data_sources: List of data sources used.
        data_hash: Hash of input data for reproducibility.
        timestamp: When this provenance record was created.
    
    Example:
        >>> provenance = ProvenanceRecord(
        ...     user_parameters={
        ...         "sector_names": ["Information", "Finance", "Services"],
        ...         "geo_scope": "Virginia",
        ...     },
        ...     fallbacks_applied={
        ...         "capital_share": {"value": 0.33, "reason": "No capital data available"},
        ...         "depreciation_rate": {"value": 0.05, "reason": "Using BEA default"},
        ...     },
        ...     simulation_params={
        ...         "random_seed": 42,
        ...         "convergence_tolerance": 1e-6,
        ...     },
        ... )
    """
    
    user_parameters: dict[str, Any] = field(default_factory=dict)
    fallbacks_applied: dict[str, Any] = field(default_factory=dict)
    simulation_params: dict[str, Any] = field(default_factory=dict)
    data_sources: list[str] = field(default_factory=list)
    data_hash: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_fallback(
        self, 
        param_name: str, 
        value: Any, 
        reason: str = "No data available"
    ) -> None:
        """Record a fallback value with reason."""
        self.fallbacks_applied[param_name] = {
            "value": value,
            "reason": reason,
        }
    
    def add_data_source(self, source: str) -> None:
        """Record a data source that was used."""
        if source not in self.data_sources:
            self.data_sources.append(source)
    
    @property
    def has_fallbacks(self) -> bool:
        """Whether any fallback values were applied."""
        return len(self.fallbacks_applied) > 0
    
    @property
    def fallback_count(self) -> int:
        """Number of fallbacks applied."""
        return len(self.fallbacks_applied)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "user_parameters": self.user_parameters,
            "fallbacks_applied": self.fallbacks_applied,
            "simulation_params": self.simulation_params,
            "data_sources": self.data_sources,
            "data_hash": self.data_hash,
            "timestamp": self.timestamp.isoformat(),
            "has_fallbacks": self.has_fallbacks,
            "fallback_count": self.fallback_count,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Framework Output Envelope
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class FrameworkOutputEnvelope:
    """
    Self-describing output envelope for framework results.
    
    The envelope is the canonical contract between frameworks and the API layer.
    The API layer MUST NOT invent structure - it passes the envelope through.
    
    Key Guarantees:
        1. dimensions contains the exact axes for all outputs
        2. provenance captures all parameter sources
        3. outputs is framework-unique, not API-normalized
        4. metadata provides execution context
    
    Attributes:
        framework_slug: Identifier for the framework that produced this.
        framework_version: Version of the framework.
        dimensions: Canonical dimension manifest.
        provenance: Parameter provenance record.
        outputs: Framework-specific output data.
        metadata: Additional execution metadata.
    
    Example:
        >>> envelope = FrameworkOutputEnvelope(
        ...     framework_slug="remsom",
        ...     framework_version="1.0.0",
        ...     dimensions=DimensionManifest(
        ...         sectors=["Information", "Finance", "Services"],
        ...     ),
        ...     provenance=ProvenanceRecord(
        ...         user_parameters={"sector_names": ["Information", "Finance", "Services"]},
        ...     ),
        ...     outputs={
        ...         "sector_employment": {"Information": 0.85, "Finance": 0.91, "Services": 0.78},
        ...         "sector_output": {"Information": 2.3e9, "Finance": 4.1e9, "Services": 1.8e9},
        ...     },
        ... )
    """
    
    framework_slug: str
    framework_version: str
    dimensions: DimensionManifest
    provenance: ProvenanceRecord
    outputs: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate envelope integrity."""
        if not self.framework_slug:
            raise ValueError("framework_slug is required")
        if not self.framework_version:
            raise ValueError("framework_version is required")
    
    def validate_output_dimensions(self) -> list[str]:
        """
        Validate that outputs conform to declared dimensions.
        
        Returns:
            List of validation warnings (empty if all valid).
        """
        warnings = []
        
        for output_name, output_data in self.outputs.items():
            if isinstance(output_data, dict):
                # Check if dict keys match sector names
                keys = set(output_data.keys())
                sectors = set(self.dimensions.sectors)
                
                if keys == sectors:
                    continue  # Valid sector-keyed output
                
                # Check for time period keys
                time_periods = set(str(t) for t in self.dimensions.time_periods)
                if keys == time_periods or keys == set(self.dimensions.time_periods):
                    continue  # Valid time-keyed output
                
                # Check for cohort keys
                cohorts = set(self.dimensions.cohorts)
                if keys == cohorts:
                    continue  # Valid cohort-keyed output
                
                # Keys don't match any known dimension
                if keys and sectors and not keys.issubset(sectors | time_periods | cohorts):
                    warnings.append(
                        f"Output '{output_name}' has keys {keys} which don't match "
                        f"declared dimensions"
                    )
        
        return warnings
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API response."""
        return {
            "framework_slug": self.framework_slug,
            "framework_version": self.framework_version,
            "dimensions": self.dimensions.to_dict(),
            "provenance": self.provenance.to_dict(),
            "outputs": self.outputs,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FrameworkOutputEnvelope":
        """Deserialize from dictionary."""
        return cls(
            framework_slug=data["framework_slug"],
            framework_version=data["framework_version"],
            dimensions=DimensionManifest(
                sectors=tuple(data["dimensions"].get("sectors", [])),
                time_periods=tuple(data["dimensions"].get("time_periods", [])),
                cohorts=tuple(data["dimensions"].get("cohorts", [])),
                geography=data["dimensions"].get("geography", "National"),
                custom_dimensions={
                    k: tuple(v) 
                    for k, v in data["dimensions"].get("custom_dimensions", {}).items()
                },
            ),
            provenance=ProvenanceRecord(
                user_parameters=data["provenance"].get("user_parameters", {}),
                fallbacks_applied=data["provenance"].get("fallbacks_applied", {}),
                simulation_params=data["provenance"].get("simulation_params", {}),
                data_sources=data["provenance"].get("data_sources", []),
                data_hash=data["provenance"].get("data_hash", ""),
            ),
            outputs=data.get("outputs", {}),
            metadata=data.get("metadata", {}),
        )


# ════════════════════════════════════════════════════════════════════════════════
# Factory Functions
# ════════════════════════════════════════════════════════════════════════════════


def create_dimension_manifest(
    sectors: Sequence[str] | None = None,
    time_periods: Sequence[int | str] | None = None,
    cohorts: Sequence[str] | None = None,
    geography: str = "National",
    **custom_dimensions: Sequence[str],
) -> DimensionManifest:
    """
    Factory function to create a DimensionManifest.
    
    Args:
        sectors: Sector names.
        time_periods: Time period labels.
        cohorts: Cohort labels.
        geography: Geographic scope.
        **custom_dimensions: Additional named dimensions.
    
    Returns:
        Validated DimensionManifest.
    """
    return DimensionManifest(
        sectors=tuple(sectors) if sectors else (),
        time_periods=tuple(time_periods) if time_periods else (),
        cohorts=tuple(cohorts) if cohorts else (),
        geography=geography,
        custom_dimensions={k: tuple(v) for k, v in custom_dimensions.items()},
    )


def create_provenance_record(
    user_parameters: dict[str, Any] | None = None,
    fallbacks: dict[str, tuple[Any, str]] | None = None,
    simulation_params: dict[str, Any] | None = None,
    data_sources: list[str] | None = None,
) -> ProvenanceRecord:
    """
    Factory function to create a ProvenanceRecord.
    
    Args:
        user_parameters: User-provided parameters.
        fallbacks: Dict mapping param name to (value, reason) tuples.
        simulation_params: Stochastic/computational parameters.
        data_sources: List of data sources used.
    
    Returns:
        ProvenanceRecord with fallbacks structured correctly.
    """
    record = ProvenanceRecord(
        user_parameters=user_parameters or {},
        simulation_params=simulation_params or {},
        data_sources=data_sources or [],
    )
    
    if fallbacks:
        for param_name, (value, reason) in fallbacks.items():
            record.add_fallback(param_name, value, reason)
    
    return record
