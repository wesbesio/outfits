// File: static/js/form-image-upload.js
// Revision: 1.1 - Fix click to upload functionality

/**
 * Initializes image upload UI for outfit/component creation forms
 * This provides a preview and selection but doesn't upload until the form is submitted
 */
 function initializeFormImageUpload(container, itemType) {
    if (!container) {
        console.error('Image upload container not found');
        return;
    }
    
    // Find file input or create one if it doesn't exist
    let fileInput = container.querySelector('input[type="file"]');
    if (!fileInput) {
        console.error('File input not found in container');
        return;
    }
    
    console.log('Initializing image upload for', itemType, fileInput);
    
    let selectedFile = null;
    
    // Click to trigger file input - Use a clearer approach
    container.onclick = function(e) {
        // Don't trigger file dialog if clicking on the remove button
        if (e.target.closest('.remove-preview-btn')) {
            return;
        }
        
        console.log('Container clicked, triggering file input click');
        // Directly trigger click on file input
        fileInput.click();
    };
    
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
        console.log('File input change event', e.target.files);
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // Handle selected file
    function handleFileSelect(file) {
        console.log('File selected:', file.name, file.type);
        
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
        const hasImageInput = document.getElementById('has-image');
        if (hasImageInput) {
            hasImageInput.value = 'true';
        }
        
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
            
            // Re-add the file input to the DOM (it was removed when we changed innerHTML)
            container.appendChild(fileInput);
        };
        
        reader.readAsDataURL(file);
    }
    
    // Reset the container to initial state
    function resetContainer() {
        selectedFile = null;
        const hasImageInput = document.getElementById('has-image');
        if (hasImageInput) {
            hasImageInput.value = 'false';
        }
        
        container.innerHTML = `
            <div class="upload-content">
                <span