/**
 * MDSA Dashboard - D3.js Visualizations
 *
 * Provides interactive visualizations for:
 * - Domain routing flow (Sankey diagram)
 * - Latency heatmap
 * - RAG statistics
 * - Request timeline
 * - Domain distribution
 */

// ============================================================================
// 1. SANKEY DIAGRAM - Query Routing Flow
// ============================================================================

function createSankeyDiagram(containerId, data) {
    const container = d3.select(`#${containerId}`);
    const width = container.node().getBoundingClientRect().width;
    const height = 400;

    // Clear previous content
    container.html("");

    // Check for empty data
    if (!data || !data.domains || data.domains.length === 0 || !data.total_requests || data.total_requests === 0) {
        container.html(`
            <div style="text-align: center; padding: 100px 20px; color: #888;">
                <p style="font-size: 18px; margin-bottom: 15px;">📊 No query data yet</p>
                <p style="font-size: 14px; margin-bottom: 20px;">Process some queries or generate demo data to see the routing flow</p>
                <button onclick="generateDemoData()" style="background: linear-gradient(135deg, #4CAF50, #45a049); color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; transition: transform 0.2s;">
                    🎲 Generate Demo Data
                </button>
            </div>
        `);
        return;
    }

    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height);

    // Create nodes and links for Sankey
    const nodes = [
        { name: "User Queries", id: 0 },
        { name: "TinyBERT Router", id: 1 },
        ...data.domains.map((d, i) => ({ name: d.name, id: i + 2 })),
        { name: "Successful Responses", id: data.domains.length + 2 },
        { name: "Escalated", id: data.domains.length + 3 }
    ];

    const links = [];

    // Queries to Router
    links.push({
        source: 0,
        target: 1,
        value: data.total_requests
    });

    // Router to Domains
    data.domains.forEach((domain, i) => {
        links.push({
            source: 1,
            target: i + 2,
            value: domain.requests
        });

        // Domains to Success/Escalation
        if (domain.success_rate > 0.5) {
            links.push({
                source: i + 2,
                target: data.domains.length + 2,
                value: domain.requests * domain.success_rate
            });
        }
        if (domain.success_rate < 1.0) {
            links.push({
                source: i + 2,
                target: data.domains.length + 3,
                value: domain.requests * (1 - domain.success_rate)
            });
        }
    });

    // D3 Sankey layout
    const sankey = d3.sankey()
        .nodeWidth(15)
        .nodePadding(10)
        .extent([[1, 1], [width - 1, height - 5]]);

    const { nodes: sankeyNodes, links: sankeyLinks } = sankey({
        nodes: nodes.map(d => Object.assign({}, d)),
        links: links.map(d => Object.assign({}, d))
    });

    // Draw links
    svg.append("g")
        .selectAll("path")
        .data(sankeyLinks)
        .join("path")
        .attr("d", d3.sankeyLinkHorizontal())
        .attr("stroke", d => d.source.name.includes("Router") ? "#4CAF50" : "#2196F3")
        .attr("stroke-width", d => Math.max(1, d.width))
        .attr("fill", "none")
        .attr("opacity", 0.5)
        .append("title")
        .text(d => `${d.source.name} → ${d.target.name}\n${d.value} requests`);

    // Draw nodes
    svg.append("g")
        .selectAll("rect")
        .data(sankeyNodes)
        .join("rect")
        .attr("x", d => d.x0)
        .attr("y", d => d.y0)
        .attr("height", d => d.y1 - d.y0)
        .attr("width", d => d.x1 - d.x0)
        .attr("fill", d => {
            if (d.name.includes("Escalated")) return "#f44336";
            if (d.name.includes("Success")) return "#4CAF50";
            if (d.name.includes("Router")) return "#FF9800";
            return "#2196F3";
        })
        .append("title")
        .text(d => `${d.name}\n${d.value} requests`);

    // Add labels
    svg.append("g")
        .selectAll("text")
        .data(sankeyNodes)
        .join("text")
        .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
        .attr("y", d => (d.y1 + d.y0) / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
        .text(d => d.name)
        .style("fill", "#fff")
        .style("font-size", "12px");
}

