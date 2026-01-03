# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - CBSS Simulation Engine
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
CBSS (Cohort-Based State Simulation) Engine.

This module provides the core simulation runtime for deterministic,
vectorized cohort-state evolution across all meta-frameworks.

Includes advanced transition functions:
- MarkovTransition: Discrete state Markov chains
- NeuralTransition: Neural network-based transitions
- EnsembleTransition: Ensemble of multiple transition models
"""

from krl_frameworks.simulation.cbss import (
    CBSSEngine,
    ConvergenceChecker,
    CompositeTransition,
    IdentityTransition,
    LinearDecayTransition,
    PolicyShock,
    PolicyShockEngine,
    SimulationResult,
    TransitionFunction,
)

from krl_frameworks.simulation.advanced_transitions import (
    # Markov
    MarkovTransition,
    MarkovConfig,
    TransitionType,
    # Neural
    NeuralTransition,
    NeuralConfig,
    ActivationFn,
    # Ensemble
    EnsembleTransition,
    EnsembleConfig,
    EnsembleMethod,
    # Utility
    LinearTransition,
)

__all__ = [
    # CBSS Core
    "CBSSEngine",
    "ConvergenceChecker",
    "CompositeTransition",
    "IdentityTransition",
    "LinearDecayTransition",
    "PolicyShock",
    "PolicyShockEngine",
    "SimulationResult",
    "TransitionFunction",
    # Markov Transitions
    "MarkovTransition",
    "MarkovConfig",
    "TransitionType",
    # Neural Transitions
    "NeuralTransition",
    "NeuralConfig",
    "ActivationFn",
    # Ensemble Transitions
    "EnsembleTransition",
    "EnsembleConfig",
    "EnsembleMethod",
    # Utility
    "LinearTransition",
]
