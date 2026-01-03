from __future__ import annotations
#!/usr/bin/env python3
# ════════════════════════════════════════════════════════════════════════════════
# CGE-Microsim Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Generic CGE-Microsimulation Framework.

This framework provides a flexible macro-micro linkage architecture that can be
configured for various policy analysis scenarios. Unlike SAM-CGE-Poverty (which
is specialized for poverty analysis), this framework supports:

- Configurable macro models (not just SAM-CGE)
- Flexible linkage mechanisms (top-down, bottom-up, or iterative)
- Multiple outcome metrics (not just poverty)
- Sectoral heterogeneity in household responses

Methodology:
    1. **Macro Layer**: Computable General Equilibrium model
    2. **Linkage Layer**: Maps macro shocks to micro-level changes
    3. **Micro Layer**: Household microsimulation with behavioral responses
    4. **Feedback** (optional): Aggregate micro changes back to macro

Use Cases:
    - Tax policy analysis with distributional impacts
    - Trade liberalization with labor market effects
    - Climate policy with household energy consumption
    - Healthcare reform with insurance coverage changes

References:
    - Bourguignon, F., et al. (2008). "Evaluating the poverty impact of
      economic policies: Some analytical challenges."
    - Savard, L. (2003). "Poverty and income distribution in a CGE-household
      micro-simulation model: Top-down/bottom up approach."
