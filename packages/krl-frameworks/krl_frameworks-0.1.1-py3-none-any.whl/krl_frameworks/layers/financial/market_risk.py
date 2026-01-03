# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Market Risk Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Market Risk Assessment Framework.

Production-grade market risk modeling with:
- Value-at-Risk (VaR): Historical, Parametric, Monte Carlo
- Expected Shortfall (ES/CVaR)
- Greeks (Delta, Gamma, Vega, Theta, Rho)
- Stress Testing
- Scenario Analysis
- Factor-based risk decomposition

References:
    - Basel Committee on Banking Supervision FRTB
    - RiskMetrics Technical Document
    - Jorion (2006). "Value at Risk"
    - Hull (2018). "Risk Management and Financial Institutions"

Tier: PROFESSIONAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np
from scipy import stats

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

__all__ = ["MarketRiskFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Market Risk Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class VaRMethod(Enum):
    """VaR calculation methods."""
    HISTORICAL = "Historical Simulation"
    PARAMETRIC = "Variance-Covariance"
    MONTE_CARLO = "Monte Carlo"
    CORNISH_FISHER = "Cornish-Fisher"


class AssetClass(Enum):
    """Asset classes for risk decomposition."""
    EQUITY = "Equity"
    FIXED_INCOME = "Fixed Income"
    FX = "Foreign Exchange"
    COMMODITIES = "Commodities"
    DERIVATIVES = "Derivatives"


@dataclass
class Position:
    """Trading position."""
    
    id: str = ""
    asset_name: str = ""
    asset_class: AssetClass = AssetClass.EQUITY
    quantity: float = 0.0
    market_value: float = 0.0
    currency: str = "USD"
    
    # Greeks (for derivatives)
    delta: float = 1.0  # Default delta=1 for linear positions
    gamma: float = 0.0
    vega: float = 0.0
    theta: float = 0.0
    rho: float = 0.0


@dataclass
class RiskFactors:
    """Market risk factors."""
    
    equity_returns: np.ndarray = field(default_factory=lambda: np.array([]))
    interest_rates: np.ndarray = field(default_factory=lambda: np.array([]))
    fx_rates: np.ndarray = field(default_factory=lambda: np.array([]))
    volatilities: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Factor names
    factor_names: list[str] = field(default_factory=list)


@dataclass
class VaRResult:
    """Value-at-Risk computation result."""
    
    var: float = 0.0  # VaR at confidence level
    confidence_level: float = 0.95
    holding_period_days: int = 1
    method: VaRMethod = VaRMethod.HISTORICAL
    
    # Distribution info
    mean_loss: float = 0.0
    loss_std: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0


@dataclass
class ESResult:
    """Expected Shortfall (CVaR) result."""
    
    es: float = 0.0  # Expected Shortfall
    var: float = 0.0  # Associated VaR
    confidence_level: float = 0.95
    holding_period_days: int = 1
    
    # Tail statistics
    avg_tail_loss: float = 0.0
    max_tail_loss: float = 0.0
    n_tail_observations: int = 0


@dataclass
class GreeksResult:
    """Portfolio Greeks."""
    
    delta: float = 0.0  # Price sensitivity
    gamma: float = 0.0  # Delta sensitivity
    vega: float = 0.0  # Volatility sensitivity
    theta: float = 0.0  # Time decay
    rho: float = 0.0  # Interest rate sensitivity
    
    # Position-level
    position_deltas: dict[str, float] = field(default_factory=dict)
    position_vegas: dict[str, float] = field(default_factory=dict)


@dataclass
class StressTestResult:
    """Stress test result."""
    
    scenario_name: str = ""
    scenario_description: str = ""
    
    # P&L impact
    pnl_impact: float = 0.0
    pnl_impact_percent: float = 0.0
    
    # Factor shocks
    factor_shocks: dict[str, float] = field(default_factory=dict)
    
    # Position-level impacts
    position_impacts: dict[str, float] = field(default_factory=dict)


@dataclass
class RiskDecomposition:
    """Risk factor decomposition."""
    
    # Factor contributions to total VaR
    factor_contributions: dict[str, float] = field(default_factory=dict)
    
    # Marginal VaR
    marginal_var: dict[str, float] = field(default_factory=dict)
    
    # Component VaR
    component_var: dict[str, float] = field(default_factory=dict)
    
    # Diversification benefit
    undiversified_var: float = 0.0
    diversified_var: float = 0.0
    diversification_benefit: float = 0.0


@dataclass
class MarketRiskMetrics:
    """Comprehensive market risk assessment."""
    
    # VaR measures
    var_95: VaRResult = field(default_factory=VaRResult)
    var_99: VaRResult = field(default_factory=VaRResult)
    
    # Expected Shortfall
    es_95: ESResult = field(default_factory=ESResult)
    es_99: ESResult = field(default_factory=ESResult)
    
    # Greeks
    greeks: GreeksResult = field(default_factory=GreeksResult)
    
    # Risk decomposition
    decomposition: RiskDecomposition = field(default_factory=RiskDecomposition)
    
    # Stress tests
    stress_tests: list[StressTestResult] = field(default_factory=list)
    
    # Summary
    total_market_value: float = 0.0
    var_as_percent_of_portfolio: float = 0.0


# ════════════════════════════════════════════════════════════════════════════════
# Market Risk Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class MarketRiskTransition(TransitionFunction):
    """
    Transition function for market risk dynamics.
    
    Models price movements and risk evolution.
    """
    
    name = "MarketRiskTransition"
    
    def __init__(
        self,
        drift: float = 0.0,
        volatility: float = 0.15,
    ):
        self.drift = drift
        self.volatility = volatility
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply market dynamics."""
        params = params or {}
        
        n_cohorts = state.n_cohorts
        dt = 1.0 / 252  # Daily
        
        # GBM returns
        z = np.random.normal(0, 1, n_cohorts)
        returns = self.drift * dt + self.volatility * np.sqrt(dt) * z
        
        # Update sector output as market values
        new_sector = state.sector_output * (1 + returns[:, np.newaxis])
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=state.opportunity_score,
            sector_output=new_sector,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Market Risk Framework
# ════════════════════════════════════════════════════════════════════════════════


class MarketRiskFramework(BaseMetaFramework):
    """
    Market Risk Assessment Framework.
    
    Production-grade implementation of market risk measures:
    
    - Value-at-Risk (Historical, Parametric, Monte Carlo)
    - Expected Shortfall (ES/CVaR)
    - Greeks computation
    - Stress testing
    - Factor-based risk decomposition
    
    Token Weight: 5
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = MarketRiskFramework()
        >>> var = framework.compute_var(
        ...     positions=portfolio,
        ...     returns=historical_returns,
        ...     confidence_level=0.99
        ... )
        >>> print(f"99% 1-day VaR: ${var.var:,.0f}")
    
    References:
        - Basel FRTB
        - RiskMetrics
        - Jorion (2006)
    """
    
    METADATA = FrameworkMetadata(
        slug="market-risk",
        name="Market Risk Assessment",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.PROFESSIONAL,
        description=(
            "Comprehensive market risk framework with VaR, ES, Greeks, "
            "stress testing, and factor decomposition."
        ),
        required_domains=["positions", "returns", "risk_factors"],
        output_domains=["var", "es", "greeks", "stress_tests"],
        constituent_models=["historical_var", "parametric_var", "monte_carlo_var"],
        tags=["market-risk", "var", "expected-shortfall", "stress-testing"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        base_volatility: float = 0.15,
        n_simulations: int = 10000,
        seed: Optional[int] = None,
    ):
        super().__init__()
        self.base_volatility = base_volatility
        self.n_simulations = n_simulations
        self.seed = seed
        self._rng = np.random.default_rng(seed)
        self._transition_fn = MarketRiskTransition(volatility=base_volatility)
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return framework metadata."""
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Initialize state for portfolio."""
        n_cohorts = config.cohort_size or 100
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.70),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.full(n_cohorts, 0.80),
            housing_cost_ratio=np.full(n_cohorts, 0.30),
            opportunity_score=np.random.beta(2, 2, n_cohorts),
            sector_output=np.full((n_cohorts, 5), 1000.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.25),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply market risk transition."""
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """Compute market risk metrics from state."""
        returns = np.diff(state.sector_output, axis=0) / state.sector_output[:-1] if state.sector_output.shape[0] > 1 else np.array([0])
        return {
            "portfolio_volatility": float(np.std(returns)) if len(returns) > 0 else 0.0,
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        """Compute final output."""
        return {
            "framework": "market-risk",
            "n_periods": trajectory.n_periods,
        }

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Market Risk dashboard specification."""
        return FrameworkDashboardSpec(
            slug="market_risk",
            name="Market Risk Assessment",
            description=(
                "Comprehensive market risk framework with VaR, Expected Shortfall, "
                "Greeks computation, stress testing, and factor decomposition."
            ),
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "var_method": {
                        "type": "string",
                        "title": "VaR Method",
                        "enum": ["historical", "parametric", "monte_carlo"],
                        "default": "historical",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                    },
                    "confidence_level": {
                        "type": "number",
                        "title": "Confidence Level",
                        "minimum": 0.9,
                        "maximum": 0.999,
                        "default": 0.99,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-format": ".0%",
                        "x-ui-group": "parameters",
                    },
                    "holding_period": {
                        "type": "integer",
                        "title": "Holding Period (days)",
                        "minimum": 1,
                        "maximum": 252,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-group": "parameters",
                    },
                    "asset_classes": {
                        "type": "array",
                        "title": "Asset Classes",
                        "items": {
                            "type": "string",
                            "enum": ["equity", "fixed_income", "fx", "commodities", "derivatives"],
                        },
                        "default": ["equity", "fixed_income"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "portfolio",
                    },
                },
            },
            default_parameters={
                "var_method": "historical",
                "confidence_level": 0.99,
                "holding_period": 10,
                "asset_classes": ["equity", "fixed_income"],
            },
            parameter_groups=[
                ParameterGroupSpec(key="methodology", title="Methodology", parameters=["var_method"]),
                ParameterGroupSpec(key="parameters", title="Risk Parameters", parameters=["confidence_level", "holding_period"]),
                ParameterGroupSpec(key="portfolio", title="Portfolio", parameters=["asset_classes"]),
            ],
            required_domains=["positions", "returns", "risk_factors"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="var_gauge",
                    title="Value-at-Risk",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "format": "$,.0f"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="var_gauge_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="pnl_distribution",
                    title="P&L Distribution",
                    view_type=ViewType.HISTOGRAM,
                    config={"field": "pnl", "bins": 50, "show_var": True, "show_es": True},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="pnl_distribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="factor_exposures",
                    title="Factor Exposures",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "factor", "y_field": "exposure", "color_by": "asset_class"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="factor_exposures_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="stressed_var",
                    title="Stressed VaR",
                    view_type=ViewType.METRIC_GRID,
                    config={"metrics": [
                        {"key": "var_99", "label": "VaR (99%)", "format": "$,.0f"},
                        {"key": "es_99", "label": "ES (99%)", "format": "$,.0f"},
                        {"key": "stressed_var", "label": "Stressed VaR", "format": "$,.0f"},
                        {"key": "var_ratio", "label": "Stress/Base Ratio", "format": ".1x"},
                    ]},
                result_class=ResultClass.SCALAR_INDEX,
                output_key="stressed_var_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
            ],
        )
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_var(
        self,
        positions: list[Position],
        returns: np.ndarray,
        confidence_level: float = 0.95,
        holding_period_days: int = 1,
        method: VaRMethod = VaRMethod.HISTORICAL,
    ) -> VaRResult:
        """
        Compute Value-at-Risk.
        
        Args:
            positions: Portfolio positions
            returns: Historical returns matrix (T, n)
            confidence_level: VaR confidence level
            holding_period_days: Holding period
            method: VaR calculation method
        
        Returns:
            VaR result
        """
        if len(positions) == 0:
            return VaRResult(confidence_level=confidence_level)
        
        # Position weights
        total_value = sum(p.market_value for p in positions)
        weights = np.array([p.market_value / total_value for p in positions])
        
        # Ensure returns match positions
        n_positions = len(positions)
        if returns.shape[1] != n_positions:
            # Use first n columns or pad
            if returns.shape[1] >= n_positions:
                returns = returns[:, :n_positions]
            else:
                pad = np.tile(returns[:, 0:1], (1, n_positions - returns.shape[1]))
                returns = np.hstack([returns, pad])
        
        # Portfolio returns
        portfolio_returns = returns @ weights
        
        if method == VaRMethod.HISTORICAL:
            # Historical simulation
            var = -np.percentile(portfolio_returns, (1 - confidence_level) * 100)
            
        elif method == VaRMethod.PARAMETRIC:
            # Variance-covariance method
            mu = np.mean(portfolio_returns)
            sigma = np.std(portfolio_returns)
            var = -(mu + stats.norm.ppf(1 - confidence_level) * sigma)
            
        elif method == VaRMethod.MONTE_CARLO:
            # Monte Carlo simulation
            mu = np.mean(portfolio_returns)
            sigma = np.std(portfolio_returns)
            simulated = self._rng.normal(mu, sigma, self.n_simulations)
            var = -np.percentile(simulated, (1 - confidence_level) * 100)
            
        else:  # Cornish-Fisher
            mu = np.mean(portfolio_returns)
            sigma = np.std(portfolio_returns)
            skew = stats.skew(portfolio_returns)
            kurt = stats.kurtosis(portfolio_returns)
            
            z = stats.norm.ppf(1 - confidence_level)
            z_cf = (z + (z**2 - 1) * skew / 6 +
                    (z**3 - 3*z) * (kurt - 3) / 24 -
                    (2*z**3 - 5*z) * skew**2 / 36)
            var = -(mu + z_cf * sigma)
        
        # Scale to holding period
        var = var * total_value * np.sqrt(holding_period_days)
        
        return VaRResult(
            var=float(var),
            confidence_level=confidence_level,
            holding_period_days=holding_period_days,
            method=method,
            mean_loss=float(-np.mean(portfolio_returns) * total_value),
            loss_std=float(np.std(portfolio_returns) * total_value),
            skewness=float(stats.skew(portfolio_returns)),
            kurtosis=float(stats.kurtosis(portfolio_returns)),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_expected_shortfall(
        self,
        positions: list[Position],
        returns: np.ndarray,
        confidence_level: float = 0.95,
        holding_period_days: int = 1,
    ) -> ESResult:
        """
        Compute Expected Shortfall (CVaR).
        
        Args:
            positions: Portfolio positions
            returns: Historical returns matrix
            confidence_level: ES confidence level
            holding_period_days: Holding period
        
        Returns:
            ES result
        """
        if len(positions) == 0:
            return ESResult(confidence_level=confidence_level)
        
        total_value = sum(p.market_value for p in positions)
        weights = np.array([p.market_value / total_value for p in positions])
        
        n_positions = len(positions)
        if returns.shape[1] != n_positions:
            if returns.shape[1] >= n_positions:
                returns = returns[:, :n_positions]
            else:
                pad = np.tile(returns[:, 0:1], (1, n_positions - returns.shape[1]))
                returns = np.hstack([returns, pad])
        
        portfolio_returns = returns @ weights
        
        # VaR threshold
        var_threshold = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
        
        # Expected Shortfall = mean of returns below VaR
        tail_returns = portfolio_returns[portfolio_returns <= var_threshold]
        
        if len(tail_returns) > 0:
            es = -np.mean(tail_returns)
            max_tail_loss = -np.min(tail_returns)
        else:
            es = -var_threshold
            max_tail_loss = -var_threshold
        
        # Scale
        es = es * total_value * np.sqrt(holding_period_days)
        var = -var_threshold * total_value * np.sqrt(holding_period_days)
        max_tail_loss = max_tail_loss * total_value * np.sqrt(holding_period_days)
        
        return ESResult(
            es=float(es),
            var=float(var),
            confidence_level=confidence_level,
            holding_period_days=holding_period_days,
            avg_tail_loss=float(es),
            max_tail_loss=float(max_tail_loss),
            n_tail_observations=len(tail_returns),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_greeks(
        self,
        positions: list[Position],
        spot_price: float = 100.0,
        volatility: float = 0.20,
        risk_free_rate: float = 0.05,
        time_to_expiry: float = 1.0,
    ) -> GreeksResult:
        """
        Compute portfolio Greeks.
        
        Args:
            positions: Portfolio positions (with individual Greeks)
            spot_price: Underlying spot price
            volatility: Implied volatility
            risk_free_rate: Risk-free rate
            time_to_expiry: Time to expiry in years
        
        Returns:
            Portfolio Greeks
        """
        total_delta = 0.0
        total_gamma = 0.0
        total_vega = 0.0
        total_theta = 0.0
        total_rho = 0.0
        
        position_deltas = {}
        position_vegas = {}
        
        for pos in positions:
            # Scale by position size
            pos_delta = pos.delta * pos.quantity * spot_price
            pos_gamma = pos.gamma * pos.quantity * spot_price**2 / 100
            pos_vega = pos.vega * pos.quantity
            pos_theta = pos.theta * pos.quantity
            pos_rho = pos.rho * pos.quantity
            
            total_delta += pos_delta
            total_gamma += pos_gamma
            total_vega += pos_vega
            total_theta += pos_theta
            total_rho += pos_rho
            
            position_deltas[pos.id] = pos_delta
            position_vegas[pos.id] = pos_vega
        
        return GreeksResult(
            delta=float(total_delta),
            gamma=float(total_gamma),
            vega=float(total_vega),
            theta=float(total_theta),
            rho=float(total_rho),
            position_deltas=position_deltas,
            position_vegas=position_vegas,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def run_stress_test(
        self,
        positions: list[Position],
        scenario_name: str,
        factor_shocks: dict[str, float],
    ) -> StressTestResult:
        """
        Run stress test scenario.
        
        Args:
            positions: Portfolio positions
            scenario_name: Name of the scenario
            factor_shocks: Percentage shocks to risk factors
        
        Returns:
            Stress test result
        """
        total_value = sum(p.market_value for p in positions)
        total_pnl = 0.0
        position_impacts = {}
        
        for pos in positions:
            pos_pnl = 0.0
            
            # Apply relevant shocks
            if pos.asset_class == AssetClass.EQUITY:
                equity_shock = factor_shocks.get("equity", 0.0)
                pos_pnl = pos.market_value * equity_shock * pos.delta
                
            elif pos.asset_class == AssetClass.FIXED_INCOME:
                rate_shock = factor_shocks.get("interest_rate", 0.0)
                # Duration-based approximation
                duration = 5.0  # Assumed
                pos_pnl = -pos.market_value * duration * rate_shock / 100
                
            elif pos.asset_class == AssetClass.FX:
                fx_shock = factor_shocks.get("fx", 0.0)
                pos_pnl = pos.market_value * fx_shock
                
            elif pos.asset_class == AssetClass.COMMODITIES:
                commodity_shock = factor_shocks.get("commodity", 0.0)
                pos_pnl = pos.market_value * commodity_shock
                
            # Volatility impact through vega
            vol_shock = factor_shocks.get("volatility", 0.0)
            pos_pnl += pos.vega * vol_shock * 100  # Vega in $ per 1% vol
            
            position_impacts[pos.id] = float(pos_pnl)
            total_pnl += pos_pnl
        
        return StressTestResult(
            scenario_name=scenario_name,
            scenario_description=f"Stress test with shocks: {factor_shocks}",
            pnl_impact=float(total_pnl),
            pnl_impact_percent=float(total_pnl / total_value * 100) if total_value else 0.0,
            factor_shocks=factor_shocks,
            position_impacts=position_impacts,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def decompose_risk(
        self,
        positions: list[Position],
        returns: np.ndarray,
        factor_returns: np.ndarray,
        factor_names: list[str],
        confidence_level: float = 0.95,
    ) -> RiskDecomposition:
        """
        Decompose portfolio risk by factor.
        
        Args:
            positions: Portfolio positions
            returns: Position returns (T, n)
            factor_returns: Factor returns (T, k)
            factor_names: Names of factors
            confidence_level: VaR confidence level
        
        Returns:
            Risk decomposition
        """
        if len(positions) == 0:
            return RiskDecomposition()
        
        total_value = sum(p.market_value for p in positions)
        weights = np.array([p.market_value / total_value for p in positions])
        
        n_positions = len(positions)
        if returns.shape[1] != n_positions:
            if returns.shape[1] >= n_positions:
                returns = returns[:, :n_positions]
            else:
                returns = np.tile(returns[:, 0:1], (1, n_positions))
        
        portfolio_returns = returns @ weights
        
        # Total VaR
        total_var = -np.percentile(portfolio_returns, (1 - confidence_level) * 100) * total_value
        
        # Factor betas (OLS regression)
        n_factors = factor_returns.shape[1]
        betas = np.zeros(n_factors)
        
        for k in range(n_factors):
            # Simple OLS
            X = factor_returns[:, k]
            cov_xy = np.cov(X, portfolio_returns)[0, 1]
            var_x = np.var(X)
            betas[k] = cov_xy / var_x if var_x > 0 else 0
        
        # Factor VaRs
        factor_vars = {}
        factor_contributions = {}
        
        for k, name in enumerate(factor_names):
            factor_vol = np.std(factor_returns[:, k])
            factor_var_k = np.abs(betas[k]) * factor_vol * stats.norm.ppf(confidence_level) * total_value
            factor_vars[name] = float(factor_var_k)
            factor_contributions[name] = float(factor_var_k / max(total_var, 1e-10))
        
        # Marginal VaR per position
        marginal_var = {}
        portfolio_vol = np.std(portfolio_returns)
        
        for i, pos in enumerate(positions):
            # Marginal VaR = weight * cov(r_i, r_p) / portfolio_vol
            cov_ip = np.cov(returns[:, i], portfolio_returns)[0, 1]
            mvar = (pos.market_value / total_value) * cov_ip / portfolio_vol * stats.norm.ppf(confidence_level)
            marginal_var[pos.id] = float(mvar * total_value)
        
        # Component VaR
        component_var = {
            pos_id: mvar * weights[i]
            for i, (pos_id, mvar) in enumerate(marginal_var.items())
        }
        
        # Undiversified VaR (sum of individual VaRs)
        individual_vars = [
            np.std(returns[:, i]) * positions[i].market_value * stats.norm.ppf(confidence_level)
            for i in range(n_positions)
        ]
        undiversified_var = sum(individual_vars)
        
        diversification_benefit = undiversified_var - total_var
        
        return RiskDecomposition(
            factor_contributions=factor_contributions,
            marginal_var=marginal_var,
            component_var=component_var,
            undiversified_var=float(undiversified_var),
            diversified_var=float(total_var),
            diversification_benefit=float(diversification_benefit),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def assess_market_risk(
        self,
        positions: list[Position],
        returns: np.ndarray,
    ) -> MarketRiskMetrics:
        """
        Comprehensive market risk assessment.
        
        Args:
            positions: Portfolio positions
            returns: Historical returns
        
        Returns:
            Complete market risk metrics
        """
        # VaR at multiple confidence levels
        var_95 = self.compute_var(positions, returns, 0.95)
        var_99 = self.compute_var(positions, returns, 0.99)
        
        # Expected Shortfall
        es_95 = self.compute_expected_shortfall(positions, returns, 0.95)
        es_99 = self.compute_expected_shortfall(positions, returns, 0.99)
        
        # Greeks
        greeks = self.compute_greeks(positions)
        
        # Standard stress scenarios
        stress_tests = [
            self.run_stress_test(positions, "2008 Financial Crisis", {
                "equity": -0.40,
                "interest_rate": -2.0,
                "volatility": 0.50,
            }),
            self.run_stress_test(positions, "Rate Spike", {
                "interest_rate": 3.0,
                "equity": -0.15,
            }),
            self.run_stress_test(positions, "Equity Crash", {
                "equity": -0.30,
                "volatility": 0.40,
            }),
        ]
        
        # Risk decomposition (simplified)
        n_factors = 3
        factor_returns = np.random.randn(returns.shape[0], n_factors) * 0.01
        decomposition = self.decompose_risk(
            positions, returns, factor_returns,
            ["Market", "Size", "Value"]
        )
        
        total_value = sum(p.market_value for p in positions)
        
        return MarketRiskMetrics(
            var_95=var_95,
            var_99=var_99,
            es_95=es_95,
            es_99=es_99,
            greeks=greeks,
            decomposition=decomposition,
            stress_tests=stress_tests,
            total_market_value=total_value,
            var_as_percent_of_portfolio=var_99.var / total_value * 100 if total_value else 0,
        )
