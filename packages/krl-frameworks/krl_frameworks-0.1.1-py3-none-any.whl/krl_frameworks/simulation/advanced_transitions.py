# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Advanced Transition Functions
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Advanced Transition Functions.

Sophisticated state transition implementations:
- MarkovTransition: Discrete state Markov chains
- NeuralTransition: Neural network-based transitions
- EnsembleTransition: Ensemble of multiple transition models

These extend the basic TransitionFunction for complex dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Protocol, Sequence

import numpy as np

from krl_frameworks.core import (
    CohortStateVector,
    FrameworkConfig,
    Tier,
    requires_tier,
)
from krl_frameworks.simulation import TransitionFunction


# ════════════════════════════════════════════════════════════════════════════════
# Markov Chain Transition
# ════════════════════════════════════════════════════════════════════════════════


class TransitionType(Enum):
    """Type of Markov transition."""
    HOMOGENEOUS = "Time-homogeneous"
    NON_HOMOGENEOUS = "Time-varying"
    ABSORBING = "Absorbing states"
    ERGODIC = "Ergodic"


@dataclass
class MarkovConfig:
    """Configuration for Markov transitions."""
    
    # Number of discrete states
    n_states: int = 5
    
    # Transition type
    transition_type: TransitionType = TransitionType.HOMOGENEOUS
    
    # State names (optional)
    state_names: list[str] = field(default_factory=lambda: [
        "Very Low", "Low", "Medium", "High", "Very High"
    ])
    
    # Time-varying parameters
    time_decay: float = 0.0  # 0 = no decay
    
    # Absorbing state indices (if applicable)
    absorbing_states: list[int] = field(default_factory=list)


class MarkovTransition(TransitionFunction):
    """
    Markov Chain Transition Function.
    
    Models discrete state transitions using transition probability matrices.
    Supports:
    - Time-homogeneous chains
    - Time-varying (non-homogeneous) chains
    - Absorbing state dynamics
    - Continuous-time approximations
    
    Example:
        >>> config = MarkovConfig(n_states=3)
        >>> P = np.array([
        ...     [0.8, 0.15, 0.05],
        ...     [0.1, 0.7, 0.2],
        ...     [0.05, 0.15, 0.8]
        ... ])
        >>> markov = MarkovTransition(P, config)
        >>> new_state = markov(state, t=0, config=framework_config)
    """
    
    def __init__(
        self,
        transition_matrix: np.ndarray,
        config: Optional[MarkovConfig] = None,
        time_varying_matrices: Optional[dict[int, np.ndarray]] = None,
    ):
        """
        Initialize Markov transition.
        
        Args:
            transition_matrix: Base transition probability matrix (n_states x n_states)
            config: Markov configuration
            time_varying_matrices: Optional time-indexed transition matrices
        """
        self.config = config or MarkovConfig()
        self.P = self._validate_matrix(transition_matrix)
        self.time_varying = time_varying_matrices or {}
        
        # Override n_states from the actual matrix dimension
        self.n_states = self.P.shape[0]
        
        # Compute stationary distribution for ergodic chains
        self._stationary = self._compute_stationary() if not self.config.absorbing_states else None
    
    def _validate_matrix(self, P: np.ndarray) -> np.ndarray:
        """Validate transition matrix properties."""
        if P.ndim != 2 or P.shape[0] != P.shape[1]:
            raise ValueError("Transition matrix must be square")
        
        if not np.allclose(P.sum(axis=1), 1.0, atol=1e-6):
            raise ValueError("Transition matrix rows must sum to 1")
        
        if np.any(P < 0):
            raise ValueError("Transition probabilities must be non-negative")
        
        return P
    
    def _compute_stationary(self) -> np.ndarray:
        """Compute stationary distribution."""
        n = self.P.shape[0]
        
        # Solve (P^T - I) * pi = 0 with sum(pi) = 1
        A = self.P.T - np.eye(n)
        A = np.vstack([A, np.ones(n)])
        b = np.zeros(n + 1)
        b[-1] = 1
        
        try:
            pi, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
            pi = np.maximum(pi, 0)  # Ensure non-negative
            pi = pi / pi.sum()  # Normalize
            return pi
        except np.linalg.LinAlgError:
            return np.ones(n) / n
    
    def _get_matrix(self, t: int) -> np.ndarray:
        """Get transition matrix for time t."""
        if t in self.time_varying:
            return self.time_varying[t]
        
        if self.config.transition_type == TransitionType.NON_HOMOGENEOUS:
            # Apply time decay
            decay = np.exp(-self.config.time_decay * t)
            
            # Blend toward uniform
            n = self.P.shape[0]
            uniform = np.ones((n, n)) / n
            
            return decay * self.P + (1 - decay) * uniform
        
        return self.P
    
    @requires_tier(Tier.TEAM)
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """
        Apply Markov transition.
        
        Args:
            state: Current cohort state
            t: Time step
            config: Framework configuration
            params: Optional parameters (unused)
        
        Returns:
            Updated CohortStateVector
        """
        params = params or {}
        
        P_t = self._get_matrix(t)
        n_states = self.n_states  # Use matrix-derived n_states
        
        # Discretize continuous state to Markov state
        # Use opportunity_score as primary state indicator
        current_scores = state.opportunity_score
        
        # Map to discrete states
        state_indices = np.clip(
            (current_scores * n_states).astype(int),
            0, n_states - 1
        )
        
        # Apply transition probabilities
        new_scores = np.zeros_like(current_scores)
        
        for i, idx in enumerate(state_indices):
            # Sample new state from transition probabilities
            probs = P_t[idx]
            new_idx = np.random.choice(n_states, p=probs)
            
            # Convert back to continuous (midpoint of state)
            new_scores[i] = (new_idx + 0.5) / n_states
        
        # Update other state components based on opportunity transition
        score_change = new_scores - current_scores
        
        # Employment tends to follow opportunity
        new_employment = np.clip(
            state.employment_prob + score_change * 0.3,
            0.0, 1.0
        )
        
        # Health burden inversely related
        new_burden = np.clip(
            state.health_burden_score - score_change * 0.2,
            0.0, 1.0
        )
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=new_burden,
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=np.clip(new_scores, 0.0, 1.0),
            sector_output=state.sector_output,
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )
    
    @property
    def stationary_distribution(self) -> Optional[np.ndarray]:
        """Get stationary distribution if ergodic."""
        return self._stationary
    
    def expected_hitting_time(self, from_state: int, to_state: int) -> float:
        """
        Calculate expected hitting time from one state to another.
        
        Args:
            from_state: Starting state index
            to_state: Target state index
        
        Returns:
            Expected number of steps to reach target
        """
        if from_state == to_state:
            return 0.0
        
        n = self.P.shape[0]
        
        # Create modified transition matrix (make target absorbing)
        P_mod = self.P.copy()
        P_mod[to_state, :] = 0
        P_mod[to_state, to_state] = 1
        
        # Fundamental matrix N = (I - Q)^(-1) where Q excludes target
        mask = np.array([i != to_state for i in range(n)])
        Q = P_mod[mask][:, mask]
        
        try:
            I = np.eye(Q.shape[0])
            N = np.linalg.inv(I - Q)
            
            # Expected hitting time is sum of row in N
            from_idx = sum(1 for i in range(from_state) if i != to_state)
            return N[from_idx].sum()
        except np.linalg.LinAlgError:
            return float('inf')


