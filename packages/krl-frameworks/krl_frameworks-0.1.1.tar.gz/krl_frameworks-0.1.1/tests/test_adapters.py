# ════════════════════════════════════════════════════════════════════════════════
# KRL Frameworks - Adapter Tests
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
Comprehensive tests for KRL Frameworks adapters.

These tests verify cross-package cohesion by:
1. Testing adapter imports work correctly
2. Testing adapter methods with mocked dependencies
3. Verifying correct API signatures are used
"""

from __future__ import annotations

import sys
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest


# ════════════════════════════════════════════════════════════════════════════════
# Optional Dependency Checks
# ════════════════════════════════════════════════════════════════════════════════

def _has_krl_geospatial() -> bool:
    """Check if krl_geospatial is installed."""
    try:
        import krl_geospatial
        return True
    except ImportError:
        return False

def _has_krl_network() -> bool:
    """Check if krl_network is installed."""
    try:
        import krl_network
        return True
    except ImportError:
        return False

skip_if_no_geospatial = pytest.mark.skipif(
    not _has_krl_geospatial(),
    reason="krl_geospatial not installed (optional dependency)"
)

skip_if_no_network = pytest.mark.skipif(
    not _has_krl_network(),
    reason="krl_network not installed (optional dependency)"
)


# ════════════════════════════════════════════════════════════════════════════════
# Spatial Adapter Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestSpatialAdapterImports:
    """Test spatial adapter import paths are correct."""
    
    def test_spatial_adapter_module_imports(self):
        """Verify spatial adapter module can be imported."""
        from krl_frameworks.adapters.spatial import (
            SpatialAdapter,
            check_geospatial_tools_installed,
        )
        assert SpatialAdapter is not None
        assert callable(check_geospatial_tools_installed)
    
    def test_geospatial_tools_check_returns_bool(self):
        """Check function returns boolean."""
        from krl_frameworks.adapters.spatial import check_geospatial_tools_installed
        result = check_geospatial_tools_installed()
        assert isinstance(result, bool)


class TestSpatialAdapterMethods:
    """Test spatial adapter methods with mocks."""
    
    @pytest.fixture
    def mock_gdf(self):
        """Create mock GeoDataFrame-like object."""
        gdf = MagicMock()
        gdf.__getitem__ = MagicMock(return_value=MagicMock(
            values=np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        ))
        return gdf
    
    def test_choropleth_data_quantiles(self, mock_gdf):
        """Test choropleth_data with quantiles scheme."""
        with patch('krl_frameworks.adapters.spatial.check_geospatial_tools_installed', return_value=True):
            from krl_frameworks.adapters.spatial import SpatialAdapter
            
            # Mock the adapter initialization
            with patch.object(SpatialAdapter, '__init__', lambda self: None):
                adapter = SpatialAdapter()
                adapter._weights_cache = {}
                
                result = adapter.choropleth_data(mock_gdf, 'test_col', scheme='quantiles', k=3)
                
                assert 'breaks' in result
                assert 'classes' in result
                assert 'scheme' in result
                assert result['scheme'] == 'quantiles'
                assert result['k'] == 3
    
    def test_choropleth_data_equal_interval(self, mock_gdf):
        """Test choropleth_data with equal_interval scheme."""
        with patch('krl_frameworks.adapters.spatial.check_geospatial_tools_installed', return_value=True):
            from krl_frameworks.adapters.spatial import SpatialAdapter
            
            with patch.object(SpatialAdapter, '__init__', lambda self: None):
                adapter = SpatialAdapter()
                adapter._weights_cache = {}
                
                result = adapter.choropleth_data(mock_gdf, 'test_col', scheme='equal_interval', k=5)
                
                assert result['scheme'] == 'equal_interval'
                assert len(result['breaks']) == 6  # k+1 breaks
    
    def test_choropleth_data_invalid_scheme(self, mock_gdf):
        """Test choropleth_data raises on invalid scheme."""
        with patch('krl_frameworks.adapters.spatial.check_geospatial_tools_installed', return_value=True):
            from krl_frameworks.adapters.spatial import SpatialAdapter
            
            with patch.object(SpatialAdapter, '__init__', lambda self: None):
                adapter = SpatialAdapter()
                adapter._weights_cache = {}
                
                with pytest.raises(ValueError, match="Unknown scheme"):
                    adapter.choropleth_data(mock_gdf, 'test_col', scheme='invalid')
    
    @skip_if_no_geospatial
    def test_compute_spatial_weights_method_validation(self):
        """Test compute_spatial_weights validates method parameter."""
        with patch('krl_frameworks.adapters.spatial.check_geospatial_tools_installed', return_value=True):
            from krl_frameworks.adapters.spatial import SpatialAdapter
            
            with patch.object(SpatialAdapter, '__init__', lambda self: None):
                adapter = SpatialAdapter()
                adapter._weights_cache = {}
                
                # Mock the weight classes
                mock_gdf = MagicMock()
                
                with patch('krl_geospatial.weights.QueenWeights') as mock_queen:
                    mock_queen.return_value = MagicMock()
                    result = adapter.compute_spatial_weights(mock_gdf, method='queen')
                    mock_queen.assert_called_once_with(mock_gdf)
    
    @skip_if_no_geospatial
    def test_spatial_weights_invalid_method(self):
        """Test compute_spatial_weights raises on invalid method."""
        with patch('krl_frameworks.adapters.spatial.check_geospatial_tools_installed', return_value=True):
            from krl_frameworks.adapters.spatial import SpatialAdapter
            
            with patch.object(SpatialAdapter, '__init__', lambda self: None):
                adapter = SpatialAdapter()
                adapter._weights_cache = {}
                
                with pytest.raises(ValueError, match="Unknown weight method"):
                    adapter.compute_spatial_weights(MagicMock(), method='invalid_method')
    
    @skip_if_no_geospatial
    def test_spatial_autocorrelation_returns_dict(self):
        """Test spatial_autocorrelation returns proper structure."""
        with patch('krl_frameworks.adapters.spatial.check_geospatial_tools_installed', return_value=True):
            from krl_frameworks.adapters.spatial import SpatialAdapter
            
            with patch.object(SpatialAdapter, '__init__', lambda self: None):
                adapter = SpatialAdapter()
                adapter._weights_cache = {}
                
                # Mock morans_i
                mock_result = MagicMock()
                mock_result.I = 0.5
                mock_result.p_sim = 0.01
                mock_result.z_sim = 2.5
                mock_result.EI = -0.1
                
                with patch('krl_geospatial.econometrics.morans_i', return_value=mock_result):
                    result = adapter.spatial_autocorrelation(np.array([1, 2, 3]), MagicMock())
                    
                    assert 'I' in result
                    assert 'p_value' in result
                    assert 'z_score' in result
                    assert 'expected_I' in result
                    assert result['I'] == 0.5


# ════════════════════════════════════════════════════════════════════════════════
# Network Adapter Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestNetworkAdapterImports:
    """Test network adapter import paths are correct."""
    
    def test_network_adapter_module_imports(self):
        """Verify network adapter module can be imported."""
        from krl_frameworks.adapters.network import (
            NetworkAdapter,
            check_network_analysis_installed,
        )
        assert NetworkAdapter is not None
        assert callable(check_network_analysis_installed)
    
    def test_network_analysis_check_returns_bool(self):
        """Check function returns boolean."""
        from krl_frameworks.adapters.network import check_network_analysis_installed
        result = check_network_analysis_installed()
        assert isinstance(result, bool)


class TestNetworkAdapterMethods:
    """Test network adapter methods with mocks."""
    
    @pytest.fixture
    def mock_graph(self):
        """Create mock NetworkX graph."""
        graph = MagicMock()
        graph.nodes.return_value = ['A', 'B', 'C']
        graph.edges.return_value = [('A', 'B'), ('B', 'C')]
        graph.is_directed.return_value = False
        graph.number_of_nodes.return_value = 3
        graph.number_of_edges.return_value = 2
        return graph
    
    def test_build_exposure_graph_creates_graph(self):
        """Test build_exposure_graph creates NetworkX graph."""
        with patch('krl_frameworks.adapters.network.check_network_analysis_installed', return_value=True):
            from krl_frameworks.adapters.network import NetworkAdapter
            
            with patch.object(NetworkAdapter, '__init__', lambda self: None):
                adapter = NetworkAdapter()
                
                df = pd.DataFrame({
                    'source': ['A', 'B', 'C'],
                    'target': ['B', 'C', 'A'],
                    'weight': [1.0, 2.0, 3.0]
                })
                
                with patch('networkx.DiGraph') as mock_digraph:
                    mock_g = MagicMock()
                    mock_g.has_edge.return_value = False
                    mock_digraph.return_value = mock_g
                    
                    result = adapter.build_exposure_graph(
                        df, 'source', 'target', 'weight', directed=True
                    )
                    
                    mock_digraph.assert_called_once()
                    assert mock_g.add_edge.call_count == 3
    
    @skip_if_no_network
    def test_compute_centrality_degree_with_normalized(self, mock_graph):
        """Test compute_centrality passes normalized to degree."""
        with patch('krl_frameworks.adapters.network.check_network_analysis_installed', return_value=True):
            from krl_frameworks.adapters.network import NetworkAdapter
            
            with patch.object(NetworkAdapter, '__init__', lambda self: None):
                adapter = NetworkAdapter()
                
                with patch('krl_network.metrics.degree_centrality') as mock_dc:
                    mock_dc.return_value = {'A': 0.5, 'B': 1.0, 'C': 0.5}
                    
                    result = adapter.compute_centrality(mock_graph, method='degree', normalized=True)
                    
                    mock_dc.assert_called_once_with(mock_graph, normalized=True)
    
    @skip_if_no_network
    def test_compute_centrality_eigenvector_without_normalized(self, mock_graph):
        """Test compute_centrality does NOT pass normalized to eigenvector."""
        with patch('krl_frameworks.adapters.network.check_network_analysis_installed', return_value=True):
            from krl_frameworks.adapters.network import NetworkAdapter
            
            with patch.object(NetworkAdapter, '__init__', lambda self: None):
                adapter = NetworkAdapter()
                
                with patch('krl_network.metrics.eigenvector_centrality') as mock_ec:
                    mock_ec.return_value = {'A': 0.3, 'B': 0.7, 'C': 0.5}
                    
                    result = adapter.compute_centrality(mock_graph, method='eigenvector', normalized=True)
                    
                    # Should NOT include normalized parameter
                    mock_ec.assert_called_once_with(mock_graph)
    
    @skip_if_no_network
    def test_compute_centrality_pagerank_without_normalized(self, mock_graph):
        """Test compute_centrality does NOT pass normalized to pagerank."""
        with patch('krl_frameworks.adapters.network.check_network_analysis_installed', return_value=True):
            from krl_frameworks.adapters.network import NetworkAdapter
            
            with patch.object(NetworkAdapter, '__init__', lambda self: None):
                adapter = NetworkAdapter()
                
                with patch('krl_network.metrics.pagerank') as mock_pr:
                    mock_pr.return_value = {'A': 0.33, 'B': 0.34, 'C': 0.33}
                    
                    result = adapter.compute_centrality(mock_graph, method='pagerank', normalized=False)
                    
                    # Should NOT include normalized parameter
                    mock_pr.assert_called_once_with(mock_graph)
    
    @skip_if_no_network
    def test_compute_centrality_betweenness_with_normalized(self, mock_graph):
        """Test compute_centrality passes normalized to betweenness."""
        with patch('krl_frameworks.adapters.network.check_network_analysis_installed', return_value=True):
            from krl_frameworks.adapters.network import NetworkAdapter
            
            with patch.object(NetworkAdapter, '__init__', lambda self: None):
                adapter = NetworkAdapter()
                
                with patch('krl_network.metrics.betweenness_centrality') as mock_bc:
                    mock_bc.return_value = {'A': 0.0, 'B': 1.0, 'C': 0.0}
                    
                    result = adapter.compute_centrality(mock_graph, method='betweenness', normalized=False)
                    
                    mock_bc.assert_called_once_with(mock_graph, normalized=False)
    
    @skip_if_no_network
    def test_compute_centrality_invalid_method(self, mock_graph):
        """Test compute_centrality raises on invalid method."""
        with patch('krl_frameworks.adapters.network.check_network_analysis_installed', return_value=True):
            from krl_frameworks.adapters.network import NetworkAdapter
            
            with patch.object(NetworkAdapter, '__init__', lambda self: None):
                adapter = NetworkAdapter()
                
                with pytest.raises(ValueError, match="Unknown centrality method"):
                    adapter.compute_centrality(mock_graph, method='invalid')
    
    def test_simulate_shock_propagation_returns_dict(self):
        """Test simulate_shock_propagation returns proper structure."""
        with patch('krl_frameworks.adapters.network.check_network_analysis_installed', return_value=True):
            from krl_frameworks.adapters.network import NetworkAdapter
            
            with patch.object(NetworkAdapter, '__init__', lambda self: None):
                adapter = NetworkAdapter()
                
                # Create a simple mock graph
                mock_graph = MagicMock()
                mock_graph.nodes.return_value = ['A', 'B', 'C']
                mock_graph.edges.return_value = [('A', 'B', {'weight': 1.0})]
                mock_graph.edges.side_effect = lambda data=False: [('A', 'B', {'weight': 1.0})] if data else [('A', 'B')]
                mock_graph.is_directed.return_value = False
                
                result = adapter.simulate_shock_propagation(
                    mock_graph,
                    initial_shock={'A': 0.5},
                    max_iterations=10
                )
                
                assert 'final_state' in result
                assert 'affected_nodes' in result
                assert 'cascade_depth' in result
                assert 'total_impact' in result


# ════════════════════════════════════════════════════════════════════════════════
# Causal Adapter Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestCausalAdapterImports:
    """Test causal adapter import paths are correct."""
    
    def test_causal_adapter_module_imports(self):
        """Verify causal adapter module can be imported."""
        from krl_frameworks.adapters.causal import (
            CausalAdapter,
            check_causal_toolkit_installed,
        )
        assert CausalAdapter is not None
        assert callable(check_causal_toolkit_installed)
    
    def test_causal_toolkit_check_returns_bool(self):
        """Check function returns boolean."""
        from krl_frameworks.adapters.causal import check_causal_toolkit_installed
        result = check_causal_toolkit_installed()
        assert isinstance(result, bool)


class TestCausalAdapterMethods:
    """Test causal adapter methods with mocks."""
    
    def test_causal_method_literal_type(self):
        """Test CausalMethod is a Literal type with expected values."""
        from krl_frameworks.adapters.causal import CausalMethod
        import typing
        
        # CausalMethod is a Literal type
        args = typing.get_args(CausalMethod)
        expected = {'did', 'scm', 'psm', 'iv', 'rdd'}
        
        assert set(args) == expected, f"Expected {expected}, got {set(args)}"
    
    def test_get_causal_estimator_function(self):
        """Test get_causal_estimator function exists and is callable."""
        from krl_frameworks.adapters.causal import get_causal_estimator
        
        assert callable(get_causal_estimator)
    
    def test_causal_adapter_has_estimate_method(self):
        """Test CausalAdapter has estimate method."""
        with patch('krl_frameworks.adapters.causal.check_causal_toolkit_installed', return_value=True):
            from krl_frameworks.adapters.causal import CausalAdapter
            
            with patch.object(CausalAdapter, '__init__', lambda self, method: setattr(self, '_method', method)):
                adapter = CausalAdapter('did')  # Use string literal
                
                assert hasattr(adapter, 'estimate') or hasattr(CausalAdapter, 'estimate')


# ════════════════════════════════════════════════════════════════════════════════
# Connector Adapter Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestConnectorAdapterImports:
    """Test connector adapter import paths are correct."""
    
    def test_connector_adapter_module_imports(self):
        """Verify connector adapter module can be imported."""
        from krl_frameworks.adapters.connectors import (
            ConnectorProtocol,
            DataBundleFactory,
        )
        assert ConnectorProtocol is not None
        assert DataBundleFactory is not None


class TestDataBundleFactory:
    """Test DataBundleFactory methods."""
    
    def test_factory_creation(self):
        """Test factory can be created."""
        from krl_frameworks.adapters.connectors import DataBundleFactory
        
        factory = DataBundleFactory()
        assert factory is not None
        assert factory.list_domains() == []
    
    def test_add_connector(self):
        """Test adding a connector."""
        from krl_frameworks.adapters.connectors import DataBundleFactory
        
        factory = DataBundleFactory()
        
        # Create mock connector with fetch method
        mock_connector = MagicMock()
        mock_connector.fetch = MagicMock(return_value=pd.DataFrame({'a': [1, 2, 3]}))
        
        result = factory.add_connector('test_domain', mock_connector)
        
        assert result is factory  # Returns self for chaining
        assert 'test_domain' in factory.list_domains()
    
    def test_add_connector_rejects_invalid(self):
        """Test adding invalid connector raises TypeError."""
        from krl_frameworks.adapters.connectors import DataBundleFactory
        
        factory = DataBundleFactory()
        
        # Object without fetch method
        invalid_connector = object()
        
        with pytest.raises(TypeError, match="fetch"):
            factory.add_connector('test', invalid_connector)
    
    def test_remove_connector(self):
        """Test removing a connector."""
        from krl_frameworks.adapters.connectors import DataBundleFactory
        
        factory = DataBundleFactory()
        
        mock_connector = MagicMock()
        mock_connector.fetch = MagicMock()
        
        factory.add_connector('test', mock_connector)
        assert 'test' in factory.list_domains()
        
        factory.remove_connector('test')
        assert 'test' not in factory.list_domains()
    
    def test_build_calls_fetch(self):
        """Test build calls connector fetch methods."""
        from krl_frameworks.adapters.connectors import DataBundleFactory
        
        factory = DataBundleFactory()
        
        mock_connector = MagicMock()
        mock_connector.fetch = MagicMock(return_value=pd.DataFrame({'col': [1, 2, 3]}))
        
        factory.add_connector('economic', mock_connector)
        
        bundle = factory.build(economic={'param1': 'value1'})
        
        mock_connector.fetch.assert_called_once_with(param1='value1')
        assert bundle is not None
    
    def test_from_connectors_class_method(self):
        """Test from_connectors factory method."""
        from krl_frameworks.adapters.connectors import DataBundleFactory
        
        mock_connector = MagicMock()
        mock_connector.fetch = MagicMock(return_value=pd.DataFrame({'x': [1]}))
        
        bundle = DataBundleFactory.from_connectors(
            connectors={'domain1': mock_connector},
            domain1={'key': 'val'}
        )
        
        mock_connector.fetch.assert_called_once_with(key='val')


# ════════════════════════════════════════════════════════════════════════════════
# Tier Conversion Tests
# ════════════════════════════════════════════════════════════════════════════════


class TestTierConversion:
    """Test tier conversion between krl-frameworks and krl-types."""
    
    def test_tier_from_string(self):
        """Test Tier.from_string conversion."""
        from krl_frameworks.core.tier import Tier
        
        assert Tier.from_string('community') == Tier.COMMUNITY
        assert Tier.from_string('COMMUNITY') == Tier.COMMUNITY
        assert Tier.from_string('Community') == Tier.COMMUNITY
        assert Tier.from_string('professional') == Tier.PROFESSIONAL
        assert Tier.from_string('PRO') == Tier.PROFESSIONAL
        assert Tier.from_string('enterprise') == Tier.ENTERPRISE
    
    def test_tier_from_string_invalid(self):
        """Test Tier.from_string raises on invalid input."""
        from krl_frameworks.core.tier import Tier
        
        with pytest.raises(ValueError, match="Invalid tier"):
            Tier.from_string('invalid_tier')
    
    def test_tier_to_api(self):
        """Test Tier.to_api returns lowercase string."""
        from krl_frameworks.core.tier import Tier
        
        assert Tier.COMMUNITY.to_api() == 'community'
        assert Tier.PROFESSIONAL.to_api() == 'professional'
        assert Tier.ENTERPRISE.to_api() == 'enterprise'
        assert Tier.PRO.to_api() == 'professional'  # Alias
    
    def test_tier_from_api_with_string(self):
        """Test Tier.from_api with string input."""
        from krl_frameworks.core.tier import Tier
        
        assert Tier.from_api('community') == Tier.COMMUNITY
        assert Tier.from_api('professional') == Tier.PROFESSIONAL
        assert Tier.from_api('enterprise') == Tier.ENTERPRISE
    
    def test_tier_from_api_with_enum(self):
        """Test Tier.from_api with mock enum input."""
        from krl_frameworks.core.tier import Tier
        
        # Mock krl_types.billing.Tier
        mock_api_tier = MagicMock()
        mock_api_tier.value = 'enterprise'
        mock_api_tier.name = 'ENTERPRISE'
        
        result = Tier.from_api(mock_api_tier)
        assert result == Tier.ENTERPRISE
    
    def test_tier_can_access(self):
        """Test Tier.can_access comparison."""
        from krl_frameworks.core.tier import Tier
        
        assert Tier.ENTERPRISE.can_access(Tier.COMMUNITY)
        assert Tier.ENTERPRISE.can_access(Tier.PROFESSIONAL)
        assert Tier.ENTERPRISE.can_access(Tier.ENTERPRISE)
        assert not Tier.COMMUNITY.can_access(Tier.PROFESSIONAL)
        assert not Tier.PROFESSIONAL.can_access(Tier.ENTERPRISE)
    
    def test_tier_ordering(self):
        """Test tier ordering for access control."""
        from krl_frameworks.core.tier import Tier
        
        assert Tier.COMMUNITY < Tier.PROFESSIONAL
        assert Tier.PROFESSIONAL < Tier.TEAM
        assert Tier.TEAM < Tier.ENTERPRISE
        assert Tier.ENTERPRISE < Tier.CUSTOM
        
        # IntEnum allows >= comparison
        assert Tier.ENTERPRISE >= Tier.COMMUNITY
        assert Tier.ENTERPRISE >= Tier.ENTERPRISE
