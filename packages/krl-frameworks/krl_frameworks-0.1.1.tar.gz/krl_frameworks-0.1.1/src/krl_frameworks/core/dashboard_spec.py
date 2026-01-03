# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Dashboard Specification Contract
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Framework Dashboard Specification Contract.

This module defines the FrameworkDashboardSpec — the single abstraction that
enables ANY KRL framework to be rendered through a generic, schema-driven
dashboard UI without framework-specific code.

The contract has three parts:
1. Parameter Schema: JSON Schema defining what users can configure
2. Output Views: Declaration of what visualizations the framework produces
3. Metadata: Tier requirements, data domains, descriptions

Design Principles:
- Frameworks are self-describing; the dashboard is a consumer
- No special cases; if REMSOM needs a conditional, the abstraction is wrong
- JSON Schema is the lingua franca for parameter contracts
- Output views declare intent, not implementation

Usage:
    # In a framework class:
    class MyFramework(BaseMetaFramework):
        @classmethod
        def dashboard_spec(cls) -> FrameworkDashboardSpec:
            return FrameworkDashboardSpec(
                slug="my-framework",
                name="My Framework",
                ...
            )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

from krl_frameworks.core.tier import Tier

__all__ = [
    "FrameworkDashboardSpec",
    "OutputViewSpec",
    "ParameterGroupSpec",
    "ViewType",
    "ResultEnvelope",
    "ResultClass",
    "TemporalSemantics",
    "SemanticConstraints",
    "RESULT_CLASS_RENDERER_CONSTRAINTS",
]


# ════════════════════════════════════════════════════════════════════════════════
# View Type Enumeration
# ════════════════════════════════════════════════════════════════════════════════


class ViewType(str, Enum):
    """
    Standard output view types that the dashboard can render.
    
    Each type maps to a specific React component in the frontend.
    Frameworks declare intent; the dashboard handles implementation.
    """
    
    # Charts - Quantitative
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    AREA_CHART = "area_chart"
    TIMESERIES = "timeseries"
    STACKED_BAR = "stacked_bar"      # Domain contribution (signed)
    WATERFALL = "waterfall"          # Aggregation audit trail
    RANKED_BAR = "ranked_bar"        # Ordinal comparison (lollipop)
    RADAR = "radar"                  # Domain profiles (≤6 domains only)
    
    # Tables & Data
    TABLE = "table"
    PIVOT_TABLE = "pivot_table"
    PROVENANCE_TABLE = "provenance_table"  # Data lineage audit
    
    # Network & Graph
    NETWORK = "network"
    DAG = "dag"
    SANKEY = "sankey"
    
    # Spatial
    CHOROPLETH = "choropleth"        # Scalar index outputs ONLY
    BUBBLE_MAP = "bubble_map"
    FLOW_MAP = "flow_map"
    
    # Statistical
    HEATMAP = "heatmap"
    BOXPLOT = "boxplot"
    HISTOGRAM = "histogram"
    SCATTER = "scatter"
    EMBEDDING_2D = "embedding_2d"    # Latent space projection (SOM/UMAP)
    U_MATRIX = "u_matrix"            # Cluster boundary visualization
    COMPONENT_PLANE = "component_plane"  # Variable loadings per neuron
    
    # Metrics & Governance
    GAUGE = "gauge"
    KPI_CARD = "kpi_card"
    METRIC_GRID = "metric_grid"
    TRAFFIC_LIGHT = "traffic_light"  # Data quality signals
    LIMITS_TEXT = "limits_text"      # Interpretation boundaries (non-editable)
    PEER_PANEL = "peer_panel"        # Structural neighbors with distances
    
    # Specialized
    TRAJECTORY = "trajectory"
    COUNTERFACTUAL = "counterfactual"
    COHORT_MATRIX = "cohort_matrix"


# ════════════════════════════════════════════════════════════════════════════════
# Result Class Enumeration (Canonical)
# ════════════════════════════════════════════════════════════════════════════════


