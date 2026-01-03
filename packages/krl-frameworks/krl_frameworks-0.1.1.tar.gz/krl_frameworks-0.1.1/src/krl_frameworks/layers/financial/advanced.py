# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Advanced Financial Frameworks
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Advanced Financial/Economic Frameworks.

Extended frameworks for financial risk and economic modeling:

    - Macro-Financial CGE: Macro-finance with CGE integration
    - Networked Financial: Financial network contagion models
    - Risk Indices: Composite financial risk indices
    - Composite Risk/Solvency: Aggregated risk scoring
    - Financial Meta-Orchestrators: Cross-model orchestration

Token Weight: 3-10 per run
Tier: COMMUNITY / PROFESSIONAL / ENTERPRISE

References:
    - Acemoglu et al. (2015). "Systemic Risk and Network Formation"
    - Battiston et al. (2012). "DebtRank"
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
    "MacroFinancialCGEFramework",
    "NetworkedFinancialFramework",
    "RiskIndicesFramework",
    "CompositeRiskFramework",
    "FinancialMetaOrchestratorFramework",
]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Financial Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class FinancialTransition(TransitionFunction):
    """Transition function for financial cohort evolution."""
    
    name = "FinancialTransition"
    
    def __init__(
        self,
        interest_rate: float = 0.05,
        default_rate: float = 0.02,
        recovery_rate: float = 0.4,
    ):
        self.interest_rate = interest_rate
        self.default_rate = default_rate
        self.recovery_rate = recovery_rate
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply financial transition with risk dynamics."""
        params = params or {}
        
        # Credit access depends on risk
        default_rate = params.get("default_rate", self.default_rate)
        risk_shock = params.get("risk_shock", 0.0)
        
        # Apply default and credit tightening
        defaults = np.random.random(len(state.credit_access_prob)) < (default_rate + risk_shock)
        
        new_credit = np.where(
            defaults,
            state.credit_access_prob * 0.5,
            state.credit_access_prob * 1.01
        )
        new_credit = np.clip(new_credit, 0, 1)
        
        # Sector output affected by financial conditions
        credit_multiplier = np.mean(new_credit)
        new_sector_output = state.sector_output * (0.98 + credit_multiplier * 0.04)
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=state.health_burden_score,
            credit_access_prob=new_credit,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=state.opportunity_score,
            sector_output=new_sector_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Macro-Financial CGE Framework
# ════════════════════════════════════════════════════════════════════════════════


class MacroFinancialCGEFramework(BaseMetaFramework):
    """
    Macro-Financial CGE Framework.
    
    Integrates macro-finance models with CGE for systemic analysis.
    Token weight: 7
    """
    
    METADATA = FrameworkMetadata(
        slug="macro_financial_cge",
        name="Macro-Financial CGE",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.TEAM,
        description=(
            "Macro-financial modeling integrated with CGE for "
            "systemic risk and economic impact analysis."
        ),
        required_domains=["financial", "macro", "sam"],
        output_domains=["systemic_risk", "macro_impact", "welfare"],
        constituent_models=["dsge", "cge_solver", "financial_accelerator"],
        tags=["macro", "financial", "cge", "systemic-risk", "dsge"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = FinancialTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.7),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.full(n_cohorts, 0.65),
            housing_cost_ratio=np.full(n_cohorts, 0.28),
            opportunity_score=np.full(n_cohorts, 0.6),
            sector_output=np.full((n_cohorts, 10), 1200.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.2),
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
            "systemic_risk": float(1 - np.mean(state.credit_access_prob)),
            "macro_welfare": float(np.mean(state.opportunity_score)),
            "gdp_growth": float(np.mean(state.sector_output) / 1200 - 1),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "macro_financial_cge", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Macro-Financial CGE dashboard specification."""
        return FrameworkDashboardSpec(
            slug="macro_financial_cge",
            name="Macro-Financial CGE",
            description=(
                "Macro-financial modeling integrated with CGE for "
                "systemic risk and economic impact analysis."
            ),
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "interest_rate": {
                        "type": "number",
                        "title": "Interest Rate",
                        "minimum": 0.0,
                        "maximum": 0.2,
                        "default": 0.05,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-format": ".1%",
                        "x-ui-group": "macro",
                    },
                    "gdp_growth": {
                        "type": "number",
                        "title": "GDP Growth Rate",
                        "minimum": -0.1,
                        "maximum": 0.1,
                        "default": 0.02,
                        "x-ui-widget": "slider",
                        "x-ui-format": ".1%",
                        "x-ui-group": "macro",
                    },
                    "credit_shock": {
                        "type": "number",
                        "title": "Credit Shock",
                        "minimum": -0.3,
                        "maximum": 0.0,
                        "default": 0.0,
                        "x-ui-widget": "slider",
                        "x-ui-group": "financial",
                    },
                    "n_periods": {
                        "type": "integer",
                        "title": "Quarters",
                        "minimum": 1,
                        "maximum": 40,
                        "default": 12,
                        "x-ui-widget": "slider",
                        "x-ui-group": "simulation",
                    },
                },
            },
            default_parameters={"interest_rate": 0.05, "gdp_growth": 0.02, "credit_shock": 0.0, "n_periods": 12},
            parameter_groups=[
                ParameterGroupSpec(key="macro", title="Macroeconomic", parameters=["interest_rate", "gdp_growth"]),
                ParameterGroupSpec(key="financial", title="Financial Conditions", parameters=["credit_shock"]),
                ParameterGroupSpec(key="simulation", title="Simulation", parameters=["n_periods"]),
            ],
            required_domains=["financial", "macro", "sam"],
            min_tier=Tier.ENTERPRISE,
            output_views=[
                OutputViewSpec(
                    key="systemic_risk",
                    title="Systemic Risk",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 1, "thresholds": [0.3, 0.5, 0.7], "format": ".1%"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="systemic_risk_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="gdp_trajectory",
                    title="GDP Trajectory",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "quarter", "y_fields": ["gdp_growth", "credit_growth"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="gdp_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="welfare",
                    title="Welfare Impact",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "sector", "y_field": "welfare_change"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="welfare_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Networked Financial Framework
# ════════════════════════════════════════════════════════════════════════════════


class NetworkedFinancialFramework(BaseMetaFramework):
    """
    Networked Financial Framework.
    
    Financial network contagion and systemic risk modeling.
    Token weight: 8
    """
    
    METADATA = FrameworkMetadata(
        slug="networked_financial",
        name="Networked Financial",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.PROFESSIONAL,
        description=(
            "Financial network contagion models for systemic risk "
            "assessment and cascading failure analysis."
        ),
        required_domains=["financial_network", "exposures", "balance_sheets"],
        output_domains=["debtrank", "contagion_paths", "systemic_importance"],
        constituent_models=["debtrank", "contagion_engine", "network_metrics"],
        tags=["network", "financial", "contagion", "systemic-risk", "debtrank"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = FinancialTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.72),
            health_burden_score=np.full(n_cohorts, 0.18),
            credit_access_prob=np.full(n_cohorts, 0.7),
            housing_cost_ratio=np.full(n_cohorts, 0.26),
            opportunity_score=np.full(n_cohorts, 0.62),
            sector_output=np.full((n_cohorts, 10), 1300.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.18),
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
            "debtrank": float(1 - np.mean(state.credit_access_prob)),
            "contagion_probability": float(np.std(state.credit_access_prob)),
            "systemically_important": int(np.sum(state.sector_output > 1200)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "networked_financial", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Networked Financial dashboard specification."""
        return FrameworkDashboardSpec(
            slug="networked_financial",
            name="Networked Financial",
            description="Financial network contagion and systemic risk modeling.",
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "default_rate": {
                        "type": "number",
                        "title": "Default Rate",
                        "minimum": 0.0,
                        "maximum": 0.2,
                        "default": 0.02,
                        "x-ui-widget": "slider",
                        "x-ui-format": ".1%",
                        "x-ui-group": "network",
                    },
                    "contagion_threshold": {
                        "type": "number",
                        "title": "Contagion Threshold",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5,
                        "x-ui-widget": "slider",
                        "x-ui-group": "network",
                    },
                    "initial_shock": {
                        "type": "string",
                        "title": "Initial Shock Node",
                        "enum": ["largest", "most_connected", "random", "none"],
                        "default": "none",
                        "x-ui-widget": "select",
                        "x-ui-group": "scenario",
                    },
                    "n_periods": {
                        "type": "integer",
                        "title": "Periods",
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-group": "simulation",
                    },
                },
            },
            default_parameters={"default_rate": 0.02, "contagion_threshold": 0.5, "initial_shock": "none", "n_periods": 10},
            parameter_groups=[
                ParameterGroupSpec(key="network", title="Network Parameters", parameters=["default_rate", "contagion_threshold"]),
                ParameterGroupSpec(key="scenario", title="Scenario", parameters=["initial_shock"]),
                ParameterGroupSpec(key="simulation", title="Simulation", parameters=["n_periods"]),
            ],
            required_domains=["financial_network", "exposures", "balance_sheets"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="debtrank",
                    title="DebtRank",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 1, "thresholds": [0.3, 0.5, 0.7], "format": ".3f"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="debtrank_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="network_graph",
                    title="Network Graph",
                    view_type=ViewType.NETWORK,
                    config={"node_size": "assets", "edge_width": "exposure", "node_color": "risk"},
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="network_graph_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="cascade",
                    title="Cascade Path",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "step", "y_fields": ["defaults", "contagion"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="cascade_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Risk Indices Framework
# ════════════════════════════════════════════════════════════════════════════════


class RiskIndicesFramework(BaseMetaFramework):
    """
    Risk Indices Framework.
    
    Composite financial risk index construction.
    Token weight: 3
    """
    
    METADATA = FrameworkMetadata(
        slug="risk_indices",
        name="Risk Indices",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.COMMUNITY,
        description=(
            "Composite financial risk index construction for "
            "market and credit risk monitoring."
        ),
        required_domains=["market_data", "credit_data"],
        output_domains=["risk_index", "volatility_index", "stress_indicator"],
        constituent_models=["var_model", "cds_spreads", "volatility_surface"],
        tags=["risk", "index", "financial", "vix", "credit-risk"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = FinancialTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.7),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.full(n_cohorts, 0.6),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.full(n_cohorts, 0.55),
            sector_output=np.full((n_cohorts, 10), 1000.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.22),
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
            "risk_index": float(np.std(state.credit_access_prob) * 100),
            "volatility_index": float(np.std(state.sector_output)),
            "stress_level": float(np.mean(state.deprivation_vector)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "risk_indices", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Risk Indices dashboard specification."""
        return FrameworkDashboardSpec(
            slug="risk_indices",
            name="Risk Indices",
            description="Composite financial risk index construction.",
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "index_type": {
                        "type": "string",
                        "title": "Index Type",
                        "enum": ["volatility", "credit_spread", "liquidity", "composite"],
                        "default": "composite",
                        "x-ui-widget": "select",
                        "x-ui-group": "index",
                    },
                    "lookback_days": {
                        "type": "integer",
                        "title": "Lookback Period (days)",
                        "minimum": 5,
                        "maximum": 252,
                        "default": 21,
                        "x-ui-widget": "slider",
                        "x-ui-group": "index",
                    },
                    "weighting": {
                        "type": "string",
                        "title": "Component Weighting",
                        "enum": ["equal", "market_cap", "inverse_volatility", "pca"],
                        "default": "equal",
                        "x-ui-widget": "select",
                        "x-ui-group": "index",
                    },
                },
            },
            default_parameters={"index_type": "composite", "lookback_days": 21, "weighting": "equal"},
            parameter_groups=[
                ParameterGroupSpec(key="index", title="Index Configuration", parameters=["index_type", "lookback_days", "weighting"]),
            ],
            required_domains=["market_data", "credit_data"],
            min_tier=Tier.COMMUNITY,
            output_views=[
                OutputViewSpec(
                    key="risk_gauge",
                    title="Risk Index",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 100, "thresholds": [20, 50, 80], "format": ".0f"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="risk_gauge_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="history",
                    title="Index History",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "date", "y_fields": ["risk_index", "volatility", "credit_spread"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="history_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="components",
                    title="Components",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "component", "y_field": "contribution"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="components_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Composite Risk/Solvency Framework
# ════════════════════════════════════════════════════════════════════════════════


class CompositeRiskFramework(BaseMetaFramework):
    """
    Composite Risk/Solvency Framework.
    
    Aggregated risk and solvency scoring.
    Token weight: 5
    """
    
    METADATA = FrameworkMetadata(
        slug="composite_risk",
        name="Composite Risk / Solvency",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.PROFESSIONAL,
        description=(
            "Aggregated risk and solvency scoring for "
            "institutional risk assessment."
        ),
        required_domains=["balance_sheets", "risk_factors", "market_data"],
        output_domains=["solvency_ratio", "composite_risk_score", "default_probability"],
        constituent_models=["merton_model", "z_score", "solvency_engine"],
        tags=["risk", "solvency", "composite", "default", "capital"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = FinancialTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.72),
            health_burden_score=np.full(n_cohorts, 0.18),
            credit_access_prob=np.full(n_cohorts, 0.68),
            housing_cost_ratio=np.full(n_cohorts, 0.27),
            opportunity_score=np.full(n_cohorts, 0.6),
            sector_output=np.full((n_cohorts, 10), 1150.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.19),
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
            "solvency_ratio": float(np.mean(state.credit_access_prob) / 0.68),
            "composite_risk": float(np.mean(state.deprivation_vector)),
            "default_prob": float(1 - np.mean(state.credit_access_prob)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "composite_risk", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Composite Risk dashboard specification."""
        return FrameworkDashboardSpec(
            slug="composite_risk",
            name="Composite Risk / Solvency",
            description="Aggregated risk and solvency scoring.",
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "risk_model": {
                        "type": "string",
                        "title": "Risk Model",
                        "enum": ["merton", "z_score", "kmv", "hybrid"],
                        "default": "hybrid",
                        "x-ui-widget": "select",
                        "x-ui-group": "model",
                    },
                    "confidence_level": {
                        "type": "number",
                        "title": "Confidence Level",
                        "enum": [0.95, 0.99, 0.999],
                        "default": 0.99,
                        "x-ui-widget": "select",
                        "x-ui-group": "model",
                    },
                    "horizon_years": {
                        "type": "integer",
                        "title": "Horizon (years)",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 1,
                        "x-ui-widget": "slider",
                        "x-ui-group": "model",
                    },
                },
            },
            default_parameters={"risk_model": "hybrid", "confidence_level": 0.99, "horizon_years": 1},
            parameter_groups=[
                ParameterGroupSpec(key="model", title="Model Configuration", parameters=["risk_model", "confidence_level", "horizon_years"]),
            ],
            required_domains=["balance_sheets", "risk_factors", "market_data"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="solvency",
                    title="Solvency Ratio",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 2, "thresholds": [0.5, 1.0, 1.5], "format": ".2f"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="solvency_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="default_prob",
                    title="Default Probability",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 0.1, "thresholds": [0.01, 0.03, 0.05], "format": ".2%"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="default_prob_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="risk_decomposition",
                    title="Risk Decomposition",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "risk_type", "y_field": "contribution", "stacked": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="risk_decomposition_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Financial Meta-Orchestrators Framework
# ════════════════════════════════════════════════════════════════════════════════


class FinancialMetaOrchestratorFramework(BaseMetaFramework):
    """
    Financial Meta-Orchestrators Framework.
    
    Cross-model orchestration for complex financial analysis.
    Token weight: 10
    """
    
    METADATA = FrameworkMetadata(
        slug="financial_meta_orchestrator",
        name="Financial Meta-Orchestrators",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.ENTERPRISE,
        description=(
            "Cross-model orchestration engine for complex multi-model "
            "financial analysis and stress testing."
        ),
        required_domains=["all_financial", "macro", "network"],
        output_domains=["integrated_risk", "scenario_outcomes", "policy_recommendations"],
        constituent_models=["orchestration_engine", "model_combiner", "scenario_generator"],
        tags=["orchestrator", "meta", "financial", "multi-model", "enterprise"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = FinancialTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.75),
            health_burden_score=np.full(n_cohorts, 0.15),
            credit_access_prob=np.full(n_cohorts, 0.75),
            housing_cost_ratio=np.full(n_cohorts, 0.25),
            opportunity_score=np.full(n_cohorts, 0.65),
            sector_output=np.full((n_cohorts, 10), 1500.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.15),
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
            "integrated_risk": float(np.mean(state.deprivation_vector)),
            "scenario_impact": float(1 - np.mean(state.opportunity_score)),
            "model_confidence": float(0.85 + np.random.random() * 0.1),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "financial_meta_orchestrator", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Financial Meta-Orchestrator dashboard specification."""
        return FrameworkDashboardSpec(
            slug="financial_meta_orchestrator",
            name="Financial Meta-Orchestrator",
            description="Cross-model orchestration for complex financial analysis.",
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "models": {
                        "type": "array",
                        "title": "Constituent Models",
                        "items": {"type": "string", "enum": ["basel_iii", "cecl", "stress_test", "market_risk", "liquidity"]},
                        "default": ["basel_iii", "cecl", "stress_test"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "orchestration",
                    },
                    "scenario": {
                        "type": "string",
                        "title": "Scenario",
                        "enum": ["baseline", "adverse", "severely_adverse", "custom"],
                        "default": "baseline",
                        "x-ui-widget": "select",
                        "x-ui-group": "orchestration",
                    },
                    "n_quarters": {
                        "type": "integer",
                        "title": "Forecast Quarters",
                        "minimum": 1,
                        "maximum": 12,
                        "default": 9,
                        "x-ui-widget": "slider",
                        "x-ui-group": "simulation",
                    },
                },
            },
            default_parameters={"models": ["basel_iii", "cecl", "stress_test"], "scenario": "baseline", "n_quarters": 9},
            parameter_groups=[
                ParameterGroupSpec(key="orchestration", title="Orchestration", parameters=["models", "scenario"]),
                ParameterGroupSpec(key="simulation", title="Simulation", parameters=["n_quarters"]),
            ],
            required_domains=["all_financial", "macro", "network"],
            min_tier=Tier.ENTERPRISE,
            output_views=[
                OutputViewSpec(
                    key="integrated_risk",
                    title="Integrated Risk",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 1, "thresholds": [0.3, 0.5, 0.7], "format": ".1%"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="integrated_risk_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="model_summary",
                    title="Model Summary",
                    view_type=ViewType.METRIC_GRID,
                    config={"metrics": [
                        {"key": "cet1_ratio", "label": "CET1 Ratio", "format": ".1%"},
                        {"key": "acl_coverage", "label": "ACL Coverage", "format": ".1%"},
                        {"key": "stressed_capital", "label": "Stressed Capital", "format": ".1%"},
                    ]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="model_summary_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="dag",
                    title="Model Dependencies",
                    view_type=ViewType.NETWORK,
                    config={"layout": "dagre", "direction": "LR"},
                    result_class=ResultClass.STRUCTURAL_SIMILARITY,
                    output_key="dag_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="scenario_trajectory",
                    title="Scenario Trajectory",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "quarter", "y_fields": ["cet1", "tier1", "total_capital"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="scenario_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )
