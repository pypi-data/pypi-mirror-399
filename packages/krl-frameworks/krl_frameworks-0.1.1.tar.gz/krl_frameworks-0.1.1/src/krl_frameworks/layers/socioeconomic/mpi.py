# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Multidimensional Poverty Index (MPI)
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Multidimensional Poverty Index (MPI) Framework.

The MPI is a deprivation-based poverty measure developed by UNDP and
Oxford Poverty & Human Development Initiative (OPHI). It assesses
poverty across three dimensions:

1. Health (2 indicators): Nutrition, Child Mortality
2. Education (2 indicators): Years of Schooling, School Attendance
3. Living Standards (6 indicators): Cooking Fuel, Sanitation, Water,
   Electricity, Housing, Assets

Methodology:
    - Uses Alkire-Foster (AF) method
    - Identifies who is poor (headcount) 
    - Measures intensity of poverty (avg deprivation share)
    - MPI = H × A (incidence × intensity)

CBSS Integration:
    - Computes per-cohort deprivation vectors
    - Tracks MPI evolution under policy shocks
    - Projects multidimensional poverty trends

References:
    - Alkire, S. & Foster, J. (2011). "Counting and Multidimensional 
      Poverty Measurement" Journal of Public Economics
    - UNDP Human Development Reports
    - OPHI Global MPI Methodology

Tier: COMMUNITY (individual index access)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np

from krl_frameworks.core.base import (
    BaseMetaFramework,
    FrameworkExecutionResult,
    FrameworkMetadata,
    VerticalLayer,
)
from krl_frameworks.core.capabilities import (
    CapabilityDeclaration,
    CapabilityScope,
    ConnectorRequirement,
    ModelZooRequirement,
)
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.core.data_bundle import DataBundle, DataDomain
from krl_frameworks.core.exceptions import (
    DataBundleValidationError,
    ExecutionError,
)
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["MPIFramework", "MPITransition", "MPIMetrics"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# MPI Configuration
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class MPIConfig:
    """
    Configuration for MPI computation.
    
    Attributes:
        poverty_cutoff: Threshold for being considered MPI-poor (k).
            Default 1/3 (deprived in at least 1/3 of weighted indicators).
        dimension_weights: Weights for [health, education, living_standards].
            Must sum to 1.0. Default equal weighting [1/3, 1/3, 1/3].
        indicator_weights: Per-dimension indicator weights.
        use_headcount_ratio: Whether to normalize by population.
    """
    
    poverty_cutoff: float = 1 / 3
    dimension_weights: tuple[float, float, float] = (1 / 3, 1 / 3, 1 / 3)
    use_headcount_ratio: bool = True
    
    # Standard MPI indicator weights (within each dimension)
    # Health: nutrition (1/6), child_mortality (1/6)
    # Education: years_schooling (1/6), school_attendance (1/6)
    # Living Standards: 6 indicators × (1/18) each
    indicator_weights: Mapping[str, float] = field(default_factory=lambda: {
        "nutrition": 1 / 6,
        "child_mortality": 1 / 6,
        "years_schooling": 1 / 6,
        "school_attendance": 1 / 6,
        "cooking_fuel": 1 / 18,
        "sanitation": 1 / 18,
        "drinking_water": 1 / 18,
        "electricity": 1 / 18,
        "housing": 1 / 18,
        "assets": 1 / 18,
    })
    
    def __post_init__(self):
        if not np.isclose(sum(self.dimension_weights), 1.0):
            raise ValueError("dimension_weights must sum to 1.0")
        if not 0 < self.poverty_cutoff <= 1:
            raise ValueError("poverty_cutoff must be in (0, 1]")


# ════════════════════════════════════════════════════════════════════════════════
# MPI Metrics
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class MPIMetrics:
    """
    Container for MPI computation results.
    
    Attributes:
        mpi: Multidimensional Poverty Index (H × A).
        headcount_ratio: Proportion of population that is MPI-poor (H).
        intensity: Average deprivation share among the poor (A).
        censored_headcount: Per-indicator contribution to MPI.
        dimensional_contribution: Contribution by dimension.
        n_poor: Number of poor cohorts.
        n_total: Total cohorts.
    """
    
    mpi: float
    headcount_ratio: float
    intensity: float
    censored_headcount: dict[str, float]
    dimensional_contribution: dict[str, float]
    n_poor: int
    n_total: int
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "mpi": self.mpi,
            "headcount_ratio": self.headcount_ratio,
            "intensity": self.intensity,
            "censored_headcount": self.censored_headcount,
            "dimensional_contribution": self.dimensional_contribution,
            "n_poor": self.n_poor,
            "n_total": self.n_total,
        }


