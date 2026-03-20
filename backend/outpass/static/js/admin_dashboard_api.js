/**
 * Admin Dashboard API - JavaScript Fetch Example
 * 
 * This file demonstrates how to fetch and display admin dashboard statistics
 * using the JavaScript Fetch API.
 * 
 * API Endpoint: GET /api/admin-dashboard/stats/
 * 
 * JSON Response Structure:
 * {
 *     "success": true,
 *     "data": {
 *         "total_students": <int>,
 *         "total_out_students": <int>,
 *         "total_inside_students": <int>,
 *         "total_pending_requests": <int>
 *     }
 * }
 */

// Get CSRF token from cookie
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Fetch admin dashboard statistics
async function fetchAdminDashboardStats() {
    try {
        const response = await fetch('/api/admin-dashboard/stats/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'same-origin' // Include cookies for authenticated requests
        });

        const data = await response.json();

        if (data.success) {
            return data.data;
        } else {
            throw new Error(data.message || 'Failed to fetch dashboard statistics');
        }
    } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        throw error;
    }
}

// Update HTML elements with dashboard statistics
function updateDashboardUI(stats) {
    // Update each stat card
    const elements = {
        'total-students': stats.total_students,
        'total-out-students': stats.total_out_students,
        'total-inside-students': stats.total_inside_students,
        'total-pending-requests': stats.total_pending_requests
    };

    for (const [id, value] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
}

// Initialize dashboard on page load
async function initAdminDashboard() {
    const loadingElement = document.getElementById('loading');
    const errorElement = document.getElementById('error-message');
    const statsContainer = document.getElementById('stats-container');

    try {
        // Show loading state
        if (loadingElement) loadingElement.style.display = 'block';
        if (errorElement) errorElement.style.display = 'none';
        
        // Fetch statistics
        const stats = await fetchAdminDashboardStats();
        
        // Update UI
        updateDashboardUI(stats);
        
        // Hide loading, show stats
        if (loadingElement) loadingElement.style.display = 'none';
        if (statsContainer) statsContainer.style.display = 'grid';
        
    } catch (error) {
        // Show error message
        if (loadingElement) loadingElement.style.display = 'none';
        if (errorElement) {
            errorElement.textContent = error.message || 'Failed to load dashboard statistics';
            errorElement.style.display = 'block';
        }
    }
}

// Auto-refresh dashboard every 30 seconds
function startAutoRefresh(intervalMs = 30000) {
    // Initial load
    initAdminDashboard();
    
    // Set up auto-refresh
    return setInterval(() => {
        initAdminDashboard();
    }, intervalMs);
}

// Example: Manual refresh button handler
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refresh-stats-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            refreshBtn.disabled = true;
            refreshBtn.textContent = 'Refreshing...';
            
            try {
                await initAdminDashboard();
            } finally {
                refreshBtn.disabled = false;
                refreshBtn.textContent = 'Refresh';
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initAdminDashboard();
    setupRefreshButton();
    // Optional: Auto-refresh every 30 seconds
    // startAutoRefresh(30000);
});

/* 
 * ============================================================================
 * Example HTML Structure for the Dashboard:
 * ============================================================================
 * 
 * <div id="loading">Loading statistics...</div>
 * <div id="error-message" style="display: none; color: red;"></div>
 * 
 * <div id="stats-container" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
 *     
 *     <div class="stat-card">
 *         <h3>Total Students</h3>
 *         <p id="total-students">-</p>
 *     </div>
 *     
 *     <div class="stat-card">
 *         <h3>Students Outside</h3>
 *         <p id="total-out-students">-</p>
 *     </div>
 *     
 *     <div class="stat-card">
 *         <h3>Students Inside</h3>
 *         <p id="total-inside-students">-</p>
 *     </div>
 *     
 *     <div class="stat-card">
 *         <h3>Pending Requests</h3>
 *         <p id="total-pending-requests">-</p>
 *     </div>
 * 
 * </div>
 * 
 * <button id="refresh-stats-btn">Refresh</button>
 * 
 * ============================================================================
 * Example Usage with jQuery:
 * ============================================================================
 * 
 * $.ajax({
 *     url: '/api/admin-dashboard/stats/',
 *     method: 'GET',
 *     success: function(response) {
 *         if (response.success) {
 *             $('#total-students').text(response.data.total_students);
 *             $('#total-out-students').text(response.data.total_out_students);
 *             $('#total-inside-students').text(response.data.total_inside_students);
 *             $('#total-pending-requests').text(response.data.total_pending_requests);
 *         }
 *     },
 *     error: function(xhr, status, error) {
 *         console.error('Error:', error);
 *     }
 * });
 * 
 */

