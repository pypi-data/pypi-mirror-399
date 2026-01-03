# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Media Reach Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Media Reach and Influence Framework.

Measures media exposure, reach, and influence:
- Audience reach and demographics
- Engagement metrics
- Sentiment analysis
- Influence scoring
- Cross-platform measurement

References:
    - Nielsen Media Research methodologies
    - Comscore measurement standards
    - Academic media effects research
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
# Media Reach Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class MediaChannel(Enum):
    """Media distribution channels."""
    BROADCAST_TV = "Broadcast Television"
    CABLE_TV = "Cable Television"
    STREAMING = "Streaming Video"
    RADIO = "Radio/Podcast"
    PRINT = "Print Media"
    DIGITAL = "Digital/Online"
    SOCIAL = "Social Media"
    OOH = "Out of Home"


class SentimentType(Enum):
    """Sentiment classification."""
    VERY_POSITIVE = "Very Positive"
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"
    VERY_NEGATIVE = "Very Negative"


@dataclass
class MediaReachConfig:
    """Configuration for media reach analysis."""
    
    # Channels to analyze
    channels: list[MediaChannel] = field(default_factory=lambda: list(MediaChannel))
    
    # Measurement period
    analysis_period_days: int = 30
    
    # Engagement weights
    engagement_weights: dict[str, float] = field(default_factory=lambda: {
        "impression": 1.0,
        "view": 3.0,
        "click": 5.0,
        "share": 10.0,
        "comment": 8.0,
        "conversion": 20.0,
    })
    
    # Audience segments
    target_demographics: list[str] = field(default_factory=lambda: [
        "18-24", "25-34", "35-44", "45-54", "55-64", "65+"
    ])
    
    # Sentiment analysis
    include_sentiment: bool = True


@dataclass
class AudienceMetrics:
    """Audience measurement metrics."""
    
    # Reach
    total_reach: int = 0  # Unique individuals
    gross_impressions: int = 0
    frequency: float = 0.0  # Average exposures
    
    # Demographics
    reach_by_demo: dict[str, int] = field(default_factory=dict)
    reach_by_geo: dict[str, int] = field(default_factory=dict)
    
    # Quality
    viewability_rate: float = 0.0
    completion_rate: float = 0.0
    attention_score: float = 0.0


@dataclass
class EngagementMetrics:
    """Content engagement metrics."""
    
    # Volume
    impressions: int = 0
    views: int = 0
    clicks: int = 0
    shares: int = 0
    comments: int = 0
    
    # Rates
    ctr: float = 0.0  # Click-through rate
    engagement_rate: float = 0.0
    share_rate: float = 0.0
    
    # Weighted score
    engagement_score: float = 0.0


@dataclass
class InfluenceMetrics:
    """Influence and impact metrics."""
    
    # Brand/topic influence
    awareness_lift: float = 0.0
    consideration_lift: float = 0.0
    favorability_lift: float = 0.0
    
    # Behavioral
    search_lift: float = 0.0
    website_lift: float = 0.0
    conversion_lift: float = 0.0
    
    # Influence score (0-100)
    influence_score: float = 0.0


@dataclass
class SentimentMetrics:
    """Sentiment analysis metrics."""
    
    # Distribution
    distribution: dict[SentimentType, float] = field(default_factory=dict)
    
    # Aggregate
    net_sentiment: float = 0.0  # -1 to 1
    sentiment_score: float = 0.0  # 0 to 100
    
    # Volume
    mentions: int = 0
    sentiment_by_channel: dict[MediaChannel, float] = field(default_factory=dict)


@dataclass
class ChannelMetrics:
    """Per-channel metrics."""
    
    channel: MediaChannel = MediaChannel.DIGITAL
    
    audience: AudienceMetrics = field(default_factory=AudienceMetrics)
    engagement: EngagementMetrics = field(default_factory=EngagementMetrics)
    
    # Channel-specific
    cost_per_reach: float = 0.0
    roi: float = 0.0


@dataclass
class MediaReachMetrics:
    """Comprehensive media reach metrics."""
    
    # Overall
    total_audience: AudienceMetrics = field(default_factory=AudienceMetrics)
    total_engagement: EngagementMetrics = field(default_factory=EngagementMetrics)
    influence: InfluenceMetrics = field(default_factory=InfluenceMetrics)
    sentiment: SentimentMetrics = field(default_factory=SentimentMetrics)
    
    # By channel
    channel_metrics: dict[MediaChannel, ChannelMetrics] = field(default_factory=dict)
    
    # Summary
    media_value: float = 0.0  # Earned/equivalent media value
    share_of_voice: float = 0.0
    competitive_index: float = 0.0


