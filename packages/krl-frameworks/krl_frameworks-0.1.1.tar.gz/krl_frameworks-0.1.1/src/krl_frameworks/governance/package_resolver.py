# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Capability → Package Resolution Algorithm
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Capability → Package Resolution Algorithm.

This module implements the formal resolution algorithm that maps capability
declarations to concrete package bindings. It enforces the canonical package
topology and provides fail-fast behavior with full auditability.

Canonical Package Topology:
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                         krl-core (runtime foundation)                    │
    │         ExecutionContext, CapabilityDeclaration, BindingRegistry         │
    │                          ZERO domain logic                               │
    └─────────────────────────────────────────────────────────────────────────┘
                    ▲                    ▲                    ▲
                    │                    │                    │
    ┌───────────────┴──────┐ ┌──────────┴──────────┐ ┌──────┴────────────────┐
    │   krl-connectors     │ │   krl-toolkits-*    │ │     krl-model-zoo     │
    │  FRED, Census, BLS   │ │ causal, geo, network│ │   ML/DL inference     │
    └──────────────────────┘ └─────────────────────┘ └───────────────────────┘
                    ▲                    ▲                    ▲
                    │                    │                    │
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                        krl-frameworks (orchestration)                    │
    │           MPIFramework, DiDFramework, domain-specific logic             │
    │          DECLARES requirements, does NOT assume presence                 │
    └─────────────────────────────────────────────────────────────────────────┘

Resolution Algorithm:
    1. Parse CapabilityDeclaration to extract requirements
    2. For each requirement, determine target package
    3. Check if package is installed
    4. Check if specific binding is available
    5. Check version compatibility
    6. Return resolution result (success or explicit failure)

Design Principles:
    1. Deterministic - same input always produces same output
    2. Inspectable - every decision is logged and auditable
    3. Fail-fast - missing packages cause immediate failure in LIVE mode
    4. Version-aware - incompatible versions are explicit failures
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from krl_frameworks.core.bindings import BindingRegistry
    from krl_frameworks.core.capabilities import CapabilityDeclaration
    from krl_frameworks.core.execution_context import ExecutionMode


__all__ = [
    "PackageResolver",
    "ResolutionResult",
    "ResolutionStatus",
    "ResolutionFailure",
    "FailureReason",
    "PackageSpec",
    "CAPABILITY_PACKAGE_MAP",
    "resolve_capabilities",
]


# ════════════════════════════════════════════════════════════════════════════════
# Canonical Package Mapping
# ════════════════════════════════════════════════════════════════════════════════

# Authoritative mapping: capability identifier → package specification
CAPABILITY_PACKAGE_MAP: dict[str, "PackageSpec"] = {}  # Populated at module load


class FailureReason(str, Enum):
    """
    Explicit failure reasons for package resolution.
    
    Each reason maps to a specific remediation action.
    """
    # Package-level failures
    PACKAGE_NOT_INSTALLED = "package_not_installed"
    PACKAGE_IMPORT_ERROR = "package_import_error"
    PACKAGE_VERSION_INCOMPATIBLE = "package_version_incompatible"
    
    # Binding-level failures
    BINDING_NOT_FOUND = "binding_not_found"
    BINDING_NOT_EXPORTED = "binding_not_exported"
    BINDING_TYPE_MISMATCH = "binding_type_mismatch"
    
    # Configuration failures
    MISSING_API_KEY = "missing_api_key"
    INVALID_CONFIGURATION = "invalid_configuration"
    
    # Runtime failures
    EXECUTION_MODE_VIOLATION = "execution_mode_violation"
    TIER_ACCESS_DENIED = "tier_access_denied"
    
    @property
    def remediation(self) -> str:
        """Get remediation guidance for this failure."""
        remediations = {
            self.PACKAGE_NOT_INSTALLED: "Install the required package with pip",
            self.PACKAGE_IMPORT_ERROR: "Check package installation and dependencies",
            self.PACKAGE_VERSION_INCOMPATIBLE: "Upgrade or downgrade to compatible version",
            self.BINDING_NOT_FOUND: "The package is installed but required binding is missing",
            self.BINDING_NOT_EXPORTED: "Binding exists but is not exported in __all__",
            self.BINDING_TYPE_MISMATCH: "Binding exists but does not satisfy protocol",
            self.MISSING_API_KEY: "Set required API key in environment or configuration",
            self.INVALID_CONFIGURATION: "Check configuration values against schema",
            self.EXECUTION_MODE_VIOLATION: "Cannot use this binding in current execution mode",
            self.TIER_ACCESS_DENIED: "Upgrade subscription tier for access",
        }
        return remediations.get(self, "Unknown failure")
    
    @property
    def is_recoverable(self) -> bool:
        """Whether this failure can be recovered from in TEST mode."""
        unrecoverable = {
            self.PACKAGE_IMPORT_ERROR,
            self.EXECUTION_MODE_VIOLATION,
        }
        return self not in unrecoverable


