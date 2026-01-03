from __future__ import annotations
#!/usr/bin/env python3
# ════════════════════════════════════════════════════════════════════════════════
# Spatial-Causal-Index Framework
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Spatial-Causal-Index Framework: Hybrid Spatial-Causal-Index Modeling.

This framework combines three methodological approaches:
1. **Spatial Analysis**: Geographic spillovers and neighborhood effects
2. **Causal Inference**: Identification of causal relationships
3. **Index Construction**: Composite indicators with dimensionality reduction

Use Cases:
    - Regional policy evaluation with spatial spillovers
    - Composite index construction with causal validation
    - Geographic inequality analysis with causal attribution
    - Network effects in socioeconomic outcomes

Methodology:
    1. Construct spatial weight matrix (distance, contiguity, or network-based)
    2. Build composite index from multiple indicators
    3. Identify causal effects using spatial causal inference
    4. Estimate direct, indirect (spillover), and total effects

References:
    - Anselin, L. (1988). "Spatial Econometrics: Methods and Models."
    - LeSage, J., & Pace, R. K. (2009). "Introduction to Spatial Econometrics."
    - Chagas, A. L. S., et al. (2016). "A spatial difference-in-differences analysis."
"""

import logging
from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.spatial import distance_matrix

from krl_frameworks.core.base import BaseMetaFramework, FrameworkMetadata, CohortStateVector
from krl_frameworks.core.config import FrameworkConfig
from krl_frameworks.core.dashboard_spec import (
    FrameworkDashboardSpec,
    ParameterGroupSpec,
    OutputViewSpec,
    ViewType,
    ResultClass,
    TemporalSemantics,
)
from krl_frameworks.core.data_bundle import DataBundle, DataDomain
from krl_frameworks.core.registry import Tier, VerticalLayer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpatialCausalIndexConfig:
    """Configuration for Spatial-Causal-Index Framework."""

    # Spatial configuration
    n_regions: int = 50  # Number of geographic units
    spatial_weight_type: Literal["distance", "contiguity", "knn"] = "distance"
    distance_decay_param: float = 1.0  # For distance-based weights
    k_neighbors: int = 5  # For KNN weights

    # Index construction
    n_indicators: int = 5  # Number of indicators in composite index
    index_aggregation: Literal["equal", "pca", "weighted"] = "pca"

    # Causal inference
    treatment_effect_heterogeneity: bool = True  # Spatially varying effects
    spatial_lag_order: int = 1  # Order of spatial lag (1 = direct neighbors)


class SpatialCausalIndexFramework(BaseMetaFramework):
    """
    Spatial-Causal-Index Framework.

    Combines spatial econometrics, causal inference, and composite index
    construction for analyzing geographic heterogeneity in policy impacts.

    Attributes:
        config: SpatialCausalIndexConfig instance.
    """

    METADATA = FrameworkMetadata(
        slug="spatial_causal_index",
        name="Spatial-Causal-Index Framework",
        version="1.0.0",
        description=(
            "Hybrid spatial-causal-index framework for analyzing geographic spillovers, "
            "causal effects, and composite indicators with spatial heterogeneity. "
            "Combines spatial econometrics with causal inference methods."
        ),
        tier=Tier.PROFESSIONAL,
        layer=VerticalLayer.SOCIOECONOMIC_ACADEMIC,
        required_domains=[
            DataDomain.SPATIAL.value,  # Geographic coordinates or adjacency
            DataDomain.ECONOMIC.value,
            DataDomain.SOCIAL.value,
        ],
        tags=[
            "spatial-econometrics",
            "causal-inference",
            "composite-index",
            "spillover-effects",
            "geographic-analysis",
        ],
    )

    def __init__(self, config: SpatialCausalIndexConfig | None = None):
        """
        Initialize Spatial-Causal-Index framework.

        Args:
            config: Framework configuration.
        """
        super().__init__()
        self.config = config or SpatialCausalIndexConfig()

        # Spatial weight matrix (initialized in _compute_initial_state)
        self._spatial_weights: np.ndarray | None = None
        self._region_coordinates: np.ndarray | None = None

        # Index components
        self._indicator_values: np.ndarray | None = None  # (n_regions, n_indicators)
        self._index_weights: np.ndarray | None = None  # (n_indicators,)

    def _compute_initial_state(
        self, data: DataBundle
    ) -> CohortStateVector:
        """
        Compute initial state with spatial index construction.

        Args:
            data: DataBundle with spatial, economic, social domains.
            config: Framework configuration.

        Returns:
            Initial CohortStateVector with spatial index.
        """
        n_regions = self.config.n_regions
        n_indicators = self.config.n_indicators

        # 1. Extract spatial data (coordinates or adjacency matrix)
        spatial_df = data.get_dataframe(DataDomain.SPATIAL.value)

        if spatial_df is not None and "latitude" in spatial_df.columns:
            # Real spatial coordinates
            self._region_coordinates = spatial_df[["latitude", "longitude"]].values[:n_regions]
        else:
            # Generate synthetic spatial coordinates (grid layout)
            self._region_coordinates = self._generate_grid_coordinates(n_regions)

        # 2. Construct spatial weight matrix
        self._spatial_weights = self._construct_spatial_weights()

        # 3. Extract or generate indicator data
        economic_df = data.get_dataframe(DataDomain.ECONOMIC.value)
        social_df = data.get_dataframe(DataDomain.SOCIAL.value)

        if economic_df is not None and social_df is not None:
            # Extract real indicators
            self._indicator_values = self._extract_indicators_from_data(
                economic_df, social_df, n_regions, n_indicators
            )
        else:
            # Generate synthetic indicators with spatial autocorrelation
            self._indicator_values = self._generate_spatially_correlated_indicators(
                n_regions, n_indicators
            )

        # 4. Construct composite index
        index_values, index_weights = self._construct_composite_index()
        self._index_weights = index_weights

        # 5. Estimate spatial effects (Moran's I for spatial autocorrelation)
        morans_i = self._calculate_morans_i(index_values)

        # 6. Construct state vector
        # Use sector_output to store index values by region
        # Use deprivation_vector for spatial statistics
        state = CohortStateVector(
            sector_output=index_values,  # Composite index by region (n_regions,)
            health_burden_score=np.zeros(n_regions),  # Placeholder
            opportunity_score=np.ones(n_regions),  # Baseline = 1.0
            credit_access_prob=np.ones(n_regions) * 0.5,  # Placeholder
            employment_prob=np.ones(n_regions) / n_regions,  # Equal shares
            housing_cost_ratio=np.ones(n_regions) * 0.3,  # Placeholder
            deprivation_vector=np.array([morans_i, 0.0]),  # [Moran's I, treatment effect]
        )

        logger.info(
            f"Spatial-Causal-Index initial state: {n_regions} regions, "
            f"{n_indicators} indicators, Moran's I={morans_i:.3f}"
        )

        return state

    def _transition(
        self, state: CohortStateVector, step: int
    ) -> CohortStateVector:
        """
        Transition with spatial causal effects.

        Args:
            state: Current state.
            step: Time step.
            config: Framework configuration.

        Returns:
            New state with spatial spillovers.
        """
        n_regions = len(state.sector_output)

        # 1. Simulate treatment (policy intervention in some regions)
        treatment = self._simulate_treatment(n_regions, step)

        # 2. Estimate causal effects with spatial spillovers
        direct_effect, spillover_effect = self._estimate_spatial_causal_effects(
            state.sector_output, treatment
        )

        # 3. Apply treatment effects
        new_index = state.sector_output.copy()
        new_index += treatment * direct_effect  # Direct effect

        # 4. Apply spatial spillovers (spatial lag)
        spatial_spillover = self._spatial_weights @ (treatment * spillover_effect)
        new_index += spatial_spillover

        # 5. Update spatial statistics
        new_morans_i = self._calculate_morans_i(new_index)
        total_treatment_effect = direct_effect + spillover_effect

        # 6. Construct new state
        new_state = CohortStateVector(
            sector_output=new_index,
            health_burden_score=state.health_burden_score,
            opportunity_score=state.opportunity_score,
            credit_access_prob=state.credit_access_prob,
            employment_prob=state.employment_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            deprivation_vector=np.array([new_morans_i, total_treatment_effect]),
        )

        return new_state

    def _compute_metrics(self, state: CohortStateVector) -> dict:
        """
        Compute spatial-causal-index metrics.

        Args:
            state: Current state.

        Returns:
            Dictionary of metrics.
        """
        index_values = state.sector_output
        morans_i = state.deprivation_vector[0]
        treatment_effect = state.deprivation_vector[1]

        # Spatial statistics
        global_mean = index_values.mean()
        spatial_variance = np.var(index_values)

        # Regional statistics
        min_region = int(np.argmin(index_values))
        max_region = int(np.argmax(index_values))

        # Hot spots (regions with high index AND high neighbors)
        spatial_lag = self._spatial_weights @ index_values
        hot_spots = (index_values > index_values.mean()) & (spatial_lag > spatial_lag.mean())

        metrics = {
            "global_index_mean": float(global_mean),
            "spatial_variance": float(spatial_variance),
            "morans_i": float(morans_i),
            "treatment_effect": float(treatment_effect),
            "index_values": index_values.tolist(),
            "min_index_region": min_region,
            "max_index_region": max_region,
            "hot_spot_count": int(hot_spots.sum()),
            "hot_spot_fraction": float(hot_spots.mean()),
            "indicator_weights": self._index_weights.tolist() if self._index_weights is not None else [],
        }

        return metrics

    # ═══════════════════════════════════════════════════════════════════════════
    # Spatial Weight Matrix Construction
    # ═══════════════════════════════════════════════════════════════════════════

    def _construct_spatial_weights(self) -> np.ndarray:
        """
        Construct spatial weight matrix.

        Returns:
            Normalized spatial weight matrix (n_regions, n_regions).
        """
        n_regions = self.config.n_regions

        if self.config.spatial_weight_type == "distance":
            # Distance-based weights with decay
            dist_matrix = distance_matrix(self._region_coordinates, self._region_coordinates)
            weights = 1.0 / (dist_matrix + 1e-8) ** self.config.distance_decay_param
            np.fill_diagonal(weights, 0)  # No self-weight

        elif self.config.spatial_weight_type == "knn":
            # K-nearest neighbors
            dist_matrix = distance_matrix(self._region_coordinates, self._region_coordinates)
            weights = np.zeros((n_regions, n_regions))
            for i in range(n_regions):
                k_nearest = np.argsort(dist_matrix[i])[1:self.config.k_neighbors + 1]
                weights[i, k_nearest] = 1.0

        else:  # contiguity (simplified: threshold distance)
            dist_matrix = distance_matrix(self._region_coordinates, self._region_coordinates)
            threshold = np.percentile(dist_matrix, 20)  # 20th percentile
            weights = (dist_matrix < threshold).astype(float)
            np.fill_diagonal(weights, 0)

        # Row-normalize weights
        row_sums = weights.sum(axis=1, keepdims=True)
        weights = weights / (row_sums + 1e-8)

        return weights

    # ═══════════════════════════════════════════════════════════════════════════
    # Composite Index Construction
    # ═══════════════════════════════════════════════════════════════════════════

    def _construct_composite_index(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Construct composite index from indicators.

        Returns:
            Tuple of (index_values, indicator_weights).
        """
        n_regions, n_indicators = self._indicator_values.shape

        if self.config.index_aggregation == "equal":
            # Equal weights
            weights = np.ones(n_indicators) / n_indicators
            index_values = self._indicator_values @ weights

        elif self.config.index_aggregation == "pca":
            # PCA-based weights (first principal component)
            # Standardize indicators
            mean = self._indicator_values.mean(axis=0)
            std = self._indicator_values.std(axis=0) + 1e-8
            standardized = (self._indicator_values - mean) / std

            # Compute covariance matrix
            cov_matrix = np.cov(standardized.T)

            # Eigenvalue decomposition
            eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

            # First principal component (largest eigenvalue)
            pc1 = eigenvectors[:, -1]
            weights = np.abs(pc1) / np.abs(pc1).sum()  # Normalize to sum to 1

            index_values = standardized @ pc1

        else:  # weighted (example: by variance explained)
            variances = self._indicator_values.var(axis=0)
            weights = variances / variances.sum()
            index_values = self._indicator_values @ weights

        return index_values, weights

    # ═══════════════════════════════════════════════════════════════════════════
    # Spatial Causal Inference
    # ═══════════════════════════════════════════════════════════════════════════

    def _simulate_treatment(self, n_regions: int, step: int) -> np.ndarray:
        """
        Simulate treatment assignment (e.g., policy intervention).

        Args:
            n_regions: Number of regions.
            step: Time step.

        Returns:
            Binary treatment indicator (n_regions,).
        """
        # Treatment in 30% of regions starting at step 5
        if step < 5:
            return np.zeros(n_regions)

        treatment_prob = 0.3
        return (np.random.rand(n_regions) < treatment_prob).astype(float)

    def _estimate_spatial_causal_effects(
        self, outcomes: np.ndarray, treatment: np.ndarray
    ) -> tuple[float, float]:
        """
        Estimate spatial causal effects using spatial lag model.

        Args:
            outcomes: Outcome variable (index values).
            treatment: Treatment indicator.

        Returns:
            Tuple of (direct_effect, spillover_effect).
        """
        # Spatial lag of treatment
        spatial_lag_treatment = self._spatial_weights @ treatment

        # Simple regression: Y ~ treatment + spatial_lag(treatment)
        # (In full implementation, would use spatial econometric estimators)

        # Direct effect: Average outcome difference for treated vs control
        treated_idx = treatment > 0.5
        if treated_idx.sum() > 0 and (~treated_idx).sum() > 0:
            direct_effect = outcomes[treated_idx].mean() - outcomes[~treated_idx].mean()
        else:
            direct_effect = 0.0

        # Spillover effect: Correlation of neighbors' treatment with outcome
        if spatial_lag_treatment.std() > 1e-8:
            correlation = np.corrcoef(outcomes, spatial_lag_treatment)[0, 1]
            spillover_effect = correlation * outcomes.std() * 0.3  # Scaled spillover
        else:
            spillover_effect = 0.0

        return direct_effect, spillover_effect

    def _calculate_morans_i(self, values: np.ndarray) -> float:
        """
        Calculate Moran's I spatial autocorrelation statistic.

        Args:
            values: Values by region.

        Returns:
            Moran's I (-1 to 1, 0 = no autocorrelation).
        """
        n = len(values)
        mean = values.mean()
        deviations = values - mean

        # Numerator: sum of (w_ij * (x_i - mean) * (x_j - mean))
        numerator = 0.0
        for i in range(n):
            for j in range(n):
                numerator += self._spatial_weights[i, j] * deviations[i] * deviations[j]

        # Denominator: sum of (x_i - mean)^2
        denominator = (deviations ** 2).sum()

        # Sum of all weights
        sum_weights = self._spatial_weights.sum()

        # Moran's I
        morans_i = (n / sum_weights) * (numerator / denominator) if denominator > 1e-8 else 0.0

        return morans_i

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _generate_grid_coordinates(self, n_regions: int) -> np.ndarray:
        """
        Generate grid coordinates for synthetic spatial data.

        Args:
            n_regions: Number of regions.

        Returns:
            Coordinates array (n_regions, 2).
        """
        grid_size = int(np.ceil(np.sqrt(n_regions)))
        coords = []
        for i in range(grid_size):
            for j in range(grid_size):
                if len(coords) < n_regions:
                    coords.append([i, j])
        return np.array(coords[:n_regions], dtype=float)

    def _generate_spatially_correlated_indicators(
        self, n_regions: int, n_indicators: int
    ) -> np.ndarray:
        """
        Generate synthetic indicators with spatial autocorrelation.

        Args:
            n_regions: Number of regions.
            n_indicators: Number of indicators.

        Returns:
            Indicator matrix (n_regions, n_indicators).
        """
        indicators = np.random.randn(n_regions, n_indicators)

        # Add spatial autocorrelation by smoothing with spatial lag
        for _ in range(3):  # Multiple passes for stronger correlation
            indicators = 0.7 * indicators + 0.3 * (self._spatial_weights @ indicators)

        return indicators

    def _extract_indicators_from_data(
        self,
        economic_df,
        social_df,
        n_regions: int,
        n_indicators: int,
    ) -> np.ndarray:
        """
        Extract real indicators from data.

        Args:
            economic_df: Economic domain DataFrame.
            social_df: Social domain DataFrame.
            n_regions: Number of regions.
            n_indicators: Number of indicators to extract.

        Returns:
            Indicator matrix (n_regions, n_indicators).
        """
        # Placeholder: In real implementation, would extract specific columns
        # For now, generate synthetic data
        return self._generate_spatially_correlated_indicators(n_regions, n_indicators)

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return Spatial-Causal-Index dashboard specification.

        Parameters extracted from SpatialCausalIndexConfig dataclass (lines 50-65).
        All defaults are actual framework defaults, not placeholders.
        """
        return FrameworkDashboardSpec(
            slug="spatial_causal_index",
            name="Spatial-Causal-Index Framework",
            description=(
                "Hybrid spatial econometrics, causal inference, and composite index construction. "
                "Analyze geographic heterogeneity in policy impacts with spatial spillovers."
            ),
            layer="socioeconomic",
            min_tier=Tier.PROFESSIONAL,
            parameters_schema={
                "type": "object",
                "properties": {
                    # Spatial Configuration
                    "n_regions": {
                        "type": "integer",
                        "title": "Number of Regions",
                        "description": "Geographic units for spatial analysis",
                        "minimum": 10,
                        "maximum": 500,
                        "default": 50,
                        "x-ui-widget": "slider",
                        "x-ui-step": 10,
                        "x-ui-group": "spatial",
                        "x-ui-order": 1,
                    },
                    "spatial_weight_type": {
                        "type": "string",
                        "title": "Spatial Weight Type",
                        "description": "Method for defining spatial relationships",
                        "enum": ["distance", "contiguity", "knn"],
                        "default": "distance",
                        "x-ui-widget": "select",
                        "x-ui-group": "spatial",
                        "x-ui-order": 2,
                        "x-ui-help": "distance: Inverse distance | contiguity: Shared borders | knn: K nearest neighbors",
                    },
                    "distance_decay_param": {
                        "type": "number",
                        "title": "Distance Decay Parameter",
                        "description": "Decay rate for distance-based weights",
                        "minimum": 0.1,
                        "maximum": 5.0,
                        "default": 1.0,
                        "x-ui-widget": "slider",
                        "x-ui-step": 0.1,
                        "x-ui-group": "spatial",
                        "x-ui-order": 3,
                    },
                    "k_neighbors": {
                        "type": "integer",
                        "title": "K Nearest Neighbors",
                        "description": "Number of neighbors for KNN weights",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 5,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "spatial",
                        "x-ui-order": 4,
                    },
                    # Index Construction
                    "n_indicators": {
                        "type": "integer",
                        "title": "Number of Indicators",
                        "description": "Indicators in composite index",
                        "minimum": 2,
                        "maximum": 20,
                        "default": 5,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "index",
                        "x-ui-order": 1,
                    },
                    "index_aggregation": {
                        "type": "string",
                        "title": "Index Aggregation Method",
                        "description": "How to combine indicators",
                        "enum": ["equal", "pca", "weighted"],
                        "default": "pca",
                        "x-ui-widget": "select",
                        "x-ui-group": "index",
                        "x-ui-order": 2,
                        "x-ui-help": "equal: Equal weights | pca: Principal components | weighted: Custom weights",
                    },
                    # Causal Inference
                    "treatment_effect_heterogeneity": {
                        "type": "boolean",
                        "title": "Spatially Varying Treatment Effects",
                        "description": "Allow treatment effects to vary by location",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "causal",
                        "x-ui-order": 1,
                    },
                    "spatial_lag_order": {
                        "type": "integer",
                        "title": "Spatial Lag Order",
                        "description": "Order of spatial spillover effects (1=direct neighbors)",
                        "minimum": 1,
                        "maximum": 3,
                        "default": 1,
                        "x-ui-widget": "slider",
                        "x-ui-step": 1,
                        "x-ui-group": "causal",
                        "x-ui-order": 2,
                    },
                },
                "required": [],
            },
            default_parameters={
                "n_regions": 50,
                "spatial_weight_type": "distance",
                "distance_decay_param": 1.0,
                "k_neighbors": 5,
                "n_indicators": 5,
                "index_aggregation": "pca",
                "treatment_effect_heterogeneity": True,
                "spatial_lag_order": 1,
            },
            parameter_groups=[
                ParameterGroupSpec(
                    key="spatial",
                    title="Spatial Configuration",
                    description="Geographic relationships and spatial weights",
                    collapsed_by_default=False,
                    parameters=["n_regions", "spatial_weight_type", "distance_decay_param", "k_neighbors"],
                ),
                ParameterGroupSpec(
                    key="index",
                    title="Index Construction",
                    description="Composite indicator specification",
                    collapsed_by_default=False,
                    parameters=["n_indicators", "index_aggregation"],
                ),
                ParameterGroupSpec(
                    key="causal",
                    title="Causal Inference",
                    description="Treatment effect estimation settings",
                    collapsed_by_default=False,
                    parameters=["treatment_effect_heterogeneity", "spatial_lag_order"],
                ),
            ],
            output_views=[
                OutputViewSpec(
                    key="spatial_index_map",
                    title="Spatial Index Map",
                    view_type=ViewType.CHOROPLETH,
                    description="Composite index by region",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="spatial_index_map_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="treatment_effects_map",
                    title="Treatment Effects Map",
                    view_type=ViewType.CHOROPLETH,
                    description="Estimated causal effects by region",
                    result_class=ResultClass.SCALAR_INDEX,
                    output_key="treatment_effects_map_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="morans_i",
                    title="Spatial Autocorrelation (Moran's I)",
                    view_type=ViewType.TIMESERIES,
                    description="Spatial clustering over time",
                result_class=ResultClass.SCALAR_INDEX,
                output_key="morans_i_data",
                tab_key="overview",
                temporal_semantics=TemporalSemantics.CROSS_SECTIONAL
                ),
                OutputViewSpec(
                    key="direct_indirect_effects",
                    title="Direct vs Spillover Effects",
                    view_type=ViewType.BAR_CHART,
                    description="Decomposition of total treatment effect",
                    result_class=ResultClass.DOMAIN_DECOMPOSITION,
                    output_key="direct_indirect_effects_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
                OutputViewSpec(
                    key="indicator_loadings",
                    title="Indicator Weights",
                    view_type=ViewType.TABLE,
                    description="Contribution of each indicator to index",
                    result_class=ResultClass.CONFIDENCE_PROVENANCE,
                    output_key="indicator_loadings_data",
                    tab_key="overview",
                    temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
                ),
            ],
        )