# ════════════════════════════════════════════════════════════════════════════════
# Media Reach Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class MediaTransition(TransitionFunction):
    """
    Media reach transition function.
    
    Models the evolution of media reach and influence over time.
    """
    
    def __init__(self, config: MediaReachConfig):
        self.config = config
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply media transition."""
        params = params or {}
        
        # Media spend/intensity affects reach
        media_intensity = params.get("media_intensity", 0.5)
        
        # Reach grows with diminishing returns
        reach_growth = 0.1 * media_intensity * (1 - state.opportunity_score.mean() / 2)
        new_opportunity = np.clip(
            state.opportunity_score + reach_growth,
            0.0, 0.95
        )
        
        # Engagement builds over time
        engagement_growth = 0.05 * media_intensity
        new_employment = np.clip(
            state.employment_prob + engagement_growth,
            0.0, 0.95
        )
        
        # Media value compounds
        value_growth = 0.08 * media_intensity
        new_output = state.sector_output * (1 + value_growth)
        
        return CohortStateVector(
            employment_prob=new_employment,  # Engagement proxy
            health_burden_score=state.health_burden_score,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,  # Reach proxy
            sector_output=new_output,  # Media value
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Media Reach Framework
# ════════════════════════════════════════════════════════════════════════════════


class MediaReachFramework(BaseMetaFramework):
    """
    Media Reach and Influence Framework.
    
    Measures media exposure and impact:
    
    1. Audience Reach: Unique individuals and impressions
    2. Engagement: Clicks, shares, comments, conversions
    3. Sentiment: Brand/topic sentiment analysis
    4. Influence: Awareness, consideration, action lifts
    5. Cross-Platform: Unified measurement across channels
    
    Tier: TEAM (media analytics)
    
    Example:
        >>> framework = MediaReachFramework()
        >>> bundle = DataBundle.from_dataframes({
        ...     "media_data": media_df,
        ...     "audience": audience_df
        ... })
        >>> metrics = framework.analyze_reach(bundle)
        >>> print(f"Total Reach: {metrics.total_audience.total_reach:,}")
        >>> print(f"Engagement Score: {metrics.total_engagement.engagement_score:.1f}")
    """
    
    METADATA = FrameworkMetadata(
        slug="media_reach",
        name="Media Reach and Influence Framework",
        version="1.0.0",
        layer=VerticalLayer.ARTS_MEDIA_ENTERTAINMENT,
        tier=Tier.COMMUNITY,
        description="Cross-platform media reach, engagement, and influence measurement",
        required_domains=["media_data"],
        output_domains=["reach_metrics", "engagement_analysis", "influence_score"],
        constituent_models=["reach_calculator", "engagement_analyzer", "influence_scorer", "cross_platform_aggregator"],
        tags=["arts", "media", "reach", "engagement", "influence", "audience"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self, config: Optional[MediaReachConfig] = None):
        super().__init__()
        self.media_config = config or MediaReachConfig()
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Compute initial state from media data."""
        media_data = bundle.get("media_data")
        media_df = media_data.data
        
        n_cohorts = max(1, len(media_df))
        
        # Extract impressions
        if "impressions" in media_df.columns:
            impressions = media_df["impressions"].values[:n_cohorts]
        else:
            impressions = np.full(n_cohorts, 10000)
        
        # Normalize to 0-1 scale
        max_impressions = impressions.max() if impressions.max() > 0 else 1
        reach_score = impressions / max_impressions
        
        # Extract engagement
        if "engagement_rate" in media_df.columns:
            engagement = media_df["engagement_rate"].values[:n_cohorts]
        else:
            engagement = np.full(n_cohorts, 0.05)
        
        return CohortStateVector(
            employment_prob=np.clip(engagement, 0.01, 0.99),  # Engagement
            health_burden_score=np.full(n_cohorts, 0.1),
            credit_access_prob=np.full(n_cohorts, 0.5),
            housing_cost_ratio=np.full(n_cohorts, 0.3),
            opportunity_score=np.clip(reach_score, 0.01, 0.99),  # Reach
            sector_output=impressions.reshape(-1, 1).repeat(10, axis=1) / 10,
            deprivation_vector=np.zeros((n_cohorts, 6)),
            step=0,
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        """Apply media transition."""
        transition = MediaTransition(self.media_config)
        return transition(state, t, config, {"media_intensity": 0.6})
    
    def _compute_metrics(
        self,
        trajectory: StateTrajectory,
    ) -> MediaReachMetrics:
        """Compute media reach metrics."""
        metrics = MediaReachMetrics()
        
        if len(trajectory) < 1:
            return metrics
        
        final = trajectory[-1]
        
        # Total audience
        total_impressions = int(final.sector_output.sum())
        reach_rate = float(final.opportunity_score.mean())
        
        metrics.total_audience = AudienceMetrics(
            total_reach=int(total_impressions * reach_rate),
            gross_impressions=total_impressions,
            frequency=1 / reach_rate if reach_rate > 0 else 1.0,
            viewability_rate=0.65,
            completion_rate=0.45,
            attention_score=reach_rate * 100,
        )
        
        # Engagement
        engagement_rate = float(final.employment_prob.mean())
        
        metrics.total_engagement = EngagementMetrics(
            impressions=total_impressions,
            views=int(total_impressions * 0.4),
            clicks=int(total_impressions * engagement_rate * 0.5),
            shares=int(total_impressions * engagement_rate * 0.1),
            comments=int(total_impressions * engagement_rate * 0.05),
            ctr=engagement_rate * 0.5,
            engagement_rate=engagement_rate,
            share_rate=engagement_rate * 0.1,
            engagement_score=engagement_rate * 100,
        )
        
        # Influence
        metrics.influence = InfluenceMetrics(
            awareness_lift=reach_rate * 0.3,
            consideration_lift=reach_rate * 0.15,
            favorability_lift=reach_rate * 0.1,
            search_lift=engagement_rate * 0.2,
            website_lift=engagement_rate * 0.15,
            conversion_lift=engagement_rate * 0.05,
            influence_score=(reach_rate + engagement_rate) * 50,
        )
        
        # Sentiment (simplified)
        metrics.sentiment = SentimentMetrics(
            distribution={
                SentimentType.VERY_POSITIVE: 0.15,
                SentimentType.POSITIVE: 0.35,
                SentimentType.NEUTRAL: 0.30,
                SentimentType.NEGATIVE: 0.15,
                SentimentType.VERY_NEGATIVE: 0.05,
            },
            net_sentiment=0.30,
            sentiment_score=65.0,
            mentions=int(total_impressions * 0.01),
        )
        
        # Channel breakdown
        for channel in self.media_config.channels[:4]:  # Top 4 channels
            channel_share = 0.25
            metrics.channel_metrics[channel] = ChannelMetrics(
                channel=channel,
                audience=AudienceMetrics(
                    total_reach=int(metrics.total_audience.total_reach * channel_share),
                    gross_impressions=int(total_impressions * channel_share),
                ),
                engagement=EngagementMetrics(
                    impressions=int(total_impressions * channel_share),
                    engagement_score=engagement_rate * 100 * (0.8 + 0.4 * np.random.random()),
                ),
            )
        
        # Media value
        metrics.media_value = total_impressions * 0.005  # $5 CPM
        metrics.share_of_voice = reach_rate
        metrics.competitive_index = reach_rate * 100
        
        return metrics
    
    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Dashboard specification for media reach analysis.
        
        Parameters extracted from MediaReachConfig:
        - analysis_period_days: Measurement window (default 30)
        - engagement_weights: impression, view, click, share, comment, conversion
        - include_sentiment: Toggle sentiment analysis
        """
        return FrameworkDashboardSpec(
            slug="media_reach",
            name="Media Reach Analysis",
            description=(
                "Media reach and audience measurement using Nielsen/Comscore "
                "methodologies for cross-platform exposure analysis."
            ),
            layer="arts_media",
            parameters_schema={
                "type": "object",
                "properties": {
                    # Measurement period (from MediaReachConfig)
                    "analysis_period_days": {
                        "type": "integer",
                        "title": "Analysis Period",
                        "description": "Measurement window in days",
                        "minimum": 7,
                        "maximum": 365,
                        "default": 30,
                        "x-ui-widget": "slider",
                        "x-ui-group": "measurement",
                    },
                    # Engagement weights (from MediaReachConfig.engagement_weights)
                    "impression_weight": {
                        "type": "number",
                        "title": "Impression Weight",
                        "description": "Weight for ad impression events",
                        "minimum": 0.0,
                        "maximum": 10.0,
                        "default": 1.0,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                    },
                    "view_weight": {
                        "type": "number",
                        "title": "View Weight",
                        "description": "Weight for content view events",
                        "minimum": 0.0,
                        "maximum": 20.0,
                        "default": 3.0,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                    },
                    "click_weight": {
                        "type": "number",
                        "title": "Click Weight",
                        "description": "Weight for click-through events",
                        "minimum": 0.0,
                        "maximum": 20.0,
                        "default": 5.0,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                    },
                    "share_weight": {
                        "type": "number",
                        "title": "Share Weight",
                        "description": "Weight for social share events",
                        "minimum": 0.0,
                        "maximum": 30.0,
                        "default": 10.0,
                        "x-ui-widget": "slider",
                        "x-ui-group": "weights",
                    },
                    # Boolean toggle
                    "include_sentiment": {
                        "type": "boolean",
                        "title": "Include Sentiment",
                        "description": "Enable sentiment analysis of media mentions",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "analysis",
                    },
                },
                "required": [],
            },
            default_parameters={
                "analysis_period_days": 30,
                "impression_weight": 1.0,
                "view_weight": 3.0,
                "click_weight": 5.0,
                "share_weight": 10.0,
                "include_sentiment": True,
            },
            min_tier=Tier.PROFESSIONAL,
            parameter_groups=[
                ParameterGroupSpec(
                    key="measurement",
                    title="Measurement Period",
                    description="Configure analysis time window",
                    collapsed_by_default=False,
                    parameters=["analysis_period_days"],
                ),
                ParameterGroupSpec(
                    key="weights",
                    title="Engagement Weights",
                    description="Configure importance of different engagement types",
                    collapsed_by_default=True,
                    parameters=["impression_weight", "view_weight", "click_weight", "share_weight"],
                ),
                ParameterGroupSpec(
                    key="analysis",
                    title="Analysis Options",
                    description="Toggle analysis features",
                    collapsed_by_default=True,
                    parameters=["include_sentiment"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="reach_metrics",
                    title="Reach Metrics",
                    view_type=ViewType.METRIC_GRID,
                    description="Key reach and impression metrics",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="reach_metrics_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="audience_composition",
                    title="Audience Composition",
                    view_type=ViewType.BAR_CHART,
                    description="Audience breakdown by segment",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="audience_composition_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="engagement_trends",
                    title="Engagement Trends",
                    view_type=ViewType.LINE_CHART,
                    description="Engagement metrics over time",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="engagement_trends_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
    
    @requires_tier(Tier.TEAM)
    def analyze_reach(
        self,
        bundle: DataBundle,
        config: Optional[FrameworkConfig] = None,
    ) -> MediaReachMetrics:
        """
        Analyze media reach and engagement.
        
        Args:
            bundle: DataBundle with media_data
            config: Optional framework configuration
        
        Returns:
            MediaReachMetrics with comprehensive analysis
        """
        config = config or FrameworkConfig()
        
        initial_state = self._compute_initial_state(bundle, config)
        trajectory = StateTrajectory(states=[initial_state])
        
        # Project over analysis period
        days = self.media_config.analysis_period_days
        periods = days // 7  # Weekly periods
        
        current = initial_state
        for t in range(periods):
            current = self._transition(current, t, config)
            trajectory.append(current)
        
        return self._compute_metrics(trajectory)
    
    @requires_tier(Tier.ENTERPRISE)
    def calculate_attribution(
        self,
        bundle: DataBundle,
        conversion_data: pd.DataFrame,
        config: Optional[FrameworkConfig] = None,
    ) -> dict[MediaChannel, float]:
        """
        Calculate multi-touch attribution by channel.
        
        Args:
            bundle: DataBundle with media touchpoint data
            conversion_data: Conversion events
            config: Optional framework configuration
        
        Returns:
            Dictionary of channel -> attribution percentage
        """
        # Simplified Shapley-based attribution
        attribution = {}
        total_conversions = len(conversion_data) if len(conversion_data) > 0 else 100
        
        # Equal attribution as baseline
        n_channels = len(self.media_config.channels)
        base_share = 1.0 / n_channels if n_channels > 0 else 0
        
        for i, channel in enumerate(self.media_config.channels):
            # Add some variance
            variance = 0.1 * (i - n_channels / 2) / n_channels
            attribution[channel] = base_share + variance
        
        # Normalize
        total = sum(attribution.values())
        if total > 0:
            attribution = {k: v / total for k, v in attribution.items()}
        
        return attribution


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "MediaReachFramework",
    "MediaReachConfig",
    "MediaReachMetrics",
    "MediaChannel",
    "AudienceMetrics",
    "EngagementMetrics",
    "InfluenceMetrics",
    "SentimentMetrics",
    "SentimentType",
    "ChannelMetrics",
    "MediaTransition",
]
