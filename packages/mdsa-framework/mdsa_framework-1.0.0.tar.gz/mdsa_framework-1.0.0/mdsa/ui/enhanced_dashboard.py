"""
Enhanced Dashboard with D3.js Visualizations

Provides real-time monitoring and visualization of MDSA orchestration.

Features:
- Real-time orchestration flow diagrams
- Interactive routing visualizations
- Live metrics and statistics
- Domain activity monitoring
- Best UX practices (minimal clicks, intuitive)

Author: MDSA Framework Team
Date: 2025-12-06
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class FlowNode:
    """Node in orchestration flow visualization."""
    id: str
    type: str  # 'query', 'router', 'domain', 'model', 'response'
    label: str
    status: str  # 'pending', 'active', 'completed', 'error'
    timestamp: float
    metadata: Dict[str, Any]


@dataclass
class FlowEdge:
    """Edge between nodes in flow visualization."""
    source: str
    target: str
    label: str
    status: str  # 'pending', 'active', 'completed'
    metadata: Dict[str, Any]


@dataclass
class MetricSnapshot:
    """Snapshot of system metrics at a point in time."""
    timestamp: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_latency_ms: float
    active_domains: List[str]
    active_models: List[str]
    routing_distribution: Dict[str, int]  # domain -> count


class EnhancedDashboard:
    """
    Enhanced dashboard with real-time visualizations.

    Provides:
    - D3.js flow diagrams
    - Real-time metrics
    - Interactive routing visualization
    - Domain activity monitoring
    """

    def __init__(self, output_dir: str = "./dashboard_output"):
        """
        Initialize enhanced dashboard.

        Args:
            output_dir: Directory to store dashboard data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Flow tracking
        self.nodes: Dict[str, FlowNode] = {}
        self.edges: List[FlowEdge] = []

        # Metrics tracking
        self.metrics_history: List[MetricSnapshot] = []
        self.current_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'latencies': [],
            'active_domains': set(),
            'active_models': set(),
            'routing_distribution': {},
        }

        # Session tracking
        self.session_id = f"session_{int(time.time())}"
        self.start_time = time.time()

    # ========================================================================
    # Flow Tracking
    # ========================================================================

    def add_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        status: str = 'pending',
        **metadata
    ) -> FlowNode:
        """Add a node to the flow visualization."""
        node = FlowNode(
            id=node_id,
            type=node_type,
            label=label,
            status=status,
            timestamp=time.time(),
            metadata=metadata
        )
        self.nodes[node_id] = node
        self._update_flow_data()
        return node

    def add_edge(
        self,
        source: str,
        target: str,
        label: str = "",
        status: str = 'pending',
        **metadata
    ) -> FlowEdge:
        """Add an edge between nodes."""
        edge = FlowEdge(
            source=source,
            target=target,
            label=label,
            status=status,
            metadata=metadata
        )
        self.edges.append(edge)
        self._update_flow_data()
        return edge

    def update_node_status(self, node_id: str, status: str, **metadata):
        """Update node status and metadata."""
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            self.nodes[node_id].metadata.update(metadata)
            self._update_flow_data()

    def update_edge_status(self, source: str, target: str, status: str):
        """Update edge status."""
        for edge in self.edges:
            if edge.source == source and edge.target == target:
                edge.status = status
                self._update_flow_data()
                break

    # ========================================================================
    # Request Tracking
    # ========================================================================

    def track_request(
        self,
        query: str,
        domain: str,
        model: str,
        latency_ms: float,
        success: bool,
        correlation_id: str
    ):
        """Track a request through the system."""
        # Update metrics
        self.current_metrics['total_requests'] += 1
        if success:
            self.current_metrics['successful_requests'] += 1
        else:
            self.current_metrics['failed_requests'] += 1

        self.current_metrics['latencies'].append(latency_ms)
        self.current_metrics['active_domains'].add(domain)
        self.current_metrics['active_models'].add(model)

        # Update routing distribution
        if domain not in self.current_metrics['routing_distribution']:
            self.current_metrics['routing_distribution'][domain] = 0
        self.current_metrics['routing_distribution'][domain] += 1

        # Create flow visualization for this request
        self._create_request_flow(query, domain, model, success, correlation_id)

        # Take metrics snapshot every 10 requests
        if self.current_metrics['total_requests'] % 10 == 0:
            self._take_metrics_snapshot()

    def _create_request_flow(
        self,
        query: str,
        domain: str,
        model: str,
        success: bool,
        correlation_id: str
    ):
        """Create flow visualization for a single request."""
        # Query node
        query_id = f"{correlation_id}_query"
        self.add_node(
            query_id,
            'query',
            query[:50] + "..." if len(query) > 50 else query,
            status='completed',
            query=query
        )

        # Router node
        router_id = f"{correlation_id}_router"
        self.add_node(
            router_id,
            'router',
            'TinyBERT Router',
            status='completed'
        )
        self.add_edge(query_id, router_id, 'classify')

        # Domain node
        domain_id = f"{correlation_id}_domain"
        self.add_node(
            domain_id,
            'domain',
            f'{domain.title()} Domain',
            status='completed',
            domain=domain
        )
        self.add_edge(router_id, domain_id, f'route to {domain}')

        # Model node
        model_id = f"{correlation_id}_model"
        self.add_node(
            model_id,
            'model',
            model.split('/')[-1] if '/' in model else model,
            status='completed',
            model=model
        )
        self.add_edge(domain_id, model_id, 'execute')

        # Response node
        response_id = f"{correlation_id}_response"
        self.add_node(
            response_id,
            'response',
            'Response' if success else 'Error',
            status='completed' if success else 'error'
        )
        self.add_edge(model_id, response_id, 'generate')

    # ========================================================================
    # Metrics Tracking
    # ========================================================================

    def _take_metrics_snapshot(self):
        """Take a snapshot of current metrics."""
        snapshot = MetricSnapshot(
            timestamp=time.time(),
            total_requests=self.current_metrics['total_requests'],
            successful_requests=self.current_metrics['successful_requests'],
            failed_requests=self.current_metrics['failed_requests'],
            avg_latency_ms=sum(self.current_metrics['latencies']) / len(self.current_metrics['latencies'])
                if self.current_metrics['latencies'] else 0.0,
            active_domains=list(self.current_metrics['active_domains']),
            active_models=list(self.current_metrics['active_models']),
            routing_distribution=dict(self.current_metrics['routing_distribution'])
        )
        self.metrics_history.append(snapshot)
        self._update_metrics_data()

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return {
            'session_id': self.session_id,
            'uptime_seconds': time.time() - self.start_time,
            'total_requests': self.current_metrics['total_requests'],
            'successful_requests': self.current_metrics['successful_requests'],
            'failed_requests': self.current_metrics['failed_requests'],
            'success_rate': (
                self.current_metrics['successful_requests'] / self.current_metrics['total_requests']
                if self.current_metrics['total_requests'] > 0 else 0.0
            ),
            'avg_latency_ms': (
                sum(self.current_metrics['latencies']) / len(self.current_metrics['latencies'])
                if self.current_metrics['latencies'] else 0.0
            ),
            'active_domains': list(self.current_metrics['active_domains']),
            'active_models': list(self.current_metrics['active_models']),
            'routing_distribution': dict(self.current_metrics['routing_distribution']),
        }

    # ========================================================================
    # Data Export for Visualization
    # ========================================================================

    def _update_flow_data(self):
        """Export flow data to JSON for D3.js visualization."""
        flow_data = {
            'nodes': [asdict(node) for node in self.nodes.values()],
            'edges': [asdict(edge) for edge in self.edges],
            'timestamp': time.time()
        }

        output_file = self.output_dir / f"{self.session_id}_flow.json"
        with open(output_file, 'w') as f:
            json.dump(flow_data, f, indent=2)

    def _update_metrics_data(self):
        """Export metrics data to JSON for visualization."""
        metrics_data = {
            'current': self.get_current_metrics(),
            'history': [asdict(snapshot) for snapshot in self.metrics_history],
            'timestamp': time.time()
        }

        output_file = self.output_dir / f"{self.session_id}_metrics.json"
        with open(output_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)

    def generate_html_dashboard(self) -> str:
        """
        Generate standalone HTML dashboard with D3.js visualizations.

        Returns:
            Path to generated HTML file
        """
        html_content = self._get_dashboard_html_template()

        output_file = self.output_dir / f"{self.session_id}_dashboard.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def _get_dashboard_html_template(self) -> str:
        """Get HTML template for dashboard."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDSA Enhanced Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .panel {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}

        .panel:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}

        .panel h2 {{
            color: #667eea;
            margin-bottom: 16px;
            font-size: 1.5rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 8px;
        }}

        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }}

        .metric:last-child {{
            border-bottom: none;
        }}

        .metric-label {{
            font-weight: 500;
            color: #555;
        }}

        .metric-value {{
            font-size: 1.2rem;
            font-weight: bold;
            color: #667eea;
        }}

        .metric-value.success {{
            color: #10b981;
        }}

        .metric-value.error {{
            color: #ef4444;
        }}

        #flow-chart {{
            width: 100%;
            height: 600px;
            border: 1px solid #eee;
            border-radius: 8px;
            background: #f9fafb;
        }}

        .node {{
            cursor: pointer;
        }}

        .node circle {{
            fill: #667eea;
            stroke: #fff;
            stroke-width: 2px;
            transition: all 0.3s;
        }}

        .node:hover circle {{
            fill: #764ba2;
            r: 12;
        }}

        .node text {{
            font-size: 12px;
            fill: #333;
        }}

        .link {{
            fill: none;
            stroke: #999;
            stroke-width: 2px;
        }}

        .link.active {{
            stroke: #667eea;
            stroke-width: 3px;
        }}

        .refresh-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s;
        }}

        .refresh-btn:hover {{
            background: #764ba2;
        }}

        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .status-indicator.active {{
            background: #10b981;
            box-shadow: 0 0 10px #10b981;
        }}

        .status-indicator.inactive {{
            background: #ef4444;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 MDSA Enhanced Dashboard</h1>

        <div class="dashboard-grid">
            <!-- Metrics Panel -->
            <div class="panel">
                <h2>📊 System Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Status</span>
                    <span class="metric-value">
                        <span class="status-indicator active"></span>
                        Online
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Requests</span>
                    <span class="metric-value" id="total-requests">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Success Rate</span>
                    <span class="metric-value success" id="success-rate">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Latency</span>
                    <span class="metric-value" id="avg-latency">0ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Domains</span>
                    <span class="metric-value" id="active-domains">0</span>
                </div>
            </div>

            <!-- Routing Distribution Panel -->
            <div class="panel">
                <h2>🔀 Routing Distribution</h2>
                <div id="routing-chart" style="height: 200px;"></div>
            </div>
        </div>

        <!-- Flow Visualization Panel -->
        <div class="panel">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2>🌊 Orchestration Flow</h2>
                <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
            </div>
            <div id="flow-chart"></div>
        </div>
    </div>

    <script>
        const sessionId = "{self.session_id}";

        // Load and update data
        async function loadData() {{
            try {{
                // Load metrics
                const metricsResponse = await fetch(`${{sessionId}}_metrics.json`);
                const metricsData = await metricsResponse.json();
                updateMetrics(metricsData.current);

                // Load flow
                const flowResponse = await fetch(`${{sessionId}}_flow.json`);
                const flowData = await flowResponse.json();
                updateFlowChart(flowData);
            }} catch (error) {{
                console.error('Error loading data:', error);
            }}
        }}

        function updateMetrics(metrics) {{
            document.getElementById('total-requests').textContent = metrics.total_requests;
            document.getElementById('success-rate').textContent =
                (metrics.success_rate * 100).toFixed(1) + '%';
            document.getElementById('avg-latency').textContent =
                metrics.avg_latency_ms.toFixed(1) + 'ms';
            document.getElementById('active-domains').textContent =
                metrics.active_domains.length;

            updateRoutingChart(metrics.routing_distribution);
        }}

        function updateRoutingChart(distribution) {{
            const data = Object.entries(distribution).map(([domain, count]) => ({{
                domain, count
            }}));

            const margin = {{ top: 20, right: 20, bottom: 40, left: 40 }};
            const width = document.getElementById('routing-chart').offsetWidth - margin.left - margin.right;
            const height = 200 - margin.top - margin.bottom;

            d3.select('#routing-chart').selectAll('*').remove();

            const svg = d3.select('#routing-chart')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom)
                .append('g')
                .attr('transform', `translate(${{margin.left}},${{margin.top}})`);

            const x = d3.scaleBand()
                .domain(data.map(d => d.domain))
                .range([0, width])
                .padding(0.3);

            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.count) || 1])
                .range([height, 0]);

            svg.selectAll('.bar')
                .data(data)
                .enter()
                .append('rect')
                .attr('class', 'bar')
                .attr('x', d => x(d.domain))
                .attr('y', d => y(d.count))
                .attr('width', x.bandwidth())
                .attr('height', d => height - y(d.count))
                .attr('fill', '#667eea')
                .attr('rx', 4);

            svg.append('g')
                .attr('transform', `translate(0,${{height}})`)
                .call(d3.axisBottom(x));

            svg.append('g')
                .call(d3.axisLeft(y));
        }}

        function updateFlowChart(flowData) {{
            const width = document.getElementById('flow-chart').offsetWidth;
            const height = 600;

            d3.select('#flow-chart').selectAll('*').remove();

            const svg = d3.select('#flow-chart')
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            // Create simple flow visualization
            const nodes = flowData.nodes.slice(-20); // Show last 20 nodes
            const edges = flowData.edges.filter(e =>
                nodes.find(n => n.id === e.source) && nodes.find(n => n.id === e.target)
            );

            // Position nodes in layers
            const nodesByType = {{}};
            nodes.forEach(node => {{
                if (!nodesByType[node.type]) nodesByType[node.type] = [];
                nodesByType[node.type].push(node);
            }});

            const types = ['query', 'router', 'domain', 'model', 'response'];
            const layerWidth = width / (types.length + 1);

            nodes.forEach(node => {{
                const typeIndex = types.indexOf(node.type);
                const typeNodes = nodesByType[node.type] || [];
                const indexInType = typeNodes.indexOf(node);

                node.x = layerWidth * (typeIndex + 1);
                node.y = (height / (typeNodes.length + 1)) * (indexInType + 1);
            }});

            // Draw edges
            svg.selectAll('.link')
                .data(edges)
                .enter()
                .append('line')
                .attr('class', 'link')
                .attr('x1', d => {{ const s = nodes.find(n => n.id === d.source); return s ? s.x : 0; }})
                .attr('y1', d => {{ const s = nodes.find(n => n.id === d.source); return s ? s.y : 0; }})
                .attr('x2', d => {{ const t = nodes.find(n => n.id === d.target); return t ? t.x : 0; }})
                .attr('y2', d => {{ const t = nodes.find(n => n.id === d.target); return t ? t.y : 0; }})
                .attr('stroke', '#999')
                .attr('stroke-width', 2);

            // Draw nodes
            const nodeGroups = svg.selectAll('.node')
                .data(nodes)
                .enter()
                .append('g')
                .attr('class', 'node')
                .attr('transform', d => `translate(${{d.x}},${{d.y}})`);

            nodeGroups.append('circle')
                .attr('r', 8)
                .attr('fill', d => {{
                    switch(d.type) {{
                        case 'query': return '#3b82f6';
                        case 'router': return '#8b5cf6';
                        case 'domain': return '#10b981';
                        case 'model': return '#f59e0b';
                        case 'response': return d.status === 'error' ? '#ef4444' : '#06b6d4';
                        default: return '#667eea';
                    }}
                }})
                .attr('stroke', '#fff')
                .attr('stroke-width', 2);

            nodeGroups.append('text')
                .attr('dy', -12)
                .attr('text-anchor', 'middle')
                .attr('font-size', '10px')
                .text(d => d.label.length > 15 ? d.label.substring(0, 15) + '...' : d.label);
        }}

        // Auto-refresh every 5 seconds
        setInterval(loadData, 5000);
        loadData();
    </script>
</body>
</html>"""

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def clear(self):
        """Clear all tracked data."""
        self.nodes.clear()
        self.edges.clear()
        self.metrics_history.clear()
        self.current_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'latencies': [],
            'active_domains': set(),
            'active_models': set(),
            'routing_distribution': {},
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time,
            'nodes_count': len(self.nodes),
            'edges_count': len(self.edges),
            'metrics_snapshots': len(self.metrics_history),
            'current_metrics': self.get_current_metrics(),
        }


