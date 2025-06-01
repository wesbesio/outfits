// File: static/js/main.js
// Revision: 3.0 - Remove loading indicator functions

// FIND AND REMOVE THESE FUNCTIONS:

// Loading states
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Loading...</p>
            </div>
        `;
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const loadingState = element.querySelector('.loading-state');
        if (loadingState) {
            loadingState.remove();
        }
    }
}

// END REMOVE BLOCK

// ADD THIS FUNCTION INSTEAD - Better navigation with HTMX transitions
function navigateToPage(url, targetSelector = '#main-content') {
    htmx.ajax('GET', url, {
        target: targetSelector,
        swap: 'innerHTML transition:opacity',
        push: true
    });
}