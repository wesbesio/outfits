// File: static/js/form-image-upload.js
// Revision: 1.0 - Handle image upload during form creation

/**
 * Initializes image upload UI for outfit/component creation forms
 * This provides a preview and selection but doesn't upload until the form is submitted
 */
 function initializeFormImageUpload(container, itemType) {
    if (!container) return;
    
    const fileInput = container.querySelector('input[type="file"]');
    if (!fileInput) return;
    
    let selectedFile = null;
    
    // Click to trigger file input
    container.addEventListener('click', (e) => {
        if (!e.target.closest('.remove-preview-btn')) {
            fileInput.click();
        }
    });
    
    // Drag and drop functionality
    container.addEventListener('dragover', (e) => {
        e.preventDefault();
        container.classList.add('drag-over');
    });
    
    container.addEventListener('dragenter', (e) => {
        e.preventDefault();
        container.classList.add('drag-over');
    });
    
    container.addEventListener('dragleave', (e) => {
        e.preventDefault();
        if (!container.contains(e.relatedTarget)) {
            container.classList.remove('drag-over');
        }
    });
    
    container.addEventListener('drop', (e) => {
        e.preventDefault();
        container.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // File selection handler
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // Handle selected file
    function handleFileSelect(file) {
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            showToast('Invalid file type. Please upload a JPEG, PNG, or WebP image.', 'error');
            return;
        }
        
        // Validate file size (5MB limit)
        const maxSize = 5 * 1024 * 1024;
        if (file.size > maxSize) {
            showToast('File too large. Maximum size is 5MB.', 'error');
            return;
        }
        
        // Store the file
        selectedFile = file;
        
        // Update the hidden input value
        document.getElementById('has-image').value = 'true';
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            container.innerHTML = `
                <div class="preview-container">
                    <img src="${e.target.result}" alt="Preview" class="preview-image">
                    <button type="button" class="btn btn-small btn-secondary remove-preview-btn">
                        Remove
                    </button>
                </div>
            `;
            
            // Add remove functionality
            const removeBtn = container.querySelector('.remove-preview-btn');
            if (removeBtn) {
                removeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    resetContainer();
                });
            }
        };
        
        reader.readAsDataURL(file);
    }
    
    // Reset the container to initial state
    function resetContainer() {
        selectedFile = null;
        document.getElementById('has-image').value = 'false';
        
        container.innerHTML = `
            <div class="upload-content">
                <span class="upload-icon">📁</span>
                <p class="upload-text">
                    <strong>Click to upload</strong> or drag and drop<br>
                    <small>JPEG, PNG, WebP up to 5MB</small>
                </p>
            </div>
        `;
        
        // Recreate file input
        if (!container.querySelector('input[type="file"]')) {
            container.appendChild(fileInput);
        }
    }
}

/**
 * Handles form submission with image upload
 * This is called after the form is successfully submitted
 */
function handleFormSubmit(event) {
    if (!event.detail.successful) return;
    
    const response = event.detail.xhr.response;
    const hasImage = document.getElementById('has-image').value === 'true';
    
    // If there's no image to upload, we're done
    if (!hasImage) {
        showToast('Item created successfully!', 'success');
        return;
    }
    
    try {
        // Parse the response to get the ID of the newly created item
        const responseData = JSON.parse(response);
        const itemId = responseData.id || responseData.comid || responseData.outid;
        const itemType = responseData.comid ? 'component' : 'outfit';
        
        if (itemId) {
            // Get the file
            const fileInput = document.querySelector(`#${itemType}-image-input`);
            if (fileInput && fileInput.files.length > 0) {
                uploadImage(itemId, itemType, fileInput.files[0]);
            }
        }
    } catch (e) {
        // If we can't parse the response, navigate to the list page
        if (window.location.pathname.includes('outfits')) {
            window.location.href = '/outfits';
        } else {
            window.location.href = '/components';
        }
    }
}

/**
 * Uploads an image for a newly created item
 */
function uploadImage(itemId, itemType, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `/api/${itemType}s/${itemId}/upload-image`);
    
    xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            showToast(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} created with image!`, 'success');
            
            // Navigate to the detail page
            window.location.href = `/${itemType}s/${itemId}`;
        } else {
            showToast(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} created, but image upload failed.`, 'warning');
            
            // Navigate to the detail page anyway
            window.location.href = `/${itemType}s/${itemId}`;
        }
    };
    
    xhr.onerror = () => {
        showToast(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} created, but image upload failed.`, 'warning');
        
        // Navigate to the detail page anyway
        window.location.href = `/${itemType}s/${itemId}`;
    };
    
    xhr.send(formData);
}

/**
 * Shows a toast notification
 */
function showToast(message, type = 'success') {
    // Use existing toast function if available
    if (window.appUtils && window.appUtils.showToast) {
        window.appUtils.showToast(message, type);
        return;
    }
    
    // Fallback toast implementation
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

/**
 * Creates a toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Add CSS for previews
const previewStyles = document.createElement('style');
previewStyles.textContent = `
.preview-container {
    position: relative;
    width: 100%;
    height: 200px;
    border-radius: var(--radius-md);
    overflow: hidden;
}

.preview-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.remove-preview-btn {
    position: absolute;
    top: var(--spacing-sm);
    right: var(--spacing-sm);
    background: rgba(0, 0, 0, 0.5);
    color: white;
    border: none;
    transition: background var(--transition-fast);
}

.remove-preview-btn:hover {
    background: rgba(239, 68, 68, 0.9);
}
`;
document.head.appendChild(previewStyles);