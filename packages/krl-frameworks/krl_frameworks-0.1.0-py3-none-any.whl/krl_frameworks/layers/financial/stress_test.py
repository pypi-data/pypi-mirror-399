# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Stress Testing Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Regulatory Stress Testing Framework.

Implements CCAR and DFAST stress testing methodologies:
- Capital adequacy under stress
- Pre-Provision Net Revenue (PPNR) projections
- Credit loss estimation
- Operational risk scenarios
- Liquidity stress testing

References:
    - Federal Reserve CCAR/DFAST Instructions
    - Basel Committee on Banking Supervision: Stress Testing Principles
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np
import pandas as pd

from krl_frameworks.core import (
    BaseMetaFramework,
    CohortStateVector,
    DataBundle,
    FrameworkConfig,
    FrameworkMetadata,
    Tier,
    VerticalLayer,
    requires_tier,
)
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.core.state import StateTrajectory
from krl_frameworks.simulation import TransitionFunction


# ════════════════════════════════════════════════════════════════════════════════
# Stress Testing Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class StressScenario(Enum):
    """Federal Reserve stress scenarios."""
    BASELINE = "Baseline"
    ADVERSE = "Adverse"
    SEVERELY_ADVERSE = "Severely Adverse"
    GLOBAL_MARKET_SHOCK = "Global Market Shock"
    COUNTERPARTY_DEFAULT = "Counterparty Default"


class StressTestType(Enum):
    """Type of stress test."""
    CCAR = "Comprehensive Capital Analysis and Review"
    DFAST = "Dodd-Frank Act Stress Testing"
    ILST = "Internal Liquidity Stress Test"
    ICAAP = "Internal Capital Adequacy Assessment"


@dataclass
class MacroScenario:
    """Macroeconomic scenario variables."""
    
    # GDP
    real_gdp_growth: list[float] = field(default_factory=list)
    
    # Unemployment
    unemployment_rate: list[float] = field(default_factory=list)
    
    # Interest rates
    fed_funds_rate: list[float] = field(default_factory=list)
    ten_year_treasury: list[float] = field(default_factory=list)
    
    # Housing
    house_price_index: list[float] = field(default_factory=list)
    
    # Equity
    dow_jones: list[float] = field(default_factory=list)
    vix: list[float] = field(default_factory=list)
    
    # Commercial real estate
    cre_price_index: list[float] = field(default_factory=list)
    
    @classmethod
    def severely_adverse(cls, quarters: int = 9) -> "MacroScenario":
        """Create severely adverse scenario (2008-like crisis)."""
        return cls(
            real_gdp_growth=[-6.0, -8.0, -7.5, -4.0, -2.0, 0.0, 1.5, 2.0, 2.5][:quarters],
            unemployment_rate=[5.5, 7.0, 8.5, 9.5, 10.0, 10.0, 9.5, 9.0, 8.5][:quarters],
            fed_funds_rate=[3.0, 2.0, 1.0, 0.5, 0.25, 0.25, 0.25, 0.25, 0.25][:quarters],
            ten_year_treasury=[3.0, 2.5, 2.0, 1.5, 1.0, 1.5, 2.0, 2.5, 2.5][:quarters],
            house_price_index=[0, -5, -12, -18, -22, -25, -24, -22, -20][:quarters],
            dow_jones=[0, -15, -30, -40, -45, -40, -35, -30, -25][:quarters],
            vix=[20, 40, 65, 80, 70, 55, 40, 35, 30][:quarters],
            cre_price_index=[0, -8, -18, -28, -35, -38, -35, -32, -28][:quarters],
        )


@dataclass
class StressTestConfig:
    """Configuration for stress testing."""
    
    # Test parameters
    test_type: StressTestType = StressTestType.DFAST
    horizon_quarters: int = 9
    
    # Scenarios to run
    scenarios: list[StressScenario] = field(default_factory=lambda: [
        StressScenario.BASELINE,
        StressScenario.ADVERSE,
        StressScenario.SEVERELY_ADVERSE,
    ])
    
    # Capital floors
    cet1_floor: float = 0.045  # 4.5% CET1 minimum
    tier1_floor: float = 0.06  # 6% Tier 1 minimum
    total_capital_floor: float = 0.08  # 8% Total Capital minimum
    
    # Stress capital buffer
    scb_floor: float = 0.025  # 2.5% minimum SCB
    
    # GSIB surcharge (if applicable)
    gsib_surcharge: float = 0.0


