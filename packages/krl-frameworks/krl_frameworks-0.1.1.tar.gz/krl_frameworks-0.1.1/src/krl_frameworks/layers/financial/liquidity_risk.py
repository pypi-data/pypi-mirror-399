# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Liquidity Risk Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Liquidity Risk Assessment Framework.

Implements comprehensive liquidity risk measurement and stress testing:
- Liquidity Coverage Ratio (LCR) - Basel III
- Net Stable Funding Ratio (NSFR) - Basel III
- Cash flow forecasting and gap analysis
- Liquidity stress testing
- Funding concentration risk
- Intraday liquidity monitoring

References:
    - Basel III: International regulatory framework for banks (2010-2017)
    - BCBS 238: Monitoring tools for intraday liquidity management
    - ECB Guide to ICAAP: Internal liquidity adequacy assessment
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np

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

__all__ = ["LiquidityRiskFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Liquidity Risk Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class LiquidityRatioType(Enum):
    """Regulatory liquidity ratio types."""
    LCR = "Liquidity Coverage Ratio"
    NSFR = "Net Stable Funding Ratio"
    LTD = "Loan-to-Deposit Ratio"
    QUICK = "Quick Ratio"


class HQLALevel(Enum):
    """High-Quality Liquid Assets levels (Basel III)."""
    LEVEL_1 = "Level 1 - Cash, Central Bank Reserves"
    LEVEL_2A = "Level 2A - Government Bonds, Covered Bonds"
    LEVEL_2B = "Level 2B - Corporate Bonds, Equities, MBS"


class StressScenario(Enum):
    """Liquidity stress scenarios."""
    BASELINE = "Baseline"
    MODERATE = "Moderate Stress"
    SEVERE = "Severe Stress"
    SYSTEMIC = "Systemic Crisis"


@dataclass
class LiquidityConfig:
    """Configuration for liquidity risk analysis."""
    
    # Time horizons
    lcr_horizon_days: int = 30
    nsfr_horizon_months: int = 12
    stress_horizon_days: int = 90
    
    # LCR parameters
    lcr_minimum: float = 1.0  # 100% regulatory minimum
    level_2a_cap: float = 0.40  # 40% of total HQLA
    level_2b_cap: float = 0.15  # 15% of total HQLA
    
    # NSFR parameters
    nsfr_minimum: float = 1.0  # 100% regulatory minimum
    
    # Stress test parameters
    retail_outflow_rate: float = 0.05  # 5% in 30 days
    wholesale_outflow_rate: float = 0.25  # 25% in 30 days
    collateral_outflow_rate: float = 0.10
    
    # Funding concentration
    funding_concentration_threshold: float = 0.10  # 10% from single source
    
    # Intraday
    intraday_buffer: float = 0.20  # 20% of daily settlements


@dataclass
class HQLAPortfolio:
    """High-Quality Liquid Assets breakdown."""
    
    # Level 1 (100% weight)
    cash: float = 0.0
    central_bank_reserves: float = 0.0
    sovereign_bonds: float = 0.0
    
    # Level 2A (85% weight, max 40% of total)
    government_bonds: float = 0.0
    covered_bonds: float = 0.0
    pse_securities: float = 0.0
    
    # Level 2B (50-75% weight, max 15% of total)
    corporate_bonds: float = 0.0
    equities: float = 0.0
    rmbs: float = 0.0
    
    @property
    def level_1_total(self) -> float:
        """Total Level 1 assets."""
        return self.cash + self.central_bank_reserves + self.sovereign_bonds
    
    @property
    def level_2a_total(self) -> float:
        """Total Level 2A assets (pre-haircut)."""
        return self.government_bonds + self.covered_bonds + self.pse_securities
    
    @property
    def level_2b_total(self) -> float:
        """Total Level 2B assets (pre-haircut)."""
        return self.corporate_bonds + self.equities + self.rmbs
    
    def compute_hqla(self, level_2a_cap: float = 0.40, level_2b_cap: float = 0.15) -> float:
        """
        Compute total HQLA with haircuts and caps.
        
        Level 1: 100% weight
        Level 2A: 85% weight, capped at 40% of adjusted HQLA
        Level 2B: 50% weight, capped at 15% of adjusted HQLA
        """
        l1 = self.level_1_total
        l2a = self.level_2a_total * 0.85
        l2b = (self.corporate_bonds * 0.50 + 
               self.equities * 0.50 + 
               self.rmbs * 0.75)
        
        # Cap Level 2
        max_l2 = l1 / (1 - level_2a_cap - level_2b_cap) * (level_2a_cap + level_2b_cap)
        l2a = min(l2a, l1 / (1 - level_2a_cap) * level_2a_cap)
        l2b = min(l2b, l1 / (1 - level_2b_cap) * level_2b_cap)
        
        return l1 + l2a + l2b


@dataclass
class CashFlowBucket:
    """Cash flow analysis for a time bucket."""
    
    bucket_name: str = ""
    days_from_now: int = 0
    
    # Inflows
    maturing_assets: float = 0.0
    loan_repayments: float = 0.0
    other_inflows: float = 0.0
    
    # Outflows
    maturing_liabilities: float = 0.0
    deposit_withdrawals: float = 0.0
    other_outflows: float = 0.0
    
    @property
    def net_cash_flow(self) -> float:
        """Net cash flow for this bucket."""
        inflows = self.maturing_assets + self.loan_repayments + self.other_inflows
        outflows = self.maturing_liabilities + self.deposit_withdrawals + self.other_outflows
        return inflows - outflows


@dataclass
class LCRMetrics:
    """Liquidity Coverage Ratio metrics."""
    
    # HQLA
    hqla: HQLAPortfolio = field(default_factory=HQLAPortfolio)
    total_hqla: float = 0.0
    
    # Cash outflows
    retail_deposits_outflow: float = 0.0
    wholesale_deposits_outflow: float = 0.0
    secured_funding_outflow: float = 0.0
    derivative_outflow: float = 0.0
    other_outflow: float = 0.0
    total_outflow: float = 0.0
    
    # Cash inflows (capped at 75% of outflows)
    loan_inflows: float = 0.0
    secured_lending_inflow: float = 0.0
    other_inflow: float = 0.0
    total_inflow: float = 0.0
    capped_inflow: float = 0.0
    
    # LCR
    net_cash_outflow: float = 0.0
    lcr: float = 0.0
    
    # Compliance
    meets_minimum: bool = False
    surplus_deficit: float = 0.0


@dataclass
class NSFRMetrics:
    """Net Stable Funding Ratio metrics."""
    
    # Available Stable Funding (ASF)
    tier1_capital: float = 0.0
    tier2_capital: float = 0.0
    stable_deposits: float = 0.0
    less_stable_deposits: float = 0.0
    wholesale_funding_1yr: float = 0.0
    total_asf: float = 0.0
    
    # Required Stable Funding (RSF)
    cash: float = 0.0
    unencumbered_l1: float = 0.0
    loans_to_banks: float = 0.0
    performing_loans: float = 0.0
    mortgages: float = 0.0
    other_assets: float = 0.0
    off_balance_sheet: float = 0.0
    total_rsf: float = 0.0
    
    # NSFR
    nsfr: float = 0.0
    
    # Compliance
    meets_minimum: bool = False
    surplus_deficit: float = 0.0


@dataclass
class StressTestResult:
    """Liquidity stress test results."""
    
    scenario: StressScenario = StressScenario.BASELINE
    
    # Outflow assumptions
    retail_outflow_rate: float = 0.0
    wholesale_outflow_rate: float = 0.0
    
    # Day-by-day liquidity
    daily_net_liquidity: list[float] = field(default_factory=list)
    cumulative_net_position: list[float] = field(default_factory=list)
    
    # Minimum liquidity
    minimum_liquidity: float = 0.0
    minimum_day: int = 0
    
    # Survival horizon
    survival_days: int = 0
    survives_horizon: bool = True
    
    # Buffer requirements
    required_buffer: float = 0.0
    current_buffer: float = 0.0
    buffer_adequacy: bool = True


@dataclass
class FundingConcentration:
    """Funding concentration analysis."""
    
    # Top counterparties
    top_5_funding_share: float = 0.0
    top_10_funding_share: float = 0.0
    largest_single_source: float = 0.0
    
    # By type
    retail_share: float = 0.0
    wholesale_share: float = 0.0
    interbank_share: float = 0.0
    capital_markets_share: float = 0.0
    
    # Concentration risk
    herfindahl_index: float = 0.0
    concentration_risk_level: str = ""


@dataclass
class LiquidityRiskMetrics:
    """Comprehensive liquidity risk metrics."""
    
    # Regulatory ratios
    lcr: LCRMetrics = field(default_factory=LCRMetrics)
    nsfr: NSFRMetrics = field(default_factory=NSFRMetrics)
    
    # Cash flow analysis
    cash_flow_gaps: list[CashFlowBucket] = field(default_factory=list)
    cumulative_gap: float = 0.0
    
    # Stress tests
    stress_tests: dict[str, StressTestResult] = field(default_factory=dict)
    
    # Funding concentration
    funding_concentration: FundingConcentration = field(default_factory=FundingConcentration)
    
    # Overall assessment
    overall_risk_rating: str = ""
    key_vulnerabilities: list[str] = field(default_factory=list)


# ════════════════════════════════════════════════════════════════════════════════
# Liquidity Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class LiquidityTransition(TransitionFunction):
    """
    Liquidity risk transition function.
    
    Models the evolution of liquidity position over time
    under various stress scenarios.
    """
    
    name = "LiquidityTransition"
    
    def __init__(
        self,
        daily_outflow_rate: float = 0.01,
        inflow_volatility: float = 0.02,
        asset_liquidation_cost: float = 0.05,
    ):
        self.daily_outflow_rate = daily_outflow_rate
        self.inflow_volatility = inflow_volatility
        self.asset_liquidation_cost = asset_liquidation_cost
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply liquidity transition dynamics."""
        params = params or {}
        
        n_cohorts = state.n_cohorts
        
        # Stress level affects outflows
        stress_level = params.get("stress_level", 0.0)  # 0 to 1
        
        # Base outflow rate + stress component
        outflow_rate = self.daily_outflow_rate * (1 + stress_level * 2)
        
        # Random inflow variation
        inflow_shock = np.random.normal(0, self.inflow_volatility, n_cohorts)
        
        # Credit access as proxy for liquidity
        new_credit = np.clip(
            state.credit_access_prob * (1 - outflow_rate) + inflow_shock,
            0.0, 1.0
        )
        
        # Sector output affected by liquidity constraints
        liquidity_multiplier = 0.95 + 0.1 * np.mean(new_credit)
        new_sector_output = state.sector_output * liquidity_multiplier
        
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
# Liquidity Risk Framework
# ════════════════════════════════════════════════════════════════════════════════


class LiquidityRiskFramework(BaseMetaFramework):
    """
    Liquidity Risk Assessment Framework.
    
    Production-grade implementation of Basel III liquidity risk
    measurement and stress testing. Supports:
    
    - Liquidity Coverage Ratio (LCR) calculation
    - Net Stable Funding Ratio (NSFR) calculation
    - Cash flow gap analysis
    - Multi-scenario stress testing
    - Funding concentration analysis
    - Intraday liquidity monitoring
    
    Token Weight: 5
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = LiquidityRiskFramework()
        >>> lcr = framework.compute_lcr(
        ...     hqla=hqla_portfolio,
        ...     outflows=cash_outflows,
        ...     inflows=cash_inflows,
        ... )
        >>> print(f"LCR: {lcr.lcr:.1%}")
    
    References:
        - Basel III LCR: BCBS 238, 239
        - Basel III NSFR: BCBS 295
        - ECB ILAAP Guide
    """
    
    METADATA = FrameworkMetadata(
        slug="liquidity-risk",
        name="Liquidity Risk Assessment",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.PROFESSIONAL,
        description=(
            "Basel III liquidity risk measurement including LCR, NSFR, "
            "cash flow analysis, and stress testing."
        ),
        required_domains=["assets", "liabilities", "cash_flows"],
        output_domains=["lcr", "nsfr", "stress_test", "funding_risk"],
        constituent_models=["lcr_calculator", "nsfr_calculator", "stress_simulator"],
        tags=["liquidity", "basel-iii", "lcr", "nsfr", "stress-test", "regulatory"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        config: Optional[LiquidityConfig] = None,
    ):
        super().__init__()
        self.config = config or LiquidityConfig()
        self._transition_fn = LiquidityTransition()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        """Return framework metadata."""
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Initialize state for liquidity analysis."""
        n_cohorts = config.cohort_size or 100
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.65),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.random.beta(8, 2, n_cohorts),  # high liquidity baseline
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
        """Apply liquidity transition dynamics."""
        return self._transition_fn(state, t, config)
    
    def _compute_metrics(
        self,
        state: CohortStateVector,
    ) -> dict[str, Any]:
        """Compute liquidity-relevant metrics from state."""
        return {
            "mean_liquidity": float(np.mean(state.credit_access_prob)),
            "min_liquidity": float(np.min(state.credit_access_prob)),
            "liquidity_at_risk": float(np.percentile(state.credit_access_prob, 5)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        """Compute final output from trajectory."""
        return {
            "framework": "liquidity-risk",
            "n_periods": trajectory.n_periods,
        }

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Liquidity Risk dashboard specification."""
        return FrameworkDashboardSpec(
            slug="liquidity_risk",
            name="Liquidity Risk Assessment",
            description=(
                "Basel III liquidity risk measurement including LCR, NSFR, "
                "cash flow gap analysis, and multi-scenario stress testing."
            ),
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "stress_scenario": {
                        "type": "string",
                        "title": "Stress Scenario",
                        "enum": ["baseline", "moderate", "severe", "systemic"],
                        "default": "baseline",
                        "x-ui-widget": "select",
                        "x-ui-group": "scenario",
                    },
                    "time_horizon": {
                        "type": "integer",
                        "title": "Time Horizon (days)",
                        "minimum": 1,
                        "maximum": 365,
                        "default": 30,
                        "x-ui-widget": "slider",
                        "x-ui-group": "parameters",
                    },
                    "liquidity_buffer": {
                        "type": "number",
                        "title": "Liquidity Buffer (%)",
                        "minimum": 0,
                        "maximum": 50,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-format": ".0%",
                        "x-ui-group": "parameters",
                    },
                    "funding_source": {
                        "type": "string",
                        "title": "Primary Funding Source",
                        "enum": ["retail_deposits", "wholesale", "interbank", "central_bank"],
                        "default": "retail_deposits",
                        "x-ui-widget": "select",
                        "x-ui-group": "funding",
                    },
                },
            },
            default_parameters={
                "stress_scenario": "baseline",
                "time_horizon": 30,
                "liquidity_buffer": 10,
                "funding_source": "retail_deposits",
            },
            parameter_groups=[
                ParameterGroupSpec(key="scenario", title="Stress Scenario", parameters=["stress_scenario"]),
                ParameterGroupSpec(key="parameters", title="Parameters", parameters=["time_horizon", "liquidity_buffer"]),
                ParameterGroupSpec(key="funding", title="Funding", parameters=["funding_source"]),
            ],
            required_domains=["assets", "liabilities", "cash_flows"],
            min_tier=Tier.PROFESSIONAL,
            output_views=[
                OutputViewSpec(
                    key="lcr_gauge",
                    title="LCR",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 2, "thresholds": [0.8, 1.0, 1.5], "format": ".0%"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="lcr_gauge_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="nsfr_gauge",
                    title="NSFR",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 2, "thresholds": [0.8, 1.0, 1.5], "format": ".0%"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="nsfr_gauge_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="cash_flow_ladder",
                    title="Cash Flow Ladder",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "time_bucket", "y_field": "net_cash_flow", "color_by": "sign"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="cash_flow_ladder_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="liquidity_buffer",
                    title="Liquidity Buffer",
                    view_type=ViewType.METRIC_GRID,
                    config={"metrics": [
                        {"key": "lcr", "label": "LCR", "format": ".0%"},
                        {"key": "nsfr", "label": "NSFR", "format": ".0%"},
                        {"key": "hqla", "label": "HQLA", "format": "$,.0f"},
                        {"key": "survival_days", "label": "Survival Period", "format": ".0f days"},
                    ]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="liquidity_buffer_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_lcr(
        self,
        hqla: HQLAPortfolio,
        retail_deposits: float,
        wholesale_deposits: float,
        secured_funding: float,
        derivative_positions: float,
        committed_facilities: float,
        loan_inflows: float,
        secured_lending: float,
        *,
        stable_deposit_rate: float = 0.95,
        less_stable_deposit_rate: float = 0.90,
    ) -> LCRMetrics:
        """
        Compute Liquidity Coverage Ratio (LCR).
        
        LCR = HQLA / Net Cash Outflows (30 days)
        
        Args:
            hqla: High-quality liquid assets portfolio
            retail_deposits: Total retail deposits
            wholesale_deposits: Total wholesale deposits
            secured_funding: Secured funding transactions
            derivative_positions: Derivative exposures
            committed_facilities: Committed credit/liquidity facilities
            loan_inflows: Expected loan repayments
            secured_lending: Secured lending transactions
            stable_deposit_rate: Retention rate for stable deposits
            less_stable_deposit_rate: Retention rate for less stable deposits
        
        Returns:
            LCR calculation results
        """
        # Compute HQLA
        total_hqla = hqla.compute_hqla(
            self.config.level_2a_cap,
            self.config.level_2b_cap
        )
        
        # Cash outflows (30-day horizon)
        # Retail: stable (5%), less stable (10%)
        retail_stable = retail_deposits * 0.6 * (1 - stable_deposit_rate)
        retail_less_stable = retail_deposits * 0.4 * (1 - less_stable_deposit_rate)
        retail_outflow = retail_stable + retail_less_stable
        
        # Wholesale: unsecured (25-100%), secured (various)
        wholesale_outflow = wholesale_deposits * self.config.wholesale_outflow_rate
        
        # Secured funding
        secured_outflow = secured_funding * self.config.collateral_outflow_rate
        
        # Derivatives (simplified)
        derivative_outflow = derivative_positions * 0.05
        
        # Committed facilities
        other_outflow = committed_facilities * 0.10
        
        total_outflow = (
            retail_outflow 
            + wholesale_outflow 
            + secured_outflow 
            + derivative_outflow 
            + other_outflow
        )
        
        # Cash inflows (capped at 75% of outflows)
        loan_inflow = loan_inflows * 0.50  # assume 50% collectability
        secured_inflow = secured_lending * 0.50
        other_inflow = 0.0
        
        total_inflow = loan_inflow + secured_inflow + other_inflow
        capped_inflow = min(total_inflow, 0.75 * total_outflow)
        
        # Net cash outflow
        net_cash_outflow = total_outflow - capped_inflow
        
        # LCR
        lcr = total_hqla / max(net_cash_outflow, 1e-10)
        
        meets_minimum = lcr >= self.config.lcr_minimum
        surplus_deficit = total_hqla - net_cash_outflow * self.config.lcr_minimum
        
        return LCRMetrics(
            hqla=hqla,
            total_hqla=float(total_hqla),
            retail_deposits_outflow=float(retail_outflow),
            wholesale_deposits_outflow=float(wholesale_outflow),
            secured_funding_outflow=float(secured_outflow),
            derivative_outflow=float(derivative_outflow),
            other_outflow=float(other_outflow),
            total_outflow=float(total_outflow),
            loan_inflows=float(loan_inflow),
            secured_lending_inflow=float(secured_inflow),
            other_inflow=float(other_inflow),
            total_inflow=float(total_inflow),
            capped_inflow=float(capped_inflow),
            net_cash_outflow=float(net_cash_outflow),
            lcr=float(lcr),
            meets_minimum=meets_minimum,
            surplus_deficit=float(surplus_deficit),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_nsfr(
        self,
        tier1_capital: float,
        tier2_capital: float,
        retail_deposits: float,
        wholesale_funding: float,
        other_liabilities: float,
        cash_and_reserves: float,
        government_securities: float,
        loans_to_banks: float,
        performing_loans: float,
        mortgages: float,
        other_assets: float,
        off_balance_sheet: float,
        *,
        retail_stable_share: float = 0.6,
    ) -> NSFRMetrics:
        """
        Compute Net Stable Funding Ratio (NSFR).
        
        NSFR = Available Stable Funding / Required Stable Funding
        
        Args:
            tier1_capital: CET1 + AT1 capital
            tier2_capital: Tier 2 capital
            retail_deposits: Total retail deposits
            wholesale_funding: Wholesale funding > 1 year
            other_liabilities: Other liabilities and equity
            cash_and_reserves: Cash and central bank reserves
            government_securities: Government and PSE securities
            loans_to_banks: Loans to financial institutions
            performing_loans: Performing non-retail loans
            mortgages: Residential mortgages
            other_assets: Other assets
            off_balance_sheet: Off-balance sheet exposures
            retail_stable_share: Share of retail deposits that are stable
        
        Returns:
            NSFR calculation results
        """
        # Available Stable Funding (ASF)
        # Tier 1 & 2: 100%
        asf_capital = tier1_capital + tier2_capital
        
        # Stable retail deposits: 95%
        stable_deposits = retail_deposits * retail_stable_share * 0.95
        
        # Less stable retail deposits: 90%
        less_stable_deposits = retail_deposits * (1 - retail_stable_share) * 0.90
        
        # Wholesale funding >1yr: 100%
        asf_wholesale = wholesale_funding * 1.0
        
        # Other liabilities: 50%
        asf_other = other_liabilities * 0.50
        
        total_asf = (
            asf_capital 
            + stable_deposits 
            + less_stable_deposits 
            + asf_wholesale 
            + asf_other
        )
        
        # Required Stable Funding (RSF)
        # Cash: 0%
        rsf_cash = cash_and_reserves * 0.0
        
        # Government securities (unencumbered L1): 5%
        rsf_govt = government_securities * 0.05
        
        # Loans to banks <6m: 10%
        rsf_bank_loans = loans_to_banks * 0.10
        
        # Performing loans: 65%
        rsf_loans = performing_loans * 0.65
        
        # Mortgages (risk weight <35%): 65%
        rsf_mortgages = mortgages * 0.65
        
        # Other assets: 100%
        rsf_other = other_assets * 1.0
        
        # Off-balance sheet: 5%
        rsf_obs = off_balance_sheet * 0.05
        
        total_rsf = (
            rsf_cash 
            + rsf_govt 
            + rsf_bank_loans 
            + rsf_loans 
            + rsf_mortgages 
            + rsf_other 
            + rsf_obs
        )
        
        # NSFR
        nsfr = total_asf / max(total_rsf, 1e-10)
        
        meets_minimum = nsfr >= self.config.nsfr_minimum
        surplus_deficit = total_asf - total_rsf * self.config.nsfr_minimum
        
        return NSFRMetrics(
            tier1_capital=float(tier1_capital),
            tier2_capital=float(tier2_capital),
            stable_deposits=float(stable_deposits),
            less_stable_deposits=float(less_stable_deposits),
            wholesale_funding_1yr=float(asf_wholesale),
            total_asf=float(total_asf),
            cash=float(rsf_cash),
            unencumbered_l1=float(rsf_govt),
            loans_to_banks=float(rsf_bank_loans),
            performing_loans=float(rsf_loans),
            mortgages=float(rsf_mortgages),
            other_assets=float(rsf_other),
            off_balance_sheet=float(rsf_obs),
            total_rsf=float(total_rsf),
            nsfr=float(nsfr),
            meets_minimum=meets_minimum,
            surplus_deficit=float(surplus_deficit),
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def run_stress_test(
        self,
        initial_liquidity: float,
        daily_inflows: np.ndarray,
        daily_outflows: np.ndarray,
        scenario: StressScenario = StressScenario.MODERATE,
        horizon_days: int = 90,
    ) -> StressTestResult:
        """
        Run liquidity stress test scenario.
        
        Args:
            initial_liquidity: Starting liquidity buffer
            daily_inflows: Baseline daily inflows
            daily_outflows: Baseline daily outflows
            scenario: Stress scenario to apply
            horizon_days: Stress test horizon in days
        
        Returns:
            Stress test results
        """
        # Stress multipliers by scenario
        multipliers = {
            StressScenario.BASELINE: (1.0, 1.0),
            StressScenario.MODERATE: (0.8, 1.2),  # inflows down 20%, outflows up 20%
            StressScenario.SEVERE: (0.5, 1.5),    # inflows down 50%, outflows up 50%
            StressScenario.SYSTEMIC: (0.2, 2.0),  # inflows down 80%, outflows double
        }
        
        inflow_mult, outflow_mult = multipliers[scenario]
        
        # Extend arrays if needed
        n = len(daily_inflows)
        if n < horizon_days:
            # Repeat pattern
            daily_inflows = np.tile(daily_inflows, int(np.ceil(horizon_days / n)))[:horizon_days]
            daily_outflows = np.tile(daily_outflows, int(np.ceil(horizon_days / n)))[:horizon_days]
        else:
            daily_inflows = daily_inflows[:horizon_days]
            daily_outflows = daily_outflows[:horizon_days]
        
        # Apply stress
        stressed_inflows = daily_inflows * inflow_mult
        stressed_outflows = daily_outflows * outflow_mult
        
        # Compute daily net liquidity
        daily_net = stressed_inflows - stressed_outflows
        
        # Cumulative position
        cumulative = np.zeros(horizon_days)
        cumulative[0] = initial_liquidity + daily_net[0]
        for t in range(1, horizon_days):
            cumulative[t] = cumulative[t - 1] + daily_net[t]
        
        # Minimum liquidity and day
        min_liquidity = float(np.min(cumulative))
        min_day = int(np.argmin(cumulative))
        
        # Survival horizon (days until liquidity exhausted)
        negative_days = np.where(cumulative < 0)[0]
        if len(negative_days) > 0:
            survival_days = int(negative_days[0])
            survives = False
        else:
            survival_days = horizon_days
            survives = True
        
        # Required buffer
        required_buffer = abs(min_liquidity) if min_liquidity < 0 else 0.0
        buffer_adequate = initial_liquidity >= required_buffer
        
        return StressTestResult(
            scenario=scenario,
            retail_outflow_rate=float(1 - inflow_mult),
            wholesale_outflow_rate=float(outflow_mult - 1),
            daily_net_liquidity=daily_net.tolist(),
            cumulative_net_position=cumulative.tolist(),
            minimum_liquidity=min_liquidity,
            minimum_day=min_day,
            survival_days=survival_days,
            survives_horizon=survives,
            required_buffer=float(required_buffer),
            current_buffer=float(initial_liquidity),
            buffer_adequacy=buffer_adequate,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_funding_concentration(
        self,
        funding_sources: dict[str, float],
        source_types: dict[str, str],
    ) -> FundingConcentration:
        """
        Analyze funding concentration risk.
        
        Args:
            funding_sources: Dict of source_name -> amount
            source_types: Dict of source_name -> type (retail, wholesale, etc.)
        
        Returns:
            Funding concentration analysis
        """
        total_funding = sum(funding_sources.values())
        if total_funding <= 0:
            return FundingConcentration()
        
        # Sort by size
        sorted_sources = sorted(funding_sources.items(), key=lambda x: -x[1])
        
        # Top counterparty concentration
        shares = [amt / total_funding for _, amt in sorted_sources]
        
        top_5_share = sum(shares[:5]) if len(shares) >= 5 else sum(shares)
        top_10_share = sum(shares[:10]) if len(shares) >= 10 else sum(shares)
        largest_single = shares[0] if shares else 0.0
        
        # By type
        type_totals = {}
        for name, amount in funding_sources.items():
            t = source_types.get(name, "other")
            type_totals[t] = type_totals.get(t, 0) + amount
        
        retail_share = type_totals.get("retail", 0) / total_funding
        wholesale_share = type_totals.get("wholesale", 0) / total_funding
        interbank_share = type_totals.get("interbank", 0) / total_funding
        capital_markets_share = type_totals.get("capital_markets", 0) / total_funding
        
        # Herfindahl index
        hhi = sum(s ** 2 for s in shares)
        
        # Risk classification
        if hhi > 0.25 or largest_single > 0.20:
            concentration_level = "High"
        elif hhi > 0.10 or largest_single > 0.10:
            concentration_level = "Medium"
        else:
            concentration_level = "Low"
        
        return FundingConcentration(
            top_5_funding_share=float(top_5_share),
            top_10_funding_share=float(top_10_share),
            largest_single_source=float(largest_single),
            retail_share=float(retail_share),
            wholesale_share=float(wholesale_share),
            interbank_share=float(interbank_share),
            capital_markets_share=float(capital_markets_share),
            herfindahl_index=float(hhi),
            concentration_risk_level=concentration_level,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def assess_liquidity_risk(
        self,
        hqla: HQLAPortfolio,
        deposits: dict[str, float],
        funding_sources: dict[str, float],
        cash_flows: list[CashFlowBucket],
        *,
        run_stress_tests: bool = True,
    ) -> LiquidityRiskMetrics:
        """
        Comprehensive liquidity risk assessment.
        
        Args:
            hqla: HQLA portfolio
            deposits: Deposit breakdown (retail, wholesale, etc.)
            funding_sources: All funding sources with amounts
            cash_flows: Cash flow buckets for gap analysis
            run_stress_tests: Whether to run stress scenarios
        
        Returns:
            Complete liquidity risk assessment
        """
        # LCR
        lcr = self.compute_lcr(
            hqla=hqla,
            retail_deposits=deposits.get("retail", 0),
            wholesale_deposits=deposits.get("wholesale", 0),
            secured_funding=deposits.get("secured", 0),
            derivative_positions=deposits.get("derivatives", 0),
            committed_facilities=deposits.get("committed", 0),
            loan_inflows=deposits.get("loan_inflows", 0),
            secured_lending=deposits.get("secured_lending", 0),
        )
        
        # NSFR
        nsfr = self.compute_nsfr(
            tier1_capital=deposits.get("tier1_capital", 0),
            tier2_capital=deposits.get("tier2_capital", 0),
            retail_deposits=deposits.get("retail", 0),
            wholesale_funding=deposits.get("wholesale_1yr", 0),
            other_liabilities=deposits.get("other_liabilities", 0),
            cash_and_reserves=hqla.cash + hqla.central_bank_reserves,
            government_securities=hqla.sovereign_bonds + hqla.government_bonds,
            loans_to_banks=deposits.get("loans_to_banks", 0),
            performing_loans=deposits.get("performing_loans", 0),
            mortgages=deposits.get("mortgages", 0),
            other_assets=deposits.get("other_assets", 0),
            off_balance_sheet=deposits.get("off_balance_sheet", 0),
        )
        
        # Cash flow gap analysis
        cumulative_gap = 0.0
        for bucket in cash_flows:
            cumulative_gap += bucket.net_cash_flow
        
        # Funding concentration
        source_types = {k: "wholesale" if "bank" in k.lower() else "retail" for k in funding_sources}
        concentration = self.analyze_funding_concentration(funding_sources, source_types)
        
        # Stress tests
        stress_tests = {}
        if run_stress_tests and cash_flows:
            inflows = np.array([b.maturing_assets + b.loan_repayments for b in cash_flows])
            outflows = np.array([b.maturing_liabilities + b.deposit_withdrawals for b in cash_flows])
            initial_liquidity = hqla.compute_hqla()
            
            for scenario in StressScenario:
                stress_tests[scenario.name] = self.run_stress_test(
                    initial_liquidity, inflows, outflows, scenario,
                    horizon_days=self.config.stress_horizon_days,
                )
        
        # Overall assessment
        vulnerabilities = []
        
        if not lcr.meets_minimum:
            vulnerabilities.append(f"LCR below minimum: {lcr.lcr:.1%}")
        if not nsfr.meets_minimum:
            vulnerabilities.append(f"NSFR below minimum: {nsfr.nsfr:.1%}")
        if concentration.concentration_risk_level == "High":
            vulnerabilities.append("High funding concentration risk")
        if cumulative_gap < 0:
            vulnerabilities.append(f"Negative cumulative cash flow gap: {cumulative_gap:,.0f}")
        
        severe_stress = stress_tests.get("SEVERE")
        if severe_stress and not severe_stress.survives_horizon:
            vulnerabilities.append(f"Does not survive severe stress (day {severe_stress.survival_days})")
        
        if len(vulnerabilities) >= 3:
            overall_rating = "High Risk"
        elif len(vulnerabilities) >= 1:
            overall_rating = "Medium Risk"
        else:
            overall_rating = "Low Risk"
        
        return LiquidityRiskMetrics(
            lcr=lcr,
            nsfr=nsfr,
            cash_flow_gaps=cash_flows,
            cumulative_gap=float(cumulative_gap),
            stress_tests=stress_tests,
            funding_concentration=concentration,
            overall_risk_rating=overall_rating,
            key_vulnerabilities=vulnerabilities,
        )