class ResultClass(str, Enum):
    """
    Canonical result classes for analytical frameworks.
    
    Each class has strict visualization constraints:
    - SCALAR_INDEX: Choropleths, ranked bars (NO line charts, NO trends)
    - DOMAIN_DECOMPOSITION: Stacked bars, waterfalls (NO pie charts)
    - STRUCTURAL_SIMILARITY: Embedding plots, U-matrix (NO ranked clusters)
    - CONFIDENCE_PROVENANCE: Traffic lights, provenance tables (ALWAYS visible)
    
    CRITICAL: Mixing result classes in a single visualization is PROHIBITED.
    """
    
    SCALAR_INDEX = "scalar_index"                    # Executive layer
    DOMAIN_DECOMPOSITION = "domain_decomposition"   # Analyst layer
    STRUCTURAL_SIMILARITY = "structural_similarity" # Strategic layer
    CONFIDENCE_PROVENANCE = "confidence_provenance" # Governance layer


class TemporalSemantics(str, Enum):
    """
    Temporal interpretation of framework outputs.
    
    This is NOT a view-level property; it is a framework-level constraint.
    CROSS_SECTIONAL frameworks CANNOT produce TIMESERIES views.
    """
    
    UNSPECIFIED = "unspecified"          # No temporal constraint
    CROSS_SECTIONAL = "cross_sectional"  # Static snapshot (REMSOM)
    PROJECTION = "projection"            # Forward simulation (explicit model)
    PANEL = "panel"                      # Repeated cross-sections
    TIME_SERIES = "time_series"          # Native temporal model


# ════════════════════════════════════════════════════════════════════════════════
# Result-Class-to-Renderer Compatibility Matrix (Authoritative)
# ════════════════════════════════════════════════════════════════════════════════

RESULT_CLASS_RENDERER_CONSTRAINTS: dict[ResultClass, dict[str, set[ViewType]]] = {
    ResultClass.SCALAR_INDEX: {
        "allowed": {
            ViewType.CHOROPLETH,
            ViewType.RANKED_BAR,
            ViewType.BAR_CHART,
            ViewType.METRIC_GRID,
            ViewType.KPI_CARD,
            ViewType.GAUGE,
            ViewType.TABLE,
            ViewType.LINE_CHART,  # Temporal index trajectories (HDI over time, MPI trends)
            ViewType.TIMESERIES,  # Time-series index projections
        },
        "prohibited": {
            ViewType.EMBEDDING_2D,
            ViewType.U_MATRIX,
            ViewType.SCATTER,
        },
    },
    ResultClass.DOMAIN_DECOMPOSITION: {
        "allowed": {
            ViewType.STACKED_BAR,
            ViewType.WATERFALL,
            ViewType.BAR_CHART,
            ViewType.RADAR,
            ViewType.TABLE,
            ViewType.HEATMAP,  # Sector/dimension matrices
            ViewType.HISTOGRAM,  # Distribution decomposition
        },
        "prohibited": {
            ViewType.CHOROPLETH,
            ViewType.TIMESERIES,
            ViewType.LINE_CHART,
        },
    },
    ResultClass.STRUCTURAL_SIMILARITY: {
        "allowed": {
            ViewType.EMBEDDING_2D,
            ViewType.U_MATRIX,
            ViewType.PEER_PANEL,
            ViewType.COMPONENT_PLANE,
            ViewType.HEATMAP,
            ViewType.TABLE,
            ViewType.NETWORK,  # Network graphs showing structural relationships
        },
        "required": {
            ViewType.U_MATRIX,  # Must have topology distance visualization
        },
        "prohibited": {
            ViewType.CHOROPLETH,
            ViewType.BAR_CHART,
            ViewType.RANKED_BAR,
            ViewType.TIMESERIES,
        },
    },
    ResultClass.CONFIDENCE_PROVENANCE: {
        "allowed": {
            ViewType.TRAFFIC_LIGHT,
            ViewType.PROVENANCE_TABLE,
            ViewType.LIMITS_TEXT,
            ViewType.TABLE,
            ViewType.METRIC_GRID,
        },
        "prohibited": {
            ViewType.CHOROPLETH,
            ViewType.TIMESERIES,
            ViewType.SCATTER,
        },
    },
}


