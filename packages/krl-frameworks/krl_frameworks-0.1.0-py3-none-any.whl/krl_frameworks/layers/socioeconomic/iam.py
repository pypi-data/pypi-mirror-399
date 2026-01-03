# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Integrated Assessment Models (IAMs)
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Integrated Assessment Models (IAMs) Framework.

IAMs couple climate, economic, and social systems to project
long-term scenarios. Key models include:

- DICE: Dynamic Integrated Climate-Economy Model
- GCAM: Global Change Assessment Model
- FUND: Climate Framework for Uncertainty, Negotiation, and Distribution
- PAGE: Policy Analysis of the Greenhouse Effect

Token Weight: 5 per run
Tier: FREE (Community) / PRO / ENTERPRISE

References:
    - Nordhaus, W. (2017). "Revisiting the social cost of carbon"
    - Calvin et al. (2019). "GCAM v5.1: model overview and documentation"
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

__all__ = ["IAMFramework", "IAMTransition"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# IAM Configuration
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class IAMConfig:
    """Configuration for IAM computation."""
    
    model_type: str = "dice"  # dice, gcam, fund, page
    time_horizon: int = 100  # years
    discount_rate: float = 0.03
    climate_sensitivity: float = 3.0  # degrees C per doubling CO2
    damage_function: str = "quadratic"  # quadratic, cubic
    
    # Token weight for monetization
    token_weight: int = 5


# ════════════════════════════════════════════════════════════════════════════════
# IAM Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class IAMTransition(TransitionFunction):
    """Transition function for IAM cohort state evolution."""
    
    name = "IAMTransition"
    
    def __init__(
        self,
        warming_rate: float = 0.02,  # degrees per period
        damage_coef: float = 0.003,  # quadratic damage coefficient
    ):
        self.warming_rate = warming_rate
        self.damage_coef = damage_coef
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply IAM transition with climate damages."""
        params = params or {}
        
        # Temperature anomaly increases
        temp_change = t * params.get("warming_rate", self.warming_rate)
        
        # Economic damage (quadratic in temperature)
        damage = params.get("damage_coef", self.damage_coef) * temp_change ** 2
        
        # Apply damage to sector output
        new_sector_output = state.sector_output * (1 - damage)
        
        # Health burden increases with warming
        new_health_burden = np.clip(
            state.health_burden_score + damage * 0.1, 0, 1
        )
        
        return CohortStateVector(
            employment_prob=state.employment_prob * (1 - damage * 0.5),
            health_burden_score=new_health_burden,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=state.opportunity_score * (1 - damage * 0.2),
            sector_output=new_sector_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# IAM Framework
# ════════════════════════════════════════════════════════════════════════════════


class IAMFramework(BaseMetaFramework):
    """
    Integrated Assessment Models (IAMs) Framework.
    
    Implements climate-economy coupling for long-term scenario analysis.
    Supports DICE, GCAM, FUND, and PAGE model variants.
    """
    
    METADATA = FrameworkMetadata(
        slug="iam",
        name="Integrated Assessment Models (DICE/GCAM)",
        version="1.0.0",
        layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
        tier=Tier.TEAM,
        description=(
            "Climate-economy integrated assessment models for long-term "
            "projections of climate impacts on socioeconomic systems."
        ),
        required_domains=["climate", "economic", "emissions"],
        output_domains=["temperature_path", "damage_path", "welfare"],
        constituent_models=["dice", "gcam", "fund", "page"],
        tags=["climate", "iam", "dice", "gcam", "socioeconomic"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        config: Optional[IAMConfig] = None,
    ):
        super().__init__()
        self.iam_config = config or IAMConfig()
        self._transition_fn = IAMTransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return IAM framework metadata."""
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from economic/climate data."""
        # Infer cohort size from data bundle (like HDI/SPI frameworks)
        n_cohorts = 100  # Default
        for domain in ["climate", "economic", "energy", "environment"]:
            if bundle.has_domain(domain):
                data = bundle.get(domain)
                n_cohorts = len(data.data)
                break

        n_sectors = 10

        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.7),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.full(n_cohorts, 0.6),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.full(n_cohorts, 0.5),
            sector_output=np.full((n_cohorts, n_sectors), 1000.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.2),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Execute IAM transition."""
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """Compute IAM metrics from final state."""
        return {
            "model_type": self.iam_config.model_type,
            "avg_health_burden": float(np.mean(state.health_burden_score)),
            "avg_opportunity": float(np.mean(state.opportunity_score)),
            "total_sector_output": float(np.sum(state.sector_output)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        """Compute IAM outputs from trajectory."""
        return {
            "model_type": self.iam_config.model_type,
            "time_horizon": self.iam_config.time_horizon,
            "n_periods": trajectory.n_periods,
            "final_damage_estimate": 0.05,  # Placeholder
            "social_cost_carbon": 50.0,  # $/ton CO2 placeholder
        }

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return IAM dashboard specification.

        IAM is a TEAM tier framework for climate-economy integrated
        assessment modeling (DICE, GCAM, FUND, PAGE).
        """
        return FrameworkDashboardSpec(
            slug="iam",
            name="Integrated Assessment Models (IAM)",
            description=(
                "Climate-economy integrated assessment models (DICE/GCAM) "
                "for long-term projections of climate impacts on socioeconomic "
                "systems. Couples atmospheric temperature, carbon cycle, economic "
                "damages, and mitigation policies."
            ),
            layer="socioeconomic",
            parameters_schema={
                "type": "object",
                "properties": {
                    # Model Selection
                    "model_type": {
                        "type": "string",
                        "title": "IAM Model Type",
                        "description": "Select integrated assessment model variant",
                        "enum": ["dice", "gcam", "fund", "page"],
                        "default": "dice",
                        "x-ui-widget": "select",
                        "x-ui-group": "model",
                        "x-ui-order": 1,
                        "x-ui-help": "DICE: Dynamic Integrated Climate-Economy (Nordhaus); GCAM: Global Change Assessment Model; FUND: Climate Framework; PAGE: Policy Analysis of Greenhouse Effect"
                    },
                    "time_horizon": {
                        "type": "integer",
                        "title": "Time Horizon",
                        "description": "Projection horizon (years)",
                        "minimum": 25,
                        "maximum": 200,
                        "default": 100,
                        "x-ui-widget": "slider",
                        "x-ui-step": 25,
                        "x-ui-unit": "years",
                        "x-ui-group": "model",
                        "x-ui-order": 2,
                    },
                    "discount_rate": {
                        "type": "number",
                        "title": "Social Discount Rate",
                        "description": "Annual discount rate for welfare calculations",
                        "minimum": 0,
                        "maximum": 0.10,
                        "default": 0.03,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-format": ".1%",
                        "x-ui-group": "model",
                        "x-ui-order": 3,
                        "x-ui-help": "Stern Review uses 1.4%, Nordhaus uses 3-4%"
                    },
                    # Climate Parameters
                    "climate_sensitivity": {
                        "type": "number",
                        "title": "Climate Sensitivity",
                        "description": "Equilibrium temperature increase for 2x CO2 (°C)",
                        "minimum": 1.5,
                        "maximum": 6.0,
                        "default": 3.0,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.5,
                        "x-ui-unit": "°C",
                        "x-ui-group": "climate",
                        "x-ui-order": 1,
                        "x-ui-help": "IPCC AR6 likely range: 2.5-4.0°C"
                    },
                    "warming_rate": {
                        "type": "number",
                        "title": "Warming Rate",
                        "description": "Temperature increase per period",
                        "minimum": 0,
                        "maximum": 0.1,
                        "default": 0.02,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-format": ".3f",
                        "x-ui-unit": "°C/period",
                        "x-ui-group": "climate",
                        "x-ui-order": 2,
                    },
                    # Economic Damage
                    "damage_function": {
                        "type": "string",
                        "title": "Damage Function",
                        "description": "Economic damage functional form",
                        "enum": ["quadratic", "cubic", "weitzman"],
                        "default": "quadratic",
                        "x-ui-widget": "select",
                        "x-ui-group": "economic",
                        "x-ui-order": 1,
                        "x-ui-help": "Quadratic: Nordhaus DICE; Cubic: higher tail risk; Weitzman: fat-tailed uncertainty"
                    },
                    "damage_coef": {
                        "type": "number",
                        "title": "Damage Coefficient",
                        "description": "Coefficient for damage function",
                        "minimum": 0,
                        "maximum": 0.01,
                        "default": 0.003,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.0005,
                        "x-ui-format": ".4f",
                        "x-ui-group": "economic",
                        "x-ui-order": 2,
                    },
                    # Simulation
                    "n_periods": {
                        "type": "integer",
                        "title": "Simulation Periods",
                        "description": "Number of periods to simulate",
                        "minimum": 10,
                        "maximum": 100,
                        "default": 50,
                        "x-ui-widget": "slider",
                        "x-ui-step": 10,
                        "x-ui-unit": "periods",
                        "x-ui-group": "simulation",
                        "x-ui-order": 1,
                    },
                },
                "required": [],
            },
            default_parameters={
                "model_type": "dice",
                "time_horizon": 100,
                "discount_rate": 0.03,
                "climate_sensitivity": 3.0,
                "warming_rate": 0.02,
                "damage_function": "quadratic",
                "damage_coef": 0.003,
                "n_periods": 50,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="model",
                    title="Model Configuration",
                    description="IAM model selection and general settings",
                    collapsed_by_default=False,
                    parameters=["model_type", "time_horizon", "discount_rate"],
                ),
                ParameterGroupSpec(
                    key="climate",
                    title="Climate Parameters",
                    description="Temperature dynamics and climate sensitivity",
                    collapsed_by_default=False,
                    parameters=["climate_sensitivity", "warming_rate"],
                ),
                ParameterGroupSpec(
                    key="economic",
                    title="Economic Damage",
                    description="Damage function specification",
                    collapsed_by_default=False,
                    parameters=["damage_function", "damage_coef"],
                ),
                ParameterGroupSpec(
                    key="simulation",
                    title="Simulation Settings",
                    description="Projection periods and execution",
                    collapsed_by_default=True,
                    parameters=["n_periods"],
                ),
            ],
            required_domains=["climate", "economic", "emissions"],
            min_tier=Tier.TEAM,
            output_views=[
                # Temperature Trajectory
                OutputViewSpec(
                    key="temperature_path",
                    title="Temperature Trajectory",
                    view_type=ViewType.LINE_CHART,
                    description="Global mean temperature anomaly over time",
                    config={
                        "x_field": "period",
                        "y_field": "temperature_anomaly",
                        "x_label": "Year",
                        "y_label": "Temperature Anomaly (°C)",
                        "color": "#ef4444",
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="temperature_path_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # Economic Damage
                OutputViewSpec(
                    key="damage_path",
                    title="Economic Damage",
                    view_type=ViewType.LINE_CHART,
                    description="Climate damage as % of GDP",
                    config={
                        "x_field": "period",
                        "y_field": "damage_pct_gdp",
                        "x_label": "Year",
                        "y_label": "Damage (% GDP)",
                        "color": "#f59e0b",
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="damage_path_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.TIME_SERIES
                ),
                # Social Cost of Carbon
                OutputViewSpec(
                    key="scc",
                    title="Social Cost of Carbon",
                    view_type=ViewType.METRIC_GRID,
                    description="Present value of marginal ton CO2",
                    config={
                        "metrics": [
                            {"key": "social_cost_carbon", "label": "SCC ($/ton CO2)", "format": ".2f"},
                            {"key": "final_damage_estimate", "label": "Final Damage (% GDP)", "format": ".2%"},
                        ]
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="scc_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # Emissions Trajectory
                OutputViewSpec(
                    key="emissions",
                    title="Emissions Path",
                    view_type=ViewType.LINE_CHART,
                    description="CO2 emissions over time",
                    config={
                        "x_field": "period",
                        "y_field": "co2_emissions",
                        "x_label": "Year",
                        "y_label": "CO2 Emissions (GtC)",
                    },
                result_class=ResultClass.SCALAR_INDEX,
                output_key="emissions_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                # Welfare
                OutputViewSpec(
                    key="welfare",
                    title="Welfare Analysis",
                    view_type=ViewType.BAR_CHART,
                    description="Discounted welfare by scenario",
                    config={
                        "x_field": "scenario",
                        "y_field": "welfare",
                        "color_field": "scenario",
                    },
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="welfare_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                # Results Table
                OutputViewSpec(
                    key="summary_table",
                    title="Summary",
                    view_type=ViewType.TABLE,
                    description="Key results summary",
                    config={
                        "columns": [
                            {"key": "model_type", "label": "Model"},
                            {"key": "time_horizon", "label": "Time Horizon (years)"},
                            {"key": "social_cost_carbon", "label": "SCC ($/ton)", "format": ".2f"},
                            {"key": "final_damage_estimate", "label": "Final Damage (%)", "format": ".2%"},
                        ]
                    },
                result_class=ResultClass.CONFIDENCE_PROVENANCE,
                output_key="summary_table_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )
