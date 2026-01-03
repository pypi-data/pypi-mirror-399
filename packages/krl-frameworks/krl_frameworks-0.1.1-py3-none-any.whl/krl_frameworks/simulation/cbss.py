# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - CBSS Simulation Engine
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Cohort-Based State Simulation (CBSS) Engine.

This module provides the core simulation infrastructure for deterministic,
vectorized cohort-state evolution. All framework simulations flow through
the CBSSEngine which manages:

- State initialization from DataBundle
- Temporal evolution via transition functions
- Policy shock injection
- Trajectory accumulation
- Convergence detection

Architecture Notes:
    The CBSS pattern treats populations as cohorts (age×sector×geography)
    and evolves their state vectors through discrete time steps. This
    enables:
    
    1. Deterministic reproducibility (seeded RNG per cohort)
    2. Vectorized NumPy execution (no Python loops over cohorts)
    3. Clean separation of transition logic from engine mechanics

Example:
    >>> engine = CBSSEngine(seed=42)
    >>> trajectory = engine.simulate(
    ...     initial_state=state,
    ...     transition_fn=my_transition,
    ...     n_periods=20,
    ...     policy_shocks=[shock1, shock2],
    ... )
    >>> print(trajectory.final_state)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Sequence

import numpy as np

from krl_frameworks.core.exceptions import (
    ConvergenceError,
    SimulationError,
    StateValidationError,
)
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier, requires_tier

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig, SimulationConfig

__all__ = [
    "CBSSEngine",
    "TransitionFunction",
    "PolicyShock",
    "PolicyShockEngine",
    "ConvergenceChecker",
    "SimulationResult",
]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Transition Functions
# ════════════════════════════════════════════════════════════════════════════════


class TransitionFunction(ABC):
    """
    Abstract base class for cohort state transition functions.
    
    A transition function defines how the cohort state evolves from
    time t to t+1. Implementations must be vectorized (operate on
    the full CohortStateVector, not individual cohorts).
    
    Attributes:
        name: Human-readable name for logging/debugging.
    """
    
    name: str = "BaseTransition"
    
    @abstractmethod
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        """
        Apply transition to evolve state from t to t+1.
        
        Args:
            state: Current cohort state vector at time t.
            t: Current time period (0-indexed).
            config: Framework configuration.
            params: Optional framework-specific parameters.
            
        Returns:
            New CohortStateVector representing state at t+1.
            
        Note:
            Must be a pure function - do not mutate input state.
            Must be vectorized - use NumPy operations, no Python loops.
        """
        ...

    def validate_state(self, state: CohortStateVector) -> None:
        """Validate state before transition. Override if needed."""
        state.validate()


class IdentityTransition(TransitionFunction):
    """No-op transition that returns state unchanged. Useful for testing."""
    
    name = "IdentityTransition"
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        return state


class LinearDecayTransition(TransitionFunction):
    """
    Simple linear decay transition for testing.
    
    Applies decay factor to employment_prob each period.
    """
    
    name = "LinearDecayTransition"
    
    def __init__(self, decay_rate: float = 0.01):
        self.decay_rate = decay_rate
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        return state.apply_shock("employment_prob", delta=-self.decay_rate)


class CompositeTransition(TransitionFunction):
    """
    Composes multiple transition functions in sequence.
    
    Useful for combining domain-specific transitions.
    """
    
    name = "CompositeTransition"
    
    def __init__(self, *transitions: TransitionFunction):
        self.transitions = transitions
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        for transition in self.transitions:
            state = transition(state, t, config, params=params)
        return state


# ════════════════════════════════════════════════════════════════════════════════
# Policy Shocks
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class PolicyShock:
    """
    Represents an exogenous policy shock applied at a specific time.
    
    Policy shocks modify the cohort state vector at their activation
    time, simulating interventions like:
    - Employment stimulus programs
    - Housing subsidy changes
    - Healthcare policy reforms
    - Education investment shifts
    
    Attributes:
        name: Descriptive name for the shock.
        activation_time: Time period when shock activates (0-indexed).
        target_field: CohortStateVector field to modify.
        delta: Additive change to apply (can be negative).
        multiplier: Multiplicative change (applied after delta).
        cohort_mask: Optional boolean mask for targeted cohorts.
        duration: Number of periods shock persists (None = permanent).
        metadata: Additional shock metadata.
    """
    
    name: str
    activation_time: int
    target_field: str
    delta: float = 0.0
    multiplier: float = 1.0
    cohort_mask: Optional[np.ndarray] = field(default=None, repr=False)
    duration: Optional[int] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        valid_fields = {
            "employment_prob",
            "health_burden_score",
            "credit_access_prob",
            "housing_cost_ratio",
            "opportunity_score",
        }
        if self.target_field not in valid_fields:
            raise ValueError(
                f"target_field must be one of {valid_fields}, "
                f"got {self.target_field!r}"
            )
        if self.activation_time < 0:
            raise ValueError("activation_time must be non-negative")
    
    def is_active(self, t: int) -> bool:
        """Check if shock is active at time t."""
        if t < self.activation_time:
            return False
        if self.duration is None:
            return True
        return t < self.activation_time + self.duration
    
    def apply(self, state: CohortStateVector) -> CohortStateVector:
        """Apply shock to state vector."""
        current = getattr(state, self.target_field)
        
        # Apply delta and multiplier
        modified = (current + self.delta) * self.multiplier
        
        # Apply cohort mask if specified
        if self.cohort_mask is not None:
            modified = np.where(self.cohort_mask, modified, current)
        
        # Clamp probabilities to [0, 1]
        if "prob" in self.target_field or "score" in self.target_field:
            modified = np.clip(modified, 0.0, 1.0)
        
        return state.with_field(self.target_field, modified)


class PolicyShockEngine:
    """
    Manages policy shock scheduling and application.
    
    Tracks active shocks and applies them at appropriate times
    during simulation.
    """
    
    def __init__(self, shocks: Optional[Sequence[PolicyShock]] = None):
        self.shocks = list(shocks) if shocks else []
        self._shock_log: list[dict[str, Any]] = []
    
    def add_shock(self, shock: PolicyShock) -> None:
        """Add a policy shock to the schedule."""
        self.shocks.append(shock)
    
    def get_active_shocks(self, t: int) -> list[PolicyShock]:
        """Get all shocks active at time t."""
        return [s for s in self.shocks if s.is_active(t)]
    
    def apply_shocks(
        self,
        state: CohortStateVector,
        t: int,
    ) -> CohortStateVector:
        """Apply all active shocks to state at time t."""
        active = self.get_active_shocks(t)
        
        for shock in active:
            state = shock.apply(state)
            self._shock_log.append({
                "time": t,
                "shock_name": shock.name,
                "target_field": shock.target_field,
                "delta": shock.delta,
                "multiplier": shock.multiplier,
            })
            logger.debug(f"Applied shock '{shock.name}' at t={t}")
        
        return state
    
    @property
    def shock_log(self) -> list[dict[str, Any]]:
        """Return log of all applied shocks."""
        return self._shock_log.copy()
    
    def clear_log(self) -> None:
        """Clear the shock application log."""
        self._shock_log.clear()


