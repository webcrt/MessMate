// Mess Management System - Main JavaScript

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize interactive elements
    initializeInteractiveElements();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize auto-dismiss alerts
    initializeAlerts();
    
    console.log('Mess Management System initialized successfully');
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize form validation
function initializeFormValidation() {
    // Custom validation for rating forms
    const ratingForms = document.querySelectorAll('form[action*="feedback"]');
    ratingForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const rating = form.querySelector('input[name="rating"]:checked');
            if (!rating) {
                e.preventDefault();
                showAlert('Please select a rating before submitting feedback.', 'warning');
                return false;
            }
        });
    });
    
    // Date validation for meal confirmation
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);
        
        // Set maximum date to 3 days from now for meal confirmations
        if (input.closest('.meal-confirmation, #meal_confirmation')) {
            const maxDate = new Date();
            maxDate.setDate(maxDate.getDate() + 3);
            input.setAttribute('max', maxDate.toISOString().split('T')[0]);
        }
    });
    
    // File upload validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check file size (16MB limit)
                if (file.size > 16 * 1024 * 1024) {
                    showAlert('File size must be less than 16MB.', 'error');
                    input.value = '';
                    return;
                }
                
                // Check file type
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!allowedTypes.includes(file.type)) {
                    showAlert('Please upload only JPG, PNG, or GIF images.', 'error');
                    input.value = '';
                    return;
                }
            }
        });
    });
}

// Initialize interactive elements
function initializeInteractiveElements() {
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
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
    
    // Rating button interactions
    const ratingButtons = document.querySelectorAll('.rating-btn');
    ratingButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from siblings
            const siblings = this.parentNode.parentNode.querySelectorAll('.rating-btn');
            siblings.forEach(sibling => sibling.classList.remove('rating-active'));
            
            // Add active class to clicked button
            this.classList.add('rating-active');
            
            // Add visual feedback
            this.style.transform = 'scale(1.1)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
        });
    });
    
    // Meal type filter functionality
    const filterButtons = document.querySelectorAll('[onclick*="filterMeals"]');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active state
            const siblings = this.parentNode.querySelectorAll('.btn');
            siblings.forEach(sibling => sibling.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Auto-refresh data on dashboard pages
    if (window.location.pathname.includes('dashboard')) {
        // Refresh every 5 minutes
        setInterval(refreshDashboardData, 5 * 60 * 1000);
    }
}

// Initialize animations
function initializeAnimations() {
    // Fade in cards on page load
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Animate statistics on dashboard
    animateStatistics();
}

// Initialize auto-dismiss alerts
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 500);
            }
        }, 5000);
    });
}

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main content
    const mainContent = document.querySelector('.main-content') || document.body;
    const container = document.createElement('div');
    container.className = 'container mt-3';
    container.appendChild(alertContainer);
    mainContent.insertBefore(container, mainContent.firstChild);
    
    // Auto-dismiss
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 5000);
}

// Image preview functionality
function previewImage(event) {
    const input = event.target;
    const preview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('preview');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            preview.style.display = 'block';
            preview.style.opacity = '0';
            setTimeout(() => {
                preview.style.transition = 'opacity 0.3s ease';
                preview.style.opacity = '1';
            }, 10);
        };
        
        reader.readAsDataURL(input.files[0]);
    } else {
        preview.style.display = 'none';
    }
}

// Dashboard data refresh
function refreshDashboardData() {
    // This would typically make AJAX calls to refresh dashboard data
    // For now, we'll just show a subtle notification
    const timestamp = new Date().toLocaleTimeString();
    console.log(`Dashboard data refreshed at ${timestamp}`);
}

// Animate statistics counters
function animateStatistics() {
    const statNumbers = document.querySelectorAll('.stat-item h3, .h1, .h2, .h3, .h4, .display-4');
    
    statNumbers.forEach(stat => {
        const text = stat.textContent;
        const number = parseInt(text.replace(/[^\d]/g, ''));
        
        if (number && number > 0 && number < 10000) {
            animateCounter(stat, 0, number, 1500);
        }
    });
}

// Counter animation function
function animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    const originalText = element.textContent;
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(progress * (end - start) + start);
        element.textContent = originalText.replace(/\d+/, current);
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Meal filtering functionality
function filterMeals(type) {
    const cards = document.querySelectorAll('.meal-card');
    const buttons = document.querySelectorAll('.btn-group .btn');
    
    // Update button states
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Filter cards with animation
    cards.forEach((card, index) => {
        if (type === 'all' || card.dataset.mealType === type) {
            setTimeout(() => {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.3s ease';
            }, index * 50);
        } else {
            card.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                card.style.display = 'none';
            }, 300);
        }
    });
}

// Form submission with loading state
function submitFormWithLoading(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    
    // Simulate form processing (replace with actual form submission)
    setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }, 2000);
}

// Enhanced search functionality
function enhancedSearch(searchTerm, targetElements) {
    const term = searchTerm.toLowerCase();
    
    targetElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        const match = text.includes(term);
        
        element.style.display = match ? 'block' : 'none';
        
        if (match && term.length > 0) {
            // Highlight matching text
            highlightText(element, searchTerm);
        } else {
            // Remove highlights
            removeHighlights(element);
        }
    });
}

// Text highlighting function
function highlightText(element, searchTerm) {
    const text = element.textContent;
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    const highlightedText = text.replace(regex, '<mark>$1</mark>');
    element.innerHTML = highlightedText;
}

// Remove text highlights
function removeHighlights(element) {
    const marks = element.querySelectorAll('mark');
    marks.forEach(mark => {
        mark.outerHTML = mark.textContent;
    });
}

// Local storage utilities
const Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('Local storage not available:', e);
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn('Error reading from local storage:', e);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('Error removing from local storage:', e);
        }
    }
};

// User preferences management
const UserPreferences = {
    save: function(preferences) {
        Storage.set('userPreferences', preferences);
    },
    
    load: function() {
        return Storage.get('userPreferences', {
            theme: 'auto',
            notifications: true,
            autoRefresh: true
        });
    },
    
    apply: function() {
        const prefs = this.load();
        
        // Apply theme
        if (prefs.theme === 'dark') {
            document.body.classList.add('dark-theme');
        }
        
        // Apply other preferences
        if (!prefs.autoRefresh) {
            clearInterval(window.dashboardRefreshInterval);
        }
    }
};

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showAlert('An unexpected error occurred. Please refresh the page.', 'error');
});

// Unhandled promise rejection handling
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showAlert('A network error occurred. Please check your connection.', 'error');
    e.preventDefault();
});

// Performance monitoring
const Performance = {
    mark: function(name) {
        if (window.performance && window.performance.mark) {
            window.performance.mark(name);
        }
    },
    
    measure: function(name, startMark, endMark) {
        if (window.performance && window.performance.measure) {
            try {
                window.performance.measure(name, startMark, endMark);
                const measures = window.performance.getEntriesByName(name);
                if (measures.length > 0) {
                    console.log(`${name}: ${measures[0].duration.toFixed(2)}ms`);
                }
            } catch (e) {
                console.warn('Performance measurement failed:', e);
            }
        }
    }
};

// Mark page load start
Performance.mark('pageLoadStart');

// Mark when everything is loaded
window.addEventListener('load', function() {
    Performance.mark('pageLoadEnd');
    Performance.measure('pageLoadTime', 'pageLoadStart', 'pageLoadEnd');
});

// Export functions for global use
window.MessManagement = {
    showAlert,
    previewImage,
    filterMeals,
    submitFormWithLoading,
    enhancedSearch,
    Storage,
    UserPreferences,
    Performance
};
