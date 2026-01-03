"""
Test Enhanced Dashboard

Tests:
- Flow node/edge tracking
- Metrics collection
- HTML generation
- Data export for D3.js
- Real-time updates

Author: MDSA Framework Team
Date: 2025-12-06
"""

import pytest
import json
import time
from pathlib import Path
from mdsa.ui.enhanced_dashboard import (
    EnhancedDashboard,
    FlowNode,
    FlowEdge,
    MetricSnapshot
)


class TestFlowTracking:
    """Test flow visualization tracking."""

    def test_add_node(self):
        """Test adding nodes to flow."""
        dashboard = EnhancedDashboard()

        node = dashboard.add_node(
            "test_node_1",
            "query",
            "Test Query",
            status="active",
            extra_data="test"
        )

        assert isinstance(node, FlowNode)
        assert node.id == "test_node_1"
        assert node.type == "query"
        assert node.label == "Test Query"
        assert node.status == "active"
        assert node.metadata['extra_data'] == "test"
        assert "test_node_1" in dashboard.nodes

    def test_add_edge(self):
        """Test adding edges between nodes."""
        dashboard = EnhancedDashboard()

        dashboard.add_node("node1", "query", "Query")
        dashboard.add_node("node2", "router", "Router")

        edge = dashboard.add_edge(
            "node1",
            "node2",
            "classify",
            status="active"
        )

        assert isinstance(edge, FlowEdge)
        assert edge.source == "node1"
        assert edge.target == "node2"
        assert edge.label == "classify"
        assert edge.status == "active"
        assert edge in dashboard.edges

    def test_update_node_status(self):
        """Test updating node status."""
        dashboard = EnhancedDashboard()

        dashboard.add_node("test_node", "query", "Test")
        dashboard.update_node_status(
            "test_node",
            "completed",
            result="success"
        )

        node = dashboard.nodes["test_node"]
        assert node.status == "completed"
        assert node.metadata['result'] == "success"

    def test_update_edge_status(self):
        """Test updating edge status."""
        dashboard = EnhancedDashboard()

        dashboard.add_node("node1", "query", "Q")
        dashboard.add_node("node2", "router", "R")
        dashboard.add_edge("node1", "node2", "classify")

        dashboard.update_edge_status("node1", "node2", "completed")

        edge = dashboard.edges[0]
        assert edge.status == "completed"


class TestMetricsTracking:
    """Test metrics collection and tracking."""

    def test_track_request(self):
        """Test tracking a single request."""
        dashboard = EnhancedDashboard()

        dashboard.track_request(
            query="Test query",
            domain="finance",
            model="gpt2",
            latency_ms=100.5,
            success=True,
            correlation_id="req_1"
        )

        metrics = dashboard.get_current_metrics()
        assert metrics['total_requests'] == 1
        assert metrics['successful_requests'] == 1
        assert metrics['failed_requests'] == 0
        assert 'finance' in metrics['active_domains']
        assert 'gpt2' in metrics['active_models']
        assert metrics['routing_distribution']['finance'] == 1

    def test_track_multiple_requests(self):
        """Test tracking multiple requests."""
        dashboard = EnhancedDashboard()

        requests = [
            ("Query 1", "finance", "gpt2", 100.0, True),
            ("Query 2", "medical", "phi-2", 150.0, True),
            ("Query 3", "finance", "gpt2", 120.0, False),
        ]

        for i, (query, domain, model, latency, success) in enumerate(requests):
            dashboard.track_request(
                query, domain, model, latency, success, f"req_{i}"
            )

        metrics = dashboard.get_current_metrics()
        assert metrics['total_requests'] == 3
        assert metrics['successful_requests'] == 2
        assert metrics['failed_requests'] == 1
        assert metrics['success_rate'] == pytest.approx(2/3)
        assert len(metrics['active_domains']) == 2
        assert metrics['routing_distribution']['finance'] == 2
        assert metrics['routing_distribution']['medical'] == 1

    def test_average_latency_calculation(self):
        """Test average latency calculation."""
        dashboard = EnhancedDashboard()

        latencies = [100.0, 200.0, 300.0]
        for i, latency in enumerate(latencies):
            dashboard.track_request(
                f"Query {i}",
                "finance",
                "gpt2",
                latency,
                True,
                f"req_{i}"
            )

        metrics = dashboard.get_current_metrics()
        expected_avg = sum(latencies) / len(latencies)
        assert metrics['avg_latency_ms'] == pytest.approx(expected_avg)

    def test_metrics_snapshot(self):
        """Test taking metrics snapshots."""
        dashboard = EnhancedDashboard()

        # Track 10 requests to trigger snapshot
        for i in range(10):
            dashboard.track_request(
                f"Query {i}",
                "finance",
                "gpt2",
                100.0,
                True,
                f"req_{i}"
            )

        assert len(dashboard.metrics_history) == 1
        snapshot = dashboard.metrics_history[0]
        assert isinstance(snapshot, MetricSnapshot)
        assert snapshot.total_requests == 10
        assert snapshot.successful_requests == 10

    def test_request_flow_creation(self):
        """Test that request creates proper flow nodes."""
        dashboard = EnhancedDashboard()

        dashboard.track_request(
            "Test query",
            "finance",
            "gpt2",
            100.0,
            True,
            "req_1"
        )

        # Should create: query -> router -> domain -> model -> response
        assert len(dashboard.nodes) == 5
        assert len(dashboard.edges) == 4

        # Check node types
        node_types = [node.type for node in dashboard.nodes.values()]
        assert 'query' in node_types
        assert 'router' in node_types
        assert 'domain' in node_types
        assert 'model' in node_types
        assert 'response' in node_types


