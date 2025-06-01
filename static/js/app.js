// MikroTik Hotspot User Generator - JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeFormValidation();
    initializeUserCounter();
    initializePasswordValidation();
    initializeCopyToClipboard();
});

// Form validation and user experience enhancements
function initializeFormValidation() {
    const form = document.getElementById('generatorForm');
    if (!form) return;

    // Real-time validation
    const inputs = form.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });

    // IP Address validation
    const ipInput = document.getElementById('base_ip');
    if (ipInput) {
        ipInput.addEventListener('input', validateIPAddress);
    }

    // Number range validation
    const startNumber = document.getElementById('start_number');
    const endNumber = document.getElementById('end_number');
    if (startNumber && endNumber) {
        startNumber.addEventListener('input', validateNumberRange);
        endNumber.addEventListener('input', validateNumberRange);
    }

    // Character type validation
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', validateCharacterTypes);
    });

    // Form submission
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            showAlert('Please fix the validation errors before submitting.', 'error');
        } else {
            showLoadingState(e.target.querySelector('button[type="submit"]'));
        }
    });
}

// User counter functionality
function initializeUserCounter() {
    const startNumber = document.getElementById('start_number');
    const endNumber = document.getElementById('end_number');
    const userCount = document.getElementById('userCount');

    if (!startNumber || !endNumber || !userCount) return;

    function updateUserCount() {
        const start = parseInt(startNumber.value) || 1;
        const end = parseInt(endNumber.value) || 1;
        const count = Math.max(0, end - start + 1);
        userCount.textContent = count;
        
        // Update color based on count
        if (count > 100) {
            userCount.className = 'text-warning fw-bold';
        } else if (count > 50) {
            userCount.className = 'text-info fw-bold';
        } else {
            userCount.className = 'text-primary fw-bold';
        }
    }

    startNumber.addEventListener('input', updateUserCount);
    endNumber.addEventListener('input', updateUserCount);
    
    // Initial update
    updateUserCount();
}

// Password validation
function initializePasswordValidation() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            validatePasswordStrength(this);
        });
    });

    // Confirm password validation
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    
    if (password && confirmPassword) {
        confirmPassword.addEventListener('input', function() {
            validatePasswordMatch(password, confirmPassword);
        });
    }
}

// Copy to clipboard functionality
function initializeCopyToClipboard() {
    // Auto-select textarea content on focus
    const textarea = document.getElementById('commandsTextarea');
    if (textarea) {
        textarea.addEventListener('focus', function() {
            this.select();
        });
    }
}

// Copy to clipboard function
function copyToClipboard() {
    const textarea = document.getElementById('commandsTextarea');
    const button = document.getElementById('copyButton');
    
    if (!textarea || !button) return;

    try {
        textarea.select();
        document.execCommand('copy');
        
        // Show success feedback
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
        button.classList.remove('btn-light');
        button.classList.add('btn-success');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-light');
        }, 2000);
        
        showAlert('Commands copied to clipboard!', 'success');
    } catch (err) {
        showAlert('Failed to copy to clipboard. Please select and copy manually.', 'error');
    }
}

// Validation functions
function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required.');
        return false;
    }
    
    if (field.type === 'email' && value && !isValidEmail(value)) {
        showFieldError(field, 'Please enter a valid email address.');
        return false;
    }
    
    if (field.type === 'number') {
        const min = parseInt(field.getAttribute('min'));
        const max = parseInt(field.getAttribute('max'));
        const numValue = parseInt(value);
        
        if (min !== null && numValue < min) {
            showFieldError(field, `Value must be at least ${min}.`);
            return false;
        }
        
        if (max !== null && numValue > max) {
            showFieldError(field, `Value must be no more than ${max}.`);
            return false;
        }
    }
    
    clearFieldError(field);
    return true;
}

