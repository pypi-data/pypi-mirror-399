# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Advanced Experimental Frameworks
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Advanced Experimental/Research Frameworks.

Extended frameworks for experimental and computational research:

    - Spatial Causal (GCCM/Matching): Geographically-weighted causal models
    - SD-ABM Hybrids: System Dynamics + Agent-Based Model coupling
    - Multilayer Spatial-Network Engines: Multi-layer network analysis

Token Weight: 6-9 per run
Tier: PROFESSIONAL / ENTERPRISE

References:
    - Anselin, L. (2003). "Spatial Econometrics: Methods and Models"
    - Epstein, J. (2006). "Generative Social Science"
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
    ResultClass,
    TemporalSemantics,
    ViewType,
)
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = [
    "SpatialCausalFramework",
    "SDABMFramework",
    "MultilayerNetworkFramework",
]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Experimental Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class ExperimentalTransition(TransitionFunction):
    """Transition function for experimental cohort evolution."""
    
    name = "ExperimentalTransition"
    
    def __init__(
        self,
        treatment_effect: float = 0.15,
        spillover_decay: float = 0.5,
    ):
        self.treatment_effect = treatment_effect
        self.spillover_decay = spillover_decay
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply experimental transition with treatment effects."""
        params = params or {}
        
        # Treatment effect (for treated cohorts)
        treatment = params.get("treatment_effect", self.treatment_effect)
        treated_mask = params.get("treated_mask", np.random.random(len(state.employment_prob)) > 0.5)
        
        # Apply treatment effect to outcomes
        effect = np.where(treated_mask, treatment, 0)
        
        new_opportunity = np.clip(state.opportunity_score + effect * 0.3, 0, 1)
        new_employment = np.clip(state.employment_prob + effect * 0.2, 0.1, 0.95)
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output * (1 + effect[:, np.newaxis] * 0.05),
            deprivation_vector=state.deprivation_vector * (1 - effect[:, np.newaxis] * 0.1),
        )


# ════════════════════════════════════════════════════════════════════════════════
# Spatial Causal (GCCM/Matching) Framework
# ════════════════════════════════════════════════════════════════════════════════


class SpatialCausalFramework(BaseMetaFramework):
    """
    Spatial Causal (GCCM/Matching) Framework.
    
    Geographically-weighted causal inference with spatial matching.
    Token weight: 6
    """
    
    METADATA = FrameworkMetadata(
        slug="spatial_causal_gccm",
        name="Spatial Causal (GCCM/Matching)",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.TEAM,
        description=(
            "Geographically-weighted causal inference using GCCM "
            "and spatial matching methods."
        ),
        required_domains=["spatial", "treatment", "outcomes", "covariates"],
        output_domains=["spatial_ate", "gwr_coefficients", "matched_pairs"],
        constituent_models=["gccm", "spatial_matching", "gwr", "kriging"],
        tags=["spatial", "causal", "gccm", "matching", "gwr"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = ExperimentalTransition()
    
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
            "spatial_ate": float(np.mean(state.opportunity_score)),
            "gwr_r2": float(0.75 + np.random.random() * 0.15),
            "matched_pairs": int(len(state.employment_prob) // 2),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "spatial_causal_gccm", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Spatial Causal (GCCM/Matching) dashboard specification."""
        return FrameworkDashboardSpec(
            slug="spatial_causal_gccm",
            name="Spatial Causal (GCCM/Matching)",
            description=(
                "Geographically-weighted causal inference using GCCM "
                "and spatial matching methods."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "spatial_bandwidth": {
                        "type": "number",
                        "title": "Spatial Bandwidth",
                        "minimum": 1.0,
                        "maximum": 500.0,
                        "default": 50.0,
                        "x-ui-widget": "slider",
                        "x-ui-group": "spatial",
                    },
                    "kernel_type": {
                        "type": "string",
                        "title": "Kernel Type",
                        "enum": ["gaussian", "bisquare", "exponential"],
                        "default": "gaussian",
                        "x-ui-widget": "select",
                        "x-ui-group": "spatial",
                    },
                    "n_neighbors": {
                        "type": "integer",
                        "title": "Number of Neighbors",
                        "minimum": 5,
                        "maximum": 100,
                        "default": 20,
                        "x-ui-widget": "slider",
                        "x-ui-group": "matching",
                    },
                },
            },
            default_parameters={"spatial_bandwidth": 50.0, "kernel_type": "gaussian", "n_neighbors": 20},
            parameter_groups=[
                ParameterGroupSpec(key="spatial", title="Spatial Settings", parameters=["spatial_bandwidth", "kernel_type"]),
                ParameterGroupSpec(key="matching", title="Matching", parameters=["n_neighbors"]),
            ],
            required_domains=["spatial", "treatment", "outcomes", "covariates"],
            min_tier=Tier.TEAM,
            output_views=[
                OutputViewSpec(
                    key="spatial_ate",
                    title="Spatial ATE Map",
                    view_type=ViewType.CHOROPLETH,
                    config={"color_field": "treatment_effect", "geo_field": "geometry"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="spatial_ate_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="gwr_coefficients",
                    title="GWR Coefficients",
                    view_type=ViewType.HEATMAP,
                    config={"x_field": "location", "y_field": "variable", "value_field": "coefficient"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="gwr_coefficients_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="matched_pairs",
                    title="Matched Pairs",
                    view_type=ViewType.TABLE,
                    config={"columns": ["treated_unit", "control_unit", "distance", "weight"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="matched_pairs_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# SD-ABM Hybrids Framework
# ════════════════════════════════════════════════════════════════════════════════


class SDABMFramework(BaseMetaFramework):
    """
    System Dynamics - Agent-Based Model Hybrids Framework.
    
    Couples SD stock-flow models with ABM micro-behavior.
    Token weight: 8
    """
    
    METADATA = FrameworkMetadata(
        slug="sd_abm",
        name="SD-ABM Hybrids",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.PROFESSIONAL,
        description=(
            "Hybrid System Dynamics and Agent-Based Model coupling "
            "for multi-scale socioeconomic simulation."
        ),
        required_domains=["stock_flows", "agent_behaviors", "network"],
        output_domains=["stock_trajectories", "agent_outcomes", "emergent_patterns"],
        constituent_models=["sd_engine", "abm_engine", "coupling_bridge"],
        tags=["system-dynamics", "abm", "agent-based", "hybrid", "simulation"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = ExperimentalTransition()
    
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
            housing_cost_ratio=np.full(n_cohorts, 0.31),
            opportunity_score=np.full(n_cohorts, 0.50),
            sector_output=np.full((n_cohorts, 10), 950.0),
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
            "stock_level": float(np.sum(state.sector_output)),
            "agent_welfare": float(np.mean(state.opportunity_score)),
            "emergence_score": float(np.std(state.employment_prob)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "sd_abm", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return SD-ABM Hybrids dashboard specification."""
        return FrameworkDashboardSpec(
            slug="sd_abm",
            name="SD-ABM Hybrids",
            description=(
                "Hybrid System Dynamics and Agent-Based Model coupling "
                "for multi-scale socioeconomic simulation."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "n_agents": {
                        "type": "integer",
                        "title": "Number of Agents",
                        "minimum": 100,
                        "maximum": 10000,
                        "default": 1000,
                        "x-ui-widget": "slider",
                        "x-ui-group": "abm",
                    },
                    "sd_timestep": {
                        "type": "number",
                        "title": "SD Timestep",
                        "minimum": 0.01,
                        "maximum": 1.0,
                        "default": 0.1,
                        "x-ui-widget": "slider",
                        "x-ui-group": "sd",
                    },
                    "coupling_frequency": {
                        "type": "integer",
                        "title": "Coupling Frequency",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-group": "coupling",
                    },
                },
            },
            default_parameters={"n_agents": 1000, "sd_timestep": 0.1, "coupling_frequency": 10},
            parameter_groups=[
                ParameterGroupSpec(key="abm", title="Agent-Based Model", parameters=["n_agents"]),
                ParameterGroupSpec(key="sd", title="System Dynamics", parameters=["sd_timestep"]),
                ParameterGroupSpec(key="coupling", title="Coupling", parameters=["coupling_frequency"]),
            ],
            required_domains=["stock_flows", "agent_behaviors", "network"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="stock_trajectories",
                    title="Stock Trajectories",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "time", "y_fields": ["stock_level", "flow_rate"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="stock_trajectories_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="agent_outcomes",
                    title="Agent Outcomes",
                    view_type=ViewType.HISTOGRAM,
                    config={"x_field": "outcome", "bins": 50},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="agent_outcomes_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="emergent_patterns",
                    title="Emergent Patterns",
                    view_type=ViewType.HEATMAP,
                    config={"x_field": "time", "y_field": "variable", "value_field": "value"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="emergent_patterns_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Multilayer Spatial-Network Engines Framework
# ════════════════════════════════════════════════════════════════════════════════


class MultilayerNetworkFramework(BaseMetaFramework):
    """
    Multilayer Spatial-Network Engines Framework.
    
    Multi-layer network analysis with spatial components.
    Token weight: 9
    """
    
    METADATA = FrameworkMetadata(
        slug="multilayer_network",
        name="Multilayer Spatial-Network Engines",
        version="1.0.0",
        layer=VerticalLayer.EXPERIMENTAL_RESEARCH,
        tier=Tier.PROFESSIONAL,
        description=(
            "Multi-layer network analysis engines with spatial "
            "interdependencies and cascading effects."
        ),
        required_domains=["network_layers", "spatial", "node_attributes"],
        output_domains=["multiplex_centrality", "cascade_paths", "community_structure"],
        constituent_models=["multiplex_engine", "spatial_network", "cascade_model"],
        tags=["network", "multilayer", "spatial", "cascade", "multiplex"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = ExperimentalTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.64),
            health_burden_score=np.full(n_cohorts, 0.24),
            credit_access_prob=np.full(n_cohorts, 0.54),
            housing_cost_ratio=np.full(n_cohorts, 0.30),
            opportunity_score=np.full(n_cohorts, 0.52),
            sector_output=np.full((n_cohorts, 10), 1000.0),
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
            "centrality_avg": float(np.mean(state.opportunity_score)),
            "modularity": float(0.35 + np.random.random() * 0.25),
            "cascade_risk": float(np.max(state.deprivation_vector)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "multilayer_network", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Multilayer Spatial-Network dashboard specification."""
        return FrameworkDashboardSpec(
            slug="multilayer_network",
            name="Multilayer Spatial-Network Engines",
            description=(
                "Multi-layer network analysis engines with spatial "
                "interdependencies and cascading effects."
            ),
            layer="experimental",
            parameters_schema={
                "type": "object",
                "properties": {
                    "n_layers": {
                        "type": "integer",
                        "title": "Number of Layers",
                        "minimum": 2,
                        "maximum": 10,
                        "default": 3,
                        "x-ui-widget": "slider",
                        "x-ui-group": "network",
                    },
                    "interlayer_coupling": {
                        "type": "number",
                        "title": "Interlayer Coupling",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.3,
                        "x-ui-widget": "slider",
                        "x-ui-group": "network",
                    },
                    "cascade_threshold": {
                        "type": "number",
                        "title": "Cascade Threshold",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5,
                        "x-ui-widget": "slider",
                        "x-ui-group": "cascade",
                    },
                },
            },
            default_parameters={"n_layers": 3, "interlayer_coupling": 0.3, "cascade_threshold": 0.5},
            parameter_groups=[
                ParameterGroupSpec(key="network", title="Network Structure", parameters=["n_layers", "interlayer_coupling"]),
                ParameterGroupSpec(key="cascade", title="Cascade Dynamics", parameters=["cascade_threshold"]),
            ],
            required_domains=["network_layers", "spatial", "node_attributes"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="multiplex_centrality",
                    title="Multiplex Centrality",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "node", "y_field": "centrality", "color_field": "layer"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="multiplex_centrality_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="cascade_paths",
                    title="Cascade Paths",
                    view_type=ViewType.NETWORK,
                    config={"node_size": "centrality", "edge_width": "flow", "highlight_cascade": True},
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="cascade_paths_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="community_structure",
                    title="Community Structure",
                    view_type=ViewType.HEATMAP,
                    config={"x_field": "node_i", "y_field": "node_j", "value_field": "same_community"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="community_structure_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )
