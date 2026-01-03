# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Gender Inequality Index (GII)
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Gender Inequality Index (GII) Framework.

GII measures gender-based disadvantage across three dimensions:
reproductive health, empowerment, and the labor market. It shows
the loss in potential human development due to inequality between
female and male achievements.

Core Methodology:
    1. Compute female and male indices for each dimension
    2. Aggregate using geometric means (separate by gender)
    3. Compute harmonic mean of gender indices
    4. GII = 1 - (harmonic_mean / reference standard)

Three Dimensions:
    - Reproductive Health: MMR, AFR
    - Empowerment: Female parliament share, secondary education
    - Labor Market: Female labor force participation

References:
    - UNDP Human Development Report Technical Notes
    - Seth, S. (2009). "Inequality, Interactions and Human Development"
    - Klasen, S. & Schüler, D. (2011). "Reforming the GII"

Tier: COMMUNITY
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np

from krl_frameworks.core.base import (
    BaseMetaFramework,
    FrameworkMetadata,
    VerticalLayer,
)
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    ParameterGroupSpec,
    OutputViewSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["GIIFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# GII Data Structures
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class GIIDimensions:
    """Input data for GII calculation by dimension."""
    
    # Reproductive Health (female only)
    maternal_mortality_ratio: float = 0.0  # per 100,000 live births
    adolescent_birth_rate: float = 0.0     # per 1,000 women ages 15-19
    
    # Empowerment
    female_parliament_share: float = 0.0   # proportion (0-1)
    male_parliament_share: float = 0.0     # proportion (0-1)
    female_secondary_education: float = 0.0  # proportion with at least secondary
    male_secondary_education: float = 0.0
    
    # Labor Market
    female_labor_force_participation: float = 0.0  # proportion (0-1)
    male_labor_force_participation: float = 0.0


@dataclass
class GIIMetrics:
    """
    Container for GII computation results.
    
    Attributes:
        gii: Gender Inequality Index (0-1, higher = more inequality)
        female_index: Aggregate female achievement index
        male_index: Aggregate male achievement index
        health_female: Female reproductive health index
        empowerment_female: Female empowerment index
        empowerment_male: Male empowerment index
        labor_female: Female labor market index
        labor_male: Male labor market index
        harmonic_mean: Harmonic mean of gender indices
        reference: Reference standard (geometric mean of equally distributed)
    """
    
    gii: float = 0.0
    
    # Gender-specific aggregates
    female_index: float = 0.0
    male_index: float = 0.0
    
    # Dimension indices
    health_female: float = 0.0
    empowerment_female: float = 0.0
    empowerment_male: float = 0.0
    labor_female: float = 0.0
    labor_male: float = 0.0
    
    # Aggregation components
    harmonic_mean: float = 0.0
    reference: float = 0.0
    
    # Decomposition
    health_contribution: float = 0.0
    empowerment_contribution: float = 0.0
    labor_contribution: float = 0.0


@dataclass
class GIIComparison:
    """Comparison of GII across regions/time."""
    
    region_name: str = ""
    gii: float = 0.0
    rank: int = 0
    
    # Relative to best/worst
    gap_to_best: float = 0.0
    gap_to_worst: float = 0.0
    
    # Change over time
    change_from_previous: float = 0.0
    change_pct: float = 0.0


# ════════════════════════════════════════════════════════════════════════════════
# GII Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class GIITransition(TransitionFunction):
    """
    Transition function for gender inequality dynamics.
    
    Models the evolution of gender gaps across dimensions
    with policy interventions and demographic changes.
    """
    
    name = "GIITransition"
    
    def __init__(
        self,
        convergence_rate: float = 0.02,
        policy_impact: float = 0.05,
    ):
        self.convergence_rate = convergence_rate
        self.policy_impact = policy_impact
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply gender gap transition dynamics."""
        params = params or {}
        
        n_cohorts = state.n_cohorts
        
        # Policy intervention indicator
        policy_intervention = params.get("policy_intervention", 0.0)
        
        # Gender gap converges over time (opportunity score as proxy)
        gap_reduction = self.convergence_rate + policy_intervention * self.policy_impact
        
        # Improve opportunity (reduce inequality)
        new_opportunity = np.clip(
            state.opportunity_score + gap_reduction * (1 - state.opportunity_score),
            0.0, 1.0
        )
        
        # Employment follows (with lag)
        new_employment = np.clip(
            state.employment_prob + gap_reduction * 0.5 * (new_opportunity - state.employment_prob),
            0.0, 1.0
        )
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Gender Inequality Index Framework
# ════════════════════════════════════════════════════════════════════════════════


class GIIFramework(BaseMetaFramework):
    """
    Gender Inequality Index (GII) Framework.
    
    Production-grade implementation of the UNDP Gender Inequality Index,
    measuring gender-based disadvantage across three dimensions:
    
    - Reproductive Health (MMR, adolescent birth rate)
    - Empowerment (parliament share, secondary education)
    - Labor Market (labor force participation)
    
    Token Weight: 3
    Tier: COMMUNITY
    
    Example:
        >>> framework = GIIFramework()
        >>> result = framework.compute_gii(
        ...     maternal_mortality_ratio=19,
        ...     adolescent_birth_rate=21,
        ...     female_parliament_share=0.21,
        ...     female_secondary_education=0.95,
        ...     male_secondary_education=0.94,
        ...     female_labor_force=0.56,
        ...     male_labor_force=0.69,
        ... )
        >>> print(f"GII: {result.gii:.3f}")
    
    References:
        - UNDP HDR Technical Notes (2020)
        - Seth (2009): Inequality, Interactions and Human Development
    """
    
    METADATA = FrameworkMetadata(
        slug="gii",
        name="Gender Inequality Index",
        version="1.0.0",
        layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
        tier=Tier.COMMUNITY,
        description=(
            "UNDP Gender Inequality Index measuring gender-based "
            "disadvantage in health, empowerment, and labor market."
        ),
        required_domains=["demographic", "health", "education", "labor"],
        output_domains=["gii", "gender_gaps", "dimension_indices"],
        constituent_models=["health_index", "empowerment_index", "labor_index"],
        tags=["gender", "inequality", "development", "undp", "sdg-5"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    # Normalization parameters (UNDP methodology)
    MMR_MIN = 10.0      # Minimum maternal mortality ratio
    MMR_MAX = 1000.0    # Maximum maternal mortality ratio
    AFR_MIN = 1.0       # Minimum adolescent fertility rate
    AFR_MAX = 200.0     # Maximum adolescent fertility rate
    
    def __init__(self):
        super().__init__()
        self._transition_fn = GIITransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return framework metadata."""
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Initialize state from demographic data."""
        n_cohorts = config.cohort_size or 100
        
        # Initialize with moderate gender inequality
        return CohortStateVector(
            employment_prob=np.random.beta(5, 3, n_cohorts),  # female employment
            health_burden_score=np.random.beta(2, 8, n_cohorts),  # lower = better
            credit_access_prob=np.random.beta(4, 4, n_cohorts),
            housing_cost_ratio=np.full(n_cohorts, 0.30),
            opportunity_score=np.random.beta(4, 4, n_cohorts),
            sector_output=np.full((n_cohorts, 5), 1000.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.25),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply GII transition dynamics."""
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """Compute GII-relevant metrics from state."""
        return {
            "mean_opportunity": float(np.mean(state.opportunity_score)),
            "mean_employment": float(np.mean(state.employment_prob)),
            "health_burden": float(np.mean(state.health_burden_score)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        """Compute final output from trajectory."""
        return {
            "framework": "gii",
            "n_periods": trajectory.n_periods,
        }
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    def _normalize_health(
        self,
        mmr: float,
        afr: float,
    ) -> float:
        """
        Normalize reproductive health indicators.
        
        Uses geometric mean of normalized MMR and AFR.
        """
        # Normalize MMR (higher is worse, so invert)
        mmr_norm = 10 / np.clip(mmr, self.MMR_MIN, self.MMR_MAX)
        
        # Normalize AFR (higher is worse)
        afr_norm = (self.AFR_MAX - np.clip(afr, self.AFR_MIN, self.AFR_MAX)) / (self.AFR_MAX - self.AFR_MIN)
        
        # Geometric mean
        return np.sqrt(mmr_norm * afr_norm)
    
    def _normalize_empowerment(
        self,
        parliament_share: float,
        secondary_education: float,
    ) -> float:
        """
        Normalize empowerment indicators.
        
        Uses geometric mean of parliament share and education.
        """
        # Ensure floor values
        parliament = max(parliament_share, 0.001)
        education = max(secondary_education, 0.001)
        
        return np.sqrt(parliament * education)
    
    def _normalize_labor(
        self,
        labor_force_participation: float,
    ) -> float:
        """Normalize labor market participation."""
        return np.clip(labor_force_participation, 0.001, 1.0)
    
    def compute_gii(
        self,
        maternal_mortality_ratio: float,
        adolescent_birth_rate: float,
        female_parliament_share: float,
        female_secondary_education: float,
        male_secondary_education: float,
        female_labor_force: float,
        male_labor_force: float,
        *,
        male_parliament_share: Optional[float] = None,
    ) -> GIIMetrics:
        """
        Compute Gender Inequality Index.
        
        Args:
            maternal_mortality_ratio: Deaths per 100,000 live births
            adolescent_birth_rate: Births per 1,000 women ages 15-19
            female_parliament_share: Share of parliament seats (0-1)
            female_secondary_education: Share with secondary education (0-1)
            male_secondary_education: Share with secondary education (0-1)
            female_labor_force: Labor force participation rate (0-1)
            male_labor_force: Labor force participation rate (0-1)
            male_parliament_share: Optional, defaults to 1 - female
        
        Returns:
            GII metrics with dimension breakdowns
        """
        # Default male parliament share
        if male_parliament_share is None:
            male_parliament_share = 1.0 - female_parliament_share
        
        # Step 1: Compute dimension indices
        
        # Health (female only - geometric mean of normalized MMR and AFR)
        health_f = self._normalize_health(maternal_mortality_ratio, adolescent_birth_rate)
        
        # Empowerment indices
        empowerment_f = self._normalize_empowerment(female_parliament_share, female_secondary_education)
        empowerment_m = self._normalize_empowerment(male_parliament_share, male_secondary_education)
        
        # Labor indices
        labor_f = self._normalize_labor(female_labor_force)
        labor_m = self._normalize_labor(male_labor_force)
        
        # Step 2: Aggregate to gender indices (geometric mean across dimensions)
        # Female: geometric mean of health, empowerment, labor
        female_index = (health_f * empowerment_f * labor_f) ** (1/3)
        
        # Male: geometric mean of 1 (health placeholder), empowerment, labor
        # Note: For males, health is set to 1 as reproductive health applies only to females
        male_index = (1.0 * empowerment_m * labor_m) ** (1/3)
        
        # Step 3: Compute harmonic mean of gender indices
        if female_index > 0 and male_index > 0:
            harmonic_mean = 2 / (1/female_index + 1/male_index)
        else:
            harmonic_mean = 0.0
        
        # Step 4: Compute reference (equally distributed)
        # Average of dimensions then geometric mean
        health_avg = health_f  # Only female for health
        empowerment_avg = (empowerment_f + empowerment_m) / 2
        labor_avg = (labor_f + labor_m) / 2
        
        reference = (health_avg * empowerment_avg * labor_avg) ** (1/3)
        
        # Step 5: GII = 1 - (harmonic_mean / reference)
        if reference > 0:
            gii = 1 - harmonic_mean / reference
        else:
            gii = 1.0
        
        gii = np.clip(gii, 0.0, 1.0)
        
        # Compute dimension contributions
        total_gap = (
            abs(empowerment_f - empowerment_m) + 
            abs(labor_f - labor_m) + 
            (1 - health_f)  # Health gap from ideal
        )
        
        if total_gap > 0:
            health_contribution = (1 - health_f) / total_gap
            empowerment_contribution = abs(empowerment_f - empowerment_m) / total_gap
            labor_contribution = abs(labor_f - labor_m) / total_gap
        else:
            health_contribution = empowerment_contribution = labor_contribution = 1/3
        
        return GIIMetrics(
            gii=float(gii),
            female_index=float(female_index),
            male_index=float(male_index),
            health_female=float(health_f),
            empowerment_female=float(empowerment_f),
            empowerment_male=float(empowerment_m),
            labor_female=float(labor_f),
            labor_male=float(labor_m),
            harmonic_mean=float(harmonic_mean),
            reference=float(reference),
            health_contribution=float(health_contribution),
            empowerment_contribution=float(empowerment_contribution),
            labor_contribution=float(labor_contribution),
        )
    
    def compute_gii_from_dimensions(
        self,
        dimensions: GIIDimensions,
    ) -> GIIMetrics:
        """
        Compute GII from a GIIDimensions object.
        
        Args:
            dimensions: All input data in a structured object
        
        Returns:
            GII metrics
        """
        return self.compute_gii(
            maternal_mortality_ratio=dimensions.maternal_mortality_ratio,
            adolescent_birth_rate=dimensions.adolescent_birth_rate,
            female_parliament_share=dimensions.female_parliament_share,
            female_secondary_education=dimensions.female_secondary_education,
            male_secondary_education=dimensions.male_secondary_education,
            female_labor_force=dimensions.female_labor_force_participation,
            male_labor_force=dimensions.male_labor_force_participation,
            male_parliament_share=dimensions.male_parliament_share,
        )
    
    def compare_regions(
        self,
        regions: dict[str, GIIDimensions],
    ) -> list[GIIComparison]:
        """
        Compare GII across multiple regions.
        
        Args:
            regions: Dict of region_name -> GIIDimensions
        
        Returns:
            List of GIIComparison objects ranked by GII
        """
        # Compute GII for each region
        results = {}
        for name, dims in regions.items():
            metrics = self.compute_gii_from_dimensions(dims)
            results[name] = metrics.gii
        
        # Sort by GII (lower is better)
        sorted_regions = sorted(results.items(), key=lambda x: x[1])
        
        best_gii = sorted_regions[0][1] if sorted_regions else 0.0
        worst_gii = sorted_regions[-1][1] if sorted_regions else 1.0
        
        comparisons = []
        for rank, (name, gii) in enumerate(sorted_regions, 1):
            comparisons.append(GIIComparison(
                region_name=name,
                gii=float(gii),
                rank=rank,
                gap_to_best=float(gii - best_gii),
                gap_to_worst=float(worst_gii - gii),
            ))
        
        return comparisons
    
    def simulate_policy_impact(
        self,
        baseline: GIIDimensions,
        policy_effects: dict[str, float],
        years: int = 10,
    ) -> list[GIIMetrics]:
        """
        Simulate GII trajectory under policy intervention.
        
        Args:
            baseline: Starting GII dimensions
            policy_effects: Dict of dimension -> annual improvement rate
            years: Number of years to simulate
        
        Returns:
            List of GIIMetrics for each year
        """
        trajectory = []
        current = baseline
        
        for year in range(years + 1):
            metrics = self.compute_gii_from_dimensions(current)
            trajectory.append(metrics)
            
            if year < years:
                # Apply policy effects
                current = GIIDimensions(
                    maternal_mortality_ratio=max(
                        self.MMR_MIN,
                        current.maternal_mortality_ratio * (1 - policy_effects.get("mmr_reduction", 0))
                    ),
                    adolescent_birth_rate=max(
                        self.AFR_MIN,
                        current.adolescent_birth_rate * (1 - policy_effects.get("afr_reduction", 0))
                    ),
                    female_parliament_share=min(
                        0.5,
                        current.female_parliament_share + policy_effects.get("parliament_increase", 0)
                    ),
                    male_parliament_share=max(
                        0.5,
                        current.male_parliament_share - policy_effects.get("parliament_increase", 0)
                    ),
                    female_secondary_education=min(
                        1.0,
                        current.female_secondary_education + policy_effects.get("education_increase", 0)
                    ),
                    male_secondary_education=current.male_secondary_education,
                    female_labor_force_participation=min(
                        1.0,
                        current.female_labor_force_participation + policy_effects.get("labor_increase", 0)
                    ),
                    male_labor_force_participation=current.male_labor_force_participation,
                )

        return trajectory

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return GII dashboard specification.

        Parameters extracted from GIITransition (lines 157-163) and methodology constants.
        GII is primarily a calculation framework with minimal configurable parameters.
        """
        return FrameworkDashboardSpec(
            slug="gii",
            name="Gender Inequality Index",
            description=(
                "UNDP Gender Inequality Index measuring gender-based disadvantage in "
                "reproductive health, empowerment, and labor market participation."
            ),
            layer="socioeconomic",
            min_tier=Tier.COMMUNITY,
            parameters_schema={
                "type": "object",
                "properties": {
                    # Transition Parameters
                    "convergence_rate": {
                        "type": "number",
                        "title": "Natural Convergence Rate",
                        "description": "Annual rate of gender gap reduction without interventions",
                        "minimum": 0.0,
                        "maximum": 0.10,
                        "default": 0.02,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-unit": "%",
                        "x-ui-format": ".1%",
                        "x-ui-group": "dynamics",
                        "x-ui-order": 1,
                    },
                    "policy_impact": {
                        "type": "number",
                        "title": "Policy Impact Multiplier",
                        "description": "Amplification of gender gap reduction from policy interventions",
                        "minimum": 0.0,
                        "maximum": 0.20,
                        "default": 0.05,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-group": "dynamics",
                        "x-ui-order": 2,
                    },
                    # Normalization Bounds (UNDP methodology)
                    "mmr_min": {
                        "type": "number",
                        "title": "MMR Min (Normalization)",
                        "description": "Minimum maternal mortality ratio for normalization",
                        "minimum": 1.0,
                        "maximum": 50.0,
                        "default": 10.0,
                        "x-ui-widget": "number",
                        "x-ui-unit": "per 100k",
                        "x-ui-group": "normalization",
                        "x-ui-order": 1,
                    },
                    "mmr_max": {
                        "type": "number",
                        "title": "MMR Max (Normalization)",
                        "description": "Maximum maternal mortality ratio for normalization",
                        "minimum": 100.0,
                        "maximum": 2000.0,
                        "default": 1000.0,
                        "x-ui-widget": "number",
                        "x-ui-unit": "per 100k",
                        "x-ui-group": "normalization",
                        "x-ui-order": 2,
                    },
                },
                "required": [],
            },
            default_parameters={
                "convergence_rate": 0.02,
                "policy_impact": 0.05,
                "mmr_min": 10.0,
                "mmr_max": 1000.0,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="dynamics",
                    title="Gender Gap Dynamics",
                    description="Convergence and policy impact settings",
                    collapsed_by_default=False,
                    parameters=["convergence_rate", "policy_impact"],
                ),
                ParameterGroupSpec(
                    key="normalization",
                    title="Normalization Bounds",
                    description="UNDP methodology bounds for indicator normalization",
                    collapsed_by_default=True,
                    parameters=["mmr_min", "mmr_max"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="gii_score",
                    title="GII Score",
                    view_type=ViewType.GAUGE,
                    description="Overall Gender Inequality Index (0-1, lower is better)",
                result_class=ResultClass.SCALAR_INDEX,
                output_key="gii_score_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="dimension_indices",
                    title="Dimension Scores",
                    view_type=ViewType.BAR_CHART,
                    description="Health, empowerment, and labor market indices",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="dimension_indices_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="gender_gaps",
                    title="Gender Gaps by Indicator",
                    view_type=ViewType.BAR_CHART,
                    description="Male-female gaps across all indicators",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="gender_gaps_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="gii_trajectory",
                    title="GII Over Time",
                    view_type=ViewType.TIMESERIES,
                    description="Historical and projected gender inequality",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="gii_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="decomposition_table",
                    title="GII Decomposition",
                    view_type=ViewType.TABLE,
                    description="Contribution of each dimension to overall GII",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="decomposition_table_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
