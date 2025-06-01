// File: static/js/basic-upload.js
// Revision: 1.2 - Add detailed error handling and debugging

window.basicUpload = {
    // When the file input changes, update the preview
    handleFileSelect: function(inputId, previewId, hasImageId) {
        console.log('File selected for', inputId);
        const fileInput = document.getElementById(inputId);
        const previewArea = document.getElementById(previewId);
        const hasImageInput = document.getElementById(hasImageId);
        
        if (!fileInput || !previewArea) {
            console.error('Missing elements:', {fileInput, previewArea});
            return;
        }
        
        if (fileInput.files && fileInput.files[0]) {
            // We have a file selected
            const file = fileInput.files[0];
            console.log('Selected file:', file.name, file.type, file.size, 'bytes');
            
            // Update has-image flag
            if (hasImageInput) {
                hasImageInput.value = 'true';
            }
            
            // Create file reader for preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewArea.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 100%; max-height: 200px; border-radius: 4px;">`;
                previewArea.style.display = 'block';
                console.log('Preview displayed');
            };
            reader.onerror = function(e) {
                console.error('Error reading file:', e);
            };
            reader.readAsDataURL(file);
        }
    },
    
    // Trigger the file input click
    openFilePicker: function(inputId) {
        console.log('Opening file picker for', inputId);
        const fileInput = document.getElementById(inputId);
        if (fileInput) {
            fileInput.click();
        } else {
            console.error('File input not found:', inputId);
        }
    },
    
    // Submit the form with JSON data
    submitForm: function(formId, e) {
        e.preventDefault();
        console.log('Intercepting form submission for', formId);
        
        const form = document.getElementById(formId);
        if (!form) {
            console.error('Form not found:', formId);
            return;
        }
        
        // Get form data excluding the file
        const formData = new FormData(form);
        const jsonData = {};
        
        // Convert FormData to a plain object, handling types
        formData.forEach((value, key) => {
            console.log(`Form field: ${key} = ${value} (${typeof value})`);
            
            // Skip the file input
            if (key === 'image_file') return;
            
            // Skip has_image (not part of the API model)
            if (key === 'has_image') return;
            
            // Handle radio buttons for "active"
            if (key === 'active') {
                jsonData[key] = value === 'true';
                return;
            }
            
            // Handle numeric fields
            if (key === 'cost' || key === 'vendorid' || key === 'piecid') {
                // If the value is empty, set to null (for optional fields)
                if (value === '') {
                    jsonData[key] = null;
                } else {
                    // Parse as integer
                    const numVal = parseInt(value, 10);
                    jsonData[key] = isNaN(numVal) ? null : numVal;
                }
                return;
            }
            
            // Handle other fields
            jsonData[key] = value === '' ? null : value;
        });
        
        // Add default flag value (expected by API)
        jsonData.flag = false;
        
        // Extract hx-* attributes
        const url = form.getAttribute('hx-post') || form.getAttribute('hx-put');
        const target = form.getAttribute('hx-target');
        const pushUrl = form.getAttribute('hx-push-url');
        
        console.log('Submitting data:', JSON.stringify(jsonData, null, 2));
        
        // Send the data as JSON
        fetch(url, {
            method: form.getAttribute('hx-post') ? 'POST' : 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => {
            console.log('Response status:', response.status);
            
            // If there's an error, get the error details
            if (!response.ok) {
                // Clone the response so we can use it twice
                const responseClone = response.clone();
                
                // First, try to get the response text for detailed error
                return responseClone.text().then(text => {
                    console.error('Error response:', text);
                    
                    try {
                        // Try to parse as JSON
                        const errorJson = JSON.parse(text);
                        console.error('Error details:', errorJson);
                        alert(`Error: ${JSON.stringify(errorJson, null, 2)}`);
                    } catch (e) {
                        // Not JSON, just show the text
                        alert(`Error: ${text}`);
                    }
                    
                    throw new Error(`Request failed with status: ${response.status}`);
                });
            }
            
            return response.json();
        })
        .then(data => {
            console.log('Form submission successful:', data);
            
            // Check if we need to upload an image
            const hasImageInput = document.getElementById('has-image');
            const hasImage = hasImageInput && hasImageInput.value === 'true';
            
            if (hasImage) {
                // We have an image to upload
                const itemId = data.comid || data.outid;
                const itemType = data.comid ? 'component' : 'outfit';
                const fileInput = document.getElementById(`${itemType}-image-input`);
                
                if (itemId && fileInput && fileInput.files && fileInput.files[0]) {
                    console.log('Uploading image for', itemType, itemId);
                    uploadImage(itemId, itemType, fileInput.files[0], pushUrl);
                } else {
                    // No image to upload, just redirect
                    if (pushUrl) {
                        window.location.href = pushUrl;
                    }
                }
            } else {
                // No image to upload, just redirect
                if (pushUrl) {
                    window.location.href = pushUrl;
                }
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
        });
    }
};

function uploadImage(itemId, itemType, file, redirectUrl) {
    console.log(`Starting upload for ${itemType} ${itemId}`);
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch(`/api/${itemType}s/${itemId}/upload-image`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('Image upload response:', response.status);
        
        if (response.ok) {
            console.log('Image uploaded successfully');
            
            // Redirect to the detail page if URL is provided
            if (redirectUrl) {
                if (redirectUrl.includes(':id')) {
                    // Replace :id with actual ID
                    redirectUrl = redirectUrl.replace(':id', itemId);
                }
                window.location.href = redirectUrl;
            } else {
                // Default redirect
                window.location.href = `/${itemType}s/${itemId}`;
            }
        } else {
            console.error('Image upload failed');
            
            // Still redirect to the item
            if (redirectUrl) {
                if (redirectUrl.includes(':id')) {
                    // Replace :id with actual ID
                    redirectUrl = redirectUrl.replace(':id', itemId);
                }
                window.location.href = redirectUrl;
            } else {
                window.location.href = `/${itemType}s/${itemId}`;
            }
        }
    })
    .catch(error => {
        console.error('Error uploading image:', error);
        
        // Still redirect to the item
        if (redirectUrl) {
            if (redirectUrl.includes(':id')) {
                // Replace :id with actual ID
                redirectUrl = redirectUrl.replace(':id', itemId);
            }
            window.location.href = redirectUrl;
        } else {
            window.location.href = `/${itemType}s/${itemId}`;
        }
    });
}