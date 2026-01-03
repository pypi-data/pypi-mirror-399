# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Causal Estimator Adapters
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Causal estimator adapters delegating to krl-causal-policy-toolkit.

krl-frameworks does NOT re-implement causal methods.
All DiD, SCM, matching, IV, RDD logic is sourced from
krl-causal-policy-toolkit. This adapter provides thin
wiring for state transformation and result normalization.

Design Principles:
    - Delegate, do not duplicate
    - Prevents silent divergence
    - Keeps regulatory audit clean
    - Internal causal code limited to: wiring, state transformation, result normalization
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    import pandas as pd

__all__ = [
    "CausalMethod",
    "CausalAdapter",
    "get_causal_estimator",
    "check_causal_toolkit_installed",
]

# Supported causal methods
CausalMethod = Literal["did", "scm", "psm", "iv", "rdd"]

# Cache for estimator instances
_ESTIMATOR_CACHE: dict[str, Any] = {}


class CausalToolkitNotInstalledError(ImportError):
    """Raised when krl-causal-policy-toolkit is not installed."""
    
    def __init__(self) -> None:
        super().__init__(
            "Causal estimators require krl-causal-policy-toolkit. "
            "Install with: pip install krl-frameworks[causal]"
        )


def check_causal_toolkit_installed() -> bool:
    """
    Check if krl-causal-policy-toolkit is installed.
    
    Returns:
        True if installed, False otherwise.
    """
    try:
        import krl_policy  # noqa: F401
        return True
    except ImportError:
        return False


def _require_causal_toolkit() -> None:
    """Verify krl-causal-policy-toolkit is installed, raise if not."""
    if not check_causal_toolkit_installed():
        raise CausalToolkitNotInstalledError()


def get_causal_estimator(method: CausalMethod, *, fresh: bool = False) -> Any:
    """
    Get a causal estimator from krl-causal-policy-toolkit.
    
    Lazy import to avoid hard dependency.
    
    Args:
        method: One of 'did', 'scm', 'psm', 'iv', 'rdd'.
        fresh: If True, create new instance instead of using cache.
    
    Returns:
        Estimator instance from krl-causal-policy-toolkit.
    
    Raises:
        CausalToolkitNotInstalledError: If krl-causal-policy-toolkit not installed.
        ValueError: If method not recognized.
    
    Example:
        >>> estimator = get_causal_estimator("did")
        >>> result = estimator.fit(data, outcome_col="y", treatment_col="treated")
    """
    if not fresh and method in _ESTIMATOR_CACHE:
        return _ESTIMATOR_CACHE[method]
    
    _require_causal_toolkit()
    
    # Import estimators from krl-causal-policy-toolkit
    from krl_policy.estimators import (
        DifferenceInDifferences,
        InstrumentalVariables,
        PropensityScoreMatching,
        RegressionDiscontinuity,
        SyntheticControlMethod,
    )
    
    estimators = {
        "did": DifferenceInDifferences,
        "scm": SyntheticControlMethod,
        "psm": PropensityScoreMatching,
        "iv": InstrumentalVariables,
        "rdd": RegressionDiscontinuity,
    }
    
    if method not in estimators:
        raise ValueError(
            f"Unknown causal method '{method}'. "
            f"Available: {list(estimators.keys())}"
        )
    
    estimator = estimators[method]()
    
    if not fresh:
        _ESTIMATOR_CACHE[method] = estimator
    
    return estimator


def clear_estimator_cache() -> None:
    """Clear the estimator cache."""
    _ESTIMATOR_CACHE.clear()


