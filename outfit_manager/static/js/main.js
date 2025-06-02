// File: static/js/main.js
// Revision: 1.0 - Minimal utilities only

// HTMX Configuration
document.addEventListener('DOMContentLoaded', function() {
    // Configure HTMX defaults
    htmx.config.globalViewTransitions = true;
    htmx.config.defaultSwapStyle = 'innerHTML';
    
    // Add loading states
    document.addEventListener('htmx:beforeRequest', function(evt) {
        const target = evt.target;
        target.classList.add('htmx-loading');
    });
    
    document.addEventListener('htmx:afterRequest', function(evt) {
        const target = evt.target;
        target.classList.remove('htmx-loading');
    });
    
    // Handle navigation active states
    document.addEventListener('htmx:afterSettle', function(evt) {
        updateActiveNavigation();
    });
});

// Update active navigation states
function updateActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link, .bottom-nav-item');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath.includes(href) && href !== '/')) {
            link.classList.add('active');
        }
    });
}

// Initialize on page load
updateActiveNavigation();
