# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Spatial Analysis Adapters
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Spatial analysis adapters delegating to krl-geospatial-tools.

Optional, adapter-based, lazy-loaded.
Imported only if framework declares requires_spatial=True
and extras are installed. No hard dependency.

Provides access to:
    - Spatial weights (queen, rook, k-nearest, distance-based)
    - Spatial autocorrelation (Moran's I, Geary's C)
    - Spatial lag computation
    - Geographically weighted regression support
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np
    
    # Use string annotations to avoid import errors
    GeoDataFrame = Any  # geopandas.GeoDataFrame

__all__ = [
    "SpatialAdapter",
    "SpatialLagAdapter",
    "SpatialErrorAdapter",
    "GWRAdapter",
    "check_geospatial_tools_installed",
]


class GeospatialToolsNotInstalledError(ImportError):
    """Raised when krl-geospatial-tools is not installed."""
    
    def __init__(self) -> None:
        super().__init__(
            "Spatial analysis requires krl-geospatial-tools. "
            "Install with: pip install krl-frameworks[geospatial]"
        )


def check_geospatial_tools_installed() -> bool:
    """
    Check if krl-geospatial-tools is installed.
    
    Returns:
        True if installed, False otherwise.
    """
    try:
        import krl_geospatial  # noqa: F401
        return True
    except ImportError:
        return False


def _require_geospatial_tools() -> None:
    """Verify krl-geospatial-tools is installed, raise if not."""
    if not check_geospatial_tools_installed():
        raise GeospatialToolsNotInstalledError()


class SpatialAdapter:
    """
    Thin adapter for spatial analysis within frameworks.
    
    Provides access to spatial weights, adjacency matrices,
    and spatial econometrics from krl-geospatial-tools.
    
    Example:
        >>> adapter = SpatialAdapter()
        >>> weights = adapter.compute_spatial_weights(gdf, method="queen")
        >>> moran = adapter.spatial_autocorrelation(values, weights)
        >>> print(f"Moran's I: {moran['I']}, p-value: {moran['p_value']}")
    """
    
    def __init__(self) -> None:
        """Initialize adapter, verifying toolkit availability."""
        _require_geospatial_tools()
        self._weights_cache: dict[str, Any] = {}
    
    @staticmethod
    def is_available() -> bool:
        """Check if the geospatial toolkit is available."""
        return check_geospatial_tools_installed()
    
    def compute_spatial_weights(
        self,
        gdf: GeoDataFrame,
        method: str = "queen",
        *,
        k: int = 5,
        distance_band: float | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Compute spatial weights matrix.
        
        Args:
            gdf: GeoDataFrame with geometry column.
            method: Weight type - one of:
                - 'queen': Queen contiguity (shared edges or vertices)
                - 'rook': Rook contiguity (shared edges only)
                - 'knn': K-nearest neighbors
                - 'distance': Distance-band weights
            k: Number of neighbors for knn method.
            distance_band: Maximum distance for distance-band weights.
            **kwargs: Additional method-specific parameters.
        
        Returns:
            Spatial weights object (krl_geospatial.weights.SpatialWeights).
        
        Raises:
            GeospatialToolsNotInstalledError: If toolkit not installed.
        """
        # Import weight CLASSES from krl-geospatial-tools (not functions!)
        # Cohesion Note: krl-geospatial-tools exports classes, not factory functions
        from krl_geospatial.weights import (
            QueenWeights,
            RookWeights,
            KNNWeights,
            DistanceBandWeights,
        )
        
        if method == "queen":
            return QueenWeights(gdf, **kwargs)
        elif method == "rook":
            return RookWeights(gdf, **kwargs)
        elif method == "knn":
            return KNNWeights(gdf, k=k, **kwargs)
        elif method == "distance":
            if distance_band is None:
                raise ValueError("distance_band required for distance method")
            return DistanceBandWeights(gdf, threshold=distance_band, **kwargs)
        else:
            raise ValueError(
                f"Unknown weight method '{method}'. "
                f"Available: ['queen', 'rook', 'knn', 'distance']"
            )
    
    def spatial_autocorrelation(
        self,
        values: np.ndarray,
        weights: Any,
        *,
        permutations: int = 999,
    ) -> dict[str, float]:
        """
        Compute Moran's I spatial autocorrelation.
        
        Args:
            values: Array of values to test for spatial autocorrelation.
            weights: Spatial weights matrix.
            permutations: Number of permutations for significance testing.
        
        Returns:
            Dict with:
            - 'I': Moran's I statistic
            - 'p_value': Pseudo p-value from permutation test
            - 'z_score': Z-score under normality assumption
            - 'expected_I': Expected I under null hypothesis
        """
        # Cohesion Note: morans_i is in econometrics, not statistics
        from krl_geospatial.econometrics import morans_i
        
        result = morans_i(values, weights, permutations=permutations)
        
        # Handle both object and dict return types for robustness
        if hasattr(result, 'I'):
            return {
                "I": float(result.I),
                "p_value": float(getattr(result, 'p_sim', getattr(result, 'p_value', 0.0))),
                "z_score": float(getattr(result, 'z_sim', getattr(result, 'z_score', 0.0))),
                "expected_I": float(getattr(result, 'EI', -1/(len(values)-1))),
            }
        elif isinstance(result, dict):
            return {
                "I": float(result.get('I', 0.0)),
                "p_value": float(result.get('p_value', result.get('p_sim', 0.0))),
                "z_score": float(result.get('z_score', result.get('z_sim', 0.0))),
                "expected_I": float(result.get('expected_I', result.get('EI', 0.0))),
            }
        else:
            return {"I": float(result), "p_value": 0.0, "z_score": 0.0, "expected_I": 0.0}
    
    def spatial_lag(
        self,
        values: np.ndarray,
        weights: Any,
    ) -> np.ndarray:
        """
        Compute spatial lag of values.
        
        The spatial lag is the weighted average of neighboring values.
        
        Args:
            values: Array of values.
            weights: Spatial weights matrix.
        
        Returns:
            Array of spatially lagged values.
        """
        import numpy as np
        
        # Spatial lag computed directly from weights object
        # Most weight objects support lag() or sparse matrix multiplication
        if hasattr(weights, 'lag'):
            return weights.lag(values)
        elif hasattr(weights, 'sparse'):
            return weights.sparse @ values
        elif hasattr(weights, 'full'):
            w_matrix = weights.full()[0]  # full() returns (W, ids)
            return w_matrix @ values
        else:
            # Fallback: manual computation
            n = len(values)
            result = np.zeros(n)
            for i in range(n):
                if hasattr(weights, 'neighbors') and i in weights.neighbors:
                    neighbors = weights.neighbors[i]
                    w_vals = weights.weights[i] if hasattr(weights, 'weights') else [1] * len(neighbors)
                    result[i] = sum(w * values[j] for j, w in zip(neighbors, w_vals))
            return result
    
    def local_morans(
        self,
        values: np.ndarray,
        weights: Any,
        *,
        permutations: int = 999,
    ) -> dict[str, np.ndarray]:
        """
        Compute Local Moran's I (LISA).
        
        Args:
            values: Array of values.
            weights: Spatial weights matrix.
            permutations: Number of permutations for significance.
        
        Returns:
            Dict with:
            - 'Is': Array of local Moran's I values
            - 'p_values': Array of p-values
            - 'quadrants': Array of quadrant classifications (HH, HL, LH, LL)
        """
        # Cohesion Note: local_morans_i is in econometrics module
        from krl_geospatial.econometrics import local_morans_i
        
        result = local_morans_i(values, weights, permutations=permutations)
        
        # Handle both object and dict return types
        if hasattr(result, 'Is'):
            return {
                "Is": result.Is,
                "p_values": getattr(result, 'p_sim', getattr(result, 'p_values', None)),
                "quadrants": getattr(result, 'q', getattr(result, 'quadrants', None)),
            }
        elif isinstance(result, dict):
            return result
        else:
            return {"Is": result, "p_values": None, "quadrants": None}
    
    def choropleth_data(
        self,
        gdf: GeoDataFrame,
        column: str,
        *,
        scheme: str = "quantiles",
        k: int = 5,
    ) -> dict[str, Any]:
        """
        Prepare data for choropleth visualization.
        
        Args:
            gdf: GeoDataFrame with geometry and data.
            column: Column to map.
            scheme: Classification scheme ('quantiles', 'equal_interval', 'natural_breaks').
            k: Number of classes.
        
        Returns:
            Dict with classification breaks and class assignments.
        """
        # Cohesion Note: Use numpy-based classification directly.
        # krl_geospatial.mapping.classify_values exists but we keep this
        # self-contained to avoid tight coupling for a simple operation.
        import numpy as np
        
        values = gdf[column].values
        
        if scheme == "quantiles":
            breaks = np.percentile(values, np.linspace(0, 100, k + 1))
        elif scheme == "equal_interval":
            breaks = np.linspace(values.min(), values.max(), k + 1)
        elif scheme == "natural_breaks":
            # Simple natural breaks using percentile approximation
            breaks = np.percentile(values, np.linspace(0, 100, k + 1))
        else:
            raise ValueError(f"Unknown scheme: {scheme}. Use 'quantiles', 'equal_interval', or 'natural_breaks'.")
        
        # Classify values into bins
        classes = np.digitize(values, breaks[1:-1])
        
        return {
            "breaks": breaks.tolist(),
            "classes": classes.tolist(),
            "scheme": scheme,
            "k": k,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Spatial Econometric Adapters for REMSOM Integration
# ════════════════════════════════════════════════════════════════════════════════


class SpatialLagAdapter:
    """
    Spatial Autoregressive (SAR) Model Adapter.
    
    Estimates spatial lag models where the dependent variable is influenced
    by spatially weighted neighbors:
    
        y = ρWy + Xβ + ε
    
    Where:
        - ρ (rho): Spatial autoregressive coefficient
        - W: Row-standardized spatial weights matrix
        - Wy: Spatial lag of dependent variable
        - Xβ: Exogenous variables
    
    Used by REMSOM to model spatial spillover effects in opportunity scores.
    """
    
    def __init__(self) -> None:
        """Initialize SAR adapter."""
        self._model = None
        self._results = None
    
    def fit(
        self,
        y: "np.ndarray",
        X: "np.ndarray",
        weights: Any,
    ) -> dict[str, Any]:
        """
        Fit Spatial Lag (SAR) model.
        
        Args:
            y: Dependent variable array (n,).
            X: Independent variable matrix (n, k).
            weights: Spatial weights object or matrix.
        
        Returns:
            Dict with model results including rho, betas, and diagnostics.
        """
        try:
            from krl_geospatial.econometrics import SpatialLag
            self._model = SpatialLag(y, X, weights)
            self._results = self._model.fit()
        except ImportError:
            # Fallback: Simple OLS with spatial lag as regressor
            import numpy as np
            W = self._weights_to_matrix(weights, len(y))
            Wy = W @ y
            X_aug = np.column_stack([Wy, X])
            betas = np.linalg.lstsq(X_aug, y, rcond=None)[0]
            rho = betas[0]
            residuals = y - X_aug @ betas
            return {
                "rho": float(rho),
                "betas": betas[1:].tolist(),
                "residuals": residuals,
                "r_squared": 1 - (residuals.var() / y.var()),
                "aic": None,
                "method": "ols_fallback",
            }
        
        return {
            "rho": float(getattr(self._results, 'rho', 0.0)),
            "betas": list(getattr(self._results, 'betas', [])),
            "residuals": getattr(self._results, 'residuals', None),
            "r_squared": float(getattr(self._results, 'r_squared', 0.0)),
            "aic": getattr(self._results, 'aic', None),
            "method": "ml",
        }
    
    def predict(self, X: "np.ndarray", weights: Any) -> "np.ndarray":
        """Predict using fitted SAR model."""
        if self._results is None:
            raise ValueError("Model not fitted. Call fit() first.")
        if hasattr(self._results, 'predict'):
            return self._results.predict(X, weights)
        # Fallback
        import numpy as np
        rho = self._results.get('rho', 0.0) if isinstance(self._results, dict) else getattr(self._results, 'rho', 0.0)
        betas = self._results.get('betas', []) if isinstance(self._results, dict) else getattr(self._results, 'betas', [])
        Xb = X @ np.array(betas)
        return Xb / (1 - rho)  # Reduced form approximation
    
    @staticmethod
    def _weights_to_matrix(weights: Any, n: int) -> "np.ndarray":
        """Convert weights object to numpy matrix."""
        import numpy as np
        if hasattr(weights, 'full'):
            return weights.full()[0]
        elif hasattr(weights, 'sparse'):
            return weights.sparse.toarray()
        elif isinstance(weights, np.ndarray):
            return weights
        else:
            return np.eye(n)


class SpatialErrorAdapter:
    """
    Spatial Error Model (SEM) Adapter.
    
    Estimates models where errors exhibit spatial autocorrelation:
    
        y = Xβ + u
        u = λWu + ε
    
    Where:
        - λ (lambda): Spatial error coefficient
        - W: Spatial weights matrix
        - Wu: Spatial lag of errors
    
    Used by REMSOM to account for spatially correlated unobservables.
    """
    
    def __init__(self) -> None:
        """Initialize SEM adapter."""
        self._model = None
        self._results = None
    
    def fit(
        self,
        y: "np.ndarray",
        X: "np.ndarray",
        weights: Any,
    ) -> dict[str, Any]:
        """
        Fit Spatial Error model.
        
        Args:
            y: Dependent variable array (n,).
            X: Independent variable matrix (n, k).
            weights: Spatial weights object or matrix.
        
        Returns:
            Dict with lambda, betas, and diagnostics.
        """
        try:
            from krl_geospatial.econometrics import SpatialError
            self._model = SpatialError(y, X, weights)
            self._results = self._model.fit()
        except ImportError:
            # Fallback: Cochrane-Orcutt style iteration
            import numpy as np
            W = self._weights_to_matrix(weights, len(y))
            
            # Initial OLS
            betas = np.linalg.lstsq(X, y, rcond=None)[0]
            residuals = y - X @ betas
            
            # Estimate lambda from residual spatial correlation
            W_resid = W @ residuals
            lambda_est = np.corrcoef(residuals, W_resid)[0, 1]
            
            # GLS transform
            I = np.eye(len(y))
            A = I - lambda_est * W
            y_t = A @ y
            X_t = A @ X
            betas_gls = np.linalg.lstsq(X_t, y_t, rcond=None)[0]
            residuals_gls = y_t - X_t @ betas_gls
            
            return {
                "lambda": float(lambda_est),
                "betas": betas_gls.tolist(),
                "residuals": residuals_gls,
                "r_squared": 1 - (residuals_gls.var() / y.var()),
                "aic": None,
                "method": "gls_fallback",
            }
        
        return {
            "lambda": float(getattr(self._results, 'lam', 0.0)),
            "betas": list(getattr(self._results, 'betas', [])),
            "residuals": getattr(self._results, 'residuals', None),
            "r_squared": float(getattr(self._results, 'r_squared', 0.0)),
            "aic": getattr(self._results, 'aic', None),
            "method": "ml",
        }
    
    @staticmethod
    def _weights_to_matrix(weights: Any, n: int) -> "np.ndarray":
        """Convert weights object to numpy matrix."""
        import numpy as np
        if hasattr(weights, 'full'):
            return weights.full()[0]
        elif hasattr(weights, 'sparse'):
            return weights.sparse.toarray()
        elif isinstance(weights, np.ndarray):
            return weights
        else:
            return np.eye(n)


class GWRAdapter:
    """
    Geographically Weighted Regression (GWR) Adapter.
    
    Estimates local regression models where coefficients vary spatially:
    
        y_i = β_0(u_i, v_i) + Σ β_k(u_i, v_i) x_ik + ε_i
    
    Where (u_i, v_i) are the coordinates of observation i, allowing
    coefficients to vary continuously across space.
    
    Used by REMSOM to detect spatial heterogeneity in opportunity drivers.
    """
    
    def __init__(self, bandwidth: float | None = None) -> None:
        """
        Initialize GWR adapter.
        
        Args:
            bandwidth: Fixed bandwidth for kernel weighting.
                If None, uses adaptive bandwidth selection.
        """
        self.bandwidth = bandwidth
        self._model = None
        self._results = None
    
    def fit(
        self,
        y: "np.ndarray",
        X: "np.ndarray",
        coordinates: "np.ndarray",
        kernel: str = "bisquare",
    ) -> dict[str, Any]:
        """
        Fit Geographically Weighted Regression.
        
        Args:
            y: Dependent variable array (n,).
            X: Independent variable matrix (n, k).
            coordinates: Spatial coordinates array (n, 2).
            kernel: Kernel function type ('gaussian', 'bisquare', 'exponential').
        
        Returns:
            Dict with local betas, local R-squared, and diagnostics.
        """
        try:
            from krl_geospatial.econometrics import GWR
            self._model = GWR(
                coordinates=coordinates,
                y=y,
                X=X,
                bw=self.bandwidth,
                kernel=kernel,
            )
            self._results = self._model.fit()
        except ImportError:
            # Fallback: Simple local regression at each point
            import numpy as np
            n = len(y)
            k = X.shape[1] if X.ndim > 1 else 1
            
            local_betas = np.zeros((n, k))
            local_r2 = np.zeros(n)
            
            # Default bandwidth if not set
            bw = self.bandwidth or np.median(self._pairwise_distances(coordinates))
            
            for i in range(n):
                # Compute distances from point i
                dists = np.sqrt(((coordinates - coordinates[i]) ** 2).sum(axis=1))
                
                # Compute kernel weights
                if kernel == "gaussian":
                    weights = np.exp(-0.5 * (dists / bw) ** 2)
                elif kernel == "bisquare":
                    weights = np.where(dists < bw, (1 - (dists / bw) ** 2) ** 2, 0)
                else:  # exponential
                    weights = np.exp(-dists / bw)
                
                # Weighted least squares
                W = np.diag(weights)
                try:
                    XtWX = X.T @ W @ X
                    XtWy = X.T @ W @ y
                    local_betas[i] = np.linalg.solve(XtWX, XtWy)
                    y_pred = X @ local_betas[i]
                    ss_res = np.sum(weights * (y - y_pred) ** 2)
                    ss_tot = np.sum(weights * (y - np.average(y, weights=weights)) ** 2)
                    local_r2[i] = 1 - ss_res / ss_tot if ss_tot > 0 else 0
                except np.linalg.LinAlgError:
                    local_betas[i] = np.zeros(k)
                    local_r2[i] = 0
            
            return {
                "local_betas": local_betas,
                "local_r_squared": local_r2,
                "bandwidth": bw,
                "aic": None,
                "method": "wls_fallback",
            }
        
        return {
            "local_betas": getattr(self._results, 'params', None),
            "local_r_squared": getattr(self._results, 'localR2', None),
            "bandwidth": getattr(self._model, 'bw', self.bandwidth),
            "aic": getattr(self._results, 'aic', None),
            "method": "gwr",
        }
    
    @staticmethod
    def _pairwise_distances(coords: "np.ndarray") -> "np.ndarray":
        """Compute all pairwise distances."""
        import numpy as np
        n = len(coords)
        distances = []
        for i in range(n):
            for j in range(i + 1, n):
                d = np.sqrt(((coords[i] - coords[j]) ** 2).sum())
                distances.append(d)
        return np.array(distances)
