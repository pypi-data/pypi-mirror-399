# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - CBO Scoring Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Congressional Budget Office (CBO) Scoring Framework.

Implements the CBO's methodology for estimating budgetary effects of
proposed legislation, including:
- Direct spending (mandatory) projections
- Revenue effects
- Discretionary spending estimates
- Dynamic scoring with macroeconomic feedback

References:
    - CBO's Methods for Estimating the Costs of Legislation
    - PAYGO and Budget Enforcement Act procedures
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
from krl_frameworks.core.state import StateTrajectory
from krl_frameworks.core.exceptions import (
    DataBundleValidationError,
    ConfigurationError,
    ExecutionError,
)
from krl_frameworks.simulation import TransitionFunction
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)


# ════════════════════════════════════════════════════════════════════════════════
# CBO-Specific Data Structures
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class CBOScoringConfig:
    """Configuration for CBO scoring analysis."""
    
    # Budget window
    scoring_window_years: int = 10
    baseline_year: int = 2024
    
    # Scoring options
    use_dynamic_scoring: bool = False
    include_interest_effects: bool = True
    use_current_law_baseline: bool = True
    
    # Discount rate for present value calculations
    discount_rate: float = 0.03
    
    # GDP elasticities for dynamic scoring
    labor_supply_elasticity: float = 0.25
    capital_elasticity: float = 0.35
    
    # Behavioral response parameters
    behavioral_response_lag: int = 2  # Years before full behavioral response
    max_behavioral_adjustment: float = 0.15  # Max % adjustment from behavioral effects


@dataclass
class BudgetScore:
    """CBO budget score results."""
    
    # Core scoring outputs (in millions)
    outlays_by_year: dict[int, float] = field(default_factory=dict)
    revenues_by_year: dict[int, float] = field(default_factory=dict)
    deficit_effect_by_year: dict[int, float] = field(default_factory=dict)
    
    # Summary measures
    ten_year_cost: float = 0.0
    five_year_cost: float = 0.0
    first_year_cost: float = 0.0
    
    # Present value
    present_value_cost: float = 0.0
    
    # Dynamic scoring additions
    gdp_effect_by_year: dict[int, float] = field(default_factory=dict)
    dynamic_feedback_by_year: dict[int, float] = field(default_factory=dict)
    
    # Metadata
    scoring_date: str = ""
    legislation_id: str = ""
    uncertainty_range: tuple[float, float] = (0.0, 0.0)
    
    @property
    def paygo_score(self) -> float:
        """PAYGO scorecard value (5-year + 10-year)."""
        return self.five_year_cost + self.ten_year_cost


@dataclass
class CBOMetrics:
    """Comprehensive CBO analysis metrics."""
    
    # Budget scores
    mandatory_score: BudgetScore = field(default_factory=BudgetScore)
    discretionary_score: BudgetScore = field(default_factory=BudgetScore)
    revenue_score: BudgetScore = field(default_factory=BudgetScore)
    total_score: BudgetScore = field(default_factory=BudgetScore)
    
    # Program-level metrics
    program_costs: dict[str, float] = field(default_factory=dict)
    coverage_effects: dict[str, int] = field(default_factory=dict)  # People affected
    
    # Macroeconomic effects (dynamic scoring)
    gdp_impact_percent: float = 0.0
    employment_impact: int = 0
    wage_effect_percent: float = 0.0
    
    # Distributional analysis
    income_quintile_effects: dict[str, float] = field(default_factory=dict)
    regional_effects: dict[str, float] = field(default_factory=dict)
    
    # Confidence metrics
    estimation_confidence: str = "medium"  # low, medium, high
    key_uncertainties: list[str] = field(default_factory=list)


