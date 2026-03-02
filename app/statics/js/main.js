// Main JavaScript file

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
    setupEventListeners();
    checkUserAuth();
});

// Initialize all components
function initializeComponents() {
    initMobileMenu();
    initSmoothScroll();
    initFormValidation();
    initCounters();
    initTooltips();
    initDropdowns();
    initModals();
    initTabs();
    initAccordions();
}

// Mobile menu functionality
function initMobileMenu() {
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');

            // Animate hamburger icon
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });

        // Close menu on window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 768) {
                mobileMenu.classList.add('hidden');
                const icon = menuButton.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
    }
}

// Smooth scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            if (href !== '#') {
                e.preventDefault();
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
}

// Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });

        // Real-time validation
        form.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('blur', function() {
                validateField(this);
            });

            field.addEventListener('input', function() {
                removeFieldError(this);
            });
        });
    });
}

// Validate single field
function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const name = field.name;
    const errorDiv = document.getElementById(`${field.id}-error`) || createErrorElement(field);

    let isValid = true;
    let errorMessage = '';

    // Required validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }

    // Email validation
    else if (type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }

    // Phone validation
    else if (name === 'phone' && value) {
        const phoneRegex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid phone number';
        }
    }

    // Password validation
    else if (type === 'password' && value) {
        if (value.length < 8) {
            isValid = false;
            errorMessage = 'Password must be at least 8 characters';
        }
    }

    if (!isValid) {
        field.classList.add('border-red-500');
        errorDiv.textContent = errorMessage;
        errorDiv.classList.remove('hidden');
    } else {
        field.classList.remove('border-red-500');
        errorDiv.classList.add('hidden');
    }

    return isValid;
}

// Create error element for field
function createErrorElement(field) {
    const errorDiv = document.createElement('div');
    errorDiv.id = `${field.id}-error`;
    errorDiv.className = 'text-red-500 text-sm mt-1 hidden';
    field.parentNode.appendChild(errorDiv);
    return errorDiv;
}

// Remove field error
function removeFieldError(field) {
    field.classList.remove('border-red-500');
    const errorDiv = document.getElementById(`${field.id}-error`);
    if (errorDiv) {
        errorDiv.classList.add('hidden');
    }
}

// Validate entire form
function validateForm(form) {
    let isValid = true;
    const fields = form.querySelectorAll('input, textarea, select');

    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    return isValid;
}

// Animated counters
function initCounters() {
    const counters = document.querySelectorAll('[data-counter]');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const duration = parseInt(counter.getAttribute('data-duration')) || 2000;

                animateCounter(counter, 0, target, duration);
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => observer.observe(counter));
}

// Animate single counter
function animateCounter(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        element.textContent = Math.round(current);

        if (current >= end) {
            element.textContent = end;
            clearInterval(timer);
        }
    }, 16);
}

// Tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');

    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const element = e.target;
    const text = element.getAttribute('data-tooltip');

    const tooltip = document.createElement('div');
    tooltip.className = 'absolute bg-gray-900 text-white text-sm px-2 py-1 rounded z-50';
    tooltip.textContent = text;
    tooltip.setAttribute('data-tooltip-instance', '');

    const rect = element.getBoundingClientRect();
    tooltip.style.top = rect.top - 30 + 'px';
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';

    document.body.appendChild(tooltip);
}

function hideTooltip(e) {
    const tooltip = document.querySelector('[data-tooltip-instance]');
    if (tooltip) {
        tooltip.remove();
    }
}

// Dropdowns
function initDropdowns() {
    document.querySelectorAll('[data-dropdown-button]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdownId = this.getAttribute('data-dropdown');
            const dropdown = document.getElementById(dropdownId);

            if (dropdown) {
                dropdown.classList.toggle('hidden');
            }
        });
    });

    // Close dropdowns on outside click
    document.addEventListener('click', function() {
        document.querySelectorAll('[data-dropdown]').forEach(dropdown => {
            dropdown.classList.add('hidden');
        });
    });
}

// Modals
function initModals() {
    document.querySelectorAll('[data-modal-open]').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-open');
            openModal(modalId);
        });
    });

    document.querySelectorAll('[data-modal-close]').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-close');
            closeModal(modalId);
        });
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