// ============================================================================
// 2. LATENCY HEATMAP
// ============================================================================

function createLatencyHeatmap(containerId, data) {
    const container = d3.select(`#${containerId}`);
    const width = container.node().getBoundingClientRect().width;
    const height = 300;

    container.html("");

    // Check for empty data
    if (!data || !data.latencies || data.latencies.length === 0 || !data.domains || data.domains.length === 0) {
        container.html(`
            <div style="text-align: center; padding: 80px 20px; color: #888;">
                <p style="font-size: 16px; margin-bottom: 10px;">🌡️ No latency data available</p>
                <p style="font-size: 13px;">Start processing queries to see domain latency heatmap</p>
            </div>
        `);
        return;
    }

    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height);

    const margin = { top: 50, right: 30, bottom: 50, left: 120 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const x = d3.scaleBand()
        .domain(data.time_buckets)
        .range([0, chartWidth])
        .padding(0.05);

    const y = d3.scaleBand()
        .domain(data.domains)
        .range([0, chartHeight])
        .padding(0.05);

    // Safe max calculation
    const maxLatency = d3.max(data.latencies.flat()) || 100;

    const colorScale = d3.scaleSequential()
        .domain([0, maxLatency])
        .interpolator(d3.interpolateRdYlGn);

    // Draw cells
    data.domains.forEach((domain, i) => {
        data.time_buckets.forEach((bucket, j) => {
            const latency = data.latencies[i][j];

            g.append("rect")
                .attr("x", x(bucket))
                .attr("y", y(domain))
                .attr("width", x.bandwidth())
                .attr("height", y.bandwidth())
                .attr("fill", colorScale(latency))
                .attr("stroke", "#1a1a1a")
                .attr("stroke-width", 1)
                .on("mouseover", function(event) {
                    d3.select(this).attr("stroke", "#fff").attr("stroke-width", 2);
                    showTooltip(event, `${domain}<br>${bucket}<br>${latency.toFixed(0)}ms`);
                })
                .on("mouseout", function() {
                    d3.select(this).attr("stroke", "#1a1a1a").attr("stroke-width", 1);
                    hideTooltip();
                });
        });
    });

    // X axis
    g.append("g")
        .attr("transform", `translate(0,${chartHeight})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .style("fill", "#fff");

    // Y axis
    g.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .style("fill", "#fff");

    // Title
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 20)
        .attr("text-anchor", "middle")
        .style("fill", "#4CAF50")
        .style("font-size", "16px")
        .text("Domain Latency Heatmap (ms)");
}

// ============================================================================
// 3. RAG STATISTICS BAR CHART
// ============================================================================

function createRAGChart(containerId, data) {
    const container = d3.select(`#${containerId}`);
    const width = container.node().getBoundingClientRect().width;
    const height = 300;

    container.html("");

    // Check for empty data
    if (!data || ((!data.global_docs || data.global_docs === 0) && (!data.local_docs || Object.keys(data.local_docs).length === 0))) {
        container.html(`
            <div style="text-align: center; padding: 80px 20px; color: #888;">
                <p style="font-size: 16px; margin-bottom: 10px;">📚 No RAG documents yet</p>
                <p style="font-size: 13px;">Upload documents to see distribution across global and local RAG</p>
            </div>
        `);
        return;
    }

    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height);

    const margin = { top: 40, right: 30, bottom: 80, left: 60 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Prepare data
    const ragData = [
        { category: "Global RAG", count: data.global_docs },
        ...Object.entries(data.local_docs).map(([domain, count]) => ({
            category: domain,
            count: count
        }))
    ];

    // Scales
    const x = d3.scaleBand()
        .domain(ragData.map(d => d.category))
        .range([0, chartWidth])
        .padding(0.2);

    const y = d3.scaleLinear()
        .domain([0, d3.max(ragData, d => d.count)])
        .range([chartHeight, 0]);

    // Bars
    g.selectAll("rect")
        .data(ragData)
        .join("rect")
        .attr("x", d => x(d.category))
        .attr("y", d => y(d.count))
        .attr("width", x.bandwidth())
        .attr("height", d => chartHeight - y(d.count))
        .attr("fill", (d, i) => i === 0 ? "#9C27B0" : "#2196F3")
        .on("mouseover", function(event, d) {
            d3.select(this).attr("fill", "#4CAF50");
            showTooltip(event, `${d.category}<br>${d.count} documents`);
        })
        .on("mouseout", function(event, d) {
            const i = ragData.indexOf(d);
            d3.select(this).attr("fill", i === 0 ? "#9C27B0" : "#2196F3");
            hideTooltip();
        });

    // Value labels on bars
    g.selectAll("text.value")
        .data(ragData)
        .join("text")
        .attr("class", "value")
        .attr("x", d => x(d.category) + x.bandwidth() / 2)
        .attr("y", d => y(d.count) - 5)
        .attr("text-anchor", "middle")
        .style("fill", "#fff")
        .style("font-size", "12px")
        .text(d => d.count);

    // X axis
    g.append("g")
        .attr("transform", `translate(0,${chartHeight})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end")
        .style("fill", "#fff");

    // Y axis
    g.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .style("fill", "#fff");

    // Title
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 20)
        .attr("text-anchor", "middle")
        .style("fill", "#4CAF50")
        .style("font-size", "16px")
        .text("RAG Document Distribution");
}

// ============================================================================
// 4. REQUEST TIMELINE (Line Chart)
// ============================================================================

function createTimelineChart(containerId, data) {
    const container = d3.select(`#${containerId}`);
    const width = container.node().getBoundingClientRect().width;
    const height = 200;

    container.html("");

    // Check for empty data
    if (!data || !Array.isArray(data) || data.length === 0) {
        container.html(`
            <div style="text-align: center; padding: 60px 20px; color: #888;">
                <p style="font-size: 14px;">⏱️ No request timeline data</p>
            </div>
        `);
        return;
    }

    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height);

    const margin = { top: 30, right: 30, bottom: 40, left: 50 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const x = d3.scaleTime()
        .domain(d3.extent(data.timeline, d => new Date(d.timestamp)))
        .range([0, chartWidth]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data.timeline, d => d.count)])
        .range([chartHeight, 0]);

    // Line generator
    const line = d3.line()
        .x(d => x(new Date(d.timestamp)))
        .y(d => y(d.count))
        .curve(d3.curveMonotoneX);

    // Draw line
    g.append("path")
        .datum(data.timeline)
        .attr("fill", "none")
        .attr("stroke", "#4CAF50")
        .attr("stroke-width", 2)
        .attr("d", line);

    // Draw points
    g.selectAll("circle")
        .data(data.timeline)
        .join("circle")
        .attr("cx", d => x(new Date(d.timestamp)))
        .attr("cy", d => y(d.count))
        .attr("r", 4)
        .attr("fill", "#4CAF50")
        .on("mouseover", function(event, d) {
            d3.select(this).attr("r", 6);
            showTooltip(event, `${new Date(d.timestamp).toLocaleTimeString()}<br>${d.count} requests`);
        })
        .on("mouseout", function() {
            d3.select(this).attr("r", 4);
            hideTooltip();
        });

    // X axis
    g.append("g")
        .attr("transform", `translate(0,${chartHeight})`)
        .call(d3.axisBottom(x).ticks(6))
        .selectAll("text")
        .style("fill", "#fff");

    // Y axis
    g.append("g")
        .call(d3.axisLeft(y).ticks(5))
        .selectAll("text")
        .style("fill", "#fff");

    // Title
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 15)
        .attr("text-anchor", "middle")
        .style("fill", "#4CAF50")
        .style("font-size", "14px")
        .text("Requests Over Time");
}