function validateIPAddress(event) {
    const field = event.target;
    const value = field.value.trim();
    
    if (!value) return;
    
    // Check for partial IP format (e.g., 192.168.1)
    const ipPattern = /^(\d{1,3}\.){2}\d{1,3}$/;
    if (!ipPattern.test(value)) {
        showFieldError(field, 'Please enter a valid IP address format (e.g., 192.168.1)');
        return false;
    }
    
    // Validate each octet
    const octets = value.split('.');
    for (let octet of octets) {
        const num = parseInt(octet);
        if (num < 0 || num > 255) {
            showFieldError(field, 'Each part of the IP address must be between 0 and 255.');
            return false;
        }
    }
    
    clearFieldError(field);
    return true;
}

function validateNumberRange() {
    const startNumber = document.getElementById('start_number');
    const endNumber = document.getElementById('end_number');
    
    if (!startNumber || !endNumber) return;
    
    const start = parseInt(startNumber.value);
    const end = parseInt(endNumber.value);
    
    if (start && end && start > end) {
        showFieldError(endNumber, 'End number must be greater than or equal to start number.');
        return false;
    }
    
    clearFieldError(startNumber);
    clearFieldError(endNumber);
    return true;
}

function validateCharacterTypes() {
    const checkboxes = document.querySelectorAll('input[name="uppercase"], input[name="lowercase"], input[name="numbers"], input[name="special"]');
    const checked = Array.from(checkboxes).some(cb => cb.checked);
    
    const container = checkboxes[0].closest('.mb-3');
    const errorElement = container.querySelector('.invalid-feedback');
    
    if (!checked) {
        if (!errorElement) {
            const error = document.createElement('div');
            error.className = 'invalid-feedback d-block';
            error.textContent = 'Please select at least one character type.';
            container.appendChild(error);
        }
        return false;
    } else {
        if (errorElement) {
            errorElement.remove();
        }
        return true;
    }
}

function validatePasswordStrength(passwordField) {
    const password = passwordField.value;
    const minLength = 6;
    
    if (password.length < minLength) {
        showFieldError(passwordField, `Password must be at least ${minLength} characters long.`);
        return false;
    }
    
    clearFieldError(passwordField);
    return true;
}

function validatePasswordMatch(passwordField, confirmField) {
    if (passwordField.value !== confirmField.value) {
        showFieldError(confirmField, 'Passwords do not match.');
        return false;
    }
    
    clearFieldError(confirmField);
    return true;
}

function validateForm() {
    const form = document.getElementById('generatorForm');
    if (!form) return true;
    
    let isValid = true;
    
    // Validate all required fields
    const requiredFields = form.querySelectorAll('input[required]');
    requiredFields.forEach(field => {
        if (!validateField({ target: field })) {
            isValid = false;
        }
    });
    
    // Validate character types
    if (!validateCharacterTypes()) {
        isValid = false;
    }
    
    // Validate number range
    if (!validateNumberRange()) {
        isValid = false;
    }
    
    return isValid;
}

// Helper functions
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorElement = document.createElement('div');
    errorElement.className = 'invalid-feedback';
    errorElement.textContent = message;
    
    field.parentNode.appendChild(errorElement);
}

function clearFieldError(field) {
    if (typeof field === 'object' && field.target) {
        field = field.target;
    }
    
    field.classList.remove('is-invalid');
    
    const errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

function isValidEmail(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}

function showAlert(message, type) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main container
    const container = document.querySelector('main.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

function showLoadingState(button) {
    button.classList.add('btn-loading');
    button.disabled = true;
}

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-dismissible)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter to submit form
    if (e.ctrlKey && e.key === 'Enter') {
        const form = document.getElementById('generatorForm');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }
    
    // Ctrl+C on textarea to copy
    if (e.ctrlKey && e.key === 'c') {
        const textarea = document.getElementById('commandsTextarea');
        if (textarea && document.activeElement === textarea) {
            copyToClipboard();
        }
    }
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const href = this.getAttribute('href');
        if (href && href !== '#') {
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});
