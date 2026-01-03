# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Government Operational Tools
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Government Operational Frameworks - Extended Tools.

Additional frameworks for government policy analysis:

    - MPI Operational Tools: Operational MPI dashboards for government use
    - City/State Resilience Dashboards: Multi-hazard resilience assessment
    - Interagency Spatial Causal Toolkits: Cross-agency spatial causal analysis

Token Weight: 2-6 per run
Tier: COMMUNITY / PROFESSIONAL

References:
    - UNDP Guidance on MPI Operationalization
    - Rockefeller Foundation City Resilience Framework
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
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier
from krl_frameworks.simulation.cbss import TransitionFunction
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = [
    "MPIOperationalFramework",
    "CityResilienceFramework",
    "InteragencySpatialCausalFramework",
]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Government Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class GovernmentTransition(TransitionFunction):
    """Transition function for government-focused cohort evolution."""
    
    name = "GovernmentTransition"
    
    def __init__(
        self,
        policy_effectiveness: float = 0.6,
        implementation_lag: int = 2,
    ):
        self.policy_effectiveness = policy_effectiveness
        self.implementation_lag = implementation_lag
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply government policy transition."""
        params = params or {}
        
        # Policy impact with lag
        if t >= params.get("implementation_lag", self.implementation_lag):
            effectiveness = params.get("policy_effectiveness", self.policy_effectiveness)
            deprivation_reduction = 0.02 * effectiveness
        else:
            deprivation_reduction = 0.0
        
        # Reduce deprivation gradually
        new_deprivation = np.clip(
            state.deprivation_vector * (1 - deprivation_reduction), 0, 1
        )
        
        # Improve opportunity score
        new_opportunity = np.clip(
            state.opportunity_score + deprivation_reduction * 0.5, 0, 1
        )
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=np.clip(
                state.health_burden_score - deprivation_reduction * 0.3, 0, 1
            ),
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output,
            deprivation_vector=new_deprivation,
        )


# ════════════════════════════════════════════════════════════════════════════════
# MPI Operational Tools Framework
# ════════════════════════════════════════════════════════════════════════════════


class MPIOperationalFramework(BaseMetaFramework):
    """
    MPI Operational Tools for Government Use.
    
    Provides operational dashboards and monitoring tools for
    government agencies implementing MPI-based poverty programs.
    
    Token weight: 2
    """
    
    METADATA = FrameworkMetadata(
        slug="mpi_operational",
        name="MPI Operational Tools",
        version="1.0.0",
        layer=VerticalLayer.GOVERNMENT_POLICY,
        tier=Tier.COMMUNITY,
        description=(
            "Operational MPI dashboards and monitoring tools for "
            "government poverty reduction programs."
        ),
        required_domains=["household", "poverty_indicators", "geographic"],
        output_domains=["mpi_dashboard", "targeting_lists", "progress_reports"],
        constituent_models=["mpi_calculator", "targeting_engine", "progress_tracker"],
        tags=["mpi", "operational", "government", "dashboard", "poverty"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = GovernmentTransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        n_cohorts = config.cohort_size or 100
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.5),
            health_burden_score=np.full(n_cohorts, 0.35),
            credit_access_prob=np.full(n_cohorts, 0.4),
            housing_cost_ratio=np.full(n_cohorts, 0.35),
            opportunity_score=np.full(n_cohorts, 0.4),
            sector_output=np.full((n_cohorts, 10), 500.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.35),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        return {
            "mpi_headcount": float(np.mean(state.deprivation_vector > 0.33)),
            "avg_deprivation": float(np.mean(state.deprivation_vector)),
            "policy_reach": float(np.mean(state.opportunity_score)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "mpi_operational", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return MPI Operational dashboard specification."""
        return FrameworkDashboardSpec(
            slug="mpi_operational",
            name="MPI Operational Tools",
            description=(
                "Operational MPI dashboards and monitoring tools for "
                "government poverty reduction programs."
            ),
            layer="government",
            parameters_schema={
                "type": "object",
                "properties": {
                    "indicators": {
                        "type": "array",
                        "title": "MPI Indicators",
                        "items": {
                            "type": "string",
                            "enum": ["health", "education", "living_standards", "employment", "housing", "assets"],
                        },
                        "default": ["health", "education", "living_standards"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "indicators",
                    },
                    "performance_period": {
                        "type": "string",
                        "title": "Performance Period",
                        "enum": ["monthly", "quarterly", "annual"],
                        "default": "quarterly",
                        "x-ui-widget": "select",
                        "x-ui-group": "time",
                    },
                    "benchmark_type": {
                        "type": "string",
                        "title": "Benchmark Type",
                        "enum": ["national", "regional", "international"],
                        "default": "national",
                        "x-ui-widget": "select",
                        "x-ui-group": "comparison",
                    },
                },
            },
            default_parameters={
                "indicators": ["health", "education", "living_standards"],
                "performance_period": "quarterly",
                "benchmark_type": "national",
            },
            parameter_groups=[
                ParameterGroupSpec(key="indicators", title="Indicators", parameters=["indicators"]),
                ParameterGroupSpec(key="time", title="Time Period", parameters=["performance_period"]),
                ParameterGroupSpec(key="comparison", title="Comparison", parameters=["benchmark_type"]),
            ],
            required_domains=["household", "poverty_indicators", "geographic"],
            min_tier=Tier.TEAM,
            output_views=[
                OutputViewSpec(
                    key="performance_scorecard",
                    title="Performance Scorecard",
                    view_type=ViewType.TABLE,
                    config={"columns": ["indicator", "target", "actual", "variance", "status"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="performance_scorecard_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="trend_analysis",
                    title="Trend Analysis",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "period", "y_field": "mpi_value", "color_by": "indicator"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="trend_analysis_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="indicator_breakdown",
                    title="Indicator Breakdown",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "indicator", "y_field": "deprivation_rate", "sort": "desc"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="indicator_breakdown_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# City/State Resilience Dashboards Framework
# ════════════════════════════════════════════════════════════════════════════════


class CityResilienceFramework(BaseMetaFramework):
    """
    City/State Resilience Dashboards Framework.
    
    Multi-hazard resilience assessment for urban and state-level
    government planning.
    
    Token weight: 3
    """
    
    METADATA = FrameworkMetadata(
        slug="city_resilience",
        name="City/State Resilience Dashboards",
        version="1.0.0",
        layer=VerticalLayer.GOVERNMENT_POLICY,
        tier=Tier.COMMUNITY,
        description=(
            "Multi-hazard resilience assessment dashboards for "
            "city and state-level government planning."
        ),
        required_domains=["infrastructure", "hazard", "social", "economic"],
        output_domains=["resilience_index", "vulnerability_map", "action_plan"],
        constituent_models=["hazard_model", "vulnerability_assessor", "resilience_scorer"],
        tags=["resilience", "city", "state", "hazard", "infrastructure", "dashboard"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = GovernmentTransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        n_cohorts = config.cohort_size or 100
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.65),
            health_burden_score=np.full(n_cohorts, 0.25),
            credit_access_prob=np.full(n_cohorts, 0.55),
            housing_cost_ratio=np.full(n_cohorts, 0.32),
            opportunity_score=np.full(n_cohorts, 0.55),
            sector_output=np.full((n_cohorts, 10), 1000.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.25),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        return {
            "resilience_index": float(np.mean(state.opportunity_score)),
            "vulnerability_score": float(np.mean(state.deprivation_vector)),
            "infrastructure_health": float(np.mean(state.sector_output) / 1000),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "city_resilience", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return City Resilience dashboard specification."""
        return FrameworkDashboardSpec(
            slug="city_resilience",
            name="City/State Resilience Dashboards",
            description=(
                "Multi-hazard resilience assessment dashboards for "
                "city and state-level government planning."
            ),
            layer="government",
            parameters_schema={
                "type": "object",
                "properties": {
                    "resilience_dimensions": {
                        "type": "array",
                        "title": "Resilience Dimensions",
                        "items": {
                            "type": "string",
                            "enum": ["infrastructure", "economic", "social", "institutional", "environmental"],
                        },
                        "default": ["infrastructure", "economic", "social"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "dimensions",
                    },
                    "hazard_types": {
                        "type": "array",
                        "title": "Hazard Types",
                        "items": {
                            "type": "string",
                            "enum": ["flood", "earthquake", "hurricane", "wildfire", "drought", "pandemic"],
                        },
                        "default": ["flood", "earthquake"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "hazards",
                    },
                    "time_horizon": {
                        "type": "string",
                        "title": "Planning Horizon",
                        "enum": ["short_term", "medium_term", "long_term"],
                        "default": "medium_term",
                        "x-ui-widget": "select",
                        "x-ui-group": "planning",
                    },
                },
            },
            default_parameters={
                "resilience_dimensions": ["infrastructure", "economic", "social"],
                "hazard_types": ["flood", "earthquake"],
                "time_horizon": "medium_term",
            },
            parameter_groups=[
                ParameterGroupSpec(key="dimensions", title="Dimensions", parameters=["resilience_dimensions"]),
                ParameterGroupSpec(key="hazards", title="Hazards", parameters=["hazard_types"]),
                ParameterGroupSpec(key="planning", title="Planning", parameters=["time_horizon"]),
            ],
            required_domains=["infrastructure", "hazard", "social", "economic"],
            min_tier=Tier.TEAM,
            output_views=[
                OutputViewSpec(
                    key="resilience_index",
                    title="Resilience Index",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 100, "thresholds": [40, 70]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="resilience_index_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="dimension_scores",
                    title="Dimension Scores",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "dimension", "y_field": "score", "color_by": "status"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="dimension_scores_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="vulnerability_map",
                    title="Vulnerability Network",
                    view_type=ViewType.NETWORK,
                    config={"nodes": "assets", "edges": "dependencies", "color_by": "vulnerability"},
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="vulnerability_map_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Interagency Spatial Causal Toolkits Framework
# ════════════════════════════════════════════════════════════════════════════════


class InteragencySpatialCausalFramework(BaseMetaFramework):
    """
    Interagency Spatial Causal Toolkits Framework.
    
    Cross-agency spatial causal analysis for coordinated policy evaluation.
    
    Token weight: 6
    """
    
    METADATA = FrameworkMetadata(
        slug="interagency_spatial_causal",
        name="Interagency Spatial Causal Toolkits",
        version="1.0.0",
        layer=VerticalLayer.GOVERNMENT_POLICY,
        tier=Tier.TEAM,
        description=(
            "Cross-agency spatial causal analysis toolkit for "
            "coordinated policy evaluation across jurisdictions."
        ),
        required_domains=["spatial", "agency_data", "policy_interventions"],
        output_domains=["spatial_causal_effects", "spillover_estimates", "coordination_report"],
        constituent_models=["spatial_weights", "causal_estimator", "spillover_model", "agency_harmonizer"],
        tags=["spatial", "causal", "interagency", "coordination", "policy"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = GovernmentTransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        n_cohorts = config.cohort_size or 100
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.65),
            health_burden_score=np.full(n_cohorts, 0.25),
            credit_access_prob=np.full(n_cohorts, 0.55),
            housing_cost_ratio=np.full(n_cohorts, 0.32),
            opportunity_score=np.full(n_cohorts, 0.55),
            sector_output=np.full((n_cohorts, 10), 1000.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.25),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        return {
            "spatial_effect": float(np.std(state.sector_output)),
            "spillover_estimate": float(np.mean(state.opportunity_score) * 0.15),
            "coordination_score": float(1 - np.mean(state.deprivation_vector)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "interagency_spatial_causal", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Interagency Spatial Causal dashboard specification."""
        return FrameworkDashboardSpec(
            slug="interagency_spatial_causal",
            name="Interagency Spatial Causal Toolkits",
            description=(
                "Cross-agency spatial causal analysis toolkit for "
                "coordinated policy evaluation across jurisdictions."
            ),
            layer="government",
            parameters_schema={
                "type": "object",
                "properties": {
                    "agencies": {
                        "type": "array",
                        "title": "Participating Agencies",
                        "items": {
                            "type": "string",
                        },
                        "default": [],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "agencies",
                    },
                    "spatial_granularity": {
                        "type": "string",
                        "title": "Spatial Granularity",
                        "enum": ["county", "state", "region", "national"],
                        "default": "county",
                        "x-ui-widget": "select",
                        "x-ui-group": "spatial",
                    },
                    "causal_model": {
                        "type": "string",
                        "title": "Causal Model",
                        "enum": ["did", "iv", "rdd", "synthetic_control"],
                        "default": "did",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                    },
                },
            },
            default_parameters={
                "agencies": [],
                "spatial_granularity": "county",
                "causal_model": "did",
            },
            parameter_groups=[
                ParameterGroupSpec(key="agencies", title="Agencies", parameters=["agencies"]),
                ParameterGroupSpec(key="spatial", title="Spatial", parameters=["spatial_granularity"]),
                ParameterGroupSpec(key="methodology", title="Methodology", parameters=["causal_model"]),
            ],
            required_domains=["spatial", "agency_data", "policy_interventions"],
            min_tier=Tier.TEAM,
            output_views=[
                OutputViewSpec(
                    key="spillover_effects",
                    title="Spillover Effects",
                    view_type=ViewType.NETWORK,
                    config={"nodes": "jurisdictions", "edges": "spillovers", "weight_by": "effect_size"},
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="spillover_effects_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="agency_impacts",
                    title="Agency Impacts",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "agency", "y_field": "impact", "color_by": "direction"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="agency_impacts_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="spatial_distribution",
                    title="Spatial Distribution",
                    view_type=ViewType.TABLE,
                    config={"columns": ["jurisdiction", "treatment", "effect", "se", "pvalue"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="spatial_distribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
