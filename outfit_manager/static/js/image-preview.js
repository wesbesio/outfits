// File: static/js/image-preview.js
// Revision: 1.1 - Fixed scope of setupImagePreview function

// Define setupImagePreview in a scope accessible to both listeners
function setupImagePreview(fileInputId, previewImgId) {
    const fileInput = document.getElementById(fileInputId);
    const previewImg = document.getElementById(previewImgId);

    // Ensure elements exist before adding event listener
    if (fileInput && previewImg) {
        // Remove old listener to prevent duplicates if this is called multiple times on the same element
        // This is a simple way; a more robust way might involve storing and removing specific listeners.
        const newFileInput = fileInput.cloneNode(true);
        fileInput.parentNode.replaceChild(newFileInput, fileInput);
        
        newFileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    previewImg.style.display = 'block'; // Show the image
                };
                reader.readAsDataURL(file);
            } else {
                // Don't hide or clear if no file is selected on an existing input,
                // only if clearing is intended. For now, just no update.
                // previewImg.src = '#';
                // previewImg.style.display = 'none'; 
            }
        });
    } else {
        // console.warn(`setupImagePreview: Could not find elements - Input: #${fileInputId}, Preview: #${previewImgId}`);
    }
}

// Initial setup on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    // console.log("DOMContentLoaded: Setting up initial image previews.");
    setupImagePreview('component-image-upload', 'component-image-preview');
    setupImagePreview('outfit-image-upload', 'outfit-image-preview');
});

// Handle HTMX afterSwap to re-initialize event listeners for dynamic content
document.body.addEventListener('htmx:afterSwap', function(event) {
    // console.log("htmx:afterSwap triggered for target:", event.detail.target);
    // Check if the swapped content is within #main-content or is #main-content itself
    const mainContent = document.getElementById('main-content');
    if (mainContent && (mainContent.contains(event.detail.target) || mainContent === event.detail.target || event.detail.target.id === 'main-content')) {
        // console.log("htmx:afterSwap: Re-setting up image previews within #main-content.");
        setupImagePreview('component-image-upload', 'component-image-preview');
        setupImagePreview('outfit-image-upload', 'outfit-image-preview');
    } else if (event.detail.target.querySelector('#component-image-upload') || event.detail.target.querySelector('#outfit-image-upload')) {
        // If the target itself contains the upload fields (e.g. form content directly swapped)
        // console.log("htmx:afterSwap: Re-setting up image previews within swapped target that is not #main-content but contains fields.");
        setupImagePreview('component-image-upload', 'component-image-preview');
        setupImagePreview('outfit-image-upload', 'outfit-image-preview');
    }
});
