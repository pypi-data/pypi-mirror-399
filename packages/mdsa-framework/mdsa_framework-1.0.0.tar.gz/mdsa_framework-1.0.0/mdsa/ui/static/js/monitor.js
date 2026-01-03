/**
 * MDSA Dashboard - Monitor Page JavaScript
 *
 * Handles real-time metrics updates and UI interactions
 */

const UTILS = window.MDSAUtils;

// State
let autoRefreshEnabled = true;
let refreshInterval = null;
const REFRESH_INTERVAL_MS = 5000; // 5 seconds

// Fetch metrics from API
async function fetchMetrics() {
    try {
        const response = await fetch('/api/metrics');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        UTILS.log(`Failed to fetch metrics: ${error.message}`, 'error');
        UTILS.showNotification('Failed to fetch metrics', 'error');
        return null;
    }
}

// Update system overview
function updateSystemOverview(system, uptime) {
    if (!system) return;

    // Status
    const statusText = system.status === 'running' ? '🟢 Running' : '🔴 Stopped';
    UTILS.updateElement('systemStatus', statusText);

    // Uptime
    UTILS.updateElement('systemUptime', UTILS.formatUptime(uptime));

    // CPU Cores
    UTILS.updateElement('cpuCores', system.cpu_cores > 0 ? `${system.cpu_cores} cores` : 'N/A');

    // GPU
    const gpuText = system.has_gpu ? `✅ ${system.gpu_type}` : '❌ None';
    UTILS.updateElement('gpuType', gpuText);
}

// Update request statistics
function updateRequestStats(requests) {
    if (!requests) return;

    UTILS.updateElement('totalRequests', UTILS.formatNumber(requests.total));
    UTILS.updateElement('successRequests', UTILS.formatNumber(requests.success));
    UTILS.updateElement('errorRequests', UTILS.formatNumber(requests.errors));
    UTILS.updateElement('successRate', `${requests.success_rate.toFixed(1)}%`);
}

// Update performance metrics
function updatePerformanceMetrics(performance) {
    if (!performance) return;

    UTILS.updateElement('avgLatency', `${performance.avg_latency_ms.toFixed(1)}ms`);
    UTILS.updateElement('p50Latency', `${performance.p50_latency_ms.toFixed(1)}ms`);
    UTILS.updateElement('p95Latency', `${performance.p95_latency_ms.toFixed(1)}ms`);
    UTILS.updateElement('throughput', `${performance.throughput_rps.toFixed(2)} req/s`);
}

// Update models table
function updateModelsTable(models) {
    if (!models) return;

    // Update summary
    UTILS.updateElement('modelCount', models.count);
    UTILS.updateElement('maxModels', models.max_models);
    UTILS.updateElement('totalMemory', models.total_memory_mb.toFixed(1));

    // Update table
    const tbody = document.getElementById('modelsTable');
    if (!tbody) return;

    if (models.loaded.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No models loaded</td></tr>';
        return;
    }

    // Build table rows
    let html = '';
    for (const model of models.loaded) {
        const lastUsed = formatTimeAgo(model.last_used);
        html += `
            <tr>
                <td><code>${escapeHtml(model.id)}</code></td>
                <td>${escapeHtml(model.name)}</td>
                <td>${model.memory_mb.toFixed(1)} MB</td>
                <td>${UTILS.formatNumber(model.use_count)}</td>
                <td>${lastUsed}</td>
            </tr>
        `;
    }

    tbody.innerHTML = html;
}

// Format time ago
function formatTimeAgo(timestamp) {
    const now = Date.now() / 1000;
    const diff = now - timestamp;

    if (diff < 60) {
        return 'Just now';
    } else if (diff < 3600) {
        const mins = Math.floor(diff / 60);
        return `${mins} min${mins > 1 ? 's' : ''} ago`;
    } else if (diff < 86400) {
        const hours = Math.floor(diff / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        const days = Math.floor(diff / 86400);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
}

// Escape HTML to prevent XSS
function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') return unsafe;
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Update all metrics
async function updateMetrics() {
    UTILS.log('Updating metrics...');

    const metrics = await fetchMetrics();
    if (!metrics) {
        UTILS.showNotification('Failed to connect to MDSA framework', 'error');
        return;
    }

    // Update all sections
    updateSystemOverview(metrics.system, metrics.uptime_seconds);
    updateRequestStats(metrics.requests);
    updatePerformanceMetrics(metrics.performance);
    updateModelsTable(metrics.models);

    // Update last update time
    const now = new Date().toLocaleTimeString();
    UTILS.updateElement('lastUpdate', `Last update: ${now}`);
    UTILS.updateElement('footerTimestamp', now);

    // Show success notification on first load
    if (!window.metricsLoadedOnce) {
        UTILS.showNotification('Connected to MDSA framework', 'success');
        window.metricsLoadedOnce = true;
    }

    UTILS.log('Metrics updated successfully');
}

// Start auto-refresh
function startAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }

    refreshInterval = setInterval(() => {
        if (autoRefreshEnabled) {
            updateMetrics();
        }
    }, REFRESH_INTERVAL_MS);

    UTILS.log('Auto-refresh started');
}

// Stop auto-refresh
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
    UTILS.log('Auto-refresh stopped');
}

// Initialize monitor page
function initMonitor() {
    UTILS.log('Initializing monitor page...');

    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            UTILS.log('Manual refresh triggered');
            updateMetrics();
        });
    }

    // Auto-refresh toggle
    const autoRefreshCheckbox = document.getElementById('autoRefresh');
    if (autoRefreshCheckbox) {
        autoRefreshCheckbox.addEventListener('change', (e) => {
            autoRefreshEnabled = e.target.checked;
            UTILS.log(`Auto-refresh ${autoRefreshEnabled ? 'enabled' : 'disabled'}`);

            if (autoRefreshEnabled) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        });
    }

    // Initial load
    updateMetrics();

    // Start auto-refresh if enabled
    if (autoRefreshEnabled) {
        startAutoRefresh();
    }

    UTILS.log('Monitor page initialized');
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMonitor);
} else {
    initMonitor();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});
