# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Layer 3: Experimental / Research Frameworks
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Layer 3: Experimental and Research Analysis Frameworks.

This module provides frameworks for causal inference and
experimental analysis, including randomized controlled trials
and quasi-experimental methods.

Team Tier:
    - RCTFramework: Randomized Controlled Trial analysis
    - DiDFramework: Difference-in-Differences estimation
    - SyntheticControlFramework: Synthetic Control Method
    - PropensityScoreFramework: Propensity Score Matching / IPW
    - RegressionDiscontinuityFramework: Sharp/Fuzzy RDD
    - InstrumentalVariablesFramework: 2SLS / IV estimation
    - TWFEFramework: Two-Way Fixed Effects panel data
    - EventStudyFramework: Event Study analysis

Professional Tier:
    - DMLFramework: Double Machine Learning (debiased ML)
    - BayesianCausalFramework: Bayesian causal inference
    - TimeSeriesCausalFramework: Time series causal methods (ITS, Granger)
    - MLCausalFramework: ML-based causal inference (meta-learners, CATE)
    - SpatialCausalFramework: Spatial Causal (GCCM/Matching)
    - SDABMFramework: System Dynamics - Agent-Based Model Hybrids
    - MultilayerNetworkFramework: Multilayer Spatial-Network Engines
    - BunchingFramework: Bunching estimator for policy evaluation
"""

from krl_frameworks.layers.experimental.rct import RCTFramework
from krl_frameworks.layers.experimental.did import DiDFramework
from krl_frameworks.layers.experimental.synthetic_control import SyntheticControlFramework
from krl_frameworks.layers.experimental.psm import PropensityScoreFramework
from krl_frameworks.layers.experimental.rdd import RegressionDiscontinuityFramework
from krl_frameworks.layers.experimental.iv import InstrumentalVariablesFramework
from krl_frameworks.layers.experimental.twfe import TWFEFramework
from krl_frameworks.layers.experimental.event_study import EventStudyFramework
from krl_frameworks.layers.experimental.dml import DMLFramework
from krl_frameworks.layers.experimental.bayesian import BayesianCausalFramework
from krl_frameworks.layers.experimental.timeseries import TimeSeriesCausalFramework
from krl_frameworks.layers.experimental.ml_causal import MLCausalFramework
from krl_frameworks.layers.experimental.bunching import BunchingFramework
from krl_frameworks.layers.experimental.advanced import (
    SpatialCausalFramework,
    SDABMFramework,
    MultilayerNetworkFramework,
)

__all__ = [
    # Team Tier
    "RCTFramework",
    "DiDFramework",
    "SyntheticControlFramework",
    "PropensityScoreFramework",
    "RegressionDiscontinuityFramework",
    "InstrumentalVariablesFramework",
    "TWFEFramework",
    "EventStudyFramework",
    # Professional Tier
    "DMLFramework",
    "BayesianCausalFramework",
    "TimeSeriesCausalFramework",
    "MLCausalFramework",
    "BunchingFramework",
    "SpatialCausalFramework",
    "SDABMFramework",
    "MultilayerNetworkFramework",
]
