/**
 * Hostel Lock System - Main JavaScript
 * 
 * Includes reusable functions for:
 * - CSRF token handling
 * - Login API calls
 * - Message display
 */

// ============================================================
// CSRF Token Functions
// ============================================================

/**
 * Get CSRF token from Django cookie
 * Django automatically sets 'csrftoken' cookie after first page load
 * @returns {string} CSRF token value
 */
function getCsrfToken() {
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
    
    return cookieValue || '';
}

/**
 * Login user via REST API
 * @param {string} username - User's username
 * @param {string} password - User's password
 * @returns {Promise} - Resolves with API response data
 */
async function loginApi(username, password) {
    const csrfToken = getCsrfToken();
    
    const response = await fetch('/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    });
    
    const data = await response.json();
    return data;
}

// ============================================================
// Message Display Functions
// ============================================================

/**
 * Show a message to the user
 * @param {string} message - Message text
 * @param {string} type - Message type (success, error, info, warning)
 * @param {string} containerId - Optional ID of container element
 */
function showApiMessage(message, type, containerId) {
    const container = containerId ? document.getElementById(containerId) : document.body;
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `api-message ${type} show`;
    messageDiv.textContent = message;
    
    // Insert at the top of container
    const firstChild = container.firstChild;
    if (firstChild) {
        container.insertBefore(messageDiv, firstChild);
    } else {
        container.appendChild(messageDiv);
    }
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        messageDiv.className = `api-message ${type}`;
        setTimeout(function() {
            messageDiv.remove();
        }, 500);
    }, 5000);
}

/**
 * Show error message in login form
 * @param {string} message - Error message
 */
function showLoginError(message) {
    const messageBox = document.getElementById('api-message');
    if (messageBox) {
        messageBox.textContent = message;
        messageBox.className = 'api-message show error';
        
        setTimeout(function() {
            messageBox.className = 'api-message';
        }, 5000);
    }
}

/**
 * Show success message in login form
 * @param {string} message - Success message
 */
function showLoginSuccess(message) {
    const messageBox = document.getElementById('api-message');
    if (messageBox) {
        messageBox.textContent = message;
        messageBox.className = 'api-message show success';
        
        setTimeout(function() {
            messageBox.className = 'api-message';
        }, 5000);
    }
}

// ============================================================
// Main Document Ready
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.messages');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Date validation for outpass form
    const departureInput = document.getElementById('id_departure_date');
    const returnInput = document.getElementById('id_return_date');
    
    if (departureInput && returnInput) {
        // Set minimum date/time to current time
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        departureInput.min = now.toISOString().slice(0, 16);
        
        departureInput.addEventListener('change', function() {
            returnInput.min = this.value;
        });
    }

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-danger, .delete-btn');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to proceed with this action?')) {
                e.preventDefault();
            }
        });
    });

    // Table row hover effect
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('click', function() {
            // Optional: Add row selection functionality
        });
    });

    // Search functionality (if search input exists)
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const table = document.querySelector('table');
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        });
    }

    // Mobile menu toggle (if exists)
    const menuToggle = document.getElementById('menu-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#dc3545';
                } else {
                    field.style.borderColor = '#ddd';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

    // Status filter (if exists)
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function(e) {
            const status = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {
                if (status === 'all') {
                    row.style.display = '';
                } else {
                    const statusCell = row.querySelector('.status');
                    if (statusCell && statusCell.classList.contains(status)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
        });
    }

    // Add loading state to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(function(button) {
        button.addEventListener('click', function() {
            if (!this.classList.contains('no-loading')) {
                const originalText = this.textContent;
                this.textContent = 'Loading...';
                this.disabled = true;
                
                setTimeout(function() {
                    button.textContent = originalText;
                    button.disabled = false;
                }, 2000);
            }
        });
    });

    console.log('Hostel Lock System - JavaScript initialized');
});

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

// Utility function to show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `messages ${type}`;
    notification.textContent = message;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(notification, container.firstChild);
    
    setTimeout(function() {
        notification.style.opacity = '0';
        setTimeout(function() {
            notification.remove();
        }, 500);
    }, 3000);
}


// =============================================================================
// Outpass API Functions (Fetch API + FormData)
// =============================================================================

/**
 * Create outpass using Fetch API and FormData
 * @param {HTMLFormElement} form - The form element to submit
 * @returns {Promise} - Resolves with API response data
 */
async function createOutpassApi(formElement) {
    const csrfToken = getCsrfToken();
    
    // Create FormData from form element
    const formData = new FormData(formElement);
    
    const response = await fetch('/api/create-outpass/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    });
    
    const data = await response.json();
    return data;
}

/**
 * Submit outpass with manual data (not from form)
 * @param {string} purpose - Purpose of outpass
 * @param {string} destination - Destination address
 * @param {string} timeOut - Time out datetime string (YYYY-MM-DDTHH:MM)
 * @param {string} returnDate - Return datetime string (YYYY-MM-DDTHH:MM)
 * @param {File} imageFile - Optional image file
 * @returns {Promise} - Resolves with API response data
 */
async function submitOutpass(purpose, destination, timeOut, returnDate, imageFile = null) {
    const csrfToken = getCsrfToken();
    
    const formData = new FormData();
    formData.append('purpose', purpose);
    formData.append('destination', destination);
    formData.append('time_out', timeOut);
    formData.append('return_date', returnDate);
    
    if (imageFile) {
        formData.append('image', imageFile);
    }
    
    const response = await fetch('/api/create-outpass/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    });
    
    const data = await response.json();
    return data;
}

/**
 * Display success/error message in the API message container
 * @param {string} message - Message to display
 * @param {string} type - Message type (success, error, info)
 * @param {string} containerId - Optional ID of message container
 */
function displayApiMessage(message, type, containerId = 'api-message') {
    const container = document.getElementById(containerId);
    if (container) {
        container.textContent = message;
        container.className = `api-message show ${type}`;
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            container.className = 'api-message';
        }, 5000);
    }
}