# ════════════════════════════════════════════════════════════════════════════════
# Neural Network Transition
# ════════════════════════════════════════════════════════════════════════════════


class ActivationFn(Enum):
    """Neural network activation functions."""
    RELU = "relu"
    TANH = "tanh"
    SIGMOID = "sigmoid"
    SOFTPLUS = "softplus"


@dataclass
class NeuralConfig:
    """Configuration for neural transitions."""
    
    # Architecture
    hidden_layers: list[int] = field(default_factory=lambda: [64, 32])
    activation: ActivationFn = ActivationFn.TANH
    
    # Input/output
    input_dim: int = 6  # State dimensions
    output_dim: int = 6
    
    # Regularization
    dropout_rate: float = 0.0
    l2_reg: float = 0.0
    
    # Constraints
    output_bounds: tuple[float, float] = (0.0, 1.0)
    residual_connection: bool = True


class NeuralTransition(TransitionFunction):
    """
    Neural Network Transition Function.
    
    Uses a feedforward neural network to learn complex transition dynamics.
    Supports:
    - Flexible architecture specification
    - Residual connections for stable training
    - Output bounds enforcement
    - Time-conditioned transitions
    
    Note: This is a simplified implementation. For production use,
    integrate with PyTorch/TensorFlow backends.
    
    Example:
        >>> config = NeuralConfig(hidden_layers=[128, 64])
        >>> neural = NeuralTransition(config)
        >>> neural.set_weights(trained_weights)
        >>> new_state = neural(state, t=0, config=framework_config)
    """
    
    def __init__(
        self,
        config: Optional[NeuralConfig] = None,
        weights: Optional[list[np.ndarray]] = None,
    ):
        """
        Initialize neural transition.
        
        Args:
            config: Neural network configuration
            weights: Pre-trained weights (alternating W, b)
        """
        self.config = config or NeuralConfig()
        
        # Initialize weights
        self.weights: list[np.ndarray] = []
        self.biases: list[np.ndarray] = []
        
        if weights:
            self.set_weights(weights)
        else:
            self._init_weights()
    
    def _init_weights(self) -> None:
        """Initialize weights with Xavier initialization."""
        dims = [self.config.input_dim + 1] + self.config.hidden_layers + [self.config.output_dim]
        
        for i in range(len(dims) - 1):
            fan_in, fan_out = dims[i], dims[i + 1]
            scale = np.sqrt(2.0 / (fan_in + fan_out))
            
            W = np.random.randn(fan_in, fan_out) * scale
            b = np.zeros(fan_out)
            
            self.weights.append(W)
            self.biases.append(b)
    
    def set_weights(self, weights: list[np.ndarray]) -> None:
        """Set network weights from flat list."""
        self.weights = []
        self.biases = []
        
        for i in range(0, len(weights), 2):
            self.weights.append(weights[i])
            self.biases.append(weights[i + 1])
    
    def _activation(self, x: np.ndarray) -> np.ndarray:
        """Apply activation function."""
        if self.config.activation == ActivationFn.RELU:
            return np.maximum(0, x)
        elif self.config.activation == ActivationFn.TANH:
            return np.tanh(x)
        elif self.config.activation == ActivationFn.SIGMOID:
            return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))
        elif self.config.activation == ActivationFn.SOFTPLUS:
            return np.log1p(np.exp(np.clip(x, -500, 500)))
        return x
    
    def _forward(self, x: np.ndarray, t: int) -> np.ndarray:
        """Forward pass through network."""
        # Add time as input feature
        t_normalized = t / 100.0  # Normalize time
        x_with_t = np.concatenate([x, np.full((x.shape[0], 1), t_normalized)], axis=1)
        
        h = x_with_t
        
        for i, (W, b) in enumerate(zip(self.weights, self.biases)):
            z = h @ W + b
            
            # Apply activation (except last layer)
            if i < len(self.weights) - 1:
                h = self._activation(z)
            else:
                h = z
        
        # Apply output bounds
        low, high = self.config.output_bounds
        h = np.clip(h, low, high)
        
        return h
    
    @requires_tier(Tier.ENTERPRISE)
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """
        Apply neural transition.
        
        Args:
            state: Current cohort state
            t: Time step
            config: Framework configuration
            params: Optional parameters
        
        Returns:
            Updated CohortStateVector
        """
        params = params or {}
        
        # Extract state vector
        n_cohorts = len(state.employment_prob)
        
        state_array = np.column_stack([
            state.employment_prob,
            state.health_burden_score,
            state.credit_access_prob,
            state.housing_cost_ratio,
            state.opportunity_score,
            state.sector_output.mean(axis=1) if state.sector_output.ndim > 1 else state.sector_output,
        ])
        
        # Forward pass
        output = self._forward(state_array, t)
        
        # Apply residual connection
        if self.config.residual_connection:
            output = state_array[:, :6] + 0.1 * output
            output = np.clip(output, 0.0, 1.0)
        
        # Reconstruct state
        return CohortStateVector(
            employment_prob=output[:, 0],
            health_burden_score=output[:, 1],
            credit_access_prob=output[:, 2],
            housing_cost_ratio=output[:, 3],
            opportunity_score=output[:, 4],
            sector_output=state.sector_output * (1 + 0.01 * (output[:, 5:6] - 0.5)),
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )
    
    def train(
        self,
        states: list[CohortStateVector],
        next_states: list[CohortStateVector],
        epochs: int = 100,
        learning_rate: float = 0.001,
    ) -> list[float]:
        """
        Train the neural transition on state pairs.
        
        Args:
            states: Current states
            next_states: Next states (targets)
            epochs: Training epochs
            learning_rate: Learning rate
        
        Returns:
            Training loss history
        """
        losses = []
        
        # Prepare training data
        X = []
        Y = []
        
        for state, next_state in zip(states, next_states):
            x = np.column_stack([
                state.employment_prob,
                state.health_burden_score,
                state.credit_access_prob,
                state.housing_cost_ratio,
                state.opportunity_score,
                state.sector_output.mean(axis=1),
            ])
            y = np.column_stack([
                next_state.employment_prob,
                next_state.health_burden_score,
                next_state.credit_access_prob,
                next_state.housing_cost_ratio,
                next_state.opportunity_score,
                next_state.sector_output.mean(axis=1),
            ])
            X.append(x)
            Y.append(y)
        
        X = np.vstack(X)
        Y = np.vstack(Y)
        
        for epoch in range(epochs):
            # Forward pass
            pred = self._forward(X, epoch)
            
            # Compute loss
            loss = np.mean((pred - Y) ** 2)
            losses.append(loss)
            
            # Simplified gradient update (would use autograd in practice)
            # This is a placeholder for demonstration
            error = pred - Y
            
            # Update last layer weights
            if self.weights:
                self.weights[-1] -= learning_rate * (self.weights[-1] * 0.01)
        
        return losses