class ResolutionStatus(str, Enum):
    """
    Status of capability resolution.
    
    SUCCESS: Capability fully resolved to installed binding
    DEGRADED: Capability partially resolved (TEST mode only)
    FAILED: Resolution impossible, execution cannot proceed
    SKIPPED: Optional capability intentionally not resolved
    """
    SUCCESS = "success"
    DEGRADED = "degraded"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class PackageSpec:
    """
    Specification for a package that provides a capability.
    
    Attributes:
        package_name: PyPI package name (e.g., "krl-data-connectors")
        import_path: Python import path (e.g., "krl_data_connectors")
        min_version: Minimum required version (semver)
        max_version: Maximum supported version (semver, optional)
        binding_path: Subpath to specific binding (e.g., "connectors.fred")
        capability_type: Type of capability (connector, toolkit, model)
    """
    package_name: str
    import_path: str
    min_version: str = "0.0.0"
    max_version: str | None = None
    binding_path: str = ""
    capability_type: str = "unknown"
    
    @property
    def full_import_path(self) -> str:
        """Get full import path including binding."""
        if self.binding_path:
            return f"{self.import_path}.{self.binding_path}"
        return self.import_path
    
    def version_compatible(self, installed_version: str) -> bool:
        """Check if installed version is compatible."""
        try:
            from packaging.version import Version
            installed = Version(installed_version)
            min_v = Version(self.min_version)
            
            if installed < min_v:
                return False
            
            if self.max_version:
                max_v = Version(self.max_version)
                if installed > max_v:
                    return False
            
            return True
        except Exception:
            # If packaging not available, do string comparison
            return installed_version >= self.min_version


