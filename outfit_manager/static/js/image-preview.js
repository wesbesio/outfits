// File: static/js/image-preview.js
// Revision: 1.0 - Minimal JS for image preview in forms

document.addEventListener('DOMContentLoaded', () => {
    // Function to handle image preview
    function setupImagePreview(fileInputId, previewImgId) {
        const fileInput = document.getElementById(fileInputId);
        const previewImg = document.getElementById(previewImgId);

        if (fileInput && previewImg) {
            fileInput.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewImg.src = e.target.result;
                        previewImg.style.display = 'block'; // Show the image
                    };
                    reader.readAsDataURL(file);
                } else {
                    previewImg.src = '#';
                    previewImg.style.display = 'none'; // Hide if no file
                }
            });
        }
    }

    // Setup for component form
    setupImagePreview('component-image-upload', 'component-image-preview');

    // Setup for outfit form (will be used in Phase 3)
    setupImagePreview('outfit-image-upload', 'outfit-image-preview');
});

// Handle HTMX afterswap to re-initialize event listeners for dynamic content
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'main-content' || event.detail.target.closest('.main-content')) {
        setupImagePreview('component-image-upload', 'component-image-preview');
        setupImagePreview('outfit-image-upload', 'outfit-image-preview');
    }
});