# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Input-Output Tables (IO Tables) Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Input-Output Tables (IO Tables) Framework.

Implements Leontief Input-Output analysis for economic impact
assessment and multiplier computation.

Core Methodology:
    1. Construct technical coefficients matrix (A) from IO tables
    2. Compute Leontief inverse: L = (I - A)^(-1)
    3. Calculate Type I multipliers (direct + indirect effects)
    4. Calculate Type II multipliers (+ induced effects via households)
    5. Sectoral decomposition and backward/forward linkages

Key Outputs:
    - Output multipliers: ∂X / ∂Y (output per unit final demand)
    - Employment multipliers: jobs per unit final demand
    - Value-added multipliers: GDP contribution per unit demand
    - Backward/Forward linkage indices

CBSS Integration:
    - sector_output vector represents multi-sector production
    - Models inter-sectoral propagation of demand shocks
    - Simulates supply chain disruption cascades

References:
    - Leontief, W. (1936). "Quantitative Input-Output Relations"
    - Miller, R.E. & Blair, P.D. (2009). "Input-Output Analysis"
    - BEA Make and Use Tables methodology

Tier: PROFESSIONAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np

from krl_frameworks.core.base import (
    BaseMetaFramework,
    FrameworkMetadata,
    VerticalLayer,
)
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier, requires_tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["IOTablesFramework", "IOTransition", "IOMetrics"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# IO Metrics
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class IOMetrics:
    """
    Container for IO analysis results.
    
    Attributes:
        output_multipliers: Type I output multipliers by sector.
        employment_multipliers: Employment multipliers by sector.
        value_added_multipliers: Value-added multipliers by sector.
        type_ii_output_multipliers: Type II multipliers (with induced).
        backward_linkages: Backward linkage indices by sector.
        forward_linkages: Forward linkage indices by sector.
        key_sectors: Sectors with high backward AND forward linkages.
        total_output_impact: Aggregate output impact from final demand.
        leontief_inverse: The computed Leontief inverse matrix.
    """
    
    output_multipliers: dict[str, float]
    employment_multipliers: dict[str, float]
    value_added_multipliers: dict[str, float]
    type_ii_output_multipliers: dict[str, float]
    backward_linkages: dict[str, float]
    forward_linkages: dict[str, float]
    key_sectors: list[str]
    total_output_impact: float
    leontief_inverse: Optional[np.ndarray]
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary (excluding large matrices)."""
        return {
            "output_multipliers": self.output_multipliers,
            "employment_multipliers": self.employment_multipliers,
            "value_added_multipliers": self.value_added_multipliers,
            "type_ii_output_multipliers": self.type_ii_output_multipliers,
            "backward_linkages": self.backward_linkages,
            "forward_linkages": self.forward_linkages,
            "key_sectors": self.key_sectors,
            "total_output_impact": self.total_output_impact,
        }


# ════════════════════════════════════════════════════════════════════════════════
# IO Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class IOTransition(TransitionFunction):
    """
    Transition function for IO-based economic dynamics.
    
    Models inter-sectoral propagation of shocks through the
    Leontief inverse structure.
    """
    
    name = "IOTransition"
    
    def __init__(
        self,
        leontief_inverse: Optional[np.ndarray] = None,
        demand_growth_rate: float = 0.02,
    ):
        self.leontief_inverse = leontief_inverse
        self.demand_growth_rate = demand_growth_rate
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply IO transition with multiplier effects."""
        params = params or {}
        
        demand_growth = params.get("demand_growth_rate", self.demand_growth_rate)
        demand_shock = params.get("demand_shock", None)
        
        # Base growth in final demand
        new_output = state.sector_output * (1 + demand_growth)
        
        # Apply demand shock through Leontief inverse if available
        if demand_shock is not None and self.leontief_inverse is not None:
            shock = np.asarray(demand_shock)
            if shock.shape[0] == self.leontief_inverse.shape[0]:
                # Compute total output change: ΔX = L × ΔY
                output_change = self.leontief_inverse @ shock
                # Apply to sector output (broadcast if needed)
                if len(state.sector_output) == len(output_change):
                    new_output = state.sector_output + output_change
        
        # Employment follows output with lag
        employment_elasticity = 0.5
        output_pct_change = (new_output - state.sector_output) / (state.sector_output + 1e-10)
        new_employment = np.clip(
            state.employment_prob * (1 + employment_elasticity * output_pct_change.mean()),
            0, 1
        )
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=state.opportunity_score,
            sector_output=np.clip(new_output, 0, None),
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# IO Tables Framework
# ════════════════════════════════════════════════════════════════════════════════


class IOTablesFramework(BaseMetaFramework):
    """
    Input-Output Tables Framework for economic impact analysis.
    
    Implements Leontief Input-Output analysis including:
    - Technical coefficients computation
    - Leontief inverse calculation
    - Type I and Type II multipliers
    - Backward and forward linkage analysis
    
    Example:
        >>> bundle = DataBundle.from_dataframes({
        ...     "io_table": io_df,  # Square IO transaction matrix
        ...     "sectors": sector_df,  # Sector metadata
        ... })
        >>> io = IOTablesFramework()
        >>> metrics = io.compute_multipliers(bundle)
        >>> print(f"Agriculture multiplier: {metrics.output_multipliers['agriculture']:.2f}")
    """
    
    def __init__(self):
        super().__init__()
        self._leontief_inverse: Optional[np.ndarray] = None
        self._sector_names: list[str] = []
        self._transition_fn = IOTransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return IO Tables framework metadata."""
        return FrameworkMetadata(
            slug="io-tables",
            name="Input-Output Tables Analysis",
            version="1.0.0",
            layer=VerticalLayer.META_PEER_FRAMEWORKS,
            tier=Tier.PROFESSIONAL,
            description=(
                "Leontief Input-Output analysis for economic impact "
                "assessment, multipliers, and sectoral linkages."
            ),
            required_domains=["io_table"],
            output_domains=["multipliers", "linkages", "leontief_inverse"],
            constituent_models=["leontief_inverse", "multiplier_calculator"],
            tags=["economic", "input-output", "multipliers", "leontief", "macro"],
            author="Khipu Research Labs",
            license="Apache-2.0",
        )
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from IO table."""
        io_data = bundle.get("io_table") if bundle.has_domain("io_table") else None
        
        if io_data is None:
            n_cohorts = getattr(config, "cohort_size", 100)
            return CohortStateVector.zeros(n_cohorts)
        
        df = io_data.data
        
        # IO table is typically square NxN
        n_sectors = len(df)
        
        # Extract total output by sector (row sums + final demand)
        if "total_output" in df.columns:
            sector_output = df["total_output"].values.astype(float)
        else:
            # Assume matrix values represent inter-industry flows
            sector_output = df.sum(axis=1).values.astype(float)
        
        # Normalize to reasonable scale
        sector_output = sector_output / (sector_output.max() + 1e-10)
        
        return CohortStateVector(
            employment_prob=np.full(n_sectors, 0.7),
            health_burden_score=np.full(n_sectors, 0.3),
            credit_access_prob=np.full(n_sectors, 0.6),
            housing_cost_ratio=np.full(n_sectors, 0.3),
            opportunity_score=sector_output,
            sector_output=sector_output,
            deprivation_vector=np.full(n_sectors, 0.2),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        step: int,
    ) -> CohortStateVector:
        """Apply IO transition using the configured transition function."""
        from krl_frameworks.core.config import FrameworkConfig
        return self._transition_fn(state, step, FrameworkConfig())
    
    def _compute_technical_coefficients(
        self,
        io_matrix: np.ndarray,
        total_output: np.ndarray,
    ) -> np.ndarray:
        """
        Compute technical coefficients matrix A.
        
        A[i,j] = Z[i,j] / X[j]
        
        Where Z is intermediate flows matrix and X is total output.
        """
        n = io_matrix.shape[0]
        A = np.zeros((n, n))
        
        for j in range(n):
            if total_output[j] > 0:
                A[:, j] = io_matrix[:, j] / total_output[j]
        
        return A
    
    def _compute_leontief_inverse(
        self,
        A: np.ndarray,
    ) -> np.ndarray:
        """
        Compute Leontief inverse L = (I - A)^(-1).
        
        The Leontief inverse captures total (direct + indirect)
        requirements per unit of final demand.
        """
        n = A.shape[0]
        I = np.eye(n)
        
        try:
            L = np.linalg.inv(I - A)
        except np.linalg.LinAlgError:
            logger.warning("Singular matrix in Leontief inverse, using pseudo-inverse")
            L = np.linalg.pinv(I - A)
        
        return L
    
    def _compute_multipliers(
        self,
        L: np.ndarray,
        va_coefficients: Optional[np.ndarray] = None,
        emp_coefficients: Optional[np.ndarray] = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute Type I multipliers from Leontief inverse.
        
        Output multiplier: sum of column j of L
        VA multiplier: v' × L (value-added row vector × L)
        Employment multiplier: e' × L (employment coefficients × L)
        """
        n = L.shape[0]
        
        # Output multipliers: column sums of L
        output_mult = L.sum(axis=0)
        
        # Value-added multipliers
        if va_coefficients is not None:
            va_mult = va_coefficients @ L
        else:
            # Assume 50% value-added share
            va_mult = 0.5 * output_mult
        
        # Employment multipliers
        if emp_coefficients is not None:
            emp_mult = emp_coefficients @ L
        else:
            # Assume employment proportional to output
            emp_mult = output_mult / 1000  # Jobs per $1M output
        
        return output_mult, va_mult, emp_mult
    
    def _compute_linkages(
        self,
        L: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Compute backward and forward linkage indices.
        
        Backward linkage: column sums of L (demand pull)
        Forward linkage: row sums of L (supply push)
        
        Normalized by average to get indices (>1 = above average linkage).
        """
        n = L.shape[0]
        
        backward = L.sum(axis=0)
        forward = L.sum(axis=1)
        
        # Normalize by average
        avg_backward = backward.mean()
        avg_forward = forward.mean()
        
        backward_idx = backward / avg_backward if avg_backward > 0 else backward
        forward_idx = forward / avg_forward if avg_forward > 0 else forward
        
        return backward_idx, forward_idx
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> dict[str, Any]:
        """Compute IO metrics from trajectory."""
        state = trajectory.final_state
        n_sectors = len(state.sector_output)
        
        # Generate sector names if not available
        sector_names = self._sector_names or [f"sector_{i}" for i in range(n_sectors)]
        
        # Use cached Leontief inverse if available
        if self._leontief_inverse is not None:
            L = self._leontief_inverse
            output_mult, va_mult, emp_mult = self._compute_multipliers(L)
            backward_idx, forward_idx = self._compute_linkages(L)
        else:
            # Synthetic multipliers from state
            output_mult = np.full(n_sectors, 2.0)  # Typical multiplier ~2
            va_mult = output_mult * 0.5
            emp_mult = output_mult / 1000
            backward_idx = np.ones(n_sectors)
            forward_idx = np.ones(n_sectors)
        
        # Identify key sectors (high backward AND forward)
        key_mask = (backward_idx > 1) & (forward_idx > 1)
        key_sectors = [sector_names[i] for i in range(n_sectors) if key_mask[i]]
        
        # Total output impact
        total_impact = float(np.sum(state.sector_output * output_mult))
        
        return IOMetrics(
            output_multipliers={sector_names[i]: float(output_mult[i]) for i in range(min(n_sectors, len(sector_names)))},
            employment_multipliers={sector_names[i]: float(emp_mult[i]) for i in range(min(n_sectors, len(sector_names)))},
            value_added_multipliers={sector_names[i]: float(va_mult[i]) for i in range(min(n_sectors, len(sector_names)))},
            type_ii_output_multipliers={},  # Requires household sector
            backward_linkages={sector_names[i]: float(backward_idx[i]) for i in range(min(n_sectors, len(sector_names)))},
            forward_linkages={sector_names[i]: float(forward_idx[i]) for i in range(min(n_sectors, len(sector_names)))},
            key_sectors=key_sectors,
            total_output_impact=total_impact,
            leontief_inverse=self._leontief_inverse,
        ).to_dict()
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return IO Tables dashboard specification.
        
        Input-Output analysis for economic impact and multiplier computation.
        """
        return FrameworkDashboardSpec(
            slug="io-tables",
            name="Input-Output Tables Analysis",
            description=(
                "Leontief Input-Output analysis for economic impact "
                "assessment, multipliers, and sectoral linkages."
            ),
            layer="meta",
            parameters_schema={
                "type": "object",
                "properties": {
                    "n_sectors": {
                        "type": "integer",
                        "title": "Number of Sectors",
                        "description": "Number of economic sectors in IO table",
                        "minimum": 2,
                        "maximum": 100,
                        "default": 20,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "io_structure",
                        "x-ui-order": 1,
                    },
                    "multiplier_type": {
                        "type": "string",
                        "title": "Multiplier Type",
                        "description": "Type of multiplier to compute",
                        "enum": ["type_i", "type_ii"],
                        "default": "type_i",
                        "x-ui-widget": "select",
                        "x-ui-group": "analysis",
                        "x-ui-order": 1,
                    },
                    "impact_analysis": {
                        "type": "string",
                        "title": "Impact Analysis",
                        "description": "Type of impact analysis to perform",
                        "enum": ["output", "employment", "value_added", "income"],
                        "default": "output",
                        "x-ui-widget": "select",
                        "x-ui-group": "analysis",
                        "x-ui-order": 2,
                    },
                },
                "required": ["n_sectors"],
            },
            default_parameters={
                "n_sectors": 20,
                "multiplier_type": "type_i",
                "impact_analysis": "output",
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="io_structure",
                    title="IO Table Structure",
                    description="Define the structure of the input-output table",
                    collapsed_by_default=False,
                ),
                ParameterGroupSpec(
                    key="analysis",
                    title="Analysis Configuration",
                    description="Configure multiplier and impact analysis",
                    collapsed_by_default=True,
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="io_matrix",
                    title="IO Matrix",
                    view_type=ViewType.TABLE,
                    description="Input-Output transaction matrix",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="io_matrix_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="multiplier_effects",
                    title="Multiplier Effects",
                    view_type=ViewType.BAR_CHART,
                    description="Sector multipliers (Type I/II)",
                result_class=ResultClass.DOMAIN_DECOMPOSITION,
                output_key="multiplier_effects_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="sector_linkages",
                    title="Sector Linkages",
                    view_type=ViewType.NETWORK,
                    description="Backward and forward linkage network",
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="sector_linkages_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
            min_tier=Tier.TEAM,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_multipliers(
        self,
        bundle: DataBundle,
        sector_names: Optional[list[str]] = None,
    ) -> IOMetrics:
        """
        Compute IO multipliers and linkages from IO table.
        
        Args:
            bundle: DataBundle with 'io_table' domain.
            sector_names: Optional list of sector names.
        
        Returns:
            IOMetrics with multipliers and linkage indices.
        """
        io_data = bundle.get("io_table") if bundle.has_domain("io_table") else None
        
        if io_data is None:
            return IOMetrics(
                output_multipliers={},
                employment_multipliers={},
                value_added_multipliers={},
                type_ii_output_multipliers={},
                backward_linkages={},
                forward_linkages={},
                key_sectors=[],
                total_output_impact=0.0,
                leontief_inverse=None,
            )
        
        df = io_data.data
        
        # Extract numeric columns for IO matrix
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        io_matrix = df[numeric_cols].values.astype(float)
        
        # Get sector names
        if sector_names is not None:
            self._sector_names = sector_names
        elif hasattr(df, "index") and df.index.dtype == object:
            self._sector_names = df.index.tolist()
        else:
            self._sector_names = numeric_cols
        
        n_sectors = io_matrix.shape[0]
        
        # Get total output (row sums if not provided)
        if "total_output" in df.columns:
            total_output = df["total_output"].values.astype(float)
        else:
            total_output = io_matrix.sum(axis=1)
        
        # Compute technical coefficients
        A = self._compute_technical_coefficients(io_matrix, total_output)
        
        # Compute Leontief inverse
        L = self._compute_leontief_inverse(A)
        self._leontief_inverse = L
        
        # Update transition function with Leontief inverse
        self._transition_fn = IOTransition(leontief_inverse=L)
        
        # Compute multipliers
        output_mult, va_mult, emp_mult = self._compute_multipliers(L)
        
        # Compute linkages
        backward_idx, forward_idx = self._compute_linkages(L)
        
        # Key sectors
        key_mask = (backward_idx > 1) & (forward_idx > 1)
        key_sectors = [self._sector_names[i] for i in range(n_sectors) if key_mask[i]]
        
        # Build metrics dict
        output_dict = {self._sector_names[i]: float(output_mult[i]) for i in range(n_sectors)}
        va_dict = {self._sector_names[i]: float(va_mult[i]) for i in range(n_sectors)}
        emp_dict = {self._sector_names[i]: float(emp_mult[i]) for i in range(n_sectors)}
        backward_dict = {self._sector_names[i]: float(backward_idx[i]) for i in range(n_sectors)}
        forward_dict = {self._sector_names[i]: float(forward_idx[i]) for i in range(n_sectors)}
        
        return IOMetrics(
            output_multipliers=output_dict,
            employment_multipliers=emp_dict,
            value_added_multipliers=va_dict,
            type_ii_output_multipliers={},
            backward_linkages=backward_dict,
            forward_linkages=forward_dict,
            key_sectors=key_sectors,
            total_output_impact=float(output_mult.sum()),
            leontief_inverse=L,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def impact_analysis(
        self,
        bundle: DataBundle,
        final_demand_change: np.ndarray,
    ) -> dict[str, Any]:
        """
        Compute economic impact of final demand change.
        
        Args:
            bundle: DataBundle with IO table.
            final_demand_change: Vector of final demand changes by sector.
        
        Returns:
            Dict with output, employment, and value-added impacts.
        """
        # Ensure Leontief inverse is computed
        if self._leontief_inverse is None:
            self.compute_multipliers(bundle)
        
        if self._leontief_inverse is None:
            return {"error": "Could not compute Leontief inverse"}
        
        L = self._leontief_inverse
        delta_y = np.asarray(final_demand_change)
        
        # Total output change: ΔX = L × ΔY
        delta_x = L @ delta_y
        
        # Compute impacts
        return {
            "output_change": {self._sector_names[i]: float(delta_x[i]) for i in range(len(delta_x))},
            "total_output_change": float(delta_x.sum()),
            "direct_effect": float(delta_y.sum()),
            "indirect_effect": float(delta_x.sum() - delta_y.sum()),
            "multiplier_effect": float(delta_x.sum() / delta_y.sum()) if delta_y.sum() != 0 else 0,
        }