# ════════════════════════════════════════════════════════════════════════════════
# Output View Specification
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class OutputViewSpec:
    """
    Specification for a single output view in the dashboard.
    
    Declares what the framework produces and how it should be rendered.
    The key must match a key in ResultEnvelope.outputs.
    
    GOVERNANCE FIELDS (Required for production frameworks):
    - result_class: Binds this view to a canonical result class for constraint validation
    - output_key: Must match framework output schema key exactly (validated at registration)
    - tab_key: Groups views into dashboard tabs for logical organization
    - temporal_semantics: Declares what time means in this output (CROSS_SECTIONAL for REMSOM)
    
    CONSTRAINT FIELDS:
    - prohibited_views: View types that MUST NOT be used for this output
    - required_views: View types that MUST be present for this output class
    
    DISPLAY FIELDS:
    - requires_geo_header: Whether to show region/geo header (default True)
    - requires_confidence_badge: Whether to show confidence indicator
    - is_required: If True, this view cannot be hidden by user
    - semantic_intent: Human-readable declaration of epistemic role
    
    BACKWARD COMPATIBILITY:
    - legacy_aliases: Old key names for migration support
    - fallback_allowed: Whether synthetic/demo data fallback is permitted (default False)
    - fallback_label_required: If fallback used, must show warning label
    
    Attributes:
        key: Unique identifier matching output data key.
        title: Human-readable title for the view tab/section.
        view_type: How this output should be rendered.
        description: Optional explanation shown in UI.
        tier_required: Minimum tier to view this output (defaults to framework tier).
        config: Optional view-specific configuration (axis labels, colors, etc.).
    """
    
    # Core fields (required)
    key: str
    title: str
    view_type: ViewType | str
    
    # Display fields
    description: str | None = None
    tier_required: Tier | None = None
    config: dict[str, Any] = field(default_factory=dict)
    
    # Governance fields (constitutional law)
    result_class: ResultClass | None = None
    output_key: str | None = None  # Must match framework output schema key
    tab_key: str | None = None  # Tab grouping (e.g., "opportunity_overview", "drivers")
    temporal_semantics: TemporalSemantics | None = None
    
    # Constraint fields
    prohibited_views: tuple[ViewType, ...] = field(default_factory=tuple)
    required_views: tuple[ViewType, ...] = field(default_factory=tuple)
    
    # Display control
    requires_geo_header: bool = True
    requires_confidence_badge: bool = False
    is_required: bool = False  # Cannot hide this view
    semantic_intent: str | None = None  # Epistemic role declaration
    
    # Backward compatibility
    legacy_aliases: tuple[str, ...] = field(default_factory=tuple)
    fallback_allowed: bool = False  # NO synthetic fallback by default
    fallback_label_required: bool = True  # If fallback used, MUST label it
    
    def __post_init__(self) -> None:
        """Validate governance constraints at construction time."""
        # If result_class is set, validate view_type against constraint matrix
        if self.result_class is not None and isinstance(self.view_type, ViewType):
            constraints = RESULT_CLASS_RENDERER_CONSTRAINTS.get(self.result_class.value, {})
            prohibited = constraints.get("prohibited", set())
            
            if self.view_type in prohibited:
                raise ValueError(
                    f"ViewType.{self.view_type.name} is PROHIBITED for result class "
                    f"{self.result_class.value}. Allowed: {constraints.get('allowed', set())}"
                )
    
    def validate_against_constraints(self) -> list[str]:
        """
        Validate this spec against RESULT_CLASS_RENDERER_CONSTRAINTS.
        Returns list of validation errors (empty if valid).
        """
        errors = []
        
        if self.result_class is None:
            errors.append(f"View '{self.key}': missing result_class (governance required)")
            return errors
        
        constraints = RESULT_CLASS_RENDERER_CONSTRAINTS.get(self.result_class.value, {})
        allowed = constraints.get("allowed", set())
        prohibited = constraints.get("prohibited", set())
        required = constraints.get("required", set())
        
        vt = self.view_type if isinstance(self.view_type, ViewType) else None
        
        if vt:
            if vt in prohibited:
                errors.append(
                    f"View '{self.key}': {vt.value} is PROHIBITED for {self.result_class.value}"
                )
            if vt not in allowed:
                errors.append(
                    f"View '{self.key}': {vt.value} is NOT ALLOWED for {self.result_class.value}"
                )
        
        return errors
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize for API response."""
        return {
            "key": self.key,
            "title": self.title,
            "view_type": self.view_type.value if isinstance(self.view_type, ViewType) else self.view_type,
            "description": self.description,
            "tier_required": self.tier_required.name if self.tier_required else None,
            "config": self.config,
            # Governance fields
            "result_class": self.result_class.value if self.result_class else None,
            "output_key": self.output_key,
            "tab_key": self.tab_key,
            "temporal_semantics": self.temporal_semantics.value if self.temporal_semantics else None,
            "requires_geo_header": self.requires_geo_header,
            "requires_confidence_badge": self.requires_confidence_badge,
            "is_required": self.is_required,
            "semantic_intent": self.semantic_intent,
            "fallback_allowed": self.fallback_allowed,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Parameter Group Specification
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ParameterGroupSpec:
    """
    Grouping specification for parameters in the UI.
    
    Parameters can be organized into collapsible sections.
    If not specified, all parameters appear in a single group.
    
    Attributes:
        key: Group identifier.
        title: Display title for the group.
        description: Optional help text.
        collapsed_by_default: Whether to show collapsed initially.
        parameters: List of parameter keys belonging to this group.
    """
    
    key: str
    title: str
    description: str | None = None
    collapsed_by_default: bool = False
    parameters: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize for API response."""
        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "collapsed_by_default": self.collapsed_by_default,
            "parameters": self.parameters,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Semantic Constraints (Framework-Level Governance)
