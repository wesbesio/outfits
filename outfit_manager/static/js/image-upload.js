// Image upload functionality with drag & drop support

class ImageUploader {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            maxSize: 5 * 1024 * 1024, // 5MB
            allowedTypes: ['image/jpeg', 'image/png', 'image/webp'],
            uploadUrl: options.uploadUrl || '/api/upload',
            onSuccess: options.onSuccess || this.defaultOnSuccess,
            onError: options.onError || this.defaultOnError,
            onProgress: options.onProgress || this.defaultOnProgress,
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.createFileInput();
    }
    
    createFileInput() {
        if (!this.container.querySelector('input[type="file"]')) {
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = this.options.allowedTypes.join(',');
            fileInput.style.display = 'none';
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
            this.container.appendChild(fileInput);
        }
    }
    
    setupEventListeners() {
        // Click to upload
        this.container.addEventListener('click', (e) => {
            if (!e.target.closest('.remove-image-btn')) {
                const fileInput = this.container.querySelector('input[type="file"]');
                if (fileInput) fileInput.click();
            }
        });
        
        // Drag and drop
        this.container.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.container.addEventListener('dragenter', (e) => this.handleDragEnter(e));
        this.container.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.container.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Prevent default drag behaviors on the document
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.container.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.container.classList.add('drag-over');
    }
    
    handleDragEnter(e) {
        e.preventDefault();
        this.container.classList.add('drag-over');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        // Only remove drag-over if we're leaving the container completely
        if (!this.container.contains(e.relatedTarget)) {
            this.container.classList.remove('drag-over');
        }
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.container.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }
    
    handleFile(file) {
        // Validate file
        const validation = this.validateFile(file);
        if (!validation.valid) {
            this.options.onError(validation.error);
            return;
        }
        
        // Show preview
        this.showPreview(file);
        
        // Upload file
        this.uploadFile(file);
    }
    
    validateFile(file) {
        // Check file type
        if (!this.options.allowedTypes.includes(file.type)) {
            return {
                valid: false,
                error: `Invalid file type. Allowed types: ${this.options.allowedTypes.join(', ')}`
            };
        }
        
        // Check file size
        if (file.size > this.options.maxSize) {
            const maxSizeMB = this.options.maxSize / (1024 * 1024);
            return {
                valid: false,
                error: `File too large. Maximum size: ${maxSizeMB}MB`
            };
        }
        
        return { valid: true };
    }
    
    showPreview(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            // Update container with preview
            this.container.innerHTML = `
                <div class="upload-preview">
                    <img src="${e.target.result}" alt="Preview" class="preview-image">
                    <div class="preview-overlay">
                        <div class="preview-actions">
                            <button type="button" class="btn btn-small btn-secondary remove-preview-btn">
                                Remove
                            </button>
                        </div>
                    </div>
                    <div class="upload-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%"></div>
                        </div>
                        <span class="progress-text">Uploading...</span>
                    </div>
                </div>
            `;
            
            // Add remove functionality
            const removeBtn = this.container.querySelector('.remove-preview-btn');
            if (removeBtn) {
                removeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.resetContainer();
                });
            }
            
            // Animate preview in
            const preview = this.container.querySelector('.upload-preview');
            if (preview) {
                preview.style.opacity = '0';
                preview.style.transform = 'scale(0.9)';
                requestAnimationFrame(() => {
                    preview.style.transition = 'all 300ms ease-in-out';
                    preview.style.opacity = '1';
                    preview.style.transform = 'scale(1)';
                });
            }
        };
        
        reader.readAsDataURL(file);
    }
    
    uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const xhr = new XMLHttpRequest();
        
        // Progress tracking
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                this.options.onProgress(percentComplete);
                this.updateProgress(percentComplete);
            }
        });
        
        // Success handling
        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    this.options.onSuccess(response);
                    this.showUploadSuccess();
                } catch (e) {
                    this.options.onError('Invalid server response');
                    this.showUploadError('Invalid server response');
                }
            } else {
                const error = xhr.responseText || 'Upload failed';
                this.options.onError(error);
                this.showUploadError(error);
            }
        });
        
        // Error handling
        xhr.addEventListener('error', () => {
            this.options.onError('Network error during upload');
            this.showUploadError('Network error during upload');
        });
        
        // Start upload
        xhr.open('POST', this.options.uploadUrl);
        xhr.send(formData);
    }
    
    updateProgress(percent) {
        const progressFill = this.container.querySelector('.progress-fill');
        const progressText = this.container.querySelector('.progress-text');
        
        if (progressFill) {
            progressFill.style.width = `${percent}%`;
        }
        
        if (progressText) {
            progressText.textContent = `Uploading... ${Math.round(percent)}%`;
        }
    }
    
    showUploadSuccess() {
        const progressContainer = this.container.querySelector('.upload-progress');
        if (progressContainer) {
            progressContainer.innerHTML = `
                <div class="upload-success">
                    <span class="success-icon">✅</span>
                    <span class="success-text">Upload complete!</span>
                </div>
            `;
            
            // Hide success message after 2 seconds
            setTimeout(() => {
                if (progressContainer) {
                    progressContainer.style.opacity = '0';
                    setTimeout(() => {
                        if (progressContainer.parentNode) {
                            progressContainer.remove();
                        }
                    }, 300);
                }
            }, 2000);
        }
    }
    
    showUploadError(error) {
        const progressContainer = this.container.querySelector('.upload-progress');
        if (progressContainer) {
            progressContainer.innerHTML = `
                <div class="upload-error">
                    <span class="error-icon">❌</span>
                    <span class="error-text">Upload failed</span>
                    <button type="button" class="btn btn-small retry-btn">Retry</button>
                </div>
            `;
            
            const retryBtn = progressContainer.querySelector('.retry-btn');
            if (retryBtn) {
                retryBtn.addEventListener('click', () => {
                    this.resetContainer();
                });
            }
        }
        
        // Show toast notification
        if (window.appUtils) {
            window.appUtils.showToast(error, 'error');
        }
    }
    
    resetContainer() {
        this.container.innerHTML = `
            <div class="upload-content">
                <span class="upload-icon">📁</span>
                <p class="upload-text">
                    <strong>Click to upload</strong> or drag and drop<br>
                    <small>JPEG, PNG, WebP up to 5MB</small>
                </p>
            </div>
        `;
        
        this.createFileInput();
    }
    
    // Default event handlers
    defaultOnSuccess(response) {
        console.log('Upload successful:', response);
        if (window.appUtils) {
            window.appUtils.showToast('Image uploaded successfully!', 'success');
        }
    }
    
    defaultOnError(error) {
        console.error('Upload error:', error);
        if (window.appUtils) {
            window.appUtils.showToast(error, 'error');
        }
    }
    
    defaultOnProgress(percent) {
        console.log('Upload progress:', percent + '%');
    }
}