# ============================================================================
# Demo
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MDSA Enhanced Dashboard - Demo")
    print("=" * 60)

    # Create dashboard
    dashboard = EnhancedDashboard()

    # Simulate some requests
    print("\nSimulating requests...")

    sample_requests = [
        ("How do I transfer money?", "finance", "microsoft/phi-2", 145.5, True),
        ("What are flu symptoms?", "medical", "microsoft/phi-2", 132.3, True),
        ("Reset my password", "support", "microsoft/phi-2", 98.7, True),
        ("Fix login error", "technical", "microsoft/phi-2", 156.2, True),
        ("Account balance?", "finance", "microsoft/phi-2", 87.4, True),
        ("Refund status?", "support", "microsoft/phi-2", 102.1, True),
        ("Diabetes treatment", "medical", "microsoft/phi-2", 178.9, True),
        ("Software crash", "technical", "microsoft/phi-2", 143.6, True),
    ]

    for i, (query, domain, model, latency, success) in enumerate(sample_requests):
        correlation_id = f"req_{i+1}"
        dashboard.track_request(query, domain, model, latency, success, correlation_id)
        print(f"  [OK] Tracked: {query[:40]}... -> {domain}")

    # Generate HTML dashboard
    print("\nGenerating HTML dashboard...")
    html_file = dashboard.generate_html_dashboard()
    print(f"  [OK] Dashboard saved: {html_file}")

    # Show stats
    print("\nDashboard Statistics:")
    stats = dashboard.get_stats()
    print(f"  - Session ID: {stats['session_id']}")
    print(f"  - Total Requests: {stats['current_metrics']['total_requests']}")
    print(f"  - Success Rate: {stats['current_metrics']['success_rate']*100:.1f}%")
    print(f"  - Avg Latency: {stats['current_metrics']['avg_latency_ms']:.1f}ms")
    print(f"  - Active Domains: {len(stats['current_metrics']['active_domains'])}")
    print(f"  - Flow Nodes: {stats['nodes_count']}")
    print(f"  - Flow Edges: {stats['edges_count']}")

    print(f"\n[SUCCESS] Open {html_file} in your browser to view the dashboard!")
    print("=" * 60)