# ════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class SemanticConstraints:
    """
    Framework-level governance constraints defining epistemic boundaries.
    
    This is the CONSTITUTIONAL LAW for what a framework can and cannot represent
    in the dashboard. Violations are caught at registration time, not runtime.
    
    TEMPORAL CONSTRAINTS:
    - prohibit_timeseries: If True, no time-axis visualizations permitted
    - temporal_semantics: Default TemporalSemantics for all outputs
    
    EXPORT CONSTRAINTS:
    - exports_require_provenance: If True, all exports MUST include data provenance
    - exports_require_confidence: If True, all exports MUST include confidence metrics
    
    VISUALIZATION CONSTRAINTS:
    - required_result_classes: Every output_view MUST declare one of these
    - prohibited_view_types: These ViewTypes are NEVER allowed for this framework
    - u_matrix_required_for_som: If framework uses SOM, U-Matrix must be available
    
    DATA CONSTRAINTS:
    - fallback_prohibited: If True, NO synthetic/demo fallback permitted (enterprise)
    - requires_production_data: If True, framework cannot run without real data
    
    Example:
        >>> constraints = SemanticConstraints(
        ...     prohibit_timeseries=True,
        ...     temporal_semantics=TemporalSemantics.CROSS_SECTIONAL,
        ...     exports_require_provenance=True,
        ...     u_matrix_required_for_som=True,
        ...     fallback_prohibited=True,
        ... )
    """
    
    # Temporal constraints
    prohibit_timeseries: bool = False
    temporal_semantics: TemporalSemantics = TemporalSemantics.UNSPECIFIED
    
    # Export constraints
    exports_require_provenance: bool = False
    exports_require_confidence: bool = False
    
    # Visualization constraints
    required_result_classes: tuple[ResultClass, ...] = field(default_factory=tuple)
    prohibited_view_types: tuple[ViewType, ...] = field(default_factory=tuple)
    u_matrix_required_for_som: bool = False
    
    # Data constraints (enterprise governance)
    fallback_prohibited: bool = False
    requires_production_data: bool = False
    
    # Epistemic documentation
    semantic_rationale: str | None = None  # Why these constraints exist
    
    def validate_output_view(self, view: "OutputViewSpec") -> list[str]:
        """
        Validate a single OutputViewSpec against these constraints.
        Returns list of violation messages (empty if valid).
        """
        errors = []
        
        vt = view.view_type if isinstance(view.view_type, ViewType) else None
        
        # Check timeseries prohibition
        if self.prohibit_timeseries and vt == ViewType.TIMESERIES:
            errors.append(
                f"View '{view.key}': TIMESERIES is PROHIBITED for this framework "
                f"(cross-sectional analysis only)"
            )
        
        # Check prohibited view types
        if vt and vt in self.prohibited_view_types:
            errors.append(
                f"View '{view.key}': {vt.value} is in framework-level prohibited list"
            )
        
        # Check result class requirement
        if self.required_result_classes and view.result_class:
            if view.result_class not in self.required_result_classes:
                errors.append(
                    f"View '{view.key}': result_class {view.result_class.value} not in "
                    f"required set {[r.value for r in self.required_result_classes]}"
                )
        
        # Check temporal semantics alignment
        if (self.temporal_semantics != TemporalSemantics.UNSPECIFIED and 
            view.temporal_semantics and
            view.temporal_semantics != self.temporal_semantics):
            errors.append(
                f"View '{view.key}': temporal_semantics {view.temporal_semantics.value} "
                f"conflicts with framework constraint {self.temporal_semantics.value}"
            )
        
        return errors
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize for API response."""
        return {
            "prohibit_timeseries": self.prohibit_timeseries,
            "temporal_semantics": self.temporal_semantics.value,
            "exports_require_provenance": self.exports_require_provenance,
            "exports_require_confidence": self.exports_require_confidence,
            "required_result_classes": [r.value for r in self.required_result_classes],
            "prohibited_view_types": [v.value for v in self.prohibited_view_types],
            "u_matrix_required_for_som": self.u_matrix_required_for_som,
            "fallback_prohibited": self.fallback_prohibited,
            "requires_production_data": self.requires_production_data,
            "semantic_rationale": self.semantic_rationale,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Framework Dashboard Specification
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class FrameworkDashboardSpec:
    """
    Complete specification for rendering a framework in the dashboard.
    
    This is the ONLY contract between krl-frameworks and the dashboard UI.
    If a framework provides a dashboard_spec(), it becomes UI-renderable.
    
    The dashboard consumes this specification to:
    1. Generate parameter controls from parameters_schema (JSON Schema)
    2. Render output views based on output_views declarations
    3. Enforce tier restrictions
    4. Show contextual documentation
    
    Attributes:
        slug: Framework unique identifier (matches registry).
        name: Human-readable display name.
        description: Brief description for catalog/tooltips.
        layer: Vertical layer (for categorization).
        
        parameters_schema: JSON Schema defining all configurable parameters.
        default_parameters: Default values for all parameters.
        parameter_groups: Optional UI grouping for parameters.
        
        required_domains: Data domains the framework needs.
        min_tier: Minimum subscription tier for access.
        
        output_views: List of output view specifications.
        
        documentation_url: Link to full documentation.
        example_config: Example configuration for tutorials.
    
    Example:
        >>> spec = FrameworkDashboardSpec(
        ...     slug="mpi",
        ...     name="Multidimensional Poverty Index",
        ...     description="Alkire-Foster MPI computation",
        ...     layer="socioeconomic",
        ...     parameters_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "health_weight": {
        ...                 "type": "number",
        ...                 "minimum": 0,
        ...                 "maximum": 1,
        ...                 "default": 0.33,
        ...                 "title": "Health Weight",
        ...                 "description": "Weight for health dimension"
        ...             }
        ...         }
        ...     },
        ...     default_parameters={"health_weight": 0.33},
        ...     required_domains=["health", "education", "income"],
        ...     min_tier=Tier.COMMUNITY,
        ...     output_views=[
        ...         OutputViewSpec("mpi_score", "MPI Score", ViewType.GAUGE),
        ...         OutputViewSpec("decomposition", "Decomposition", ViewType.BAR_CHART),
        ...     ]
        ... )
    """
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Identity
    # ─────────────────────────────────────────────────────────────────────────────
    
    slug: str
    name: str
    description: str
    layer: str
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Parameter Contract
    # ─────────────────────────────────────────────────────────────────────────────
    
    parameters_schema: dict[str, Any]
    default_parameters: dict[str, Any]
    
    # Version (default to 1.0.0, can be overridden)
    version: str = "1.0.0"
    
    parameter_groups: list[ParameterGroupSpec] = field(default_factory=list)
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Requirements
    # ─────────────────────────────────────────────────────────────────────────────
    
    required_domains: list[str] = field(default_factory=list)
    min_tier: Tier = Tier.COMMUNITY
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Outputs
    # ─────────────────────────────────────────────────────────────────────────────
    
    output_views: list[OutputViewSpec] = field(default_factory=list)
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Semantic Constraints (Constitutional Law for Framework)
    # ─────────────────────────────────────────────────────────────────────────────
    # These constraints are validated at registration time to prevent analytical
    # malpractice in the dashboard. They define what the framework CAN and CANNOT
    # do from a visualization and epistemic perspective.
    
    semantic_constraints: "SemanticConstraints | None" = None
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Documentation
    # ─────────────────────────────────────────────────────────────────────────────
    
    documentation_url: str | None = None
    example_config: dict[str, Any] | None = None
    
    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to dictionary for API response.
        
        This is what /frameworks/{slug}/spec returns.
        """
        return {
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "layer": self.layer,
            "version": self.version,
            "parameters_schema": self.parameters_schema,
            "default_parameters": self.default_parameters,
            "parameter_groups": [g.to_dict() for g in self.parameter_groups],
            "required_domains": self.required_domains,
            "min_tier": self.min_tier.name,
            "output_views": [v.to_dict() for v in self.output_views],
            "semantic_constraints": self.semantic_constraints.to_dict() if self.semantic_constraints else None,
            "documentation_url": self.documentation_url,
            "example_config": self.example_config,
        }
    
    def validate_governance(self) -> list[str]:
        """
        Validate all output views against governance constraints.
        
        This method should be called at framework registration time
        to catch visualization malpractice before runtime.
        
        Returns list of validation errors (empty if valid).
        """
        errors = []
        
        # Validate each output view against RESULT_CLASS_RENDERER_CONSTRAINTS
        for view in self.output_views:
            view_errors = view.validate_against_constraints()
            errors.extend(view_errors)
        
        # Validate against framework-level semantic constraints
        if self.semantic_constraints:
            for view in self.output_views:
                constraint_errors = self.semantic_constraints.validate_output_view(view)
                errors.extend(constraint_errors)
            
            # Check U-Matrix requirement for SOM-based frameworks
            if self.semantic_constraints.u_matrix_required_for_som:
                has_som_output = any(
                    v.result_class == ResultClass.STRUCTURAL_SIMILARITY 
                    for v in self.output_views
                )
                has_u_matrix = any(
                    v.view_type == ViewType.U_MATRIX 
                    for v in self.output_views
                )
                if has_som_output and not has_u_matrix:
                    errors.append(
                        f"Framework '{self.slug}': U_MATRIX is REQUIRED for "
                        f"frameworks with STRUCTURAL_SIMILARITY outputs (SOM-based)"
                    )
        
        return errors
    
    def validate_parameters(self, params: dict[str, Any]) -> list[str]:
        """
        Validate parameters against schema.
        
        Returns list of validation errors (empty if valid).
        Uses jsonschema if available, basic validation otherwise.
        """
        errors = []
        
        try:
            import jsonschema
            validator = jsonschema.Draft7Validator(self.parameters_schema)
            for error in validator.iter_errors(params):
                errors.append(f"{'.'.join(str(p) for p in error.path)}: {error.message}")
        except ImportError:
            # Basic validation without jsonschema
            schema_props = self.parameters_schema.get("properties", {})
            required = self.parameters_schema.get("required", [])
            
            for req in required:
                if req not in params:
                    errors.append(f"Missing required parameter: {req}")
            
            for key, value in params.items():
                if key in schema_props:
                    prop_schema = schema_props[key]
                    prop_type = prop_schema.get("type")
                    
                    if prop_type == "number" and not isinstance(value, (int, float)):
                        errors.append(f"{key}: expected number, got {type(value).__name__}")
                    elif prop_type == "integer" and not isinstance(value, int):
                        errors.append(f"{key}: expected integer, got {type(value).__name__}")
                    elif prop_type == "string" and not isinstance(value, str):
                        errors.append(f"{key}: expected string, got {type(value).__name__}")
                    elif prop_type == "boolean" and not isinstance(value, bool):
                        errors.append(f"{key}: expected boolean, got {type(value).__name__}")
                    elif prop_type == "array" and not isinstance(value, list):
                        errors.append(f"{key}: expected array, got {type(value).__name__}")
                    
                    # Range validation
                    if prop_type in ("number", "integer"):
                        if "minimum" in prop_schema and value < prop_schema["minimum"]:
                            errors.append(f"{key}: value {value} below minimum {prop_schema['minimum']}")
                        if "maximum" in prop_schema and value > prop_schema["maximum"]:
                            errors.append(f"{key}: value {value} above maximum {prop_schema['maximum']}")
        
        return errors


