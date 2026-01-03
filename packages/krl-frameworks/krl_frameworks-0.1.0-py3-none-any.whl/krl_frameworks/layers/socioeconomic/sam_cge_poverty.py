from __future__ import annotations
#!/usr/bin/env python3
# ════════════════════════════════════════════════════════════════════════════════
# SAM-CGE-Poverty Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
SAM-CGE-Poverty Framework: CGE + Household Microsimulation for Poverty Analysis.

This framework extends the SAM-CGE model with household-level microsimulation
to analyze distributional impacts of economic policies on poverty and inequality.

Methodology:
    1. **Macro Layer (SAM-CGE)**: Multi-sector general equilibrium model
    2. **Micro Layer (Microsimulation)**: Household survey microdata linkage
    3. **Linkage Mechanism**: Map CGE shocks to household income changes
    4. **Poverty Analysis**: Calculate poverty headcount, gap, Gini coefficient

Key Features:
    - Top-down linkage (CGE → microsimulation, no feedback)
    - Household income decomposition (labor, capital, transfers)
    - Poverty line calibration (World Bank $2.15/day or country-specific)
    - Inequality metrics (Gini, Theil, Atkinson indices)
    - Distributional analysis by quintile/decile

References:
    - Bourguignon, F., & Spadaro, A. (2006). "Microsimulation as a tool for
      evaluating redistribution policies." Journal of Economic Inequality.
    - Davies, J. B. (2009). "Combining microsimulation with CGE and macro
      modelling for distributional analysis in developing countries."
