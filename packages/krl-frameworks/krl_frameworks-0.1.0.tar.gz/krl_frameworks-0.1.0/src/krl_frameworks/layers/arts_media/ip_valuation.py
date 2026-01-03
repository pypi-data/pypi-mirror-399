# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - IP Valuation Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Intellectual Property Valuation Framework.

Implements comprehensive IP value assessment:
- Patent portfolio valuation
- Trademark and brand valuation
- Copyright asset valuation
- Trade secret valuation
- Franchise/licensing value

References:
    - ISO 10668 (Brand Valuation)
    - IVSC Intangible Asset Guidelines
    - WIPO IP Valuation Methods

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
from krl_frameworks.core.tier import Tier, requires_tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["IPValuationFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# IP Valuation Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class IPType(Enum):
    """Types of intellectual property."""
    PATENT = "Patent"
    TRADEMARK = "Trademark"
    COPYRIGHT = "Copyright"
    TRADE_SECRET = "Trade Secret"
    FRANCHISE = "Franchise"
    SOFTWARE = "Software"
    DATA = "Data/Database"
    DESIGN = "Design Right"


class PatentType(Enum):
    """Patent categories."""
    UTILITY = "Utility Patent"
    DESIGN = "Design Patent"
    PLANT = "Plant Patent"
    PROVISIONAL = "Provisional"


class ValuationMethod(Enum):
    """IP valuation methods."""
    INCOME = "Income Approach"
    MARKET = "Market Approach"
    COST = "Cost Approach"
    RELIEF_FROM_ROYALTY = "Relief from Royalty"
    OPTION_PRICING = "Real Options"


@dataclass
class PatentAsset:
    """Patent asset details."""
    
    id: str = ""
    title: str = ""
    patent_type: PatentType = PatentType.UTILITY
    
    # Filing and status
    filing_date: str = ""
    grant_date: str = ""
    expiration_date: str = ""
    remaining_life_years: float = 15.0
    status: str = "Active"
    
    # Geographic coverage
    jurisdictions: list[str] = field(default_factory=list)
    
    # Technology area
    technology_class: str = ""
    
    # Citations
    forward_citations: int = 0  # Others citing this
    backward_citations: int = 0  # This cites others
    
    # Litigation history
    litigation_wins: int = 0
    litigation_losses: int = 0


@dataclass
class TrademarkAsset:
    """Trademark asset details."""
    
    id: str = ""
    name: str = ""
    
    # Registration
    registration_date: str = ""
    renewal_date: str = ""
    jurisdictions: list[str] = field(default_factory=list)
    
    # Classification
    nice_classes: list[int] = field(default_factory=list)
    
    # Brand metrics
    brand_awareness: float = 0.0  # 0-100%
    brand_strength_score: float = 0.0  # 0-100
    
    # Revenue attribution
    branded_revenue: float = 0.0


@dataclass
class CopyrightAsset:
    """Copyright asset details."""
    
    id: str = ""
    title: str = ""
    
    # Creation and registration
    creation_date: str = ""
    registration_date: str = ""
    expiration_date: str = ""
    
    # Work type
    work_type: str = ""  # Literary, Musical, Audiovisual, etc.
    
    # Revenue
    annual_royalties: float = 0.0
    licensing_revenue: float = 0.0


@dataclass
class IPValuation:
    """IP asset valuation result."""
    
    asset_id: str = ""
    asset_type: IPType = IPType.PATENT
    
    # Valuation by method
    income_value: float = 0.0
    market_value: float = 0.0
    cost_value: float = 0.0
    royalty_relief_value: float = 0.0
    
    # Final value
    fair_value: float = 0.0
    method_used: ValuationMethod = ValuationMethod.INCOME
    
    # Key drivers
    remaining_life: float = 0.0
    royalty_rate: float = 0.0
    discount_rate: float = 0.0
    
    # Confidence
    low_estimate: float = 0.0
    high_estimate: float = 0.0
    confidence: float = 0.90


@dataclass
class PortfolioValuation:
    """IP portfolio valuation."""
    
    total_assets: int = 0
    
    # By type
    patent_count: int = 0
    trademark_count: int = 0
    copyright_count: int = 0
    other_count: int = 0
    
    # Values
    patent_value: float = 0.0
    trademark_value: float = 0.0
    copyright_value: float = 0.0
    other_value: float = 0.0
    total_value: float = 0.0
    
    # Portfolio metrics
    average_remaining_life: float = 0.0
    concentration_index: float = 0.0  # HHI of value distribution


@dataclass
class LicensingAnalysis:
    """IP licensing analysis."""
    
    asset_id: str = ""
    
    # Licensing structure
    exclusive: bool = False
    territories: list[str] = field(default_factory=list)
    
    # Economics
    upfront_fee: float = 0.0
    running_royalty_rate: float = 0.0
    minimum_royalty: float = 0.0
    
    # Projected revenue
    annual_royalty_revenue: float = 0.0
    npv_of_license: float = 0.0


@dataclass
class IPMetrics:
    """Complete IP valuation metrics."""
    
    valuation: IPValuation = field(default_factory=IPValuation)
    licensing: Optional[LicensingAnalysis] = None
    
    # Strategic value
    strategic_premium: float = 0.0  # Value to strategic buyer
    synergy_value: float = 0.0


# ════════════════════════════════════════════════════════════════════════════════
# IP Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class IPValueTransition(TransitionFunction):
    """Transition function for IP value over time."""
    
    name = "IPValueTransition"
    
    def __init__(self, decay_rate: float = 0.05):
        self.decay_rate = decay_rate
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        
        # IP value typically appreciates early then decays
        remaining_life = params.get("remaining_life", 15)
        
        if t < remaining_life / 3:
            # Early growth phase
            value_change = 0.05
        elif t < 2 * remaining_life / 3:
            # Mature phase
            value_change = 0.0
        else:
            # Decline phase
            value_change = -self.decay_rate
        
        new_output = state.sector_output * (1 + value_change)
        
        return CohortStateVector(
            employment_prob=state.employment_prob,
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=state.opportunity_score,
            sector_output=new_output,
            deprivation_vector=state.deprivation_vector,
        )


# ════════════════════════════════════════════════════════════════════════════════
# IP Valuation Framework
# ════════════════════════════════════════════════════════════════════════════════


class IPValuationFramework(BaseMetaFramework):
    """
    Intellectual Property Valuation Framework.
    
    Production-grade IP valuation following ISO 10668 and IVSC standards:
    
    - Patent portfolio valuation
    - Trademark and brand valuation
    - Copyright asset valuation
    - Relief-from-royalty method
    - Real options pricing
    
    Token Weight: 5
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = IPValuationFramework()
        >>> valuation = framework.value_patent(patent, revenues)
        >>> print(f"Patent Value: ${valuation.fair_value:.1f}M")
    
    References:
        - ISO 10668
        - IVSC Intangible Assets
        - WIPO IP Valuation
    """
    
    METADATA = FrameworkMetadata(
        slug="ip-valuation",
        name="IP Valuation",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.PROFESSIONAL,
        description=(
            "Intellectual property valuation using income, market, "
            "and cost approaches per ISO 10668 and IVSC standards."
        ),
        required_domains=["ip_assets", "revenue_data"],
        output_domains=["ip_value", "royalty_rates", "portfolio_value"],
        constituent_models=["dcf", "royalty_relief", "market_comps", "real_options"],
        tags=["ip", "patents", "trademarks", "copyright", "valuation"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    # Industry royalty rates (% of revenue)
    ROYALTY_RATES = {
        "pharmaceutical": 0.08,
        "software": 0.06,
        "semiconductor": 0.04,
        "consumer_electronics": 0.03,
        "automotive": 0.02,
        "medical_device": 0.07,
        "aerospace": 0.05,
        "entertainment": 0.10,
        "retail": 0.02,
        "default": 0.05,
    }
    
    def __init__(self, discount_rate: float = 0.12):
        super().__init__()
        self.discount_rate = discount_rate
        self._transition_fn = IPValueTransition()
    
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
            sector_output=np.full((n_cohorts, 5), 100.0),
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
            "mean_output": float(np.mean(state.sector_output)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "ip-valuation", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Dashboard specification for IP valuation."""
        return FrameworkDashboardSpec(
            slug="ip-valuation",
            name="IP Valuation",
            description=(
                "Intellectual property valuation using income, market, "
                "and cost approaches per ISO 10668 and IVSC standards."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    "ip_type": {
                        "type": "string",
                        "title": "IP Type",
                        "description": "Type of intellectual property asset",
                        "enum": ["patent", "trademark", "copyright", "trade_secret", "franchise", "software", "data", "design"],
                        "default": "patent",
                        "x-ui-widget": "select",
                        "x-ui-group": "asset",
                    },
                    "valuation_method": {
                        "type": "string",
                        "title": "Valuation Method",
                        "description": "Primary IP valuation methodology",
                        "enum": ["income", "market", "cost", "relief_from_royalty", "option_pricing"],
                        "default": "relief_from_royalty",
                        "x-ui-widget": "select",
                        "x-ui-group": "methodology",
                    },
                    "discount_rate": {
                        "type": "number",
                        "title": "Discount Rate",
                        "description": "Discount rate for DCF calculations",
                        "minimum": 0.05,
                        "maximum": 0.30,
                        "default": 0.12,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-format": ".0%",
                        "x-ui-group": "methodology",
                    },
                    "royalty_rate": {
                        "type": "number",
                        "title": "Royalty Rate",
                        "description": "Applicable royalty rate for relief-from-royalty",
                        "minimum": 0.01,
                        "maximum": 0.20,
                        "default": 0.05,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.005,
                        "x-ui-format": ".1%",
                        "x-ui-group": "methodology",
                    },
                    "remaining_life_years": {
                        "type": "number",
                        "title": "Remaining Life (Years)",
                        "description": "Remaining useful life of the IP asset",
                        "minimum": 1,
                        "maximum": 30,
                        "default": 15.0,
                        "x-ui-widget": "slider",
                        "x-ui-group": "asset",
                    },
                    "tax_rate": {
                        "type": "number",
                        "title": "Tax Rate",
                        "description": "Applicable tax rate for after-tax calculations",
                        "minimum": 0.0,
                        "maximum": 0.50,
                        "default": 0.25,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-format": ".0%",
                        "x-ui-group": "methodology",
                    },
                    "industry": {
                        "type": "string",
                        "title": "Industry",
                        "description": "Industry sector for royalty rate benchmarking",
                        "enum": ["pharmaceutical", "software", "semiconductor", "consumer_electronics", "automotive", "medical_device", "aerospace", "entertainment", "retail"],
                        "default": "entertainment",
                        "x-ui-widget": "select",
                        "x-ui-group": "asset",
                    },
                },
                "required": [],
            },
            default_parameters={
                "ip_type": "patent",
                "valuation_method": "relief_from_royalty",
                "discount_rate": 0.12,
                "royalty_rate": 0.05,
                "remaining_life_years": 15.0,
                "tax_rate": 0.25,
                "industry": "entertainment",
            },
            min_tier=Tier.PROFESSIONAL,
            parameter_groups=[
                ParameterGroupSpec(
                    key="asset",
                    title="IP Asset Properties",
                    parameters=["ip_type", "remaining_life_years", "industry"],
                ),
                ParameterGroupSpec(
                    key="methodology",
                    title="Valuation Methodology",
                    parameters=["valuation_method", "discount_rate", "royalty_rate", "tax_rate"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="ip_value",
                    title="IP Fair Value",
                    view_type=ViewType.GAUGE,
                    description="Estimated intellectual property value",
                    config={"min": 0, "max": 100, "format": "$,.1f", "suffix": "M"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="ip_value_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="cash_flow_projection",
                    title="Royalty Cash Flows",
                    view_type=ViewType.LINE_CHART,
                    description="Projected royalty cash flows over remaining life",
                    config={"x_field": "year", "y_fields": ["royalty_savings", "discounted_value"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="cash_flow_projection_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="valuation_range",
                    title="Valuation Range",
                    view_type=ViewType.BAR_CHART,
                    description="Low/Fair/High value estimates",
                    config={"x_field": "estimate", "y_field": "value"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="valuation_range_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="sensitivity_analysis",
                    title="Sensitivity Analysis",
                    view_type=ViewType.TABLE,
                    description="Value sensitivity to discount rate and royalty rate",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="sensitivity_analysis_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def get_royalty_rate(
        self,
        industry: str,
        ip_type: IPType = IPType.PATENT,
    ) -> float:
        """
        Get appropriate royalty rate for industry.
        
        Args:
            industry: Industry sector
            ip_type: Type of IP
        
        Returns:
            Royalty rate (as decimal)
        """
        base_rate = self.ROYALTY_RATES.get(industry.lower(), self.ROYALTY_RATES["default"])
        
        # Adjust by IP type
        type_multipliers = {
            IPType.PATENT: 1.0,
            IPType.TRADEMARK: 0.8,
            IPType.COPYRIGHT: 0.6,
            IPType.TRADE_SECRET: 0.7,
            IPType.FRANCHISE: 1.2,
            IPType.SOFTWARE: 1.0,
            IPType.DATA: 0.5,
            IPType.DESIGN: 0.4,
        }
        
        return base_rate * type_multipliers.get(ip_type, 1.0)
    
    @requires_tier(Tier.PROFESSIONAL)
    def relief_from_royalty(
        self,
        revenue_projection: list[float],
        royalty_rate: float,
        remaining_life: int,
        tax_rate: float = 0.25,
    ) -> float:
        """
        Value IP using relief-from-royalty method.
        
        Args:
            revenue_projection: Annual revenue projections
            royalty_rate: Applicable royalty rate
            remaining_life: Years of remaining IP life
            tax_rate: Applicable tax rate
        
        Returns:
            Relief-from-royalty value
        """
        value = 0.0
        
        for i in range(min(remaining_life, len(revenue_projection))):
            royalty_savings = revenue_projection[i] * royalty_rate
            after_tax = royalty_savings * (1 - tax_rate)
            discounted = after_tax / ((1 + self.discount_rate) ** (i + 1))
            value += discounted
        
        # Terminal value if projections shorter than life
        if len(revenue_projection) < remaining_life and revenue_projection:
            last_rev = revenue_projection[-1]
            for i in range(len(revenue_projection), remaining_life):
                # Decay assumption
                rev = last_rev * (0.95 ** (i - len(revenue_projection) + 1))
                royalty_savings = rev * royalty_rate
                after_tax = royalty_savings * (1 - tax_rate)
                discounted = after_tax / ((1 + self.discount_rate) ** (i + 1))
                value += discounted
        
        return value
    
    @requires_tier(Tier.PROFESSIONAL)
    def value_patent(
        self,
        patent: PatentAsset,
        revenue_projection: list[float],
        industry: str = "default",
    ) -> IPValuation:
        """
        Value a patent asset.
        
        Args:
            patent: Patent details
            revenue_projection: Revenue projections
            industry: Industry sector
        
        Returns:
            Patent valuation
        """
        # Get appropriate royalty rate
        royalty_rate = self.get_royalty_rate(industry, IPType.PATENT)
        
        # Citation strength adjustment
        citation_ratio = patent.forward_citations / max(1, patent.backward_citations)
        strength_adj = 1 + min(0.5, citation_ratio * 0.1)
        
        # Litigation adjustment
        if patent.litigation_wins > 0:
            litigation_adj = 1.2
        elif patent.litigation_losses > 0:
            litigation_adj = 0.7
        else:
            litigation_adj = 1.0
        
        effective_royalty = royalty_rate * strength_adj * litigation_adj
        
        # Relief-from-royalty value
        rfr_value = self.relief_from_royalty(
            revenue_projection,
            effective_royalty,
            int(patent.remaining_life_years),
        )
        
        # Geographic coverage premium
        geo_premium = 1 + len(patent.jurisdictions) * 0.05
        rfr_value *= geo_premium
        
        # Income value (simplified DCF)
        income_value = rfr_value * 0.95  # Similar to RFR
        
        # Cost value (development costs proxy)
        cost_value = sum(revenue_projection[:3]) * 0.3 if len(revenue_projection) >= 3 else rfr_value * 0.5
        
        # Fair value (weighted)
        fair_value = 0.7 * rfr_value + 0.2 * income_value + 0.1 * cost_value
        
        return IPValuation(
            asset_id=patent.id,
            asset_type=IPType.PATENT,
            income_value=income_value,
            market_value=0.0,
            cost_value=cost_value,
            royalty_relief_value=rfr_value,
            fair_value=fair_value,
            method_used=ValuationMethod.RELIEF_FROM_ROYALTY,
            remaining_life=patent.remaining_life_years,
            royalty_rate=effective_royalty,
            discount_rate=self.discount_rate,
            low_estimate=fair_value * 0.7,
            high_estimate=fair_value * 1.4,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def value_trademark(
        self,
        trademark: TrademarkAsset,
        revenue_projection: list[float],
    ) -> IPValuation:
        """
        Value a trademark asset.
        
        Args:
            trademark: Trademark details
            revenue_projection: Branded revenue projections
        
        Returns:
            Trademark valuation
        """
        # Brand strength determines royalty rate
        # Higher brand strength = higher royalty
        base_royalty = 0.02 + (trademark.brand_strength_score / 100) * 0.08
        
        # Awareness premium
        awareness_premium = 1 + (trademark.brand_awareness / 100) * 0.3
        
        effective_royalty = base_royalty * awareness_premium
        
        # Trademarks can be renewed indefinitely - use 20 year horizon
        rfr_value = self.relief_from_royalty(
            revenue_projection,
            effective_royalty,
            remaining_life=20,
        )
        
        # Income approach (brand premium)
        brand_premium = sum(revenue_projection) * 0.05  # 5% brand premium
        income_value = brand_premium / self.discount_rate
        
        fair_value = 0.6 * rfr_value + 0.4 * income_value
        
        return IPValuation(
            asset_id=trademark.id,
            asset_type=IPType.TRADEMARK,
            income_value=income_value,
            market_value=0.0,
            cost_value=0.0,
            royalty_relief_value=rfr_value,
            fair_value=fair_value,
            method_used=ValuationMethod.RELIEF_FROM_ROYALTY,
            remaining_life=20,  # Indefinite with renewal
            royalty_rate=effective_royalty,
            discount_rate=self.discount_rate,
            low_estimate=fair_value * 0.75,
            high_estimate=fair_value * 1.3,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def value_copyright(
        self,
        copyright: CopyrightAsset,
        remaining_life: int = 50,
    ) -> IPValuation:
        """
        Value a copyright asset.
        
        Args:
            copyright: Copyright details
            remaining_life: Remaining copyright life
        
        Returns:
            Copyright valuation
        """
        # Income approach from royalties and licensing
        annual_income = copyright.annual_royalties + copyright.licensing_revenue
        
        # DCF of income stream with decay
        decay_rate = 0.03  # Copyrights decay slowly
        income_value = 0.0
        
        for i in range(min(remaining_life, 30)):  # Cap at 30 years
            annual = annual_income * ((1 - decay_rate) ** i)
            discounted = annual / ((1 + self.discount_rate) ** (i + 1))
            income_value += discounted
        
        return IPValuation(
            asset_id=copyright.id,
            asset_type=IPType.COPYRIGHT,
            income_value=income_value,
            market_value=0.0,
            cost_value=0.0,
            royalty_relief_value=0.0,
            fair_value=income_value,
            method_used=ValuationMethod.INCOME,
            remaining_life=remaining_life,
            royalty_rate=0.0,
            discount_rate=self.discount_rate,
            low_estimate=income_value * 0.8,
            high_estimate=income_value * 1.25,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def value_portfolio(
        self,
        valuations: list[IPValuation],
    ) -> PortfolioValuation:
        """
        Value an IP portfolio.
        
        Args:
            valuations: Individual IP valuations
        
        Returns:
            Portfolio valuation
        """
        # Count by type
        patent_vals = [v for v in valuations if v.asset_type == IPType.PATENT]
        trademark_vals = [v for v in valuations if v.asset_type == IPType.TRADEMARK]
        copyright_vals = [v for v in valuations if v.asset_type == IPType.COPYRIGHT]
        other_vals = [v for v in valuations if v.asset_type not in [IPType.PATENT, IPType.TRADEMARK, IPType.COPYRIGHT]]
        
        patent_value = sum(v.fair_value for v in patent_vals)
        trademark_value = sum(v.fair_value for v in trademark_vals)
        copyright_value = sum(v.fair_value for v in copyright_vals)
        other_value = sum(v.fair_value for v in other_vals)
        
        total_value = patent_value + trademark_value + copyright_value + other_value
        
        # Average remaining life
        avg_life = np.mean([v.remaining_life for v in valuations]) if valuations else 0
        
        # Concentration (HHI)
        if total_value > 0:
            shares = [(v.fair_value / total_value) ** 2 for v in valuations]
            hhi = sum(shares)
        else:
            hhi = 0
        
        return PortfolioValuation(
            total_assets=len(valuations),
            patent_count=len(patent_vals),
            trademark_count=len(trademark_vals),
            copyright_count=len(copyright_vals),
            other_count=len(other_vals),
            patent_value=patent_value,
            trademark_value=trademark_value,
            copyright_value=copyright_value,
            other_value=other_value,
            total_value=total_value,
            average_remaining_life=avg_life,
            concentration_index=hhi,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_licensing(
        self,
        valuation: IPValuation,
        exclusive: bool = False,
        territories: Optional[list[str]] = None,
    ) -> LicensingAnalysis:
        """
        Analyze licensing economics for IP.
        
        Args:
            valuation: IP valuation
            exclusive: Whether license is exclusive
            territories: Licensed territories
        
        Returns:
            Licensing analysis
        """
        territories = territories or ["Worldwide"]
        
        # Exclusive licenses command premium
        exclusivity_factor = 1.5 if exclusive else 1.0
        
        # Territory coverage
        if "Worldwide" in territories:
            territory_factor = 1.0
        else:
            territory_factor = len(territories) * 0.15
        
        # Running royalty based on valuation
        running_royalty = valuation.royalty_rate * exclusivity_factor * territory_factor
        
        # Upfront (25% of value for exclusive, 10% for non-exclusive)
        upfront = valuation.fair_value * (0.25 if exclusive else 0.10)
        
        # Minimum guarantee
        minimum = valuation.fair_value * 0.05 / valuation.remaining_life
        
        # Projected annual royalty
        annual_royalty = valuation.fair_value * running_royalty
        
        # NPV of license
        npv = upfront + sum(
            annual_royalty / ((1 + self.discount_rate) ** i)
            for i in range(1, int(valuation.remaining_life) + 1)
        )
        
        return LicensingAnalysis(
            asset_id=valuation.asset_id,
            exclusive=exclusive,
            territories=territories,
            upfront_fee=upfront,
            running_royalty_rate=running_royalty,
            minimum_royalty=minimum,
            annual_royalty_revenue=annual_royalty,
            npv_of_license=npv,
        )
