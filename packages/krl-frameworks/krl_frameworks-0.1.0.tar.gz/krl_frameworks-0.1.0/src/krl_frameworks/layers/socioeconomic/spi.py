# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Social Progress Index (SPI)
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Social Progress Index (SPI) Framework.

The SPI is a comprehensive measure of social progress developed by
the Social Progress Imperative. It measures societal well-being
independent of economic indicators, focusing on three dimensions:

1. Basic Human Needs:
   - Nutrition & Basic Medical Care
   - Water & Sanitation
   - Shelter
   - Personal Safety

2. Foundations of Wellbeing:
   - Access to Basic Knowledge
   - Access to Information & Communications
   - Health & Wellness
   - Environmental Quality

3. Opportunity:
   - Personal Rights
   - Personal Freedom & Choice
   - Inclusiveness
   - Access to Advanced Education

Methodology:
    - 54 outcome indicators across 12 components
    - Each component aggregated via principal component analysis
    - Dimension scores averaged to produce SPI (0-100 scale)

CBSS Integration:
    - Maps deprivation vector to SPI components
    - Tracks social progress under policy interventions
    - Projects multi-dimensional improvement trajectories

References:
    - Social Progress Imperative Methodology
    - Porter, M.E. & Stern, S. "Social Progress Index"

Tier: COMMUNITY (individual index access)
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
from krl_frameworks.core.data_bundle import DataBundle, DataDomain
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["SPIFramework", "SPITransition", "SPIMetrics"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# SPI Configuration
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class SPIConfig:
    """
    Configuration for SPI computation.
    
    Attributes:
        dimension_weights: Weights for [basic_needs, wellbeing, opportunity].
        component_weights: Per-dimension component weights.
        scale_min: Minimum SPI score.
        scale_max: Maximum SPI score.
    """
    
    dimension_weights: tuple[float, float, float] = (1 / 3, 1 / 3, 1 / 3)
    scale_min: float = 0.0
    scale_max: float = 100.0


# ════════════════════════════════════════════════════════════════════════════════
# SPI Metrics
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class SPIMetrics:
    """
    Container for SPI computation results.
    
    Attributes:
        spi: Social Progress Index (0-100).
        basic_human_needs: Basic Human Needs dimension score.
        foundations_wellbeing: Foundations of Wellbeing dimension score.
        opportunity: Opportunity dimension score.
        component_scores: Per-component scores (12 components).
        tier: SPI tier classification.
    """
    
    spi: float
    basic_human_needs: float
    foundations_wellbeing: float
    opportunity: float
    component_scores: dict[str, float]
    tier: str
    
    @classmethod
    def classify(cls, spi: float) -> str:
        """Classify SPI into performance tier."""
        if spi >= 85:
            return "Very High Social Progress"
        elif spi >= 75:
            return "High Social Progress"
        elif spi >= 65:
            return "Upper Middle Social Progress"
        elif spi >= 55:
            return "Lower Middle Social Progress"
        elif spi >= 45:
            return "Low Social Progress"
        else:
            return "Very Low Social Progress"
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "spi": self.spi,
            "basic_human_needs": self.basic_human_needs,
            "foundations_wellbeing": self.foundations_wellbeing,
            "opportunity": self.opportunity,
            "component_scores": self.component_scores,
            "tier": self.tier,
        }


