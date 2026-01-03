# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Human Development Index (HDI)
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Human Development Index (HDI) Framework.

The HDI is a composite index developed by UNDP measuring average
achievement in three key dimensions of human development:

1. Long and Healthy Life: Life expectancy at birth
2. Knowledge: Mean years of schooling + Expected years of schooling
3. Decent Standard of Living: GNI per capita (PPP $)

Methodology:
    - Each dimension normalized to [0, 1] using goalposts
    - HDI = geometric mean of three dimension indices
    - Classifications: Low (<0.55), Medium (0.55-0.7), High (0.7-0.8), 
      Very High (≥0.8)

CBSS Integration:
    - Tracks HDI components per cohort over time
    - Models education and health improvements
    - Projects income growth trajectories

References:
    - UNDP Human Development Report Technical Notes
    - Sen, A. (1999). "Development as Freedom"

Tier: COMMUNITY (individual index access)
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
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.core.data_bundle import DataBundle, DataDomain
from krl_frameworks.core.exceptions import DataBundleValidationError
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["HDIFramework", "HDITransition", "HDIMetrics"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# HDI Goalposts (UNDP 2022 methodology)
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class HDIGoalposts:
    """
    UNDP-defined goalposts for HDI normalization.
    
    Each dimension is normalized using:
        index = (observed - min) / (max - min)
    
    For income (GNI), log transformation is applied first.
    """
    
    # Life expectancy (years)
    life_expectancy_min: float = 20.0
    life_expectancy_max: float = 85.0
    
    # Mean years of schooling
    schooling_mean_min: float = 0.0
    schooling_mean_max: float = 15.0
    
    # Expected years of schooling
    schooling_expected_min: float = 0.0
    schooling_expected_max: float = 18.0
    
    # GNI per capita (PPP $) - log transformed
    gni_min: float = 100.0
    gni_max: float = 75000.0


# ════════════════════════════════════════════════════════════════════════════════
# HDI Metrics
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class HDIMetrics:
    """
    Container for HDI computation results.
    
    Attributes:
        hdi: Human Development Index (geometric mean).
        health_index: Life expectancy dimension index.
        education_index: Education dimension index.
        income_index: GNI dimension index.
        classification: Development classification.
        component_values: Raw component values.
    """
    
    hdi: float
    health_index: float
    education_index: float
    income_index: float
    classification: str
    component_values: dict[str, float]
    
    @classmethod
    def classify(cls, hdi: float) -> str:
        """Classify HDI into development category."""
        if hdi >= 0.8:
            return "Very High Human Development"
        elif hdi >= 0.7:
            return "High Human Development"
        elif hdi >= 0.55:
            return "Medium Human Development"
        else:
            return "Low Human Development"
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "hdi": self.hdi,
            "health_index": self.health_index,
            "education_index": self.education_index,
            "income_index": self.income_index,
            "classification": self.classification,
            "component_values": self.component_values,
        }


