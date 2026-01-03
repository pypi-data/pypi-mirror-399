# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Regulatory Impact Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Regulatory Impact Assessment (RIA) Framework.

Implements comprehensive regulatory impact analysis following:
- OMB Circular A-4 methodology
- Executive Order 12866/13563 requirements
- Cost-benefit analysis standards
- Regulatory flexibility analysis (RFA)

References:
    - OMB Circular A-4 (Regulatory Analysis)
    - Executive Order 12866 (Regulatory Planning and Review)
    - Regulatory Flexibility Act
    - EPA Guidelines for Economic Analysis

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
from krl_frameworks.simulation.cbss import TransitionFunction
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    OutputViewSpec,
    ParameterGroupSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["RegulatoryImpactFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# RIA Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class RegulatoryCategory(Enum):
    """Types of regulatory actions."""
    ECONOMICALLY_SIGNIFICANT = "Economically Significant (>$100M)"
    SIGNIFICANT = "Significant"
    ROUTINE = "Routine"
    DEREGULATORY = "Deregulatory"


class CostCategory(Enum):
    """Categories of regulatory costs."""
    COMPLIANCE = "Compliance Costs"
    ADMINISTRATIVE = "Administrative Costs"
    OPPORTUNITY = "Opportunity Costs"
    INDIRECT = "Indirect/Spillover Costs"


class BenefitCategory(Enum):
    """Categories of regulatory benefits."""
    HEALTH = "Health Benefits"
    SAFETY = "Safety Benefits"
    ENVIRONMENTAL = "Environmental Benefits"
    ECONOMIC = "Economic Benefits"
    SOCIAL = "Social Benefits"


@dataclass
class CostEstimate:
    """Regulatory cost estimate."""
    
    category: CostCategory = CostCategory.COMPLIANCE
    
    # Annual costs (millions $)
    first_year: float = 0.0
    annual_recurring: float = 0.0
    one_time: float = 0.0
    
    # Distributional
    small_business_share: float = 0.0
    large_business_share: float = 0.0
    government_share: float = 0.0
    
    # Uncertainty
    low_estimate: float = 0.0
    high_estimate: float = 0.0
    confidence_level: float = 0.90


@dataclass
class BenefitEstimate:
    """Regulatory benefit estimate."""
    
    category: BenefitCategory = BenefitCategory.ECONOMIC
    
    # Annual benefits (millions $)
    annual_monetized: float = 0.0
    
    # Non-monetized benefits description
    non_monetized: str = ""
    
    # Statistical lives saved (if applicable)
    lives_saved: float = 0.0
    value_of_statistical_life: float = 11.6  # 2024 VSL in millions
    
    # Uncertainty
    low_estimate: float = 0.0
    high_estimate: float = 0.0


@dataclass
class RIAResult:
    """Regulatory Impact Analysis results."""
    
    # Classification
    category: RegulatoryCategory = RegulatoryCategory.ROUTINE
    
    # Cost-benefit summary (present value, millions $)
    total_costs_pv: float = 0.0
    total_benefits_pv: float = 0.0
    net_benefits_pv: float = 0.0
    
    # Annualized
    annualized_costs: float = 0.0
    annualized_benefits: float = 0.0
    annualized_net_benefits: float = 0.0
    
    # Benefit-cost ratio
    bcr: float = 0.0
    
    # Break-even analysis
    break_even_year: Optional[int] = None
    
    # Cost detail
    cost_estimates: list[CostEstimate] = field(default_factory=list)
    
    # Benefit detail
    benefit_estimates: list[BenefitEstimate] = field(default_factory=list)
    
    # Regulatory flexibility
    small_entity_impact: str = ""
    rfa_required: bool = False


@dataclass
class DistributionalAnalysis:
    """Distributional impact analysis."""
    
    # Income quintile impacts (% change in welfare)
    quintile_impacts: dict[int, float] = field(default_factory=dict)
    
    # Geographic impacts
    urban_impact: float = 0.0
    rural_impact: float = 0.0
    
    # Industry impacts
    industry_impacts: dict[str, float] = field(default_factory=dict)
    
    # Employment effects
    jobs_created: float = 0.0
    jobs_lost: float = 0.0
    net_employment: float = 0.0
    
    # Equity assessment
    progressive: bool = False
    regressive: bool = False


@dataclass
class AlternativesAnalysis:
    """Analysis of regulatory alternatives."""
    
    alternative_name: str = ""
    description: str = ""
    
    costs_pv: float = 0.0
    benefits_pv: float = 0.0
    net_benefits_pv: float = 0.0
    
    # Comparison to preferred
    cost_difference: float = 0.0
    benefit_difference: float = 0.0
    
    # Feasibility
    technically_feasible: bool = True
    legally_feasible: bool = True


@dataclass
class RIAMetrics:
    """Comprehensive RIA results."""
    
    main_result: RIAResult = field(default_factory=RIAResult)
    distributional: DistributionalAnalysis = field(default_factory=DistributionalAnalysis)
    alternatives: list[AlternativesAnalysis] = field(default_factory=list)
    
    # Sensitivity analysis
    sensitivity_results: dict[str, float] = field(default_factory=dict)


# ════════════════════════════════════════════════════════════════════════════════
# RIA Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class RegulatoryTransition(TransitionFunction):
    """Transition function for regulatory impact simulation."""
    
    name = "RegulatoryTransition"
    
    def __init__(self, compliance_cost_effect: float = -0.02, benefit_effect: float = 0.03):
        self.compliance_cost_effect = compliance_cost_effect
        self.benefit_effect = benefit_effect
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        
        # Regulation implementation effect
        implementation_year = params.get("implementation_year", 0)
        
        if t >= implementation_year:
            # Compliance costs reduce output initially
            cost_effect = self.compliance_cost_effect * np.exp(-0.1 * (t - implementation_year))
            # Benefits grow over time
            benefit_effect = self.benefit_effect * (1 - np.exp(-0.2 * (t - implementation_year)))
            
            net_effect = cost_effect + benefit_effect
        else:
            net_effect = 0
        
        new_opportunity = np.clip(state.opportunity_score + net_effect, 0, 1)
        new_output = state.sector_output * (1 + net_effect * 0.5)
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=np.clip(state.health_burden_score - benefit_effect * 0.5, 0, 1),
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=new_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Regulatory Impact Framework
# ════════════════════════════════════════════════════════════════════════════════


class RegulatoryImpactFramework(BaseMetaFramework):
    """
    Regulatory Impact Assessment Framework.
    
    Production-grade RIA following OMB Circular A-4:
    
    - Cost-benefit analysis
    - Distributional impact assessment
    - Alternatives analysis
    - Regulatory flexibility analysis
    - Sensitivity analysis
    
    Token Weight: 6
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = RegulatoryImpactFramework()
        >>> result = framework.analyze_regulation(
        ...     costs=[CostEstimate(annual_recurring=50)],
        ...     benefits=[BenefitEstimate(annual_monetized=100)],
        ... )
        >>> print(f"Net Benefits: ${result.net_benefits_pv:.1f}M")
    
    References:
        - OMB Circular A-4
        - E.O. 12866
    """
    
    METADATA = FrameworkMetadata(
        slug="regulatory-impact",
        name="Regulatory Impact Assessment",
        version="1.0.0",
        layer=VerticalLayer.GOVERNMENT_POLICY,
        tier=Tier.PROFESSIONAL,
        description=(
            "Comprehensive regulatory impact analysis following "
            "OMB Circular A-4 and E.O. 12866 requirements."
        ),
        required_domains=["costs", "benefits", "affected_entities"],
        output_domains=["net_benefits", "bcr", "distributional_impacts"],
        constituent_models=["cba", "rfa", "distributional", "sensitivity"],
        tags=["regulatory", "impact-assessment", "cost-benefit", "omb"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(
        self,
        discount_rate: float = 0.03,
        analysis_horizon: int = 20,
        vsl: float = 11.6,  # Value of Statistical Life in millions
    ):
        super().__init__()
        self.discount_rate = discount_rate
        self.analysis_horizon = analysis_horizon
        self.vsl = vsl
        self._transition_fn = RegulatoryTransition()
    
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
            employment_prob=np.full(n_cohorts, 0.70),
            health_burden_score=np.full(n_cohorts, 0.25),
            credit_access_prob=np.full(n_cohorts, 0.65),
            housing_cost_ratio=np.full(n_cohorts, 0.32),
            opportunity_score=np.full(n_cohorts, 0.5),
            sector_output=np.full((n_cohorts, 5), 1000.0),
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
            "mean_opportunity": float(np.mean(state.opportunity_score)),
            "mean_health_burden": float(np.mean(state.health_burden_score)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "regulatory-impact", "n_periods": trajectory.n_periods}

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Return Regulatory Impact dashboard specification."""
        return FrameworkDashboardSpec(
            slug="regulatory-impact",
            name="Regulatory Impact Assessment",
            description=(
                "Comprehensive regulatory impact analysis following "
                "OMB Circular A-4 and E.O. 12866 requirements."
            ),
            layer="government",
            parameters_schema={
                "type": "object",
                "properties": {
                    "regulation_type": {
                        "type": "string",
                        "title": "Regulation Type",
                        "enum": ["economically_significant", "significant", "routine", "deregulatory"],
                        "default": "significant",
                        "x-ui-widget": "select",
                        "x-ui-group": "regulation",
                    },
                    "cost_benefit_method": {
                        "type": "string",
                        "title": "Cost-Benefit Method",
                        "enum": ["standard_cba", "break_even", "cost_effectiveness", "multi_criteria"],
                        "default": "standard_cba",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                    },
                    "affected_sectors": {
                        "type": "array",
                        "title": "Affected Sectors",
                        "items": {
                            "type": "string",
                            "enum": ["small_business", "large_business", "government", "consumers", "environment"],
                        },
                        "default": ["small_business", "large_business"],
                        "x-ui-widget": "multiselect",
                        "x-ui-group": "sectors",
                    },
                },
            },
            default_parameters={
                "regulation_type": "significant",
                "cost_benefit_method": "standard_cba",
                "affected_sectors": ["small_business", "large_business"],
            },
            parameter_groups=[
                ParameterGroupSpec(key="regulation", title="Regulation", parameters=["regulation_type"]),
                ParameterGroupSpec(key="methodology", title="Methodology", parameters=["cost_benefit_method"]),
                ParameterGroupSpec(key="sectors", title="Sectors", parameters=["affected_sectors"]),
            ],
            required_domains=["costs", "benefits", "affected_entities"],
            min_tier=Tier.ENTERPRISE,
            output_views=[
                OutputViewSpec(
                    key="net_benefits",
                    title="Net Benefits",
                    view_type=ViewType.GAUGE,
                    config={"min": -1000, "max": 1000, "format": "$,.0fM", "color_range": ["red", "yellow", "green"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="net_benefits_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="cost_breakdown",
                    title="Cost Breakdown",
                    view_type=ViewType.BAR_CHART,
                    config={"x_field": "category", "y_field": "cost", "color_by": "sector", "format": "$,.0f"},
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="cost_breakdown_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="benefit_categories",
                    title="Benefit Categories",
                    view_type=ViewType.TABLE,
                    config={"columns": ["category", "quantified", "monetized", "annual_value", "pv"]},
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="benefit_categories_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="distributional_impacts",
                    title="Distributional Impacts",
                    view_type=ViewType.LINE_CHART,
                    config={"x_field": "year", "y_field": "impact", "color_by": "affected_group"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="distributional_impacts_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )

    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════

    @requires_tier(Tier.PROFESSIONAL)
    def compute_present_value(
        self,
        annual_values: list[float],
        start_year: int = 0,
    ) -> float:
        """
        Compute present value of annual values.
        
        Args:
            annual_values: List of annual values
            start_year: Year offset for discounting
        
        Returns:
            Present value
        """
        pv = 0.0
        for i, value in enumerate(annual_values):
            year = start_year + i
            pv += value / ((1 + self.discount_rate) ** year)
        return pv
    
    @requires_tier(Tier.PROFESSIONAL)
    def annualize(self, present_value: float, years: int) -> float:
        """
        Convert present value to annualized value.
        
        Args:
            present_value: Present value
            years: Number of years
        
        Returns:
            Annualized value
        """
        if years <= 0:
            return 0.0
        
        # Annuity factor
        r = self.discount_rate
        factor = r / (1 - (1 + r) ** (-years))
        
        return present_value * factor
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_costs(
        self,
        costs: list[CostEstimate],
    ) -> tuple[float, list[float]]:
        """
        Analyze regulatory costs over time.
        
        Args:
            costs: List of cost estimates
        
        Returns:
            Tuple of (present value, annual costs)
        """
        annual_costs = [0.0] * self.analysis_horizon
        
        for cost in costs:
            # First year includes one-time costs
            annual_costs[0] += cost.first_year + cost.one_time
            
            # Recurring costs
            for i in range(self.analysis_horizon):
                if i > 0 or cost.first_year == 0:
                    annual_costs[i] += cost.annual_recurring
        
        pv = self.compute_present_value(annual_costs)
        
        return pv, annual_costs
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_benefits(
        self,
        benefits: list[BenefitEstimate],
    ) -> tuple[float, list[float]]:
        """
        Analyze regulatory benefits over time.
        
        Args:
            benefits: List of benefit estimates
        
        Returns:
            Tuple of (present value, annual benefits)
        """
        annual_benefits = [0.0] * self.analysis_horizon
        
        for benefit in benefits:
            annual_value = benefit.annual_monetized
            
            # Add monetized value of lives saved
            if benefit.lives_saved > 0:
                annual_value += benefit.lives_saved * benefit.value_of_statistical_life
            
            for i in range(self.analysis_horizon):
                annual_benefits[i] += annual_value
        
        pv = self.compute_present_value(annual_benefits)
        
        return pv, annual_benefits
    
    @requires_tier(Tier.PROFESSIONAL)
    def classify_regulation(
        self,
        annual_costs: float,
        annual_benefits: float,
    ) -> RegulatoryCategory:
        """
        Classify regulation by significance.
        
        Args:
            annual_costs: Annual costs in millions
            annual_benefits: Annual benefits in millions
        
        Returns:
            Regulatory category
        """
        max_impact = max(annual_costs, annual_benefits)
        
        if max_impact >= 100:
            return RegulatoryCategory.ECONOMICALLY_SIGNIFICANT
        elif max_impact >= 25:
            return RegulatoryCategory.SIGNIFICANT
        elif annual_benefits > annual_costs * 1.5:
            return RegulatoryCategory.DEREGULATORY
        else:
            return RegulatoryCategory.ROUTINE
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_regulation(
        self,
        costs: list[CostEstimate],
        benefits: list[BenefitEstimate],
    ) -> RIAResult:
        """
        Complete regulatory impact analysis.
        
        Args:
            costs: List of cost estimates
            benefits: List of benefit estimates
        
        Returns:
            RIA results
        """
        # Analyze costs and benefits
        costs_pv, annual_costs = self.analyze_costs(costs)
        benefits_pv, annual_benefits = self.analyze_benefits(benefits)
        
        # Net benefits
        net_pv = benefits_pv - costs_pv
        
        # Annualize
        annualized_costs = self.annualize(costs_pv, self.analysis_horizon)
        annualized_benefits = self.annualize(benefits_pv, self.analysis_horizon)
        
        # BCR
        bcr = benefits_pv / costs_pv if costs_pv > 0 else float('inf')
        
        # Break-even year
        cumulative_net = 0.0
        break_even = None
        for i in range(self.analysis_horizon):
            cumulative_net += annual_benefits[i] - annual_costs[i]
            if cumulative_net >= 0 and break_even is None:
                break_even = i + 1
        
        # Classification
        category = self.classify_regulation(
            max(annual_costs) if annual_costs else 0,
            max(annual_benefits) if annual_benefits else 0,
        )
        
        # RFA check
        small_biz_cost = sum(c.small_business_share * c.annual_recurring for c in costs)
        rfa_required = small_biz_cost > 0
        
        return RIAResult(
            category=category,
            total_costs_pv=costs_pv,
            total_benefits_pv=benefits_pv,
            net_benefits_pv=net_pv,
            annualized_costs=annualized_costs,
            annualized_benefits=annualized_benefits,
            annualized_net_benefits=annualized_benefits - annualized_costs,
            bcr=bcr,
            break_even_year=break_even,
            cost_estimates=costs,
            benefit_estimates=benefits,
            rfa_required=rfa_required,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def distributional_analysis(
        self,
        costs: list[CostEstimate],
        benefits: list[BenefitEstimate],
        income_distribution: Optional[np.ndarray] = None,
    ) -> DistributionalAnalysis:
        """
        Analyze distributional impacts.
        
        Args:
            costs: Cost estimates
            benefits: Benefit estimates
            income_distribution: Optional income distribution weights
        
        Returns:
            Distributional analysis
        """
        # Quintile impacts (simplified - would use detailed data)
        total_cost = sum(c.annual_recurring for c in costs)
        total_benefit = sum(b.annual_monetized for b in benefits)
        
        # Assume costs hit lower quintiles harder, benefits more even
        quintile_impacts = {}
        for q in range(1, 6):
            cost_share = (6 - q) / 15  # Lower quintiles bear more costs
            benefit_share = 1 / 5  # Even benefits
            
            net_impact = (benefit_share * total_benefit - cost_share * total_cost)
            quintile_impacts[q] = net_impact
        
        # Check progressivity
        progressive = quintile_impacts[1] > quintile_impacts[5]
        regressive = quintile_impacts[1] < quintile_impacts[5]
        
        # Employment effects (simplified)
        compliance_jobs = -total_cost * 0.01  # Jobs lost to compliance
        industry_jobs = total_benefit * 0.005  # Jobs from cleaner industry
        
        return DistributionalAnalysis(
            quintile_impacts=quintile_impacts,
            urban_impact=0.0,
            rural_impact=0.0,
            jobs_created=max(0, industry_jobs),
            jobs_lost=abs(min(0, compliance_jobs)),
            net_employment=compliance_jobs + industry_jobs,
            progressive=progressive,
            regressive=regressive,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def sensitivity_analysis(
        self,
        costs: list[CostEstimate],
        benefits: list[BenefitEstimate],
        discount_rates: list[float] = [0.03, 0.07],
    ) -> dict[str, float]:
        """
        Perform sensitivity analysis.
        
        Args:
            costs: Cost estimates
            benefits: Benefit estimates
            discount_rates: Discount rates to test
        
        Returns:
            Sensitivity results
        """
        results = {}
        
        original_rate = self.discount_rate
        
        for rate in discount_rates:
            self.discount_rate = rate
            result = self.analyze_regulation(costs, benefits)
            results[f"net_benefits_at_{rate:.0%}"] = result.net_benefits_pv
            results[f"bcr_at_{rate:.0%}"] = result.bcr
        
        self.discount_rate = original_rate
        
        return results
    
    @requires_tier(Tier.PROFESSIONAL)
    def full_ria(
        self,
        costs: list[CostEstimate],
        benefits: list[BenefitEstimate],
    ) -> RIAMetrics:
        """
        Complete Regulatory Impact Assessment.
        
        Args:
            costs: Cost estimates
            benefits: Benefit estimates
        
        Returns:
            Full RIA metrics
        """
        main_result = self.analyze_regulation(costs, benefits)
        distributional = self.distributional_analysis(costs, benefits)
        sensitivity = self.sensitivity_analysis(costs, benefits)
        
        # Baseline alternative (no action)
        no_action = AlternativesAnalysis(
            alternative_name="No Action",
            description="Maintain status quo",
            costs_pv=0,
            benefits_pv=0,
            net_benefits_pv=0,
            cost_difference=-main_result.total_costs_pv,
            benefit_difference=-main_result.total_benefits_pv,
        )
        
        return RIAMetrics(
            main_result=main_result,
            distributional=distributional,
            alternatives=[no_action],
            sensitivity_results=sensitivity,
        )