@dataclass
class PPNRProjection:
    """Pre-Provision Net Revenue projection."""
    
    # Revenue
    net_interest_income: float = 0.0
    noninterest_income: float = 0.0
    total_revenue: float = 0.0
    
    # Expenses
    compensation: float = 0.0
    other_expense: float = 0.0
    total_expense: float = 0.0
    
    # PPNR
    ppnr: float = 0.0
    ppnr_as_pct_assets: float = 0.0


@dataclass
class StressLosses:
    """Projected losses under stress."""
    
    # Credit losses by portfolio
    first_lien_residential: float = 0.0
    junior_lien_residential: float = 0.0
    credit_card: float = 0.0
    commercial_industrial: float = 0.0
    commercial_real_estate: float = 0.0
    other_consumer: float = 0.0
    other_loans: float = 0.0
    
    # Total credit losses
    total_loan_losses: float = 0.0
    loss_rate: float = 0.0
    
    # Other losses
    securities_losses: float = 0.0
    trading_losses: float = 0.0
    operational_losses: float = 0.0
    
    # Total
    total_losses: float = 0.0


@dataclass
class CapitalPath:
    """Capital ratio path through stress."""
    
    quarters: list[int] = field(default_factory=list)
    
    # Capital levels
    cet1_capital: list[float] = field(default_factory=list)
    tier1_capital: list[float] = field(default_factory=list)
    total_capital: list[float] = field(default_factory=list)
    
    # Capital ratios
    cet1_ratio: list[float] = field(default_factory=list)
    tier1_ratio: list[float] = field(default_factory=list)
    total_ratio: list[float] = field(default_factory=list)
    leverage_ratio: list[float] = field(default_factory=list)
    
    # Minimums
    cet1_minimum: float = 0.0
    tier1_minimum: float = 0.0
    total_minimum: float = 0.0
    leverage_minimum: float = 0.0
    
    # Buffer
    capital_buffer: float = 0.0
    scb_requirement: float = 0.0


@dataclass
class StressTestResult:
    """Single scenario stress test result."""
    
    scenario: StressScenario = StressScenario.BASELINE
    
    # Projections
    ppnr: list[PPNRProjection] = field(default_factory=list)
    losses: StressLosses = field(default_factory=StressLosses)
    capital_path: CapitalPath = field(default_factory=CapitalPath)
    
    # Pass/fail
    passes_minimum_requirements: bool = True
    binding_constraint: str = ""
    capital_shortfall: float = 0.0


@dataclass
class StressTestMetrics:
    """Comprehensive stress test metrics."""
    
    # Results by scenario
    results: dict[StressScenario, StressTestResult] = field(default_factory=dict)
    
    # Summary
    worst_case_cet1: float = 0.0
    worst_case_scenario: StressScenario = StressScenario.BASELINE
    
    # Capital planning
    max_distributable_amount: float = 0.0
    recommended_capital_buffer: float = 0.0
    
    # Overall assessment
    overall_pass: bool = True
    risk_rating: str = "Low"