# ════════════════════════════════════════════════════════════════════════════════
# CBO Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class CBOTransition(TransitionFunction):
    """
    CBO budget scoring transition function.
    
    Models the evolution of fiscal variables under proposed legislation,
    incorporating:
    - Baseline spending growth
    - Policy-induced changes
    - Behavioral responses
    - Dynamic macroeconomic feedback
    """
    
    def __init__(self, config: CBOScoringConfig):
        self.config = config
        
        # Growth assumptions (align with CBO baseline)
        self.baseline_outlay_growth = 0.045  # 4.5% nominal
        self.baseline_revenue_growth = 0.042  # 4.2% nominal
        self.inflation_rate = 0.025  # 2.5%
        self.real_gdp_growth = 0.018  # 1.8%
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply CBO scoring transition for one period."""
        params = params or {}
        
        # Extract policy parameters
        outlay_change = params.get("outlay_change_rate", 0.0)
        revenue_change = params.get("revenue_change_rate", 0.0)
        behavioral_response = params.get("behavioral_response", 0.0)
        
        # Calculate period in scoring window
        year_offset = t + 1
        
        # Apply behavioral response lag
        if year_offset <= self.config.behavioral_response_lag:
            behavioral_factor = (year_offset / self.config.behavioral_response_lag) * behavioral_response
        else:
            behavioral_factor = min(behavioral_response, self.config.max_behavioral_adjustment)
        
        # Update employment probability (fiscal impact on jobs)
        employment_effect = (
            0.3 * outlay_change  # Spending multiplier
            - 0.1 * revenue_change  # Tax drag
            + 0.2 * behavioral_factor  # Behavioral response
        )
        new_employment = np.clip(
            state.employment_prob * (1 + employment_effect),
            0.0, 1.0
        )
        
        # Update credit access (government program effects)
        credit_effect = 0.15 * outlay_change  # Spending increases credit access
        new_credit = np.clip(
            state.credit_access_prob * (1 + credit_effect),
            0.0, 1.0
        )
        
        # Update sector output (fiscal stimulus/drag)
        gdp_multiplier = 1.0 + (
            0.8 * outlay_change  # Direct spending multiplier
            - 0.5 * revenue_change  # Tax multiplier
        )
        new_sector_output = state.sector_output * gdp_multiplier
        
        # Update opportunity score
        opportunity_effect = (
            0.2 * outlay_change  # Public investment
            - 0.05 * revenue_change  # Tax burden
        )
        new_opportunity = np.clip(
            state.opportunity_score * (1 + opportunity_effect),
            0.0, 1.0
        )
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score,  # Unchanged in base CBO
            credit_access_prob=new_credit,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_sector_output,
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )


# ════════════════════════════════════════════════════════════════════════════════
# CBO Scoring Framework
# ════════════════════════════════════════════════════════════════════════════════


class CBOScoringFramework(BaseMetaFramework):
    """
    Congressional Budget Office Scoring Framework.
    
    Implements CBO-style budget scoring for policy proposals, including:
    - 10-year budget window projections
    - PAYGO scoring
    - Dynamic macroeconomic feedback (optional)
    - Distributional impact analysis
    
    This framework models how proposed legislation affects federal
    spending, revenues, and deficits over time.
    
    Tier: PROFESSIONAL (budget scoring requires validated data)
    
    Example:
        >>> cbo = CBOScoringFramework()
        >>> bundle = DataBundle.from_dataframes({"fiscal": fiscal_df, "economic": econ_df})
        >>> score = cbo.score_legislation(bundle, legislation_params)
        >>> print(f"10-year cost: ${score.ten_year_cost:,.0f}M")
    """
    
    METADATA = FrameworkMetadata(
        slug="cbo_scoring",
        name="CBO Budget Scoring Framework",
        version="1.0.0",
        layer=VerticalLayer.GOVERNMENT_POLICY,
        tier=Tier.PROFESSIONAL,
        description="Congressional Budget Office methodology for estimating budgetary effects",
        required_domains=["fiscal", "economic"],
        output_domains=["budget_score", "fiscal_impact"],
        constituent_models=["baseline_projector", "behavioral_estimator", "macro_feedback"],
        tags=["government", "cbo", "budget", "scoring", "legislation"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self, config: Optional[CBOScoringConfig] = None):
        super().__init__()
        self.scoring_config = config or CBOScoringConfig()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from fiscal and economic data."""
        fiscal_data = bundle.get("fiscal")
        econ_data = bundle.get("economic")
        
        fiscal_df = fiscal_data.data
        econ_df = econ_data.data
        
        n_cohorts = len(fiscal_df)
        
        # Extract fiscal baseline
        if "outlays" in fiscal_df.columns:
            baseline_outlays = fiscal_df["outlays"].values[:n_cohorts]
        else:
            baseline_outlays = np.full(n_cohorts, 1e6)  # Default $1M per cohort
        
        # Extract employment baseline
        if "employment_rate" in econ_df.columns:
            employment = econ_df["employment_rate"].values[:n_cohorts]
        else:
            employment = np.full(n_cohorts, 0.95)
        
        # Calculate sector output from GDP
        if "gdp" in econ_df.columns:
            gdp = econ_df["gdp"].values[:n_cohorts]
            sector_output = np.column_stack([gdp / 10] * 10)
        else:
            sector_output = np.full((n_cohorts, 10), 1e5)
        
        # Credit access from financial conditions
        if "credit_conditions" in fiscal_df.columns:
            credit = fiscal_df["credit_conditions"].values[:n_cohorts]
        else:
            credit = np.full(n_cohorts, 0.7)
        
        return CohortStateVector(
            employment_prob=np.clip(employment, 0, 1),
            health_burden_score=np.full(n_cohorts, 0.1),  # Low baseline
            credit_access_prob=np.clip(credit, 0, 1),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.full(n_cohorts, 0.6),
            sector_output=sector_output,
            deprivation_vector=np.zeros((n_cohorts, 6)),
            step=0,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply CBO transition function."""
        transition = CBOTransition(self.scoring_config)
        return transition(state, t, config)
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> CBOMetrics:
        """Compute CBO scoring metrics from simulation trajectory."""
        metrics = CBOMetrics()
        
        if len(trajectory) < 2:
            return metrics
        
        initial_state = trajectory.initial_state
        final_state = trajectory.final_state
        
        # Compute budget scores by year
        base_year = self.scoring_config.baseline_year
        
        for i, state in enumerate(trajectory.states):
            year = base_year + i
            
            # Calculate implied outlays from sector output changes
            if i > 0:
                prev_output = trajectory.states[i-1].sector_output.sum()
                curr_output = state.sector_output.sum()
                outlay_change = curr_output - prev_output
                
                metrics.total_score.outlays_by_year[year] = outlay_change / 1e6  # Convert to millions
                metrics.total_score.deficit_effect_by_year[year] = outlay_change / 1e6
        
        # Calculate summary measures
        years = sorted(metrics.total_score.deficit_effect_by_year.keys())
        if years:
            metrics.total_score.first_year_cost = metrics.total_score.deficit_effect_by_year.get(years[0], 0)
            metrics.total_score.five_year_cost = sum(
                metrics.total_score.deficit_effect_by_year.get(y, 0)
                for y in years[:5]
            )
            metrics.total_score.ten_year_cost = sum(
                metrics.total_score.deficit_effect_by_year.get(y, 0)
                for y in years[:10]
            )
        
        # Calculate employment impact
        initial_employment = initial_state.employment_prob.mean()
        final_employment = final_state.employment_prob.mean()
        employment_change = final_employment - initial_employment
        
        metrics.employment_impact = int(employment_change * 160_000_000)  # US labor force
        
        # GDP impact
        initial_gdp = initial_state.sector_output.sum()
        final_gdp = final_state.sector_output.sum()
        metrics.gdp_impact_percent = ((final_gdp / initial_gdp) - 1) * 100
        
        return metrics

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return CBO Scoring dashboard specification."""
        return FrameworkDashboardSpec(
            slug="cbo_scoring",
            name="CBO Budget Scoring Framework",
            description=(
                "Congressional Budget Office methodology for estimating budgetary "
                "effects of proposed legislation over a 10-year window."
            ),
            layer="government",
            parameters_schema={
                "type": "object",
                "properties": {
                    "scoring_window": {
                        "type": "integer",
                        "title": "Scoring Window (years)",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-group": "window",
                    },
                    "baseline_scenario": {
                        "type": "string",
                        "title": "Baseline Scenario",
                        "enum": ["current_law", "current_policy", "cbo_extended"],
                        "default": "current_law",
                        "x-ui-widget": "select",
                        "x-ui-group": "baseline",
                    },
                    "policy_proposal": {
                        "type": "string",
                        "title": "Policy Proposal Type",
                        "enum": ["tax_change", "spending_program", "entitlement_reform", "regulatory"],
                        "default": "spending_program",
                        "x-ui-widget": "select",
                        "x-ui-group": "policy",
                    },
                    "discount_rate": {
                        "type": "number",
                        "title": "Discount Rate",
                        "minimum": 0.0,
                        "maximum": 0.10,
                        "default": 0.03,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-format": ".1%",
                        "x-ui-group": "parameters",
                    },
                },
            },
            default_parameters={
                "scoring_window": 10,
                "baseline_scenario": "current_law",
                "policy_proposal": "spending_program",
                "discount_rate": 0.03,
            },
            parameter_groups=[
                ParameterGroupSpec(key="window", title="Scoring Window", parameters=["scoring_window"]),
                ParameterGroupSpec(key="baseline", title="Baseline", parameters=["baseline_scenario"]),
                ParameterGroupSpec(key="policy", title="Policy", parameters=["policy_proposal"]),
                ParameterGroupSpec(key="parameters", title="Parameters", parameters=["discount_rate"]),
            ],
            required_domains=["fiscal", "economic"],
            min_tier=Tier.ENTERPRISE,
            output_views=[
                OutputViewSpec(
                    key="budget_impact",
                    title="Budget Impact Over Time",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "year", "y_field": "deficit_effect", "format": "$,.0f"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="budget_impact_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="ten_year_score",
                    title="10-Year Budget Score",
                    view_type=ViewType.TABLE,
                    config={"columns": ["year", "outlays", "revenues", "deficit_effect", "cumulative"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="ten_year_score_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="sensitivity_analysis",
                    title="Sensitivity Analysis",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "scenario", "y_field": "cost_variance", "color_by": "direction"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="sensitivity_analysis_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def score_legislation(
        self,
        bundle: DataBundle,
        legislation_params: dict[str, Any],
        config: Optional[FrameworkConfig] = None,
    ) -> BudgetScore:
        """
        Score proposed legislation using CBO methodology.
        
        Args:
            bundle: DataBundle with fiscal and economic data
            legislation_params: Parameters describing the legislation
            config: Optional framework configuration
        
        Returns:
            BudgetScore with 10-year projections
        """
        config = config or FrameworkConfig()
        
        # Compute initial state
        initial_state = self._compute_initial_state(bundle, config)
        
        # Run simulation for scoring window
        trajectory = StateTrajectory(states=[initial_state])
        current_state = initial_state
        
        transition = CBOTransition(self.scoring_config)
        
        for t in range(self.scoring_config.scoring_window_years):
            current_state = transition(current_state, t, config, legislation_params)
            trajectory.append(current_state)
        
        # Compute metrics
        metrics = self._compute_metrics(trajectory)
        
        return metrics.total_score
    
    @requires_tier(Tier.ENTERPRISE)
    def dynamic_score(
        self,
        bundle: DataBundle,
        legislation_params: dict[str, Any],
        config: Optional[FrameworkConfig] = None,
    ) -> CBOMetrics:
        """
        Perform dynamic scoring with macroeconomic feedback.
        
        This Enterprise-tier feature includes:
        - GDP effects from fiscal policy
        - Labor supply responses
        - Capital formation effects
        - Interest rate feedback
        
        Args:
            bundle: DataBundle with fiscal and economic data
            legislation_params: Parameters describing the legislation
            config: Optional framework configuration
        
        Returns:
            CBOMetrics with full dynamic scoring results
        """
        # Enable dynamic scoring in config
        dynamic_config = CBOScoringConfig(
            **{**self.scoring_config.__dict__, "use_dynamic_scoring": True}
        )
        
        # Store original config
        original_config = self.scoring_config
        self.scoring_config = dynamic_config
        
        try:
            config = config or FrameworkConfig()
            
            # Compute initial state
            initial_state = self._compute_initial_state(bundle, config)
            
            # Run simulation with dynamic feedback
            trajectory = StateTrajectory(states=[initial_state])
            current_state = initial_state
            
            transition = CBOTransition(dynamic_config)
            
            for t in range(dynamic_config.scoring_window_years):
                # Add dynamic feedback parameters
                dynamic_params = {**legislation_params}
                
                # Calculate dynamic feedback from previous period
                if t > 0:
                    prev_state = trajectory.states[t]
                    gdp_change = (
                        current_state.sector_output.sum() / 
                        prev_state.sector_output.sum() - 1
                    )
                    dynamic_params["behavioral_response"] = (
                        gdp_change * dynamic_config.labor_supply_elasticity
                    )
                
                current_state = transition(current_state, t, config, dynamic_params)
                trajectory.append(current_state)
            
            # Compute full metrics
            metrics = self._compute_metrics(trajectory)
            metrics.estimation_confidence = "medium"
            metrics.key_uncertainties = [
                "Labor supply elasticity assumptions",
                "Behavioral response timing",
                "Macroeconomic baseline projections",
            ]
            
            return metrics
            
        finally:
            self.scoring_config = original_config


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "CBOScoringFramework",
    "CBOScoringConfig",
    "BudgetScore",
    "CBOMetrics",
    "CBOTransition",
]
