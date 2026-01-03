# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Advanced Arts/Media Frameworks
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Advanced Arts/Media/Entertainment Frameworks.

Extended frameworks for cultural and media analysis:

    - Cultural CGE: Cultural economics with CGE integration
    - Audience/Media ABM: Agent-based audience simulation
    - Cultural Opportunity/Equity Indices: Cultural access measurement
    - Media Impact/Press & Streaming: Media impact metrics
    - Experimental Integrated Cultural Ecosystem: Full ecosystem modeling

Token Weight: 3-8 per run
Tier: COMMUNITY / PROFESSIONAL

References:
    - Throsby, D. (2001). "Economics and Culture"
    - UNESCO Framework for Cultural Statistics
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
    "CulturalCGEFramework",
    "AudienceABMFramework",
    "CulturalEquityFramework",
    "MediaImpactFramework",
    "IntegratedCulturalFramework",
]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Cultural Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class CulturalTransition(TransitionFunction):
    """Transition function for cultural cohort evolution."""
    
    name = "CulturalTransition"
    
    def __init__(
        self,
        cultural_participation_rate: float = 0.3,
        content_decay: float = 0.1,
    ):
        self.cultural_participation_rate = cultural_participation_rate
        self.content_decay = content_decay
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply cultural transition with participation dynamics."""
        params = params or {}
        
        # Cultural participation affects opportunity and well-being
        participation = params.get(
            "cultural_participation_rate", self.cultural_participation_rate
        )
        
        # Improve opportunity through cultural engagement
        new_opportunity = np.clip(
            state.opportunity_score + participation * 0.02, 0, 1
        )
        
        # Cultural sector output (arts/media sectors)
        arts_growth = 0.03 + participation * 0.02
        new_sector_output = state.sector_output.copy()
        new_sector_output[:, -2:] *= (1 + arts_growth)  # Last 2 sectors = arts/media
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=np.clip(
                state.health_burden_score - participation * 0.005, 0, 1
            ),
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_sector_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Cultural CGE Framework
# ════════════════════════════════════════════════════════════════════════════════


class CulturalCGEFramework(BaseMetaFramework):
    """
    Cultural CGE Framework.
    
    Cultural economics with CGE integration.
    Token weight: 3
    """
    
    METADATA = FrameworkMetadata(
        slug="cultural_cge",
        name="Cultural CGE",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.COMMUNITY,
        description=(
            "Cultural economics modeling with CGE integration for "
            "arts sector economic impact analysis."
        ),
        required_domains=["cultural_sector", "economic", "sam"],
        output_domains=["cultural_gdp", "employment_impact", "multipliers"],
        constituent_models=["cultural_sam", "cge_solver", "satellite_accounts"],
        tags=["culture", "cge", "economics", "arts", "multiplier"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = CulturalTransition()
    
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
            health_burden_score=np.full(n_cohorts, 0.25),
            credit_access_prob=np.full(n_cohorts, 0.5),
            housing_cost_ratio=np.full(n_cohorts, 0.35),
            opportunity_score=np.full(n_cohorts, 0.5),
            sector_output=np.full((n_cohorts, 10), 800.0),
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
            "cultural_gdp_share": float(np.mean(state.sector_output[:, -2:]) / 800),
            "employment_multiplier": float(1.0 + np.mean(state.employment_prob) * 0.5),
            "arts_sector_output": float(np.sum(state.sector_output[:, -2:])),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "cultural_cge", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Dashboard specification for cultural CGE modeling."""
        return FrameworkDashboardSpec(
            slug="cultural_cge",
            name="Cultural CGE Modeling",
            description=(
                "Cultural economics modeling with CGE integration for "
                "arts sector economic impact analysis."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    "cultural_participation_rate": {
                        "type": "number",
                        "title": "Cultural Participation Rate",
                        "description": "Baseline cultural participation rate in population",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.3,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-format": ".0%",
                        "x-ui-group": "participation",
                    },
                    "content_decay": {
                        "type": "number",
                        "title": "Content Decay Rate",
                        "description": "Annual decay rate for cultural content value",
                        "minimum": 0.0,
                        "maximum": 0.5,
                        "default": 0.1,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-format": ".0%",
                        "x-ui-group": "economic",
                    },
                    "shock_type": {
                        "type": "string",
                        "title": "Shock Type",
                        "description": "Type of economic shock to simulate",
                        "enum": ["demand_shock", "supply_shock", "policy_change", "technology_shock"],
                        "default": "demand_shock",
                        "x-ui-widget": "select",
                        "x-ui-group": "scenario",
                    },
                    "shock_magnitude": {
                        "type": "number",
                        "title": "Shock Magnitude (%)",
                        "description": "Magnitude of economic shock",
                        "minimum": -50,
                        "maximum": 50,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-step": 5,
                        "x-ui-format": ".0%",
                        "x-ui-group": "scenario",
                    },
                    "cultural_sector": {
                        "type": "string",
                        "title": "Cultural Sector",
                        "description": "Primary cultural sector for analysis",
                        "enum": ["performing_arts", "visual_arts", "publishing", "audiovisual", "heritage", "design"],
                        "default": "performing_arts",
                        "x-ui-widget": "select",
                        "x-ui-group": "sector",
                    },
                },
                "required": [],
            },
            default_parameters={
                "cultural_participation_rate": 0.3,
                "content_decay": 0.1,
                "shock_type": "demand_shock",
                "shock_magnitude": 10,
                "cultural_sector": "performing_arts",
            },
            min_tier=Tier.COMMUNITY,
            parameter_groups=[
                ParameterGroupSpec(
                    key="participation",
                    title="Participation",
                    parameters=["cultural_participation_rate"],
                ),
                ParameterGroupSpec(
                    key="sector",
                    title="Cultural Sector",
                    parameters=["cultural_sector"],
                ),
                ParameterGroupSpec(
                    key="economic",
                    title="Economic Parameters",
                    parameters=["content_decay"],
                ),
                ParameterGroupSpec(
                    key="scenario",
                    title="Shock Scenario",
                    parameters=["shock_type", "shock_magnitude"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="sector_impacts",
                    title="Sector Impacts",
                    view_type=ViewType.BAR_CHART,
                    description="Economic impacts by sector",
                    config={"x_field": "sector", "y_field": "impact"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="sector_impacts_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="multiplier_effects",
                    title="Multiplier Effects",
                    view_type=ViewType.TABLE,
                    description="Economic multiplier analysis",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="multiplier_effects_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="employment_effects",
                    title="Employment Effects",
                    view_type=ViewType.LINE_CHART,
                    description="Employment impact trajectory",
                    config={"x_field": "period", "y_fields": ["direct", "indirect", "induced"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="employment_effects_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Audience/Media ABM Framework
# ════════════════════════════════════════════════════════════════════════════════


class AudienceABMFramework(BaseMetaFramework):
    """
    Audience/Media ABM Framework.
    
    Agent-based audience simulation for media consumption.
    Token weight: 3
    """
    
    METADATA = FrameworkMetadata(
        slug="audience_abm",
        name="Audience / Media ABM",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.COMMUNITY,
        description=(
            "Agent-based audience simulation for media consumption "
            "patterns and content diffusion."
        ),
        required_domains=["audience_data", "content_catalog", "behavior"],
        output_domains=["viewership", "engagement", "diffusion_curves"],
        constituent_models=["abm_engine", "preference_model", "social_influence"],
        tags=["audience", "abm", "media", "simulation", "diffusion"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = CulturalTransition()
    
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
            health_burden_score=np.full(n_cohorts, 0.23),
            credit_access_prob=np.full(n_cohorts, 0.52),
            housing_cost_ratio=np.full(n_cohorts, 0.33),
            opportunity_score=np.full(n_cohorts, 0.52),
            sector_output=np.full((n_cohorts, 10), 850.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.26),
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
            "viewership_rate": float(np.mean(state.opportunity_score)),
            "engagement_score": float(np.mean(state.employment_prob)),
            "diffusion_speed": float(0.15 + np.random.random() * 0.1),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "audience_abm", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Dashboard specification for audience ABM."""
        return FrameworkDashboardSpec(
            slug="audience_abm",
            name="Audience ABM",
            description=(
                "Agent-based audience simulation for media consumption "
                "patterns and content diffusion."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    "n_agents": {
                        "type": "integer",
                        "title": "Number of Agents",
                        "description": "Total number of audience agents to simulate",
                        "minimum": 100,
                        "maximum": 100000,
                        "default": 1000,
                        "x-ui-widget": "number",
                        "x-ui-group": "agents",
                    },
                    "network_type": {
                        "type": "string",
                        "title": "Network Type",
                        "description": "Social network topology",
                        "enum": ["random", "small_world", "scale_free", "lattice"],
                        "default": "small_world",
                        "x-ui-widget": "select",
                        "x-ui-group": "network",
                    },
                    "connectivity": {
                        "type": "number",
                        "title": "Network Connectivity",
                        "description": "Average connections per agent",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 8,
                        "x-ui-widget": "slider",
                        "x-ui-group": "network",
                    },
                    "influence_decay": {
                        "type": "number",
                        "title": "Influence Decay",
                        "description": "Rate at which social influence decays with distance",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "network",
                    },
                    "content_type": {
                        "type": "string",
                        "title": "Content Type",
                        "description": "Type of content being diffused",
                        "enum": ["video", "audio", "text", "interactive", "mixed"],
                        "default": "video",
                        "x-ui-widget": "select",
                        "x-ui-group": "content",
                    },
                    "cultural_participation_rate": {
                        "type": "number",
                        "title": "Base Participation Rate",
                        "description": "Baseline cultural participation probability",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.3,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-format": ".0%",
                        "x-ui-group": "agents",
                    },
                },
                "required": [],
            },
            default_parameters={
                "n_agents": 1000,
                "network_type": "small_world",
                "connectivity": 8,
                "influence_decay": 0.5,
                "content_type": "video",
                "cultural_participation_rate": 0.3,
            },
            min_tier=Tier.COMMUNITY,
            parameter_groups=[
                ParameterGroupSpec(
                    key="agents",
                    title="Agent Population",
                    parameters=["n_agents", "cultural_participation_rate"],
                ),
                ParameterGroupSpec(
                    key="network",
                    title="Social Network",
                    parameters=["network_type", "connectivity", "influence_decay"],
                ),
                ParameterGroupSpec(
                    key="content",
                    title="Content Type",
                    parameters=["content_type"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="adoption_curves",
                    title="Adoption Curves",
                    view_type=ViewType.LINE_CHART,
                    description="Content adoption over time",
                    config={"x_field": "time", "y_fields": ["adopters", "cumulative"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="adoption_curves_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="preference_distribution",
                    title="Preference Distribution",
                    view_type=ViewType.HISTOGRAM,
                    description="Agent preference distributions",
                    config={"field": "preference", "bins": 20},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="preference_distribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="network_visualization",
                    title="Network Visualization",
                    view_type=ViewType.NETWORK,
                    description="Social network influence graph",
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="network_visualization_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Cultural Opportunity/Equity Indices Framework
# ════════════════════════════════════════════════════════════════════════════════


class CulturalEquityFramework(BaseMetaFramework):
    """
    Cultural Opportunity/Equity Indices Framework.
    
    Cultural access and equity measurement.
    Token weight: 4
    """
    
    METADATA = FrameworkMetadata(
        slug="cultural_equity",
        name="Cultural Opportunity / Equity Indices",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.TEAM,
        description=(
            "Cultural opportunity and equity index construction "
            "for measuring access to arts and culture."
        ),
        required_domains=["cultural_facilities", "demographics", "participation"],
        output_domains=["cultural_opportunity_index", "equity_score", "access_gaps"],
        constituent_models=["opportunity_mapper", "equity_calculator", "gap_analyzer"],
        tags=["culture", "equity", "opportunity", "index", "access"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = CulturalTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.58),
            health_burden_score=np.full(n_cohorts, 0.27),
            credit_access_prob=np.full(n_cohorts, 0.48),
            housing_cost_ratio=np.full(n_cohorts, 0.36),
            opportunity_score=np.full(n_cohorts, 0.45),
            sector_output=np.full((n_cohorts, 10), 750.0),
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
        return {
            "opportunity_index": float(np.mean(state.opportunity_score)),
            "equity_score": float(1 - np.std(state.opportunity_score)),
            "access_gap": float(np.max(state.deprivation_vector) - np.min(state.deprivation_vector)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "cultural_equity", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Dashboard specification for cultural equity measurement."""
        return FrameworkDashboardSpec(
            slug="cultural_equity",
            name="Cultural Equity Indices",
            description=(
                "Cultural opportunity and equity index construction "
                "for measuring access to arts and culture."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    "equity_dimension": {
                        "type": "string",
                        "title": "Equity Dimension",
                        "description": "Primary dimension for equity analysis",
                        "enum": ["access", "participation", "representation", "funding", "outcomes"],
                        "default": "access",
                        "x-ui-widget": "select",
                        "x-ui-group": "equity",
                    },
                    "geographic_scope": {
                        "type": "string",
                        "title": "Geographic Scope",
                        "description": "Geographic level of analysis",
                        "enum": ["national", "regional", "local", "neighborhood"],
                        "default": "regional",
                        "x-ui-widget": "select",
                        "x-ui-group": "geography",
                    },
                    "demographic_focus": {
                        "type": "string",
                        "title": "Demographic Focus",
                        "description": "Primary demographic dimension for disparity analysis",
                        "enum": ["age", "income", "race_ethnicity", "education", "disability", "rural_urban"],
                        "default": "income",
                        "x-ui-widget": "select",
                        "x-ui-group": "demographics",
                    },
                    "cultural_participation_rate": {
                        "type": "number",
                        "title": "Baseline Participation",
                        "description": "Baseline cultural participation rate",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.3,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-format": ".0%",
                        "x-ui-group": "equity",
                    },
                    "index_weighting": {
                        "type": "string",
                        "title": "Index Weighting",
                        "description": "Weighting scheme for composite index",
                        "enum": ["equal", "pca", "expert", "outcome_based"],
                        "default": "equal",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                    },
                },
                "required": [],
            },
            default_parameters={
                "equity_dimension": "access",
                "geographic_scope": "regional",
                "demographic_focus": "income",
                "cultural_participation_rate": 0.3,
                "index_weighting": "equal",
            },
            min_tier=Tier.PROFESSIONAL,
            parameter_groups=[
                ParameterGroupSpec(
                    key="equity",
                    title="Equity Dimensions",
                    parameters=["equity_dimension", "cultural_participation_rate"],
                ),
                ParameterGroupSpec(
                    key="geography",
                    title="Geographic Scope",
                    parameters=["geographic_scope"],
                ),
                ParameterGroupSpec(
                    key="demographics",
                    title="Demographics",
                    parameters=["demographic_focus"],
                ),
                ParameterGroupSpec(
                    key="methodology",
                    title="Methodology",
                    parameters=["index_weighting"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="equity_index",
                    title="Equity Index",
                    view_type=ViewType.GAUGE,
                    description="Overall cultural equity score",
                    config={"min": 0, "max": 100, "thresholds": [40, 60, 80]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="equity_index_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="disparity_analysis",
                    title="Disparity Analysis",
                    view_type=ViewType.BAR_CHART,
                    description="Equity gaps by dimension",
                    config={"x_field": "group", "y_field": "gap"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="disparity_analysis_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="access_map",
                    title="Access Map",
                    view_type=ViewType.TABLE,
                    description="Cultural access by geography",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="access_map_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Media Impact/Press & Streaming Framework
# ════════════════════════════════════════════════════════════════════════════════


class MediaImpactFramework(BaseMetaFramework):
    """
    Media Impact/Press & Streaming Framework.
    
    Media impact metrics for press and streaming content.
    Token weight: 6
    """
    
    METADATA = FrameworkMetadata(
        slug="media_impact_streaming",
        name="Media Impact / Press & Streaming",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.PROFESSIONAL,
        description=(
            "Media impact metrics for press and streaming content "
            "including reach, engagement, and influence."
        ),
        required_domains=["media_data", "audience", "engagement"],
        output_domains=["reach", "impressions", "influence_score", "roi"],
        constituent_models=["reach_model", "attribution", "sentiment_analyzer"],
        tags=["media", "impact", "streaming", "press", "influence"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = CulturalTransition()
    
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
            health_burden_score=np.full(n_cohorts, 0.22),
            credit_access_prob=np.full(n_cohorts, 0.55),
            housing_cost_ratio=np.full(n_cohorts, 0.32),
            opportunity_score=np.full(n_cohorts, 0.55),
            sector_output=np.full((n_cohorts, 10), 950.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.24),
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
            "reach": float(np.mean(state.opportunity_score) * 1e6),
            "engagement_rate": float(np.mean(state.employment_prob)),
            "influence_score": float(np.mean(state.sector_output[:, -2:]) / 950),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "media_impact_streaming", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Dashboard specification for media impact analysis."""
        return FrameworkDashboardSpec(
            slug="media_impact_streaming",
            name="Media Impact Analysis",
            description=(
                "Media impact metrics for press and streaming content "
                "including reach, engagement, and influence."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    "media_type": {
                        "type": "string",
                        "title": "Media Type",
                        "description": "Type of media channel",
                        "enum": ["press", "streaming", "broadcast", "social", "podcast"],
                        "default": "streaming",
                        "x-ui-widget": "select",
                        "x-ui-group": "media",
                    },
                    "effect_model": {
                        "type": "string",
                        "title": "Effect Model",
                        "description": "Media effect theory model",
                        "enum": ["direct_effects", "agenda_setting", "priming", "framing", "cultivation"],
                        "default": "direct_effects",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                    },
                    "audience_scope": {
                        "type": "string",
                        "title": "Audience Scope",
                        "description": "Target audience scope",
                        "enum": ["mass", "niche", "targeted", "personalized"],
                        "default": "mass",
                        "x-ui-widget": "select",
                        "x-ui-group": "audience",
                    },
                    "cultural_participation_rate": {
                        "type": "number",
                        "title": "Engagement Rate",
                        "description": "Base audience engagement rate",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.3,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-format": ".0%",
                        "x-ui-group": "audience",
                    },
                    "content_decay": {
                        "type": "number",
                        "title": "Impact Decay Rate",
                        "description": "Rate at which media impact decays",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.1,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-group": "methodology",
                    },
                    "attribution_window_days": {
                        "type": "integer",
                        "title": "Attribution Window (Days)",
                        "description": "Days to attribute media effects",
                        "minimum": 1,
                        "maximum": 90,
                        "default": 30,
                        "x-ui-widget": "slider",
                        "x-ui-group": "methodology",
                    },
                },
                "required": [],
            },
            default_parameters={
                "media_type": "streaming",
                "effect_model": "direct_effects",
                "audience_scope": "mass",
                "cultural_participation_rate": 0.3,
                "content_decay": 0.1,
                "attribution_window_days": 30,
            },
            min_tier=Tier.PROFESSIONAL,
            parameter_groups=[
                ParameterGroupSpec(
                    key="media",
                    title="Media Type",
                    parameters=["media_type"],
                ),
                ParameterGroupSpec(
                    key="audience",
                    title="Audience",
                    parameters=["audience_scope", "cultural_participation_rate"],
                ),
                ParameterGroupSpec(
                    key="methodology",
                    title="Methodology",
                    parameters=["effect_model", "content_decay", "attribution_window_days"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="impact_attribution",
                    title="Impact Attribution",
                    view_type=ViewType.BAR_CHART,
                    description="Impact by media channel",
                    config={"x_field": "channel", "y_field": "impact"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="impact_attribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="reach_trajectory",
                    title="Reach Trajectory",
                    view_type=ViewType.LINE_CHART,
                    description="Audience reach over time",
                    config={"x_field": "time", "y_fields": ["reach", "engagement"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="reach_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="effect_magnitude",
                    title="Effect Magnitude",
                    view_type=ViewType.GAUGE,
                    description="Overall media effect strength",
                    config={"min": 0, "max": 100, "thresholds": [30, 60, 80]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="effect_magnitude_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Experimental Integrated Cultural Ecosystem Framework
# ════════════════════════════════════════════════════════════════════════════════


class IntegratedCulturalFramework(BaseMetaFramework):
    """
    Experimental Integrated Cultural Ecosystem Framework.
    
    Full cultural ecosystem modeling.
    Token weight: 8
    """
    
    METADATA = FrameworkMetadata(
        slug="integrated_cultural_ecosystem",
        name="Experimental Integrated Cultural Ecosystem",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.PROFESSIONAL,
        description=(
            "Full cultural ecosystem modeling integrating production, "
            "distribution, consumption, and impact pathways."
        ),
        required_domains=["cultural_production", "distribution", "consumption", "impact"],
        output_domains=["ecosystem_health", "value_chain", "sustainability_score"],
        constituent_models=["ecosystem_engine", "value_chain_model", "sustainability_assessor"],
        tags=["culture", "ecosystem", "integrated", "experimental", "sustainability"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = CulturalTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.63),
            health_burden_score=np.full(n_cohorts, 0.24),
            credit_access_prob=np.full(n_cohorts, 0.53),
            housing_cost_ratio=np.full(n_cohorts, 0.33),
            opportunity_score=np.full(n_cohorts, 0.53),
            sector_output=np.full((n_cohorts, 10), 900.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.26),
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
            "ecosystem_health": float(np.mean(state.opportunity_score)),
            "value_chain_efficiency": float(np.mean(state.sector_output) / 900),
            "sustainability_score": float(1 - np.mean(state.deprivation_vector)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "integrated_cultural_ecosystem", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Dashboard specification for integrated cultural ecosystem."""
        return FrameworkDashboardSpec(
            slug="integrated_cultural_ecosystem",
            name="Integrated Cultural Ecosystem",
            description=(
                "Full cultural ecosystem modeling integrating production, "
                "distribution, consumption, and impact pathways."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    "component_frameworks": {
                        "type": "array",
                        "title": "Component Frameworks",
                        "description": "Sub-frameworks to include in integration",
                        "items": {
                            "type": "string",
                            "enum": ["cultural_cge", "audience_abm", "cultural_equity", "media_impact"],
                        },
                        "default": ["cultural_cge", "audience_abm"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "integration",
                    },
                    "integration_method": {
                        "type": "string",
                        "title": "Integration Method",
                        "description": "Method for combining framework outputs",
                        "enum": ["sequential", "parallel", "weighted_ensemble", "hierarchical"],
                        "default": "sequential",
                        "x-ui-widget": "select",
                        "x-ui-group": "integration",
                    },
                    "analysis_scope": {
                        "type": "string",
                        "title": "Analysis Scope",
                        "description": "Focus area for ecosystem analysis",
                        "enum": ["production", "distribution", "consumption", "impact", "full_chain"],
                        "default": "full_chain",
                        "x-ui-widget": "select",
                        "x-ui-group": "scope",
                    },
                    "cultural_participation_rate": {
                        "type": "number",
                        "title": "Participation Rate",
                        "description": "Baseline cultural participation rate",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.3,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-format": ".0%",
                        "x-ui-group": "parameters",
                    },
                    "content_decay": {
                        "type": "number",
                        "title": "Content Decay Rate",
                        "description": "Annual decay rate for cultural content",
                        "minimum": 0.0,
                        "maximum": 0.5,
                        "default": 0.1,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-format": ".0%",
                        "x-ui-group": "parameters",
                    },
                    "simulation_periods": {
                        "type": "integer",
                        "title": "Simulation Periods",
                        "description": "Number of time periods to simulate",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 12,
                        "x-ui-widget": "slider",
                        "x-ui-group": "simulation",
                    },
                },
                "required": [],
            },
            default_parameters={
                "component_frameworks": ["cultural_cge", "audience_abm"],
                "integration_method": "sequential",
                "analysis_scope": "full_chain",
                "cultural_participation_rate": 0.3,
                "content_decay": 0.1,
                "simulation_periods": 12,
            },
            min_tier=Tier.PROFESSIONAL,
            parameter_groups=[
                ParameterGroupSpec(
                    key="integration",
                    title="Integration Settings",
                    parameters=["component_frameworks", "integration_method"],
                ),
                ParameterGroupSpec(
                    key="scope",
                    title="Analysis Scope",
                    parameters=["analysis_scope"],
                ),
                ParameterGroupSpec(
                    key="parameters",
                    title="Model Parameters",
                    parameters=["cultural_participation_rate", "content_decay"],
                ),
                ParameterGroupSpec(
                    key="simulation",
                    title="Simulation",
                    parameters=["simulation_periods"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="integrated_dashboard",
                    title="Integrated Dashboard",
                    view_type=ViewType.METRIC_GRID,
                    description="Combined ecosystem metrics",
                    config={"metrics": ["ecosystem_health", "value_chain_efficiency", "sustainability_score"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="integrated_dashboard_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="component_results",
                    title="Component Results",
                    view_type=ViewType.TABLE,
                    description="Results from each sub-framework",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="component_results_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="ecosystem_trajectory",
                    title="Ecosystem Trajectory",
                    view_type=ViewType.LINE_CHART,
                    description="Ecosystem evolution over time",
                    config={"x_field": "period", "y_fields": ["health", "efficiency", "sustainability"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="ecosystem_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
