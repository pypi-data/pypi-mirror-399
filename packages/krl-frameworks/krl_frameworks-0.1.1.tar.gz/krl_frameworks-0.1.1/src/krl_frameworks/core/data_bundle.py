# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Data Bundle
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
DataBundle for explicit data injection into frameworks.

This module provides the DataBundle class, which encapsulates all data
required by a framework for execution. DataBundle ensures explicit
data provisioning, domain validation, and reproducibility compliance.

Data Domains (aligned with REMSOM's 8 domains):
    - labor: Employment, wages, labor force participation
    - economic: GDP, income, sectoral outputs
    - housing: Housing costs, availability, quality
    - education: Attainment, enrollment, quality metrics
    - health: Mortality, morbidity, access to care
    - financial: Credit access, savings, debt
    - demographic: Age, race, gender, household structure
    - transportation: Commute times, transit access, mobility
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Iterator

import numpy as np

from krl_frameworks.core.exceptions import DataBundleValidationError

if TYPE_CHECKING:
    import pandas as pd
    from numpy.typing import NDArray


# ════════════════════════════════════════════════════════════════════════════════
# Data Domain Enum
# ════════════════════════════════════════════════════════════════════════════════


class DataDomain(str, Enum):
    """
    Canonical data domains for socioeconomic framework analysis.
    
    These domains align with REMSOM's 8-domain architecture and provide
    a standardized vocabulary for data requirements across frameworks.
    """
    
    # Core REMSOM domains
    LABOR = "labor"
    ECONOMIC = "economic"
    HOUSING = "housing"
    EDUCATION = "education"
    HEALTH = "health"
    FINANCIAL = "financial"
    DEMOGRAPHIC = "demographic"
    TRANSPORTATION = "transportation"
    
    # Extended domains for additional frameworks
    ENVIRONMENT = "environment"
    GOVERNANCE = "governance"
    INFRASTRUCTURE = "infrastructure"
    SOCIAL = "social"
    CULTURAL = "cultural"
    MEDIA = "media"
    CLIMATE = "climate"
    ENERGY = "energy"
    SAM = "sam"  # Social Accounting Matrix (CGE models)
    SECTORS = "sectors"  # Sector-specific economic data
    SPATIAL = "spatial"  # Geographic/spatial data
    CAUSAL = "causal"  # Causal inference data
    
    @classmethod
    def core_domains(cls) -> list[DataDomain]:
        """Return the 8 core REMSOM domains."""
        return [
            cls.LABOR,
            cls.ECONOMIC,
            cls.HOUSING,
            cls.EDUCATION,
            cls.HEALTH,
            cls.FINANCIAL,
            cls.DEMOGRAPHIC,
            cls.TRANSPORTATION,
        ]
    
    @classmethod
    def from_string(cls, value: str) -> DataDomain:
        """Convert a string to DataDomain, case-insensitive."""
        return cls(value.lower())


# ════════════════════════════════════════════════════════════════════════════════
# Domain Data Container
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class DomainData:
    """
    Container for a single data domain's content.

    Attributes:
        domain: The data domain this belongs to.
        data: The actual data (DataFrame or array).
        source: Data source identifier (e.g., "ACS_2023", "FRED").
        version: Version of the data extraction.
        timestamp: When the data was extracted/loaded.
        schema: Optional schema definition for validation.
        metadata: Additional domain-specific metadata.
        quality_scores: Quality scores for this data source (6 dimensions).
        source_quality_rank: Rank of this source (0=primary, 1+=fallback).
    """

    domain: DataDomain
    data: pd.DataFrame | NDArray[Any]
    source: str = ""
    version: str = "1.0.0"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    schema: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # NEW: Quality awareness fields
    quality_scores: dict[str, float] = field(default_factory=dict)
    source_quality_rank: int = 0  # 0=primary, 1+=fallback
    
    @property
    def n_records(self) -> int:
        """Number of records in the data."""
        if hasattr(self.data, "__len__"):
            return len(self.data)
        return 0
    
    @property
    def columns(self) -> list[str]:
        """Column names if data is a DataFrame."""
        if hasattr(self.data, "columns"):
            return list(self.data.columns)
        return []
    
    def content_hash(self) -> str:
        """Compute a hash of the data content for versioning."""
        if hasattr(self.data, "to_json"):
            content = self.data.to_json()
        else:
            content = json.dumps(self.data.tolist() if hasattr(self.data, "tolist") else str(self.data))
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def validate_schema(self) -> bool:
        """Validate data against schema if provided."""
        if self.schema is None:
            return True
        
        if hasattr(self.data, "columns"):
            required_cols = self.schema.get("required_columns", [])
            return all(col in self.data.columns for col in required_cols)
        
        return True
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "domain": self.domain.value,
            "source": self.source,
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "n_records": self.n_records,
            "columns": self.columns,
            "content_hash": self.content_hash(),
            "metadata": self.metadata,
            "quality_scores": self.quality_scores,
            "source_quality_rank": self.source_quality_rank,
        }