// ============================================================================
// 5. DOMAIN DISTRIBUTION PIE CHART
// ============================================================================

function createDomainPieChart(containerId, data) {
    const container = d3.select(`#${containerId}`);
    const width = container.node().getBoundingClientRect().width;
    const height = 300;

    container.html("");

    // Check for empty data
    if (!data || !Array.isArray(data) || data.length === 0) {
        container.html(`
            <div style="text-align: center; padding: 80px 20px; color: #888;">
                <p style="font-size: 16px; margin-bottom: 10px;">🥧 No domain request data</p>
                <p style="font-size: 13px;">Process queries to see distribution across domains</p>
            </div>
        `);
        return;
    }

    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height);

    const radius = Math.min(width, height) / 2 - 40;

    const g = svg.append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    const color = d3.scaleOrdinal()
        .domain(data.map(d => d.domain))
        .range(["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336", "#00BCD4"]);

    const pie = d3.pie()
        .value(d => d.requests)
        .sort(null);

    const arc = d3.arc()
        .innerRadius(0)
        .outerRadius(radius);

    const labelArc = d3.arc()
        .innerRadius(radius * 0.6)
        .outerRadius(radius * 0.6);

    // Draw slices
    const slices = g.selectAll("path")
        .data(pie(data))
        .join("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data.domain))
        .attr("stroke", "#1a1a1a")
        .attr("stroke-width", 2)
        .on("mouseover", function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr("transform", function() {
                    const [x, y] = arc.centroid(d);
                    return `translate(${x * 0.1},${y * 0.1})`;
                });
            showTooltip(event, `${d.data.domain}<br>${d.data.requests} requests (${((d.data.requests / d3.sum(data, dd => dd.requests)) * 100).toFixed(1)}%)`);
        })
        .on("mouseout", function() {
            d3.select(this)
                .transition()
                .duration(200)
                .attr("transform", "translate(0,0)");
            hideTooltip();
        });

    // Add labels
    g.selectAll("text")
        .data(pie(data))
        .join("text")
        .attr("transform", d => `translate(${labelArc.centroid(d)})`)
        .attr("text-anchor", "middle")
        .style("fill", "#fff")
        .style("font-size", "12px")
        .text(d => {
            const percent = (d.data.requests / d3.sum(data, dd => dd.requests)) * 100;
            return percent > 5 ? d.data.domain.split('_')[0] : '';
        });

    // Title
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 20)
        .attr("text-anchor", "middle")
        .style("fill", "#4CAF50")
        .style("font-size", "16px")
        .text("Domain Request Distribution");
}

