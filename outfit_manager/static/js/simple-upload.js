// File: static/js/simple-upload.js
// Revision: 1.1 - Fixed event handling for upload buttons

document.addEventListener('DOMContentLoaded', function() {
    console.log('Simple upload script loaded - revision 1.1');
    
    // Find all upload containers
    const uploadContainers = document.querySelectorAll('.upload-container');
    console.log('Found upload containers:', uploadContainers.length);
    
    uploadContainers.forEach(function(container) {
        const fileInput = container.querySelector('input[type="file"]');
        const uploadButton = container.querySelector('.upload-button');
        const previewArea = container.querySelector('.preview-area');
        const hasImageInput = document.getElementById('has-image');
        
        console.log('Processing container:', container.id);
        console.log('File input:', fileInput ? 'yes' : 'no');
        console.log('Upload button:', uploadButton ? 'yes' : 'no');
        
        // Handle button click - this is the key part that needs fixing
        if (uploadButton) {
            console.log('Adding click handler to button');
            uploadButton.onclick = function(e) {
                console.log('Upload button clicked');
                e.preventDefault();
                e.stopPropagation();
                if (fileInput) {
                    fileInput.click();
                } else {
                    console.error('No file input found');
                }
            };
        } else {
            console.error('Upload button not found in container');
        }
        
        // Handle file selection
        if (fileInput) {
            fileInput.onchange = function(e) {
                console.log('File selected:', fileInput.files.length > 0 ? fileInput.files[0].name : 'none');
                
                if (fileInput.files && fileInput.files[0]) {
                    // Update hidden input
                    if (hasImageInput) {
                        hasImageInput.value = 'true';
                    }
                    
                    // Show preview
                    const file = fileInput.files[0];
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        console.log('File loaded for preview');
                        if (previewArea) {
                            previewArea.innerHTML = `<img src="${e.target.result}" class="preview-image" alt="Preview">`;
                            previewArea.style.display = 'block';
                        }
                    };
                    
                    reader.readAsDataURL(file);
                }
            };
        }
        
        // Handle drag and drop
        container.ondragover = function(e) {
            e.preventDefault();
            container.classList.add('dragover');
        };
            
        container.ondragleave = function(e) {
            e.preventDefault();
            container.classList.remove('dragover');
        };
            
        container.ondrop = function(e) {
            console.log('File dropped');
            e.preventDefault();
            container.classList.remove('dragover');
            
            if (e.dataTransfer.files && e.dataTransfer.files[0] && fileInput) {
                // Directly set the files
                fileInput.files = e.dataTransfer.files;
                
                // Trigger change event manually
                const event = new Event('change');
                fileInput.dispatchEvent(event);
            }
        };
    });
    
    // Handle form submission
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('htmx:afterRequest', function(event) {
            console.log('Form submitted:', event.detail.successful ? 'success' : 'failure');
            
            if (!event.detail.successful) return;
            
            const hasImageInput = document.getElementById('has-image');
            const hasImage = hasImageInput && hasImageInput.value === 'true';
            
            if (!hasImage) return;
            
            try {
                const response = event.detail.xhr.response;
                const responseData = JSON.parse(response);
                const itemId = responseData.id || responseData.comid || responseData.outid;
                
                if (!itemId) return;
                
                const isOutfit = form.id === 'outfit-form';
                const itemType = isOutfit ? 'outfit' : 'component';
                const fileInput = document.querySelector(`#${itemType}-image-input`);
                
                if (fileInput && fileInput.files && fileInput.files[0]) {
                    console.log('Uploading image for', itemType, itemId);
                    uploadImage(itemId, itemType, fileInput.files[0]);
                }
            } catch (error) {
                console.error('Error handling form submission:', error);
            }
        });
    });
    
    function uploadImage(itemId, itemType, file) {
        const formData = new FormData();
        formData.append('file', file);
        
        fetch(`/api/${itemType}s/${itemId}/upload-image`, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                console.log('Image uploaded successfully');
                window.location.href = `/${itemType}s/${itemId}`;
            } else {
                console.error('Image upload failed');
                window.location.href = `/${itemType}s/${itemId}`;
            }
        })
        .catch(error => {
            console.error('Error uploading image:', error);
            window.location.href = `/${itemType}s/${itemId}`;
        });
    }
});