// Initialize image upload areas
function initializeImageUpload(container) {
    if (!container) return;
    
    // Get upload URL from data attributes or determine from context
    let uploadUrl = container.dataset.uploadUrl;
    
    if (!uploadUrl) {
        // Try to determine upload URL from page context
        const pathname = window.location.pathname;
        if (pathname.includes('/outfits/')) {
            const outfitId = pathname.split('/')[2];
            uploadUrl = `/api/outfits/${outfitId}/upload-image`;
        } else if (pathname.includes('/components/')) {
            const componentId = pathname.split('/')[2];
            uploadUrl = `/api/components/${componentId}/upload-image`;
        }
    }
    
    if (!uploadUrl) {
        console.warn('No upload URL found for image upload container');
        return;
    }
    
    new ImageUploader(container, {
        uploadUrl: uploadUrl,
        onSuccess: (response) => {
            // Refresh the current view to show the new image
            if (window.location.pathname.includes('/outfits/') || window.location.pathname.includes('/components/')) {
                window.location.reload();
            }
        }
    });
}

// Auto-initialize image upload areas on page load
function initializeAllImageUploads() {
    const containers = document.querySelectorAll('.image-upload-container');
    containers.forEach(container => {
        if (!container.hasAttribute('data-initialized')) {
            initializeImageUpload(container);
            container.setAttribute('data-initialized', 'true');
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAllImageUploads);
} else {
    initializeAllImageUploads();
}

// Re-initialize on HTMX content swaps
document.body.addEventListener('htmx:afterSwap', initializeAllImageUploads);

// CSS for upload components (injected via JavaScript)
const uploadStyles = `
.upload-preview {
    position: relative;
    border-radius: var(--radius-md);
    overflow: hidden;
}

.preview-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
}

.preview-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: flex-start;
    justify-content: flex-end;
    padding: var(--spacing-sm);
    opacity: 0;
    transition: opacity var(--transition-fast);
}

.upload-preview:hover .preview-overlay {
    opacity: 1;
}

.preview-actions {
    display: flex;
    gap: var(--spacing-xs);
}

.upload-progress {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.95);
    padding: var(--spacing-sm);
    text-align: center;
}

.progress-bar {
    width: 100%;
    height: 4px;
    background: #E5E7EB;
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: var(--spacing-xs);
}

.progress-fill {
    height: 100%;
    background: var(--primary-color);
    transition: width 300ms ease-in-out;
}

.progress-text {
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.upload-success,
.upload-error {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-xs);
    flex-wrap: wrap;
}

.upload-success {
    color: var(--success-color);
}

.upload-error {
    color: var(--error-color);
}

.success-icon,
.error-icon {
    font-size: 1rem;
}

.success-text,
.error-text {
    font-size: 0.75rem;
    font-weight: 500;
}

.retry-btn {
    font-size: 0.75rem;
    padding: var(--spacing-xs) var(--spacing-sm);
}

.image-upload-container.drag-over {
    border-color: var(--primary-color);
    background: var(--accent-color);
    transform: scale(1.02);
}

.touching {
    transform: scale(0.98);
    transition: transform 150ms ease-in-out;
}
`;

// Inject styles
if (!document.getElementById('image-upload-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'image-upload-styles';
    styleSheet.textContent = uploadStyles;
    document.head.appendChild(styleSheet);
}

// Export for global use
window.ImageUploader = ImageUploader;
window.initializeImageUpload = initializeImageUpload;