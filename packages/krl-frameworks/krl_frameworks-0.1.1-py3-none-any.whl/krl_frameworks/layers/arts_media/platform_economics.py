# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Platform Economics Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Platform Economics Framework.

Implements comprehensive platform economics analysis:
- Two-sided market dynamics
- Network effects measurement
- Platform monetization analysis
- Creator economy metrics
- Marketplace economics

References:
    - Rochet & Tirole (2003) - Two-Sided Markets
    - Parker & Van Alstyne (2005) - Network Effects
    - Platform Economics Literature

Tier: PROFESSIONAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np
from scipy import stats, optimize

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

__all__ = ["PlatformEconomicsFramework"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Platform Economics Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class PlatformType(Enum):
    """Types of platforms."""
    MARKETPLACE = "Marketplace"
    CONTENT = "Content Platform"
    SOCIAL = "Social Network"
    GAMING = "Gaming Platform"
    FINTECH = "FinTech Platform"
    SAAS = "SaaS Platform"
    AGGREGATOR = "Aggregator"


class SideType(Enum):
    """Market sides."""
    CONSUMER = "Consumer"
    PRODUCER = "Producer/Creator"
    ADVERTISER = "Advertiser"
    DEVELOPER = "Developer"


class MonetizationType(Enum):
    """Platform monetization models."""
    TRANSACTION_FEE = "Transaction Fee"
    SUBSCRIPTION = "Subscription"
    ADVERTISING = "Advertising"
    FREEMIUM = "Freemium"
    LISTING_FEE = "Listing Fee"
    HYBRID = "Hybrid"


class NetworkEffectType(Enum):
    """Types of network effects."""
    DIRECT_SAME_SIDE = "Direct Same-Side"
    INDIRECT_CROSS_SIDE = "Indirect Cross-Side"
    DATA_NETWORK = "Data Network Effect"
    LOCAL = "Local Network Effect"


@dataclass
class MarketSide:
    """Platform market side metrics."""
    
    side_type: SideType = SideType.CONSUMER
    
    # User metrics
    total_users: int = 0
    active_users: int = 0
    new_users: int = 0
    churned_users: int = 0
    
    # Engagement
    dau_mau_ratio: float = 0.0  # Daily/Monthly active users
    avg_session_time: float = 0.0  # minutes
    avg_sessions_per_user: float = 0.0
    
    # Economics
    arpu: float = 0.0  # Average revenue per user
    cac: float = 0.0  # Customer acquisition cost
    ltv: float = 0.0  # Lifetime value
    
    # Network value
    side_value: float = 0.0  # Value this side brings


@dataclass
class NetworkEffects:
    """Network effects metrics."""
    
    # Same-side effects
    same_side_elasticity: float = 0.0  # % change in value per % change in users
    
    # Cross-side effects
    cross_side_elasticity: float = 0.0  # Effect of other side on this side
    
    # Critical mass
    critical_mass_reached: bool = False
    tipping_point_users: int = 0
    
    # Data network effects
    data_advantage_score: float = 0.0  # 0-100
    
    # Network effect strength
    overall_strength: float = 0.0  # 0-100


@dataclass
class PlatformMonetization:
    """Platform monetization metrics."""
    
    model: MonetizationType = MonetizationType.TRANSACTION_FEE
    
    # Revenue
    total_revenue: float = 0.0
    transaction_revenue: float = 0.0
    subscription_revenue: float = 0.0
    advertising_revenue: float = 0.0
    
    # Rates
    take_rate: float = 0.0  # Platform commission
    subscription_price: float = 0.0
    cpm: float = 0.0  # Advertising CPM
    
    # Unit economics
    gross_margin: float = 0.0
    contribution_margin: float = 0.0


@dataclass
class CreatorEconomics:
    """Creator economy metrics."""
    
    total_creators: int = 0
    active_creators: int = 0
    
    # Earnings distribution
    total_creator_earnings: float = 0.0
    median_earnings: float = 0.0
    top_1pct_share: float = 0.0  # Earnings share of top 1%
    gini_coefficient: float = 0.0  # Earnings inequality
    
    # Platform share
    platform_take_rate: float = 0.0
    creator_share: float = 0.0
    
    # Success metrics
    creators_earning_min_wage: int = 0
    creators_full_time: int = 0


@dataclass
class MarketplaceDynamics:
    """Marketplace-specific metrics."""
    
    # Volume
    gmv: float = 0.0  # Gross merchandise value
    transactions: int = 0
    avg_transaction_value: float = 0.0
    
    # Liquidity
    buyer_liquidity: float = 0.0  # % of buyers who transact
    seller_liquidity: float = 0.0  # % of sellers who sell
    match_rate: float = 0.0
    
    # Quality
    avg_rating: float = 0.0
    dispute_rate: float = 0.0
    repeat_transaction_rate: float = 0.0


@dataclass
class PlatformValuation:
    """Platform valuation metrics."""
    
    # User-based
    value_per_user: float = 0.0
    value_per_active_user: float = 0.0
    
    # Transaction-based
    multiple_of_gmv: float = 0.0
    multiple_of_revenue: float = 0.0
    
    # Growth adjusted
    peg_ratio: float = 0.0  # Price to earnings to growth
    
    # Total value
    enterprise_value: float = 0.0
    equity_value: float = 0.0


@dataclass
class PlatformMetrics:
    """Complete platform economics metrics."""
    
    platform_type: PlatformType = PlatformType.MARKETPLACE
    
    sides: list[MarketSide] = field(default_factory=list)
    network_effects: NetworkEffects = field(default_factory=NetworkEffects)
    monetization: PlatformMonetization = field(default_factory=PlatformMonetization)
    
    # Optional specialized metrics
    creator: Optional[CreatorEconomics] = None
    marketplace: Optional[MarketplaceDynamics] = None
    valuation: Optional[PlatformValuation] = None


# ════════════════════════════════════════════════════════════════════════════════
# Platform Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class PlatformGrowthTransition(TransitionFunction):
    """Transition function for platform growth dynamics."""
    
    name = "PlatformGrowthTransition"
    
    def __init__(
        self,
        network_effect_strength: float = 0.1,
        natural_churn: float = 0.05,
    ):
        self.network_effect_strength = network_effect_strength
        self.natural_churn = natural_churn
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        
        # S-curve growth with network effects
        critical_mass = params.get("critical_mass", 100000)
        current_users = np.mean(state.sector_output)
        
        # Network effect multiplier (logistic)
        network_mult = 1 / (1 + np.exp(-self.network_effect_strength * (current_users / critical_mass - 1)))
        
        # Growth rate
        organic_growth = 0.10 * network_mult
        churn = self.natural_churn
        
        net_growth = organic_growth - churn
        
        new_output = state.sector_output * (1 + net_growth)
        new_opportunity = np.clip(state.opportunity_score + network_mult * 0.1, 0, 1)
        
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
# Platform Economics Framework
# ════════════════════════════════════════════════════════════════════════════════


class PlatformEconomicsFramework(BaseMetaFramework):
    """
    Platform Economics Framework.
    
    Production-grade platform economics analysis:
    
    - Two-sided market dynamics
    - Network effects measurement
    - Platform monetization optimization
    - Creator economy analysis
    - Marketplace liquidity metrics
    
    Token Weight: 6
    Tier: PROFESSIONAL
    
    Example:
        >>> framework = PlatformEconomicsFramework()
        >>> metrics = framework.analyze_platform(consumer_side, creator_side)
        >>> print(f"Network Effect Strength: {metrics.network_effects.overall_strength:.1f}")
    
    References:
        - Rochet & Tirole (2003)
        - Parker & Van Alstyne (2005)
    """
    
    METADATA = FrameworkMetadata(
        slug="platform-economics",
        name="Platform Economics",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.PROFESSIONAL,
        description=(
            "Two-sided market and platform economics analysis including "
            "network effects, monetization, and creator economy metrics."
        ),
        required_domains=["user_data", "transaction_data"],
        output_domains=["network_effects", "monetization", "valuation"],
        constituent_models=["network_model", "ltv_model", "pricing_model"],
        tags=["platform", "two-sided-market", "network-effects", "creator-economy"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self, discount_rate: float = 0.12):
        super().__init__()
        self.discount_rate = discount_rate
        self._transition_fn = PlatformGrowthTransition()
    
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
            "mean_output": float(np.mean(state.sector_output)),
            "mean_opportunity": float(np.mean(state.opportunity_score)),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "platform-economics", "n_periods": trajectory.n_periods}
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """Dashboard specification for platform economics."""
        return FrameworkDashboardSpec(
            slug="platform-economics",
            name="Platform Economics",
            description=(
                "Two-sided market and platform economics analysis including "
                "network effects, monetization, and creator economy metrics."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    "platform_type": {
                        "type": "string",
                        "title": "Platform Type",
                        "description": "Type of platform business model",
                        "enum": ["marketplace", "content", "social", "gaming", "fintech", "saas", "aggregator"],
                        "default": "marketplace",
                        "x-ui-widget": "select",
                        "x-ui-group": "platform",
                    },
                    "monetization_model": {
                        "type": "string",
                        "title": "Monetization Model",
                        "description": "Primary platform monetization strategy",
                        "enum": ["transaction_fee", "subscription", "advertising", "freemium", "listing_fee", "hybrid"],
                        "default": "transaction_fee",
                        "x-ui-widget": "select",
                        "x-ui-group": "monetization",
                    },
                    "discount_rate": {
                        "type": "number",
                        "title": "Discount Rate",
                        "description": "Discount rate for LTV and valuation calculations",
                        "minimum": 0.05,
                        "maximum": 0.30,
                        "default": 0.12,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-format": ".0%",
                        "x-ui-group": "valuation",
                    },
                    "take_rate": {
                        "type": "number",
                        "title": "Take Rate (%)",
                        "description": "Platform commission/take rate",
                        "minimum": 0.0,
                        "maximum": 0.50,
                        "default": 0.15,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-format": ".0%",
                        "x-ui-group": "monetization",
                    },
                    "network_effect_strength": {
                        "type": "number",
                        "title": "Network Effect Strength",
                        "description": "Network effect coefficient (0-1)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.1,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.05,
                        "x-ui-group": "network",
                    },
                    "natural_churn": {
                        "type": "number",
                        "title": "Natural Churn Rate",
                        "description": "Baseline monthly churn rate",
                        "minimum": 0.01,
                        "maximum": 0.20,
                        "default": 0.05,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.01,
                        "x-ui-format": ".0%",
                        "x-ui-group": "network",
                    },
                    "critical_mass": {
                        "type": "integer",
                        "title": "Critical Mass (Users)",
                        "description": "User count for network effects to dominate",
                        "minimum": 1000,
                        "maximum": 10000000,
                        "default": 100000,
                        "x-ui-widget": "number",
                        "x-ui-group": "network",
                    },
                    "min_viable_earnings": {
                        "type": "number",
                        "title": "Min Viable Earnings ($)",
                        "description": "Minimum annual earnings for creator viability",
                        "minimum": 10000,
                        "maximum": 200000,
                        "default": 50000,
                        "x-ui-widget": "number",
                        "x-ui-group": "creator",
                    },
                },
                "required": [],
            },
            default_parameters={
                "platform_type": "marketplace",
                "monetization_model": "transaction_fee",
                "discount_rate": 0.12,
                "take_rate": 0.15,
                "network_effect_strength": 0.1,
                "natural_churn": 0.05,
                "critical_mass": 100000,
                "min_viable_earnings": 50000,
            },
            min_tier=Tier.PROFESSIONAL,
            parameter_groups=[
                ParameterGroupSpec(
                    key="platform",
                    title="Platform Type",
                    parameters=["platform_type"],
                ),
                ParameterGroupSpec(
                    key="monetization",
                    title="Monetization",
                    parameters=["monetization_model", "take_rate"],
                ),
                ParameterGroupSpec(
                    key="network",
                    title="Network Effects",
                    parameters=["network_effect_strength", "natural_churn", "critical_mass"],
                ),
                ParameterGroupSpec(
                    key="valuation",
                    title="Valuation",
                    parameters=["discount_rate"],
                ),
                ParameterGroupSpec(
                    key="creator",
                    title="Creator Economy",
                    parameters=["min_viable_earnings"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="platform_metrics",
                    title="Platform Metrics",
                    view_type=ViewType.METRIC_GRID,
                    description="Key platform performance metrics",
                    config={"metrics": ["ltv", "cac", "ltv_cac_ratio", "arpu"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="platform_metrics_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="network_effects",
                    title="Network Effects",
                    view_type=ViewType.LINE_CHART,
                    description="Network effect strength over time",
                    config={"x_field": "users", "y_fields": ["value", "elasticity"]},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="network_effects_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="creator_distribution",
                    title="Creator Earnings Distribution",
                    view_type=ViewType.HISTOGRAM,
                    description="Distribution of creator earnings with Gini coefficient",
                    config={"field": "earnings", "bins": 20},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="creator_distribution_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="revenue_breakdown",
                    title="Revenue Breakdown",
                    view_type=ViewType.BAR_CHART,
                    description="Revenue by monetization stream",
                    config={"x_field": "stream", "y_field": "revenue"},
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="revenue_breakdown_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_ltv(
        self,
        arpu: float,
        retention_rate: float,
        margin: float = 1.0,
    ) -> float:
        """
        Compute customer lifetime value.
        
        Args:
            arpu: Average revenue per user (monthly)
            retention_rate: Monthly retention rate (0-1)
            margin: Gross margin (0-1)
        
        Returns:
            Lifetime value
        """
        if retention_rate >= 1:
            return float('inf')
        
        churn_rate = 1 - retention_rate
        monthly_discount = self.discount_rate / 12
        
        # LTV = ARPU * Margin / (Churn + Discount Rate)
        ltv = (arpu * margin) / (churn_rate + monthly_discount)
        
        return ltv
    
    @requires_tier(Tier.PROFESSIONAL)
    def compute_ltv_cac_ratio(
        self,
        ltv: float,
        cac: float,
    ) -> float:
        """
        Compute LTV/CAC ratio.
        
        Args:
            ltv: Lifetime value
            cac: Customer acquisition cost
        
        Returns:
            LTV/CAC ratio (>3 is healthy)
        """
        if cac <= 0:
            return float('inf')
        return ltv / cac
    
    @requires_tier(Tier.PROFESSIONAL)
    def measure_network_effects(
        self,
        user_growth: list[float],
        value_growth: list[float],
        cross_side_users: Optional[list[float]] = None,
    ) -> NetworkEffects:
        """
        Measure network effect strength.
        
        Args:
            user_growth: Time series of user counts
            value_growth: Time series of value metrics (revenue, engagement)
            cross_side_users: Time series of cross-side user counts
        
        Returns:
            Network effects metrics
        """
        # Same-side elasticity (log-log regression)
        if len(user_growth) > 2 and len(value_growth) > 2:
            log_users = np.log(np.array(user_growth) + 1)
            log_value = np.log(np.array(value_growth) + 1)
            
            if len(log_users) == len(log_value):
                try:
                    slope, _, r_value, _, _ = stats.linregress(log_users, log_value)
                    same_side_elasticity = slope
                except Exception:
                    same_side_elasticity = 0.0
            else:
                same_side_elasticity = 0.0
        else:
            same_side_elasticity = 0.0
        
        # Cross-side elasticity
        cross_side_elasticity = 0.0
        if cross_side_users and len(cross_side_users) > 2:
            log_cross = np.log(np.array(cross_side_users) + 1)
            if len(log_cross) == len(log_value):
                try:
                    slope, _, _, _, _ = stats.linregress(log_cross, log_value)
                    cross_side_elasticity = slope
                except Exception:
                    pass
        
        # Network effect strength (composite)
        # Elasticity > 1 indicates strong network effects
        strength = min(100, max(0, (same_side_elasticity + cross_side_elasticity) * 50))
        
        # Critical mass detection (inflection point)
        if len(user_growth) > 10:
            growth_rates = np.diff(user_growth) / (np.array(user_growth[:-1]) + 1)
            max_growth_idx = np.argmax(growth_rates)
            tipping_point = int(user_growth[max_growth_idx])
            critical_mass = user_growth[-1] > tipping_point * 2
        else:
            tipping_point = 0
            critical_mass = False
        
        return NetworkEffects(
            same_side_elasticity=same_side_elasticity,
            cross_side_elasticity=cross_side_elasticity,
            critical_mass_reached=critical_mass,
            tipping_point_users=tipping_point,
            data_advantage_score=strength * 0.5,  # Data effects grow with network
            overall_strength=strength,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_take_rate(
        self,
        gmv: float,
        platform_revenue: float,
        industry: str = "marketplace",
    ) -> tuple[float, str]:
        """
        Analyze platform take rate.
        
        Args:
            gmv: Gross merchandise value
            platform_revenue: Platform's revenue
            industry: Industry for benchmarking
        
        Returns:
            Tuple of (take_rate, assessment)
        """
        take_rate = platform_revenue / gmv if gmv > 0 else 0
        
        # Industry benchmarks
        benchmarks = {
            "marketplace": (0.10, 0.20),  # (low, high)
            "food_delivery": (0.20, 0.35),
            "ride_sharing": (0.20, 0.30),
            "app_store": (0.15, 0.30),
            "saas": (0.00, 0.05),  # B2B SaaS typically lower
            "content": (0.30, 0.50),
        }
        
        low, high = benchmarks.get(industry.lower(), (0.10, 0.25))
        
        if take_rate < low:
            assessment = "Below industry benchmark - may be undermonetizing"
        elif take_rate > high:
            assessment = "Above industry benchmark - may face disintermediation risk"
        else:
            assessment = "Within industry benchmark"
        
        return take_rate, assessment
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_creator_economy(
        self,
        creator_earnings: np.ndarray,
        platform_take: float,
        min_viable_earnings: float = 50000,  # Annual
    ) -> CreatorEconomics:
        """
        Analyze creator economy metrics.
        
        Args:
            creator_earnings: Array of individual creator annual earnings
            platform_take: Platform's take rate
            min_viable_earnings: Minimum viable annual earnings
        
        Returns:
            Creator economics metrics
        """
        total_creators = len(creator_earnings)
        active_creators = sum(1 for e in creator_earnings if e > 0)
        
        # Earnings distribution
        total_earnings = np.sum(creator_earnings)
        median = float(np.median(creator_earnings))
        
        # Top 1% share (power law analysis)
        sorted_earnings = np.sort(creator_earnings)[::-1]
        top_1pct_count = max(1, int(total_creators * 0.01))
        top_1pct_earnings = np.sum(sorted_earnings[:top_1pct_count])
        top_1pct_share = top_1pct_earnings / total_earnings if total_earnings > 0 else 0
        
        # Gini coefficient
        n = len(creator_earnings)
        if n > 0 and np.sum(creator_earnings) > 0:
            sorted_e = np.sort(creator_earnings)
            cumsum = np.cumsum(sorted_e)
            gini = (2 * np.sum((np.arange(1, n + 1) * sorted_e))) / (n * cumsum[-1]) - (n + 1) / n
        else:
            gini = 0
        
        # Success metrics
        earning_min = sum(1 for e in creator_earnings if e >= min_viable_earnings)
        full_time = sum(1 for e in creator_earnings if e >= min_viable_earnings * 2)
        
        return CreatorEconomics(
            total_creators=total_creators,
            active_creators=active_creators,
            total_creator_earnings=float(total_earnings),
            median_earnings=median,
            top_1pct_share=top_1pct_share,
            gini_coefficient=gini,
            platform_take_rate=platform_take,
            creator_share=1 - platform_take,
            creators_earning_min_wage=earning_min,
            creators_full_time=full_time,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def analyze_marketplace(
        self,
        gmv: float,
        transactions: int,
        unique_buyers: int,
        unique_sellers: int,
        total_buyers: int,
        total_sellers: int,
    ) -> MarketplaceDynamics:
        """
        Analyze marketplace dynamics.
        
        Args:
            gmv: Gross merchandise value
            transactions: Total transactions
            unique_buyers: Unique transacting buyers
            unique_sellers: Unique transacting sellers
            total_buyers: Total registered buyers
            total_sellers: Total registered sellers
        
        Returns:
            Marketplace dynamics metrics
        """
        avg_value = gmv / transactions if transactions > 0 else 0
        
        # Liquidity metrics
        buyer_liquidity = unique_buyers / total_buyers if total_buyers > 0 else 0
        seller_liquidity = unique_sellers / total_sellers if total_sellers > 0 else 0
        
        # Match rate (simplified)
        potential_matches = min(total_buyers, total_sellers)
        actual_matches = min(unique_buyers, unique_sellers)
        match_rate = actual_matches / potential_matches if potential_matches > 0 else 0
        
        return MarketplaceDynamics(
            gmv=gmv,
            transactions=transactions,
            avg_transaction_value=avg_value,
            buyer_liquidity=buyer_liquidity,
            seller_liquidity=seller_liquidity,
            match_rate=match_rate,
            avg_rating=0.0,
            dispute_rate=0.0,
            repeat_transaction_rate=0.0,
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def value_platform(
        self,
        revenue: float,
        revenue_growth: float,
        active_users: int,
        gmv: Optional[float] = None,
    ) -> PlatformValuation:
        """
        Value a platform business.
        
        Args:
            revenue: Annual revenue
            revenue_growth: Revenue growth rate
            active_users: Monthly active users
            gmv: Gross merchandise value (for marketplaces)
        
        Returns:
            Platform valuation
        """
        # Revenue multiple (growth-adjusted)
        if revenue_growth > 0.50:
            revenue_multiple = 15
        elif revenue_growth > 0.30:
            revenue_multiple = 10
        elif revenue_growth > 0.15:
            revenue_multiple = 6
        else:
            revenue_multiple = 4
        
        enterprise_value = revenue * revenue_multiple
        
        # Value per user
        value_per_user = enterprise_value / active_users if active_users > 0 else 0
        
        # GMV multiple (for marketplaces)
        gmv_multiple = enterprise_value / gmv if gmv and gmv > 0 else 0
        
        return PlatformValuation(
            value_per_user=value_per_user,
            value_per_active_user=value_per_user,
            multiple_of_gmv=gmv_multiple,
            multiple_of_revenue=revenue_multiple,
            peg_ratio=revenue_multiple / (revenue_growth * 100) if revenue_growth > 0 else 0,
            enterprise_value=enterprise_value,
            equity_value=enterprise_value * 0.9,  # Assuming 10% debt
        )
    
    @requires_tier(Tier.PROFESSIONAL)
    def full_analysis(
        self,
        sides: list[MarketSide],
        platform_type: PlatformType = PlatformType.MARKETPLACE,
        user_growth: Optional[list[float]] = None,
        revenue_growth: Optional[list[float]] = None,
    ) -> PlatformMetrics:
        """
        Complete platform economics analysis.
        
        Args:
            sides: Market sides data
            platform_type: Type of platform
            user_growth: Historical user growth
            revenue_growth: Historical revenue growth
        
        Returns:
            Complete platform metrics
        """
        # Network effects
        user_growth = user_growth or [s.total_users for s in sides]
        revenue_growth = revenue_growth or [1.0]
        
        network_effects = self.measure_network_effects(
            user_growth,
            revenue_growth,
        )
        
        # Monetization
        total_revenue = sum(s.arpu * s.active_users for s in sides)
        
        monetization = PlatformMonetization(
            model=MonetizationType.HYBRID,
            total_revenue=total_revenue,
            gross_margin=0.70,  # Typical for platforms
            contribution_margin=0.50,
        )
        
        # Valuation
        total_active = sum(s.active_users for s in sides)
        growth = (revenue_growth[-1] - revenue_growth[0]) / revenue_growth[0] if len(revenue_growth) > 1 else 0.20
        
        valuation = self.value_platform(
            total_revenue,
            growth,
            total_active,
        )
        
        return PlatformMetrics(
            platform_type=platform_type,
            sides=sides,
            network_effects=network_effects,
            monetization=monetization,
            valuation=valuation,
        )
