# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - DAG Orchestration Module
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
DAG module for cross-layer framework orchestration.

Provides directed acyclic graph (DAG) based orchestration for composing
multiple frameworks into analysis pipelines with automatic dependency
resolution and execution ordering.
"""

from krl_frameworks.dag.composer import (
    DAGEdge,
    DAGNode,
    DataFlowMapper,
    ExecutionResult,
    ExecutionStatus,
    FrameworkDAG,
    PipelineBuilder,
    TopologicalExecutor,
)

__all__ = [
    "DAGEdge",
    "DAGNode",
    "DataFlowMapper",
    "ExecutionResult",
    "ExecutionStatus",
    "FrameworkDAG",
    "PipelineBuilder",
    "TopologicalExecutor",
]