# ════════════════════════════════════════════════════════════════════════════════
# MPI Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class MPITransition(TransitionFunction):
    """
    Transition function for MPI cohort state evolution.
    
    Models how deprivation indicators change over time based on:
    - Natural economic transitions
    - Policy intervention effects
    - Cross-dimensional spillovers
    
    The transition uses the CohortStateVector's deprivation_vector
    which maps to the 6 MPI deprivation dimensions.
    """
    
    name = "MPITransition"
    
    def __init__(
        self,
        natural_improvement_rate: float = 0.005,
        cross_spillover_rate: float = 0.1,
    ):
        """
        Initialize MPI transition.
        
        Args:
            natural_improvement_rate: Base improvement rate per period.
            cross_spillover_rate: How improvements in one dimension
                spill over to others.
        """
        self.natural_improvement_rate = natural_improvement_rate
        self.cross_spillover_rate = cross_spillover_rate
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: Optional[FrameworkConfig] = None,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """
        Apply MPI transition to evolve cohort deprivation.
        
        The transition:
        1. Applies natural improvement (gradual deprivation reduction)
        2. Computes cross-dimensional spillovers
        3. Updates health burden from deprivation average
        
        Args:
            state: Current cohort state.
            t: Time period.
            config: Framework configuration (optional).
            params: Optional MPI-specific parameters.
            
        Returns:
            Updated CohortStateVector.
        """
        params = params or {}
        improvement_rate = params.get(
            "improvement_rate", self.natural_improvement_rate
        )
        spillover = params.get("spillover_rate", self.cross_spillover_rate)
        
        # Get current deprivation (n_cohorts × n_dims)
        deprivation = state.deprivation_vector.copy()
        n_dims = deprivation.shape[1]
        
        # 1. Natural improvement (reduce deprivation)
        deprivation = deprivation * (1 - improvement_rate)
        
        # 2. Cross-dimensional spillover
        # Average deprivation improvement spreads to other dimensions
        if spillover > 0 and n_dims > 1:
            mean_dep = deprivation.mean(axis=1, keepdims=True)
            spillover_effect = spillover * (deprivation - mean_dep)
            deprivation = deprivation - spillover_effect
        
        # Clamp to [0, 1]
        deprivation = np.clip(deprivation, 0, 1)
        
        # 3. Update health burden from deprivation average
        # Higher deprivation → higher health burden
        avg_deprivation = deprivation.mean(axis=1)
        health_burden = np.clip(avg_deprivation * 0.8, 0, 1)
        
        # 4. Update opportunity score (inverse of deprivation)
        opportunity = np.clip(1 - avg_deprivation * 0.7, 0, 1)
        
        # Build updated state
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=health_burden,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=opportunity,
            sector_output=state.sector_output,
            deprivation_vector=deprivation,
        )


# ════════════════════════════════════════════════════════════════════════════════
# MPI Framework
# ════════════════════════════════════════════════════════════════════════════════