class TestDataExport:
    """Test data export for visualizations."""

    def test_flow_data_export(self):
        """Test exporting flow data to JSON."""
        dashboard = EnhancedDashboard(output_dir="./test_dashboard_output")

        dashboard.add_node("node1", "query", "Test")
        dashboard.add_edge("node1", "node2", "link")

        # Check JSON file exists
        flow_file = Path(dashboard.output_dir) / f"{dashboard.session_id}_flow.json"
        assert flow_file.exists()

        # Check JSON content
        with open(flow_file, 'r') as f:
            data = json.load(f)

        assert 'nodes' in data
        assert 'edges' in data
        assert 'timestamp' in data
        assert len(data['nodes']) == 1
        assert len(data['edges']) == 1

        # Cleanup
        flow_file.unlink()
        Path(dashboard.output_dir).rmdir()

    def test_metrics_data_export(self):
        """Test exporting metrics data to JSON."""
        dashboard = EnhancedDashboard(output_dir="./test_dashboard_output")

        # Track requests to trigger metrics export
        for i in range(10):
            dashboard.track_request(
                f"Query {i}", "finance", "gpt2", 100.0, True, f"req_{i}"
            )

        # Check JSON file exists
        metrics_file = Path(dashboard.output_dir) / f"{dashboard.session_id}_metrics.json"
        assert metrics_file.exists()

        # Check JSON content
        with open(metrics_file, 'r') as f:
            data = json.load(f)

        assert 'current' in data
        assert 'history' in data
        assert 'timestamp' in data
        assert data['current']['total_requests'] == 10

        # Cleanup
        metrics_file.unlink()
        flow_file = Path(dashboard.output_dir) / f"{dashboard.session_id}_flow.json"
        if flow_file.exists():
            flow_file.unlink()
        Path(dashboard.output_dir).rmdir()


class TestHTMLGeneration:
    """Test HTML dashboard generation."""

    def test_generate_html_dashboard(self):
        """Test generating HTML dashboard."""
        dashboard = EnhancedDashboard(output_dir="./test_dashboard_output")

        # Track some requests
        dashboard.track_request("Test", "finance", "gpt2", 100.0, True, "req_1")

        # Generate HTML
        html_file = dashboard.generate_html_dashboard()

        # Check file exists
        assert Path(html_file).exists()
        assert html_file.endswith('.html')

        # Check HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '<!DOCTYPE html>' in content
        assert 'MDSA Enhanced Dashboard' in content
        assert 'd3.v7.min.js' in content
        assert 'flow-chart' in content
        assert 'routing-chart' in content

        # Cleanup
        Path(html_file).unlink()
        metrics_file = Path(dashboard.output_dir) / f"{dashboard.session_id}_metrics.json"
        flow_file = Path(dashboard.output_dir) / f"{dashboard.session_id}_flow.json"
        if metrics_file.exists():
            metrics_file.unlink()
        if flow_file.exists():
            flow_file.unlink()
        Path(dashboard.output_dir).rmdir()

    def test_html_includes_d3js(self):
        """Test that HTML includes D3.js library."""
        dashboard = EnhancedDashboard()
        html = dashboard._get_dashboard_html_template()

        assert 'https://d3js.org/d3.v7.min.js' in html

    def test_html_includes_visualizations(self):
        """Test that HTML includes visualization elements."""
        dashboard = EnhancedDashboard()
        html = dashboard._get_dashboard_html_template()

        # Check for key visualization elements
        assert 'flow-chart' in html
        assert 'routing-chart' in html
        assert 'updateFlowChart' in html
        assert 'updateRoutingChart' in html
        assert 'loadData' in html


