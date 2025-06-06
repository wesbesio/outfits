// File: static/js/form-error-handler.js
// Revision: 1.1 - Enhanced error handling with better validation error detection

document.addEventListener('DOMContentLoaded', () => {
    const errorToast = document.getElementById('global-error-toast');
    const errorMessageElement = document.getElementById('global-error-message');

    if (!errorToast || !errorMessageElement) {
        console.warn('Global error display elements not found in the DOM.');
        return;
    }

    // NEW: Function to parse and format error messages better
    function parseErrorMessage(xhr) {
        let message = `Error: ${xhr.status} - ${xhr.statusText}`;
        
        // Handle FastAPI validation errors specifically
        if (xhr.status === 422) {
            message = "Please check your input values and try again.";
            
            // Try to extract specific validation error details
            try {
                const errorData = JSON.parse(xhr.responseText);
                if (errorData && errorData.detail && Array.isArray(errorData.detail)) {
                    const validationErrors = errorData.detail
                        .map(err => `${err.loc ? err.loc.join('.') : 'field'}: ${err.msg}`)
                        .join(', ');
                    message = `Validation Error: ${validationErrors}`;
                }
            } catch (e) {
                // Keep the generic validation message if we can't parse details
            }
            return message;
        }
        
        // Handle search/filter related errors
        if (xhr.status === 400 && xhr.responseURL && xhr.responseURL.includes('/api/')) {
            message = "Invalid search parameters. Please check your filters and try again.";
            return message;
        }
        
        // Try to get a more specific error message from server response
        try {
            const responseJson = JSON.parse(xhr.responseText);
            if (responseJson && responseJson.detail) {
                message = `Server Error: ${responseJson.detail}`;
            } else if (responseJson && responseJson.error) {
                message = `Server Error: ${responseJson.error}`;
            }
        } catch (e) {
            // Response was not JSON or JSON parsing failed
            if (xhr.responseText && xhr.responseText.length < 200 && !xhr.responseText.trim().startsWith("<!DOCTYPE html>")) {
                // If it's a short text response that's not HTML, show it
                message = xhr.responseText.trim();
            } else if (xhr.status >= 500) {
                message = "Server error occurred. Please try again or contact support.";
            } else if (xhr.status === 404) {
                message = "The requested item was not found.";
            } else if (xhr.status === 403) {
                message = "You don't have permission to perform this action.";
            }
        }
        
        return message;
    }

    // NEW: Function to show error toast with auto-hide
    function showErrorToast(message, autoHide = true) {
        errorMessageElement.textContent = message;
        errorToast.style.display = 'flex';
        
        // Auto-hide after 5 seconds for non-critical errors
        if (autoHide) {
            setTimeout(() => {
                if (errorToast.style.display === 'flex') {
                    errorToast.style.display = 'none';
                }
            }, 5000);
        }
    }

    // Enhanced response error handler
    document.body.addEventListener('htmx:responseError', function(event) {
        console.error("HTMX Response Error:", event.detail.xhr);
        
        const message = parseErrorMessage(event.detail.xhr);
        const isServerError = event.detail.xhr.status >= 500;
        
        // Show error with auto-hide for client errors, manual dismiss for server errors
        showErrorToast(message, !isServerError);
    });

    // Enhanced send error handler
    document.body.addEventListener('htmx:sendError', function(event) {
        console.error("HTMX Send Error (e.g., network issue):", event.detail.error);
        
        let message = 'Network error or connection issue. Please check your internet connection and try again.';
        
        // Check if it's a timeout or connection refused error
        if (event.detail.error && event.detail.error.toString().includes('timeout')) {
            message = 'Request timed out. Please try again.';
        } else if (event.detail.error && event.detail.error.toString().includes('refused')) {
            message = 'Could not connect to server. Please check your connection.';
        }
        
        showErrorToast(message, false); // Don't auto-hide network errors
    });

    // NEW: Add specific handler for search/filter operations
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        // Check if this is a search request
        const url = event.detail.requestConfig.path;
        if (url && (url.includes('/api/components/') || url.includes('/api/outfits/'))) {
            // Add a small delay to prevent rapid-fire search requests
            const now = Date.now();
            if (window.lastSearchTime && (now - window.lastSearchTime) < 100) {
                console.log('Throttling rapid search request');
                event.preventDefault();
                return;
            }
            window.lastSearchTime = now;
        }
    });

    // NEW: Success feedback for certain operations
    document.body.addEventListener('htmx:afterSwap', function(event) {
        // Hide error toast on successful operations
        if (errorToast.style.display === 'flex') {
            errorToast.style.display = 'none';
        }
        
        // Check if we just loaded search results
        const target = event.detail.target;
        if (target && (target.id === 'component-list-container' || target.id === 'outfit-list-container')) {
            // Could add success feedback here if needed
            console.log('Search results loaded successfully');
        }
    });

    // Manual close button functionality
    const closeButton = errorToast.querySelector('button');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            errorToast.style.display = 'none';
        });
    }
    
    // Allow clicking outside toast to close it
    errorToast.addEventListener('click', function(event) {
        if (event.target === errorToast) {
            errorToast.style.display = 'none';
        }
    });

    // NEW: Escape key to close error toast
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && errorToast.style.display === 'flex') {
            errorToast.style.display = 'none';
        }
    });
    
    // Example of how to manually trigger an error for testing:
    // window.testError = function() {
    //     showErrorToast('This is a test error message', true);
    // };
});