class MPIFramework(BaseMetaFramework):
    """
    Multidimensional Poverty Index (MPI) Framework.
    
    Implements the UNDP/OPHI Multidimensional Poverty Index using
    the Alkire-Foster method. Computes poverty headcount, intensity,
    and dimensional contributions.
    
    Community tier provides:
    - MPI computation from cohort data
    - Headcount ratio (H) and intensity (A)
    - Dimensional decomposition
    
    Integration Spine:
    - REQUIRES: health, education, housing data domains
    - OPTIONAL: time_series.arima for trend forecasting
    - METHODOLOGY: Alkire-Foster (internal, not from model zoo)
    
    Example:
        >>> bundle = DataBundle.from_dataframes({
        ...     "health": health_df,
        ...     "education": education_df,
        ...     "housing": housing_df,
        ... })
        >>> mpi = MPIFramework()
        >>> result = mpi.fit(bundle).simulate(n_periods=10)
        >>> print(result.metrics["mpi"])
    """
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Spine - Capability Declaration
    # ═══════════════════════════════════════════════════════════════════════════
    
    CAPABILITIES = CapabilityDeclaration(
        connectors=[
            # Required data domains for MPI computation
            ConnectorRequirement(
                domain="health",
                connector_type="census",  # Preferred connector
                scope=CapabilityScope.REQUIRED,
                min_observations=100,
                temporal_coverage=1,
                fallback_connectors=("bls", "worldbank"),
            ),
            ConnectorRequirement(
                domain="education",
                connector_type="census",
                scope=CapabilityScope.REQUIRED,
                min_observations=100,
                temporal_coverage=1,
                fallback_connectors=("worldbank",),
            ),
            ConnectorRequirement(
                domain="housing",
                connector_type="census",
                scope=CapabilityScope.REQUIRED,
                min_observations=100,
                temporal_coverage=1,
                fallback_connectors=("hud", "worldbank"),
            ),
        ],
        toolkits=[
            # MPI uses Alkire-Foster methodology internally
            # No external toolkit dependencies
        ],
        model_zoo=[
            # Optional ML augmentation for trend analysis
            ModelZooRequirement(
                category="time_series",
                model_type="arima",
                purpose="MPI trend forecasting",
                scope=CapabilityScope.OPTIONAL,
            ),
        ],
    )
    
    def __init__(self, mpi_config: Optional[MPIConfig] = None):
        """
        Initialize MPI Framework.
        
        Args:
            mpi_config: MPI-specific configuration. Defaults to
                standard UNDP/OPHI parameters.
        """
        super().__init__()
        self.mpi_config = mpi_config or MPIConfig()
        self._transition = MPITransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return MPI framework metadata."""
        return FrameworkMetadata(
            slug="mpi",
            name="Multidimensional Poverty Index",
            version="1.0.0",
            layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
            tier=Tier.COMMUNITY,
            description=(
                "UNDP/OPHI Multidimensional Poverty Index using "
                "Alkire-Foster methodology. Measures poverty across "
                "health, education, and living standards dimensions."
            ),
            required_domains=["health", "education", "housing"],
            output_domains=["mpi", "headcount_ratio", "intensity"],
            constituent_models=["alkire_foster", "deprivation_scorer"],
            tags=["socioeconomic", "poverty", "mpi", "multidimensional"],
            author="Khipu Research Labs",
            license="Apache-2.0",
        )
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return MPI dashboard specification.
        
        ════════════════════════════════════════════════════════════════════════════
        ██  CANONICAL REFERENCE — DO NOT DEVIATE  ██
        ════════════════════════════════════════════════════════════════════════════
        
        This dashboard_spec is the GOLD STANDARD for all framework specifications.
        All other frameworks must follow this exact pattern:
        
        1. PARAMETERS_SCHEMA: JSON Schema with proper types, bounds, defaults,
           x-ui-widget hints, and x-ui-group assignments
        
        2. DEFAULT_PARAMETERS: Dictionary containing actual framework defaults
           (NOT placeholders, NOT guesses — real values from the implementation)
        
        3. PARAMETER_GROUPS: Reference ONLY parameters that exist in schema
        
        4. OUTPUT_VIEWS: Each with key, title, view_type from ViewType enum
        
        When creating or updating any framework's dashboard_spec, compare against
        this implementation. The validation test at:
          tests/core/test_dashboard_spec_validation.py::test_mpi_is_canonical_reference
        ensures this remains the authoritative template.
        
        See: KRL_FORENSIC_AUDIT_REPORT.md for methodology.
        ════════════════════════════════════════════════════════════════════════════
        """
        return FrameworkDashboardSpec(
            slug="mpi",
            name="Multidimensional Poverty Index",
            description=(
                "Compute the UNDP/OPHI Multidimensional Poverty Index "
                "using Alkire-Foster methodology. Measure poverty across "
                "health, education, and living standards dimensions."
            ),
            layer="socioeconomic",
            parameters_schema={
                "type": "object",
                "properties": {
                    # Core Parameters
                    "poverty_cutoff": {
                        "type": "number",
                        "title": "Poverty Cutoff (k)",
                        "description": "Threshold for being MPI-poor (fraction of weighted indicators)",
                        "minimum": 0.1,
                        "maximum": 1.0,
                        "default": 0.333,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-group": "core",
                        "x-ui-order": 1,
                    },
                    # Dimension Weights
                    "health_weight": {
                        "type": "number",
                        "title": "Health Weight",
                        "description": "Weight for health dimension",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.333,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-group": "weights",
                        "x-ui-order": 1,
                    },
                    "education_weight": {
                        "type": "number",
                        "title": "Education Weight",
                        "description": "Weight for education dimension",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.333,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-group": "weights",
                        "x-ui-order": 2,
                    },
                    "living_standards_weight": {
                        "type": "number",
                        "title": "Living Standards Weight",
                        "description": "Weight for living standards dimension",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.333,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-group": "weights",
                        "x-ui-order": 3,
                    },
                    # Simulation
                    "n_periods": {
                        "type": "integer",
                        "title": "Projection Periods",
                        "description": "Number of periods to project",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-unit": "years",
                        "x-ui-group": "simulation",
                        "x-ui-order": 1,
                    },
                    "improvement_rate": {
                        "type": "number",
                        "title": "Natural Improvement Rate",
                        "description": "Base annual improvement in deprivation",
                        "minimum": 0,
                        "maximum": 0.05,
                        "default": 0.005,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.001,
                        "x-ui-unit": "%",
                        "x-ui-format": ".1%",
                        "x-ui-group": "simulation",
                        "x-ui-order": 2,
                    },
                },
                "required": [],
            },
            default_parameters={
                "poverty_cutoff": 0.333,
                "health_weight": 0.333,
                "education_weight": 0.333,
                "living_standards_weight": 0.333,
                "n_periods": 10,
                "improvement_rate": 0.005,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="core",
                    title="Core Settings",
                    description="Poverty threshold and methodology",
                    collapsed_by_default=False,
                    parameters=["poverty_cutoff"],
                ),
                ParameterGroupSpec(
                    key="weights",
                    title="Dimension Weights",
                    description="Weights for each dimension (should sum to 1)",
                    collapsed_by_default=False,
                    parameters=["health_weight", "education_weight", "living_standards_weight"],
                ),
                ParameterGroupSpec(
                    key="simulation",
                    title="Simulation",
                    description="Projection settings",
                    collapsed_by_default=True,
                    parameters=["n_periods", "improvement_rate"],
                ),
            ],
            required_domains=["health", "education", "housing"],
            min_tier=Tier.COMMUNITY,
            output_views=[
                # MPI Score Gauge
                OutputViewSpec(
                    key="mpi_score",
                    title="MPI Score",
                    view_type=ViewType.GAUGE,
                    description="Overall Multidimensional Poverty Index",
                    config={
                        "min": 0,
                        "max": 1,
                        "thresholds": [0.1, 0.3, 0.5],
                        "colors": ["#22c55e", "#f59e0b", "#ef4444"],
                        "format": ".3f",
                    },
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="mpi_score_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # Summary Metrics
                OutputViewSpec(
                    key="summary",
                    title="Summary",
                    view_type=ViewType.METRIC_GRID,
                    description="Key MPI components",
                    config={
                        "metrics": [
                            {"key": "mpi", "label": "MPI", "format": ".3f"},
                            {"key": "headcount_ratio", "label": "Headcount (H)", "format": ".1%"},
                            {"key": "intensity", "label": "Intensity (A)", "format": ".1%"},
                            {"key": "n_poor", "label": "Poor Population", "format": ","},
                        ]
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="summary_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # Dimensional Contribution
                OutputViewSpec(
                    key="dimensional_contribution",
                    title="Dimensions",
                    view_type=ViewType.BAR_CHART,
                    description="Contribution to MPI by dimension",
                    config={
                        "x_axis": "Dimension",
                        "y_axis": "Contribution (%)",
                        "colors": ["#3b82f6", "#22c55e", "#f59e0b"],
                    },
                result_class=ResultClass.DOMAIN_DECOMPOSITION,
                output_key="dimensional_contribution_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # Indicator Breakdown
                OutputViewSpec(
                    key="censored_headcount",
                    title="Indicators",
                    view_type=ViewType.BAR_CHART,
                    description="Censored headcount by indicator",
                    config={
                        "orientation": "horizontal",
                        "x_axis": "Headcount Ratio",
                        "y_axis": "Indicator",
                    },
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="censored_headcount_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # MPI Trajectory
                OutputViewSpec(
                    key="mpi_trajectory",
                    title="Trend",
                    view_type=ViewType.LINE_CHART,
                    description="MPI evolution over projection period",
                    config={
                        "x_axis": "Year",
                        "y_axis": "MPI",
                        "series": [
                            {"key": "mpi", "label": "MPI"},
                            {"key": "headcount_ratio", "label": "Headcount"},
                        ],
                    },
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="mpi_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # Data Table
                OutputViewSpec(
                    key="detailed_results",
                    title="Data",
                    view_type=ViewType.TABLE,
                    description="Full indicator data",
                    config={
                        "columns": [
                            {"key": "indicator", "label": "Indicator"},
                            {"key": "headcount", "label": "Headcount", "format": ".2%"},
                            {"key": "contribution", "label": "Contribution", "format": ".2%"},
                            {"key": "weight", "label": "Weight", "format": ".3f"},
                        ],
                        "sortable": True,
                    },
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="detailed_results_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
            documentation_url="https://docs.khipuresearch.com/frameworks/mpi",
            example_config={
                "poverty_cutoff": 0.333,
                "n_periods": 10,
            },
        )
    
    def _validate_bundle(self, bundle: DataBundle) -> None:
        """Validate that bundle contains required MPI domains."""
        required = {DataDomain.HEALTH, DataDomain.EDUCATION, DataDomain.HOUSING}
        available = set(bundle.domains.keys())
        
        # Map string keys to domains
        domain_names = {"health", "education", "housing"}
        missing = domain_names - available
        
        if missing:
            raise DataBundleValidationError(
                f"MPI requires domains: {domain_names}. Missing: {missing}"
            )
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
    ) -> CohortStateVector:
        """
        Compute initial cohort state from data bundle.
        
        Extracts deprivation indicators from health, education,
        and housing domains to construct initial deprivation vector.
        """
        self._validate_bundle(bundle)
        
        # Extract domain data
        health = bundle.get("health").data
        education = bundle.get("education").data
        housing = bundle.get("housing").data
        
        # Determine cohort count (use smallest dataset)
        n_cohorts = min(len(health), len(education), len(housing))
        
        # Extract deprivation indicators (normalize to [0, 1])
        # Higher values = more deprived
        
        # Health dimension (2 indicators mapped to 1)
        health_dep = self._compute_health_deprivation(health, n_cohorts)
        
        # Education dimension (2 indicators mapped to 1)
        education_dep = self._compute_education_deprivation(education, n_cohorts)
        
        # Living standards (6 indicators mapped to 4 in simplified version)
        living_dep = self._compute_living_deprivation(housing, n_cohorts)
        
        # Stack into deprivation vector [n_cohorts × 6]
        deprivation_vector = np.column_stack([
            health_dep,
            education_dep,
            living_dep,
        ])
        
        # Compute derived state fields
        avg_dep = deprivation_vector.mean(axis=1)
        
        return CohortStateVector(
            employment_prob=np.clip(1 - avg_dep * 0.5, 0.3, 0.95),
            health_burden_score=np.clip(health_dep, 0, 1),
            credit_access_prob=np.clip(1 - avg_dep * 0.6, 0.2, 0.9),
            housing_cost_ratio=np.clip(living_dep.mean(axis=1) * 0.5, 0.1, 0.6),
            opportunity_score=np.clip(1 - avg_dep * 0.7, 0.2, 0.8),
            sector_output=np.zeros((n_cohorts, 10)),  # Not used for MPI
            deprivation_vector=deprivation_vector,
        )
    
    def _compute_health_deprivation(
        self, health_df, n_cohorts: int
    ) -> np.ndarray:
        """Compute health deprivation from health data."""
        # Use mortality rate or health burden if available
        if "mortality_rate" in health_df.columns:
            # Normalize mortality to [0, 1] deprivation
            mortality = health_df["mortality_rate"].values[:n_cohorts]
            return np.clip(mortality * 50, 0, 1)  # Scale up small rates
        elif "health_burden" in health_df.columns:
            return np.clip(health_df["health_burden"].values[:n_cohorts], 0, 1)
        else:
            # Default moderate deprivation
            return np.full(n_cohorts, 0.3)
    
    def _compute_education_deprivation(
        self, education_df, n_cohorts: int
    ) -> np.ndarray:
        """Compute education deprivation from education data."""
        if "hs_graduation_rate" in education_df.columns:
            # Low graduation = high deprivation
            graduation = education_df["hs_graduation_rate"].values[:n_cohorts]
            return np.clip(1 - graduation, 0, 1)
        elif "years_schooling" in education_df.columns:
            # Less than 6 years = deprived
            years = education_df["years_schooling"].values[:n_cohorts]
            return np.clip(1 - years / 12, 0, 1)
        else:
            return np.full(n_cohorts, 0.25)
    
    def _compute_living_deprivation(
        self, housing_df, n_cohorts: int
    ) -> np.ndarray:
        """Compute living standards deprivation (4 sub-dimensions)."""
        dims = []
        
        # Housing quality
        if "housing_quality" in housing_df.columns:
            dims.append(1 - housing_df["housing_quality"].values[:n_cohorts])
        else:
            dims.append(np.full(n_cohorts, 0.2))
        
        # Sanitation
        if "sanitation_access" in housing_df.columns:
            dims.append(1 - housing_df["sanitation_access"].values[:n_cohorts])
        else:
            dims.append(np.full(n_cohorts, 0.15))
        
        # Water
        if "water_access" in housing_df.columns:
            dims.append(1 - housing_df["water_access"].values[:n_cohorts])
        else:
            dims.append(np.full(n_cohorts, 0.1))
        
        # Electricity/utilities
        if "electricity_access" in housing_df.columns:
            dims.append(1 - housing_df["electricity_access"].values[:n_cohorts])
        else:
            dims.append(np.full(n_cohorts, 0.1))
        
        return np.column_stack([np.clip(d, 0, 1) for d in dims])
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
    ) -> CohortStateVector:
        """Apply MPI transition function."""
        return self._transition_fn(state, t, self.config)
    
    @property
    def _transition_fn(self) -> MPITransition:
        """Get transition function (avoid name collision)."""
        return MPITransition()
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """
        Compute MPI metrics from final state.
        
        Uses final state to compute:
        - MPI (H × A)
        - Headcount ratio (H)
        - Intensity (A)
        - Dimensional contributions
        """
        return self._compute_mpi_from_state(state).to_dict()
    
    def _compute_mpi_from_state(
        self,
        state: CohortStateVector,
    ) -> MPIMetrics:
        """
        Compute MPI metrics from cohort state.
        
        Uses Alkire-Foster methodology:
        1. Compute weighted deprivation score per cohort
        2. Identify poor (score >= poverty_cutoff)
        3. Compute headcount ratio H = n_poor / n_total
        4. Compute intensity A = avg(deprivation | poor)
        5. MPI = H × A
        """
        deprivation = state.deprivation_vector
        n_cohorts = state.n_cohorts
        n_dims = deprivation.shape[1]
        
        # Weighted deprivation score per cohort
        # Equal weighting across available dimensions
        weights = np.ones(n_dims) / n_dims
        weighted_dep = (deprivation * weights).sum(axis=1)
        
        # Identify poor cohorts
        k = self.mpi_config.poverty_cutoff
        is_poor = weighted_dep >= k
        n_poor = int(is_poor.sum())
        
        # Headcount ratio
        H = n_poor / n_cohorts if n_cohorts > 0 else 0.0
        
        # Intensity (average deprivation among poor)
        if n_poor > 0:
            A = weighted_dep[is_poor].mean()
        else:
            A = 0.0
        
        # MPI
        mpi = H * A
        
        # Dimensional contributions
        dim_names = ["health", "education", "housing_quality", 
                     "sanitation", "water", "electricity"][:n_dims]
        dimensional_contribution = {}
        censored_headcount = {}
        
        for i, name in enumerate(dim_names):
            if n_poor > 0:
                # Censored headcount: avg deprivation in dim i among poor
                censored = deprivation[is_poor, i].mean() * H
                contrib = (weights[i] * censored) / mpi if mpi > 0 else 0
            else:
                censored = 0.0
                contrib = 0.0
            
            censored_headcount[name] = censored
            dimensional_contribution[name] = contrib
        
        return MPIMetrics(
            mpi=mpi,
            headcount_ratio=H,
            intensity=A,
            censored_headcount=censored_headcount,
            dimensional_contribution=dimensional_contribution,
            n_poor=n_poor,
            n_total=n_cohorts,
        )
    
    def compute_mpi(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> MPIMetrics:
        """
        Compute MPI directly from data bundle (no simulation).
        
        Convenience method for one-shot MPI computation.
        
        Args:
            bundle: Data bundle with health, education, housing.
            config: Optional configuration.
            
        Returns:
            MPIMetrics with MPI, H, A, and decomposition.
        """
        from krl_frameworks.core.config import FrameworkConfig
        config = config or FrameworkConfig()
        self.config = config  # Store for use in _compute_initial_state
        
        state = self._compute_initial_state(bundle)
        return self._compute_mpi_from_state(state)
