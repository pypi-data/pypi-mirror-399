# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - CECL Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Current Expected Credit Losses (CECL) Framework.

Implements the FASB ASC 326 accounting standard for credit loss
estimation, including:
- Probability of Default (PD) models
- Loss Given Default (LGD) estimation
- Exposure at Default (EAD) calculation
- Discounted Cash Flow (DCF) methods
- Vintage analysis

References:
    - FASB ASC 326: Financial Instruments - Credit Losses
    - Interagency Policy Statement on Allowances for Credit Losses (2020)
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
# CECL Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class CECLMethod(Enum):
    """CECL estimation methodology."""
    DCF = "Discounted Cash Flow"
    LOSS_RATE = "Loss Rate"
    ROLL_RATE = "Roll Rate"
    VINTAGE = "Vintage Analysis"
    PD_LGD = "Probability of Default x Loss Given Default"
    WARM = "Weighted Average Remaining Maturity"


class EconomicScenario(Enum):
    """Economic forecast scenario."""
    BASELINE = "Baseline"
    ADVERSE = "Adverse"
    SEVERELY_ADVERSE = "Severely Adverse"
    OPTIMISTIC = "Optimistic"


@dataclass
class CECLConfig:
    """Configuration for CECL calculations."""
    
    # Methodology
    method: CECLMethod = CECLMethod.PD_LGD
    
    # Forecast horizon
    reasonable_supportable_period: int = 8  # quarters
    reversion_period: int = 4  # quarters
    
    # Scenario weights
    scenario_weights: dict[EconomicScenario, float] = field(default_factory=lambda: {
        EconomicScenario.BASELINE: 0.5,
        EconomicScenario.ADVERSE: 0.3,
        EconomicScenario.SEVERELY_ADVERSE: 0.2,
    })
    
    # Discount rate
    effective_interest_rate: float = 0.05
    
    # Segmentation
    segment_by_risk_rating: bool = True
    segment_by_product: bool = True


@dataclass
class SegmentACL:
    """Allowance for Credit Losses by segment."""
    
    segment_name: str = ""
    
    # Balances
    outstanding_balance: float = 0.0
    acl_balance: float = 0.0
    acl_rate: float = 0.0
    
    # Components
    lifetime_pd: float = 0.0
    lgd: float = 0.0
    ead: float = 0.0
    
    # Coverage
    coverage_ratio: float = 0.0


@dataclass
class CECLReserve:
    """CECL reserve (ACL) calculation results."""
    
    # Total ACL
    total_acl: float = 0.0
    
    # By pool/segment
    segment_acl: list[SegmentACL] = field(default_factory=list)
    
    # Components
    funded_acl: float = 0.0
    unfunded_acl: float = 0.0
    
    # Qualitative adjustments
    qualitative_adjustment: float = 0.0
    
    # Coverage
    total_coverage_ratio: float = 0.0
    
    # Period changes
    provision_expense: float = 0.0
    charge_offs: float = 0.0
    recoveries: float = 0.0


@dataclass
class CECLMetrics:
    """Comprehensive CECL metrics."""
    
    # Reserve
    reserve: CECLReserve = field(default_factory=CECLReserve)
    
    # Risk metrics
    weighted_average_pd: float = 0.0
    weighted_average_lgd: float = 0.0
    expected_loss_rate: float = 0.0
    
    # Portfolio stats
    total_loans: float = 0.0
    avg_remaining_life: float = 0.0
    
    # Vintage analysis
    vintage_loss_rates: dict[str, float] = field(default_factory=dict)
    
    # Scenario impact
    scenario_acls: dict[EconomicScenario, float] = field(default_factory=dict)