# ════════════════════════════════════════════════════════════════════════════════
# SPI Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class SPITransition(TransitionFunction):
    """
    Transition function for SPI cohort state evolution.
    
    Models improvements across the three SPI dimensions with
    different rates of change and cross-dimensional spillovers.
    """
    
    name = "SPITransition"
    
    def __init__(
        self,
        basic_needs_improvement: float = 0.008,
        wellbeing_improvement: float = 0.005,
        opportunity_improvement: float = 0.004,
    ):
        self.basic_needs_improvement = basic_needs_improvement
        self.wellbeing_improvement = wellbeing_improvement
        self.opportunity_improvement = opportunity_improvement
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply SPI transition."""
        params = params or {}
        
        # Get improvement rates
        basic_rate = params.get("basic_needs_rate", self.basic_needs_improvement)
        wellbeing_rate = params.get("wellbeing_rate", self.wellbeing_improvement)
        opp_rate = params.get("opportunity_rate", self.opportunity_improvement)
        
        # Update deprivation vector (6 dims mapped to SPI components)
        # dims 0-1: basic needs, dims 2-3: wellbeing, dims 4-5: opportunity
        deprivation = state.deprivation_vector.copy()
        
        # Basic needs improve fastest
        deprivation[:, :2] *= (1 - basic_rate)
        
        # Wellbeing improves moderately
        deprivation[:, 2:4] *= (1 - wellbeing_rate)
        
        # Opportunity improves slowly
        deprivation[:, 4:] *= (1 - opp_rate)
        
        deprivation = np.clip(deprivation, 0, 1)
        
        # Update health burden (linked to basic needs)
        avg_basic_needs_dep = deprivation[:, :2].mean(axis=1)
        health_burden = np.clip(avg_basic_needs_dep, 0, 1)
        
        # Update opportunity score (linked to opportunity dimension)
        avg_opp_dep = deprivation[:, 4:].mean(axis=1)
        opportunity = np.clip(1 - avg_opp_dep, 0, 1)
        
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
# SPI Framework
# ════════════════════════════════════════════════════════════════════════════════


class SPIFramework(BaseMetaFramework):
    """
    Social Progress Index (SPI) Framework.
    
    Implements the Social Progress Imperative's methodology for
    measuring societal well-being across basic needs, foundations
    of wellbeing, and opportunity dimensions.
    
    Example:
        >>> bundle = DataBundle.from_dataframes({
        ...     "health": health_df,
        ...     "education": edu_df,
        ...     "housing": housing_df,
        ... })
        >>> spi = SPIFramework()
        >>> metrics = spi.compute_spi(bundle)
        >>> print(f"SPI: {metrics.spi:.1f} ({metrics.tier})")
    """
    
    def __init__(self, config: Optional[SPIConfig] = None):
        super().__init__()
        self.spi_config = config or SPIConfig()
        self._transition_fn = SPITransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return SPI framework metadata."""
        return FrameworkMetadata(
            slug="spi",
            name="Social Progress Index",
            version="1.0.0",
            layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
            tier=Tier.COMMUNITY,
            description=(
                "Social Progress Imperative's index measuring "
                "societal wellbeing across basic needs, wellbeing "
                "foundations, and opportunity dimensions."
            ),
            required_domains=["health", "education", "housing"],
            output_domains=["spi", "basic_human_needs", "foundations_wellbeing", "opportunity"],
            constituent_models=["pca_weighter", "dimension_scorer", "composite_aggregator"],
            tags=["socioeconomic", "wellbeing", "spi", "social_progress"],
            author="Khipu Research Labs",
            license="Apache-2.0",
        )
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state mapping to SPI components."""
        # Try to get relevant domain data (optional domains)
        health_data = bundle.get("health") if bundle.has_domain("health") else None
        edu_data = bundle.get("education") if bundle.has_domain("education") else None
        housing_data = bundle.get("housing") if bundle.has_domain("housing") else None
        
        # Determine cohort size
        n_cohorts = 100
        for data in [health_data, edu_data, housing_data]:
            if data is not None:
                n_cohorts = len(data.data)
                break
        
        # Build 6-dimension deprivation vector:
        # [nutrition, shelter, knowledge, health, rights, inclusiveness]
        deprivation = np.zeros((n_cohorts, 6))
        
        # Basic Human Needs (dims 0-1)
        if health_data is not None:
            df = health_data.data
            if "mortality_rate" in df.columns:
                deprivation[:, 0] = np.clip(df["mortality_rate"].values[:n_cohorts] * 20, 0, 1)
            else:
                deprivation[:, 0] = 0.2
        else:
            deprivation[:, 0] = 0.25
        
        if housing_data is not None:
            df = housing_data.data
            if "housing_quality" in df.columns:
                deprivation[:, 1] = np.clip(1 - df["housing_quality"].values[:n_cohorts], 0, 1)
            else:
                deprivation[:, 1] = 0.2
        else:
            deprivation[:, 1] = 0.2
        
        # Foundations of Wellbeing (dims 2-3)
        if edu_data is not None:
            df = edu_data.data
            if "hs_graduation_rate" in df.columns:
                deprivation[:, 2] = np.clip(1 - df["hs_graduation_rate"].values[:n_cohorts], 0, 1)
            else:
                deprivation[:, 2] = 0.3
        else:
            deprivation[:, 2] = 0.3
        
        if health_data is not None:
            df = health_data.data
            if "insurance_rate" in df.columns:
                deprivation[:, 3] = np.clip(1 - df["insurance_rate"].values[:n_cohorts], 0, 1)
            else:
                deprivation[:, 3] = 0.25
        else:
            deprivation[:, 3] = 0.25
        
        # Opportunity (dims 4-5)
        deprivation[:, 4] = np.random.uniform(0.15, 0.35, n_cohorts)  # Rights
        deprivation[:, 5] = np.random.uniform(0.2, 0.4, n_cohorts)  # Inclusiveness
        
        # Compute derived fields
        avg_basic = deprivation[:, :2].mean(axis=1)
        avg_wellbeing = deprivation[:, 2:4].mean(axis=1)
        avg_opportunity = deprivation[:, 4:].mean(axis=1)
        
        return CohortStateVector(
            employment_prob=np.clip(0.5 + (1 - avg_opportunity) * 0.4, 0.3, 0.95),
            health_burden_score=np.clip(avg_basic, 0, 1),
            credit_access_prob=np.clip(1 - avg_wellbeing * 0.5, 0.3, 0.9),
            housing_cost_ratio=np.clip(deprivation[:, 1] * 0.5 + 0.15, 0.1, 0.6),
            opportunity_score=np.clip(1 - avg_opportunity, 0, 1),
            sector_output=np.full((n_cohorts, 10), 50),
            deprivation_vector=deprivation,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply SPI transition."""
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> dict[str, Any]:
        """Compute SPI metrics from trajectory."""
        return self._compute_spi_from_state(trajectory.final_state).to_dict()
    
    def _compute_spi_from_state(
        self,
        state: CohortStateVector,
    ) -> SPIMetrics:
        """
        Compute SPI metrics from cohort state.
        
        Maps the 6-dimension deprivation vector to SPI's
        three dimensions and 12 components.
        """
        deprivation = state.deprivation_vector
        
        # Convert deprivation (0-1, higher=worse) to score (0-100, higher=better)
        def dep_to_score(dep: np.ndarray) -> float:
            return float((1 - dep.mean()) * 100)
        
        # Dimension scores (average of component scores)
        # Basic Human Needs: dims 0-1
        basic_needs = dep_to_score(deprivation[:, :2])
        
        # Foundations of Wellbeing: dims 2-3
        wellbeing = dep_to_score(deprivation[:, 2:4])
        
        # Opportunity: dims 4-5
        opportunity = dep_to_score(deprivation[:, 4:])
        
        # Overall SPI
        spi = (basic_needs + wellbeing + opportunity) / 3
        
        # Component scores (simplified - 6 components from 6 dims)
        component_names = [
            "nutrition_medical_care",
            "shelter",
            "access_basic_knowledge",
            "health_wellness",
            "personal_rights",
            "inclusiveness",
        ]
        component_scores = {
            name: dep_to_score(deprivation[:, i:i+1])
            for i, name in enumerate(component_names)
        }
        
        return SPIMetrics(
            spi=spi,
            basic_human_needs=basic_needs,
            foundations_wellbeing=wellbeing,
            opportunity=opportunity,
            component_scores=component_scores,
            tier=SPIMetrics.classify(spi),
        )
    
    def compute_spi(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> SPIMetrics:
        """
        Compute SPI directly from data bundle.
        
        Convenience method for one-shot SPI computation.
        """
        from krl_frameworks.core.config import FrameworkConfig
        config = config or FrameworkConfig()
        
        state = self._compute_initial_state(bundle, config)
        return self._compute_spi_from_state(state)

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return SPI dashboard specification.
        
        SPI is a COMMUNITY tier framework providing social progress
        measurement across basic needs, wellbeing, and opportunity.
        """
        return FrameworkDashboardSpec(
            slug="spi",
            name="Social Progress Index",
            description=(
                "Compute the Social Progress Index measuring societal "
                "well-being across Basic Human Needs, Foundations of "
                "Wellbeing, and Opportunity dimensions."
            ),
            layer="socioeconomic",
            parameters_schema={
                "type": "object",
                "properties": {
                    # Dimension Weights
                    "basic_needs_weight": {
                        "type": "number",
                        "title": "Basic Needs Weight",
                        "description": "Weight for Basic Human Needs dimension",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.333,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-group": "weights",
                        "x-ui-order": 1,
                    },
                    "wellbeing_weight": {
                        "type": "number",
                        "title": "Wellbeing Weight",
                        "description": "Weight for Foundations of Wellbeing dimension",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.333,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-group": "weights",
                        "x-ui-order": 2,
                    },
                    "opportunity_weight": {
                        "type": "number",
                        "title": "Opportunity Weight",
                        "description": "Weight for Opportunity dimension",
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
                    "basic_needs_improvement": {
                        "type": "number",
                        "title": "Basic Needs Improvement Rate",
                        "description": "Annual improvement in basic needs",
                        "minimum": 0,
                        "maximum": 0.02,
                        "default": 0.008,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.001,
                        "x-ui-format": ".2%",
                        "x-ui-group": "simulation",
                        "x-ui-order": 2,
                    },
                    "wellbeing_improvement": {
                        "type": "number",
                        "title": "Wellbeing Improvement Rate",
                        "description": "Annual improvement in wellbeing",
                        "minimum": 0,
                        "maximum": 0.02,
                        "default": 0.005,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.001,
                        "x-ui-format": ".2%",
                        "x-ui-group": "simulation",
                        "x-ui-order": 3,
                    },
                    "opportunity_improvement": {
                        "type": "number",
                        "title": "Opportunity Improvement Rate",
                        "description": "Annual improvement in opportunity",
                        "minimum": 0,
                        "maximum": 0.02,
                        "default": 0.004,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.001,
                        "x-ui-format": ".2%",
                        "x-ui-group": "simulation",
                        "x-ui-order": 4,
                    },
                },
                "required": [],
            },
            default_parameters={
                "basic_needs_weight": 0.333,
                "wellbeing_weight": 0.333,
                "opportunity_weight": 0.333,
                "n_periods": 10,
                "basic_needs_improvement": 0.008,
                "wellbeing_improvement": 0.005,
                "opportunity_improvement": 0.004,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="weights",
                    title="Dimension Weights",
                    description="Weights for each dimension (should sum to 1)",
                    collapsed_by_default=False,
                    parameters=["basic_needs_weight", "wellbeing_weight", "opportunity_weight"],
                ),
                ParameterGroupSpec(
                    key="simulation",
                    title="Simulation Settings",
                    description="Projection periods and improvement rates",
                    collapsed_by_default=True,
                    parameters=["n_periods", "basic_needs_improvement", "wellbeing_improvement", "opportunity_improvement"],
                ),
            ],
            required_domains=["health", "education", "housing", "environment"],
            min_tier=Tier.COMMUNITY,
            output_views=[
                # SPI Gauge
                OutputViewSpec(
                    key="spi_score",
                    title="SPI Score",
                    view_type=ViewType.GAUGE,
                    description="Overall Social Progress Index (0-100)",
                    config={
                        "min": 0,
                        "max": 100,
                        "thresholds": [45, 55, 65, 75, 85],
                        "colors": ["#ef4444", "#f97316", "#f59e0b", "#22c55e", "#0ea5e9", "#6366f1"],
                        "format": ".1f",
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="spi_score_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # Summary Metrics
                OutputViewSpec(
                    key="summary",
                    title="Summary",
                    view_type=ViewType.METRIC_GRID,
                    description="SPI dimension scores",
                    config={
                        "metrics": [
                            {"key": "spi", "label": "SPI", "format": ".1f"},
                            {"key": "basic_human_needs", "label": "Basic Needs", "format": ".1f"},
                            {"key": "foundations_wellbeing", "label": "Wellbeing", "format": ".1f"},
                            {"key": "opportunity", "label": "Opportunity", "format": ".1f"},
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
                    description="SPI dimension scores",
                    config={
                        "x_field": "dimension",
                        "y_field": "score",
                        "color_field": "dimension",
                    },
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="dimensions_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # Component Breakdown
                OutputViewSpec(
                    key="components",
                    title="Components",
                    view_type=ViewType.BAR_CHART,
                    description="SPI component scores (12 components)",
                    config={
                        "x_field": "component",
                        "y_field": "score",
                        "color_field": "dimension",
                    },
                result_class=ResultClass.DOMAIN_DECOMPOSITION,
                output_key="components_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # SPI Trajectory
                OutputViewSpec(
                    key="spi_trajectory",
                    title="SPI Trajectory",
                    view_type=ViewType.LINE_CHART,
                    description="Projected SPI over time",
                    config={
                        "x_field": "period",
                        "y_fields": ["spi", "basic_human_needs", "foundations_wellbeing", "opportunity"],
                        "x_label": "Year",
                        "y_label": "Score (0-100)",
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="spi_trajectory_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # Classification
                OutputViewSpec(
                    key="tier",
                    title="Progress Tier",
                    view_type=ViewType.TABLE,
                    description="Social progress tier classification",
                    config={
                        "columns": [
                            {"key": "tier", "label": "Tier"},
                            {"key": "spi", "label": "SPI", "format": ".1f"},
                        ]
                    },
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="tier_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