# ════════════════════════════════════════════════════════════════════════════════
# Result Envelope
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class ResultEnvelope:
    """
    Standardized result container for framework execution.
    
    The dashboard expects all framework outputs in this envelope.
    Keys in `outputs` must match OutputViewSpec.key declarations.
    
    Attributes:
        framework: Framework slug that produced this result.
        parameters: Parameters used for execution.
        outputs: Dict of output data keyed by OutputViewSpec.key.
        metrics: Summary metrics for KPI display.
        metadata: Execution metadata (runtime, tier, confidence, etc.).
        execution_id: Unique identifier for this execution.
        timestamp: When execution completed.
    """
    
    framework: str
    parameters: dict[str, Any]
    outputs: dict[str, Any]
    metrics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_id: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize for API response."""
        return {
            "framework": self.framework,
            "parameters": self.parameters,
            "outputs": self.outputs,
            "metrics": self.metrics,
            "metadata": self.metadata,
            "execution_id": self.execution_id,
            "timestamp": self.timestamp,
        }


# ════════════════════════════════════════════════════════════════════════════════
# JSON Schema Conventions
# ════════════════════════════════════════════════════════════════════════════════

# These are the extended JSON Schema properties we support for UI generation.
# They are not part of standard JSON Schema but are recognized by our ParameterPanel.

JSON_SCHEMA_UI_EXTENSIONS = """
UI Extension Properties (add to any property in parameters_schema):

