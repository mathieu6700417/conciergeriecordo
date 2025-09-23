// Main JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Loading utility
    window.showLoading = function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    };

    window.hideLoading = function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    };

    // Toast notification utility - disabled
    window.showToast = function(message, type = 'info') {
        // Notifications are disabled - do nothing
        console.log(`[${type}] ${message}`);
    };

    // API utility functions
    window.api = {
        async call(endpoint, options = {}) {
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            const finalOptions = { ...defaultOptions, ...options };

            try {
                const response = await fetch(`/api${endpoint}`, finalOptions);
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                }

                return data;
            } catch (error) {
                console.error('API call failed:', error);
                throw error;
            }
        },

        async get(endpoint) {
            return this.call(endpoint, { method: 'GET' });
        },

        async post(endpoint, data) {
            return this.call(endpoint, {
                method: 'POST',
                body: JSON.stringify(data),
            });
        },

        async uploadPhoto(photoDataUrl) {
            return this.post('/upload-photo', { photo: photoDataUrl });
        }
    };

    // Format price utility
    window.formatPrice = function(price) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'EUR'
        }).format(price);
    };

    // Validate form utility
    window.validateForm = function(form) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        });

        // Validate email
        const emailInputs = form.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            if (input.value && !isValidEmail(input.value)) {
                input.classList.add('is-invalid');
                isValid = false;
            }
        });

        return isValid;
    };

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Remove validation classes when user starts typing
    document.addEventListener('input', function(e) {
        if (e.target.matches('input, select, textarea')) {
            e.target.classList.remove('is-invalid', 'is-valid');
        }
    });

    // Handle navigation active states
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });

    // Mobile navigation improvements
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking on a link
        navbarCollapse.addEventListener('click', function(e) {
            if (e.target.classList.contains('nav-link')) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                    toggle: false
                });
                bsCollapse.hide();
            }
        });
    }

    // Initialize tooltips if they exist
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers if they exist
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});