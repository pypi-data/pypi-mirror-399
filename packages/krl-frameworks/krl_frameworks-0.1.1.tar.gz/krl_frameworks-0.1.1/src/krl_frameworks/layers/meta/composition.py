# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Composition Engine
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Composition Engine.

Framework composition patterns for building complex analyses:
- Layered composition (stacking frameworks)
- Parallel composition (multiple independent paths)
- Sequential composition (pipeline)
- Recursive composition (nested frameworks)
- Cross-layer composition (combining layers)

References:
    - KRL Architecture: Composition patterns
    - Functional composition principles

Tier: ENTERPRISE
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Type, Union

import numpy as np

from krl_frameworks.core.base import (
    BaseMetaFramework,
    FrameworkMetadata,
    VerticalLayer,
)
from krl_frameworks.core.dashboard_spec import FrameworkDashboardSpec
from krl_frameworks.core.data_bundle import DataBundle
from krl_frameworks.core.state import CohortStateVector, StateTrajectory
from krl_frameworks.core.tier import Tier, requires_tier
from krl_frameworks.simulation.cbss import TransitionFunction

if TYPE_CHECKING:
    from krl_frameworks.core.config import FrameworkConfig

__all__ = ["CompositionEngine"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Composition Data Structures
# ════════════════════════════════════════════════════════════════════════════════


class CompositionPattern(Enum):
    """Framework composition patterns."""
    SEQUENTIAL = "Sequential (A → B → C)"
    PARALLEL = "Parallel (A ∥ B ∥ C)"
    LAYERED = "Layered (stack outputs)"
    BRANCHING = "Branching (split and merge)"
    RECURSIVE = "Recursive (nested)"
    CROSS_LAYER = "Cross-Layer (multi-domain)"


class LayerCombination(Enum):
    """Cross-layer combination strategies."""
    SOCIO_FINANCIAL = "Socioeconomic + Financial"
    SOCIO_GOVERNMENT = "Socioeconomic + Government"
    EXPERIMENTAL_META = "Experimental + Meta"
    FULL_STACK = "All layers"


@dataclass
class CompositionNode:
    """Node in composition graph."""
    
    id: str = ""
    framework_class: Optional[Type[BaseMetaFramework]] = None
    transform: Optional[Callable[[dict], dict]] = None
    children: list["CompositionNode"] = field(default_factory=list)
    
    # For nested compositions
    sub_composition: Optional["Composition"] = None


@dataclass
class Composition:
    """Composition specification."""
    
    pattern: CompositionPattern = CompositionPattern.SEQUENTIAL
    nodes: list[CompositionNode] = field(default_factory=list)
    
    # Configuration
    config: dict[str, Any] = field(default_factory=dict)
    
    # Combination function
    combine_fn: Optional[Callable[[list[dict]], dict]] = None


@dataclass
class LayerResult:
    """Result from a single layer."""
    
    layer: VerticalLayer = VerticalLayer.SOCIOECONOMIC_ACADEMIC
    metrics: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompositionResult:
    """Result from composition execution."""
    
    pattern: CompositionPattern = CompositionPattern.SEQUENTIAL
    
    # Layer results
    layer_results: list[LayerResult] = field(default_factory=list)
    
    # Combined output
    combined_metrics: dict[str, Any] = field(default_factory=dict)
    combined_output: dict[str, Any] = field(default_factory=dict)
    
    # Composition metadata
    n_layers: int = 0
    n_frameworks: int = 0


@dataclass
class CrossLayerResult:
    """Result from cross-layer composition."""
    
    combination: LayerCombination = LayerCombination.FULL_STACK
    
    # Per-layer outputs
    socioeconomic: Optional[dict[str, Any]] = None
    financial: Optional[dict[str, Any]] = None
    government: Optional[dict[str, Any]] = None
    experimental: Optional[dict[str, Any]] = None
    meta: Optional[dict[str, Any]] = None
    
    # Integrated output
    integrated_metrics: dict[str, Any] = field(default_factory=dict)
    
    # Cross-layer insights
    correlations: dict[str, float] = field(default_factory=dict)
    synergies: dict[str, float] = field(default_factory=dict)


@dataclass
class CompositionMetrics:
    """Comprehensive composition analysis."""
    
    result: CompositionResult = field(default_factory=CompositionResult)
    cross_layer: Optional[CrossLayerResult] = None
    
    # Complexity metrics
    total_frameworks: int = 0
    total_layers: int = 0
    composition_depth: int = 0


# ════════════════════════════════════════════════════════════════════════════════
# Composition Transition Function
# ════════════════════════════════════════════════════════════════════════════════


class CompositionTransition(TransitionFunction):
    """Transition function for composed framework evolution."""
    
    name = "CompositionTransition"
    
    def __init__(self, composition_synergy: float = 0.15):
        self.composition_synergy = composition_synergy
    
    def __call__(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> CohortStateVector:
        params = params or {}
        
        n_layers = params.get("n_layers", 1)
        synergy = self.composition_synergy * np.log1p(n_layers)
        
        # Cross-layer synergy improves all dimensions
        new_opportunity = np.clip(state.opportunity_score + synergy * 0.02, 0, 1)
        new_employment = np.clip(state.employment_prob + synergy * 0.01, 0.1, 0.95)
        
        return CohortStateVector(
            employment_prob=new_employment,
            health_burden_score=state.health_burden_score * (1 - synergy * 0.02),
            credit_access_prob=state.credit_access_prob,
            housing_cost_ratio=state.housing_cost_ratio,
            opportunity_score=new_opportunity,
            sector_output=state.sector_output * (1 + synergy * 0.01),
            deprivation_vector=state.deprivation_vector * (1 - synergy * 0.02),
        )


# ════════════════════════════════════════════════════════════════════════════════
# Composition Engine
# ════════════════════════════════════════════════════════════════════════════════


class CompositionEngine(BaseMetaFramework):
    """
    Composition Engine.
    
    Framework composition patterns for complex analyses:
    
    - Sequential, parallel, and layered composition
    - Cross-layer integration
    - Recursive nesting
    - Custom combination functions
    
    Token Weight: 9
    Tier: ENTERPRISE
    
    Example:
        >>> engine = CompositionEngine()
        >>> composition = engine.build_composition([
        ...     WBIFramework,
        ...     SystemicRiskFramework,
        ... ], pattern=CompositionPattern.CROSS_LAYER)
        >>> result = engine.execute_composition(composition, data)
    
    References:
        - KRL Architecture Documentation
    """
    
    METADATA = FrameworkMetadata(
        slug="composition-engine",
        name="Composition Engine",
        version="1.0.0",
        layer=VerticalLayer.META_PEER_FRAMEWORKS,
        tier=Tier.ENTERPRISE,
        description=(
            "Framework composition engine for building complex multi-layer "
            "analyses with cross-layer integration."
        ),
        required_domains=["frameworks", "composition_pattern"],
        output_domains=["integrated_metrics", "cross_layer_insights"],
        constituent_models=["sequential", "parallel", "cross_layer", "recursive"],
        tags=["composition", "meta", "cross-layer", "integration"],
        author="Khipu Research Labs",
        license="Apache-2.0",
    )
    
    def __init__(self):
        super().__init__()
        self._transition_fn = CompositionTransition()
        self._layer_frameworks: dict[VerticalLayer, list[Type[BaseMetaFramework]]] = {}
    
    @classmethod
    def metadata(cls) -> FrameworkMetadata:
        return cls.METADATA
    
    def _compute_initial_state(
        self,
        bundle: DataBundle,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        n_cohorts = config.cohort_size or 100
        return CohortStateVector(
            employment_prob=np.full(n_cohorts, 0.70),
            health_burden_score=np.full(n_cohorts, 0.2),
            credit_access_prob=np.full(n_cohorts, 0.70),
            housing_cost_ratio=np.full(n_cohorts, 0.30),
            opportunity_score=np.full(n_cohorts, 0.5),
            sector_output=np.full((n_cohorts, 5), 1000.0),
            deprivation_vector=np.full((n_cohorts, 6), 0.25),
        )
    
    def _transition(
        self,
        state: CohortStateVector,
        t: int,
        config: FrameworkConfig,
    ) -> CohortStateVector:
        n_layers = len(self._layer_frameworks)
        return self._transition_fn(state, t, config, params={"n_layers": n_layers})
    
    def _compute_metrics(self, state: CohortStateVector) -> dict[str, Any]:
        return {
            "mean_outcome": float(np.mean(state.opportunity_score)),
            "n_layers": len(self._layer_frameworks),
        }
    
    def _compute_output(
        self,
        trajectory: StateTrajectory,
        config: FrameworkConfig,
    ) -> dict[str, Any]:
        return {"framework": "composition-engine", "n_periods": trajectory.n_periods}
    
    # ════════════════════════════════════════════════════════════════════════════
    # Public API Methods
    # ════════════════════════════════════════════════════════════════════════════
    
    @requires_tier(Tier.ENTERPRISE)
    def register_layer(
        self,
        layer: VerticalLayer,
        frameworks: list[Type[BaseMetaFramework]],
    ) -> None:
        """
        Register frameworks for a layer.
        
        Args:
            layer: Vertical layer
            frameworks: List of framework classes
        """
        self._layer_frameworks[layer] = frameworks
        logger.info(f"Registered {len(frameworks)} frameworks for {layer.name}")
    
    @requires_tier(Tier.ENTERPRISE)
    def build_composition(
        self,
        framework_classes: list[Type[BaseMetaFramework]],
        pattern: CompositionPattern = CompositionPattern.SEQUENTIAL,
        config: Optional[dict[str, Any]] = None,
    ) -> Composition:
        """
        Build a composition from framework classes.
        
        Args:
            framework_classes: List of framework classes
            pattern: Composition pattern
            config: Optional configuration
        
        Returns:
            Composition specification
        """
        nodes = []
        
        for i, cls in enumerate(framework_classes):
            node = CompositionNode(
                id=f"node_{i}_{cls.__name__}",
                framework_class=cls,
            )
            nodes.append(node)
        
        return Composition(
            pattern=pattern,
            nodes=nodes,
            config=config or {},
        )
    
    @requires_tier(Tier.ENTERPRISE)
    def execute_composition(
        self,
        composition: Composition,
        data: dict[str, Any],
    ) -> CompositionResult:
        """
        Execute a composition.
        
        Args:
            composition: Composition specification
            data: Input data
        
        Returns:
            Composition execution result
        """
        layer_results = []
        all_metrics: dict[str, list[float]] = {}
        
        if composition.pattern == CompositionPattern.SEQUENTIAL:
            # Sequential: pass output of each to next
            current_data = data.copy()
            
            for node in composition.nodes:
                if node.framework_class:
                    framework = node.framework_class()
                    meta = framework.metadata()
                    
                    # Execute framework
                    if hasattr(framework, "run"):
                        result = framework.run(current_data)
                    else:
                        result = {"metrics": {}, "output": {}}
                    
                    layer_result = LayerResult(
                        layer=meta.layer,
                        metrics=result.get("metrics", {}),
                        output=result.get("output", {}),
                    )
                    layer_results.append(layer_result)
                    
                    # Accumulate metrics
                    for key, value in layer_result.metrics.items():
                        if isinstance(value, (int, float)):
                            if key not in all_metrics:
                                all_metrics[key] = []
                            all_metrics[key].append(float(value))
                    
                    # Pass output to next
                    current_data.update(result.get("output", {}))
        
        elif composition.pattern == CompositionPattern.PARALLEL:
            # Parallel: execute all independently
            for node in composition.nodes:
                if node.framework_class:
                    framework = node.framework_class()
                    meta = framework.metadata()
                    
                    if hasattr(framework, "run"):
                        result = framework.run(data)
                    else:
                        result = {"metrics": {}, "output": {}}
                    
                    layer_result = LayerResult(
                        layer=meta.layer,
                        metrics=result.get("metrics", {}),
                        output=result.get("output", {}),
                    )
                    layer_results.append(layer_result)
                    
                    for key, value in layer_result.metrics.items():
                        if isinstance(value, (int, float)):
                            if key not in all_metrics:
                                all_metrics[key] = []
                            all_metrics[key].append(float(value))
        
        elif composition.pattern == CompositionPattern.LAYERED:
            # Layered: stack outputs
            stacked_output: dict[str, list[Any]] = {}
            
            for node in composition.nodes:
                if node.framework_class:
                    framework = node.framework_class()
                    meta = framework.metadata()
                    
                    if hasattr(framework, "run"):
                        result = framework.run(data)
                    else:
                        result = {"metrics": {}, "output": {}}
                    
                    layer_result = LayerResult(
                        layer=meta.layer,
                        metrics=result.get("metrics", {}),
                        output=result.get("output", {}),
                    )
                    layer_results.append(layer_result)
                    
                    # Stack outputs
                    for key, value in result.get("output", {}).items():
                        if key not in stacked_output:
                            stacked_output[key] = []
                        stacked_output[key].append(value)
                    
                    for key, value in layer_result.metrics.items():
                        if isinstance(value, (int, float)):
                            if key not in all_metrics:
                                all_metrics[key] = []
                            all_metrics[key].append(float(value))
        
        # Combine metrics
        combined_metrics = {
            key: float(np.mean(values))
            for key, values in all_metrics.items()
        }
        
        # Custom combine function
        if composition.combine_fn:
            outputs = [r.output for r in layer_results]
            combined_output = composition.combine_fn(outputs)
        else:
            combined_output = {}
            for r in layer_results:
                combined_output.update(r.output)
        
        return CompositionResult(
            pattern=composition.pattern,
            layer_results=layer_results,
            combined_metrics=combined_metrics,
            combined_output=combined_output,
            n_layers=len(set(r.layer for r in layer_results)),
            n_frameworks=len(layer_results),
        )
    
    @requires_tier(Tier.ENTERPRISE)
    def cross_layer_composition(
        self,
        combination: LayerCombination,
        data: dict[str, Any],
    ) -> CrossLayerResult:
        """
        Execute cross-layer composition.
        
        Args:
            combination: Layer combination type
            data: Input data
        
        Returns:
            Cross-layer composition result
        """
        result = CrossLayerResult(combination=combination)
        all_outputs: list[dict[str, Any]] = []
        
        # Execute registered frameworks per layer
        if combination in (LayerCombination.SOCIO_FINANCIAL, LayerCombination.FULL_STACK):
            if VerticalLayer.SOCIOECONOMIC_ACADEMIC in self._layer_frameworks:
                socio_outputs = []
                for cls in self._layer_frameworks[VerticalLayer.SOCIOECONOMIC_ACADEMIC]:
                    framework = cls()
                    if hasattr(framework, "run"):
                        socio_outputs.append(framework.run(data))
                
                if socio_outputs:
                    result.socioeconomic = {
                        "n_frameworks": len(socio_outputs),
                        "outputs": socio_outputs,
                    }
                    all_outputs.extend(socio_outputs)
            
            if VerticalLayer.FINANCIAL_ECONOMIC in self._layer_frameworks:
                fin_outputs = []
                for cls in self._layer_frameworks[VerticalLayer.FINANCIAL_ECONOMIC]:
                    framework = cls()
                    if hasattr(framework, "run"):
                        fin_outputs.append(framework.run(data))
                
                if fin_outputs:
                    result.financial = {
                        "n_frameworks": len(fin_outputs),
                        "outputs": fin_outputs,
                    }
                    all_outputs.extend(fin_outputs)
        
        if combination in (LayerCombination.SOCIO_GOVERNMENT, LayerCombination.FULL_STACK):
            if VerticalLayer.GOVERNMENT_POLICY in self._layer_frameworks:
                gov_outputs = []
                for cls in self._layer_frameworks[VerticalLayer.GOVERNMENT_POLICY]:
                    framework = cls()
                    if hasattr(framework, "run"):
                        gov_outputs.append(framework.run(data))
                
                if gov_outputs:
                    result.government = {
                        "n_frameworks": len(gov_outputs),
                        "outputs": gov_outputs,
                    }
                    all_outputs.extend(gov_outputs)
        
        if combination in (LayerCombination.EXPERIMENTAL_META, LayerCombination.FULL_STACK):
            if VerticalLayer.EXPERIMENTAL_RESEARCH in self._layer_frameworks:
                exp_outputs = []
                for cls in self._layer_frameworks[VerticalLayer.EXPERIMENTAL_RESEARCH]:
                    framework = cls()
                    if hasattr(framework, "run"):
                        exp_outputs.append(framework.run(data))
                
                if exp_outputs:
                    result.experimental = {
                        "n_frameworks": len(exp_outputs),
                        "outputs": exp_outputs,
                    }
                    all_outputs.extend(exp_outputs)
            
            if VerticalLayer.META_PEER_FRAMEWORKS in self._layer_frameworks:
                meta_outputs = []
                for cls in self._layer_frameworks[VerticalLayer.META_PEER_FRAMEWORKS]:
                    framework = cls()
                    if hasattr(framework, "run"):
                        meta_outputs.append(framework.run(data))
                
                if meta_outputs:
                    result.meta = {
                        "n_frameworks": len(meta_outputs),
                        "outputs": meta_outputs,
                    }
                    all_outputs.extend(meta_outputs)
        
        # Compute integrated metrics
        if all_outputs:
            integrated: dict[str, list[float]] = {}
            
            for output in all_outputs:
                if isinstance(output, dict):
                    for key, value in output.get("metrics", {}).items():
                        if isinstance(value, (int, float)):
                            if key not in integrated:
                                integrated[key] = []
                            integrated[key].append(float(value))
            
            result.integrated_metrics = {
                key: float(np.mean(values))
                for key, values in integrated.items()
            }
        
        # Compute cross-layer synergies (simplified)
        result.synergies = {
            "socio_financial": 0.15 if result.socioeconomic and result.financial else 0.0,
            "socio_government": 0.12 if result.socioeconomic and result.government else 0.0,
            "experimental_meta": 0.10 if result.experimental and result.meta else 0.0,
        }
        
        return result
    
    @requires_tier(Tier.ENTERPRISE)
    def analyze_composition(
        self,
        framework_classes: list[Type[BaseMetaFramework]],
        data: dict[str, Any],
        pattern: CompositionPattern = CompositionPattern.SEQUENTIAL,
    ) -> CompositionMetrics:
        """
        Comprehensive composition analysis.
        
        Args:
            framework_classes: List of framework classes
            data: Input data
            pattern: Composition pattern
        
        Returns:
            Complete composition metrics
        """
        # Build and execute composition
        composition = self.build_composition(framework_classes, pattern)
        result = self.execute_composition(composition, data)
        
        # Cross-layer if multiple layers
        cross_layer = None
        if result.n_layers > 1:
            # Register frameworks by layer
            for cls in framework_classes:
                framework = cls()
                meta = framework.metadata()
                
                if meta.layer not in self._layer_frameworks:
                    self._layer_frameworks[meta.layer] = []
                self._layer_frameworks[meta.layer].append(cls)
            
            cross_layer = self.cross_layer_composition(
                LayerCombination.FULL_STACK,
                data,
            )
        
        # Compute composition depth (max nesting)
        def get_depth(nodes: list[CompositionNode], depth: int = 1) -> int:
            max_depth = depth
            for node in nodes:
                if node.sub_composition:
                    child_depth = get_depth(node.sub_composition.nodes, depth + 1)
                    max_depth = max(max_depth, child_depth)
            return max_depth
        
        composition_depth = get_depth(composition.nodes)
        
        return CompositionMetrics(
            result=result,
            cross_layer=cross_layer,
            total_frameworks=result.n_frameworks,
            total_layers=result.n_layers,
            composition_depth=composition_depth,
        )

    @classmethod
    def dashboard_spec(cls) -> FrameworkDashboardSpec:
        """
        Return Composition Engine dashboard specification.

        Parameters extracted from CompositionTransition and composition patterns.
        """
        return FrameworkDashboardSpec(
            slug="composition-engine",
            name="Composition Engine",
            description="Meta-framework for composing multiple frameworks in sequential, parallel, layered, or cross-layer patterns",
            layer="meta",
            min_tier=Tier.ENTERPRISE,
            parameters_schema={
                "type": "object",
                "properties": {
                    # ═══════════════════════════════════════════════════════
                    # Composition Configuration
                    # ═══════════════════════════════════════════════════════
                    "composition_pattern": {
                        "type": "string",
                        "title": "Composition Pattern",
                        "description": "Framework composition strategy",
                        "enum": [
                            "sequential",
                            "parallel",
                            "layered",
                            "branching",
                            "recursive",
                            "cross_layer",
                        ],
                        "default": "sequential",
                        "x-ui-widget": "select",
                        "x-ui-group": "composition",
                        "x-ui-order": 1,
                        "x-ui-help": "Sequential: A→B→C, Parallel: A∥B∥C, Cross-Layer: multi-domain integration",
                    },
                    "layer_combination": {
                        "type": "string",
                        "title": "Layer Combination",
                        "description": "Cross-layer integration strategy (for cross_layer pattern)",
                        "enum": [
                            "socio_financial",
                            "socio_government",
                            "experimental_meta",
                            "full_stack",
                        ],
                        "default": "full_stack",
                        "x-ui-widget": "select",
                        "x-ui-group": "composition",
                        "x-ui-order": 2,
                        "x-ui-help": "Applicable only when composition_pattern = cross_layer",
                    },
                    "composition_synergy": {
                        "type": "number",
                        "title": "Composition Synergy Factor",
                        "description": "Cross-framework synergy multiplier (positive feedback)",
                        "minimum": 0.0,
                        "maximum": 0.5,
                        "default": 0.15,
                        "x-ui-widget": "slider",
                        "x-ui-group": "composition",
                        "x-ui-order": 3,
                        "x-ui-help": "Higher values amplify benefits from multi-framework composition",
                    },

                    # ═══════════════════════════════════════════════════════
                    # Framework Selection
                    # ═══════════════════════════════════════════════════════
                    "n_frameworks": {
                        "type": "integer",
                        "title": "Number of Frameworks",
                        "description": "Number of frameworks to compose",
                        "minimum": 2,
                        "maximum": 10,
                        "default": 3,
                        "x-ui-widget": "number",
                        "x-ui-group": "selection",
                        "x-ui-order": 4,
                        "x-ui-help": "Total frameworks in composition (minimum: 2)",
                    },
                    "n_layers": {
                        "type": "integer",
                        "title": "Number of Layers",
                        "description": "Number of vertical layers involved",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 2,
                        "x-ui-widget": "number",
                        "x-ui-group": "selection",
                        "x-ui-order": 5,
                        "x-ui-help": "Cross-layer compositions integrate multiple vertical layers",
                    },

                    # ═══════════════════════════════════════════════════════
                    # Execution Configuration
                    # ═══════════════════════════════════════════════════════
                    "parallel_execution": {
                        "type": "boolean",
                        "title": "Enable Parallel Execution",
                        "description": "Execute independent frameworks in parallel (faster)",
                        "default": True,
                        "x-ui-widget": "checkbox",
                        "x-ui-group": "execution",
                        "x-ui-order": 6,
                        "x-ui-help": "Parallelization only for patterns: parallel, layered, branching",
                    },
                    "max_composition_depth": {
                        "type": "integer",
                        "title": "Maximum Composition Depth",
                        "description": "Maximum nesting depth for recursive compositions",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 3,
                        "x-ui-widget": "number",
                        "x-ui-group": "execution",
                        "x-ui-order": 7,
                        "x-ui-help": "Prevents infinite recursion in nested compositions",
                    },
                },
                "required": ["composition_pattern"],
            },
            default_parameters={
                "composition_pattern": "sequential",
                "layer_combination": "full_stack",
                "composition_synergy": 0.15,
                "n_frameworks": 3,
                "n_layers": 2,
                "parallel_execution": True,
                "max_composition_depth": 3,
            },
            parameter_groups=[
                {
                    "id": "composition",
                    "label": "Composition Configuration",
                    "description": "Pattern and synergy settings",
                    "order": 1,
                },
                {
                    "id": "selection",
                    "label": "Framework Selection",
                    "description": "Number of frameworks and layers to compose",
                    "order": 2,
                },
                {
                    "id": "execution",
                    "label": "Execution Configuration",
                    "description": "Parallelization and depth limits",
                    "order": 3,
                },
            ],
            output_views=[
                {
                    "id": "composition_summary",
                    "type": "table",
                    "title": "Composition Summary",
                    "description": "Overall composition metrics",
                    "config": {
                        "columns": [
                            {"key": "pattern", "label": "Pattern"},
                            {"key": "total_frameworks", "label": "Frameworks"},
                            {"key": "total_layers", "label": "Layers"},
                            {"key": "composition_depth", "label": "Depth"},
                        ],
                    },
                },
                {
                    "id": "layer_breakdown",
                    "type": "bar_chart",
                    "title": "Layer Contributions",
                    "description": "Metrics contribution from each vertical layer",
                    "config": {
                        "x_axis": "layer",
                        "y_axis": "contribution",
                        "series": [
                            {"metric_path": "layer_results", "label": "Layer Contribution"},
                        ],
                    },
                },
                {
                    "id": "cross_layer_synergies",
                    "type": "heatmap",
                    "title": "Cross-Layer Synergies",
                    "description": "Synergy matrix showing cross-layer interactions",
                    "config": {
                        "metric_path": "cross_layer.synergies",
                        "x_axis": "layer_from",
                        "y_axis": "layer_to",
                        "color_scale": "viridis",
                    },
                },
                {
                    "id": "integrated_metrics",
                    "type": "radar_chart",
                    "title": "Integrated Metrics",
                    "description": "Combined output across all composed frameworks",
                    "config": {
                        "metrics": [
                            {"path": "combined_metrics.economic", "label": "Economic"},
                            {"path": "combined_metrics.social", "label": "Social"},
                            {"path": "combined_metrics.governance", "label": "Governance"},
                            {"path": "combined_metrics.environmental", "label": "Environmental"},
                        ],
                    },
                },
                {
                    "id": "composition_graph",
                    "type": "network_diagram",
                    "title": "Composition Graph",
                    "description": "Directed graph of framework composition structure",
                    "config": {
                        "metric_path": "composition_graph",
                        "node_size_by": "complexity",
                        "edge_thickness_by": "data_flow",
                        "layout": "hierarchical",
                    },
                },
            ],
        )
