/**
 * MDSA Dashboard - Common JavaScript Utilities
 */

// Format timestamp to human-readable format
function formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

// Format uptime in seconds to human-readable format
function formatUptime(seconds) {
    if (seconds < 60) {
        return `${Math.floor(seconds)}s`;
    } else if (seconds < 3600) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}m ${secs}s`;
    } else if (seconds < 86400) {
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${mins}m`;
    } else {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        return `${days}d ${hours}h`;
    }
}

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format bytes to human-readable format
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Show/hide elements
function show(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.classList.remove('hidden');
}

function hide(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.classList.add('hidden');
}

// Add fade-in animation
function fadeIn(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.classList.add('fade-in');
}

// Show notification banner
function showNotification(message, type = 'info') {
    const banner = document.getElementById('statusBanner');
    if (!banner) return;

    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : '🔄';
    banner.innerHTML = `
        <div class="status-icon">${icon}</div>
        <div class="status-text">${message}</div>
    `;

    banner.style.display = 'flex';
    fadeIn('statusBanner');

    // Auto-hide after 5 seconds
    setTimeout(() => {
        banner.style.display = 'none';
    }, 5000);
}

// Safe element update
function updateElement(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = value;
        fadeIn(id);
    }
}

// Safe HTML update
function updateHTML(id, html) {
    const el = document.getElementById(id);
    if (el) {
        el.innerHTML = html;
        fadeIn(id);
    }
}

// Log to console with timestamp
function log(message, level = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = `[MDSA Dashboard ${timestamp}]`;

    if (level === 'error') {
        console.error(prefix, message);
    } else if (level === 'warn') {
        console.warn(prefix, message);
    } else {
        console.log(prefix, message);
    }
}

// Export utilities
window.MDSAUtils = {
    formatTimestamp,
    formatUptime,
    formatNumber,
    formatBytes,
    show,
    hide,
    fadeIn,
    showNotification,
    updateElement,
    updateHTML,
    log
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    log('MDSA Dashboard initialized');
});