# ════════════════════════════════════════════════════════════════════════════════
# Ensemble Transition
# ════════════════════════════════════════════════════════════════════════════════


class EnsembleMethod(Enum):
    """Ensemble combination methods."""
    MEAN = "Average"
    WEIGHTED = "Weighted Average"
    MEDIAN = "Median"
    BEST = "Best Performer"
    STACKING = "Stacking"


@dataclass
class EnsembleConfig:
    """Configuration for ensemble transitions."""
    
    # Combination method
    method: EnsembleMethod = EnsembleMethod.MEAN
    
    # Weights for weighted average
    weights: Optional[list[float]] = None
    
    # Adaptive weighting
    adaptive: bool = False
    adaptation_rate: float = 0.1
    
    # Uncertainty quantification
    compute_uncertainty: bool = True


class EnsembleTransition(TransitionFunction):
    """
    Ensemble Transition Function.
    
    Combines multiple transition functions for robust predictions:
    - Mean/median aggregation
    - Weighted combinations
    - Adaptive weighting based on performance
    - Uncertainty quantification
    
    Example:
        >>> markov = MarkovTransition(P_matrix)
        >>> linear = LinearTransition()
        >>> neural = NeuralTransition()
        >>> ensemble = EnsembleTransition([markov, linear, neural])
        >>> new_state, uncertainty = ensemble(state, t=0, config=config)
    """
    
    def __init__(
        self,
        transitions: list[TransitionFunction],
        config: Optional[EnsembleConfig] = None,
    ):
        """
        Initialize ensemble transition.
        
        Args:
            transitions: List of transition functions to combine
            config: Ensemble configuration
        """
        self.transitions = transitions
        self.config = config or EnsembleConfig()
        
        # Initialize weights
        n = len(transitions)
        if self.config.weights:
            self._weights = np.array(self.config.weights)
        else:
            self._weights = np.ones(n) / n
        
        # Performance tracking for adaptive weighting
        self._performance: list[float] = [1.0] * n
        self._last_predictions: list[CohortStateVector] = []
    
    @property
    def weights(self) -> np.ndarray:
        """Current ensemble weights."""
        return self._weights
    
    def _combine_states(
        self,
        states: list[CohortStateVector],
        weights: np.ndarray,
    ) -> CohortStateVector:
        """Combine multiple states using configured method."""
        method = self.config.method
        
        if method == EnsembleMethod.MEDIAN:
            # Stack and take median
            employment = np.median([s.employment_prob for s in states], axis=0)
            health = np.median([s.health_burden_score for s in states], axis=0)
            credit = np.median([s.credit_access_prob for s in states], axis=0)
            housing = np.median([s.housing_cost_ratio for s in states], axis=0)
            opportunity = np.median([s.opportunity_score for s in states], axis=0)
            output = np.median([s.sector_output for s in states], axis=0)
        else:
            # Weighted average
            employment = sum(w * s.employment_prob for w, s in zip(weights, states))
            health = sum(w * s.health_burden_score for w, s in zip(weights, states))
            credit = sum(w * s.credit_access_prob for w, s in zip(weights, states))
            housing = sum(w * s.housing_cost_ratio for w, s in zip(weights, states))
            opportunity = sum(w * s.opportunity_score for w, s in zip(weights, states))
            output = sum(w * s.sector_output for w, s in zip(weights, states))
        
        return CohortStateVector(
            employment_prob=np.clip(employment, 0, 1),
            health_burden_score=np.clip(health, 0, 1),
            credit_access_prob=np.clip(credit, 0, 1),
            housing_cost_ratio=np.clip(housing, 0, 1),
            opportunity_score=np.clip(opportunity, 0, 1),
            sector_output=output,
            deprivation_vector=states[0].deprivation_vector,
            step=states[0].step,
        )
    
    def _compute_uncertainty(
        self,
        states: list[CohortStateVector],
    ) -> dict[str, np.ndarray]:
        """Compute prediction uncertainty from ensemble spread."""
        return {
            "employment_std": np.std([s.employment_prob for s in states], axis=0),
            "health_std": np.std([s.health_burden_score for s in states], axis=0),
            "opportunity_std": np.std([s.opportunity_score for s in states], axis=0),
            "overall_std": np.mean([
                np.std([s.employment_prob for s in states], axis=0),
                np.std([s.opportunity_score for s in states], axis=0),
            ], axis=0),
        }
    
    def _update_weights(
        self,
        actual: CohortStateVector,
        predictions: list[CohortStateVector],
    ) -> None:
        """Update weights based on prediction performance."""
        if not self.config.adaptive:
            return
        
        # Compute errors for each model
        errors = []
        for pred in predictions:
            mse = np.mean((pred.opportunity_score - actual.opportunity_score) ** 2)
            errors.append(mse)
        
        # Convert errors to performance (inverse)
        errors = np.array(errors) + 1e-8
        performance = 1.0 / errors
        performance = performance / performance.sum()
        
        # Update with exponential moving average
        alpha = self.config.adaptation_rate
        self._weights = (1 - alpha) * self._weights + alpha * performance
        self._weights = self._weights / self._weights.sum()
    
    @requires_tier(Tier.ENTERPRISE)
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """
        Apply ensemble transition.
        
        Args:
            state: Current cohort state
            t: Time step
            config: Framework configuration
            params: Optional parameters
        
        Returns:
            Combined CohortStateVector
        """
        params = params or {}
        
        # Get predictions from all models
        predictions = []
        for transition in self.transitions:
            try:
                pred = transition(state, t, config, params)
                predictions.append(pred)
            except Exception:
                # Skip failed models
                pass
        
        if not predictions:
            # Return unchanged state if all models fail
            return CohortStateVector(
                employment_prob=state.employment_prob,
                health_burden_score=state.health_burden_score,
                credit_access_prob=state.credit_access_prob,
                housing_cost_ratio=state.housing_cost_ratio,
                opportunity_score=state.opportunity_score,
                sector_output=state.sector_output,
                deprivation_vector=state.deprivation_vector,
                step=t + 1,
            )
        
        # Adjust weights for available models
        weights = self._weights[:len(predictions)]
        weights = weights / weights.sum()
        
        # Combine predictions
        combined = self._combine_states(predictions, weights)
        
        # Store for adaptive updating
        self._last_predictions = predictions
        
        return combined
    
    def get_uncertainty(self) -> Optional[dict[str, np.ndarray]]:
        """Get uncertainty from last prediction."""
        if not self._last_predictions or not self.config.compute_uncertainty:
            return None
        return self._compute_uncertainty(self._last_predictions)
    
    def update_from_observation(self, observed: CohortStateVector) -> None:
        """Update weights based on observed outcome."""
        if self._last_predictions:
            self._update_weights(observed, self._last_predictions)