For numbers/integers:
    "x-ui-widget": "slider" | "input" | "range"
    "x-ui-step": 0.01              # Step increment for slider
    "x-ui-unit": "%"               # Unit label (%, $, years, etc.)
    "x-ui-format": ".2f"           # Display format

For strings:
    "x-ui-widget": "select" | "input" | "textarea" | "color"
    "x-ui-placeholder": "Enter value..."

For arrays:
    "x-ui-widget": "multiselect" | "chips" | "list"
    "x-ui-allow-custom": true      # Allow custom values

For booleans:
    "x-ui-widget": "switch" | "checkbox"

For all types:
    "x-ui-group": "advanced"       # Parameter group key
    "x-ui-order": 10               # Display order within group
    "x-ui-condition": {"field": "mode", "equals": "advanced"}  # Conditional visibility
    "x-ui-help": "Detailed help text..."
    "x-ui-readonly": true          # Display only, not editable

Example:
    "labor_elasticity": {
        "type": "number",
        "title": "Labor Elasticity",
        "description": "Labor supply elasticity parameter",
        "minimum": 0,
        "maximum": 1,
        "default": 0.7,
        "x-ui-widget": "slider",
        "x-ui-step": 0.05,
        "x-ui-group": "model_parameters",
        "x-ui-order": 1
    }
"""