# ════════════════════════════════════════════════════════════════════════════════
# HDI Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class HDITransition(TransitionFunction):
    """
    Transition function for HDI cohort state evolution.
    
    Models gradual improvements in HDI components over time,
    with realistic growth rates for:
    - Life expectancy (slow, ~0.1-0.2 years/year)
    - Education years (moderate, ~0.1-0.3 years/year)
    - Income (variable, based on sector output)
    """
    
    name = "HDITransition"
    
    def __init__(
        self,
        life_exp_improvement: float = 0.002,  # ~0.15 years/year
        education_improvement: float = 0.005,  # ~0.15 years/year
        income_growth_rate: float = 0.02,  # 2% per year
    ):
        self.life_exp_improvement = life_exp_improvement
        self.education_improvement = education_improvement
        self.income_growth_rate = income_growth_rate
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply HDI transition."""
        params = params or {}
        
        # Health improvement reduces health burden
        health_improvement = params.get(
            "life_exp_improvement", self.life_exp_improvement
        )
        new_health_burden = np.clip(
            state.health_burden_score * (1 - health_improvement),
            0, 1
        )
        
        # Education improvement increases opportunity
        edu_improvement = params.get(
            "education_improvement", self.education_improvement
        )
        new_opportunity = np.clip(
            state.opportunity_score + edu_improvement * 0.5,
            0, 1
        )
        
        # Income growth affects sector output and credit access
        income_growth = params.get("income_growth_rate", self.income_growth_rate)
        new_sector_output = state.sector_output * (1 + income_growth)
        new_credit_access = np.clip(
            state.credit_access_prob + income_growth * 0.1,
            0, 1
        )
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=new_health_burden,
            credit_access_prob=new_credit_access,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_sector_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# HDI Framework
# ════════════════════════════════════════════════════════════════════════════════


class HDIFramework(BaseMetaFramework):
    """
    Human Development Index (HDI) Framework.
    
    Implements UNDP's Human Development Index using standard
    methodology with goalposts and geometric mean aggregation.
    
    Example:
        >>> bundle = DataBundle.from_dataframes({
        ...     "health": health_df,  # with life_expectancy column
        ...     "education": edu_df,  # with schooling columns
        ...     "economic": econ_df,  # with gni_per_capita column
        ... })
        >>> hdi = HDIFramework()
        >>> metrics = hdi.compute_hdi(bundle)
        >>> print(f"HDI: {metrics.hdi:.3f} ({metrics.classification})")
    """
    
    def __init__(
        self,
        goalposts: Optional[HDIGoalposts] = None,
    ):
        super().__init__()
        self.goalposts = goalposts or HDIGoalposts()
        self._transition_fn = HDITransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return HDI framework metadata."""
        return FrameworkMetadata(
            slug="hdi",
            name="Human Development Index",
            version="1.0.0",
            layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
            tier=Tier.COMMUNITY,
            description=(
                "UNDP Human Development Index measuring achievement "
                "in health, education, and standard of living."
            ),
            required_domains=["health", "education", "economic"],
            output_domains=["hdi", "health_index", "education_index", "income_index"],
            constituent_models=["goalposts_normalizer", "geometric_aggregator"],
            tags=["socioeconomic", "development", "hdi", "undp"],
            author="Khipu Research Labs",
            license="Apache-2.0",
        )
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from HDI components."""
        # Extract data (optional domains)
        health_data = bundle.get("health") if bundle.has_domain("health") else None
        edu_data = bundle.get("education") if bundle.has_domain("education") else None
        econ_data = bundle.get("economic") if bundle.has_domain("economic") else None
        
        # Determine cohort count
        n_cohorts = 100  # Default
        if health_data:
            n_cohorts = len(health_data.data)
        elif edu_data:
            n_cohorts = len(edu_data.data)
        elif econ_data:
            n_cohorts = len(econ_data.data)
        
        # Extract life expectancy → health burden
        if health_data and "life_expectancy" in health_data.data.columns:
            life_exp = health_data.data["life_expectancy"].values[:n_cohorts]
            # Normalize: higher life exp = lower health burden
            health_idx = self._normalize_life_expectancy(life_exp)
            health_burden = 1 - health_idx
        else:
            health_burden = np.full(n_cohorts, 0.3)
        
        # Extract education → opportunity score
        if edu_data:
            edu_df = edu_data.data
            # Handle mean years of schooling
            if "mean_years_schooling" in edu_df.columns:
                mean_schooling = edu_df["mean_years_schooling"].values[:n_cohorts]
            elif "years_schooling" in edu_df.columns:
                mean_schooling = edu_df["years_schooling"].values[:n_cohorts]
            else:
                mean_schooling = np.full(n_cohorts, 10.0)
            # Handle expected years of schooling
            if "expected_years_schooling" in edu_df.columns:
                expected_schooling = edu_df["expected_years_schooling"].values[:n_cohorts]
            else:
                expected_schooling = np.full(n_cohorts, 12.0)
            edu_idx = self._compute_education_index(mean_schooling, expected_schooling)
            opportunity = edu_idx
        else:
            opportunity = np.full(n_cohorts, 0.6)
        
        # Extract GNI → credit access and sector output
        if econ_data and "gni_per_capita" in econ_data.data.columns:
            gni = econ_data.data["gni_per_capita"].values[:n_cohorts]
            income_idx = self._normalize_gni(gni)
            credit_access = np.clip(income_idx * 0.9, 0.2, 0.95)
            sector_output = np.column_stack([gni / 10] * 10)  # Distribute across sectors
        else:
            credit_access = np.full(n_cohorts, 0.5)
            sector_output = np.full((n_cohorts, 10), 5000)
        
        return CohortStateVector(
            employment_prob=np.clip(0.4 + opportunity * 0.5, 0.3, 0.95),
            health_burden_score=np.clip(health_burden, 0, 1),
            credit_access_prob=np.clip(credit_access, 0, 1),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.clip(opportunity, 0, 1),
            sector_output=sector_output,
            deprivation_vector=np.column_stack([
                health_burden,
                1 - opportunity,
                1 - credit_access,
                np.full(n_cohorts, 0.2),
                np.full(n_cohorts, 0.2),
                np.full(n_cohorts, 0.2),
            ]),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply HDI transition."""
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> dict[str, Any]:
        """Compute HDI metrics from trajectory."""
        return self._compute_hdi_from_state(trajectory.final_state).to_dict()
    
    def _normalize_life_expectancy(self, life_exp: np.ndarray) -> np.ndarray:
        """Normalize life expectancy to [0, 1] index."""
        g = self.goalposts
        return np.clip(
            (life_exp - g.life_expectancy_min) / 
            (g.life_expectancy_max - g.life_expectancy_min),
            0, 1
        )
    
    def _compute_education_index(
        self,
        mean_years: np.ndarray,
        expected_years: np.ndarray,
    ) -> np.ndarray:
        """Compute education dimension index."""
        g = self.goalposts
        
        # Mean years index
        mean_idx = np.clip(
            (mean_years - g.schooling_mean_min) /
            (g.schooling_mean_max - g.schooling_mean_min),
            0, 1
        )
        
        # Expected years index
        expected_idx = np.clip(
            (expected_years - g.schooling_expected_min) /
            (g.schooling_expected_max - g.schooling_expected_min),
            0, 1
        )
        
        # Geometric mean of the two
        return np.sqrt(mean_idx * expected_idx)
    
    def _normalize_gni(self, gni: np.ndarray) -> np.ndarray:
        """Normalize GNI per capita using log transformation."""
        g = self.goalposts
        
        # Log transform
        log_gni = np.log(np.clip(gni, g.gni_min, g.gni_max))
        log_min = np.log(g.gni_min)
        log_max = np.log(g.gni_max)
        
        return np.clip((log_gni - log_min) / (log_max - log_min), 0, 1)
    
    def _compute_hdi_from_state(
        self,
        state: CohortStateVector,
    ) -> HDIMetrics:
        """Compute HDI from cohort state (population average)."""
        # Map state fields to HDI dimensions
        # Health: inverse of health burden
        health_index = float(1 - state.health_burden_score.mean())
        
        # Education: opportunity score
        education_index = float(state.opportunity_score.mean())
        
        # Income: derived from credit access and sector output
        avg_output = state.sector_output.mean()
        income_index = float(np.clip(
            state.credit_access_prob.mean() * 0.7 + 
            np.log1p(avg_output) / np.log1p(75000) * 0.3,
            0, 1
        ))
        
        # HDI = geometric mean
        hdi = float((health_index * education_index * income_index) ** (1/3))
        
        return HDIMetrics(
            hdi=hdi,
            health_index=health_index,
            education_index=education_index,
            income_index=income_index,
            classification=HDIMetrics.classify(hdi),
            component_values={
                "avg_health_burden": float(state.health_burden_score.mean()),
                "avg_opportunity": float(state.opportunity_score.mean()),
                "avg_sector_output": float(avg_output),
            },
        )
    
    def compute_hdi(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> HDIMetrics:
        """
        Compute HDI directly from data bundle.
        
        Convenience method for one-shot HDI computation.
        """
        from krl_frameworks.core.config import FrameworkConfig
        config = config or FrameworkConfig()
        
        state = self._compute_initial_state(bundle, config)
        return self._compute_hdi_from_state(state)

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return HDI dashboard specification.
        
        HDI is a COMMUNITY tier framework providing human development
        measurement across health, education, and income dimensions.
        """
        return FrameworkDashboardSpec(
            slug="hdi",
            name="Human Development Index",
            description=(
                "Compute the UNDP Human Development Index measuring "
                "average achievement in health, education, and living "
                "standards using geometric mean aggregation."
            ),
            layer="socioeconomic",
            parameters_schema={
                "type": "object",
                "properties": {
                    # Goalpost Overrides
                    "life_expectancy_min": {
                        "type": "number",
                        "title": "Min Life Expectancy",
                        "description": "Minimum goalpost for life expectancy (years)",
                        "minimum": 10,
                        "maximum": 40,
                        "default": 20,
                        "x-ui-widget": "number",
                        "x-ui-group": "goalposts",
                        "x-ui-order": 1,
                    },
                    "life_expectancy_max": {
                        "type": "number",
                        "title": "Max Life Expectancy",
                        "description": "Maximum goalpost for life expectancy (years)",
                        "minimum": 70,
                        "maximum": 100,
                        "default": 85,
                        "x-ui-widget": "number",
                        "x-ui-group": "goalposts",
                        "x-ui-order": 2,
                    },
                    "gni_min": {
                        "type": "number",
                        "title": "Min GNI per Capita",
                        "description": "Minimum goalpost for GNI per capita (PPP $)",
                        "minimum": 50,
                        "maximum": 500,
                        "default": 100,
                        "x-ui-widget": "number",
                        "x-ui-group": "goalposts",
                        "x-ui-order": 3,
                    },
                    "gni_max": {
                        "type": "number",
                        "title": "Max GNI per Capita",
                        "description": "Maximum goalpost for GNI per capita (PPP $)",
                        "minimum": 50000,
                        "maximum": 150000,
                        "default": 75000,
                        "x-ui-widget": "number",
                        "x-ui-group": "goalposts",
                        "x-ui-order": 4,
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
                    "life_exp_improvement": {
                        "type": "number",
                        "title": "Life Expectancy Improvement",
                        "description": "Annual improvement rate in life expectancy",
                        "minimum": 0,
                        "maximum": 0.01,
                        "default": 0.002,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.0005,
                        "x-ui-format": ".2%",
                        "x-ui-group": "simulation",
                        "x-ui-order": 2,
                    },
                    "education_improvement": {
                        "type": "number",
                        "title": "Education Improvement",
                        "description": "Annual improvement rate in education",
                        "minimum": 0,
                        "maximum": 0.02,
                        "default": 0.005,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.001,
                        "x-ui-format": ".2%",
                        "x-ui-group": "simulation",
                        "x-ui-order": 3,
                    },
                    "income_growth_rate": {
                        "type": "number",
                        "title": "Income Growth Rate",
                        "description": "Annual income growth rate",
                        "minimum": 0,
                        "maximum": 0.1,
                        "default": 0.02,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-format": ".1%",
                        "x-ui-group": "simulation",
                        "x-ui-order": 4,
                    },
                },
                "required": [],
            },
            default_parameters={
                "life_expectancy_min": 20,
                "life_expectancy_max": 85,
                "gni_min": 100,
                "gni_max": 75000,
                "n_periods": 10,
                "life_exp_improvement": 0.002,
                "education_improvement": 0.005,
                "income_growth_rate": 0.02,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="goalposts",
                    title="UNDP Goalposts",
                    description="Normalization bounds for HDI dimensions",
                    collapsed_by_default=True,
                    parameters=["life_expectancy_min", "life_expectancy_max", "gni_min", "gni_max"],
                ),
                ParameterGroupSpec(
                    key="simulation",
                    title="Simulation Settings",
                    description="Projection and improvement rates",
                    collapsed_by_default=False,
                    parameters=["n_periods", "life_exp_improvement", "education_improvement", "income_growth_rate"],
                ),
            ],
            required_domains=["health", "education", "economic"],
            min_tier=Tier.COMMUNITY,
            output_views=[
                # HDI Gauge
                OutputViewSpec(
                    key="hdi_score",
                    title="HDI Score",
                    view_type=ViewType.GAUGE,
                    description="Overall Human Development Index (0-1)",
                    config={
                        "min": 0,
                        "max": 1,
                        "thresholds": [0.55, 0.70, 0.80],
                        "colors": ["#ef4444", "#f59e0b", "#22c55e", "#0ea5e9"],
                        "format": ".3f",
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="hdi_score_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # Summary Metrics
                OutputViewSpec(
                    key="summary",
                    title="Summary",
                    view_type=ViewType.METRIC_GRID,
                    description="HDI dimension indices",
                    config={
                        "metrics": [
                            {"key": "hdi", "label": "HDI", "format": ".3f"},
                            {"key": "health_index", "label": "Health Index", "format": ".3f"},
                            {"key": "education_index", "label": "Education Index", "format": ".3f"},
                            {"key": "income_index", "label": "Income Index", "format": ".3f"},
                        ]
                    },
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="summary_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # Dimension Bar Chart
                OutputViewSpec(
                    key="dimensions",
                    title="Dimensions",
                    view_type=ViewType.BAR_CHART,
                    description="HDI dimension scores",
                    config={
                        "x_field": "dimension",
                        "y_field": "value",
                        "color_field": "dimension",
                    },
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="dimensions_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # HDI Trajectory
                OutputViewSpec(
                    key="hdi_trajectory",
                    title="HDI Trajectory",
                    view_type=ViewType.LINE_CHART,
                    description="Projected HDI over time",
                    config={
                        "x_field": "period",
                        "y_fields": ["hdi", "health_index", "education_index", "income_index"],
                        "x_label": "Year",
                        "y_label": "Index Value",
                    },
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="hdi_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # Classification
                OutputViewSpec(
                    key="classification",
                    title="Development Classification",
                    view_type=ViewType.TABLE,
                    description="UNDP development tier classification",
                    config={
                        "columns": [
                            {"key": "classification", "label": "Tier"},
                            {"key": "hdi", "label": "HDI", "format": ".3f"},
                        ]
                    },
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="classification_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