@dataclass
class ResolutionFailure:
    """
    Detailed failure information for resolution debugging.
    
    Captures everything needed to diagnose and fix resolution failures.
    """
    capability_type: str
    capability_name: str
    reason: FailureReason
    package_spec: PackageSpec | None
    installed_version: str | None = None
    expected_version: str | None = None
    details: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for audit logging."""
        return {
            "capability_type": self.capability_type,
            "capability_name": self.capability_name,
            "reason": self.reason.value,
            "remediation": self.reason.remediation,
            "is_recoverable": self.reason.is_recoverable,
            "package_name": self.package_spec.package_name if self.package_spec else None,
            "installed_version": self.installed_version,
            "expected_version": self.expected_version,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def __str__(self) -> str:
        """Human-readable failure description."""
        pkg = self.package_spec.package_name if self.package_spec else "unknown"
        return (
            f"[{self.reason.value}] {self.capability_type}:{self.capability_name} "
            f"(package={pkg}): {self.details or self.reason.remediation}"
        )


@dataclass
class ResolutionResult:
    """
    Complete result of capability resolution.
    
    Contains the resolution status, any failures, and the resolved
    binding if successful.
    """
    capability_type: str
    capability_name: str
    status: ResolutionStatus
    binding: Any | None = None
    package_spec: PackageSpec | None = None
    installed_version: str | None = None
    failure: ResolutionFailure | None = None
    warnings: list[str] = field(default_factory=list)
    
    @property
    def is_success(self) -> bool:
        """Whether resolution succeeded."""
        return self.status == ResolutionStatus.SUCCESS
    
    @property
    def is_failed(self) -> bool:
        """Whether resolution failed."""
        return self.status == ResolutionStatus.FAILED
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for audit logging."""
        return {
            "capability_type": self.capability_type,
            "capability_name": self.capability_name,
            "status": self.status.value,
            "has_binding": self.binding is not None,
            "package_name": self.package_spec.package_name if self.package_spec else None,
            "installed_version": self.installed_version,
            "failure": self.failure.to_dict() if self.failure else None,
            "warnings": self.warnings,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Package Resolver
# ════════════════════════════════════════════════════════════════════════════════


class PackageResolver:
    """
    Resolves capability declarations to package bindings.
    
    The resolver is the authoritative source for capability → package
    mapping. It enforces the canonical package topology and provides
    fail-fast behavior with full auditability.
    
    Design:
        1. Maintains a mapping of capability identifiers to packages
        2. Validates package installation and version compatibility
        3. Attempts to import and verify bindings
        4. Returns structured results for all resolutions
    
    Example:
        >>> resolver = PackageResolver()
        >>> result = resolver.resolve_connector("fred")
        >>> if result.is_success:
        ...     fred_connector = result.binding
        >>> else:
        ...     print(f"Failed: {result.failure}")
    """
    
    def __init__(self) -> None:
        """Initialize resolver with canonical package mappings."""
        self._package_map = self._build_package_map()
        self._resolution_log: list[ResolutionResult] = []
        self._import_cache: dict[str, Any] = {}
    
    def _build_package_map(self) -> dict[str, PackageSpec]:
        """
        Build the canonical capability → package mapping.
        
        This is the authoritative source for package topology.
        """
        mapping: dict[str, PackageSpec] = {}
        
        # ═══════════════════════════════════════════════════════════════════
        # Connectors: krl-data-connectors package
        # ═══════════════════════════════════════════════════════════════════
        connector_package = "krl-data-connectors"
        connector_import = "krl_data_connectors"
        connector_min = "1.0.0"
        
        connectors = [
            "fred", "census", "bls", "world_bank", "oecd", "imf",
            "eurostat", "who", "un_data", "fao", "unhcr", "unicef",
        ]
        for conn in connectors:
            mapping[f"connector.{conn}"] = PackageSpec(
                package_name=connector_package,
                import_path=connector_import,
                min_version=connector_min,
                binding_path=f"connectors.{conn}",
                capability_type="connector",
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # Causal Toolkit: krl-causal-policy-toolkit package
        # ═══════════════════════════════════════════════════════════════════
        causal_package = "krl-causal-policy-toolkit"
        causal_import = "krl_causal"
        causal_min = "1.0.0"
        
        causal_methods = [
            "did", "scm", "rdd", "iv", "psm", "cba",
            "difference_in_differences", "synthetic_control",
            "regression_discontinuity", "instrumental_variables",
            "propensity_score_matching", "cost_benefit_analysis",
        ]
        for method in causal_methods:
            mapping[f"toolkit.causal.{method}"] = PackageSpec(
                package_name=causal_package,
                import_path=causal_import,
                min_version=causal_min,
                binding_path=method,
                capability_type="toolkit.causal",
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # Geospatial Toolkit: krl-geospatial-tools package
        # ═══════════════════════════════════════════════════════════════════
        geo_package = "krl-geospatial-tools"
        geo_import = "krl_geospatial"
        geo_min = "0.2.0"
        
        geo_methods = [
            "queen_weights", "rook_weights", "knn_weights",
            "choropleth", "bubble_map", "heatmap",
            "spatial_join", "geocode", "buffer",
        ]
        for method in geo_methods:
            mapping[f"toolkit.geospatial.{method}"] = PackageSpec(
                package_name=geo_package,
                import_path=geo_import,
                min_version=geo_min,
                binding_path=method,
                capability_type="toolkit.geospatial",
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # Network Toolkit: krl-network-analysis package
        # ═══════════════════════════════════════════════════════════════════
        network_package = "krl-network-analysis"
        network_import = "krl_network"
        network_min = "0.2.0"
        
        network_methods = [
            "centrality", "clustering", "community_detection",
            "shortest_path", "pagerank", "betweenness",
        ]
        for method in network_methods:
            mapping[f"toolkit.network.{method}"] = PackageSpec(
                package_name=network_package,
                import_path=network_import,
                min_version=network_min,
                binding_path=method,
                capability_type="toolkit.network",
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # Model Zoo: krl-model-zoo package (unified with tiered access)
        # Derived from: /Private IP/Model Catalog/
        #   - Open/        → community tier (FREE)
        #   - Class A/     → professional tier
        #   - Proprietary/ → enterprise tier
        # ═══════════════════════════════════════════════════════════════════
        model_package = "krl-model-zoo"
        model_import = "krl_model_zoo"
        model_min = "2.0.0"
        
        # ═══════════════════════════════════════════════════════════════════
        # COMMUNITY TIER MODELS (Open/)
        # FREE - Available to all users
        # ═══════════════════════════════════════════════════════════════════
        community_models = [
            # Anomaly Detection (Open/anomaly/)
            "anomaly.isolation_forest",
            "anomaly.stl_decomposition",
            
            # Bayesian (Open/bayesian/)
            "bayesian.bayesian_linear_regression",
            "bayesian.bayesian_structural_breaks",
            "bayesian.bayesian_var",
            "bayesian.mcmc_samplers",
            
            # Clustering (Open/clustering/)
            "clustering.dbscan",
            "clustering.gaussian_mixture",
            "clustering.hierarchical",
            "clustering.kmeans",
            
            # Dimensionality Reduction (Open/dimensionality/)
            "dimensionality.arch",
            "dimensionality.factor_analysis",
            "dimensionality.pca",
            "dimensionality.tbats",
            "dimensionality.tsne",
            "dimensionality.umap",
            
            # Econometric (Open/econometric/)
            "econometric.cointegration",
            "econometric.ets",
            "econometric.prophet",
            "econometric.sarima",
            "econometric.var",
            
            # Ensemble (Open/ensemble/)
            "ensemble.dynamic_voting",
            "ensemble.equity_bagging",
            "ensemble.spatial_boosting",
            "ensemble.spatial_glm",
            "ensemble.spatial_rf",
            "ensemble.adaboost",
            "ensemble.adaptive_ensemble",
            "ensemble.bagging",
            "ensemble.bayesian_averaging",
            "ensemble.extratrees",
            "ensemble.random_forest",
            "ensemble.simple_ensemble",
            "ensemble.stacked_ensemble",
            "ensemble.stacking",
            "ensemble.voting",
            "ensemble.xgboost",
            
            # GAM (Open/gam/)
            "gam.smooth_term",
            "gam.spline",
            
            # GLM (Open/glm/)
            "glm.beta",
            "glm.gamma",
            "glm.inverse_gaussian",
            "glm.logistic",
            "glm.negative_binomial",
            "glm.poisson",
            "glm.quasi_likelihood",
            "glm.tweedie",
            "glm.zero_inflated_negative_binomial",
            "glm.zero_inflated_poisson",
            
            # Health (Open/health/)
            "health.disease_modeling_pipeline",
            
            # Hybrid (Open/hybrid/)
            "hybrid.arima_xgboost",
            "hybrid.garch_nn",
            "hybrid.prophet_lstm",
            
            # ML (Open/ml/)
            "ml.random_forest",
            "ml.regularized_regression",
            "ml.xgboost",
            
            # Neural Networks (Open/neural_networks/)
            "neural_networks.causal_gates",
            "neural_networks.causal_positional_encoding",
            "neural_networks.equity_attention",
            "neural_networks.gru",
            "neural_networks.lstm",
            "neural_networks.transformer",
            
            # Regional (Open/regional/)
            "regional.location_quotient",
            "regional.shift_share",
            
            # Signals (Open/signals/)
            "signals.ticketing",
            "signals.trust_network",
            
            # State Space (Open/state_space/)
            "state_space.bsts",
            "state_space.dynamic_factor",
            "state_space.kalman_filter",
            "state_space.local_level",
            "state_space.midas",
            "state_space.ucm",
            
            # Volatility (Open/volatility/)
            "volatility.egarch",
            "volatility.garch",
            "volatility.gjr_garch",
        ]
        
        # ═══════════════════════════════════════════════════════════════════
        # PROFESSIONAL TIER MODELS (Class A/)
        # Requires professional subscription - 141 models total
        # Includes enhanced versions of community models + exclusive models
        # ═══════════════════════════════════════════════════════════════════
        professional_models = [
            # Advanced (Class A/advanced/) - 4 models
            "advanced.agent_based",
            "advanced.gaussian_process",
            "advanced.reinforcement_learning",
            "advanced.vae",
            
            # Anomaly Detection (Class A/anomaly/) - 4 models
            "anomaly.autoencoder_anomaly",
            "anomaly.isolation_forest_pro",
            "anomaly.local_outlier_factor",
            "anomaly.stl_decomposition_pro",
            
            # Bayesian (Class A/bayesian/) - 8 models
            "bayesian.bayesian_linear_regression_pro",
            "bayesian.bayesian_mixture",
            "bayesian.bayesian_neural_network",
            "bayesian.bayesian_structural_breaks_pro",
            "bayesian.bayesian_var_pro",
            "bayesian.changepoint_detection",
            "bayesian.hierarchical_models",
            "bayesian.mcmc_samplers_pro",
            
            # Causal (Class A/causal/) - 13 models
            "causal.causal_bounds",
            "causal.causal_discovery",
            "causal.causal_forest",
            "causal.dag_discovery",
            "causal.difference_in_differences",
            "causal.double_ml",
            "causal.instrumental_variables",
            "causal.mediation_analysis",
            "causal.multi_unit_scm",
            "causal.propensity_score_matching",
            "causal.regression_discontinuity",
            "causal.synthetic_control",
            "causal.uplift",
            
            # Classification (Class A/classification/) - 8 models
            "classification.adaboost",
            "classification.causal_nb",
            "classification.decision_tree",
            "classification.equity_svm",
            "classification.extra_trees",
            "classification.gradient_boosting_classifier",
            "classification.random_forest_pro",
            "classification.voting_classifier",
            
            # Clustering (Class A/clustering/) - 5 models
            "clustering.dbscan_pro",
            "clustering.gaussian_mixture_pro",
            "clustering.hdbscan",
            "clustering.hierarchical_pro",
            "clustering.kmeans_pro",
            
            # Dimensionality (Class A/dimensionality/) - 6 models
            "dimensionality.arch_pro",
            "dimensionality.factor_analysis_pro",
            "dimensionality.pca_pro",
            "dimensionality.tbats_pro",
            "dimensionality.tsne_pro",
            "dimensionality.umap_pro",
            
            # Econometric (Class A/econometric/) - 5 models
            "econometric.cointegration_pro",
            "econometric.ets_pro",
            "econometric.prophet_pro",
            "econometric.sarima_pro",
            "econometric.var_pro",
            
            # Ensemble (Class A/ensemble/) - 16 models
            "ensemble.dynamic_voting_pro",
            "ensemble.equity_bagging_pro",
            "ensemble.spatial_boosting_pro",
            "ensemble.spatial_glm_pro",
            "ensemble.spatial_rf_pro",
            "ensemble.adaboost_pro",
            "ensemble.adaptive_ensemble_pro",
            "ensemble.bagging_pro",
            "ensemble.bayesian_averaging_pro",
            "ensemble.extratrees_pro",
            "ensemble.random_forest_pro",
            "ensemble.simple_ensemble_pro",
            "ensemble.stacked_ensemble_pro",
            "ensemble.stacking_pro",
            "ensemble.voting_pro",
            "ensemble.xgboost_pro",
            
            # GAM (Class A/gam/) - 2 models
            "gam.smooth_term_pro",
            "gam.spline_pro",
            
            # GLM (Class A/glm/) - 10 models
            "glm.beta_pro",
            "glm.gamma_pro",
            "glm.inverse_gaussian_pro",
            "glm.logistic_pro",
            "glm.negative_binomial_pro",
            "glm.poisson_pro",
            "glm.quasi_likelihood_pro",
            "glm.tweedie_pro",
            "glm.zero_inflated_negative_binomial_pro",
            "glm.zero_inflated_poisson_pro",
            
            # Hybrid (Class A/hybrid/) - 3 models
            "hybrid.arima_xgboost_pro",
            "hybrid.garch_nn_pro",
            "hybrid.prophet_lstm_pro",
            
            # ML (Class A/ml/) - 6 models
            "ml.k_nearest_neighbors",
            "ml.naive_bayes",
            "ml.random_forest_pro",
            "ml.regularized_regression_pro",
            "ml.support_vector_machine",
            "ml.xgboost_pro",
            
            # Network (Class A/network/) - 7 models
            "network.diffusion",
            "network.ergm",
            "network.graphsage",
            "network.node2vec",
            "network.spatial_autoregressive",
            "network.spatial_error",
            "network.stochastic_block_model",
            
            # Neural (Class A/neural/) - 4 models
            "neural.deepar",
            "neural.informer",
            "neural.nbeats",
            "neural.temporal_fusion_transformer",
            
            # Neural Networks (Class A/neural_networks/) - 6 models
            "neural_networks.causal_gates_pro",
            "neural_networks.causal_positional_encoding_pro",
            "neural_networks.equity_attention_pro",
            "neural_networks.gru_pro",
            "neural_networks.lstm_pro",
            "neural_networks.transformer_pro",
            
            # Optimization (Class A/optimization/) - 1 model
            "optimization.adaptive_lr",
            
            # Regional (Class A/regional/) - 2 models
            "regional.location_quotient_pro",
            "regional.shift_share_pro",
            
            # Regression (Class A/regression/) - 9 models
            "regression.elastic_net",
            "regression.gradient_boosting_regressor",
            "regression.lasso",
            "regression.linear_regression",
            "regression.mlp_regressor",
            "regression.random_forest_regressor",
            "regression.ridge",
            "regression.svr",
            "regression.voting_regressor",
            
            # Signals (Class A/signals/) - 2 models
            "signals.ticketing_pro",
            "signals.trust_network_pro",
            
            # State Space (Class A/state_space/) - 6 models
            "state_space.bsts_pro",
            "state_space.dynamic_factor_pro",
            "state_space.kalman_filter_pro",
            "state_space.local_level_pro",
            "state_space.midas_pro",
            "state_space.ucm_pro",
            
            # Unique Models (Class A/unique_models/) - 3 models
            "unique_models.causal_bounds",
            "unique_models.causal_discovery",
            "unique_models.uplift",
            
            # Variants (Class A/variants/) - 8 models
            "variants.bayesian_variants",
            "variants.causal_variants",
            "variants.ensemble_variants",
            "variants.gbm_variants",
            "variants.linear_variants",
            "variants.neural_variants",
            "variants.survival_variants",
            "variants.timeseries_variants",
            
            # Volatility (Class A/volatility/) - 3 models
            "volatility.egarch_pro",
            "volatility.garch_pro",
            "volatility.gjr_garch_pro",
        ]
        
        # ═══════════════════════════════════════════════════════════════════
        # ENTERPRISE TIER MODELS (Proprietary/)
        # Requires enterprise subscription
        # ═══════════════════════════════════════════════════════════════════
        enterprise_models = [
            # Advanced (Proprietary/advanced/)
            "proprietary.agent_based",
            "proprietary.reinforcement_learning",
        ]
        
        # Register all models with tier metadata
        all_models = (
            [(m, "community") for m in community_models] +
            [(m, "professional") for m in professional_models] +
            [(m, "enterprise") for m in enterprise_models]
        )
        
        for model, tier in all_models:
            category, model_type = model.split(".", 1)
            mapping[f"model.{model}"] = PackageSpec(
                package_name=model_package,
                import_path=model_import,
                min_version=model_min,
                binding_path=f"{category}.{model_type}",
                capability_type=f"model.{tier}",
            )
        
        return mapping
    
    def get_package_spec(self, capability_key: str) -> PackageSpec | None:
        """
        Get package specification for a capability.
        
        Args:
            capability_key: Capability identifier (e.g., "connector.fred")
        
        Returns:
            PackageSpec if mapping exists, None otherwise.
        """
        return self._package_map.get(capability_key)
    
    def check_package_installed(self, package_name: str) -> tuple[bool, str | None]:
        """
        Check if a package is installed and get its version.
        
        Args:
            package_name: PyPI package name.
        
        Returns:
            Tuple of (is_installed, version_or_none).
        """
        try:
            version = importlib.metadata.version(package_name)
            return True, version
        except importlib.metadata.PackageNotFoundError:
            return False, None
    
    def check_binding_available(
        self,
        import_path: str,
        binding_name: str | None = None,
    ) -> tuple[bool, Any | None, str | None]:
        """
        Check if a binding is importable and available.
        
        Args:
            import_path: Python import path.
            binding_name: Optional specific binding to check.
        
        Returns:
            Tuple of (is_available, binding_or_none, error_message_or_none).
        """
        cache_key = f"{import_path}.{binding_name}" if binding_name else import_path
        
        if cache_key in self._import_cache:
            cached = self._import_cache[cache_key]
            return cached is not None, cached, None
        
        try:
            module = importlib.import_module(import_path)
            
            if binding_name:
                if hasattr(module, binding_name):
                    binding = getattr(module, binding_name)
                    self._import_cache[cache_key] = binding
                    return True, binding, None
                else:
                    self._import_cache[cache_key] = None
                    return False, None, f"Binding '{binding_name}' not found in {import_path}"
            else:
                self._import_cache[cache_key] = module
                return True, module, None
                
        except ImportError as e:
            self._import_cache[cache_key] = None
            return False, None, str(e)
    
    def resolve(
        self,
        capability_key: str,
        *,
        strict: bool = True,
    ) -> ResolutionResult:
        """
        Resolve a single capability to its package binding.
        
        This is the core resolution algorithm:
        
        1. Look up capability in package map
        2. Check if target package is installed
        3. Verify version compatibility
        4. Attempt to import binding
        5. Return structured result
        
        Args:
            capability_key: Capability identifier (e.g., "connector.fred")
            strict: If True, missing packages are failures. If False, degraded.
        
        Returns:
            ResolutionResult with status and binding or failure.
        """
        # Extract capability type and name
        parts = capability_key.split(".", 1)
        cap_type = parts[0] if parts else "unknown"
        cap_name = parts[1] if len(parts) > 1 else capability_key
        
        # Step 1: Look up package specification
        spec = self.get_package_spec(capability_key)
        if spec is None:
            # Check if it's a known capability type with unknown specific binding
            failure = ResolutionFailure(
                capability_type=cap_type,
                capability_name=cap_name,
                reason=FailureReason.BINDING_NOT_FOUND,
                package_spec=None,
                details=f"No package mapping for capability '{capability_key}'",
            )
            result = ResolutionResult(
                capability_type=cap_type,
                capability_name=cap_name,
                status=ResolutionStatus.FAILED if strict else ResolutionStatus.DEGRADED,
                failure=failure,
            )
            self._resolution_log.append(result)
            return result
        
        # Step 2: Check package installation
        is_installed, installed_version = self.check_package_installed(spec.package_name)
        if not is_installed:
            failure = ResolutionFailure(
                capability_type=cap_type,
                capability_name=cap_name,
                reason=FailureReason.PACKAGE_NOT_INSTALLED,
                package_spec=spec,
                expected_version=spec.min_version,
                details=f"pip install {spec.package_name}>={spec.min_version}",
            )
            result = ResolutionResult(
                capability_type=cap_type,
                capability_name=cap_name,
                status=ResolutionStatus.FAILED if strict else ResolutionStatus.DEGRADED,
                package_spec=spec,
                failure=failure,
            )
            self._resolution_log.append(result)
            return result
        
        # Step 3: Verify version compatibility
        if not spec.version_compatible(installed_version or "0.0.0"):
            failure = ResolutionFailure(
                capability_type=cap_type,
                capability_name=cap_name,
                reason=FailureReason.PACKAGE_VERSION_INCOMPATIBLE,
                package_spec=spec,
                installed_version=installed_version,
                expected_version=f">={spec.min_version}",
                details=f"Upgrade: pip install '{spec.package_name}>={spec.min_version}'",
            )
            result = ResolutionResult(
                capability_type=cap_type,
                capability_name=cap_name,
                status=ResolutionStatus.FAILED,
                package_spec=spec,
                installed_version=installed_version,
                failure=failure,
            )
            self._resolution_log.append(result)
            return result
        
        # Step 4: Attempt to import binding
        is_available, binding, error = self.check_binding_available(
            spec.import_path,
            spec.binding_path.split(".")[-1] if spec.binding_path else None,
        )
        
        if not is_available:
            failure = ResolutionFailure(
                capability_type=cap_type,
                capability_name=cap_name,
                reason=FailureReason.BINDING_NOT_EXPORTED
                if error and "not found" in error.lower()
                else FailureReason.PACKAGE_IMPORT_ERROR,
                package_spec=spec,
                installed_version=installed_version,
                details=error or "Import failed",
            )
            result = ResolutionResult(
                capability_type=cap_type,
                capability_name=cap_name,
                status=ResolutionStatus.FAILED if strict else ResolutionStatus.DEGRADED,
                package_spec=spec,
                installed_version=installed_version,
                failure=failure,
            )
            self._resolution_log.append(result)
            return result
        
        # Step 5: Success!
        result = ResolutionResult(
            capability_type=cap_type,
            capability_name=cap_name,
            status=ResolutionStatus.SUCCESS,
            binding=binding,
            package_spec=spec,
            installed_version=installed_version,
        )
        self._resolution_log.append(result)
        return result
    
    def resolve_connector(self, connector_type: str, *, strict: bool = True) -> ResolutionResult:
        """Resolve a connector capability."""
        return self.resolve(f"connector.{connector_type}", strict=strict)
    
    def resolve_toolkit(
        self,
        toolkit: str,
        method: str | None = None,
        *,
        strict: bool = True,
    ) -> ResolutionResult:
        """Resolve a toolkit capability."""
        key = f"toolkit.{toolkit}.{method}" if method else f"toolkit.{toolkit}"
        return self.resolve(key, strict=strict)
    
    def resolve_model(
        self,
        category: str,
        model_type: str,
        *,
        strict: bool = True,
    ) -> ResolutionResult:
        """Resolve a model zoo capability."""
        return self.resolve(f"model.{category}.{model_type}", strict=strict)
    
    def resolve_capabilities(
        self,
        declaration: "CapabilityDeclaration",
        *,
        execution_mode: "ExecutionMode | None" = None,
    ) -> list[ResolutionResult]:
        """
        Resolve all capabilities in a declaration.
        
        Args:
            declaration: Capability declaration to resolve.
            execution_mode: Current execution mode (affects strictness).
        
        Returns:
            List of resolution results for all capabilities.
        """
        from krl_frameworks.core.execution_context import ExecutionMode
        
        mode = execution_mode or ExecutionMode.from_env()
        strict = mode.requires_strict_validation
        
        results: list[ResolutionResult] = []
        
        # Resolve connectors
        for conn in declaration.connectors:
            key = f"connector.{conn.connector_type}" if conn.connector_type else f"connector.{conn.domain}"
            result = self.resolve(key, strict=strict and conn.scope.value == "required")
            results.append(result)
        
        # Resolve toolkits
        for toolkit in declaration.toolkits:
            key = f"toolkit.{toolkit.toolkit}"
            if toolkit.method:
                key = f"{key}.{toolkit.method}"
            result = self.resolve(key, strict=strict and toolkit.scope.value == "required")
            results.append(result)
        
        # Resolve model zoo (always optional)
        for model in declaration.model_zoo:
            key = f"model.{model.category}.{model.model_type}"
            result = self.resolve(key, strict=False)  # Model zoo is never strict
            results.append(result)
        
        return results
    
    def get_resolution_log(self) -> list[dict[str, Any]]:
        """Get audit log of all resolutions."""
        return [r.to_dict() for r in self._resolution_log]
    
    def clear_resolution_log(self) -> None:
        """Clear the resolution log."""
        self._resolution_log.clear()
    
    def get_failed_resolutions(self) -> list[ResolutionResult]:
        """Get all failed resolutions."""
        return [r for r in self._resolution_log if r.is_failed]
    
    def get_ecosystem_status(self) -> dict[str, Any]:
        """
        Get complete ecosystem installation status.
        
        Returns status of all known packages in the canonical topology.
        """
        packages = {
            "krl-open-core": "0.2.0",
            "krl-types": "0.2.0",
            "krl-data-connectors": "1.0.0",
            "krl-causal-policy-toolkit": "1.0.0",
            "krl-geospatial-tools": "0.2.0",
            "krl-network-analysis": "0.2.0",
            "krl-model-zoo": "0.1.0",
            "krl-frameworks": "0.1.0",
        }
        
        status: dict[str, dict[str, Any]] = {}
        for pkg, min_ver in packages.items():
            is_installed, version = self.check_package_installed(pkg)
            status[pkg] = {
                "installed": is_installed,
                "version": version,
                "min_version": min_ver,
                "compatible": is_installed and (version or "0.0.0") >= min_ver,
            }
        
        return {
            "packages": status,
            "all_installed": all(s["installed"] for s in status.values()),
            "all_compatible": all(s["compatible"] for s in status.values()),
        }


# ════════════════════════════════════════════════════════════════════════════════
# Module-Level Convenience Functions
# ════════════════════════════════════════════════════════════════════════════════

_global_resolver: PackageResolver | None = None


def get_global_resolver() -> PackageResolver:
    """Get or create the global package resolver."""
    global _global_resolver
    if _global_resolver is None:
        _global_resolver = PackageResolver()
    return _global_resolver


def resolve_capabilities(
    declaration: "CapabilityDeclaration",
    *,
    execution_mode: "ExecutionMode | None" = None,
) -> list[ResolutionResult]:
    """
    Resolve all capabilities in a declaration using the global resolver.
    
    Args:
        declaration: Capability declaration to resolve.
        execution_mode: Current execution mode.
    
    Returns:
        List of resolution results.
    """
    return get_global_resolver().resolve_capabilities(
        declaration,
        execution_mode=execution_mode,
    )
