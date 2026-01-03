# ════════════════════════════════════════════════════════════════════════════════
# KRL Ecosystem - Canonical pyproject.toml Templates
# ════════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Author: KRL Platform Engineering
# Last Updated: 2025-12-30
#
# This document defines the authoritative pyproject.toml templates for all
# packages in the KRL ecosystem. These templates enforce:
#   1. Correct dependency boundaries (no circular imports)
#   2. Version constraints aligned across ecosystem
#   3. Explicit forbidden dependencies
#   4. Proper tiered optional dependencies
# ════════════════════════════════════════════════════════════════════════════════

"""
Canonical Package Templates for KRL Ecosystem.

This module provides programmatic access to the canonical package specifications
for all packages in the KRL ecosystem. Use these templates to:
    1. Generate new pyproject.toml files
    2. Validate existing pyproject.toml files
    3. Check for dependency violations
    4. Ensure version alignment

Package Topology (from bottom to top):
    
    krl-types (0.2.0)          - Type definitions, Pydantic models
         ↓
    krl-open-core (0.2.0)      - Logging, config, caching, base utilities
         ↓
    ┌────┴────────────────┬─────────────────────┬────────────────────┐
    │                     │                     │                    │
    krl-data-connectors   krl-toolkits-*       krl-model-zoo        │
    (1.0.0)               (1.0.0 / 0.2.0)      (0.1.0)              │
    │                     │                     │                    │
    └────────────────────┴─────────────────────┴────────────────────┘
                                    │
                                    ↓
                          krl-frameworks (0.1.0)
                                    │
                                    ↓
                          krl-premium-backend (0.1.0)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "PackageTemplate",
    "ECOSYSTEM_PACKAGES",
    "get_template",
    "validate_pyproject",
    "check_forbidden_dependencies",
]


# ════════════════════════════════════════════════════════════════════════════════
# ECOSYSTEM VERSION CONSTANTS
# These are the authoritative version constraints for the ecosystem
# ════════════════════════════════════════════════════════════════════════════════

PYTHON_VERSION = ">=3.11"

# Core versions - these must be aligned
VERSIONS = {
    "krl-types": "0.2.0",
    "krl-open-core": "0.2.0",
    "krl-data-connectors": "1.0.0",
    "krl-causal-policy-toolkit": "1.0.0",
    "krl-geospatial-tools": "0.2.0",
    "krl-network-analysis": "0.2.0",
    "krl-model-zoo": "2.0.1",  # Unified model zoo with tiered access
    "krl-frameworks": "0.1.0",
    "krl-premium-backend": "0.1.0",
}

# Shared dependency versions - pinned for reproducibility
SHARED_DEPS = {
    "numpy": ">=1.26.0",
    "pandas": ">=2.1.0",
    "pydantic": ">=2.5.0",
    "requests": ">=2.28.0",
    "networkx": ">=3.2.0",
}


@dataclass
class PackageTemplate:
    """
    Canonical package template specification.
    
    Attributes:
        name: PyPI package name
        version: Current version
        description: Package description
        dependencies: Required dependencies
        optional_dependencies: Optional dependency groups
        forbidden_dependencies: Packages that MUST NOT be imported
        python_requires: Python version constraint
        license: License identifier
        dev_dependencies: Development dependencies
        test_dependencies: Test dependencies
    """
    name: str
    version: str
    description: str
    dependencies: list[str]
    optional_dependencies: dict[str, list[str]] = field(default_factory=dict)
    forbidden_dependencies: list[str] = field(default_factory=list)
    python_requires: str = PYTHON_VERSION
    license: str = "Apache-2.0"
    dev_dependencies: list[str] = field(default_factory=list)
    test_dependencies: list[str] = field(default_factory=list)
    
    def to_pyproject(self) -> str:
        """Generate pyproject.toml content."""
        lines = [
            "[build-system]",
            'requires = ["setuptools>=68.0", "wheel"]',
            'build-backend = "setuptools.build_meta"',
            "",
            "[project]",
            f'name = "{self.name}"',
            f'version = "{self.version}"',
            f'description = "{self.description}"',
            f'requires-python = "{self.python_requires}"',
            f'license = {{ text = "{self.license}" }}',
            "",
            "dependencies = [",
        ]
        
        for dep in self.dependencies:
            lines.append(f'    "{dep}",')
        lines.append("]")
        
        if self.optional_dependencies:
            lines.append("")
            lines.append("[project.optional-dependencies]")
            for group, deps in self.optional_dependencies.items():
                lines.append(f"{group} = [")
                for dep in deps:
                    lines.append(f'    "{dep}",')
                lines.append("]")
        
        if self.forbidden_dependencies:
            lines.append("")
            lines.append("# ════════════════════════════════════════════════════════════════════")
            lines.append("# FORBIDDEN DEPENDENCIES - These packages MUST NOT be imported")
            lines.append("# Violation of these constraints breaks the package topology")
            lines.append("# ════════════════════════════════════════════════════════════════════")
            for forbidden in self.forbidden_dependencies:
                lines.append(f"# FORBIDDEN: {forbidden}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "optional_dependencies": self.optional_dependencies,
            "forbidden_dependencies": self.forbidden_dependencies,
            "python_requires": self.python_requires,
            "license": self.license,
        }


# ════════════════════════════════════════════════════════════════════════════════
# CANONICAL PACKAGE TEMPLATES
# ════════════════════════════════════════════════════════════════════════════════

ECOSYSTEM_PACKAGES: dict[str, PackageTemplate] = {}

# ─────────────────────────────────────────────────────────────────────────────────
# krl-types: Type definitions (no dependencies on other KRL packages)
# ─────────────────────────────────────────────────────────────────────────────────

ECOSYSTEM_PACKAGES["krl-types"] = PackageTemplate(
    name="krl-types",
    version=VERSIONS["krl-types"],
    description="Type definitions and Pydantic models for the KRL ecosystem",
    dependencies=[
        "pydantic>=2.5.0",
        "typing-extensions>=4.8.0",
    ],
    forbidden_dependencies=[
        "krl-open-core",
        "krl-data-connectors",
        "krl-causal-policy-toolkit",
        "krl-geospatial-tools",
        "krl-network-analysis",
        "krl-model-zoo",
        "krl-frameworks",
        # Also forbidden: heavy data libraries
        "pandas",  # Types should be abstract
        "numpy",   # Types should be abstract
    ],
    license="MIT",
)

# ─────────────────────────────────────────────────────────────────────────────────
# krl-open-core: Core utilities (depends only on krl-types)
# ─────────────────────────────────────────────────────────────────────────────────

ECOSYSTEM_PACKAGES["krl-open-core"] = PackageTemplate(
    name="krl-open-core",
    version=VERSIONS["krl-open-core"],
    description="Core utilities for the KRL ecosystem: logging, config, caching",
    dependencies=[
        "krl-types~=0.2.0",
        "pyyaml>=6.0",
        "python-json-logger>=2.0.0",
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
    ],
    optional_dependencies={
        "redis": ["redis>=4.5.0"],
    },
    forbidden_dependencies=[
        "krl-data-connectors",
        "krl-causal-policy-toolkit",
        "krl-geospatial-tools",
        "krl-network-analysis",
        "krl-model-zoo",
        "krl-frameworks",
        # Forbidden: domain-specific libraries
        "dowhy",
        "geopandas",
        "pymc",
    ],
    license="MIT",
)

# ─────────────────────────────────────────────────────────────────────────────────
# krl-data-connectors: Data connectors (no framework dependency)
# ─────────────────────────────────────────────────────────────────────────────────

ECOSYSTEM_PACKAGES["krl-data-connectors"] = PackageTemplate(
    name="krl-data-connectors",
    version=VERSIONS["krl-data-connectors"],
    description="Production-ready data connectors for 68+ government and research data sources",
    dependencies=[
        "krl-types~=0.2.0",
        "requests>=2.28.0",
        "pandas>=2.1.0",
        "numpy>=1.26.0",
    ],
    optional_dependencies={
        "enterprise": [
            "airbyte-api>=0.53.0",
            "httpx>=0.25.0",
        ],
        "ai": [
            "httpx>=0.25.0",
            "supermemory>=0.1.0",
        ],
    },
    forbidden_dependencies=[
        # CRITICAL: Connectors must NOT depend on frameworks
        "krl-frameworks",
        # Connectors must NOT depend on toolkits
        "krl-causal-policy-toolkit",
        "krl-geospatial-tools",
        "krl-network-analysis",
        # Connectors must NOT depend on model zoo
        "krl-model-zoo",
        "krl-model-zoo-pro",
        # Domain-specific forbidden
        "dowhy",      # Causal inference library
        "pymc",       # Probabilistic programming
        "geopandas",  # Geospatial library
    ],
    license="Apache-2.0",
)

# ─────────────────────────────────────────────────────────────────────────────────
# krl-causal-policy-toolkit: Causal inference methods
# ─────────────────────────────────────────────────────────────────────────────────

ECOSYSTEM_PACKAGES["krl-causal-policy-toolkit"] = PackageTemplate(
    name="krl-causal-policy-toolkit",
    version=VERSIONS["krl-causal-policy-toolkit"],
    description="Comprehensive Python library for policy evaluation and causal inference",
    dependencies=[
        "numpy>=1.26.0",
        "pandas>=2.1.0",
        "scipy>=1.11.0",
        "scikit-learn>=1.3.0",
        "dowhy>=0.11",
        "pymc>=5.10.0",
        "arviz>=0.17.0",
        "arch>=6.2.0",
        "statsmodels>=0.14.0",
    ],
    optional_dependencies={
        "reporting": ["jinja2>=3.1.0"],
    },
    forbidden_dependencies=[
        # CRITICAL: Toolkits must NOT depend on frameworks
        "krl-frameworks",
        # Toolkits must NOT depend on connectors (data agnostic)
        "krl-data-connectors",
        # No cross-toolkit dependencies
        "krl-geospatial-tools",
        "krl-network-analysis",
        # No model zoo dependency
        "krl-model-zoo",
    ],
    license="MIT",
)

# ─────────────────────────────────────────────────────────────────────────────────
# krl-geospatial-tools: Geospatial analysis
# ─────────────────────────────────────────────────────────────────────────────────

ECOSYSTEM_PACKAGES["krl-geospatial-tools"] = PackageTemplate(
    name="krl-geospatial-tools",
    version=VERSIONS["krl-geospatial-tools"],
    description="Geospatial analysis and mapping tools for socioeconomic research",
    dependencies=[
        "geopandas>=0.13.0",
        "shapely>=2.0.0",
        "folium>=0.14.0",
        "plotly>=5.17.0",
        "pandas>=2.1.0",
        "numpy>=1.26.0",
    ],
    optional_dependencies={
        "spatial": [
            "pysal>=23.0",
            "rtree>=1.0.0",
            "scikit-learn>=1.2.0",
        ],
        "geocoding": [
            "geopy>=2.3.0",
        ],
    },
    forbidden_dependencies=[
        # CRITICAL: Toolkits must NOT depend on frameworks
        "krl-frameworks",
        # Toolkits must NOT depend on connectors
        "krl-data-connectors",
        # No cross-toolkit dependencies
        "krl-causal-policy-toolkit",
        "krl-network-analysis",
        # Causal libraries forbidden
        "dowhy",
        "pymc",
    ],
    license="Apache-2.0",
)

# ─────────────────────────────────────────────────────────────────────────────────
# krl-network-analysis: Network/graph analysis
# ─────────────────────────────────────────────────────────────────────────────────

ECOSYSTEM_PACKAGES["krl-network-analysis"] = PackageTemplate(
    name="krl-network-analysis",
    version=VERSIONS["krl-network-analysis"],
    description="Network analysis toolkit for socioeconomic relationship modeling",
    dependencies=[
        "networkx>=3.2.0",
        "pandas>=2.1.0",
        "numpy>=1.26.0",
        "scipy>=1.11.0",
    ],
    optional_dependencies={
        "visualization": [
            "matplotlib>=3.8.0",
            "plotly>=5.17.0",
        ],
        "community": [
            "python-louvain>=0.16",
            "leidenalg>=0.10.0",
        ],
    },
    forbidden_dependencies=[
        # CRITICAL: Toolkits must NOT depend on frameworks
        "krl-frameworks",
        # Toolkits must NOT depend on connectors
        "krl-data-connectors",
        # No cross-toolkit dependencies
        "krl-causal-policy-toolkit",
        "krl-geospatial-tools",
        # Geo libraries forbidden
        "geopandas",
        "shapely",
    ],
    license="Apache-2.0",
)

# ─────────────────────────────────────────────────────────────────────────────────
# krl-model-zoo: Unified ML/DL model zoo with tiered access
# Derived from: /Private IP/Model Catalog/
#   Open/        → Community tier (FREE) - 75 models
#   Class A/     → Professional tier - 141 models  
#   Proprietary/ → Enterprise tier - 2 models
# TOTAL: 218 models
# ─────────────────────────────────────────────────────────────────────────────────

ECOSYSTEM_PACKAGES["krl-model-zoo"] = PackageTemplate(
    name="krl-model-zoo",
    version=VERSIONS["krl-model-zoo"],
    description="Unified model zoo: 218 models across anomaly detection, bayesian, causal inference, clustering, dimensionality reduction, econometrics, ensemble, GAM, GLM, health, hybrid, ML, network, neural networks, optimization, regional, regression, signals, state space, and volatility. Community tier (75 models) FREE, Professional tier (141 models), Enterprise tier (2 models).",
    dependencies=[
        "numpy>=1.26.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "transformers>=4.30.0",
        "pillow>=9.0.0",
        "gensim>=4.3.0",
    ],
    optional_dependencies={
        # ═══════════════════════════════════════════════════════════════════
        # COMMUNITY TIER (FREE) - 75 models from Open/
        # ═══════════════════════════════════════════════════════════════════
        "vision": [
            "ultralytics>=8.0.0",
        ],
        "audio": [
            "speechbrain>=0.5.0",
        ],
        "tabular": [
            "pytorch-tabnet>=4.0",
        ],
        # ═══════════════════════════════════════════════════════════════════
        # PROFESSIONAL TIER - 141 models from Class A/
        # ═══════════════════════════════════════════════════════════════════
        "pro": [
            "statsmodels>=0.14.0",
            "scikit-learn>=1.3.0",
            "scipy>=1.11.0",
            "arch>=6.2.0",
            "pymc>=5.10.0",
            "arviz>=0.17.0",
        ],
        "econometric": [
            "statsmodels>=0.14.0",
            "arch>=6.2.0",
        ],
        "bayesian": [
            "pymc>=5.10.0",
            "arviz>=0.17.0",
        ],
        "clustering": [
            "scikit-learn>=1.3.0",
            "hdbscan>=0.8.33",
        ],
        "causal": [
            "econml>=0.14.0",
            "dowhy>=0.10.0",
            "causalml>=0.14.0",
        ],
        "network": [
            "networkx>=3.2.0",
            "node2vec>=0.4.6",
            "stellargraph>=1.2.1",
            "pysal>=23.7.0",
        ],
        "regression": [
            "scikit-learn>=1.3.0",
            "xgboost>=2.0.0",
        ],
        "state_space": [
            "statsmodels>=0.14.0",
            "filterpy>=1.4.5",
        ],
        "neural": [
            "pytorch-lightning>=2.0.0",
            "pytorch-forecasting>=1.0.0",
        ],
        # ═══════════════════════════════════════════════════════════════════
        # ENTERPRISE TIER - 2 advanced proprietary models
        # ═══════════════════════════════════════════════════════════════════
        "enterprise": [
            "xgboost>=2.0.0",
            "lightgbm>=4.0.0",
            "catboost>=1.2.0",
            "stable-baselines3>=2.0.0",  # For RL models
        ],
        # ═══════════════════════════════════════════════════════════════════
        # ALL TIERS COMBINED
        # ═══════════════════════════════════════════════════════════════════
        "all": [
            "krl-model-zoo[vision,audio,tabular,pro,econometric,bayesian,clustering,causal,network,regression,state_space,neural,enterprise]",
        ],
    },
    forbidden_dependencies=[
        # CRITICAL: Model zoo must NOT depend on frameworks
        "krl-frameworks",
        # Model zoo must NOT depend on connectors (data-agnostic)
        "krl-data-connectors",
        # No toolkit dependencies (methods are separate from models)
        "krl-causal-policy-toolkit",
        "krl-geospatial-tools",
        "krl-network-analysis",
    ],
    license="Apache-2.0",
)

# ─────────────────────────────────────────────────────────────────────────────────
# krl-frameworks: Framework orchestration (depends on all lower layers)
# ─────────────────────────────────────────────────────────────────────────────────

ECOSYSTEM_PACKAGES["krl-frameworks"] = PackageTemplate(
    name="krl-frameworks",
    version=VERSIONS["krl-frameworks"],
    description="Enterprise-grade meta-framework orchestration for socioeconomic analysis",
    dependencies=[
        "numpy>=1.26.0",
        "pandas>=2.1.0",
        "pydantic>=2.5.0",
        "networkx>=3.2.0",
        "krl-open-core>=0.2.0",
        "krl-types~=0.2.0",
    ],
    optional_dependencies={
        # All lower-layer packages are OPTIONAL dependencies
        # This enforces the "declare requirements, don't assume presence" principle
        "causal": [
            "krl-causal-policy-toolkit>=1.0.0",
        ],
        "geospatial": [
            "krl-geospatial-tools>=0.2.0",
        ],
        "network": [
            "krl-network-analysis>=0.2.0",
        ],
        "connectors": [
            "krl-data-connectors>=1.0.0",
        ],
        "models": [
            "krl-model-zoo>=0.1.0",
        ],
        "all": [
            "krl-frameworks[causal,geospatial,network,connectors,models]",
        ],
    },
    forbidden_dependencies=[
        # Frameworks must NOT directly import toolkit implementations
        # They declare requirements, resolved at runtime
        # No forbidden packages here - frameworks sit at the top
    ],
    license="Apache-2.0",
)

# ─────────────────────────────────────────────────────────────────────────────────
# krl-premium-backend: API layer (highest in stack)
# ─────────────────────────────────────────────────────────────────────────────────

ECOSYSTEM_PACKAGES["krl-premium-backend"] = PackageTemplate(
    name="krl-premium-backend",
    version=VERSIONS["krl-premium-backend"],
    description="Premium API backend for KRL platform with authentication and tier management",
    dependencies=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        "redis>=5.0.0",
        "celery>=5.3.0",
        "krl-frameworks>=0.1.0",
        "krl-open-core>=0.2.0",
        "krl-types~=0.2.0",
    ],
    optional_dependencies={
        "postgres": [
            "asyncpg>=0.29.0",
            "psycopg2-binary>=2.9.0",
        ],
        "auth": [
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.0",
        ],
    },
    forbidden_dependencies=[
        # Backend must NOT directly import toolkit implementations
        # It uses frameworks which handle binding resolution
    ],
    license="Apache-2.0",
)


# ════════════════════════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════════

def get_template(package_name: str) -> PackageTemplate | None:
    """
    Get the canonical template for a package.
    
    Args:
        package_name: PyPI package name.
    
    Returns:
        PackageTemplate if package is in ecosystem, None otherwise.
    """
    return ECOSYSTEM_PACKAGES.get(package_name)


def check_forbidden_dependencies(
    package_name: str,
    actual_dependencies: list[str],
) -> list[str]:
    """
    Check if any forbidden dependencies are present.
    
    Args:
        package_name: Package being checked.
        actual_dependencies: List of actual dependencies.
    
    Returns:
        List of forbidden dependencies that were found.
    """
    template = get_template(package_name)
    if not template:
        return []
    
    violations = []
    for dep in actual_dependencies:
        # Extract package name from version constraint
        pkg = dep.split(">=")[0].split("<=")[0].split("~=")[0].split("==")[0].strip()
        if pkg in template.forbidden_dependencies:
            violations.append(pkg)
    
    return violations


def validate_pyproject(
    package_name: str,
    pyproject_dict: dict[str, Any],
) -> list[str]:
    """
    Validate a pyproject.toml against the canonical template.
    
    Args:
        package_name: Package name.
        pyproject_dict: Parsed pyproject.toml as dictionary.
    
    Returns:
        List of validation errors (empty if valid).
    """
    template = get_template(package_name)
    if not template:
        return [f"Unknown package: {package_name}"]
    
    errors = []
    project = pyproject_dict.get("project", {})
    
    # Check version
    if project.get("version") != template.version:
        errors.append(
            f"Version mismatch: expected {template.version}, "
            f"got {project.get('version')}"
        )
    
    # Check Python version
    if project.get("requires-python") != template.python_requires:
        errors.append(
            f"Python version mismatch: expected {template.python_requires}, "
            f"got {project.get('requires-python')}"
        )
    
    # Check forbidden dependencies
    dependencies = project.get("dependencies", [])
    violations = check_forbidden_dependencies(package_name, dependencies)
    for v in violations:
        errors.append(f"Forbidden dependency: {v}")
    
    return errors


# ════════════════════════════════════════════════════════════════════════════════
# DEPENDENCY GRAPH FOR DOCUMENTATION
# ════════════════════════════════════════════════════════════════════════════════

DEPENDENCY_GRAPH = """
KRL Ecosystem Dependency Graph (Canonical Topology)
═══════════════════════════════════════════════════

                    ┌─────────────────────┐
                    │  krl-premium-backend │ (API Layer)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    krl-frameworks    │ (Orchestration Layer)
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│krl-data-connectors│ │ krl-toolkits-* │ │  krl-model-zoo  │
│                 │ │ (causal, geo,  │ │                 │
│ FRED, Census,   │ │  network)      │ │  ML/DL models   │
│ BLS, WHO, etc.  │ │                │ │                 │
└────────┬────────┘ └───────┬────────┘ └────────┬────────┘
         │                  │                   │
         └──────────────────┼───────────────────┘
                            │
                 ┌──────────▼──────────┐
                 │    krl-open-core     │ (Core Utilities)
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │      krl-types       │ (Type Definitions)
                 └─────────────────────┘

DEPENDENCY RULES:
─────────────────
1. Arrows point DOWN = "depends on"
2. Packages may ONLY depend on packages BELOW them
3. Horizontal packages may NOT depend on each other
4. krl-frameworks declares but does not assume dependencies
5. Connectors, toolkits, and model-zoo are independent

FORBIDDEN PATTERNS:
───────────────────
✗ krl-data-connectors → krl-frameworks (connector depends on framework)
✗ krl-causal-policy-toolkit → krl-geospatial-tools (cross-toolkit)
✗ krl-open-core → krl-data-connectors (core depends on connector)
✗ krl-types → anything (types are the foundation)
"""