// Tabs
function initTabs() {
    document.querySelectorAll('[data-tab-group]').forEach(group => {
        const tabs = group.querySelectorAll('[data-tab]');
        const panes = group.querySelectorAll('[data-tab-pane]');

        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabId = this.getAttribute('data-tab');

                // Update tabs
                tabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');

                // Update panes
                panes.forEach(pane => {
                    if (pane.getAttribute('data-tab-pane') === tabId) {
                        pane.classList.remove('hidden');
                    } else {
                        pane.classList.add('hidden');
                    }
                });
            });
        });
    });
}

// Accordions
function initAccordions() {
    document.querySelectorAll('[data-accordion]').forEach(accordion => {
        const items = accordion.querySelectorAll('[data-accordion-item]');

        items.forEach(item => {
            const header = item.querySelector('[data-accordion-header]');
            const content = item.querySelector('[data-accordion-content]');

            header.addEventListener('click', function() {
                const isOpen = !content.classList.contains('hidden');

                // Close all items
                items.forEach(i => {
                    i.querySelector('[data-accordion-content]').classList.add('hidden');
                });

                // Open current item if it was closed
                if (!isOpen) {
                    content.classList.remove('hidden');
                }
            });
        });
    });
}

// Toast notifications
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-left`;

    // Set background color based on type
    switch(type) {
        case 'success':
            toast.classList.add('bg-green-500', 'text-white');
            break;
        case 'error':
            toast.classList.add('bg-red-500', 'text-white');
            break;
        case 'warning':
            toast.classList.add('bg-yellow-500', 'text-white');
            break;
        default:
            toast.classList.add('bg-blue-500', 'text-white');
    }

    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, duration);
}

// Loading spinner
function showLoading(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.disabled = true;
        const originalText = element.textContent;
        element.setAttribute('data-original-text', originalText);
        element.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
    }
}

function hideLoading(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.disabled = false;
        const originalText = element.getAttribute('data-original-text');
        element.textContent = originalText;
    }
}

// API calls
async function apiCall(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'API call failed');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

// Check user authentication
async function checkUserAuth() {
    const token = localStorage.getItem('access_token');
    const protectedElements = document.querySelectorAll('[data-auth-required]');
    const guestElements = document.querySelectorAll('[data-guest-only]');

    if (token) {
        try {
            // Verify token
            const user = await apiCall('/api/auth/me');

            // Show protected elements
            protectedElements.forEach(el => el.classList.remove('hidden'));
            guestElements.forEach(el => el.classList.add('hidden'));

            // Update user info
            updateUserInfo(user);
        } catch (error) {
            // Token invalid
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');

            protectedElements.forEach(el => el.classList.add('hidden'));
            guestElements.forEach(el => el.classList.remove('hidden'));
        }
    } else {
        protectedElements.forEach(el => el.classList.add('hidden'));
        guestElements.forEach(el => el.classList.remove('hidden'));
    }
}

// Update user info in UI
function updateUserInfo(user) {
    const userElements = document.querySelectorAll('[data-user-field]');

    userElements.forEach(el => {
        const field = el.getAttribute('data-user-field');
        if (user[field]) {
            el.textContent = user[field];
        }
    });
}

// Search functionality
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (searchInput && searchResults) {
        let debounceTimer;

        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = this.value.trim();

            if (query.length < 2) {
                searchResults.classList.add('hidden');
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const results = await apiCall(`/api/search?q=${encodeURIComponent(query)}`);
                    displaySearchResults(results);
                } catch (error) {
                    console.error('Search failed:', error);
                }
            }, 300);
        });
    }
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('search-results');
    if (!searchResults) return;

    searchResults.innerHTML = '';

    if (results.length === 0) {
        searchResults.innerHTML = '<div class="p-4 text-gray-500">No results found</div>';
    } else {
        results.forEach(result => {
            const item = document.createElement('a');
            item.href = result.url;
            item.className = 'block p-4 hover:bg-gray-50 border-b last:border-b-0';
            item.innerHTML = `
                <div class="font-semibold">${result.title}</div>
                <div class="text-sm text-gray-600">${result.description}</div>
            `;
            searchResults.appendChild(item);
        });
    }

    searchResults.classList.remove('hidden');
}

// Export functions for use in other scripts
window.showToast = showToast;
window.apiCall = apiCall;
window.showLoading = showLoading;
window.hideLoading = hideLoading;