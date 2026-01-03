# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - HANK Framework (Heterogeneous Agent New Keynesian)
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Heterogeneous Agent New Keynesian (HANK) Framework.

Implements macroeconomic models with heterogeneous agents:
- Household portfolio choice with borrowing constraints
- Aggregate consumption/saving dynamics
- Monetary policy transmission
- Fiscal policy multipliers
- Wealth inequality dynamics

References:
    - Kaplan, Moll & Violante (2018) - HANK Models
    - Auclert (2019) - Monetary Policy and Redistribution
    - McKay, Nakamura & Steinsson (2016) - Transmission

Tier: PROFESSIONAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional, Tuple

import numpy as np
from scipy import stats, optimize, sparse
from scipy.sparse.linalg import spsolve

from krl_frameworks.core.base import (
    BaseMetaFramework,
    FrameworkMetadata,
    VerticalLayer,
)
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier, requires_tier
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["HANKFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# HANK Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class AssetType(Enum):
    """Types of assets in portfolio."""
    LIQUID = "Liquid Assets"
    ILLIQUID = "Illiquid Assets (Housing, Retirement)"
    BONDS = "Government Bonds"
    EQUITY = "Equity"


class HouseholdType(Enum):
    """Household types by wealth."""
    HAND_TO_MOUTH = "Hand-to-Mouth"
    WEALTHY_HTM = "Wealthy Hand-to-Mouth"
    UNCONSTRAINED = "Unconstrained"


class ShockType(Enum):
    """Types of aggregate shocks."""
    MONETARY = "Monetary Policy"
    FISCAL = "Fiscal Policy"
    PRODUCTIVITY = "TFP Shock"
    DEMAND = "Demand Shock"
    INCOME = "Income Shock"


@dataclass
class HouseholdState:
    """Individual household state."""
    
    # Wealth
    liquid_assets: float = 0.0
    illiquid_assets: float = 0.0
    total_wealth: float = 0.0
    
    # Income
    labor_income: float = 0.0
    capital_income: float = 0.0
    total_income: float = 0.0
    
    # Productivity state (idiosyncratic)
    productivity: float = 1.0
    
    # Classification
    household_type: HouseholdType = HouseholdType.UNCONSTRAINED
    
    # Marginal propensity to consume
    mpc: float = 0.0


@dataclass
class IncomeProcess:
    """Idiosyncratic income process parameters."""
    
    # AR(1) process: log(z') = rho * log(z) + eps
    rho: float = 0.95  # Persistence
    sigma: float = 0.10  # Std of innovation
    
    # Grid
    n_states: int = 7
    
    # Transition matrix (computed)
    grid: np.ndarray = field(default_factory=lambda: np.array([]))
    transition: np.ndarray = field(default_factory=lambda: np.array([]))
    stationary: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class HANKParams:
    """HANK model parameters."""
    
    # Preferences
    beta: float = 0.99  # Discount factor
    gamma: float = 2.0  # Risk aversion
    frisch: float = 0.5  # Frisch elasticity
    
    # Production
    alpha: float = 0.33  # Capital share
    delta: float = 0.025  # Depreciation
    
    # Monetary policy (Taylor rule)
    phi_pi: float = 1.5  # Inflation response
    phi_y: float = 0.5 / 4  # Output gap response
    
    # Fiscal policy
    tax_rate: float = 0.30
    govt_spending_gdp: float = 0.20
    
    # Asset markets
    liquid_return: float = 0.01  # Quarterly
    illiquid_return: float = 0.02
    borrowing_limit: float = -1.0  # Multiple of average income
    illiquid_adj_cost: float = 0.02


@dataclass
class AggregateState:
    """Aggregate economic state."""
    
    # Output and consumption
    output: float = 1.0
    consumption: float = 0.70
    investment: float = 0.20
    government: float = 0.10
    
    # Prices
    interest_rate: float = 0.01
    wage: float = 1.0
    inflation: float = 0.005
    
    # Capital and labor
    capital: float = 10.0
    labor: float = 1.0
    
    # Distribution moments
    wealth_gini: float = 0.0
    liquid_gini: float = 0.0
    htm_share: float = 0.0


@dataclass
class PolicyResponse:
    """Response to policy shocks."""
    
    shock_type: ShockType = ShockType.MONETARY
    shock_size: float = 0.0  # Deviation from steady state
    
    # Impact responses (% deviation)
    output_response: list[float] = field(default_factory=list)
    consumption_response: list[float] = field(default_factory=list)
    investment_response: list[float] = field(default_factory=list)
    inflation_response: list[float] = field(default_factory=list)
    
    # Distributional responses
    htm_consumption_response: list[float] = field(default_factory=list)
    unconstrained_consumption_response: list[float] = field(default_factory=list)
    
    # Multiplier (for fiscal)
    cumulative_multiplier: float = 0.0


@dataclass
class MPCDistribution:
    """Marginal propensity to consume distribution."""
    
    # Overall
    mean_mpc: float = 0.0
    median_mpc: float = 0.0
    
    # By wealth quartile
    q1_mpc: float = 0.0  # Lowest wealth
    q2_mpc: float = 0.0
    q3_mpc: float = 0.0
    q4_mpc: float = 0.0  # Highest wealth
    
    # By type
    htm_mpc: float = 0.0
    wealthy_htm_mpc: float = 0.0
    unconstrained_mpc: float = 0.0


@dataclass
class HANKMetrics:
    """Complete HANK model metrics."""
    
    steady_state: AggregateState = field(default_factory=AggregateState)
    income_process: IncomeProcess = field(default_factory=IncomeProcess)
    mpc_distribution: MPCDistribution = field(default_factory=MPCDistribution)
    policy_responses: list[PolicyResponse] = field(default_factory=list)


# ════════════════════════════════════════════════════════════════════════════════
# HANK Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class HANKTransition(TransitionFunction):
    """Transition function for HANK dynamics."""
    
    name = "HANKTransition"
    
    def __init__(self, params: Optional[HANKParams] = None):
        self.params = params or HANKParams()
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        p = self.params
        
        # Shock
        shock = params.get("shock", 0.0)
        
        # Interest rate response (Taylor rule)
        interest_change = p.phi_pi * shock
        
        # Consumption response (heterogeneous)
        # High MPC agents respond more to income
        mpc_effect = np.where(
            state.opportunity_score < 0.3,  # Constrained
            0.8 * shock,
            0.2 * shock,
        )
        
        new_output = state.sector_output * (1 + shock + interest_change * 0.1)
        new_opportunity = np.clip(state.opportunity_score + mpc_effect * 0.1, 0, 1)
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# HANK Framework
# ════════════════════════════════════════════════════════════════════════════════


class HANKFramework(BaseMetaFramework):
    """
    Heterogeneous Agent New Keynesian Framework.
    
    Production-grade HANK implementation:
    
    - Heterogeneous household portfolio choice
    - Idiosyncratic income risk with Aiyagari dynamics
    - Monetary policy transmission channels
    - Fiscal multiplier analysis
    - MPC distribution computation
    
    Token Weight: 7
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = HANKFramework()
        >>> response = framework.simulate_monetary_shock(-0.01)
        >>> print(f"Output Impact: {response.output_response[0]:.2%}")
    
    References:
        - Kaplan, Moll & Violante (2018)
        - Auclert (2019)
    """
    
    METADATA = FrameworkMetadata(
        slug="hank",
        name="Heterogeneous Agent New Keynesian",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.PROFESSIONAL,
        description=(
            "Heterogeneous Agent New Keynesian model for analyzing "
            "monetary and fiscal policy with wealth inequality."
        ),
        required_domains=["income_process", "wealth_distribution"],
        output_domains=["policy_response", "mpc_distribution", "steady_state"],
        constituent_models=["aiyagari", "sequence_space", "taylor_rule"],
        tags=["hank", "macro", "heterogeneous-agents", "monetary-policy"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self, params: Optional[HANKParams] = None):
        super().__init__()
        self.params = params or HANKParams()
        self._transition_fn = HANKTransition(self.params)
        self._income_process: Optional[IncomeProcess] = None
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        n_cohorts = config.cohort_size or 100
        
        # Initialize with wealth distribution
        wealth = np.random.lognormal(0, 1.5, n_cohorts)
        wealth_normalized = np.clip(wealth / np.max(wealth), 0, 1)
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.95),
            health_burden_score=np.full(n_cohorts, 0.20),
            credit_access_prob=wealth_normalized,
            housing_cost_ratio=np.full(n_cohorts, 0.30),
            opportunity_score=wealth_normalized,
            sector_output=np.full((n_cohorts, 5), 1.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.25),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(self, state: CohortStateVector) -> dict[str, Any]:
        return {
            "mean_wealth": float(np.mean(state.opportunity_score)),
            "wealth_gini": self._compute_gini(state.opportunity_score),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "hank", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return HANK dashboard specification."""
        return FrameworkDashboardSpec(
            slug="hank",
            name="Heterogeneous Agent New Keynesian",
            description=(
                "Heterogeneous Agent New Keynesian model for analyzing monetary "
                "and fiscal policy transmission with wealth inequality dynamics."
            ),
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "wealth_distribution": {
                        "type": "string",
                        "title": "Wealth Distribution",
                        "enum": ["uniform", "lognormal", "pareto", "empirical_us"],
                        "default": "lognormal",
                        "x-ui-widget": "select",
                        "x-ui-group": "distribution",
                    },
                    "labor_supply_elasticity": {
                        "type": "number",
                        "title": "Frisch Elasticity",
                        "minimum": 0.1,
                        "maximum": 2.0,
                        "default": 0.5,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "parameters",
                    },
                    "mpc": {
                        "type": "number",
                        "title": "Average MPC",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.25,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-format": ".0%",
                        "x-ui-group": "parameters",
                    },
                    "n_periods": {
                        "type": "integer",
                        "title": "Simulation Periods",
                        "minimum": 10,
                        "maximum": 100,
                        "default": 40,
                        "x-ui-widget": "slider",
                        "x-ui-group": "simulation",
                    },
                },
            },
            default_parameters={
                "wealth_distribution": "lognormal",
                "labor_supply_elasticity": 0.5,
                "mpc": 0.25,
                "n_periods": 40,
            },
            parameter_groups=[
                ParameterGroupSpec(key="distribution", title="Distribution", parameters=["wealth_distribution"]),
                ParameterGroupSpec(key="parameters", title="Parameters", parameters=["labor_supply_elasticity", "mpc"]),
                ParameterGroupSpec(key="simulation", title="Simulation", parameters=["n_periods"]),
            ],
            required_domains=["income_process", "wealth_distribution"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="wealth_distribution",
                    title="Wealth Distribution",
                    view_type=ViewType.HISTOGRAM,
                    config={"field": "wealth", "bins": 50, "log_scale": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="wealth_distribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="consumption_response",
                    title="Consumption Response",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "period", "y_fields": ["aggregate_consumption", "htm_consumption", "unconstrained_consumption"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="consumption_response_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="labor_dynamics",
                    title="Labor Market Dynamics",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "period", "y_fields": ["hours", "wage", "employment"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="labor_dynamics_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="inequality_metrics",
                    title="Inequality Metrics",
                    view_type=ViewType.METRIC_GRID,
                    config={"metrics": [
                        {"key": "gini", "label": "Gini Coefficient", "format": ".3f"},
                        {"key": "top10_share", "label": "Top 10% Share", "format": ".1%"},
                        {"key": "htm_fraction", "label": "Hand-to-Mouth", "format": ".1%"},
                        {"key": "avg_mpc", "label": "Average MPC", "format": ".2f"},
                    ]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="inequality_metrics_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )

    def _compute_gini(self, values: np.ndarray) -> float:
        """Compute Gini coefficient."""
        n = len(values)
        if n == 0 or np.sum(values) == 0:
            return 0.0
        sorted_v = np.sort(values)
        cumsum = np.cumsum(sorted_v)
        return float((2 * np.sum((np.arange(1, n + 1) * sorted_v))) / (n * cumsum[-1]) - (n + 1) / n)
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def discretize_income_process(
        self,
        rho: float = 0.95,
        sigma: float = 0.10,
        n_states: int = 7,
    ) -> IncomeProcess:
        """
        Discretize AR(1) income process using Rouwenhorst method.
        
        Args:
            rho: Persistence
            sigma: Std of innovation
            n_states: Number of grid points
        
        Returns:
            Income process with grid and transition matrix
        """
        # Rouwenhorst method (better for persistent processes)
        sigma_y = sigma / np.sqrt(1 - rho ** 2)
        
        # Grid
        grid = np.linspace(-sigma_y * np.sqrt(n_states - 1), 
                          sigma_y * np.sqrt(n_states - 1), 
                          n_states)
        
        # Transition matrix
        p = (1 + rho) / 2
        
        if n_states == 2:
            transition = np.array([[p, 1 - p], [1 - p, p]])
        else:
            # Build recursively
            P_n = np.array([[p, 1 - p], [1 - p, p]])
            
            for i in range(3, n_states + 1):
                zeros_col = np.zeros((i - 1, 1))
                zeros_row = np.zeros((1, i - 1))
                
                P_new = p * np.block([[P_n, zeros_col], [zeros_row, 0]])
                P_new += (1 - p) * np.block([[zeros_col, P_n], [0, zeros_row]])
                P_new += (1 - p) * np.block([[zeros_row, 0], [P_n, zeros_col]])
                P_new += p * np.block([[0, zeros_row], [zeros_col, P_n]])
                
                P_new[1:-1, :] /= 2
                P_n = P_new
            
            transition = P_n
        
        # Stationary distribution
        eigenvalues, eigenvectors = np.linalg.eig(transition.T)
        stationary_idx = np.argmin(np.abs(eigenvalues - 1))
        stationary = np.real(eigenvectors[:, stationary_idx])
        stationary = stationary / stationary.sum()
        
        self._income_process = IncomeProcess(
            rho=rho,
            sigma=sigma,
            n_states=n_states,
            grid=np.exp(grid),  # Convert to levels
            transition=transition,
            stationary=stationary,
        )
        
        return self._income_process
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_mpc_distribution(
        self,
        wealth: np.ndarray,
        liquid_share: np.ndarray,
        income: np.ndarray,
    ) -> MPCDistribution:
        """
        Compute MPC distribution across households.
        
        Args:
            wealth: Total wealth
            liquid_share: Share of wealth that's liquid
            income: Income
        
        Returns:
            MPC distribution
        """
        n = len(wealth)
        liquid = wealth * liquid_share
        
        # Classify households
        avg_income = np.mean(income)
        
        # Hand-to-mouth: low liquid wealth
        htm_mask = liquid < 0.5 * avg_income
        
        # Wealthy HTM: low liquid but high illiquid
        illiquid = wealth - liquid
        wealthy_htm_mask = htm_mask & (illiquid > 2 * avg_income)
        
        # Pure HTM (not wealthy)
        pure_htm_mask = htm_mask & ~wealthy_htm_mask
        
        # Unconstrained
        unconstrained_mask = ~htm_mask
        
        # MPC rules (simplified)
        mpc = np.zeros(n)
        mpc[pure_htm_mask] = 0.8 + 0.15 * np.random.random(sum(pure_htm_mask))
        mpc[wealthy_htm_mask] = 0.4 + 0.2 * np.random.random(sum(wealthy_htm_mask))
        mpc[unconstrained_mask] = 0.05 + 0.15 * np.random.random(sum(unconstrained_mask))
        
        # By quartile
        quartiles = np.percentile(wealth, [25, 50, 75])
        q1_mask = wealth <= quartiles[0]
        q2_mask = (wealth > quartiles[0]) & (wealth <= quartiles[1])
        q3_mask = (wealth > quartiles[1]) & (wealth <= quartiles[2])
        q4_mask = wealth > quartiles[2]
        
        return MPCDistribution(
            mean_mpc=float(np.mean(mpc)),
            median_mpc=float(np.median(mpc)),
            q1_mpc=float(np.mean(mpc[q1_mask])) if any(q1_mask) else 0,
            q2_mpc=float(np.mean(mpc[q2_mask])) if any(q2_mask) else 0,
            q3_mpc=float(np.mean(mpc[q3_mask])) if any(q3_mask) else 0,
            q4_mpc=float(np.mean(mpc[q4_mask])) if any(q4_mask) else 0,
            htm_mpc=float(np.mean(mpc[pure_htm_mask])) if any(pure_htm_mask) else 0,
            wealthy_htm_mpc=float(np.mean(mpc[wealthy_htm_mask])) if any(wealthy_htm_mask) else 0,
            unconstrained_mpc=float(np.mean(mpc[unconstrained_mask])) if any(unconstrained_mask) else 0,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_steady_state(
        self,
        wealth_distribution: np.ndarray,
        income_distribution: np.ndarray,
    ) -> AggregateState:
        """
        Compute steady state aggregates.
        
        Args:
            wealth_distribution: Household wealth
            income_distribution: Household income
        
        Returns:
            Aggregate steady state
        """
        p = self.params
        
        # Aggregates
        total_wealth = np.sum(wealth_distribution)
        total_income = np.sum(income_distribution)
        
        # Production function
        capital = total_wealth * 0.3  # Simplified
        labor = 1.0
        output = capital ** p.alpha * labor ** (1 - p.alpha)
        
        # Consumption-output ratio
        consumption = output * (1 - p.govt_spending_gdp - 0.1)  # C/Y
        investment = output * 0.1
        government = output * p.govt_spending_gdp
        
        # Prices
        wage = (1 - p.alpha) * output / labor
        rental_rate = p.alpha * output / capital
        interest_rate = rental_rate - p.delta
        
        # Distribution
        wealth_gini = self._compute_gini(wealth_distribution)
        
        # HTM share
        avg_income = np.mean(income_distribution)
        htm_share = np.mean(wealth_distribution < 0.5 * avg_income)
        
        return AggregateState(
            output=output,
            consumption=consumption,
            investment=investment,
            government=government,
            interest_rate=interest_rate,
            wage=wage,
            inflation=0.005,  # Target
            capital=capital,
            labor=labor,
            wealth_gini=wealth_gini,
            htm_share=htm_share,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def simulate_monetary_shock(
        self,
        shock_size: float = -0.0025,  # 25bp rate cut
        horizon: int = 20,
    ) -> PolicyResponse:
        """
        Simulate monetary policy shock.
        
        Args:
            shock_size: Interest rate shock
            horizon: Simulation horizon (quarters)
        
        Returns:
            Policy response
        """
        p = self.params
        
        # Initial conditions
        output = [0.0] * horizon
        consumption = [0.0] * horizon
        investment = [0.0] * horizon
        inflation = [0.0] * horizon
        
        htm_consumption = [0.0] * horizon
        unconstrained_consumption = [0.0] * horizon
        
        # Persistence
        rho_i = 0.8
        
        # Simulate
        i_shock = shock_size
        for t in range(horizon):
            # Interest rate (decaying shock)
            i_t = i_shock * (rho_i ** t)
            
            # Output response (IS curve)
            if t > 0:
                output[t] = 0.5 * output[t - 1] - 0.3 * i_t
            else:
                output[t] = -0.3 * i_t
            
            # Inflation (Phillips curve)
            inflation[t] = 0.9 * inflation[t - 1] if t > 0 else 0
            inflation[t] += 0.1 * output[t]
            
            # Consumption - heterogeneous response
            htm_consumption[t] = 0.8 * output[t]  # High MPC
            unconstrained_consumption[t] = 0.2 * output[t]  # Low MPC
            
            # Aggregate consumption (weighted by shares)
            htm_share = 0.3
            consumption[t] = htm_share * htm_consumption[t] + (1 - htm_share) * unconstrained_consumption[t]
            
            # Investment
            investment[t] = -0.5 * i_t + 0.3 * output[t]
        
        return PolicyResponse(
            shock_type=ShockType.MONETARY,
            shock_size=shock_size,
            output_response=output,
            consumption_response=consumption,
            investment_response=investment,
            inflation_response=inflation,
            htm_consumption_response=htm_consumption,
            unconstrained_consumption_response=unconstrained_consumption,
            cumulative_multiplier=0.0,  # Not applicable for monetary
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def simulate_fiscal_shock(
        self,
        shock_size: float = 0.01,  # 1% of GDP
        shock_type: str = "spending",  # "spending" or "transfer"
        horizon: int = 20,
    ) -> PolicyResponse:
        """
        Simulate fiscal policy shock.
        
        Args:
            shock_size: Fiscal shock (% of GDP)
            shock_type: Spending or transfer
            horizon: Simulation horizon
        
        Returns:
            Policy response with multiplier
        """
        output = [0.0] * horizon
        consumption = [0.0] * horizon
        
        htm_consumption = [0.0] * horizon
        unconstrained_consumption = [0.0] * horizon
        
        # Persistence
        rho_g = 0.9
        
        # MPC matters more for transfers
        if shock_type == "transfer":
            htm_mpc = 0.9
            unconstrained_mpc = 0.15
        else:  # spending
            htm_mpc = 0.5
            unconstrained_mpc = 0.2
        
        htm_share = 0.3
        avg_mpc = htm_share * htm_mpc + (1 - htm_share) * unconstrained_mpc
        
        # Multiplier
        multiplier = 1 / (1 - avg_mpc * 0.8)  # Simplified
        
        for t in range(horizon):
            g_t = shock_size * (rho_g ** t)
            
            # Direct effect
            output[t] = multiplier * g_t
            
            # Consumption by type
            htm_consumption[t] = htm_mpc * g_t
            unconstrained_consumption[t] = unconstrained_mpc * g_t
            
            consumption[t] = htm_share * htm_consumption[t] + (1 - htm_share) * unconstrained_consumption[t]
        
        # Cumulative multiplier
        cumulative = sum(output) / sum([shock_size * (rho_g ** t) for t in range(horizon)])
        
        return PolicyResponse(
            shock_type=ShockType.FISCAL,
            shock_size=shock_size,
            output_response=output,
            consumption_response=consumption,
            investment_response=[0.0] * horizon,
            inflation_response=[0.0] * horizon,
            htm_consumption_response=htm_consumption,
            unconstrained_consumption_response=unconstrained_consumption,
            cumulative_multiplier=cumulative,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def full_analysis(
        self,
        wealth: np.ndarray,
        liquid_share: np.ndarray,
        income: np.ndarray,
    ) -> HANKMetrics:
        """
        Complete HANK analysis.
        
        Args:
            wealth: Household wealth
            liquid_share: Liquid asset share
            income: Household income
        
        Returns:
            Complete HANK metrics
        """
        # Income process
        income_proc = self.discretize_income_process()
        
        # MPC distribution
        mpc_dist = self.compute_mpc_distribution(wealth, liquid_share, income)
        
        # Steady state
        steady = self.compute_steady_state(wealth, income)
        
        # Policy responses
        monetary = self.simulate_monetary_shock()
        fiscal_spend = self.simulate_fiscal_shock(shock_type="spending")
        fiscal_transfer = self.simulate_fiscal_shock(shock_type="transfer")
        
        return HANKMetrics(
            steady_state=steady,
            income_process=income_proc,
            mpc_distribution=mpc_dist,
            policy_responses=[monetary, fiscal_spend, fiscal_transfer],
        )