# ════════════════════════════════════════════════════════════════════════════════
# Linear Transition (Utility)
# ════════════════════════════════════════════════════════════════════════════════


class LinearTransition(TransitionFunction):
    """
    Simple linear transition for baseline/testing.
    
    Applies a linear transformation: x_{t+1} = A * x_t + b
    """
    
    def __init__(
        self,
        A: Optional[np.ndarray] = None,
        b: Optional[np.ndarray] = None,
    ):
        """Initialize linear transition."""
        self.A = A if A is not None else np.eye(6) * 0.99
        self.b = b if b is not None else np.zeros(6)
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        params: Optional[dict[str, Any]] = None,
    ) -> CohortStateVector:
        """Apply linear transition."""
        # Extract state
        x = np.column_stack([
            state.employment_prob,
            state.health_burden_score,
            state.credit_access_prob,
            state.housing_cost_ratio,
            state.opportunity_score,
            state.sector_output.mean(axis=1),
        ])
        
        # Apply transformation
        y = x @ self.A.T + self.b
        y = np.clip(y, 0, 1)
        
        return CohortStateVector(
            employment_prob=y[:, 0],
            health_burden_score=y[:, 1],
            credit_access_prob=y[:, 2],
            housing_cost_ratio=y[:, 3],
            opportunity_score=y[:, 4],
            sector_output=state.sector_output * (0.99 + 0.02 * y[:, 5:6]),
            deprivation_vector=state.deprivation_vector,
            step=t + 1,
        )


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Markov
    "MarkovTransition",
    "MarkovConfig",
    "TransitionType",
    # Neural
    "NeuralTransition",
    "NeuralConfig",
    "ActivationFn",
    # Ensemble
    "EnsembleTransition",
    "EnsembleConfig",
    "EnsembleMethod",
    # Utility
    "LinearTransition",
]
