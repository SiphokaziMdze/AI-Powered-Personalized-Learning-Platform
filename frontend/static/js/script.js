// frontend/static/js/script.js - COMPLETELY FIXED

// ============ Wait for DOM to be fully loaded ============
document.addEventListener('DOMContentLoaded', function() {
    console.log('EduCore AI - Script loaded successfully! 🎓');
    
    // ============ Modal Elements ============
    const modalOverlay = document.getElementById('modalOverlay');
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');

    // Check if modals exist
    if (!modalOverlay || !loginModal || !signupModal) {
        console.log('Modals not found on this page');
        return;
    }

    // ============ Modal Functions ============
    function showModal(modal) {
        if (!modal || !modalOverlay) return;
        
        modalOverlay.hidden = false;
        modalOverlay.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    function hideModal(modal) {
        if (!modal || !modalOverlay) return;
        
        modal.setAttribute('aria-hidden', 'true');
        modal.style.display = 'none';
        modalOverlay.hidden = true;
        modalOverlay.style.display = 'none';
        document.body.style.overflow = '';
    }

    function hideAllModals() {
        hideModal(loginModal);
        hideModal(signupModal);
    }

    // ============ Button Event Listeners ============
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const getStartedBtn = document.getElementById('getStartedBtn');
    const startLearningBtn = document.getElementById('startLearningBtn');

    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            hideAllModals();
            showModal(loginModal);
        });
    }

    if (signupBtn) {
        signupBtn.addEventListener('click', function(e) {
            e.preventDefault();
            hideAllModals();
            showModal(signupModal);
        });
    }

    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', function(e) {
            e.preventDefault();
            hideAllModals();
            showModal(signupModal);
        });
    }

    if (startLearningBtn) {
        startLearningBtn.addEventListener('click', function(e) {
            e.preventDefault();
            hideAllModals();
            showModal(signupModal);
        });
    }

    // ============ Close Button Listeners ============
    const closeLogin = document.getElementById('closeLogin');
    const closeSignup = document.getElementById('closeSignup');

    if (closeLogin) {
        closeLogin.addEventListener('click', function(e) {
            e.preventDefault();
            hideModal(loginModal);
        });
    }

    if (closeSignup) {
        closeSignup.addEventListener('click', function(e) {
            e.preventDefault();
            hideModal(signupModal);
        });
    }

    // ============ Switch Between Modals ============
    const switchToSignup = document.getElementById('switchToSignup');
    const switchToLogin = document.getElementById('switchToLogin');

    if (switchToSignup) {
        switchToSignup.addEventListener('click', function(e) {
            e.preventDefault();
            hideModal(loginModal);
            showModal(signupModal);
        });
    }

    if (switchToLogin) {
        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            hideModal(signupModal);
            showModal(loginModal);
        });
    }

    // ============ Close modal when clicking overlay ============
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function(e) {
            if (e.target === modalOverlay) {
                hideAllModals();
            }
        });
    }

    // ============ Keyboard Navigation ============
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideAllModals();
        }
    });

    // ============ Notification System ============
    window.showNotification = function(type, title, message) {
        const container = document.getElementById('notificationContainer');
        if (!container) {
            console.log('Notification container not found');
            return;
        }

        const notification = document.createElement('div');
        notification.className = `toast ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            info: '💡',
            warning: '⚠️'
        };

        notification.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${icons[type] || icons.info}</span>
                <div class="toast-text">
                    <strong>${title}</strong>
                    <p>${message}</p>
                </div>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        container.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    };

    // ============ Get CSRF Token ============
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

    // ============ Login Form Handler ============
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPassword').value;
            
            // Validation
            if (!email || !password) {
                showNotification('error', 'Login Failed', 'Please fill in all fields');
                return;
            }

            // Disable button during request
            submitBtn.disabled = true;
            submitBtn.textContent = 'Signing in...';

            try {
                const response = await fetch('/api/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });

                const data = await response.json();

                if (data.success) {
                    showNotification('success', 'Login Successful', data.message);
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 500);
                } else {
                    showNotification('error', 'Login Failed', data.message);
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            } catch (error) {
                console.error('Login error:', error);
                showNotification('error', 'Error', 'An error occurred during login. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // ============ Signup Form Handler ============
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            const firstName = document.getElementById('firstName').value.trim();
            const lastName = document.getElementById('lastName').value.trim();
            const email = document.getElementById('signupEmail').value.trim();
            const password = document.getElementById('signupPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const termsAccept = document.getElementById('termsAccept').checked;
            
            // Validation
            if (!firstName || !lastName || !email || !password || !confirmPassword) {
                showNotification('error', 'Registration Failed', 'Please fill in all fields');
                return;
            }

            if (!termsAccept) {
                showNotification('error', 'Registration Failed', 'Please accept the Terms of Service');
                return;
            }

            if (password !== confirmPassword) {
                showNotification('error', 'Registration Failed', 'Passwords do not match');
                return;
            }

            if (password.length < 8) {
                showNotification('error', 'Registration Failed', 'Password must be at least 8 characters long');
                return;
            }

            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showNotification('error', 'Registration Failed', 'Please enter a valid email address');
                return;
            }

            // Disable button during request
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating account...';

            try {
                const response = await fetch('/api/signup/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        firstName: firstName,
                        lastName: lastName,
                        email: email,
                        password: password,
                        confirmPassword: confirmPassword
                    })
                });

                const data = await response.json();

                if (data.success) {
                    showNotification('success', 'Registration Successful', data.message);
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 500);
                } else {
                    showNotification('error', 'Registration Failed', data.message);
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            } catch (error) {
                console.error('Signup error:', error);
                showNotification('error', 'Error', 'An error occurred during registration. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // ============ Learn More Button ============
    const learnMoreBtn = document.getElementById('learnMoreBtn');
    if (learnMoreBtn) {
        learnMoreBtn.addEventListener('click', function() {
            const features = document.querySelector('.features');
            if (features) {
                features.scrollIntoView({ 
                    behavior: 'smooth' 
                });
            }
        });
    }

    // ============ Form Input Enhancement ============
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', function() {
            const email = this.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                this.setCustomValidity('Please enter a valid email address');
                this.reportValidity();
            } else {
                this.setCustomValidity('');
            }
        });
    });

    // ============ Password Strength Indicator ============
    const signupPassword = document.getElementById('signupPassword');
    if (signupPassword) {
        signupPassword.addEventListener('input', function() {
            const password = this.value;
            const strength = getPasswordStrength(password);
            console.log('Password strength:', strength);
            // You can add visual feedback here
        });
    }

    function getPasswordStrength(password) {
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;
        
        return strength;
    }
});