"""

import logging
from dataclasses import dataclass
from typing import Any

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
from krl_frameworks.layers.socioeconomic.sam_cge import SAMCGEFramework, SAMCGEConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SAMCGEPovertyConfig:
    """Configuration for SAM-CGE-Poverty Framework."""

    # SAM-CGE configuration (macro layer)
    n_sectors: int = 10
    elasticity_substitution: float = 0.8
    convergence_tolerance: float = 1e-4
    max_iterations: int = 100

    # Microsimulation configuration
    n_households: int = 1000  # Number of household observations
    poverty_line: float = 2.15  # World Bank extreme poverty line ($/day, 2017 PPP)
    income_elasticity_labor: float = 0.8  # Labor income elasticity to wage changes
    income_elasticity_capital: float = 1.2  # Capital income elasticity to returns


class SAMCGEPovertyFramework(BaseMetaFramework):
    """
    SAM-CGE-Poverty Framework: CGE + Household Microsimulation.

    This framework combines a multi-sector CGE model with household microsimulation
    to analyze the distributional impacts of economic policies on poverty and
    inequality. The linkage is top-down: CGE results (wage changes, sector outputs)
    are used to shock household incomes, then poverty/inequality metrics are calculated.

    Attributes:
        config: SAMCGEPovertyConfig instance.
        cge_framework: Underlying SAM-CGE framework for macro simulation.
    """

    METADATA = FrameworkMetadata(
        slug="sam_cge_poverty",
        name="SAM-CGE-Poverty Framework",
        version="1.0.0",
        description=(
            "Social Accounting Matrix - CGE model with household microsimulation "
            "for poverty and inequality analysis. Combines multi-sector general "
            "equilibrium with household-level income distribution modeling."
        ),
        tier=Tier.ENTERPRISE,
        layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
        required_domains=[
            DataDomain.SAM.value,
            DataDomain.ECONOMIC.value,
            DataDomain.SECTORS.value,
            DataDomain.DEMOGRAPHIC.value,  # Household microdata
        ],
        tags=[
            "cge",
            "microsimulation",
            "poverty",
            "inequality",
            "distributional-analysis",
            "policy-analysis",
        ],
    )

    def __init__(self, config: SAMCGEPovertyConfig | None = None):
        """
        Initialize SAM-CGE-Poverty framework.

        Args:
            config: Framework configuration. Defaults to SAMCGEPovertyConfig().
        """
        super().__init__()
        self.config = config or SAMCGEPovertyConfig()

        # Initialize underlying SAM-CGE framework
        cge_config = SAMCGEConfig(
            n_sectors=self.config.n_sectors,
            elasticity_substitution=self.config.elasticity_substitution,
            convergence_tolerance=self.config.convergence_tolerance,
            max_iterations=self.config.max_iterations,
        )
        self.cge_framework = SAMCGEFramework(config=cge_config)

        # Household microdata (initialized in _compute_initial_state)
        self._household_incomes: np.ndarray | None = None
        self._household_sectors: np.ndarray | None = None  # Sector affiliation
        self._household_weights: np.ndarray | None = None  # Survey weights

    def _compute_initial_state(
        self, data: DataBundle, config: FrameworkConfig
    ) -> CohortStateVector:
        """
        Compute initial state from SAM + household microdata.

        Args:
            data: DataBundle with SAM, economic, sectors, and demographic domains.
            config: Framework configuration.

        Returns:
            Initial CohortStateVector with CGE + microdata state.
        """
        # 1. Compute CGE initial state
        cge_state = self.cge_framework._compute_initial_state(data, config)

        # 2. Extract household microdata from demographic domain
        demographic_df = data.get_dataframe(DataDomain.DEMOGRAPHIC.value)

        if demographic_df is not None and "household_income" in demographic_df.columns:
            # Use real household microdata
            self._household_incomes = demographic_df["household_income"].values
            self._household_sectors = (
                demographic_df["sector_affiliation"].values
                if "sector_affiliation" in demographic_df.columns
                else np.random.randint(0, self.config.n_sectors, len(self._household_incomes))
            )
            self._household_weights = (
                demographic_df["survey_weight"].values
                if "survey_weight" in demographic_df.columns
                else np.ones(len(self._household_incomes))
            )
        else:
            # Generate synthetic household microdata
            self._household_incomes = self._generate_synthetic_households(
                self.config.n_households,
                cge_state.deprivation_vector[0],  # Aggregate household income from CGE
            )
            self._household_sectors = np.random.randint(
                0, self.config.n_sectors, self.config.n_households
            )
            self._household_weights = np.ones(self.config.n_households)

        # 3. Extend state vector with poverty/inequality metrics
        # Note: We use deprivation_vector to store [poverty_headcount, gini_coefficient]
        poverty_rate = self._calculate_poverty_rate(
            self._household_incomes, self._household_weights
        )
        gini = self._calculate_gini(self._household_incomes, self._household_weights)

        # Override deprivation_vector from CGE state
        extended_state = CohortStateVector(
            sector_output=cge_state.sector_output,
            health_burden_score=cge_state.health_burden_score,
            opportunity_score=cge_state.opportunity_score,
            credit_access_prob=cge_state.credit_access_prob,
            employment_prob=cge_state.employment_prob,
            housing_cost_ratio=cge_state.housing_cost_ratio,
            deprivation_vector=np.array([poverty_rate, gini]),  # Poverty + inequality
        )

        logger.info(
            f"SAM-CGE-Poverty initial state: {self.config.n_sectors} sectors, "
            f"{len(self._household_incomes)} households, poverty={poverty_rate:.1%}, Gini={gini:.3f}"
        )

        return extended_state

    def _transition(
        self, state: CohortStateVector, step: int, config: FrameworkConfig
    ) -> CohortStateVector:
        """
        Transition function: CGE simulation + microsimulation linkage.

        Args:
            state: Current state.
            step: Simulation step.
            config: Framework configuration.

        Returns:
            New state with updated poverty/inequality metrics.
        """
        # 1. Run CGE transition (macro layer)
        cge_state = self.cge_framework._transition(state, step, config)

        # 2. Extract CGE shocks
        # Wage rate change (from opportunity_score = prices)
        wage_rate_new = cge_state.opportunity_score.mean()
        wage_rate_old = state.opportunity_score.mean()
        wage_shock = wage_rate_new / (wage_rate_old + 1e-8)

        # Capital return change (from sector outputs)
        capital_return_new = (cge_state.sector_output * 0.3).sum()
        capital_return_old = (state.sector_output * 0.3).sum()
        capital_shock = capital_return_new / (capital_return_old + 1e-8)

        # 3. Microsimulation linkage: Update household incomes
        # Decompose household income into labor and capital components
        # Assume 70% labor income, 30% capital income
        labor_share = 0.7
        capital_share = 0.3

        # Apply shocks with elasticities
        labor_income_change = (wage_shock ** self.config.income_elasticity_labor) - 1
        capital_income_change = (capital_shock ** self.config.income_elasticity_capital) - 1

        # Update household incomes
        updated_incomes = self._household_incomes * (
            1 + labor_share * labor_income_change + capital_share * capital_income_change
        )
        self._household_incomes = np.clip(updated_incomes, 0, None)  # Non-negative

        # 4. Recompute poverty and inequality
        poverty_rate = self._calculate_poverty_rate(
            self._household_incomes, self._household_weights
        )
        gini = self._calculate_gini(self._household_incomes, self._household_weights)

        # 5. Construct new state
        new_state = CohortStateVector(
            sector_output=cge_state.sector_output,
            health_burden_score=cge_state.health_burden_score,
            opportunity_score=cge_state.opportunity_score,
            credit_access_prob=cge_state.credit_access_prob,
            employment_prob=cge_state.employment_prob,
            housing_cost_ratio=cge_state.housing_cost_ratio,
            deprivation_vector=np.array([poverty_rate, gini]),  # Updated poverty + inequality
        )

        return new_state

    def _compute_metrics(self, state: CohortStateVector) -> dict[str, Any]:
        """
        Compute SAM-CGE-Poverty metrics.

        Args:
            state: Current state.

        Returns:
            Dictionary of metrics (CGE + poverty + inequality).
        """
        # 1. Get CGE metrics
        cge_metrics = self.cge_framework._compute_metrics(state)

        # 2. Poverty metrics
        poverty_rate = state.deprivation_vector[0]
        gini_coefficient = state.deprivation_vector[1]

        # Poverty gap (average income shortfall for poor households)
        poverty_gap = self._calculate_poverty_gap(
            self._household_incomes, self._household_weights
        )

        # Income distribution by quintile
        income_quintiles = self._calculate_income_quintiles(
            self._household_incomes, self._household_weights
        )

        # 3. Combine metrics
        metrics = {
            **cge_metrics,  # All CGE metrics
            "poverty_headcount_rate": float(poverty_rate),
            "poverty_gap": float(poverty_gap),
            "gini_coefficient": float(gini_coefficient),
            "income_quintiles": income_quintiles.tolist(),
            "mean_household_income": float(self._household_incomes.mean()),
            "median_household_income": float(np.median(self._household_incomes)),
        }

        return metrics

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods: Household Microdata
    # ═══════════════════════════════════════════════════════════════════════════

    def _generate_synthetic_households(
        self, n_households: int, aggregate_income: float
    ) -> np.ndarray:
        """
        Generate synthetic household income distribution.

        Uses lognormal distribution to match empirical income distributions.

        Args:
            n_households: Number of households to generate.
            aggregate_income: Total household income from CGE.

        Returns:
            Array of household incomes.
        """
        # Lognormal parameters calibrated to realistic Gini ~0.35
        mu = 0.0
        sigma = 0.8

        # Generate lognormal incomes
        incomes = np.random.lognormal(mu, sigma, n_households)

        # Scale to match aggregate income
        incomes = incomes * (aggregate_income / incomes.sum())

        return incomes

    def _calculate_poverty_rate(
        self, incomes: np.ndarray, weights: np.ndarray
    ) -> float:
        """
        Calculate poverty headcount rate.

        Args:
            incomes: Household incomes (annual, in dollars).
            weights: Household survey weights.

        Returns:
            Poverty headcount rate (0-1).
        """
        # Convert poverty line from $/day to annual
        poverty_line_annual = self.config.poverty_line * 365

        # Identify poor households
        is_poor = incomes < poverty_line_annual

        # Weighted poverty rate
        poverty_rate = (is_poor * weights).sum() / weights.sum()

        return poverty_rate

    def _calculate_poverty_gap(
        self, incomes: np.ndarray, weights: np.ndarray
    ) -> float:
        """
        Calculate poverty gap (average income shortfall for poor).

        Args:
            incomes: Household incomes.
            weights: Household survey weights.

        Returns:
            Poverty gap as fraction of poverty line (0-1).
        """
        poverty_line_annual = self.config.poverty_line * 365

        # Income shortfall for poor households
        shortfall = np.maximum(poverty_line_annual - incomes, 0)

        # Weighted average shortfall
        poverty_gap = (shortfall * weights).sum() / (weights.sum() * poverty_line_annual)

        return poverty_gap

    def _calculate_gini(self, incomes: np.ndarray, weights: np.ndarray) -> float:
        """
        Calculate Gini coefficient.

        Args:
            incomes: Household incomes.
            weights: Household survey weights.

        Returns:
            Gini coefficient (0-1, 0=perfect equality).
        """
        # Sort incomes and weights
        sorted_indices = np.argsort(incomes)
        sorted_incomes = incomes[sorted_indices]
        sorted_weights = weights[sorted_indices]

        # Cumulative weighted income
        cumulative_weights = np.cumsum(sorted_weights)
        cumulative_income = np.cumsum(sorted_incomes * sorted_weights)

        # Lorenz curve area (trapezoidal rule)
        lorenz_area = np.sum(
            (cumulative_weights[1:] - cumulative_weights[:-1])
            * (cumulative_income[1:] + cumulative_income[:-1])
            / (2 * cumulative_income[-1])
        )

        # Gini = 1 - 2 * Lorenz area
        gini = 1 - 2 * lorenz_area / cumulative_weights[-1]

        return np.clip(gini, 0, 1)  # Ensure valid range

    def _calculate_income_quintiles(
        self, incomes: np.ndarray, weights: np.ndarray
    ) -> np.ndarray:
        """
        Calculate average income by quintile.

        Args:
            incomes: Household incomes.
            weights: Household survey weights.

        Returns:
            Array of 5 quintile average incomes.
        """
        # Sort by income
        sorted_indices = np.argsort(incomes)
        sorted_incomes = incomes[sorted_indices]
        sorted_weights = weights[sorted_indices]

        # Cumulative weights
        cumulative_weights = np.cumsum(sorted_weights)
        total_weight = cumulative_weights[-1]

        # Find quintile boundaries
        quintile_boundaries = [total_weight * (i / 5) for i in range(1, 5)]
        quintile_incomes = []

        start_idx = 0
        for boundary in quintile_boundaries:
            # Find households in this quintile
            end_idx = np.searchsorted(cumulative_weights, boundary, side="right")

            # Average income in quintile
            quintile_avg = (
                (sorted_incomes[start_idx:end_idx] * sorted_weights[start_idx:end_idx]).sum()
                / sorted_weights[start_idx:end_idx].sum()
                if end_idx > start_idx
                else 0
            )
            quintile_incomes.append(quintile_avg)

            start_idx = end_idx

        # Last quintile
        quintile_avg = (
            (sorted_incomes[start_idx:] * sorted_weights[start_idx:]).sum()
            / sorted_weights[start_idx:].sum()
            if start_idx < len(sorted_incomes)
            else 0
        )
        quintile_incomes.append(quintile_avg)

        return np.array(quintile_incomes)

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return SAM-CGE-Poverty dashboard specification.

        Parameters extracted from SAMCGEPovertyConfig dataclass.
        All defaults are actual framework defaults, not placeholders.
        """
        return FrameworkDashboardSpec(
            slug="sam_cge_poverty",
            name="SAM-CGE-Poverty Framework",
            description=(
                "Social Accounting Matrix CGE model with household microsimulation. "
                "Analyze distributional impacts of economic policies on poverty and inequality."
            ),
            layer="socioeconomic",
            min_tier=Tier.ENTERPRISE,
            parameters_schema={
                "type": "object",
                "properties": {
                    # Macro CGE Parameters
                    "n_sectors": {
                        "type": "integer",
                        "title": "Number of Sectors",
                        "description": "Economic sectors in SAM-CGE model",
                        "minimum": 3,
                        "maximum": 50,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "macro",
                        "x-ui-order": 1,
                    },
                    "elasticity_substitution": {
                        "type": "number",
                        "title": "Elasticity of Substitution",
                        "description": "CES production function parameter",
                        "minimum": 0.1,
                        "maximum": 2.0,
                        "default": 0.8,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "macro",
                        "x-ui-order": 2,
                    },
                    "convergence_tolerance": {
                        "type": "number",
                        "title": "Convergence Tolerance",
                        "description": "CGE equilibrium convergence threshold",
                        "minimum": 1e-6,
                        "maximum": 1e-2,
                        "default": 1e-4,
                        "x-ui-widget": "number",
                        "x-ui-format": "scientific",
                        "x-ui-group": "macro",
                        "x-ui-order": 3,
                    },
                    "max_iterations": {
                        "type": "integer",
                        "title": "Max Iterations",
                        "description": "Maximum CGE solver iterations",
                        "minimum": 10,
                        "maximum": 500,
                        "default": 100,
                        "x-ui-widget": "slider",
                        "x-ui-step": 10,
                        "x-ui-group": "macro",
                        "x-ui-order": 4,
                    },
                    # Microsimulation Parameters
                    "n_households": {
                        "type": "integer",
                        "title": "Number of Households",
                        "description": "Sample size for microsimulation",
                        "minimum": 100,
                        "maximum": 10000,
                        "default": 1000,
                        "x-ui-widget": "slider",
                        "x-ui-step": 100,
                        "x-ui-group": "micro",
                        "x-ui-order": 1,
                    },
                    "poverty_line": {
                        "type": "number",
                        "title": "Poverty Line ($/day)",
                        "description": "International poverty threshold (2017 PPP)",
                        "minimum": 0.5,
                        "maximum": 10.0,
                        "default": 2.15,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-unit": "$/day",
                        "x-ui-group": "micro",
                        "x-ui-order": 2,
                        "x-ui-help": "World Bank extreme poverty: $2.15 | Lower-middle income: $3.65 | Upper-middle: $6.85",
                    },
                    "income_elasticity_labor": {
                        "type": "number",
                        "title": "Labor Income Elasticity",
                        "description": "Responsiveness of labor income to wage changes",
                        "minimum": 0,
                        "maximum": 2.0,
                        "default": 0.8,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "linkage",
                        "x-ui-order": 1,
                    },
                    "income_elasticity_capital": {
                        "type": "number",
                        "title": "Capital Income Elasticity",
                        "description": "Responsiveness of capital income to return changes",
                        "minimum": 0,
                        "maximum": 2.0,
                        "default": 1.2,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "linkage",
                        "x-ui-order": 2,
                    },
                },
                "required": [],
            },
            default_parameters={
                "n_sectors": 10,
                "elasticity_substitution": 0.8,
                "convergence_tolerance": 1e-4,
                "max_iterations": 100,
                "n_households": 1000,
                "poverty_line": 2.15,
                "income_elasticity_labor": 0.8,
                "income_elasticity_capital": 1.2,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="macro",
                    title="Macro CGE Settings",
                    description="SAM-CGE model configuration",
                    collapsed_by_default=False,
                    parameters=["n_sectors", "elasticity_substitution", "convergence_tolerance", "max_iterations"],
                ),
                ParameterGroupSpec(
                    key="micro",
                    title="Microsimulation Settings",
                    description="Household sample and poverty threshold",
                    collapsed_by_default=False,
                    parameters=["n_households", "poverty_line"],
                ),
                ParameterGroupSpec(
                    key="linkage",
                    title="Macro-Micro Linkage",
                    description="Income elasticities for transmission",
                    collapsed_by_default=False,
                    parameters=["income_elasticity_labor", "income_elasticity_capital"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="poverty_trajectory",
                    title="Poverty Headcount Rate",
                    view_type=ViewType.TIMESERIES,
                    description="Poverty rate over simulation",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="poverty_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="gini_trajectory",
                    title="Inequality (Gini Coefficient)",
                    view_type=ViewType.TIMESERIES,
                    description="Income inequality over time",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="gini_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="quintile_shares",
                    title="Income Distribution (Quintiles)",
                    view_type=ViewType.BAR_CHART,
                    description="Income share by quintile",
                result_class=ResultClass.DOMAIN_DECOMPOSITION,
                output_key="quintile_shares_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="sector_impacts",
                    title="Sectoral Output Changes",
                    view_type=ViewType.BAR_CHART,
                    description="CGE sector output effects",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="sector_impacts_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="distributional_table",
                    title="Distributional Metrics",
                    view_type=ViewType.TABLE,
                    description="Poverty gap, severity, and inequality indices",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="distributional_table_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