"""

import logging
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from krl_frameworks.core.base import BaseMetaFramework, FrameworkMetadata, CohortStateVector
from krl_frameworks.core.config import FrameworkConfig
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    ParameterGroupSpec,
    OutputViewSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.core.data_bundle import DataBundle, DataDomain
from krl_frameworks.core.registry import Tier, VerticalLayer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CGEMicrosimConfig:
    """Configuration for generic CGE-Microsimulation Framework."""

    # CGE configuration (simplified, no full SAM-CGE)
    n_sectors: int = 10
    n_cohorts: int = 100  # Number of household cohorts/groups

    # Linkage configuration
    linkage_type: Literal["top_down", "bottom_up", "iterative"] = "top_down"
    max_linkage_iterations: int = 3  # For iterative linkage

    # Behavioral parameters
    labor_supply_elasticity: float = 0.5  # Household labor supply response
    consumption_elasticity: float = 0.8  # Consumption response to income changes

    # Convergence
    convergence_tolerance: float = 1e-3
    max_iterations: int = 50


class CGEMicrosimFramework(BaseMetaFramework):
    """
    Generic CGE-Microsimulation Framework.

    This framework provides a flexible architecture for linking macro CGE models
    with household microsimulation. It supports configurable linkage mechanisms
    and can be adapted for various policy analysis scenarios.

    Attributes:
        config: CGEMicrosimConfig instance.
    """

    METADATA = FrameworkMetadata(
        slug="cge_microsim",
        name="CGE-Microsim Framework",
        version="1.0.0",
        description=(
            "Generic Computable General Equilibrium with Microsimulation linkage. "
            "Provides flexible macro-micro modeling for policy analysis with "
            "distributional impacts across households and sectors."
        ),
        tier=Tier.ENTERPRISE,  # Generic framework = high tier
        layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
        required_domains=[
            DataDomain.ECONOMIC.value,
            DataDomain.SECTORS.value,
            DataDomain.DEMOGRAPHIC.value,
            DataDomain.LABOR.value,
        ],
        tags=[
            "cge",
            "microsimulation",
            "macro-micro-linkage",
            "distributional-analysis",
            "policy-evaluation",
        ],
    )

    def __init__(self, config: CGEMicrosimConfig | None = None):
        """
        Initialize CGE-Microsim framework.

        Args:
            config: Framework configuration.
        """
        super().__init__()
        self.config = config or CGEMicrosimConfig()

        # Household cohort data (initialized in _compute_initial_state)
        self._cohort_incomes: np.ndarray | None = None
        self._cohort_consumption: np.ndarray | None = None
        self._cohort_labor_supply: np.ndarray | None = None
        self._cohort_sector_shares: np.ndarray | None = None  # (n_cohorts, n_sectors)

    def _compute_initial_state(
        self, data: DataBundle
    ) -> CohortStateVector:
        """
        Compute initial CGE-Microsim state.

        Args:
            data: DataBundle with economic, sectors, demographic, labor domains.
            config: Framework configuration.

        Returns:
            Initial CohortStateVector.
        """
        n_sectors = self.config.n_sectors
        n_cohorts = self.config.n_cohorts

        # 1. Extract macro economic data
        economic_df = data.get_dataframe(DataDomain.ECONOMIC.value)
        sectors_df = data.get_dataframe(DataDomain.SECTORS.value)

        if economic_df is not None and "gdp" in economic_df["indicator"].values:
            base_gdp = float(economic_df[economic_df["indicator"] == "gdp"]["value"].iloc[0])
        else:
            base_gdp = 100.0  # Default

        # 2. Initialize sector outputs (simple equal distribution)
        sector_outputs = np.ones(n_sectors) * (base_gdp / n_sectors)

        # 3. Extract household cohort data
        demographic_df = data.get_dataframe(DataDomain.DEMOGRAPHIC.value)

        if demographic_df is not None and "household_income" in demographic_df.columns:
            # Group households into cohorts
            self._cohort_incomes = self._create_cohorts_from_microdata(
                demographic_df["household_income"].values, n_cohorts
            )
        else:
            # Generate synthetic cohorts (lognormal distribution)
            self._cohort_incomes = self._generate_synthetic_cohorts(n_cohorts, base_gdp * 0.6)

        # 4. Initialize cohort consumption and labor supply
        self._cohort_consumption = self._cohort_incomes * 0.7  # 70% consumption rate
        self._cohort_labor_supply = np.ones(n_cohorts) * 0.4  # 40% time working (0-1 scale)

        # 5. Initialize cohort-sector linkage (which sectors each cohort participates in)
        self._cohort_sector_shares = self._initialize_cohort_sectors(n_cohorts, n_sectors)

        # 6. Aggregate microsim metrics
        avg_income = self._cohort_incomes.mean()
        income_gini = self._calculate_gini(self._cohort_incomes)

        # 7. Construct state vector
        # Use sector_output for macro outputs, deprivation_vector for micro aggregates
        state = CohortStateVector(
            sector_output=sector_outputs,
            health_burden_score=np.ones(n_sectors) * 0.05,  # 5% unemployment
            opportunity_score=np.ones(n_sectors),  # Prices (normalized to 1)
            credit_access_prob=sector_outputs * 0.3,  # Capital stock
            employment_prob=np.ones(n_sectors) / n_sectors,  # Equal labor shares
            housing_cost_ratio=np.ones(n_sectors) * 0.2,  # Government share
            deprivation_vector=np.array([avg_income, income_gini]),  # Micro aggregates
        )

        logger.info(
            f"CGE-Microsim initial state: {n_sectors} sectors, {n_cohorts} cohorts, "
            f"GDP={base_gdp:.2f}, Gini={income_gini:.3f}"
        )

        return state

    def _transition(
        self, state: CohortStateVector, step: int
    ) -> CohortStateVector:
        """
        Transition function with macro-micro linkage.

        Args:
            state: Current state.
            step: Simulation step.
            config: Framework configuration.

        Returns:
            New state after macro-micro linkage.
        """
        n_sectors = len(state.sector_output)

        # 1. Macro simulation (simplified CGE)
        macro_state = self._simulate_macro_step(state, step)

        # 2. Extract macro shocks
        wage_shock = macro_state.opportunity_score.mean() / (state.opportunity_score.mean() + 1e-8)
        output_shock = macro_state.sector_output.sum() / (state.sector_output.sum() + 1e-8)

        # 3. Micro simulation with macro shocks (linkage)
        if self.config.linkage_type == "top_down":
            micro_state = self._top_down_linkage(wage_shock, output_shock)
        elif self.config.linkage_type == "bottom_up":
            micro_state = self._bottom_up_linkage(macro_state)
        else:  # iterative
            micro_state = self._iterative_linkage(macro_state, wage_shock, output_shock)

        # 4. Update state vector with new micro aggregates
        avg_income = self._cohort_incomes.mean()
        income_gini = self._calculate_gini(self._cohort_incomes)

        new_state = CohortStateVector(
            sector_output=macro_state.sector_output,
            health_burden_score=macro_state.health_burden_score,
            opportunity_score=macro_state.opportunity_score,
            credit_access_prob=macro_state.credit_access_prob,
            employment_prob=macro_state.employment_prob,
            housing_cost_ratio=macro_state.housing_cost_ratio,
            deprivation_vector=np.array([avg_income, income_gini]),
        )

        return new_state

    def _compute_metrics(self, state: CohortStateVector) -> dict[str, Any]:
        """
        Compute CGE-Microsim metrics.

        Args:
            state: Current state.

        Returns:
            Dictionary of macro + micro metrics.
        """
        # Macro metrics
        gdp = state.sector_output.sum()
        unemployment_rate = state.health_burden_score.mean()
        avg_price = state.opportunity_score.mean()

        # Micro metrics
        avg_income = state.deprivation_vector[0]
        gini = state.deprivation_vector[1]

        # Cohort distribution metrics
        income_deciles = self._calculate_deciles(self._cohort_incomes)
        consumption_total = self._cohort_consumption.sum()
        labor_supply_total = self._cohort_labor_supply.sum()

        metrics = {
            # Macro
            "gdp": float(gdp),
            "sector_outputs": state.sector_output.tolist(),
            "unemployment_rate": float(unemployment_rate),
            "average_price": float(avg_price),
            # Micro
            "average_cohort_income": float(avg_income),
            "gini_coefficient": float(gini),
            "total_consumption": float(consumption_total),
            "total_labor_supply": float(labor_supply_total),
            "income_deciles": income_deciles.tolist(),
            # Linkage
            "cohort_count": len(self._cohort_incomes),
            "sector_count": len(state.sector_output),
        }

        return metrics

    # ═══════════════════════════════════════════════════════════════════════════
    # Macro Simulation (Simplified CGE)
    # ═══════════════════════════════════════════════════════════════════════════

    def _simulate_macro_step(
        self, state: CohortStateVector, step: int
    ) -> CohortStateVector:
        """
        Simplified macro CGE simulation.

        Args:
            state: Current state.
            step: Time step.

        Returns:
            New macro state.
        """
        # Productivity growth
        productivity_growth = 1.01 ** step  # 1% annual growth

        # Update sector outputs
        new_outputs = state.sector_output * productivity_growth

        # Update prices (supply-demand balance, simplified)
        price_adjustment = 1.0 + 0.01 * np.random.randn(len(state.sector_output))
        new_prices = state.opportunity_score * price_adjustment
        new_prices = new_prices / (new_prices[0] + 1e-8)  # Numeraire normalization

        # Capital accumulation
        new_capital = state.credit_access_prob * 1.05  # 5% growth

        return CohortStateVector(
            sector_output=new_outputs,
            health_burden_score=state.health_burden_score,  # Fixed
            opportunity_score=new_prices,
            credit_access_prob=new_capital,
            employment_prob=state.employment_prob,  # Fixed shares
            housing_cost_ratio=state.housing_cost_ratio,
            deprivation_vector=state.deprivation_vector,  # Updated separately
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Micro Simulation Linkage Mechanisms
    # ═══════════════════════════════════════════════════════════════════════════

    def _top_down_linkage(self, wage_shock: float, output_shock: float) -> None:
        """
        Top-down linkage: Macro shocks → Micro income changes (no feedback).

        Args:
            wage_shock: Wage rate multiplier from macro.
            output_shock: Output multiplier from macro.
        """
        # Update cohort incomes based on wage shock (labor income dominates)
        labor_income_change = (wage_shock ** self.config.labor_supply_elasticity) - 1
        capital_income_change = (output_shock - 1) * 0.5  # Simplified

        # Assume 70% labor, 30% capital income
        income_multiplier = 1 + 0.7 * labor_income_change + 0.3 * capital_income_change

        self._cohort_incomes = self._cohort_incomes * income_multiplier

        # Update consumption (with elasticity)
        consumption_change = income_multiplier ** self.config.consumption_elasticity
        self._cohort_consumption = self._cohort_consumption * consumption_change

    def _bottom_up_linkage(self, macro_state: CohortStateVector) -> None:
        """
        Bottom-up linkage: Micro behavior → Macro aggregates (updates macro).

        Args:
            macro_state: Current macro state (will be modified).
        """
        # Aggregate micro consumption to macro demand
        total_consumption = self._cohort_consumption.sum()

        # Distribute consumption across sectors based on cohort-sector shares
        sector_demand = np.zeros(len(macro_state.sector_output))
        for cohort_idx in range(len(self._cohort_incomes)):
            sector_demand += (
                self._cohort_consumption[cohort_idx] *
                self._cohort_sector_shares[cohort_idx]
            )

        # Update macro outputs based on micro consumption
        # (In full model, this would feed into market clearing)
        # Here, simplified: outputs adjust to meet demand
        macro_state.sector_output[:] = sector_demand * 1.2  # Simplified multiplier

    def _iterative_linkage(
        self, macro_state: CohortStateVector, wage_shock: float, output_shock: float
    ) -> None:
        """
        Iterative linkage: Alternate top-down and bottom-up until convergence.

        Args:
            macro_state: Macro state.
            wage_shock: Initial wage shock.
            output_shock: Initial output shock.
        """
        for iteration in range(self.config.max_linkage_iterations):
            # Top-down: Macro → Micro
            prev_avg_income = self._cohort_incomes.mean()
            self._top_down_linkage(wage_shock, output_shock)

            # Bottom-up: Micro → Macro
            self._bottom_up_linkage(macro_state)

            # Check convergence
            income_change = abs(self._cohort_incomes.mean() - prev_avg_income) / prev_avg_income
            if income_change < self.config.convergence_tolerance:
                logger.debug(f"Iterative linkage converged at iteration {iteration+1}")
                break

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _create_cohorts_from_microdata(
        self, microdata: np.ndarray, n_cohorts: int
    ) -> np.ndarray:
        """
        Group microdata into cohorts by income percentiles.

        Args:
            microdata: Household-level data.
            n_cohorts: Number of cohorts to create.

        Returns:
            Array of cohort averages.
        """
        sorted_data = np.sort(microdata)
        cohort_size = len(sorted_data) // n_cohorts

        cohorts = []
        for i in range(n_cohorts):
            start_idx = i * cohort_size
            end_idx = start_idx + cohort_size if i < n_cohorts - 1 else len(sorted_data)
            cohorts.append(sorted_data[start_idx:end_idx].mean())

        return np.array(cohorts)

    def _generate_synthetic_cohorts(self, n_cohorts: int, total_income: float) -> np.ndarray:
        """
        Generate synthetic cohort income distribution.

        Args:
            n_cohorts: Number of cohorts.
            total_income: Total income to distribute.

        Returns:
            Array of cohort incomes.
        """
        # Lognormal distribution with Gini ~0.35
        incomes = np.random.lognormal(0, 0.8, n_cohorts)
        incomes = incomes * (total_income / incomes.sum())
        return incomes

    def _initialize_cohort_sectors(self, n_cohorts: int, n_sectors: int) -> np.ndarray:
        """
        Initialize cohort-sector participation shares.

        Args:
            n_cohorts: Number of cohorts.
            n_sectors: Number of sectors.

        Returns:
            Matrix (n_cohorts, n_sectors) of consumption shares.
        """
        # Random shares, normalized to sum to 1 per cohort
        shares = np.random.rand(n_cohorts, n_sectors)
        return shares / shares.sum(axis=1, keepdims=True)

    def _calculate_gini(self, incomes: np.ndarray) -> float:
        """Calculate Gini coefficient."""
        sorted_incomes = np.sort(incomes)
        n = len(incomes)
        cumsum = np.cumsum(sorted_incomes)
        return (2 * np.sum((np.arange(1, n + 1)) * sorted_incomes)) / (n * cumsum[-1]) - (n + 1) / n

    def _calculate_deciles(self, incomes: np.ndarray) -> np.ndarray:
        """Calculate average income by decile."""
        sorted_incomes = np.sort(incomes)
        decile_size = len(sorted_incomes) // 10
        deciles = []
        for i in range(10):
            start = i * decile_size
            end = start + decile_size if i < 9 else len(sorted_incomes)
            deciles.append(sorted_incomes[start:end].mean())
        return np.array(deciles)

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return CGE-Microsim dashboard specification.

        Parameters extracted from CGEMicrosimConfig dataclass (lines 54-72).
        All defaults are actual framework defaults, not placeholders.
        """
        return FrameworkDashboardSpec(
            slug="cge_microsim",
            name="CGE-Microsimulation Framework",
            description=(
                "Generic Computable General Equilibrium model with household microsimulation linkage. "
                "Analyze macro policy shocks with distributional impacts across household cohorts."
            ),
            layer="socioeconomic",
            min_tier=Tier.ENTERPRISE,
            parameters_schema={
                "type": "object",
                "properties": {
                    # Model Structure
                    "n_sectors": {
                        "type": "integer",
                        "title": "Number of Economic Sectors",
                        "description": "Sectors in the CGE model",
                        "minimum": 3,
                        "maximum": 50,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "structure",
                        "x-ui-order": 1,
                    },
                    "n_cohorts": {
                        "type": "integer",
                        "title": "Number of Household Cohorts",
                        "description": "Household groups for microsimulation",
                        "minimum": 10,
                        "maximum": 500,
                        "default": 100,
                        "x-ui-widget": "slider",
                        "x-ui-step": 10,
                        "x-ui-group": "structure",
                        "x-ui-order": 2,
                    },
                    # Linkage Mechanism
                    "linkage_type": {
                        "type": "string",
                        "title": "Macro-Micro Linkage Type",
                        "description": "How macro and micro layers interact",
                        "enum": ["top_down", "bottom_up", "iterative"],
                        "default": "top_down",
                        "x-ui-widget": "select",
                        "x-ui-group": "linkage",
                        "x-ui-order": 1,
                        "x-ui-help": "top_down: Macro→Micro only | bottom_up: Micro→Macro only | iterative: Both directions",
                    },
                    "max_linkage_iterations": {
                        "type": "integer",
                        "title": "Max Linkage Iterations",
                        "description": "Maximum iterations for iterative linkage",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 3,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "linkage",
                        "x-ui-order": 2,
                    },
                    # Behavioral Parameters
                    "labor_supply_elasticity": {
                        "type": "number",
                        "title": "Labor Supply Elasticity",
                        "description": "Household labor supply response to wage changes",
                        "minimum": 0,
                        "maximum": 2.0,
                        "default": 0.5,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "behavioral",
                        "x-ui-order": 1,
                    },
                    "consumption_elasticity": {
                        "type": "number",
                        "title": "Consumption Elasticity",
                        "description": "Consumption response to income changes",
                        "minimum": 0,
                        "maximum": 1.5,
                        "default": 0.8,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "behavioral",
                        "x-ui-order": 2,
                    },
                    # Convergence
                    "convergence_tolerance": {
                        "type": "number",
                        "title": "Convergence Tolerance",
                        "description": "Threshold for equilibrium convergence",
                        "minimum": 1e-6,
                        "maximum": 1e-1,
                        "default": 1e-3,
                        "x-ui-widget": "number",
                        "x-ui-format": "scientific",
                        "x-ui-group": "advanced",
                        "x-ui-order": 1,
                    },
                    "max_iterations": {
                        "type": "integer",
                        "title": "Max Iterations",
                        "description": "Maximum solver iterations",
                        "minimum": 10,
                        "maximum": 200,
                        "default": 50,
                        "x-ui-widget": "slider",
                        "x-ui-step": 10,
                        "x-ui-group": "advanced",
                        "x-ui-order": 2,
                    },
                },
                "required": [],
            },
            default_parameters={
                "n_sectors": 10,
                "n_cohorts": 100,
                "linkage_type": "top_down",
                "max_linkage_iterations": 3,
                "labor_supply_elasticity": 0.5,
                "consumption_elasticity": 0.8,
                "convergence_tolerance": 1e-3,
                "max_iterations": 50,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="structure",
                    title="Model Structure",
                    description="Number of sectors and household cohorts",
                    collapsed_by_default=False,
                    parameters=["n_sectors", "n_cohorts"],
                ),
                ParameterGroupSpec(
                    key="linkage",
                    title="Macro-Micro Linkage",
                    description="How macro and micro layers interact",
                    collapsed_by_default=False,
                    parameters=["linkage_type", "max_linkage_iterations"],
                ),
                ParameterGroupSpec(
                    key="behavioral",
                    title="Behavioral Parameters",
                    description="Household response elasticities",
                    collapsed_by_default=False,
                    parameters=["labor_supply_elasticity", "consumption_elasticity"],
                ),
                ParameterGroupSpec(
                    key="advanced",
                    title="Advanced Settings",
                    description="Solver convergence parameters",
                    collapsed_by_default=True,
                    parameters=["convergence_tolerance", "max_iterations"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="gdp_trajectory",
                    title="GDP Trajectory",
                    view_type=ViewType.TIMESERIES,
                    description="Total GDP over simulation",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="gdp_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="sector_outputs",
                    title="Sectoral Output",
                    view_type=ViewType.BAR_CHART,
                    description="Output by economic sector",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="sector_outputs_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="gini_trajectory",
                    title="Inequality (Gini)",
                    view_type=ViewType.TIMESERIES,
                    description="Gini coefficient over time",
                result_class=ResultClass.SCALAR_INDEX,
                output_key="gini_trajectory_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="income_distribution",
                    title="Income Distribution (Deciles)",
                    view_type=ViewType.BAR_CHART,
                    description="Average income by decile",
                result_class=ResultClass.DOMAIN_DECOMPOSITION,
                output_key="income_distribution_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="linkage_metrics",
                    title="Linkage Convergence",
                    view_type=ViewType.TABLE,
                    description="Macro-micro linkage diagnostics",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="linkage_metrics_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