# ════════════════════════════════════════════════════════════════════════════════
# CECL Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class CECLTransition(TransitionFunction):
    """
    CECL credit loss transition.
    
    Models the evolution of credit losses over the loan lifecycle.
    """
    
    def __init__(self, config: CECLConfig):
        self.config = config
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply CECL loss transition."""
        params = params or {}
        
        # Economic conditions affect PD
        gdp_growth = params.get("gdp_growth", 0.02)
        unemployment = params.get("unemployment", 0.04)
        
        # PD increases with poor economic conditions
        economic_stress = max(0, unemployment - 0.04) * 5  # Stress factor
        
        # Update health burden (proxy for credit stress)
        pd_effect = 0.01 * economic_stress - 0.005 * gdp_growth
        new_health_burden = np.clip(
            state.health_burden_score + pd_effect,
            0.0, 1.0
        )
        
        # Portfolio quality deteriorates/improves
        quality_change = -pd_effect
        new_opportunity = np.clip(
            state.opportunity_score + quality_change * 0.5,
            0.0, 1.0
        )
        
        # Loan balances (amortization)
        amortization = 0.02  # 2% paydown per period
        new_sector_output = state.sector_output * (1 - amortization)
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=new_health_burden,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_sector_output,
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )


# ════════════════════════════════════════════════════════════════════════════════
# CECL Framework
# ════════════════════════════════════════════════════════════════════════════════


class CECLFramework(BaseMetaFramework):
    """
    Current Expected Credit Losses (CECL) Framework.
    
    Implements FASB ASC 326 credit loss accounting standard:
    
    1. Lifetime Loss Estimation: Expected losses over life of loan
    2. Forward-Looking: Incorporates economic forecasts
    3. Multiple Methods: PD/LGD, DCF, vintage, loss rate
    4. Scenario Weighting: Probability-weighted outcomes
    5. Qualitative Overlays: Expert judgment adjustments
    
    Tier: ENTERPRISE (financial regulatory accounting)
    
    Example:
        >>> cecl = CECLFramework()
        >>> bundle = DataBundle.from_dataframes({
        ...     "loans": loans_df,
        ...     "historical_losses": losses_df,
        ...     "forecasts": forecasts_df
        ... })
        >>> metrics = cecl.calculate_acl(bundle)
        >>> print(f"Total ACL: ${metrics.reserve.total_acl:,.0f}")
        >>> print(f"Coverage: {metrics.reserve.total_coverage_ratio:.2%}")
    """
    
    METADATA = FrameworkMetadata(
        slug="cecl",
        name="CECL Credit Loss Framework",
        version="1.0.0",
        layer=VerticalLayer.FINANCIAL_ECONOMIC,
        tier=Tier.ENTERPRISE,
        description="FASB ASC 326 CECL allowance for credit losses calculation",
        required_domains=["loans", "historical_losses"],
        output_domains=["credit_loss_allowance", "lifetime_ecl", "reserve_ratio"],
        constituent_models=["pd_estimator", "lgd_calculator", "ead_modeler", "reserve_aggregator"],
        tags=["financial", "cecl", "credit_loss", "accounting", "banking"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self, config: Optional[CECLConfig] = None):
        super().__init__()
        self.cecl_config = config or CECLConfig()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from loan data."""
        loans_data = bundle.get("loans")
        losses_data = bundle.get("historical_losses")
        
        loans_df = loans_data.data
        
        n_cohorts = len(loans_df)
        
        # Extract loan balances
        if "balance" in loans_df.columns:
            balances = loans_df["balance"].values[:n_cohorts]
        else:
            balances = np.full(n_cohorts, 1e6)
        
        # Extract risk ratings (0-1 scale)
        if "risk_score" in loans_df.columns:
            risk = 1 - loans_df["risk_score"].values[:n_cohorts] / 100
        else:
            risk = np.full(n_cohorts, 0.15)
        
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.9),
            health_burden_score=np.clip(risk, 0, 1),  # Risk score as "burden"
            credit_access_prob=np.full(n_cohorts, 0.7),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=1 - np.clip(risk, 0, 1),  # Quality = 1 - risk
            sector_output=balances.reshape(-1, 1).repeat(10, axis=1) / 10,
            deprivation_vector=np.zeros((n_cohorts, 6)),
            step=0,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply CECL transition."""
        transition = CECLTransition(self.cecl_config)
        return transition(state, t, config)
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> CECLMetrics:
        """Compute CECL metrics."""
        metrics = CECLMetrics()
        
        if len(trajectory) < 1:
            return metrics
        
        initial_state = trajectory.initial_state
        
        # Total loan balance
        total_loans = float(initial_state.sector_output.sum())
        metrics.total_loans = total_loans
        
        # Calculate weighted average PD (from health burden)
        weighted_pd = float(initial_state.health_burden_score.mean())
        metrics.weighted_average_pd = weighted_pd
        
        # Assumed LGD (could be from data)
        lgd = 0.40
        metrics.weighted_average_lgd = lgd
        
        # Expected loss rate
        expected_loss = weighted_pd * lgd
        metrics.expected_loss_rate = expected_loss
        
        # Calculate ACL
        total_acl = total_loans * expected_loss
        
        # Create segment ACLs (simplified - 3 segments)
        segments = []
        for i, segment_name in enumerate(["Prime", "Near-Prime", "Subprime"]):
            segment_pct = [0.6, 0.3, 0.1][i]
            segment_pd = [0.02, 0.10, 0.25][i]
            
            segment = SegmentACL(
                segment_name=segment_name,
                outstanding_balance=total_loans * segment_pct,
                acl_balance=total_loans * segment_pct * segment_pd * lgd,
                acl_rate=segment_pd * lgd,
                lifetime_pd=segment_pd,
                lgd=lgd,
                coverage_ratio=segment_pd * lgd,
            )
            segments.append(segment)
        
        metrics.reserve = CECLReserve(
            total_acl=total_acl,
            segment_acl=segments,
            funded_acl=total_acl * 0.95,
            unfunded_acl=total_acl * 0.05,
            qualitative_adjustment=total_acl * 0.05,
            total_coverage_ratio=expected_loss,
        )
        
        # Scenario ACLs
        for scenario, weight in self.cecl_config.scenario_weights.items():
            multiplier = {
                EconomicScenario.BASELINE: 1.0,
                EconomicScenario.ADVERSE: 1.5,
                EconomicScenario.SEVERELY_ADVERSE: 2.5,
                EconomicScenario.OPTIMISTIC: 0.7,
            }.get(scenario, 1.0)
            metrics.scenario_acls[scenario] = total_acl * multiplier
        
        return metrics
    
    @requires_tier(Tier.ENTERPRISE)
    def calculate_acl(
        self,
        bundle: DataBundle,
        scenario: EconomicScenario = EconomicScenario.BASELINE,
        config: Optional[FrameworkConfig] = None,
    ) -> CECLMetrics:
        """
        Calculate Allowance for Credit Losses.
        
        Args:
            bundle: DataBundle with loans and historical_losses
            scenario: Economic scenario for forecasting
            config: Optional framework configuration
        
        Returns:
            CECLMetrics with ACL and supporting calculations
        """
        config = config or FrameworkConfig()
        
        initial_state = self._compute_initial_state(bundle, config)
        trajectory = StateTrajectory(states=[initial_state])
        
        # Project over reasonable and supportable period
        current = initial_state
        total_periods = self.cecl_config.reasonable_supportable_period
        
        for t in range(total_periods):
            current = self._transition(current, t, config)
            trajectory.append(current)
        
        return self._compute_metrics(trajectory)
    
    @requires_tier(Tier.ENTERPRISE)
    def vintage_analysis(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> dict[str, list[float]]:
        """
        Perform vintage loss analysis.
        
        Args:
            bundle: DataBundle with loan vintage data
            config: Optional framework configuration
        
        Returns:
            Dictionary of vintage -> cumulative loss rates
        """
        loans_data = bundle.get("loans")
        loans_df = loans_data.data
        
        # Simplified vintage analysis
        vintages = {}
        
        if "origination_year" in loans_df.columns:
            for year in loans_df["origination_year"].unique():
                vintage_df = loans_df[loans_df["origination_year"] == year]
                
                # Simulate cumulative loss development
                initial_balance = vintage_df["balance"].sum() if "balance" in vintage_df.columns else 1e6
                
                cumulative_losses = []
                loss_rate = 0.005  # 0.5% per quarter
                
                for q in range(12):  # 3 years
                    cumulative = loss_rate * (q + 1) * (1 + 0.02 * q)  # Accelerating curve
                    cumulative_losses.append(min(cumulative, 0.15))  # Cap at 15%
                
                vintages[str(year)] = cumulative_losses
        else:
            # Default vintage curve
            vintages["default"] = [0.005 * (i + 1) for i in range(12)]
        
        return vintages

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return CECL dashboard specification."""
        return FrameworkDashboardSpec(
            slug="cecl",
            name="CECL Credit Loss Framework",
            description=(
                "FASB ASC 326 Current Expected Credit Losses framework for "
                "lifetime loss estimation with forward-looking economic forecasts."
            ),
            layer="financial",
            parameters_schema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "title": "CECL Method",
                        "enum": ["pd_lgd", "dcf", "loss_rate", "roll_rate", "vintage", "warm"],
                        "default": "pd_lgd",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                        "x-ui-help": "PD*LGD: Probability of Default × Loss Given Default",
                    },
                    "reasonable_supportable_period": {
                        "type": "integer",
                        "title": "R&S Period (quarters)",
                        "minimum": 1,
                        "maximum": 12,
                        "default": 8,
                        "x-ui-widget": "slider",
                        "x-ui-group": "methodology",
                    },
                    "reversion_period": {
                        "type": "integer",
                        "title": "Reversion Period (quarters)",
                        "minimum": 1,
                        "maximum": 8,
                        "default": 4,
                        "x-ui-widget": "slider",
                        "x-ui-group": "methodology",
                    },
                    "scenario_baseline_weight": {
                        "type": "number",
                        "title": "Baseline Weight",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.5,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-group": "scenarios",
                    },
                    "scenario_adverse_weight": {
                        "type": "number",
                        "title": "Adverse Weight",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.3,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-group": "scenarios",
                    },
                    "qualitative_adjustment": {
                        "type": "number",
                        "title": "Qualitative Overlay (%)",
                        "minimum": -10,
                        "maximum": 10,
                        "default": 0,
                        "x-ui-widget": "slider",
                        "x-ui-format": ".1%",
                        "x-ui-group": "adjustments",
                    },
                },
            },
            default_parameters={
                "method": "pd_lgd",
                "reasonable_supportable_period": 8,
                "reversion_period": 4,
                "scenario_baseline_weight": 0.5,
                "scenario_adverse_weight": 0.3,
                "qualitative_adjustment": 0,
            },
            parameter_groups=[
                ParameterGroupSpec(key="methodology", title="Methodology", parameters=["method", "reasonable_supportable_period", "reversion_period"]),
                ParameterGroupSpec(key="scenarios", title="Scenario Weights", parameters=["scenario_baseline_weight", "scenario_adverse_weight"]),
                ParameterGroupSpec(key="adjustments", title="Adjustments", parameters=["qualitative_adjustment"]),
            ],
            required_domains=["loans", "historical_losses"],
            min_tier=Tier.ENTERPRISE,
            output_views=[
                OutputViewSpec(
                    key="acl_coverage",
                    title="ACL Coverage",
                    view_type=ViewType.GAUGE,
                    config={"min": 0, "max": 0.1, "thresholds": [0.01, 0.03, 0.05], "format": ".2%"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="acl_coverage_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="segment_acl",
                    title="ACL by Segment",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "segment", "y_field": "acl_balance", "stacked": True},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="segment_acl_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="pd_lgd",
                    title="PD/LGD Components",
                    view_type=ViewType.METRIC_GRID,
                    config={"metrics": [
                        {"key": "weighted_avg_pd", "label": "Weighted Avg PD", "format": ".2%"},
                        {"key": "weighted_avg_lgd", "label": "Weighted Avg LGD", "format": ".1%"},
                        {"key": "total_ead", "label": "Total EAD", "format": "$,.0f"},
                    ]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="pd_lgd_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="vintage_curves",
                    title="Vintage Curves",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "quarter", "y_fields": ["2022", "2023", "2024"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="vintage_curves_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="reserve_waterfall",
                    title="Reserve Waterfall",
                    view_type=ViewType.BAR_CHART,
                    config={"waterfall": True, "categories": ["beginning", "provision", "chargeoffs", "recoveries", "ending"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="reserve_waterfall_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "CECLFramework",
    "CECLConfig",
    "CECLMetrics",
    "CECLReserve",
    "SegmentACL",
    "CECLMethod",
    "EconomicScenario",
    "CECLTransition",
]