# ════════════════════════════════════════════════════════════════════════════════
# Convergence Checking
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ConvergenceChecker:
    """
    Checks for simulation convergence / steady state.
    
    Convergence is detected when state changes fall below
    tolerance for consecutive periods.
    
    Attributes:
        tolerance: Maximum L2 norm of state change for convergence.
        patience: Consecutive periods below tolerance needed.
        enabled: Whether to check convergence (False = run all periods).
    """
    
    tolerance: float = 1e-6
    patience: int = 3
    enabled: bool = True
    
    _consecutive_below: int = field(default=0, init=False, repr=False)
    _converged_at: Optional[int] = field(default=None, init=False, repr=False)
    
    def reset(self) -> None:
        """Reset convergence state for new simulation."""
        self._consecutive_below = 0
        self._converged_at = None
    
    def check(
        self,
        prev_state: CohortStateVector,
        curr_state: CohortStateVector,
        t: int,
    ) -> bool:
        """
        Check if simulation has converged.
        
        Args:
            prev_state: State at t-1.
            curr_state: State at t.
            t: Current time period.
            
        Returns:
            True if converged, False otherwise.
        """
        if not self.enabled:
            return False
        
        # Compute L2 norm of employment_prob change (primary indicator)
        delta = np.linalg.norm(
            curr_state.employment_prob - prev_state.employment_prob
        )
        
        if delta < self.tolerance:
            self._consecutive_below += 1
        else:
            self._consecutive_below = 0
        
        if self._consecutive_below >= self.patience:
            self._converged_at = t
            logger.info(f"Convergence detected at t={t} (delta={delta:.2e})")
            return True
        
        return False
    
    @property
    def converged_at(self) -> Optional[int]:
        """Time period when convergence was detected."""
        return self._converged_at