// ============================================================================
// TOOLTIP HELPERS
// ============================================================================

function showTooltip(event, html) {
    const tooltip = d3.select("body").selectAll(".d3-tooltip").data([null]);

    tooltip.enter()
        .append("div")
        .attr("class", "d3-tooltip")
        .merge(tooltip)
        .html(html)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 10) + "px")
        .style("opacity", 1);
}

function hideTooltip() {
    d3.select(".d3-tooltip")
        .style("opacity", 0);
}

// ============================================================================
// INITIALIZE ALL VISUALIZATIONS
// ============================================================================

async function initializeDashboard() {
    try {
        // Fetch data from API
        const response = await fetch('/api/visualization-data');
        const data = await response.json();

        // Create all visualizations
        if (data.sankey) {
            createSankeyDiagram('sankey-container', data.sankey);
        }

        if (data.heatmap) {
            createLatencyHeatmap('heatmap-container', data.heatmap);
        }

        if (data.rag) {
            createRAGChart('rag-container', data.rag);
        }

        if (data.timeline) {
            createTimelineChart('timeline-container', data.timeline);
        }

        if (data.pie) {
            createDomainPieChart('pie-container', data.pie);
        }

    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Generate demo data for testing visualizations
async function generateDemoData() {
    try {
        console.log('Generating demo data...');

        const response = await fetch('/api/admin/generate-demo-data', {
            method: 'POST',
            credentials: 'include'
        });

        const result = await response.json();

        if (response.ok) {
            console.log(`Demo data generated: ${result.generated} samples`);

            // Show success message
            alert(`✅ Generated ${result.generated} sample queries! Charts will refresh in a moment.`);

            // Reload charts immediately
            await initializeDashboard();
        } else {
            console.error('Error generating demo data:', result);
            alert(`❌ Error: ${result.detail || 'Failed to generate demo data'}`);
        }
    } catch (error) {
        console.error('Error generating demo data:', error);
        alert(`❌ Error generating demo data: ${error.message}`);
    }
}

// Initialize dashboard on page load
initializeDashboard();

// Auto-refresh every 30 seconds
setInterval(initializeDashboard, 30000);
