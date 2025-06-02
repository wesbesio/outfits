// File: static/js/form-error-handler.js
// Revision: 1.0 - HTMX error handling

// Handle HTMX errors
document.addEventListener('htmx:responseError', function(evt) {
    console.error('HTMX Response Error:', evt.detail);
    
    // Show user-friendly error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = 'Something went wrong. Please try again.';
    
    const target = evt.target;
    target.insertBefore(errorDiv, target.firstChild);
    
    // Remove error message after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
});

// Handle validation errors
document.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.xhr.status === 422) {
        // Handle validation errors
        try {
            const errors = JSON.parse(evt.detail.xhr.responseText);
            displayValidationErrors(errors);
        } catch (e) {
            console.error('Error parsing validation response:', e);
        }
    }
});

function displayValidationErrors(errors) {
    // Clear existing errors
    document.querySelectorAll('.field-error').forEach(el => el.remove());
    
    // Display new errors
    if (errors.detail) {
        errors.detail.forEach(error => {
            const field = document.querySelector(`[name="${error.loc[1]}"]`);
            if (field) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'field-error';
                errorDiv.textContent = error.msg;
                field.parentNode.insertBefore(errorDiv, field.nextSibling);
            }
        });
    }
}