class TestDashboardStats:
    """Test dashboard statistics."""

    def test_get_stats(self):
        """Test getting dashboard statistics."""
        dashboard = EnhancedDashboard()

        dashboard.track_request("Test", "finance", "gpt2", 100.0, True, "req_1")

        stats = dashboard.get_stats()

        assert 'session_id' in stats
        assert 'start_time' in stats
        assert 'nodes_count' in stats
        assert 'edges_count' in stats
        assert 'metrics_snapshots' in stats
        assert 'current_metrics' in stats
        assert stats['nodes_count'] == 5  # query, router, domain, model, response
        assert stats['edges_count'] == 4

    def test_clear_dashboard(self):
        """Test clearing dashboard data."""
        dashboard = EnhancedDashboard()

        dashboard.track_request("Test", "finance", "gpt2", 100.0, True, "req_1")
        assert len(dashboard.nodes) > 0
        assert len(dashboard.edges) > 0

        dashboard.clear()

        assert len(dashboard.nodes) == 0
        assert len(dashboard.edges) == 0
        assert dashboard.current_metrics['total_requests'] == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_update_nonexistent_node(self):
        """Test updating a node that doesn't exist."""
        dashboard = EnhancedDashboard()

        # Should not raise error
        dashboard.update_node_status("nonexistent", "completed")

        assert "nonexistent" not in dashboard.nodes

    def test_update_nonexistent_edge(self):
        """Test updating an edge that doesn't exist."""
        dashboard = EnhancedDashboard()

        # Should not raise error
        dashboard.update_edge_status("node1", "node2", "completed")

        # No edges should exist
        assert len(dashboard.edges) == 0

    def test_zero_requests_metrics(self):
        """Test metrics with zero requests."""
        dashboard = EnhancedDashboard()

        metrics = dashboard.get_current_metrics()

        assert metrics['total_requests'] == 0
        assert metrics['success_rate'] == 0.0
        assert metrics['avg_latency_ms'] == 0.0
        assert len(metrics['active_domains']) == 0

    def test_failed_request_tracking(self):
        """Test tracking failed requests."""
        dashboard = EnhancedDashboard()

        dashboard.track_request(
            "Test", "finance", "gpt2", 100.0, False, "req_1"
        )

        metrics = dashboard.get_current_metrics()
        assert metrics['failed_requests'] == 1
        assert metrics['successful_requests'] == 0
        assert metrics['success_rate'] == 0.0

        # Check response node has error status
        response_nodes = [
            node for node in dashboard.nodes.values()
            if node.type == 'response'
        ]
        assert len(response_nodes) == 1
        assert response_nodes[0].status == 'error'


class TestIntegration:
    """Integration tests for dashboard."""

    def test_full_workflow(self):
        """Test complete dashboard workflow."""
        dashboard = EnhancedDashboard(output_dir="./test_dashboard_output")

        # Simulate multiple requests
        requests = [
            ("Finance query", "finance", "gpt2", 100.0, True),
            ("Medical query", "medical", "phi-2", 150.0, True),
            ("Support query", "support", "gpt2", 80.0, True),
            ("Failed query", "technical", "gpt2", 200.0, False),
        ]

        for i, (query, domain, model, latency, success) in enumerate(requests):
            dashboard.track_request(
                query, domain, model, latency, success, f"req_{i}"
            )

        # Generate dashboard
        html_file = dashboard.generate_html_dashboard()

        # Check all components
        assert Path(html_file).exists()

        metrics = dashboard.get_current_metrics()
        assert metrics['total_requests'] == 4
        assert metrics['successful_requests'] == 3
        assert metrics['failed_requests'] == 1

        stats = dashboard.get_stats()
        assert stats['nodes_count'] == 20  # 4 requests * 5 nodes each
        assert stats['edges_count'] == 16  # 4 requests * 4 edges each

        # Cleanup
        Path(html_file).unlink()
        metrics_file = Path(dashboard.output_dir) / f"{dashboard.session_id}_metrics.json"
        flow_file = Path(dashboard.output_dir) / f"{dashboard.session_id}_flow.json"
        if metrics_file.exists():
            metrics_file.unlink()
        if flow_file.exists():
            flow_file.unlink()
        Path(dashboard.output_dir).rmdir()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
