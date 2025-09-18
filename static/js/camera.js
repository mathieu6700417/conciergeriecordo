// Camera and photo handling functionality

class CameraManager {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.stream = null;
        this.isInitialized = false;
        this.photoDataUrl = null;

        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.video = document.getElementById('camera-video');
        this.canvas = document.getElementById('camera-canvas');
        this.previewContainer = document.getElementById('photo-preview');
        this.previewImg = document.getElementById('preview-img');

        this.startCameraBtn = document.getElementById('btn-start-camera');
        this.takePhotoBtn = document.getElementById('btn-take-photo');
        this.retryPhotoBtn = document.getElementById('btn-retry-photo');
        this.confirmPhotoBtn = document.getElementById('btn-confirm-photo');
        this.fileInput = document.getElementById('file-input');
    }

    bindEvents() {
        if (this.startCameraBtn) {
            this.startCameraBtn.addEventListener('click', () => this.startCamera());
        }

        if (this.takePhotoBtn) {
            this.takePhotoBtn.addEventListener('click', () => this.takePhoto());
        }

        if (this.retryPhotoBtn) {
            this.retryPhotoBtn.addEventListener('click', () => this.retryPhoto());
        }

        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        // Handle modal close
        const photoModal = document.getElementById('photoModal');
        if (photoModal) {
            photoModal.addEventListener('hidden.bs.modal', () => this.stopCamera());
        }
    }

    async startCamera() {
        try {
            showLoading();

            // Check if camera is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Camera not supported on this device');
            }

            // Request camera access
            const constraints = {
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'environment' // Use back camera on mobile
                }
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;

            // Wait for video to load
            await new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve();
                };
            });

            this.showCameraControls();
            this.isInitialized = true;

        } catch (error) {
            console.error('Error starting camera:', error);

            let errorMessage = 'Impossible d\'accéder à la caméra. ';
            if (error.name === 'NotAllowedError') {
                errorMessage += 'Veuillez autoriser l\'accès à la caméra.';
            } else if (error.name === 'NotFoundError') {
                errorMessage += 'Aucune caméra trouvée sur cet appareil.';
            } else {
                errorMessage += 'Utilisez le sélecteur de fichier ci-dessous.';
            }

            showToast(errorMessage, 'warning');
        } finally {
            hideLoading();
        }
    }

    showCameraControls() {
        if (this.video) this.video.style.display = 'block';
        if (this.startCameraBtn) this.startCameraBtn.style.display = 'none';
        if (this.takePhotoBtn) this.takePhotoBtn.style.display = 'inline-block';
        if (this.previewContainer) this.previewContainer.style.display = 'none';
        if (this.retryPhotoBtn) this.retryPhotoBtn.style.display = 'none';
    }

    takePhoto() {
        if (!this.isInitialized || !this.video) {
            showToast('Caméra non initialisée', 'error');
            return;
        }

        try {
            // Set canvas dimensions to video dimensions
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;

            // Draw video frame to canvas
            const ctx = this.canvas.getContext('2d');
            ctx.drawImage(this.video, 0, 0);

            // Get image data as base64
            this.photoDataUrl = this.canvas.toDataURL('image/jpeg', 0.8);

            // Show preview
            this.showPhotoPreview();

        } catch (error) {
            console.error('Error taking photo:', error);
            showToast('Erreur lors de la prise de photo', 'error');
        }
    }

    showPhotoPreview() {
        if (this.previewImg && this.photoDataUrl) {
            this.previewImg.src = this.photoDataUrl;
        }

        if (this.video) this.video.style.display = 'none';
        if (this.previewContainer) this.previewContainer.style.display = 'block';
        if (this.takePhotoBtn) this.takePhotoBtn.style.display = 'none';
        if (this.retryPhotoBtn) this.retryPhotoBtn.style.display = 'inline-block';
        if (this.confirmPhotoBtn) this.confirmPhotoBtn.disabled = false;
    }

    retryPhoto() {
        this.photoDataUrl = null;
        this.showCameraControls();
        if (this.confirmPhotoBtn) this.confirmPhotoBtn.disabled = true;
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            showToast('Veuillez sélectionner un fichier image', 'error');
            return;
        }

        // Validate file size (5MB max)
        const maxSize = 5 * 1024 * 1024; // 5MB
        if (file.size > maxSize) {
            showToast('L\'image est trop volumineuse (max 5MB)', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.photoDataUrl = e.target.result;
            this.showPhotoPreview();

            // Hide camera controls since we're using file input
            if (this.video) this.video.style.display = 'none';
            if (this.startCameraBtn) this.startCameraBtn.style.display = 'none';
            if (this.takePhotoBtn) this.takePhotoBtn.style.display = 'none';
        };

        reader.readAsDataURL(file);
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        if (this.video) {
            this.video.srcObject = null;
            this.video.style.display = 'none';
        }

        this.isInitialized = false;
        this.photoDataUrl = null;

        // Reset UI
        if (this.startCameraBtn) this.startCameraBtn.style.display = 'inline-block';
        if (this.takePhotoBtn) this.takePhotoBtn.style.display = 'none';
        if (this.retryPhotoBtn) this.retryPhotoBtn.style.display = 'none';
        if (this.previewContainer) this.previewContainer.style.display = 'none';
        if (this.confirmPhotoBtn) this.confirmPhotoBtn.disabled = true;
        if (this.fileInput) this.fileInput.value = '';
    }

    getPhotoDataUrl() {
        return this.photoDataUrl;
    }

    hasPhoto() {
        return !!this.photoDataUrl;
    }

    reset() {
        this.stopCamera();
    }
}

// Initialize camera manager when DOM is loaded
let cameraManager;

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the order page
    if (document.getElementById('photoModal')) {
        cameraManager = new CameraManager();

        // Make camera manager globally available
        window.cameraManager = cameraManager;
    }

    // Handle modal reset when opened
    const photoModal = document.getElementById('photoModal');
    if (photoModal) {
        photoModal.addEventListener('show.bs.modal', function() {
            if (cameraManager) {
                cameraManager.reset();
            }
        });
    }
});

// Utility function to compress image
function compressImage(dataUrl, quality = 0.8, maxWidth = 1024, maxHeight = 1024) {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();

        img.onload = function() {
            // Calculate new dimensions
            let { width, height } = img;

            if (width > maxWidth || height > maxHeight) {
                const ratio = Math.min(maxWidth / width, maxHeight / height);
                width *= ratio;
                height *= ratio;
            }

            canvas.width = width;
            canvas.height = height;

            // Draw and compress
            ctx.drawImage(img, 0, 0, width, height);
            const compressedDataUrl = canvas.toDataURL('image/jpeg', quality);
            resolve(compressedDataUrl);
        };

        img.src = dataUrl;
    });
}

// Export for use in other modules
window.compressImage = compressImage;