# ════════════════════════════════════════════════════════════════════════════════
# Simulation Result
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class SimulationResult:
    """
    Container for simulation output.
    
    Attributes:
        trajectory: Full state trajectory over time.
        converged: Whether simulation converged early.
        convergence_time: Time of convergence (None if not converged).
        shock_log: Log of applied policy shocks.
        metrics: Framework-computed metrics from trajectory.
        diagnostics: Engine-level diagnostics.
    """
    
    trajectory: StateTrajectory
    converged: bool = False
    convergence_time: Optional[int] = None
    shock_log: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    
    @property
    def final_state(self) -> CohortStateVector:
        """Get final state from trajectory."""
        return self.trajectory.final_state
    
    @property
    def n_periods_simulated(self) -> int:
        """Number of periods actually simulated."""
        return len(self.trajectory)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize result to dictionary."""
        return {
            "n_periods_simulated": self.n_periods_simulated,
            "converged": self.converged,
            "convergence_time": self.convergence_time,
            "shock_log": self.shock_log,
            "metrics": self.metrics,
            "diagnostics": self.diagnostics,
            "final_state": self.final_state.to_dict(),
        }


# ════════════════════════════════════════════════════════════════════════════════
# CBSS Engine
# ════════════════════════════════════════════════════════════════════════════════


class CBSSEngine:
    """
    Cohort-Based State Simulation Engine.
    
    The CBSSEngine is the core execution runtime for all framework
    simulations. It manages:
    
    - Deterministic random state (seeded per simulation)
    - State validation at each step
    - Transition function execution
    - Policy shock injection
    - Convergence detection
    - Trajectory accumulation
    
    Example:
        >>> engine = CBSSEngine(seed=42)
        >>> result = engine.simulate(
        ...     initial_state=initial,
        ...     transition_fn=mpi_transition,
        ...     n_periods=20,
        ... )
        >>> print(result.final_state.employment_prob.mean())
    
    Attributes:
        seed: Random seed for reproducibility.
        validate_states: Whether to validate states each step.
    """
    
    def __init__(
        self,
        seed: Optional[int] = None,
        validate_states: bool = True,
    ):
        self.seed = seed if seed is not None else np.random.default_rng().integers(0, 2**31)
        self.validate_states = validate_states
        self._rng = np.random.default_rng(self.seed)
        self._run_count = 0
    
    def simulate(
        self,
        initial_state: CohortStateVector,
        transition_fn: TransitionFunction,
        n_periods: int,
        config: Optional[FrameworkConfig] = None,
        *,
        policy_shocks: Optional[Sequence[PolicyShock]] = None,
        convergence: Optional[ConvergenceChecker] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> SimulationResult:
        """
        Run CBSS simulation.
        
        Args:
            initial_state: Starting cohort state vector.
            transition_fn: Transition function to apply each period.
            n_periods: Maximum number of periods to simulate.
            config: Framework configuration.
            policy_shocks: Sequence of policy shocks to apply.
            convergence: Convergence checker (None = no early stopping).
            params: Framework-specific parameters for transition.
            
        Returns:
            SimulationResult containing trajectory and metadata.
            
        Raises:
            SimulationError: If simulation fails.
            StateValidationError: If state validation fails.
        """
        from krl_frameworks.core.config import FrameworkConfig
        
        self._run_count += 1
        run_id = f"run_{self._run_count:04d}"
        
        logger.info(f"Starting CBSS simulation {run_id}: n_periods={n_periods}")
        
        # Setup
        config = config or FrameworkConfig()
        shock_engine = PolicyShockEngine(policy_shocks)
        convergence = convergence or ConvergenceChecker(enabled=False)
        convergence.reset()
        
        # Validate initial state
        if self.validate_states:
            try:
                initial_state.validate()
            except Exception as e:
                raise StateValidationError(f"Initial state invalid: {e}") from e
        
        # Initialize trajectory with initial state
        trajectory = StateTrajectory(states=[initial_state])
        current_state = initial_state
        converged = False
        
        # Main simulation loop
        try:
            for t in range(n_periods):
                # Store previous for convergence check
                prev_state = current_state
                
                # Apply transition
                current_state = transition_fn(
                    current_state, t, config, params=params
                )
                
                # Apply policy shocks
                current_state = shock_engine.apply_shocks(current_state, t)
                
                # Validate new state
                if self.validate_states:
                    current_state.validate()
                
                # Record in trajectory
                trajectory.append(current_state)
                
                # Check convergence
                if convergence.check(prev_state, current_state, t):
                    converged = True
                    logger.info(f"Simulation {run_id} converged at t={t}")
                    break
        
        except StateValidationError:
            raise
        except Exception as e:
            raise SimulationError(
                f"Simulation {run_id} failed at t={t}: {e}"
            ) from e
        
        # Build result
        result = SimulationResult(
            trajectory=trajectory,
            converged=converged,
            convergence_time=convergence.converged_at,
            shock_log=shock_engine.shock_log,
            diagnostics={
                "run_id": run_id,
                "seed": self.seed,
                "n_cohorts": initial_state.n_cohorts,
                "n_periods_requested": n_periods,
            },
        )
        
        logger.info(
            f"Simulation {run_id} complete: "
            f"{result.n_periods_simulated} periods, converged={converged}"
        )
        
        return result
    
    @requires_tier(Tier.ENTERPRISE)
    def simulate_parallel(
        self,
        initial_states: Sequence[CohortStateVector],
        transition_fn: TransitionFunction,
        n_periods: int,
        config: Optional[FrameworkConfig] = None,
        **kwargs,
    ) -> list[SimulationResult]:
        """
        Run multiple simulations in parallel.
        
        Enterprise-tier feature for scenario analysis.
        
        Args:
            initial_states: Sequence of initial states for each scenario.
            transition_fn: Transition function to apply.
            n_periods: Maximum periods per simulation.
            config: Framework configuration.
            **kwargs: Additional arguments passed to simulate().
            
        Returns:
            List of SimulationResult, one per initial state.
        """
        # Note: In production, this would use multiprocessing or joblib
        # For now, sequential execution with different seeds
        results = []
        for i, state in enumerate(initial_states):
            # Create sub-engine with unique seed
            sub_engine = CBSSEngine(
                seed=self.seed + i,
                validate_states=self.validate_states,
            )
            result = sub_engine.simulate(
                initial_state=state,
                transition_fn=transition_fn,
                n_periods=n_periods,
                config=config,
                **kwargs,
            )
            results.append(result)
        
        return results
    
    def reset(self) -> None:
        """Reset engine state for fresh simulation run."""
        self._rng = np.random.default_rng(self.seed)
        self._run_count = 0
