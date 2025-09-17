// User Authentication and App Management
class OS2LearnApp {
    constructor() {
        this.users = this.loadUsers();
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupScrollEffects();
        this.animateProgressRings();
        this.setupFloatingCards();
    }

    // User Management
    loadUsers() {
        return JSON.parse(localStorage.getItem('os2_users') || '[]');
    }

    saveUsers() {
        localStorage.setItem('os2_users', JSON.stringify(this.users));
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    validatePassword(password) {
        return password.length >= 6;
    }

    emailExists(email) {
        return this.users.some(user => user.email === email);
    }

    authenticateUser(email, password) {
        const user = this.users.find(u => u.email === email && u.password === password);
        if (user) {
            this.currentUser = user;
            return true;
        }
        return false;
    }

    registerUser(userData) {
        if (this.emailExists(userData.email)) {
            return { success: false, message: 'Email already exists' };
        }

        const newUser = {
            id: Date.now(),
            firstName: userData.firstName,
            lastName: userData.lastName,
            email: userData.email,
            password: userData.password,
            createdAt: new Date().toISOString(),
            progress: this.getDefaultProgress()
        };

        this.users.push(newUser);
        this.saveUsers();
        this.currentUser = newUser;

        return { success: true, message: 'Account created successfully!' };
    }

    getDefaultProgress() {
        return {
            overallProgress: 0,
            chaptersCompleted: 0,
            videosWatched: 0,
            quizzesPassed: 0,
            averageScore: 0,
            studyStreak: 0,
            topics: {
                processManagement: 0,
                memoryManagement: 0,
                fileSystems: 0,
                ioSystems: 0
            }
        };
    }

    // Event Listeners
    setupEventListeners() {
        // Navigation buttons
        document.getElementById('loginBtn').addEventListener('click', () => this.openModal('login'));
        document.getElementById('signupBtn').addEventListener('click', () => this.openModal('signup'));

        // Hero buttons
        document.getElementById('getStartedBtn').addEventListener('click', () => this.openModal('signup'));
        document.getElementById('learnMoreBtn').addEventListener('click', () => this.scrollToSection('features'));
        document.getElementById('startLearningBtn').addEventListener('click', () => this.openModal('signup'));

        // Modal controls
        document.getElementById('closeLogin').addEventListener('click', () => this.closeModal());
        document.getElementById('closeSignup').addEventListener('click', () => this.closeModal());
        document.getElementById('modalOverlay').addEventListener('click', (e) => {
            if (e.target === document.getElementById('modalOverlay')) {
                this.closeModal();
            }
        });

        // Modal switching
        document.getElementById('switchToSignup').addEventListener('click', (e) => {
            e.preventDefault();
            this.switchModal('signup');
        });
        document.getElementById('switchToLogin').addEventListener('click', (e) => {
            e.preventDefault();
            this.switchModal('login');
        });

        // Form submissions
        document.getElementById('loginForm').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('signupForm').addEventListener('submit', (e) => this.handleSignup(e));

        // Feature cards hover effects
        this.setupFeatureCardEffects();

        // Keyboard events
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    setupFeatureCardEffects() {
        const featureCards = document.querySelectorAll('.feature-card, .topic-card');
        featureCards.forEach(card => {
            card.addEventListener('click', () => {
                this.showNotification('info', 'Feature Preview', 'This feature will be available after registration!');
            });
        });
    }

    // Modal Management
    openModal(type) {
        const overlay = document.getElementById('modalOverlay');
        const loginModal = document.getElementById('loginModal');
        const signupModal = document.getElementById('signupModal');

        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';

        if (type === 'login') {
            loginModal.style.display = 'block';
            signupModal.style.display = 'none';
            setTimeout(() => document.getElementById('loginEmail').focus(), 300);
        } else {
            signupModal.style.display = 'block';
            loginModal.style.display = 'none';
            setTimeout(() => document.getElementById('firstName').focus(), 300);
        }
    }

    closeModal() {
        const overlay = document.getElementById('modalOverlay');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
        
        // Clear forms
        document.getElementById('loginForm').reset();
        document.getElementById('signupForm').reset();
    }

    switchModal(type) {
        this.closeModal();
        setTimeout(() => this.openModal(type), 200);
    }

    // Form Handlers
    handleLogin(e) {
        e.preventDefault();
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<div class="loading"></div> Signing in...';
        submitBtn.disabled = true;

        const formData = new FormData(e.target);
        const email = formData.get('email');
        const password = formData.get('password');

        // Simulate API call delay
        setTimeout(() => {
            if (!this.validateEmail(email)) {
                this.showNotification('error', 'Invalid Email', 'Please enter a valid email address.');
                this.resetSubmitButton(submitBtn, originalText);
                return;
            }

            if (!this.validatePassword(password)) {
                this.showNotification('error', 'Invalid Password', 'Password must be at least 6 characters long.');
                this.resetSubmitButton(submitBtn, originalText);
                return;
            }

            if (this.authenticateUser(email, password)) {
                this.showNotification('success', 'Welcome Back!', `Hello ${this.currentUser.firstName}! Redirecting to dashboard...`);
                setTimeout(() => {
                    this.redirectToDashboard();
                }, 2000);
            } else {
                this.showNotification('error', 'Login Failed', 'Invalid email or password. Please try again.');
                this.resetSubmitButton(submitBtn, originalText);
            }
        }, 1500);
    }

    handleSignup(e) {
        e.preventDefault();
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<div class="loading"></div> Creating account...';
        submitBtn.disabled = true;

        const formData = new FormData(e.target);
        const userData = {
            firstName: formData.get('firstName').trim(),
            lastName: formData.get('lastName').trim(),
            email: formData.get('email').trim(),
            password: formData.get('password'),
            confirmPassword: formData.get('confirmPassword')
        };

        // Simulate API call delay
        setTimeout(() => {
            // Validation
            if (!userData.firstName || !userData.lastName) {
                this.showNotification('error', 'Missing Information', 'Please enter your first and last name.');
                this.resetSubmitButton(submitBtn, originalText);
                return;
            }

            if (!this.validateEmail(userData.email)) {
                this.showNotification('error', 'Invalid Email', 'Please enter a valid email address.');
                this.resetSubmitButton(submitBtn, originalText);
                return;
            }

            if (!this.validatePassword(userData.password)) {
                this.showNotification('error', 'Weak Password', 'Password must be at least 6 characters long.');
                this.resetSubmitButton(submitBtn, originalText);
                return;
            }

            if (userData.password !== userData.confirmPassword) {
                this.showNotification('error', 'Password Mismatch', 'Passwords do not match. Please try again.');
                this.resetSubmitButton(submitBtn, originalText);
                return;
            }

            const result = this.registerUser(userData);
            
            if (result.success) {
                this.showNotification('success', 'Account Created!', `Welcome to OS2 Learn, ${userData.firstName}! Redirecting to dashboard...`);
                setTimeout(() => {
                    this.redirectToDashboard();
                }, 2000);
            } else {
                this.showNotification('error', 'Registration Failed', result.message);
                this.resetSubmitButton(submitBtn, originalText);
            }
        }, 1500);
    }

    resetSubmitButton(btn, originalText) {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }

    redirectToDashboard() {
        // In a real app, this would redirect to the dashboard
        this.showNotification('info', 'Dashboard Loading', 'Redirecting to your personalized learning dashboard...');
        this.closeModal();
        
        // Simulate dashboard redirect
        setTimeout(() => {
            this.showNotification('success', 'Welcome!', 'You would now be redirected to your dashboard. This is a demo version.');
        }, 1000);
    }

    // Notifications
    showNotification(type, title, message) {
        const container = document.getElementById('notificationContainer');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            info: '💡'
        };

        notification.innerHTML = `
            <div class="notification-icon">${icons[type]}</div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close">&times;</button>
        `;

        container.appendChild(notification);

        // Add close functionality
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.removeNotification(notification);
        });

        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                this.removeNotification(notification);
            }
        }, 5000);
    }

    removeNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.parentElement.removeChild(notification);
            }
        }, 300);
    }

    // Scroll Effects
    setupScrollEffects() {
        const navbar = document.querySelector('.navbar');
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });

        // Intersection Observer for animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe feature and topic cards
        document.querySelectorAll('.feature-card, .topic-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
    }

    scrollToSection(sectionClass) {
        const section = document.querySelector(`.${sectionClass}`);
        if (section) {
            section.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    // Animations
    animateProgressRings() {
        const rings = document.querySelectorAll('.progress-ring-circle');
        rings.forEach((ring, index) => {
            setTimeout(() => {
                ring.style.strokeDashoffset = ring.style.strokeDashoffset;
            }, index * 200);
        });
    }

    setupFloatingCards() {
        const cards = document.querySelectorAll('.floating-card');
        
        cards.forEach((card, index) => {
            // Add subtle mouse movement effect
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'scale(1.05) translateY(-10px)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'scale(1) translateY(0)';
            });

            // Add click interaction
            card.addEventListener('click', () => {
                this.showNotification('info', 'Feature Preview', 'This interactive feature will be available in the full version!');
            });
        });

        // Add parallax effect on scroll
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            cards.forEach((card, index) => {
                const rate = scrolled * -0.5;
                card.style.transform = `translateY(${rate}px)`;
            });
        });
    }

    // Utility Methods
    debounce(func, wait) {
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

    // Demo Data Management
    generateDemoProgress() {
        return {
            overallProgress: Math.floor(Math.random() * 100),
            chaptersCompleted: Math.floor(Math.random() * 15),
            videosWatched: Math.floor(Math.random() * 25),
            quizzesPassed: Math.floor(Math.random() * 20),
            averageScore: 75 + Math.floor(Math.random() * 20),
            studyStreak: Math.floor(Math.random() * 30),
            topics: {
                processManagement: Math.floor(Math.random() * 100),
                memoryManagement: Math.floor(Math.random() * 100),
                fileSystems: Math.floor(Math.random() * 100),
                ioSystems: Math.floor(Math.random() * 100)
            }
        };
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded'), () => {
    window.os2LearnApp = new OS2LearnApp();

    // Add some demo interactions
    const statCards = document.querySelectorAll('.hero-stats .stat');
    statCards.forEach((card, index) => {
        card.addEventListener('click', () => {
            window.os2LearnApp.showNotification('info', 'Statistics', `This statistic represents real data from our learning platform!`);
        });
    });

    // Add hover effects to CTA buttons
    const ctaButtons = document.querySelectorAll('.btn-hero-primary, .btn-hero-secondary, .btn-cta-primary');
    ctaButtons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Add typing effect to hero title (optional enhancement)
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        heroTitle.style.borderRight = '2px solid rgba(255,255,255,0.7)';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            } else {
                setTimeout(() => {
                    heroTitle.style.borderRight = 'none';
                }, 1000);
            }
        };
        
        setTimeout(typeWriter, 1000);
    }

    // Add loading states for better UX
    const allButtons = document.querySelectorAll('button');
    allButtons.forEach(button => {
        if (!button.closest('.modal')) {
            button.addEventListener('click', function() {
                if (this.textContent.includes('Learn More')) {
                    // Smooth scroll behavior is already handled
                    return;
                }
                
                const originalText = this.innerHTML;
                this.style.opacity = '0.8';
                setTimeout(() => {
                    this.style.opacity = '1';
                }, 200);
            });
        }
    });

    console.log('🚀 OS2 Learn application initialized successfully!');
    console.log('👤 Current users:', window.os2LearnApp.users.length);
}