class CausalAdapter:
    """
    Thin adapter for causal estimation within frameworks.
    
    Provides wiring between framework state and toolkit estimators.
    Internal causal code is limited to:
    - Wiring
    - State transformation
    - Result normalization
    
    Example:
        >>> adapter = CausalAdapter("did")
        >>> result = adapter.estimate(
        ...     data=panel_data,
        ...     outcome_col="employment",
        ...     treatment_col="policy_active",
        ...     time_col="year",
        ...     unit_col="region_id",
        ... )
        >>> print(result["estimate"], result["std_error"])
    """
    
    def __init__(self, method: CausalMethod) -> None:
        """
        Initialize adapter for a specific causal method.
        
        Args:
            method: One of 'did', 'scm', 'psm', 'iv', 'rdd'.
        """
        self.method = method
        self._estimator: Any = None
    
    @property
    def estimator(self) -> Any:
        """Lazy-loaded estimator from krl-causal-policy-toolkit."""
        if self._estimator is None:
            self._estimator = get_causal_estimator(self.method, fresh=True)
        return self._estimator
    
    @property
    def is_available(self) -> bool:
        """Check if the causal toolkit is available."""
        return check_causal_toolkit_installed()
    
    def estimate(
        self,
        data: pd.DataFrame,
        outcome_col: str,
        treatment_col: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Run causal estimation and normalize results.
        
        Args:
            data: Panel or cross-sectional data.
            outcome_col: Name of outcome variable.
            treatment_col: Name of treatment indicator.
            **kwargs: Method-specific parameters (e.g., time_col, unit_col for DiD).
        
        Returns:
            Normalized result dict with keys:
            - estimate: Point estimate (ATE or ATT)
            - std_error: Standard error
            - ci_lower: Lower confidence bound (95%)
            - ci_upper: Upper confidence bound (95%)
            - p_value: P-value (if available)
            - method: Estimation method used
            - raw_result: Original result object
        
        Raises:
            CausalToolkitNotInstalledError: If toolkit not installed.
        """
        result = self.estimator.fit(
            data=data,
            outcome_col=outcome_col,
            treatment_col=treatment_col,
            **kwargs,
        )
        
        # Normalize to common schema
        # Handle different result object structures from toolkit
        return self._normalize_result(result)
    
    def _normalize_result(self, result: Any) -> dict[str, Any]:
        """
        Normalize toolkit result to common schema.
        
        Args:
            result: Result object from toolkit estimator.
        
        Returns:
            Normalized dict with standard keys.
        """
        # Extract estimate (try multiple common attribute names)
        estimate = None
        for attr in ("ate", "att", "effect", "estimate", "coefficient"):
            if hasattr(result, attr):
                estimate = getattr(result, attr)
                break
        
        # Extract standard error
        std_error = getattr(result, "std_error", None)
        if std_error is None:
            std_error = getattr(result, "se", None)
        
        # Extract confidence interval
        ci_lower = getattr(result, "ci_lower", None)
        ci_upper = getattr(result, "ci_upper", None)
        
        # Try to get from confidence_interval attribute
        if ci_lower is None and hasattr(result, "confidence_interval"):
            ci = result.confidence_interval
            if isinstance(ci, tuple) and len(ci) == 2:
                ci_lower, ci_upper = ci
        
        # Extract p-value
        p_value = getattr(result, "p_value", None)
        if p_value is None:
            p_value = getattr(result, "pvalue", None)
        
        return {
            "estimate": estimate,
            "std_error": std_error,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "p_value": p_value,
            "method": self.method,
            "raw_result": result,
        }
    
    def validate_data(
        self,
        data: pd.DataFrame,
        outcome_col: str,
        treatment_col: str,
    ) -> list[str]:
        """
        Validate data for causal estimation.
        
        Args:
            data: DataFrame to validate.
            outcome_col: Outcome column name.
            treatment_col: Treatment column name.
        
        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []
        
        if outcome_col not in data.columns:
            errors.append(f"Outcome column '{outcome_col}' not in data")
        
        if treatment_col not in data.columns:
            errors.append(f"Treatment column '{treatment_col}' not in data")
        
        if treatment_col in data.columns:
            unique_vals = data[treatment_col].unique()
            if len(unique_vals) < 2:
                errors.append(
                    f"Treatment column must have both treated and control units. "
                    f"Found only: {unique_vals}"
                )
        
        if len(data) < 10:
            errors.append(f"Insufficient data: {len(data)} rows (minimum 10)")
        
        return errors
