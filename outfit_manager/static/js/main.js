// Global utility functions for the Outfit Manager app

// Toast notifications
function showToast(message, type = 'success', duration = 4000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    // Auto-remove toast
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            if (container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 300);
    }, duration);
    
    // Click to dismiss
    toast.addEventListener('click', () => {
        toast.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            if (container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 300);
    });
}

// Make showToast globally available
window.showToast = showToast;

// Form utilities
function resetForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        
        // Reset radio button styling
        const radioOptions = form.querySelectorAll('.radio-option');
        radioOptions.forEach(option => {
            const input = option.querySelector('input[type="radio"]');
            if (input && input.checked) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
        
        // Clear image previews
        const imagePreviews = form.querySelectorAll('.image-preview');
        imagePreviews.forEach(preview => {
            preview.style.display = 'none';
            preview.src = '';
        });
    }
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        const value = field.value.trim();
        const errorElement = field.parentNode.querySelector('.field-error');
        
        if (!value) {
            isValid = false;
            field.classList.add('error');
            
            if (!errorElement) {
                const error = document.createElement('span');
                error.className = 'field-error';
                error.textContent = 'This field is required';
                field.parentNode.appendChild(error);
            }
        } else {
            field.classList.remove('error');
            if (errorElement) {
                errorElement.remove();
            }
        }
    });
    
    return isValid;
}

// Image handling utilities
function previewImage(input, previewElementId) {
    const file = input.files[0];
    const preview = document.getElementById(previewElementId);
    
    if (file && preview) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
            
            // Trigger preview animation
            preview.style.opacity = '0';
            preview.style.transform = 'scale(0.9)';
            requestAnimationFrame(() => {
                preview.style.transition = 'all 300ms ease-in-out';
                preview.style.opacity = '1';
                preview.style.transform = 'scale(1)';
            });
        };
        
        reader.readAsDataURL(file);
    }
}

function removeImage(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.transition = 'all 300ms ease-in-out';
        element.style.opacity = '0';
        element.style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            element.innerHTML = `
                <div class="no-image-placeholder">
                    <span class="placeholder-icon">📷</span>
                    <p>No image uploaded</p>
                </div>
            `;
            element.style.opacity = '1';
            element.style.transform = 'scale(1)';
        }, 300);
    }
}

// Navigation utilities
function navigateToPage(url, targetSelector = '#main-content') {
    htmx.ajax('GET', url, {
        target: targetSelector,
        swap: 'innerHTML',
        push: true
    });
}

function goBack() {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        navigateToPage('/');
    }
}

// Data formatting utilities
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}

function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    
    return formatDate(dateString);
}

// Local storage utilities (with fallback)
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.warn('localStorage not available, using memory storage');
        window._memoryStorage = window._memoryStorage || {};
        window._memoryStorage[key] = value;
    }
}

function getFromStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.warn('localStorage not available, using memory storage');
        window._memoryStorage = window._memoryStorage || {};
        return window._memoryStorage[key] || defaultValue;
    }
}

function removeFromStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (e) {
        if (window._memoryStorage) {
            delete window._memoryStorage[key];
        }
    }
}

// Search and filter utilities
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function setupSearchInput(inputId, targetUrl, targetElement) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    const debouncedSearch = debounce((query) => {
        htmx.ajax('GET', `${targetUrl}?search=${encodeURIComponent(query)}`, {
            target: targetElement,
            swap: 'innerHTML'
        });
    }, 300);
    
    input.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
    });
}

// Touch and gesture utilities for mobile
function addTouchSupport() {
    // Add touch classes for better mobile interactions
    document.addEventListener('touchstart', function(e) {
        e.target.classList.add('touching');
    });
    
    document.addEventListener('touchend', function(e) {
        setTimeout(() => {
            e.target.classList.remove('touching');
        }, 150);
    });
    
    // Prevent double-tap zoom on buttons
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(e) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
}

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

// Error handling
function handleError(error, context = '') {
    console.error(`Error in ${context}:`, error);
    showToast(`Something went wrong${context ? ` in ${context}` : ''}. Please try again.`, 'error');
}

// Radio button styling helper
function updateRadioButtonStyling() {
    const radioOptions = document.querySelectorAll('.radio-option');
    radioOptions.forEach(option => {
        const input = option.querySelector('input[type="radio"]');
        if (input && input.checked) {
            option.classList.add('selected');
        } else {
            option.classList.remove('selected');
        }
    });
}

// Initialize app
function initializeApp() {
    // Add touch support for mobile devices
    addTouchSupport();
    
    // Set up keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Escape key for potential future features
        if (e.key === 'Escape') {
            // Future: close any open overlays
        }
        
        // Ctrl/Cmd + K for quick search (future feature)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            // Future: show search modal
        }
    });
    
    // Set up global HTMX event listeners
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        // Re-initialize any new dynamic content
        initializeDynamicContent();
    });
    
    document.body.addEventListener('htmx:responseError', function(evt) {
        const status = evt.detail.xhr.status;
        let message = 'An error occurred';
        
        if (status === 404) {
            message = 'Item not found';
        } else if (status === 403) {
            message = 'Access denied';
        } else if (status === 500) {
            message = 'Server error';
        }
        
        showToast(message, 'error');
    });
    
    document.body.addEventListener('htmx:timeout', function(evt) {
        showToast('Request timed out. Please check your connection.', 'error');
    });
    
    // Handle radio button changes
    document.addEventListener('change', function(e) {
        if (e.target.type === 'radio') {
            const name = e.target.name;
            const radioOptions = document.querySelectorAll(`input[name="${name}"]`);
            radioOptions.forEach(option => {
                const label = option.closest('.radio-option');
                if (option.checked) {
                    label.classList.add('selected');
                } else {
                    label.classList.remove('selected');
                }
            });
        }
    });
}

function initializeDynamicContent() {
    // Re-initialize radio button styling
    updateRadioButtonStyling();
    
    // Re-initialize any new image upload areas
    const imageUploads = document.querySelectorAll('.image-upload-container');
    imageUploads.forEach(upload => {
        if (!upload.hasAttribute('data-initialized')) {
            if (window.initializeImageUpload) {
                initializeImageUpload(upload);
            }
            upload.setAttribute('data-initialized', 'true');
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Export functions for global use
window.appUtils = {
    showToast,
    resetForm,
    validateForm,
    previewImage,
    removeImage,
    navigateToPage,
    goBack,
    formatCurrency,
    formatDate,
    formatRelativeTime,
    saveToStorage,
    getFromStorage,
    removeFromStorage,
    handleError,
    showLoading,
    hideLoading,
    updateRadioButtonStyling
};