# ════════════════════════════════════════════════════════════════════════════════
# Data Bundle
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class DataBundle:
    """
    Encapsulates all data required by a framework for execution.
    
    DataBundle provides:
    - Explicit data provisioning (no hidden dependencies)
    - Domain validation against framework requirements
    - Reproducibility through content hashing
    - Audit trail for data lineage
    
    The bundle operates as a read-only container after creation,
    ensuring data integrity throughout framework execution.
    
    Attributes:
        domains: Dictionary mapping domain names to DomainData.
        bundle_id: Unique identifier for this bundle.
        created_at: Bundle creation timestamp.
        description: Human-readable description.
        metadata: Additional bundle-level metadata.
    
    Example:
        >>> bundle = DataBundle.from_dataframes({
        ...     "labor": labor_df,
        ...     "health": health_df,
        ...     "education": edu_df,
        ... })
        >>> bundle.validate_requirements(["labor", "health"])
        True
        >>> labor_data = bundle.get("labor")
    """
    
    domains: dict[str, DomainData] = field(default_factory=dict)
    bundle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Properties
    # ═══════════════════════════════════════════════════════════════════════════
    
    @property
    def available_domains(self) -> list[str]:
        """List of domain names available in this bundle."""
        return list(self.domains.keys())
    
    @property
    def n_domains(self) -> int:
        """Number of domains in the bundle."""
        return len(self.domains)
    
    @property
    def total_records(self) -> int:
        """Total number of records across all domains."""
        return sum(d.n_records for d in self.domains.values())
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Factory Methods
    # ═══════════════════════════════════════════════════════════════════════════
    
    @classmethod
    def from_dataframes(
        cls,
        dataframes: dict[str, pd.DataFrame],
        sources: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> DataBundle:
        """
        Create a DataBundle from a dictionary of DataFrames.
        
        Args:
            dataframes: Mapping of domain names to DataFrames.
            sources: Optional mapping of domain names to source identifiers.
            **kwargs: Additional bundle metadata.
        
        Returns:
            DataBundle instance.
        
        Example:
            >>> bundle = DataBundle.from_dataframes({
            ...     "labor": bls_data,
            ...     "housing": hud_data,
            ... }, sources={"labor": "BLS_QCEW", "housing": "HUD_FMR"})
        """
        sources = sources or {}
        domains: dict[str, DomainData] = {}
        
        for name, df in dataframes.items():
            try:
                domain_enum = DataDomain.from_string(name)
            except ValueError:
                # Allow custom domain names not in enum
                domain_enum = DataDomain.ECONOMIC  # Fallback
            
            domains[name] = DomainData(
                domain=domain_enum,
                data=df,
                source=sources.get(name, ""),
            )
        
        return cls(domains=domains, **kwargs)
    
    @classmethod
    def from_arrays(
        cls,
        arrays: dict[str, NDArray[Any]],
        **kwargs: Any,
    ) -> DataBundle:
        """
        Create a DataBundle from a dictionary of NumPy arrays.
        
        Args:
            arrays: Mapping of domain names to arrays.
            **kwargs: Additional bundle metadata.
        
        Returns:
            DataBundle instance.
        """
        domains: dict[str, DomainData] = {}
        
        for name, arr in arrays.items():
            try:
                domain_enum = DataDomain.from_string(name)
            except ValueError:
                domain_enum = DataDomain.ECONOMIC
            
            domains[name] = DomainData(
                domain=domain_enum,
                data=arr,
            )
        
        return cls(domains=domains, **kwargs)
    
    @classmethod
    def empty(cls, **kwargs: Any) -> DataBundle:
        """Create an empty DataBundle."""
        return cls(domains={}, **kwargs)
    
    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        sources: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> DataBundle:
        """
        Create a DataBundle from a dictionary (API request format).
        
        This is the primary factory method for creating DataBundles from
        HTTP API requests. It handles various input formats:
        
        1. List of records → converts to DataFrame
        2. Dict with 'data' key → extracts data array/list
        3. Dict with 'dataframe' key → uses as DataFrame input
        4. Dict with 'records' key → list of record dicts
        5. Empty/null values → skipped
        
        Args:
            data: Dictionary with domain names as keys and data as values.
                  Values can be:
                  - List[Dict]: Records that will become DataFrame rows
                  - Dict with 'data': Array or list of data
                  - Dict with 'dataframe': Pre-formatted DataFrame dict
                  - Dict with 'records': List of record dictionaries
                  - None/empty: Domain will be skipped
            sources: Optional mapping of domain names to source identifiers.
            **kwargs: Additional bundle metadata (description, metadata, etc.)
        
        Returns:
            DataBundle instance with populated domains.
        
        Example:
            >>> # From API request
            >>> bundle = DataBundle.from_dict({
            ...     "labor": [
            ...         {"geoid": "06037", "employment": 4500000, "unemployment_rate": 0.045},
            ...         {"geoid": "06001", "employment": 800000, "unemployment_rate": 0.038},
            ...     ],
            ...     "health": {
            ...         "records": [{"geoid": "06037", "life_expectancy": 81.2}],
            ...         "source": "CDC_WONDER"
            ...     }
            ... })
            
            >>> # Empty dict returns empty bundle
            >>> bundle = DataBundle.from_dict({})
            >>> bundle.n_domains
            0
        
        Notes:
            - Domain names are normalized to lowercase
            - Invalid domain names are accepted but logged
            - Missing or null values in records are preserved as NaN
            - Source information can be embedded in data dicts or via sources param
        """
        import pandas as pd
        
        if not data:
            return cls.empty(**kwargs)
        
        sources = sources or {}
        dataframes: dict[str, pd.DataFrame] = {}
        inferred_sources: dict[str, str] = {}
        domain_metadata: dict[str, dict[str, Any]] = {}
        
        for domain_name, domain_value in data.items():
            # Skip internal metadata keys (e.g., "_metadata")
            if domain_name.startswith("_"):
                continue
            
            if domain_value is None:
                continue
            
            # Normalize domain name
            domain_key = domain_name.lower().strip()
            
            if not domain_key:
                continue
            
            # Handle different input formats
            df: pd.DataFrame | None = None
            source: str = sources.get(domain_key, "")
            meta: dict[str, Any] = {}
            
            if isinstance(domain_value, list):
                # Format 1: List of records → DataFrame
                if domain_value:
                    df = pd.DataFrame(domain_value)
                    
            elif isinstance(domain_value, dict):
                # Check for structured formats
                if "dataframe" in domain_value:
                    # Format 3: Dict with 'dataframe' key
                    df_data = domain_value["dataframe"]
                    if isinstance(df_data, list):
                        df = pd.DataFrame(df_data)
                    elif isinstance(df_data, dict):
                        df = pd.DataFrame.from_dict(df_data)
                        
                elif "records" in domain_value:
                    # Format 4: Dict with 'records' key
                    records = domain_value["records"]
                    if records:
                        df = pd.DataFrame(records)
                        
                elif "data" in domain_value:
                    # Format 2: Dict with 'data' key
                    raw_data = domain_value["data"]
                    if isinstance(raw_data, list):
                        if raw_data and isinstance(raw_data[0], dict):
                            df = pd.DataFrame(raw_data)
                        else:
                            # Single-column data
                            df = pd.DataFrame({"value": raw_data})
                    elif isinstance(raw_data, dict):
                        df = pd.DataFrame.from_dict(raw_data)
                        
                else:
                    # Assume it's a dict of column: values
                    # Only if it looks like columnar data
                    first_val = next(iter(domain_value.values()), None)
                    if isinstance(first_val, (list, tuple)):
                        df = pd.DataFrame(domain_value)
                    elif all(isinstance(v, (int, float, str, bool, type(None))) 
                             for v in domain_value.values()):
                        # Single row of data
                        df = pd.DataFrame([domain_value])
                
                # Extract embedded source if present
                if "source" in domain_value and not source:
                    source = str(domain_value["source"])
                
                # Extract metadata if present
                if "metadata" in domain_value:
                    meta = domain_value["metadata"]
                    
            elif hasattr(domain_value, "to_frame"):
                # Already a Series
                df = domain_value.to_frame()
                
            elif hasattr(domain_value, "columns"):
                # Already a DataFrame-like object
                df = pd.DataFrame(domain_value)
            
            # Only add if we got valid data
            if df is not None and not df.empty:
                dataframes[domain_key] = df
                if source:
                    inferred_sources[domain_key] = source
                if meta:
                    domain_metadata[domain_key] = meta
        
        if not dataframes:
            return cls.empty(**kwargs)
        
        # Build bundle with all sources
        all_sources = {**inferred_sources, **sources}
        
        # Create domains
        domains: dict[str, DomainData] = {}
        
        for name, df in dataframes.items():
            try:
                domain_enum = DataDomain.from_string(name)
            except ValueError:
                # Allow custom domain names not in enum
                domain_enum = DataDomain.ECONOMIC  # Fallback
            
            domains[name] = DomainData(
                domain=domain_enum,
                data=df,
                source=all_sources.get(name, ""),
                metadata=domain_metadata.get(name, {}),
            )
        
        return cls(domains=domains, **kwargs)
    
    @classmethod
    def from_connector_results(
        cls,
        results: dict[str, dict[str, Any]],
        **kwargs: Any,
    ) -> DataBundle:
        """
        Create a DataBundle from data connector fetch results.
        
        This factory method is designed for integration with the
        FrameworkDataConnector service, which fetches data from
        external APIs (Census, BLS, FRED, etc.).
        
        Args:
            results: Dictionary mapping domain names to connector results.
                     Each result should have:
                     - 'dataframe' or 'data': The fetched data
                     - 'source': Connector/API identifier
                     - 'timestamp': When data was fetched
                     - 'metadata': Additional connector metadata
            **kwargs: Additional bundle metadata.
        
        Returns:
            DataBundle instance with connector data.
        
        Example:
            >>> results = await connector.fetch_all_domains(["labor", "health"])
            >>> bundle = DataBundle.from_connector_results(results)
        """
        import pandas as pd
        
        if not results:
            return cls.empty(**kwargs)
        
        domains: dict[str, DomainData] = {}
        
        for domain_name, result in results.items():
            # Skip internal metadata keys (e.g., "_metadata")
            if domain_name.startswith("_"):
                continue
            
            if not result:
                continue
            
            # Skip non-dict results (malformed data)
            if not isinstance(result, dict):
                continue
            
            # Extract data
            df: pd.DataFrame | None = None
            
            if "dataframe" in result:
                df_data = result["dataframe"]
                if isinstance(df_data, pd.DataFrame):
                    df = df_data
                elif isinstance(df_data, list):
                    df = pd.DataFrame(df_data)
                elif isinstance(df_data, dict):
                    df = pd.DataFrame.from_dict(df_data)
                    
            elif "data" in result:
                data = result["data"]
                if isinstance(data, pd.DataFrame):
                    df = data
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    df = pd.DataFrame.from_dict(data)
            
            if df is None or df.empty:
                continue
            
            # Get domain enum
            try:
                domain_enum = DataDomain.from_string(domain_name)
            except ValueError:
                domain_enum = DataDomain.ECONOMIC
            
            # Build metadata
            meta = result.get("metadata", {})
            if "timestamp" in result:
                meta["fetch_timestamp"] = result["timestamp"]
            if "api" in result:
                meta["api"] = result["api"]
            if "cache_hit" in result:
                meta["cache_hit"] = result["cache_hit"]
            
            domains[domain_name] = DomainData(
                domain=domain_enum,
                data=df,
                source=result.get("source", ""),
                metadata=meta,
            )
        
        # Add connector metadata to bundle
        bundle_meta = kwargs.pop("metadata", {})
        bundle_meta["data_source_type"] = "live_connectors"
        bundle_meta["connector_domains"] = list(domains.keys())
        
        return cls(domains=domains, metadata=bundle_meta, **kwargs)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Access Methods
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get(self, domain: str | DataDomain) -> DomainData:
        """
        Get data for a specific domain.
        
        Args:
            domain: Domain name or DataDomain enum.
        
        Returns:
            DomainData for the requested domain.
        
        Raises:
            DataBundleValidationError: If domain is not available.
        """
        key = domain.value if isinstance(domain, DataDomain) else domain
        
        if key not in self.domains:
            raise DataBundleValidationError(
                f"Domain '{key}' not found in bundle",
                missing_domains=[key],
            )
        
        return self.domains[key]
    
    def get_dataframe(self, domain: str | DataDomain) -> pd.DataFrame:
        """
        Get DataFrame for a specific domain.
        
        Args:
            domain: Domain name or DataDomain enum.
        
        Returns:
            DataFrame for the domain.
        
        Raises:
            DataBundleValidationError: If domain is not available or not a DataFrame.
        """
        import pandas as pd
        
        domain_data = self.get(domain)
        
        if not isinstance(domain_data.data, pd.DataFrame):
            raise DataBundleValidationError(
                f"Domain '{domain}' data is not a DataFrame",
                invalid_domains=[str(domain)],
            )
        
        return domain_data.data
    
    def get_array(self, domain: str | DataDomain) -> NDArray[Any]:
        """
        Get array for a specific domain.
        
        If the domain contains a DataFrame, its values are returned.
        
        Args:
            domain: Domain name or DataDomain enum.
        
        Returns:
            NumPy array for the domain.
        """
        domain_data = self.get(domain)
        
        if hasattr(domain_data.data, "values"):
            return domain_data.data.values
        
        return domain_data.data
    
    def has_domain(self, domain: str | DataDomain) -> bool:
        """Check if a domain is available in the bundle."""
        key = domain.value if isinstance(domain, DataDomain) else domain
        return key in self.domains
    
    def has_domains(self, domains: list[str | DataDomain]) -> bool:
        """Check if all specified domains are available."""
        return all(self.has_domain(d) for d in domains)
    
    def __contains__(self, domain: str | DataDomain) -> bool:
        """Support `domain in bundle` syntax."""
        return self.has_domain(domain)
    
    def __getitem__(self, domain: str | DataDomain) -> DomainData:
        """Support `bundle[domain]` syntax."""
        return self.get(domain)
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over domain names."""
        return iter(self.domains)
    
    def __len__(self) -> int:
        """Number of domains."""
        return len(self.domains)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Validation
    # ═══════════════════════════════════════════════════════════════════════════
    
    def validate_requirements(
        self,
        required_domains: list[str | DataDomain],
        *,
        strict: bool = True,
    ) -> bool:
        """
        Validate that all required domains are available.
        
        Args:
            required_domains: List of required domain names.
            strict: If True, raise exception on missing domains.
        
        Returns:
            True if all requirements are met.
        
        Raises:
            DataBundleValidationError: If domains are missing and strict=True.
        """
        missing = []
        
        for domain in required_domains:
            if not self.has_domain(domain):
                key = domain.value if isinstance(domain, DataDomain) else domain
                missing.append(key)
        
        if missing:
            if strict:
                raise DataBundleValidationError(
                    f"Missing required domains: {missing}",
                    missing_domains=missing,
                )
            return False
        
        return True
    
    def validate_schemas(self) -> dict[str, bool]:
        """
        Validate all domains against their schemas.
        
        Returns:
            Dictionary mapping domain names to validation results.
        """
        return {name: data.validate_schema() for name, data in self.domains.items()}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Audit & Reproducibility
    # ═══════════════════════════════════════════════════════════════════════════
    
    def content_hash(self) -> str:
        """
        Compute a hash of all bundle contents for reproducibility.
        
        This hash can be used to verify that the same data was used
        across different executions.
        
        Returns:
            SHA-256 hash (first 32 characters) of bundle contents.
        """
        hashes = {name: data.content_hash() for name, data in sorted(self.domains.items())}
        combined = json.dumps(hashes, sort_keys=True)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def manifest(self) -> dict[str, Any]:
        """
        Generate a manifest of bundle contents for auditing.
        
        Returns:
            Dictionary with bundle metadata and domain summaries.
        """
        return {
            "bundle_id": self.bundle_id,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "content_hash": self.content_hash(),
            "n_domains": self.n_domains,
            "total_records": self.total_records,
            "domains": {
                name: data.to_dict()
                for name, data in self.domains.items()
            },
            "metadata": self.metadata,
        }
    
    def to_dict(self) -> dict[str, Any]:
        """Convert bundle to dictionary (metadata only, not data)."""
        return self.manifest()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Subset & Transform
    # ═══════════════════════════════════════════════════════════════════════════
    
    def subset(self, domains: list[str | DataDomain]) -> DataBundle:
        """
        Create a new bundle with only the specified domains.
        
        Args:
            domains: List of domain names to include.
        
        Returns:
            New DataBundle with subset of domains.
        """
        subset_domains = {}
        
        for domain in domains:
            key = domain.value if isinstance(domain, DataDomain) else domain
            if key in self.domains:
                subset_domains[key] = self.domains[key]
        
        return DataBundle(
            domains=subset_domains,
            description=f"Subset of {self.bundle_id}",
            metadata={"parent_bundle_id": self.bundle_id},
        )
    
    def merge(self, other: DataBundle) -> DataBundle:
        """
        Merge with another DataBundle.

        Domains from `other` override domains in `self` if there are conflicts.

        Args:
            other: Another DataBundle to merge with.

        Returns:
            New DataBundle with combined domains.
        """
        merged_domains = {**self.domains, **other.domains}

        return DataBundle(
            domains=merged_domains,
            description=f"Merged: {self.bundle_id} + {other.bundle_id}",
            metadata={
                "parent_bundles": [self.bundle_id, other.bundle_id],
            },
        )

    def get_quality_report(self) -> dict[str, Any]:
        """
        Generate quality report for all domains in bundle.

        Aggregates quality metrics from all domains and identifies
        potential issues or recommendations for data improvements.

        Returns:
            Dictionary containing:
            - overall_quality: Weighted average quality score (0-1)
            - domain_scores: Quality scores per domain
            - warnings: List of quality warnings
            - recommendations: List of actionable recommendations

        Example:
            >>> bundle = DataBundle.from_connector_results(results)
            >>> report = bundle.get_quality_report()
            >>> print(report['overall_quality'])
            0.83
            >>> print(report['warnings'])
            ['Low temporal coverage (0.60) for housing domain']
        """
        report = {
            'overall_quality': 0.0,
            'domain_scores': {},
            'warnings': [],
            'recommendations': []
        }

        # Aggregate quality scores from all domains
        total_quality = 0.0
        scored_domains = 0

        for domain_name, domain_data in self.domains.items():
            scores = domain_data.quality_scores

            if scores:
                report['domain_scores'][domain_name] = scores

                # Compute average quality for this domain
                domain_avg = sum(scores.values()) / len(scores) if scores else 0.0
                total_quality += domain_avg
                scored_domains += 1

                # Check for quality issues and generate warnings
                if scores.get('completeness', 1.0) < 0.7:
                    report['warnings'].append(
                        f"Low completeness ({scores['completeness']:.1%}) for {domain_name} domain"
                    )

                if scores.get('temporal_coverage', 1.0) < 0.6:
                    report['warnings'].append(
                        f"Low temporal coverage ({scores['temporal_coverage']:.1%}) for {domain_name} domain"
                    )

                if scores.get('update_frequency', 1.0) < 0.5:
                    report['warnings'].append(
                        f"Infrequent updates ({scores['update_frequency']:.1%}) for {domain_name} domain"
                    )

                if scores.get('geographic_granularity', 1.0) < 0.5:
                    report['warnings'].append(
                        f"Coarse geographic granularity ({scores['geographic_granularity']:.1%}) for {domain_name} domain"
                    )

                # Check if fallback source was used
                if domain_data.source_quality_rank > 0:
                    report['warnings'].append(
                        f"Using fallback source (rank {domain_data.source_quality_rank}) for {domain_name} domain"
                    )
                    report['recommendations'].append(
                        f"Consider upgrading tier or investigating primary source failure for {domain_name}"
                    )

                # Generate recommendations based on tier accessibility
                if scores.get('tier_accessibility', 1.0) < 0.5:
                    report['recommendations'].append(
                        f"Higher quality data available for {domain_name} with Professional/Enterprise tier upgrade"
                    )

        # Compute overall quality
        if scored_domains > 0:
            report['overall_quality'] = total_quality / scored_domains

        # Add summary recommendation if overall quality is low
        if report['overall_quality'] < 0.7:
            report['recommendations'].insert(
                0,
                f"Overall data quality ({report['overall_quality']:.1%}) is below recommended threshold (70%). Consider alternative data sources or tier upgrade."
            )

        return report

    def __repr__(self) -> str:
        return (
            f"DataBundle("
            f"id={self.bundle_id[:8]}..., "
            f"domains={self.available_domains}, "
            f"records={self.total_records})"
        )


# ════════════════════════════════════════════════════════════════════════════════
# Exports
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "DataBundle",
    "DataDomain",
    "DomainData",
]
