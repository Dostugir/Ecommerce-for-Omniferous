// Main JavaScript file for Omniferous

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeSearch();
    initializeCart();
    initializeForms();
    initializeAnimations();
    initializeStripe();
});

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="query"]');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            }
        });
    }
}

// AJAX search function
function performSearch(query) {
    fetch(`/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

// Display search results
function displaySearchResults(results) {
    // Implementation for displaying search results
    console.log('Search results:', results);
}

// Cart functionality
function initializeCart() {
    // Update cart item quantity
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            updateCartItem(this);
        });
    });

    // Remove cart item
    const removeButtons = document.querySelectorAll('.remove-cart-item');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            removeCartItem(this);
        });
    });
}

// Update cart item
function updateCartItem(input) {
    const form = input.closest('form');
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Cart update error:', error);
    });
}

// Remove cart item
function removeCartItem(button) {
    if (confirm('Are you sure you want to remove this item?')) {
        const form = button.closest('form');
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            }
        })
        .catch(error => {
            console.error('Cart remove error:', error);
        });
    }
}

// Form validation and enhancement
function initializeForms() {
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="loading"></span> Processing...';
            }
        });
    });

    // Form validation
    const requiredFields = document.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
    });

    // Register form enhancements: password strength and toggle visibility
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        const password1 = registerForm.querySelector('input[name="password1"]');
        const password2 = registerForm.querySelector('input[name="password2"]');
        const strengthBar = document.getElementById('password-strength');
        const toggle = document.getElementById('toggle-password-visibility');

        if (password1 && strengthBar) {
            password1.addEventListener('input', function() {
                const score = scorePassword(password1.value);
                strengthBar.style.width = `${score}%`;
                strengthBar.className = 'progress-bar';
                if (score < 40) {
                    strengthBar.classList.add('bg-danger');
                } else if (score < 70) {
                    strengthBar.classList.add('bg-warning');
                } else {
                    strengthBar.classList.add('bg-success');
                }
            });
        }

        if (toggle) {
            toggle.addEventListener('change', function() {
                const type = this.checked ? 'text' : 'password';
                if (password1) password1.type = type;
                if (password2) password2.type = type;
            });
        }

        if (password2) {
            password2.addEventListener('input', function() {
                if (password1 && password2.value !== password1.value) {
                    password2.setCustomValidity('Passwords do not match');
                } else {
                    password2.setCustomValidity('');
                }
            });
        }
    }
}

// Field validation
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    let isValid = true;
    let errorMessage = '';

    // Remove existing error styling
    field.classList.remove('is-invalid');
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }

    // Validation rules
    switch (fieldName) {
        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address.';
            }
            break;
        case 'phone':
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phoneRegex.test(value.replace(/\s/g, ''))) {
                isValid = false;
                errorMessage = 'Please enter a valid phone number.';
            }
            break;
        case 'quantity':
            if (value < 1) {
                isValid = false;
                errorMessage = 'Quantity must be at least 1.';
            }
            break;
        default:
            if (field.hasAttribute('required') && !value) {
                isValid = false;
                errorMessage = 'This field is required.';
            }
    }

    // Apply validation result
    if (!isValid) {
        field.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = errorMessage;
        field.parentNode.appendChild(errorDiv);
    }

    return isValid;
}

// Animations
function initializeAnimations() {
    // Fade in elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe all cards and sections
    const animatedElements = document.querySelectorAll('.card, section');
    animatedElements.forEach(el => {
        observer.observe(el);
    });

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
}

// Simple password strength estimator (0-100)
function scorePassword(pass) {
    if (!pass) return 0;
    let score = 0;
    const letters = {};
    for (let i = 0; i < pass.length; i++) {
        letters[pass[i]] = (letters[pass[i]] || 0) + 1;
        score += 5.0 / letters[pass[i]];
    }
    const variations = {
        digits: /\d/.test(pass),
        lower: /[a-z]/.test(pass),
        upper: /[A-Z]/.test(pass),
        nonWords: /[^\w]/.test(pass)
    };
    let variationCount = 0;
    for (let check in variations) variationCount += variations[check] ? 1 : 0;
    score += (variationCount - 1) * 10;
    return Math.max(0, Math.min(100, Math.round(score)));
}

// Stripe payment integration
function initializeStripe() {
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();

    // Create card element
    const cardElement = document.getElementById('card-element');
    if (cardElement) {
        const card = elements.create('card', {
            style: {
                base: {
                    fontSize: '16px',
                    color: '#424770',
                    '::placeholder': {
                        color: '#aab7c4',
                    },
                },
                invalid: {
                    color: '#9e2146',
                },
            },
        });

        card.mount('#card-element');

        // Handle form submission
        const form = document.getElementById('payment-form');
        if (form) {
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                handlePayment(stripe, card);
            });
        }
    }
}

// Handle payment submission
function handlePayment(stripe, card) {
    const form = document.getElementById('payment-form');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Disable submit button
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="loading"></span> Processing...';

    // Create payment method
    stripe.createPaymentMethod({
        type: 'card',
        card: card,
    }).then(function(result) {
        if (result.error) {
            // Handle error
            const errorElement = document.getElementById('card-errors');
            errorElement.textContent = result.error.message;
            submitButton.disabled = false;
            submitButton.textContent = 'Pay Now';
        } else {
            // Send payment method to server
            const formData = new FormData(form);
            formData.append('payment_method_id', result.paymentMethod.id);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    const errorElement = document.getElementById('card-errors');
                    errorElement.textContent = data.error;
                    submitButton.disabled = false;
                    submitButton.textContent = 'Pay Now';
                }
            })
            .catch(error => {
                console.error('Payment error:', error);
                submitButton.disabled = false;
                submitButton.textContent = 'Pay Now';
            });
        }
    });
}

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'BDT'
    }).format(amount);
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export functions for global use
window.Omniferous = {
    showNotification,
    formatCurrency,
    debounce,
    throttle
};
