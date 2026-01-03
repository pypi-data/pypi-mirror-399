# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Advanced Meta/Peer Frameworks
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Advanced Meta/Peer Frameworks.

Extended meta-layer frameworks for cross-model orchestration:

    - IAM-Policy Stacks: Integrated Assessment + Policy modeling
    - HDI/MPI Dashboards: Development indicator dashboards
    - SPI Policy Simulation Stacks: Social Progress simulation

Token Weight: 2-7 per run
Tier: COMMUNITY / PROFESSIONAL

Note: These frameworks can orchestrate models from other layers.
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
from krl_frameworks.core.tier import Tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = [
    "IAMPolicyStackFramework",
    "HDIMPIDashboardFramework",
    "SPIPolicyStackFramework",
]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Meta Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class MetaTransition(TransitionFunction):
    """Transition function for meta-framework orchestration."""
    
    name = "MetaTransition"
    
    def __init__(
        self,
        orchestration_efficiency: float = 0.9,
        cross_layer_synergy: float = 0.1,
    ):
        self.orchestration_efficiency = orchestration_efficiency
        self.cross_layer_synergy = cross_layer_synergy
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply meta-framework transition with cross-layer effects."""
        params = params or {}
        
        # Synergy effect from cross-layer composition
        synergy = params.get("cross_layer_synergy", self.cross_layer_synergy)
        
        # Improve all outcomes through coordination
        new_opportunity = np.clip(
            state.opportunity_score + synergy * 0.02, 0, 1
        )
        new_employment = np.clip(
            state.employment_prob + synergy * 0.01, 0.1, 0.95
        )
        new_health = np.clip(
            state.health_burden_score - synergy * 0.01, 0, 1
        )
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=new_health,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output * (1 + synergy * 0.01),
            deprivation_vector=state.deprivation_vector * (1 - synergy * 0.02),
        )


# ════════════════════════════════════════════════════════════════════════════════
# IAM-Policy Stacks Framework
# ════════════════════════════════════════════════════════════════════════════════


class IAMPolicyStackFramework(BaseMetaFramework):
    """
    IAM-Policy Stacks Framework.
    
    Integrated Assessment + Policy modeling orchestration.
    Token weight: 7
    """
    
    METADATA = FrameworkMetadata(
        slug="iam_policy_stack",
        name="IAM-Policy Stacks",
        version="1.0.0",
        layer=VerticalLayer.META_PEER_FRAMEWORKS,
        tier=Tier.ENTERPRISE,
        description=(
            "Integrated Assessment Model + Policy simulation stack "
            "for climate-policy scenario analysis."
        ),
        required_domains=["climate", "policy", "economic"],
        output_domains=["policy_scenarios", "climate_outcomes", "welfare_impacts"],
        constituent_models=["iam_engine", "policy_simulator", "scenario_composer"],
        tags=["iam", "policy", "climate", "stack", "meta"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = MetaTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.68),
            health_burden_score=np.full(n_cohorts, 0.22),
            credit_access_prob=np.full(n_cohorts, 0.58),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.full(n_cohorts, 0.55),
            sector_output=np.full((n_cohorts, 10), 1050.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.23),
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
            "policy_effectiveness": float(np.mean(state.opportunity_score)),
            "climate_welfare_index": float(1 - np.mean(state.deprivation_vector)),
            "adaptation_score": float(np.mean(state.employment_prob)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "iam_policy_stack", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return IAM-Policy Stack dashboard specification.
        
        Integrated Assessment Model + Policy simulation stack.
        """
        return FrameworkDashboardSpec(
            slug="iam_policy_stack",
            name="IAM-Policy Stacks",
            description=(
                "Integrated Assessment Model + Policy simulation stack "
                "for climate-policy scenario analysis and welfare impacts."
            ),
            layer="meta",
            parameters_schema={
                "type": "object",
                "properties": {
                    "scenarios": {
                        "type": "array",
                        "title": "Climate Scenarios",
                        "description": "Climate scenarios to analyze (e.g., SSP1, SSP2)",
                        "items": {"type": "string"},
                        "default": ["baseline", "mitigation", "adaptation"],
                        "x-ui-widget": "multi-select",
                        "x-ui-group": "scenarios",
                        "x-ui-order": 1,
                    },
                    "policy_instruments": {
                        "type": "array",
                        "title": "Policy Instruments",
                        "description": "Policy instruments to simulate",
                        "items": {
                            "type": "string",
                            "enum": ["carbon_tax", "cap_and_trade", "subsidy", "regulation"],
                        },
                        "default": ["carbon_tax"],
                        "x-ui-widget": "multi-select",
                        "x-ui-group": "policy",
                        "x-ui-order": 1,
                    },
                    "time_horizon": {
                        "type": "integer",
                        "title": "Time Horizon",
                        "description": "Projection horizon in years",
                        "minimum": 10,
                        "maximum": 100,
                        "default": 50,
                        "x-ui-widget": "slider",
                        "x-ui-step": 5,
                        "x-ui-group": "scenarios",
                        "x-ui-order": 2,
                    },
                },
                "required": ["scenarios"],
            },
            default_parameters={
                "scenarios": ["baseline", "mitigation", "adaptation"],
                "policy_instruments": ["carbon_tax"],
                "time_horizon": 50,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="scenarios",
                    title="Scenario Configuration",
                    description="Define climate and policy scenarios",
                    collapsed_by_default=False,
                ),
                ParameterGroupSpec(
                    key="policy",
                    title="Policy Instruments",
                    description="Configure policy intervention options",
                    collapsed_by_default=True,
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="emissions_trajectory",
                    title="Emissions Trajectory",
                    view_type=ViewType.LINE_CHART,
                    description="Projected emissions pathways by scenario",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="emissions_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="policy_costs",
                    title="Policy Costs",
                    view_type=ViewType.BAR_CHART,
                    description="Cost breakdown by policy instrument",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="policy_costs_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="temperature_pathway",
                    title="Temperature Pathway",
                    view_type=ViewType.GAUGE,
                    description="Projected temperature change outcomes",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="temperature_pathway_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
            min_tier=Tier.ENTERPRISE,
        )


# ════════════════════════════════════════════════════════════════════════════════
# HDI/MPI Dashboards Framework
# ════════════════════════════════════════════════════════════════════════════════


class HDIMPIDashboardFramework(BaseMetaFramework):
    """
    HDI/MPI Dashboards Framework.
    
    Development indicator dashboard orchestration.
    Token weight: 2
    """
    
    METADATA = FrameworkMetadata(
        slug="hdi_mpi_dashboard",
        name="HDI / MPI Dashboards",
        version="1.0.0",
        layer=VerticalLayer.META_PEER_FRAMEWORKS,
        tier=Tier.COMMUNITY,
        description=(
            "Development indicator dashboards combining HDI and MPI "
            "for comprehensive development monitoring."
        ),
        required_domains=["health", "education", "economic", "poverty"],
        output_domains=["hdi", "mpi", "combined_dashboard", "trends"],
        constituent_models=["hdi_calculator", "mpi_calculator", "trend_analyzer"],
        tags=["hdi", "mpi", "dashboard", "development", "meta"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = MetaTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.6),
            health_burden_score=np.full(n_cohorts, 0.28),
            credit_access_prob=np.full(n_cohorts, 0.5),
            housing_cost_ratio=np.full(n_cohorts, 0.33),
            opportunity_score=np.full(n_cohorts, 0.48),
            sector_output=np.full((n_cohorts, 10), 850.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.3),
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
        # HDI: geometric mean of health, education, income
        health_idx = 1 - np.mean(state.health_burden_score)
        edu_idx = np.mean(state.opportunity_score)
        income_idx = np.mean(state.employment_prob)
        hdi = (health_idx * edu_idx * income_idx) ** (1/3)
        return {
            "hdi": float(hdi),
            "mpi_headcount": float(np.mean(state.deprivation_vector > 0.33)),
            "development_gap": float(1 - hdi),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "hdi_mpi_dashboard", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return HDI/MPI Dashboard specification.
        
        Combined Human Development Index and Multidimensional Poverty Index dashboard.
        """
        return FrameworkDashboardSpec(
            slug="hdi_mpi_dashboard",
            name="HDI / MPI Dashboards",
            description=(
                "Development indicator dashboards combining HDI and MPI "
                "for comprehensive development monitoring and analysis."
            ),
            layer="meta",
            parameters_schema={
                "type": "object",
                "properties": {
                    "indicators": {
                        "type": "array",
                        "title": "Development Indicators",
                        "description": "Indicators to include in analysis",
                        "items": {
                            "type": "string",
                            "enum": ["life_expectancy", "education", "income", "health", "living_standards"],
                        },
                        "default": ["life_expectancy", "education", "income"],
                        "x-ui-widget": "multi-select",
                        "x-ui-group": "indicators",
                        "x-ui-order": 1,
                    },
                    "weighting_scheme": {
                        "type": "string",
                        "title": "Weighting Scheme",
                        "description": "How to weight different dimensions",
                        "enum": ["equal", "capability", "custom"],
                        "default": "equal",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                        "x-ui-order": 1,
                    },
                    "spatial_scope": {
                        "type": "string",
                        "title": "Spatial Scope",
                        "description": "Geographic level of analysis",
                        "enum": ["national", "subnational", "municipal"],
                        "default": "national",
                        "x-ui-widget": "select",
                        "x-ui-group": "scope",
                        "x-ui-order": 1,
                    },
                },
                "required": ["indicators"],
            },
            default_parameters={
                "indicators": ["life_expectancy", "education", "income"],
                "weighting_scheme": "equal",
                "spatial_scope": "national",
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="indicators",
                    title="Indicator Selection",
                    description="Select development indicators to analyze",
                    collapsed_by_default=False,
                ),
                ParameterGroupSpec(
                    key="methodology",
                    title="Methodology",
                    description="Configure index computation methodology",
                    collapsed_by_default=True,
                ),
                ParameterGroupSpec(
                    key="scope",
                    title="Geographic Scope",
                    description="Define spatial analysis level",
                    collapsed_by_default=True,
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="composite_index",
                    title="Composite Index",
                    view_type=ViewType.GAUGE,
                    description="Overall HDI/MPI composite score",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="composite_index_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="indicator_decomposition",
                    title="Indicator Decomposition",
                    view_type=ViewType.BAR_CHART,
                    description="Contribution of each indicator to the index",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="indicator_decomposition_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="spatial_comparison",
                    title="Spatial Comparison",
                    view_type=ViewType.TABLE,
                    description="Cross-region comparison of development indicators",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="spatial_comparison_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
            min_tier=Tier.ENTERPRISE,
        )


# ════════════════════════════════════════════════════════════════════════════════
# SPI Policy Simulation Stacks Framework
# ════════════════════════════════════════════════════════════════════════════════


class SPIPolicyStackFramework(BaseMetaFramework):
    """
    SPI Policy Simulation Stacks Framework.
    
    Social Progress Index + Policy simulation.
    Token weight: 3
    """
    
    METADATA = FrameworkMetadata(
        slug="spi_policy_stack",
        name="SPI Policy Simulation Stacks",
        version="1.0.0",
        layer=VerticalLayer.META_PEER_FRAMEWORKS,
        tier=Tier.COMMUNITY,
        description=(
            "Social Progress Index + Policy simulation stack for "
            "social progress scenario analysis."
        ),
        required_domains=["social", "health", "infrastructure", "policy"],
        output_domains=["spi", "policy_scenarios", "progress_forecast"],
        constituent_models=["spi_calculator", "policy_simulator", "forecast_engine"],
        tags=["spi", "policy", "social-progress", "stack", "meta"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = MetaTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.62),
            health_burden_score=np.full(n_cohorts, 0.26),
            credit_access_prob=np.full(n_cohorts, 0.52),
            housing_cost_ratio=np.full(n_cohorts, 0.32),
            opportunity_score=np.full(n_cohorts, 0.5),
            sector_output=np.full((n_cohorts, 10), 900.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.28),
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
            "spi_score": float(np.mean(state.opportunity_score) * 100),
            "basic_needs": float(1 - np.mean(state.deprivation_vector)),
            "wellbeing": float(np.mean(state.health_burden_score < 0.3)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "spi_policy_stack", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return SPI Policy Stack dashboard specification.
        
        Social Progress Index + Policy simulation stack.
        """
        return FrameworkDashboardSpec(
            slug="spi_policy_stack",
            name="SPI Policy Simulation Stacks",
            description=(
                "Social Progress Index + Policy simulation stack for "
                "social progress scenario analysis and forecasting."
            ),
            layer="meta",
            parameters_schema={
                "type": "object",
                "properties": {
                    "spi_dimensions": {
                        "type": "array",
                        "title": "SPI Dimensions",
                        "description": "Social progress dimensions to analyze",
                        "items": {
                            "type": "string",
                            "enum": ["basic_needs", "foundations_wellbeing", "opportunity"],
                        },
                        "default": ["basic_needs", "foundations_wellbeing", "opportunity"],
                        "x-ui-widget": "multi-select",
                        "x-ui-group": "dimensions",
                        "x-ui-order": 1,
                    },
                    "policy_targets": {
                        "type": "array",
                        "title": "Policy Targets",
                        "description": "Policy intervention targets",
                        "items": {
                            "type": "string",
                            "enum": ["nutrition", "water_sanitation", "shelter", "safety", "health", "education", "rights", "inclusion"],
                        },
                        "default": ["health", "education"],
                        "x-ui-widget": "multi-select",
                        "x-ui-group": "policy",
                        "x-ui-order": 1,
                    },
                    "benchmark_countries": {
                        "type": "array",
                        "title": "Benchmark Countries",
                        "description": "Countries to use as benchmarks",
                        "items": {"type": "string"},
                        "default": [],
                        "x-ui-widget": "chips",
                        "x-ui-allow-custom": True,
                        "x-ui-group": "benchmarks",
                        "x-ui-order": 1,
                    },
                },
                "required": ["spi_dimensions"],
            },
            default_parameters={
                "spi_dimensions": ["basic_needs", "foundations_wellbeing", "opportunity"],
                "policy_targets": ["health", "education"],
                "benchmark_countries": [],
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="dimensions",
                    title="SPI Dimensions",
                    description="Select social progress dimensions",
                    collapsed_by_default=False,
                ),
                ParameterGroupSpec(
                    key="policy",
                    title="Policy Configuration",
                    description="Configure policy intervention targets",
                    collapsed_by_default=True,
                ),
                ParameterGroupSpec(
                    key="benchmarks",
                    title="Benchmarking",
                    description="Set benchmark countries for comparison",
                    collapsed_by_default=True,
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="spi_scores",
                    title="SPI Scores",
                    view_type=ViewType.GAUGE,
                    description="Overall Social Progress Index score",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="spi_scores_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="dimension_breakdown",
                    title="Dimension Breakdown",
                    view_type=ViewType.BAR_CHART,
                    description="Scores by SPI dimension",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="dimension_breakdown_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="progress_trends",
                    title="Progress Trends",
                    view_type=ViewType.LINE_CHART,
                    description="Social progress trends over time",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="progress_trends_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
            min_tier=Tier.ENTERPRISE,
        )
