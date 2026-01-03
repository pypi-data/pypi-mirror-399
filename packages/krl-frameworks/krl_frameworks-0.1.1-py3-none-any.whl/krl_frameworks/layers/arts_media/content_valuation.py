# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Content Valuation Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Content Valuation Framework.

Implements comprehensive content value assessment:
- Content lifecycle valuation
- Engagement-based pricing models
- Library asset valuation
- Revenue attribution across windows

References:
    - Media economics literature
    - Content licensing industry standards
    - Streaming platform economics research

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

__all__ = ["ContentValuationFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Content Valuation Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class ContentType(Enum):
    """Types of media content."""
    FILM = "Film"
    TV_SERIES = "TV Series"
    DOCUMENTARY = "Documentary"
    NEWS = "News"
    SPORTS = "Sports"
    MUSIC = "Music"
    PODCAST = "Podcast"
    GAME = "Video Game"
    BOOK = "Book/eBook"
    UGC = "User Generated Content"


class ContentWindow(Enum):
    """Distribution windows."""
    THEATRICAL = "Theatrical"
    PVOD = "Premium VOD"
    SVOD = "Subscription VOD"
    AVOD = "Ad-supported VOD"
    PAY_TV = "Pay TV"
    BASIC_CABLE = "Basic Cable"
    BROADCAST = "Broadcast"
    INTERNATIONAL = "International"
    SYNDICATION = "Syndication"
    HOME_VIDEO = "Home Video/EST"
    LIBRARY = "Library/Catalog"


class EngagementMetric(Enum):
    """Types of engagement metrics."""
    VIEWS = "Views/Streams"
    HOURS_WATCHED = "Hours Watched"
    COMPLETION_RATE = "Completion Rate"
    REWATCH_RATE = "Rewatch Rate"
    SOCIAL_ENGAGEMENT = "Social Engagement"
    SEARCH_INTEREST = "Search Interest"


@dataclass
class ContentMetadata:
    """Content asset metadata."""
    
    id: str = ""
    title: str = ""
    content_type: ContentType = ContentType.FILM
    
    # Basic info
    release_year: int = 2024
    runtime_minutes: int = 90
    episodes: int = 1
    seasons: int = 1
    
    # Genre and demographics
    genres: list[str] = field(default_factory=list)
    target_demo: str = ""
    rating: str = ""  # PG, R, TV-MA, etc.
    
    # Production
    production_budget: float = 0.0
    marketing_spend: float = 0.0
    
    # Talent
    star_power_score: float = 0.0  # 0-100
    franchise_value: float = 0.0


@dataclass
class EngagementData:
    """Content engagement metrics."""
    
    window: ContentWindow = ContentWindow.SVOD
    
    # Volume metrics
    total_views: float = 0.0
    unique_viewers: float = 0.0
    total_hours: float = 0.0
    
    # Quality metrics
    avg_completion_rate: float = 0.0
    avg_rating: float = 0.0  # 0-5 scale
    nps_score: float = 0.0  # -100 to 100
    
    # Retention impact
    churn_prevention_rate: float = 0.0
    acquisition_rate: float = 0.0


@dataclass
class WindowRevenue:
    """Revenue by distribution window."""
    
    window: ContentWindow = ContentWindow.THEATRICAL
    
    # Revenue (millions $)
    domestic_revenue: float = 0.0
    international_revenue: float = 0.0
    total_revenue: float = 0.0
    
    # Costs and margins
    distribution_cost: float = 0.0
    net_revenue: float = 0.0
    margin: float = 0.0


@dataclass
class ContentValuation:
    """Complete content valuation."""
    
    content_id: str = ""
    
    # Valuation methods
    dcf_value: float = 0.0  # Discounted cash flow
    comp_value: float = 0.0  # Comparable transaction
    cost_value: float = 0.0  # Cost approach
    
    # Final valuation
    fair_value: float = 0.0
    value_per_hour: float = 0.0
    value_per_view: float = 0.0
    
    # Breakdown
    remaining_life_years: float = 0.0
    annual_decay_rate: float = 0.0
    
    # Revenue by window
    window_revenues: list[WindowRevenue] = field(default_factory=list)


@dataclass
class LibraryValuation:
    """Library/catalog valuation."""
    
    total_titles: int = 0
    total_hours: float = 0.0
    
    # Value breakdown
    aggregate_value: float = 0.0
    average_title_value: float = 0.0
    value_per_hour: float = 0.0
    
    # Segment values
    premium_tier_value: float = 0.0
    standard_tier_value: float = 0.0
    filler_tier_value: float = 0.0
    
    # Growth
    annual_decay: float = 0.0
    acquisition_pipeline: float = 0.0


@dataclass
class ContentMetrics:
    """Complete content valuation metrics."""
    
    content: ContentMetadata = field(default_factory=ContentMetadata)
    engagement: list[EngagementData] = field(default_factory=list)
    valuation: ContentValuation = field(default_factory=ContentValuation)
    
    # ROI metrics
    production_roi: float = 0.0
    marketing_roi: float = 0.0
    total_roi: float = 0.0


# ════════════════════════════════════════════════════════════════════════════════
# Content Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class ContentValueTransition(TransitionFunction):
    """Transition function for content value decay simulation."""
    
    name = "ContentValueTransition"
    
    def __init__(self, decay_rate: float = 0.15):
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
        
        # Content value decay over time
        decay = np.exp(-self.decay_rate * t)
        new_output = state.sector_output * decay
        
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
# Content Valuation Framework
# ════════════════════════════════════════════════════════════════════════════════


class ContentValuationFramework(BaseMetaFramework):
    """
    Content Valuation Framework.
    
    Production-grade content value assessment:
    
    - Multi-window revenue modeling
    - Engagement-based value attribution
    - Library and catalog valuation
    - Content lifecycle modeling
    
    Token Weight: 5
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = ContentValuationFramework()
        >>> valuation = framework.value_content(content, engagement)
        >>> print(f"Fair Value: ${valuation.fair_value:.1f}M")
    
    References:
        - Media Economics
        - Content Licensing Standards
    """
    
    METADATA = FrameworkMetadata(
        slug="content-valuation",
        name="Content Valuation",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.PROFESSIONAL,
        description=(
            "Content asset valuation using multi-window revenue modeling "
            "and engagement-based attribution."
        ),
        required_domains=["content_metadata", "engagement_data"],
        output_domains=["content_value", "window_revenue", "roi"],
        constituent_models=["dcf", "comps", "engagement_model"],
        tags=["content", "valuation", "media", "entertainment"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    # Typical value decay by content type (annual rate)
    DECAY_RATES = {
        ContentType.FILM: 0.20,
        ContentType.TV_SERIES: 0.15,
        ContentType.DOCUMENTARY: 0.10,
        ContentType.NEWS: 0.90,  # Very rapid
        ContentType.SPORTS: 0.95,  # Almost immediate
        ContentType.MUSIC: 0.05,
        ContentType.PODCAST: 0.30,
        ContentType.GAME: 0.25,
        ContentType.BOOK: 0.08,
        ContentType.UGC: 0.50,
    }
    
    def __init__(self, discount_rate: float = 0.10):
        super().__init__()
        self.discount_rate = discount_rate
        self._transition_fn = ContentValueTransition()
    
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
        return {"framework": "content-valuation", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Dashboard specification for content valuation."""
        return FrameworkDashboardSpec(
            slug="content-valuation",
            name="Content Valuation",
            description=(
                "Content asset valuation using multi-window revenue modeling "
                "and engagement-based attribution."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    "content_type": {
                        "type": "string",
                        "title": "Content Type",
                        "description": "Type of media content to value",
                        "enum": ["film", "tv_series", "documentary", "news", "sports", "music", "podcast", "game", "book", "ugc"],
                        "default": "film",
                        "x-ui-widget": "select",
                        "x-ui-group": "content",
                    },
                    "discount_rate": {
                        "type": "number",
                        "title": "Discount Rate",
                        "description": "Discount rate for DCF valuation",
                        "minimum": 0.01,
                        "maximum": 0.30,
                        "default": 0.10,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-format": ".0%",
                        "x-ui-group": "valuation",
                    },
                    "valuation_method": {
                        "type": "string",
                        "title": "Valuation Method",
                        "description": "Primary valuation methodology",
                        "enum": ["dcf", "comps", "cost", "engagement_based"],
                        "default": "dcf",
                        "x-ui-widget": "select",
                        "x-ui-group": "valuation",
                    },
                    "horizon_years": {
                        "type": "integer",
                        "title": "Valuation Horizon (Years)",
                        "description": "Number of years for DCF projection",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 10,
                        "x-ui-widget": "slider",
                        "x-ui-group": "valuation",
                    },
                    "production_budget": {
                        "type": "number",
                        "title": "Production Budget ($M)",
                        "description": "Content production budget in millions",
                        "minimum": 0,
                        "maximum": 500,
                        "default": 10.0,
                        "x-ui-widget": "number",
                        "x-ui-group": "content",
                    },
                    "star_power_score": {
                        "type": "number",
                        "title": "Star Power Score",
                        "description": "Talent star power (0-100)",
                        "minimum": 0,
                        "maximum": 100,
                        "default": 50.0,
                        "x-ui-widget": "slider",
                        "x-ui-group": "content",
                    },
                    "primary_window": {
                        "type": "string",
                        "title": "Primary Window",
                        "description": "Primary distribution window",
                        "enum": ["theatrical", "pvod", "svod", "avod", "pay_tv", "broadcast", "library"],
                        "default": "svod",
                        "x-ui-widget": "select",
                        "x-ui-group": "distribution",
                    },
                },
                "required": [],
            },
            default_parameters={
                "content_type": "film",
                "discount_rate": 0.10,
                "valuation_method": "dcf",
                "horizon_years": 10,
                "production_budget": 10.0,
                "star_power_score": 50.0,
                "primary_window": "svod",
            },
            min_tier=Tier.PROFESSIONAL,
            parameter_groups=[
                ParameterGroupSpec(
                    key="content",
                    title="Content Properties",
                    parameters=["content_type", "production_budget", "star_power_score"],
                ),
                ParameterGroupSpec(
                    key="valuation",
                    title="Valuation Parameters",
                    parameters=["discount_rate", "valuation_method", "horizon_years"],
                ),
                ParameterGroupSpec(
                    key="distribution",
                    title="Distribution",
                    parameters=["primary_window"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="asset_value",
                    title="Asset Value",
                    view_type=ViewType.GAUGE,
                    description="Estimated content asset value",
                    config={"min": 0, "max": 1000, "format": "$,.0f", "suffix": "M"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="asset_value_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="revenue_forecast",
                    title="Revenue Forecast",
                    view_type=ViewType.LINE_CHART,
                    description="Projected revenue over content lifecycle",
                    config={"x_field": "year", "y_fields": ["revenue", "cumulative"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="revenue_forecast_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="window_breakdown",
                    title="Window Revenue Breakdown",
                    view_type=ViewType.BAR_CHART,
                    description="Revenue by distribution window",
                    config={"x_field": "window", "y_field": "revenue"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="window_breakdown_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="value_drivers",
                    title="Value Drivers",
                    view_type=ViewType.TABLE,
                    description="Key value drivers breakdown",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="value_drivers_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def estimate_window_revenue(
        self,
        content: ContentMetadata,
        window: ContentWindow,
        engagement: Optional[EngagementData] = None,
    ) -> WindowRevenue:
        """
        Estimate revenue for a distribution window.
        
        Args:
            content: Content metadata
            window: Distribution window
            engagement: Optional engagement data
        
        Returns:
            Window revenue estimate
        """
        # Base revenue multipliers by window (as % of production budget)
        window_multipliers = {
            ContentWindow.THEATRICAL: 2.0,
            ContentWindow.PVOD: 0.3,
            ContentWindow.SVOD: 1.5,
            ContentWindow.AVOD: 0.4,
            ContentWindow.PAY_TV: 0.5,
            ContentWindow.BASIC_CABLE: 0.3,
            ContentWindow.BROADCAST: 0.4,
            ContentWindow.INTERNATIONAL: 1.0,
            ContentWindow.SYNDICATION: 0.3,
            ContentWindow.HOME_VIDEO: 0.2,
            ContentWindow.LIBRARY: 0.15,
        }
        
        base_multiplier = window_multipliers.get(window, 0.1)
        
        # Adjust for star power
        star_adj = 1 + (content.star_power_score / 100) * 0.5
        
        # Adjust for franchise
        franchise_adj = 1 + content.franchise_value / 100
        
        base_revenue = content.production_budget * base_multiplier * star_adj * franchise_adj
        
        # Engagement adjustment
        if engagement:
            # Higher completion = higher value
            completion_adj = 0.5 + engagement.avg_completion_rate
            base_revenue *= completion_adj
        
        # Domestic/International split
        domestic = base_revenue * 0.4
        international = base_revenue * 0.6
        
        # Distribution costs
        dist_cost = base_revenue * 0.20
        
        return WindowRevenue(
            window=window,
            domestic_revenue=domestic,
            international_revenue=international,
            total_revenue=base_revenue,
            distribution_cost=dist_cost,
            net_revenue=base_revenue - dist_cost,
            margin=(base_revenue - dist_cost) / base_revenue if base_revenue > 0 else 0,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_dcf_value(
        self,
        content: ContentMetadata,
        projected_revenues: list[float],
        horizon_years: int = 10,
    ) -> float:
        """
        Compute discounted cash flow value.
        
        Args:
            content: Content metadata
            projected_revenues: Annual revenue projections
            horizon_years: Valuation horizon
        
        Returns:
            DCF value
        """
        decay_rate = self.DECAY_RATES.get(content.content_type, 0.15)
        
        dcf = 0.0
        for i in range(horizon_years):
            if i < len(projected_revenues):
                annual_rev = projected_revenues[i]
            else:
                # Decay from last known
                last_rev = projected_revenues[-1] if projected_revenues else 0
                years_beyond = i - len(projected_revenues) + 1
                annual_rev = last_rev * np.exp(-decay_rate * years_beyond)
            
            # Discount
            dcf += annual_rev / ((1 + self.discount_rate) ** (i + 1))
        
        return dcf
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_comp_value(
        self,
        content: ContentMetadata,
        comparable_prices: list[tuple[float, float]],  # (hours, price)
    ) -> float:
        """
        Compute value using comparable transactions.
        
        Args:
            content: Content metadata
            comparable_prices: List of (hours, price_paid) for comparable content
        
        Returns:
            Comparable value
        """
        if not comparable_prices:
            return 0.0
        
        # Compute price per hour from comps
        price_per_hours = [p / h for h, p in comparable_prices if h > 0]
        
        if not price_per_hours:
            return 0.0
        
        avg_price_per_hour = np.mean(price_per_hours)
        
        # Content hours
        content_hours = content.runtime_minutes / 60 * content.episodes * content.seasons
        
        base_value = content_hours * avg_price_per_hour
        
        # Quality adjustments
        star_adj = 1 + (content.star_power_score / 100) * 0.3
        
        return base_value * star_adj
    
    @requires_tier(Tier.PROFESSIONAL)
    def value_content(
        self,
        content: ContentMetadata,
        engagement: list[EngagementData],
    ) -> ContentValuation:
        """
        Complete content valuation.
        
        Args:
            content: Content metadata
            engagement: Engagement data by window
        
        Returns:
            Content valuation
        """
        # Estimate window revenues
        window_revenues = []
        total_revenue = 0.0
        
        for window in ContentWindow:
            eng_data = next((e for e in engagement if e.window == window), None)
            rev = self.estimate_window_revenue(content, window, eng_data)
            if rev.total_revenue > 0:
                window_revenues.append(rev)
                total_revenue += rev.total_revenue
        
        # DCF value (5 years of projections)
        decay_rate = self.DECAY_RATES.get(content.content_type, 0.15)
        first_year_rev = total_revenue
        projected = [first_year_rev * np.exp(-decay_rate * i) for i in range(5)]
        dcf_value = self.compute_dcf_value(content, projected)
        
        # Cost-based value
        cost_value = content.production_budget + content.marketing_spend
        
        # Final fair value (weighted average)
        fair_value = 0.6 * dcf_value + 0.4 * cost_value
        
        # Per-unit metrics
        total_hours = (content.runtime_minutes / 60) * content.episodes * content.seasons
        total_views = sum(e.total_views for e in engagement)
        
        return ContentValuation(
            content_id=content.id,
            dcf_value=dcf_value,
            comp_value=0.0,
            cost_value=cost_value,
            fair_value=fair_value,
            value_per_hour=fair_value / total_hours if total_hours > 0 else 0,
            value_per_view=fair_value / total_views if total_views > 0 else 0,
            remaining_life_years=10,
            annual_decay_rate=decay_rate,
            window_revenues=window_revenues,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def value_library(
        self,
        contents: list[ContentMetadata],
        valuations: list[ContentValuation],
    ) -> LibraryValuation:
        """
        Value an entire content library.
        
        Args:
            contents: List of content in library
            valuations: Individual content valuations
        
        Returns:
            Library valuation
        """
        total_hours = sum(
            (c.runtime_minutes / 60) * c.episodes * c.seasons
            for c in contents
        )
        
        total_value = sum(v.fair_value for v in valuations)
        
        # Tier breakdown (based on production budget)
        budgets = [c.production_budget for c in contents]
        p75 = np.percentile(budgets, 75) if budgets else 0
        p25 = np.percentile(budgets, 25) if budgets else 0
        
        premium = sum(
            v.fair_value for c, v in zip(contents, valuations)
            if c.production_budget >= p75
        )
        standard = sum(
            v.fair_value for c, v in zip(contents, valuations)
            if p25 <= c.production_budget < p75
        )
        filler = sum(
            v.fair_value for c, v in zip(contents, valuations)
            if c.production_budget < p25
        )
        
        # Weighted decay
        avg_decay = np.mean([v.annual_decay_rate for v in valuations]) if valuations else 0.15
        
        return LibraryValuation(
            total_titles=len(contents),
            total_hours=total_hours,
            aggregate_value=total_value,
            average_title_value=total_value / len(contents) if contents else 0,
            value_per_hour=total_value / total_hours if total_hours > 0 else 0,
            premium_tier_value=premium,
            standard_tier_value=standard,
            filler_tier_value=filler,
            annual_decay=avg_decay,
            acquisition_pipeline=0.0,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_roi(
        self,
        content: ContentMetadata,
        valuation: ContentValuation,
    ) -> ContentMetrics:
        """
        Compute content ROI metrics.
        
        Args:
            content: Content metadata
            valuation: Content valuation
        
        Returns:
            Content metrics with ROI
        """
        total_cost = content.production_budget + content.marketing_spend
        total_revenue = sum(w.total_revenue for w in valuation.window_revenues)
        
        production_roi = (
            (total_revenue - content.production_budget) / content.production_budget
            if content.production_budget > 0 else 0
        )
        marketing_roi = (
            total_revenue / content.marketing_spend
            if content.marketing_spend > 0 else 0
        )
        total_roi = (total_revenue - total_cost) / total_cost if total_cost > 0 else 0
        
        return ContentMetrics(
            content=content,
            engagement=[],
            valuation=valuation,
            production_roi=production_roi,
            marketing_roi=marketing_roi,
            total_roi=total_roi,
        )