# ════════════════════════════════════════════════════════════════════════════════
# Stress Test Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class StressTransition(TransitionFunction):
    """
    Stress test transition function.
    
    Models capital evolution under stress scenarios.
    """
    
    def __init__(self, scenario: MacroScenario, config: StressTestConfig):
        self.scenario = scenario
        self.config = config
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply stress scenario transition."""
        params = params or {}
        
        # Get scenario values for this quarter
        quarter = min(t, len(self.scenario.unemployment_rate) - 1)
        unemployment = self.scenario.unemployment_rate[quarter] / 100
        gdp = self.scenario.real_gdp_growth[quarter] / 100
        hpi_change = self.scenario.house_price_index[quarter] / 100 if self.scenario.house_price_index else 0
        
        # Employment impact
        employment_shock = -max(0, unemployment - 0.05) * 2
        new_employment = np.clip(
            state.employment_prob + employment_shock,
            0.1, 0.99
        )
        
        # Credit stress increases with unemployment
        credit_stress = max(0, unemployment - 0.05) * 1.5
        new_health_burden = np.clip(
            state.health_burden_score + credit_stress,
            0.0, 0.95
        )
        
        # Housing impact
        housing_impact = hpi_change * 0.5
        new_housing = np.clip(
            state.housing_cost_ratio + housing_impact,
            0.1, 0.8
        )
        
        # Portfolio quality deteriorates under stress
        quality_impact = gdp * 0.3
        new_opportunity = np.clip(
            state.opportunity_score + quality_impact,
            0.0, 1.0
        )
        
        # Capital depletes from losses
        loss_rate = credit_stress * 0.05  # Simplified loss model
        new_output = state.sector_output * (1 - loss_rate)
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=new_health_burden,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=new_housing,
            opportunity_score=new_opportunity,
            sector_output=new_output,
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Stress Testing Framework
# ════════════════════════════════════════════════════════════════════════════════


class StressTestFramework(BaseMetaFramework):
    """
    Regulatory Stress Testing Framework.
    
    Implements comprehensive bank stress testing:
    
    1. CCAR/DFAST Compliance: Federal Reserve stress test methodology
    2. Multi-Scenario: Baseline, Adverse, Severely Adverse
    3. Capital Adequacy: CET1, Tier 1, Total Capital, Leverage
    4. PPNR Modeling: Pre-provision net revenue projections
    5. Loss Estimation: Credit, market, and operational losses
    
    Tier: ENTERPRISE (bank regulatory compliance)
    
    Example:
        >>> stress_test = StressTestFramework()
        >>> bundle = DataBundle.from_dataframes({
        ...     "balance_sheet": bs_df,
        ...     "loan_portfolio": loans_df,
        ...     "capital": capital_df
        ... })
        >>> results = stress_test.run_dfast(bundle)
        >>> print(f"Min CET1: {results.worst_case_cet1:.2%}")
        >>> print(f"Passes: {results.overall_pass}")
    """
    
    METADATA = FrameworkMetadata(
        slug="stress_test",
        name="Regulatory Stress Testing Framework",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.ENTERPRISE,
        description="CCAR/DFAST bank stress testing and capital adequacy analysis",
        required_domains=["balance_sheet", "capital"],
        output_domains=["stressed_capital", "loss_projections", "capital_trajectory"],
        constituent_models=["scenario_generator", "loss_projector", "capital_simulator", "ratio_forecaster"],
        tags=["financial", "stress_test", "ccar", "dfast", "regulatory", "banking"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self, config: Optional[StressTestConfig] = None):
        super().__init__()
        self.stress_config = config or StressTestConfig()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from bank data."""
        bs_data = bundle.get("balance_sheet")
        capital_data = bundle.get("capital")
        
        bs_df = bs_data.data
        capital_df = capital_data.data
        
        n_cohorts = max(1, len(bs_df))
        
        # Extract total assets
        if "total_assets" in bs_df.columns:
            assets = bs_df["total_assets"].values[:n_cohorts]
        else:
            assets = np.full(n_cohorts, 1e10)
        
        # Extract capital ratios
        if "cet1_ratio" in capital_df.columns:
            cet1 = capital_df["cet1_ratio"].values[0] if len(capital_df) > 0 else 0.12
        else:
            cet1 = 0.12
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.95),  # Economic health
            health_burden_score=np.full(n_cohorts, 0.05),  # Credit stress
            credit_access_prob=np.full(n_cohorts, cet1),  # CET1 ratio proxy
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.full(n_cohorts, 0.8),  # Portfolio quality
            sector_output=assets.reshape(-1, 1).repeat(9, axis=1) / 9,  # Assets
            deprivation_vector=np.zeros((n_cohorts, 6)),
            step=0,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply stress transition."""
        scenario = MacroScenario.severely_adverse()
        transition = StressTransition(scenario, self.stress_config)
        return transition(state, t, config)
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> StressTestMetrics:
        """Compute stress test metrics."""
        metrics = StressTestMetrics()
        
        if len(trajectory) < 1:
            return metrics
        
        initial_state = trajectory.initial_state
        
        # Run through scenarios
        for scenario in self.stress_config.scenarios:
            result = self._run_scenario(trajectory, scenario)
            metrics.results[scenario] = result
            
            # Track worst case
            if result.capital_path.cet1_minimum < metrics.worst_case_cet1 or metrics.worst_case_cet1 == 0:
                metrics.worst_case_cet1 = result.capital_path.cet1_minimum
                metrics.worst_case_scenario = scenario
            
            if not result.passes_minimum_requirements:
                metrics.overall_pass = False
        
        # Calculate distributable amount (simplified)
        if metrics.overall_pass:
            buffer = metrics.worst_case_cet1 - self.stress_config.cet1_floor
            metrics.max_distributable_amount = max(0, buffer * float(initial_state.sector_output.sum()))
        
        # Risk rating
        if metrics.worst_case_cet1 >= 0.10:
            metrics.risk_rating = "Low"
        elif metrics.worst_case_cet1 >= 0.07:
            metrics.risk_rating = "Moderate"
        elif metrics.worst_case_cet1 >= 0.045:
            metrics.risk_rating = "High"
        else:
            metrics.risk_rating = "Critical"
        
        # Recommended buffer
        metrics.recommended_capital_buffer = max(
            self.stress_config.scb_floor,
            0.12 - metrics.worst_case_cet1
        )
        
        return metrics
    
    def _run_scenario(
        self,
        trajectory: StateTrajectory,
        scenario: StressScenario,
    ) -> StressTestResult:
        """Run a single stress scenario."""
        result = StressTestResult(scenario=scenario)
        
        # Get multipliers for scenario severity
        severity = {
            StressScenario.BASELINE: 1.0,
            StressScenario.ADVERSE: 1.5,
            StressScenario.SEVERELY_ADVERSE: 2.5,
            StressScenario.GLOBAL_MARKET_SHOCK: 3.0,
            StressScenario.COUNTERPARTY_DEFAULT: 2.8,
        }.get(scenario, 1.0)
        
        initial_state = trajectory.initial_state
        
        # Starting capital (simplified - using credit_access_prob as CET1 proxy)
        starting_cet1 = float(initial_state.credit_access_prob.mean())
        total_assets = float(initial_state.sector_output.sum())
        
        # Project capital path
        quarters = list(range(self.stress_config.horizon_quarters))
        cet1_path = []
        
        base_loss_rate = 0.01 * severity  # Base quarterly loss rate
        
        for q in quarters:
            # Losses increase then decrease (peak in quarter 3-5)
            loss_multiplier = 1 + 0.5 * np.sin(np.pi * q / self.stress_config.horizon_quarters)
            quarterly_loss = base_loss_rate * loss_multiplier
            
            # PPNR partially offsets losses
            ppnr_offset = 0.005  # 0.5% PPNR per quarter
            
            net_impact = quarterly_loss - ppnr_offset
            
            if q == 0:
                cet1 = starting_cet1 - net_impact
            else:
                cet1 = cet1_path[-1] - net_impact
            
            cet1_path.append(max(0, cet1))
        
        # Capital path
        result.capital_path = CapitalPath(
            quarters=quarters,
            cet1_ratio=cet1_path,
            tier1_ratio=[c + 0.01 for c in cet1_path],  # T1 = CET1 + 1%
            total_ratio=[c + 0.02 for c in cet1_path],  # Total = CET1 + 2%
            cet1_minimum=min(cet1_path),
            tier1_minimum=min(cet1_path) + 0.01,
            total_minimum=min(cet1_path) + 0.02,
            scb_requirement=max(self.stress_config.scb_floor, starting_cet1 - min(cet1_path)),
        )
        
        # Losses
        total_loan_losses = base_loss_rate * severity * self.stress_config.horizon_quarters * total_assets
        result.losses = StressLosses(
            first_lien_residential=total_loan_losses * 0.25,
            commercial_real_estate=total_loan_losses * 0.30,
            commercial_industrial=total_loan_losses * 0.20,
            credit_card=total_loan_losses * 0.15,
            other_loans=total_loan_losses * 0.10,
            total_loan_losses=total_loan_losses,
            loss_rate=base_loss_rate * severity * self.stress_config.horizon_quarters,
            trading_losses=total_loan_losses * 0.1 if scenario == StressScenario.GLOBAL_MARKET_SHOCK else 0,
        )
        result.losses.total_losses = result.losses.total_loan_losses + result.losses.trading_losses
        
        # Check if passes
        result.passes_minimum_requirements = (
            result.capital_path.cet1_minimum >= self.stress_config.cet1_floor
        )
        
        if not result.passes_minimum_requirements:
            result.binding_constraint = "CET1 Ratio"
            result.capital_shortfall = self.stress_config.cet1_floor - result.capital_path.cet1_minimum
        
        return result
    
    @requires_tier(Tier.ENTERPRISE)
    def run_dfast(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> StressTestMetrics:
        """
        Run DFAST stress test.
        
        Args:
            bundle: DataBundle with balance_sheet and capital data
            config: Optional framework configuration
        
        Returns:
            StressTestMetrics with all scenario results
        """
        config = config or FrameworkConfig()
        
        initial_state = self._compute_initial_state(bundle, config)
        trajectory = StateTrajectory(states=[initial_state])
        
        # Project through horizon
        current = initial_state
        for t in range(self.stress_config.horizon_quarters):
            current = self._transition(current, t, config)
            trajectory.append(current)
        
        return self._compute_metrics(trajectory)
    
    @requires_tier(Tier.ENTERPRISE)
    def run_ccar(
        self,
        bundle: DataBundle,
        capital_actions: Optional[dict[str, float]] = None,
        config: Optional[FrameworkConfig] = None,
    ) -> StressTestMetrics:
        """
        Run CCAR stress test with capital actions.
        
        Args:
            bundle: DataBundle with bank data
            capital_actions: Planned dividends, buybacks, etc.
            config: Optional framework configuration
        
        Returns:
            StressTestMetrics including capital action impact
        """
        # Run base DFAST first
        metrics = self.run_dfast(bundle, config)
        
        # Apply capital actions impact
        if capital_actions:
            dividends = capital_actions.get("dividends", 0)
            buybacks = capital_actions.get("buybacks", 0)
            
            total_distribution = dividends + buybacks
            
            # Adjust worst case for distributions
            metrics.worst_case_cet1 -= total_distribution / 1e10  # Simplified
            
            # Re-evaluate pass/fail
            metrics.overall_pass = metrics.worst_case_cet1 >= self.stress_config.cet1_floor
        
        return metrics
    
    @requires_tier(Tier.ENTERPRISE)
    def calculate_scb(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> float:
        """
        Calculate Stress Capital Buffer requirement.
        
        Args:
            bundle: DataBundle with bank data
            config: Optional framework configuration
        
        Returns:
            Stress Capital Buffer as decimal (e.g., 0.025 = 2.5%)
        """
        metrics = self.run_dfast(bundle, config)
        
        # SCB = Starting CET1 - Minimum CET1 in stress
        initial_state = self._compute_initial_state(bundle, config or FrameworkConfig())
        starting_cet1 = float(initial_state.credit_access_prob.mean())
        
        scb = starting_cet1 - metrics.worst_case_cet1
        
        # Floor at 2.5%
        return max(self.stress_config.scb_floor, scb)

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Stress Test dashboard specification."""
        return FrameworkDashboardSpec(
            slug="stress_test",
            name="Regulatory Stress Testing",
            description=(
                "CCAR/DFAST bank stress testing and capital adequacy analysis "
                "under baseline, adverse, and severely adverse scenarios."
            ),
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "test_type": {
                        "type": "string",
                        "title": "Test Type",
                        "enum": ["dfast", "ccar", "ilst", "icaap"],
                        "default": "dfast",
                        "x-ui-widget": "select",
                        "x-ui-group": "test",
                        "x-ui-help": "DFAST: Dodd-Frank, CCAR: Comprehensive Capital Analysis and Review",
                    },
                    "scenarios": {
                        "type": "array",
                        "title": "Scenarios",
                        "items": {"type": "string", "enum": ["baseline", "adverse", "severely_adverse", "global_market_shock", "counterparty_default"]},
                        "default": ["baseline", "adverse", "severely_adverse"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "test",
                    },
                    "horizon_quarters": {
                        "type": "integer",
                        "title": "Horizon (quarters)",
                        "minimum": 4,
                        "maximum": 12,
                        "default": 9,
                        "x-ui-widget": "slider",
                        "x-ui-group": "test",
                    },
                    "cet1_floor": {
                        "type": "number",
                        "title": "CET1 Floor",
                        "minimum": 0.04,
                        "maximum": 0.07,
                        "default": 0.045,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-format": ".1%",
                        "x-ui-group": "floors",
                    },
                    "scb_floor": {
                        "type": "number",
                        "title": "SCB Floor",
                        "minimum": 0.025,
                        "maximum": 0.05,
                        "default": 0.025,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-format": ".1%",
                        "x-ui-group": "floors",
                    },
                    "gsib_surcharge": {
                        "type": "number",
                        "title": "G-SIB Surcharge",
                        "minimum": 0,
                        "maximum": 0.035,
                        "default": 0,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-format": ".1%",
                        "x-ui-group": "floors",
                    },
                },
            },
            default_parameters={
                "test_type": "dfast",
                "scenarios": ["baseline", "adverse", "severely_adverse"],
                "horizon_quarters": 9,
                "cet1_floor": 0.045,
                "scb_floor": 0.025,
                "gsib_surcharge": 0,
            },
            parameter_groups=[
                ParameterGroupSpec(key="test", title="Test Configuration", parameters=["test_type", "scenarios", "horizon_quarters"]),
                ParameterGroupSpec(key="floors", title="Capital Floors", parameters=["cet1_floor", "scb_floor", "gsib_surcharge"]),
            ],
            required_domains=["balance_sheet", "capital"],
            min_tier=Tier.ENTERPRISE,
            output_views=[
                OutputViewSpec(
                    key="pass_fail",
                    title="Pass/Fail",
                    view_type=ViewType.METRIC_GRID,
                    config={"metrics": [
                        {"key": "overall_pass", "label": "Overall", "format": "boolean"},
                        {"key": "worst_case_cet1", "label": "Worst CET1", "format": ".1%"},
                        {"key": "scb", "label": "Stress Capital Buffer", "format": ".1%"},
                    ]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="pass_fail_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="capital_trajectory",
                    title="Capital Trajectory",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "quarter", "y_fields": ["baseline", "adverse", "severely_adverse"], "y_label": "CET1 Ratio"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="capital_trajectory_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="losses_by_portfolio",
                    title="Losses by Portfolio",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "portfolio", "y_field": "cumulative_loss", "color_field": "scenario"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="losses_by_portfolio_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="ppnr",
                    title="PPNR Projection",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "quarter", "y_fields": ["net_interest_income", "noninterest_income", "expense", "ppnr"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="ppnr_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="macro_scenario",
                    title="Macro Scenario",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "quarter", "y_fields": ["gdp_growth", "unemployment", "house_price_index"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="macro_scenario_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "StressTestFramework",
    "StressTestConfig",
    "StressTestMetrics",
    "StressTestResult",
    "StressScenario",
    "StressTestType",
    "MacroScenario",
    "PPNRProjection",
    "StressLosses",
    "CapitalPath",
    "StressTransition",
]
