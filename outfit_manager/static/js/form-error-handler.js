// File: static/js/form-error-handler.js
// Revision: 1.0 - Add improved error handling for forms

// Add HTMX event handlers for form submissions
document.addEventListener('DOMContentLoaded', function() {
    // Handle form submission errors
    document.body.addEventListener('htmx:responseError', function(evt) {
        const response = evt.detail.xhr;
        
        // Try to parse error details from response
        try {
            let errorDetail = "An unknown error occurred";
            
            if (response.status === 422) {
                // Validation error
                const data = JSON.parse(response.responseText);
                if (data.detail && Array.isArray(data.detail)) {
                    // FastAPI validation error format
                    errorDetail = data.detail.map(err => {
                        return `${err.loc.slice(1).join('.')}: ${err.msg}`;
                    }).join('\n');
                    showFormError(evt.target, errorDetail);
                } else if (data.detail) {
                    errorDetail = data.detail;
                    showFormError(evt.target, errorDetail);
                }
            } else if (response.status === 404) {
                errorDetail = "Resource not found";
                showFormError(evt.target, errorDetail);
            } else if (response.status === 500) {
                errorDetail = "Server error. Please try again later.";
                showFormError(evt.target, errorDetail);
            } else {
                // Generic error message
                errorDetail = `Error: ${response.status} ${response.statusText}`;
                showFormError(evt.target, errorDetail);
            }
            
            console.error('Form submission error:', errorDetail);
            
        } catch (e) {
            console.error('Error parsing error response:', e);
            showFormError(evt.target, "An unexpected error occurred");
        }
    });
});

// Display error message in the form
function showFormError(formElement, errorMessage) {
    // Find the closest form
    const form = formElement.closest('form');
    if (!form) return;
    
    // Remove any existing error messages
    const existingError = form.querySelector('.form-error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Create error element
    const errorEl = document.createElement('div');
    errorEl.className = 'form-error-message';
    errorEl.innerHTML = `
        <div class="error-icon">⚠️</div>
        <div class="error-content">
            <h4>Form Submission Error</h4>
            <p>${errorMessage}</p>
        </div>
        <button type="button" class="error-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Insert at the top of the form
    form.insertBefore(errorEl, form.firstChild);
    
    // Scroll to error
    errorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Add CSS if not already added
    if (!document.getElementById('form-error-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'form-error-styles';
        styleSheet.textContent = `
            .form-error-message {
                background: #FEF2F2;
                border: 1px solid #F87171;
                border-left: 4px solid #DC2626;
                border-radius: var(--radius-md);
                padding: var(--spacing-md);
                margin-bottom: var(--spacing-lg);
                display: flex;
                align-items: flex-start;
                gap: var(--spacing-md);
                animation: slideDown 0.3s ease-out;
            }
            
            .form-error-message h4 {
                margin: 0 0 var(--spacing-xs) 0;
                color: #B91C1C;
                font-weight: 600;
            }
            
            .form-error-message p {
                margin: 0;
                color: #991B1B;
                font-size: 0.875rem;
                white-space: pre-line;
            }
            
            .error-icon {
                font-size: 1.25rem;
                flex-shrink: 0;
            }
            
            .error-content {
                flex: 1;
            }
            
            .error-close {
                background: none;
                border: none;
                color: #9CA3AF;
                font-size: 1.25rem;
                cursor: pointer;
                padding: 0;
                line-height: 1;
            }
            
            .error-close:hover {
                color: #1F2937;
            }
            
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(styleSheet);
    }
}

// Add validation feedback for specific form fields
function addFieldValidation() {
    // Find all required inputs
    const requiredInputs = document.querySelectorAll('input[required], select[required], textarea[required]');
    
    requiredInputs.forEach(input => {
        // Add validation classes and event listeners if not already set up
        if (!input.classList.contains('validation-added')) {
            input.classList.add('validation-added');
            
            // Add validation styling on blur
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            // Remove validation styling when user starts typing again
            input.addEventListener('input', function() {
                this.classList.remove('input-invalid');
                this.classList.remove('input-valid');
                
                // Remove error message if exists
                const errorMessage = this.parentNode.querySelector('.field-error-message');
                if (errorMessage) {
                    errorMessage.remove();
                }
            });
        }
    });
}

// Validate a single field
function validateField(field) {
    // Skip if field is not required
    if (!field.hasAttribute('required')) return;
    
    // Remove any existing error message
    const existingError = field.parentNode.querySelector('.field-error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Check if field is valid
    const isValid = field.checkValidity();
    
    if (isValid) {
        field.classList.add('input-valid');
        field.classList.remove('input-invalid');
    } else {
        field.classList.add('input-invalid');
        field.classList.remove('input-valid');
        
        // Add error message
        const errorMessage = document.createElement('div');
        errorMessage.className = 'field-error-message';
        errorMessage.textContent = field.validationMessage || 'This field is required';
        
        // Insert after the field or its label
        field.parentNode.appendChild(errorMessage);
    }
}

// Initialize validation on page load
document.addEventListener('DOMContentLoaded', function() {
    addFieldValidation();
    
    // Also add validation when content is swapped via HTMX
    document.body.addEventListener('htmx:afterSwap', function() {
        addFieldValidation();
    });
});