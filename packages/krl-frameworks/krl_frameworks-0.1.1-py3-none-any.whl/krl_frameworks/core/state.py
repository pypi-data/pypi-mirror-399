# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Cohort State Vector
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Cohort State Vector definitions for CBSS (Cohort-Based State Simulation).

This module defines the canonical state vector schema used across all frameworks
for deterministic, vectorized cohort-level simulation. The CohortStateVector
provides a standardized interface for state transitions, policy shocks, and
cross-layer data flows.

Canonical Fields:
    - employment_prob: Employment probability per cohort
    - health_burden_score: Health burden index (0-1)
    - credit_access_prob: Financial access probability
    - housing_cost_ratio: Housing cost burden ratio
    - opportunity_score: Composite opportunity index
    - sector_output: Sectoral output vector
    - deprivation_vector: Multi-dimensional deprivation
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

import numpy as np
from numpy.typing import NDArray

from krl_frameworks.core.exceptions import StateValidationError

if TYPE_CHECKING:
    import pandas as pd


# Type alias for float arrays
FloatArray = NDArray[np.floating[Any]]


# ════════════════════════════════════════════════════════════════════════════════
# Cohort State Vector
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class CohortStateVector:
    """
    Canonical cohort-level state vector for CBSS simulation.
    
    This dataclass defines the 7 canonical state fields used across all
    meta-frameworks for deterministic, vectorized cohort simulation.
    All fields are NumPy arrays supporting vectorized operations.
    
    The state vector is immutable by convention - transformations return
    new instances rather than modifying in place, ensuring audit trail
    integrity and reproducibility.
    
    Attributes:
        employment_prob: Employment probability per cohort, range [0, 1].
            Shape: (n_cohorts,)
        health_burden_score: Health burden index, range [0, 1].
            Higher values indicate greater health burden.
            Shape: (n_cohorts,)
        credit_access_prob: Financial/credit access probability, range [0, 1].
            Shape: (n_cohorts,)
        housing_cost_ratio: Housing cost as ratio of income, range [0, +inf).
            Values > 0.3 typically indicate housing burden.
            Shape: (n_cohorts,)
        opportunity_score: Composite opportunity index, range [0, 1].
            Aggregated from multiple structural indices.
            Shape: (n_cohorts,)
        sector_output: Sectoral output vector.
            Shape: (n_cohorts, n_sectors) or (n_sectors,)
        deprivation_vector: Multi-dimensional deprivation indicators.
            Binary or continuous indicators per dimension.
            Shape: (n_cohorts, n_dimensions) or (n_dimensions,)
        cohort_ids: Optional identifiers for each cohort.
            Shape: (n_cohorts,)
        timestamp: When this state was created/computed.
        execution_id: UUID linking to the execution that produced this state.
        step: Simulation step number (0 = initial state).
        metadata: Additional framework-specific metadata.
    
    Example:
        >>> state = CohortStateVector(
        ...     employment_prob=np.array([0.85, 0.72, 0.91]),
        ...     health_burden_score=np.array([0.15, 0.32, 0.08]),
        ...     credit_access_prob=np.array([0.70, 0.45, 0.88]),
        ...     housing_cost_ratio=np.array([0.28, 0.42, 0.22]),
        ...     opportunity_score=np.array([0.65, 0.48, 0.78]),
        ...     sector_output=np.zeros((3, 10)),
        ...     deprivation_vector=np.zeros((3, 6)),
        ... )
        >>> state.n_cohorts
        3
        >>> state.validate()
        True
    """
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Canonical State Fields (7 required)
    # ═══════════════════════════════════════════════════════════════════════════
    
    employment_prob: FloatArray
    health_burden_score: FloatArray
    credit_access_prob: FloatArray
    housing_cost_ratio: FloatArray
    opportunity_score: FloatArray
    sector_output: FloatArray
    deprivation_vector: FloatArray
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Optional Metadata Fields
    # ═══════════════════════════════════════════════════════════════════════════
    
    cohort_ids: FloatArray | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Properties
    # ═══════════════════════════════════════════════════════════════════════════
    
    @property
    def n_cohorts(self) -> int:
        """Number of cohorts in the state vector."""
        return int(self.employment_prob.shape[0])
    
    @property
    def n_sectors(self) -> int:
        """Number of sectors in sector_output."""
        if self.sector_output.ndim == 1:
            return int(self.sector_output.shape[0])
        return int(self.sector_output.shape[1])
    
    @property
    def n_deprivation_dimensions(self) -> int:
        """Number of deprivation dimensions."""
        if self.deprivation_vector.ndim == 1:
            return int(self.deprivation_vector.shape[0])
        return int(self.deprivation_vector.shape[1])
    
    @property
    def canonical_fields(self) -> list[str]:
        """List of canonical state field names."""
        return [
            "employment_prob",
            "health_burden_score",
            "credit_access_prob",
            "housing_cost_ratio",
            "opportunity_score",
            "sector_output",
            "deprivation_vector",
        ]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Validation
    # ═══════════════════════════════════════════════════════════════════════════
    
    def validate(self, strict: bool = True) -> bool:
        """
        Validate state vector consistency and value ranges.
        
        Args:
            strict: If True, raise exceptions on validation failure.
                   If False, return False instead.
        
        Returns:
            True if valid, False if invalid (when strict=False).
        
        Raises:
            StateValidationError: When validation fails and strict=True.
        """
        try:
            self._validate_dimensions()
            self._validate_ranges()
            self._validate_no_nan_inf()
            return True
        except StateValidationError:
            if strict:
                raise
            return False
    
    def _validate_dimensions(self) -> None:
        """Validate that all 1D arrays have consistent cohort dimension."""
        n = self.n_cohorts
        
        fields_1d = [
            ("employment_prob", self.employment_prob),
            ("health_burden_score", self.health_burden_score),
            ("credit_access_prob", self.credit_access_prob),
            ("housing_cost_ratio", self.housing_cost_ratio),
            ("opportunity_score", self.opportunity_score),
        ]
        
        for name, arr in fields_1d:
            if arr.shape[0] != n:
                raise StateValidationError(
                    f"Dimension mismatch: {name} has shape {arr.shape}, expected ({n},)",
                    state_field=name,
                    expected_shape=(n,),
                    actual_shape=arr.shape,
                )
        
        # Validate 2D arrays
        if self.sector_output.ndim == 2 and self.sector_output.shape[0] != n:
            raise StateValidationError(
                f"sector_output has {self.sector_output.shape[0]} rows, expected {n}",
                state_field="sector_output",
                expected_shape=(n, self.n_sectors),
                actual_shape=self.sector_output.shape,
            )
        
        if self.deprivation_vector.ndim == 2 and self.deprivation_vector.shape[0] != n:
            raise StateValidationError(
                f"deprivation_vector has {self.deprivation_vector.shape[0]} rows, expected {n}",
                state_field="deprivation_vector",
                expected_shape=(n, self.n_deprivation_dimensions),
                actual_shape=self.deprivation_vector.shape,
            )
    
    def _validate_ranges(self) -> None:
        """Validate that probability fields are in [0, 1] range."""
        probability_fields = [
            ("employment_prob", self.employment_prob),
            ("health_burden_score", self.health_burden_score),
            ("credit_access_prob", self.credit_access_prob),
            ("opportunity_score", self.opportunity_score),
        ]
        
        for name, arr in probability_fields:
            if np.any(arr < 0) or np.any(arr > 1):
                raise StateValidationError(
                    f"{name} values must be in range [0, 1]",
                    state_field=name,
                )
        
        # Housing cost ratio must be non-negative
        if np.any(self.housing_cost_ratio < 0):
            raise StateValidationError(
                "housing_cost_ratio values must be non-negative",
                state_field="housing_cost_ratio",
            )
    
    def _validate_no_nan_inf(self) -> None:
        """Validate that no fields contain NaN or Inf values."""
        for name in self.canonical_fields:
            arr = getattr(self, name)
            if np.any(np.isnan(arr)):
                raise StateValidationError(
                    f"{name} contains NaN values",
                    state_field=name,
                )
            if np.any(np.isinf(arr)):
                raise StateValidationError(
                    f"{name} contains Inf values",
                    state_field=name,
                )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Factory Methods
    # ═══════════════════════════════════════════════════════════════════════════
    
    @classmethod
    def zeros(
        cls,
        n_cohorts: int,
        n_sectors: int = 10,
        n_deprivation_dims: int = 6,
        **kwargs: Any,
    ) -> Self:
        """
        Create a zero-initialized state vector.
        
        Args:
            n_cohorts: Number of cohorts.
            n_sectors: Number of sectors for sector_output.
            n_deprivation_dims: Number of deprivation dimensions.
            **kwargs: Additional metadata fields.
        
        Returns:
            Zero-initialized CohortStateVector.
        """
        return cls(
            employment_prob=np.zeros(n_cohorts),
            health_burden_score=np.zeros(n_cohorts),
            credit_access_prob=np.zeros(n_cohorts),
            housing_cost_ratio=np.zeros(n_cohorts),
            opportunity_score=np.zeros(n_cohorts),
            sector_output=np.zeros((n_cohorts, n_sectors)),
            deprivation_vector=np.zeros((n_cohorts, n_deprivation_dims)),
            **kwargs,
        )
    
    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        column_mapping: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Create a state vector from a pandas DataFrame.
        
        Args:
            df: DataFrame with cohort-level data.
            column_mapping: Optional mapping from canonical field names
                to DataFrame column names.
            **kwargs: Additional metadata fields.
        
        Returns:
            CohortStateVector initialized from DataFrame.
        
        Raises:
            StateValidationError: If required columns are missing.
        """
        mapping = column_mapping or {}
        
        def get_col(canonical_name: str) -> FloatArray:
            col_name = mapping.get(canonical_name, canonical_name)
            if col_name in df.columns:
                return df[col_name].values.astype(np.float64)
            raise StateValidationError(
                f"Missing required column: {col_name}",
                state_field=canonical_name,
            )
        
        # Handle 1D fields
        employment_prob = get_col("employment_prob")
        health_burden_score = get_col("health_burden_score")
        credit_access_prob = get_col("credit_access_prob")
        housing_cost_ratio = get_col("housing_cost_ratio")
        opportunity_score = get_col("opportunity_score")
        
        # Handle 2D fields - look for prefixed columns
        sector_cols = [c for c in df.columns if c.startswith("sector_")]
        if sector_cols:
            sector_output = df[sorted(sector_cols)].values.astype(np.float64)
        else:
            sector_output = np.zeros((len(df), 10))
        
        dep_cols = [c for c in df.columns if c.startswith("deprivation_")]
        if dep_cols:
            deprivation_vector = df[sorted(dep_cols)].values.astype(np.float64)
        else:
            deprivation_vector = np.zeros((len(df), 6))
        
        return cls(
            employment_prob=employment_prob,
            health_burden_score=health_burden_score,
            credit_access_prob=credit_access_prob,
            housing_cost_ratio=housing_cost_ratio,
            opportunity_score=opportunity_score,
            sector_output=sector_output,
            deprivation_vector=deprivation_vector,
            **kwargs,
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Transformations
    # ═══════════════════════════════════════════════════════════════════════════
    
    def copy(self, **overrides: Any) -> Self:
        """
        Create a copy of this state with optional field overrides.
        
        Args:
            **overrides: Fields to override in the copy.
        
        Returns:
            New CohortStateVector with overridden fields.
        """
        fields = {
            "employment_prob": self.employment_prob.copy(),
            "health_burden_score": self.health_burden_score.copy(),
            "credit_access_prob": self.credit_access_prob.copy(),
            "housing_cost_ratio": self.housing_cost_ratio.copy(),
            "opportunity_score": self.opportunity_score.copy(),
            "sector_output": self.sector_output.copy(),
            "deprivation_vector": self.deprivation_vector.copy(),
            "cohort_ids": self.cohort_ids.copy() if self.cohort_ids is not None else None,
            "timestamp": self.timestamp,
            "execution_id": self.execution_id,
            "step": self.step,
            "metadata": self.metadata.copy(),
        }
        fields.update(overrides)
        return self.__class__(**fields)
    
    def increment_step(self) -> Self:
        """Return a copy with step incremented by 1."""
        return self.copy(
            step=self.step + 1,
            timestamp=datetime.now(timezone.utc),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert state vector to a dictionary.
        
        Useful for serialization and logging.
        
        Returns:
            Dictionary representation of the state.
        """
        return {
            "employment_prob": self.employment_prob.tolist(),
            "health_burden_score": self.health_burden_score.tolist(),
            "credit_access_prob": self.credit_access_prob.tolist(),
            "housing_cost_ratio": self.housing_cost_ratio.tolist(),
            "opportunity_score": self.opportunity_score.tolist(),
            "sector_output": self.sector_output.tolist(),
            "deprivation_vector": self.deprivation_vector.tolist(),
            "n_cohorts": self.n_cohorts,
            "n_sectors": self.n_sectors,
            "n_deprivation_dimensions": self.n_deprivation_dimensions,
            "timestamp": self.timestamp.isoformat(),
            "execution_id": self.execution_id,
            "step": self.step,
            "metadata": self.metadata,
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert state vector to a pandas DataFrame.
        
        Returns:
            DataFrame with one row per cohort.
        """
        import pandas as pd
        
        data = {
            "employment_prob": self.employment_prob,
            "health_burden_score": self.health_burden_score,
            "credit_access_prob": self.credit_access_prob,
            "housing_cost_ratio": self.housing_cost_ratio,
            "opportunity_score": self.opportunity_score,
        }
        
        # Add sector columns
        for i in range(self.n_sectors):
            if self.sector_output.ndim == 2:
                data[f"sector_{i}"] = self.sector_output[:, i]
            else:
                data[f"sector_{i}"] = self.sector_output[i]
        
        # Add deprivation columns
        for i in range(self.n_deprivation_dimensions):
            if self.deprivation_vector.ndim == 2:
                data[f"deprivation_{i}"] = self.deprivation_vector[:, i]
            else:
                data[f"deprivation_{i}"] = self.deprivation_vector[i]
        
        df = pd.DataFrame(data)
        
        if self.cohort_ids is not None:
            df["cohort_id"] = self.cohort_ids
        
        return df
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Aggregation Methods
    # ═══════════════════════════════════════════════════════════════════════════
    
    def mean_opportunity_score(self) -> float:
        """Compute mean opportunity score across cohorts."""
        return float(np.mean(self.opportunity_score))
    
    def weighted_opportunity_score(self, weights: FloatArray) -> float:
        """Compute weighted mean opportunity score."""
        return float(np.average(self.opportunity_score, weights=weights))
    
    def deprivation_headcount(self, threshold: float = 0.5) -> float:
        """
        Compute headcount ratio of deprived cohorts.
        
        A cohort is considered deprived if their mean deprivation
        across dimensions exceeds the threshold.
        
        Args:
            threshold: Deprivation threshold (default 0.5).
        
        Returns:
            Proportion of cohorts that are deprived.
        """
        if self.deprivation_vector.ndim == 1:
            mean_dep = self.deprivation_vector
        else:
            mean_dep = np.mean(self.deprivation_vector, axis=1)
        
        return float(np.mean(mean_dep > threshold))
    
    def summary_statistics(self) -> dict[str, dict[str, float]]:
        """
        Compute summary statistics for all canonical fields.
        
        Returns:
            Dictionary with mean, std, min, max for each field.
        """
        stats: dict[str, dict[str, float]] = {}
        
        for name in self.canonical_fields[:5]:  # 1D fields
            arr = getattr(self, name)
            stats[name] = {
                "mean": float(np.mean(arr)),
                "std": float(np.std(arr)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
            }
        
        return stats
    
    def __repr__(self) -> str:
        return (
            f"CohortStateVector("
            f"n_cohorts={self.n_cohorts}, "
            f"n_sectors={self.n_sectors}, "
            f"step={self.step}, "
            f"execution_id={self.execution_id[:8]}...)"
        )


# ════════════════════════════════════════════════════════════════════════════════
# State Trajectory
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class StateTrajectory:
    """
    A sequence of CohortStateVectors representing simulation history.
    
    This class stores the complete trajectory of states through a
    CBSS simulation, enabling analysis, visualization, and auditing
    of the simulation path.
    
    Attributes:
        states: List of CohortStateVectors in chronological order.
        framework_slug: Identifier of the framework that produced this trajectory.
        metadata: Additional trajectory-level metadata.
    """
    
    states: list[CohortStateVector] = field(default_factory=list)
    framework_slug: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def n_steps(self) -> int:
        """Number of steps in the trajectory."""
        return len(self.states)
    
    @property
    def initial_state(self) -> CohortStateVector | None:
        """The initial state (step 0)."""
        return self.states[0] if self.states else None
    
    @property
    def final_state(self) -> CohortStateVector | None:
        """The final state."""
        return self.states[-1] if self.states else None
    
    def __len__(self) -> int:
        """Number of states in the trajectory."""
        return len(self.states)
    
    def append(self, state: CohortStateVector) -> None:
        """Add a state to the trajectory."""
        self.states.append(state)
    
    def get_field_trajectory(self, field_name: str) -> FloatArray:
        """
        Extract the trajectory of a single field across all steps.
        
        Args:
            field_name: Name of the canonical field.
        
        Returns:
            Array of shape (n_steps, n_cohorts) for the field.
        """
        return np.array([getattr(s, field_name) for s in self.states])
    
    def opportunity_score_trajectory(self) -> FloatArray:
        """Get opportunity_score values across all steps."""
        return self.get_field_trajectory("opportunity_score")
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert trajectory to a long-format DataFrame.
        
        Returns:
            DataFrame with columns: step, cohort_idx, and all canonical fields.
        """
        import pandas as pd
        
        dfs = []
        for state in self.states:
            df = state.to_dataframe()
            df["step"] = state.step
            df["cohort_idx"] = range(len(df))
            dfs.append(df)
        
        return pd.concat(dfs, ignore_index=True)


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "CohortStateVector",
    "StateTrajectory",
    "FloatArray",
]
