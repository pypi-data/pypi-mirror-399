# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Configuration
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Framework configuration classes.

This module provides configuration dataclasses for framework execution,
including simulation parameters, convergence criteria, and audit settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConvergenceMethod(str, Enum):
    """Method for checking simulation convergence."""
    
    FIXED_STEPS = "fixed_steps"  # Run exactly N steps
    TOLERANCE = "tolerance"  # Run until state change < tolerance
    COMBINED = "combined"  # Min steps + tolerance check


class AggregationMethod(str, Enum):
    """Method for aggregating cohort-level outputs."""
    
    MEAN = "mean"
    WEIGHTED_MEAN = "weighted_mean"
    MEDIAN = "median"
    SUM = "sum"


@dataclass
class SimulationConfig:
    """
    Configuration for CBSS simulation execution.
    
    Attributes:
        max_steps: Maximum simulation steps.
        min_steps: Minimum steps before convergence check.
        tolerance: Convergence tolerance for state changes.
        convergence_method: How to determine convergence.
        random_seed: Seed for reproducible stochastic operations.
        enable_audit: Whether to log execution for auditing.
        snapshot_interval: Steps between state snapshots.
    """
    
    max_steps: int = 100
    min_steps: int = 10
    tolerance: float = 1e-6
    convergence_method: ConvergenceMethod = ConvergenceMethod.FIXED_STEPS
    random_seed: int | None = None
    enable_audit: bool = True
    snapshot_interval: int = 10
    
    def __post_init__(self) -> None:
        if self.max_steps < self.min_steps:
            raise ValueError("max_steps must be >= min_steps")
        if self.tolerance <= 0:
            raise ValueError("tolerance must be positive")


@dataclass
class FrameworkConfig:
    """
    Base configuration for framework execution.
    
    Attributes:
        simulation: Simulation-specific configuration.
        aggregation_method: How to aggregate cohort outputs.
        n_sectors: Number of economic sectors.
        n_deprivation_dims: Number of deprivation dimensions.
        enable_caching: Whether to cache intermediate results.
        parallel_execution: Whether to enable parallel processing.
        max_workers: Maximum parallel workers.
        metadata: Additional framework-specific configuration.
    """
    
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    aggregation_method: AggregationMethod = AggregationMethod.WEIGHTED_MEAN
    n_sectors: int = 10
    n_deprivation_dims: int = 6
    enable_caching: bool = True
    parallel_execution: bool = False
    max_workers: int = 4
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def with_overrides(self, **overrides: Any) -> FrameworkConfig:
        """Create a new config with overridden values."""
        import copy
        new_config = copy.deepcopy(self)
        for key, value in overrides.items():
            if hasattr(new_config, key):
                setattr(new_config, key, value)
            else:
                new_config.metadata[key] = value
        return new_config
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "simulation": {
                "max_steps": self.simulation.max_steps,
                "min_steps": self.simulation.min_steps,
                "tolerance": self.simulation.tolerance,
                "convergence_method": self.simulation.convergence_method.value,
                "random_seed": self.simulation.random_seed,
                "enable_audit": self.simulation.enable_audit,
                "snapshot_interval": self.simulation.snapshot_interval,
            },
            "aggregation_method": self.aggregation_method.value,
            "n_sectors": self.n_sectors,
            "n_deprivation_dims": self.n_deprivation_dims,
            "enable_caching": self.enable_caching,
            "parallel_execution": self.parallel_execution,
            "max_workers": self.max_workers,
            "metadata": self.metadata,
        }


__all__ = [
    "ConvergenceMethod",
    "AggregationMethod",
    "SimulationConfig",
    "FrameworkConfig",
]
