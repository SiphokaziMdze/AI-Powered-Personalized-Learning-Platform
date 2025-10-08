class DashboardManager {
    constructor() {
        this.progressData = new Map();
        this.notificationQueue = [];
        this.isOnline = navigator.onLine;
        this.eventListeners = new Map();
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeProgressTracking();
        this.setupOfflineHandling();
        this.startPerformanceMonitoring();
        this.loadUserPreferences();
        
        // Initialize components
        this.animateOnLoad();
        this.setupIntersectionObserver();
        
        console.log('🚀 Dashboard initialized successfully!');
    }

    setupEventListeners() {
        // User menu dropdown
        this.initializeUserMenu();
        
        // Subject tabs
        this.initializeSubjectTabs();
        
        // Interactive elements
        this.initializeInteractiveElements();
        
        // Keyboard navigation
        this.setupKeyboardNavigation();
        
        // Touch/swipe support for mobile
        this.setupTouchHandlers();
        
        // Window events
        window.addEventListener('beforeunload', () => this.saveSession());
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
    }

    initializeUserMenu() {
        const userMenu = document.getElementById('userMenu');
        if (!userMenu) return;

        const avatar = userMenu.querySelector('#avatar') || userMenu.querySelector('.user-avatar');
        const dropdown = userMenu.querySelector('#dropdown') || userMenu.querySelector('.dropdown-menu');
        
        if (!avatar || !dropdown) return;

        const toggleMenu = (e) => {
            e?.stopPropagation();
            dropdown.classList.toggle('show');
            avatar.setAttribute('aria-expanded', dropdown.classList.contains('show'));
        };

        this.addEventListenerWithCleanup(avatar, 'click', toggleMenu);
        this.addEventListenerWithCleanup(avatar, 'keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleMenu(e);
            }
        });

        // Close dropdown when clicking outside
        this.addEventListenerWithCleanup(document, 'click', (e) => {
            if (!userMenu.contains(e.target)) {
                dropdown.classList.remove('show');
                avatar.setAttribute('aria-expanded', 'false');
            }
        });
    }

    initializeSubjectTabs() {
        const tabs = document.querySelectorAll('.subject-tab');
        const contents = document.querySelectorAll('.subject-content');
        
        if (tabs.length === 0) return;

        tabs.forEach(tab => {
            this.addEventListenerWithCleanup(tab, 'click', () => {
                const subject = tab.dataset.subject;
                if (!subject) return;
                
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Update active content with animation
                contents.forEach(c => {
                    c.classList.remove('active');
                    c.style.opacity = '0';
                });
                
                const targetContent = document.getElementById(`${subject}-content`);
                if (targetContent) {
                    setTimeout(() => {
                        targetContent.classList.add('active');
                        targetContent.style.opacity = '1';
                    }, 150);
                }
                
                // Track subject switch
                this.trackEvent('subject_switch', { subject });
            });
        });
    }

    initializeInteractiveElements() {
        // Progress items
        document.querySelectorAll('.progress-item').forEach(item => {
            this.addEventListenerWithCleanup(item, 'click', () => {
                const topicName = item.querySelector('.progress-header span:first-child')?.textContent;
                const progress = item.querySelector('.progress-header span:last-child')?.textContent;
                
                if (topicName) {
                    this.showProgressDetails(topicName, progress);
                }
            });

            // Add hover effects
            this.addHoverEffects(item);
        });

        // Material items
        document.querySelectorAll('.material-item').forEach(item => {
            this.addEventListenerWithCleanup(item, 'click', () => {
                const title = item.querySelector('h4')?.textContent;
                const status = item.querySelector('.status-badge')?.textContent;
                
                if (title) {
                    this.handleMaterialClick(title, status);
                }
            });

            this.addHoverEffects(item);
        });

        // Stat cards
        document.querySelectorAll('.stat-card').forEach(card => {
            this.addEventListenerWithCleanup(card, 'click', () => {
                const statType = this.getStatType(card);
                this.showStatDetails(statType);
            });

            this.addHoverEffects(card);
        });

        // Action buttons
        document.querySelectorAll('.action-buttons button, .topic-actions button').forEach(button => {
            this.addEventListenerWithCleanup(button, 'click', (e) => {
                this.handleButtonClick(e, button);
            });
        });
    }

    addHoverEffects(element) {
        this.addEventListenerWithCleanup(element, 'mouseenter', () => {
            element.style.transform = 'translateY(-1px)';
            element.style.transition = 'transform 0.2s ease';
        });

        this.addEventListenerWithCleanup(element, 'mouseleave', () => {
            element.style.transform = 'translateY(0)';
        });
    }

    setupKeyboardNavigation() {
        const focusableElements = document.querySelectorAll(
            '.material-item, .stat-card, .progress-item, .subject-tab, button'
        );

        focusableElements.forEach((element, index) => {
            element.setAttribute('tabindex', '0');
            
            this.addEventListenerWithCleanup(element, 'keydown', (e) => {
                switch(e.key) {
                    case 'Enter':
                    case ' ':
                        e.preventDefault();
                        element.click();
                        break;
                    case 'ArrowRight':
                    case 'ArrowDown':
                        e.preventDefault();
                        this.focusNext(focusableElements, index);
                        break;
                    case 'ArrowLeft':
                    case 'ArrowUp':
                        e.preventDefault();
                        this.focusPrev(focusableElements, index);
                        break;
                }
            });
        });
    }

    focusNext(elements, currentIndex) {
        const nextIndex = (currentIndex + 1) % elements.length;
        elements[nextIndex].focus();
    }

    focusPrev(elements, currentIndex) {
        const prevIndex = (currentIndex - 1 + elements.length) % elements.length;
        elements[prevIndex].focus();
    }

    setupTouchHandlers() {
        let touchStartX = 0;
        let touchStartY = 0;

        this.addEventListenerWithCleanup(document, 'touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }, { passive: true });

        this.addEventListenerWithCleanup(document, 'touchmove', (e) => {
            if (!touchStartX || !touchStartY) return;

            const touchEndX = e.touches[0].clientX;
            const touchEndY = e.touches[0].clientY;

            const diffX = touchStartX - touchEndX;
            const diffY = touchStartY - touchEndY;

            // Handle swipe gestures for subject tabs
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                const currentTab = document.querySelector('.subject-tab.active');
                if (currentTab) {
                    const tabs = Array.from(document.querySelectorAll('.subject-tab'));
                    const currentIndex = tabs.indexOf(currentTab);
                    
                    if (diffX > 0 && currentIndex < tabs.length - 1) {
                        // Swipe left - next tab
                        tabs[currentIndex + 1].click();
                    } else if (diffX < 0 && currentIndex > 0) {
                        // Swipe right - previous tab
                        tabs[currentIndex - 1].click();
                    }
                }
            }

            touchStartX = 0;
            touchStartY = 0;
        }, { passive: true });
    }

    initializeProgressTracking() {
        // Animate progress bars on load
        setTimeout(() => {
            document.querySelectorAll('.progress-fill').forEach((bar, index) => {
                const targetWidth = bar.style.width || '0%';
                bar.style.width = '0%';
                
                setTimeout(() => {
                    bar.style.transition = 'width 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
                    bar.style.width = targetWidth;
                }, index * 100);
            });
        }, 300);

        // Animate circular progress
        document.querySelectorAll('.progress-ring-circle').forEach((circle, index) => {
            const originalOffset = circle.style.strokeDashoffset || '0';
            circle.style.strokeDashoffset = '220';
            
            setTimeout(() => {
                circle.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
                circle.style.strokeDashoffset = originalOffset;
            }, index * 200 + 500);
        });
    }

    animateOnLoad() {
        // Fade in elements sequentially
        const animatedElements = document.querySelectorAll('.content-card, .stat-card');
        
        animatedElements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Animate stats
        this.animateCounters();
    }

    animateCounters() {
        document.querySelectorAll('.stat-number').forEach(counter => {
            const target = parseInt(counter.textContent.replace(/\D/g, ''));
            if (isNaN(target)) return;

            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = counter.textContent.replace(/\d+/, target);
                    clearInterval(timer);
                } else {
                    counter.textContent = counter.textContent.replace(/\d+/, Math.floor(current));
                }
            }, 30);
        });
    }

    setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.content-card, .material-item, .assessment-item').forEach(el => {
            observer.observe(el);
        });
    }

    // Event handlers
    handleButtonClick(e, button) {
        const action = button.textContent.trim();
        const buttonRect = button.getBoundingClientRect();
        
        // Add ripple effect
        this.createRippleEffect(e, button, buttonRect);
        
        // Handle action
        this.executeAction(action, button);
    }

    createRippleEffect(e, button, buttonRect) {
        const ripple = document.createElement('span');
        const size = Math.max(buttonRect.width, buttonRect.height);
        const x = e.clientX - buttonRect.left - size / 2;
        const y = e.clientY - buttonRect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    executeAction(action, button) {
        const actions = {
            'Continue Reading': () => this.showNotification('info', 'Opening Lesson', 'Loading lesson content...'),
            'Watch Video': () => this.showNotification('info', 'Starting Video', 'Loading video player...'),
            'Take Practice Quiz': () => this.showNotification('info', 'Loading Quiz', 'Preparing practice questions...'),
            'Ask AI Tutor': () => this.showNotification('info', 'AI Tutor', 'Connecting to AI assistant...'),
            'Study Deadlocks': () => this.showNotification('success', 'Focus Area', 'Opening deadlock prevention concepts...'),
            'Continue': () => this.showNotification('success', 'Next Steps', 'Proceeding to next topic...'),
        };

        const handler = actions[action];
        if (handler) {
            button.disabled = true;
            button.textContent = 'Loading...';
            
            handler();
            
            setTimeout(() => {
                button.disabled = false;
                button.textContent = action;
                this.showNotification('success', 'Ready!', 'Content is now available.');
            }, 2000);
        }
    }

    getStatType(card) {
        const icon = card.querySelector('.stat-icon')?.textContent || '';
        const statTypes = {
            '📚': 'lessons',
            '🎥': 'videos', 
            '🧩': 'quizzes',
            '🏆': 'achievements'
        };
        return statTypes[icon] || 'general';
    }

    showStatDetails(statType) {
        const messages = {
            lessons: 'You have completed multiple lessons across different subjects. Keep up the excellent work!',
            videos: 'You have watched educational videos to reinforce your learning.',
            quizzes: 'You have successfully completed practice quizzes with good performance.',
            achievements: 'Your overall performance shows consistent progress and dedication.'
        };

        this.showNotification('info', 'Statistics', messages[statType]);
    }

    showProgressDetails(topic, progress) {
        const details = {
            'Process Management': `Excellent progress on ${topic}! You have mastered scheduling algorithms and synchronization.`,
            'Memory Management': `Good progress on ${topic}. Consider reviewing virtual memory concepts for better understanding.`,
            'File Systems': `Making steady progress on ${topic}. Focus on directory structures next.`,
            'SQL Fundamentals': `Strong foundation in ${topic}. Ready for advanced query techniques.`,
            'Database Design': `Good understanding of ${topic}. Practice normalization exercises.`
        };

        this.showNotification('info', `${topic} - ${progress}`, 
            details[topic] || `You are making good progress in ${topic}. Keep learning!`);
    }

    handleMaterialClick(title, status) {
        const statusActions = {
            'Completed': () => this.showNotification('info', 'Review Material', `Opening ${title} for review...`),
            'In Progress': () => this.showNotification('success', 'Continue Learning', `Resuming ${title}...`),
            'Not Started': () => this.showNotification('info', 'Start Learning', `Beginning ${title}...`)
        };

        const action = statusActions[status] || statusActions['Not Started'];
        action();

        // Update progress after interaction
        setTimeout(() => {
            this.updateMaterialStatus(title, status);
        }, 2000);
    }

    updateMaterialStatus(title, currentStatus) {
        if (currentStatus === 'Not Started') {
            const materialElement = Array.from(document.querySelectorAll('.material-item'))
                .find(item => item.querySelector('h4')?.textContent === title);
            
            if (materialElement) {
                const statusBadge = materialElement.querySelector('.status-badge');
                if (statusBadge) {
                    statusBadge.textContent = 'In Progress';
                    statusBadge.className = 'status-badge in-progress';
                }
            }
        }
    }

    // Notification system
    showNotification(type, title, message, duration = 5000) {
        if (!this.isOnline && type !== 'offline') {
            this.queueNotification({ type, title, message, duration });
            return;
        }

        const container = this.getNotificationContainer();
        const notification = this.createNotificationElement(type, title, message);
        
        container.appendChild(notification);
        
        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Auto remove
        setTimeout(() => {
            this.removeNotification(notification);
        }, duration);

        // Track notification
        this.trackEvent('notification_shown', { type, title });
    }

    getNotificationContainer() {
        let container = document.getElementById('notificationContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notificationContainer';
            container.className = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    createNotificationElement(type, title, message) {
        const notification = document.createElement('div');
        notification.className = `toast ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌', 
            info: '💡',
            warning: '⚠️',
            offline: '📡'
        };

        notification.style.cssText = `
            background: var(--card);
            border: 1px solid var(--ring);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            transform: translateX(100%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            opacity: 0;
        `;

        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">${icons[type] || icons.info}</span>
                <div style="flex: 1;">
                    <strong style="display: block; margin-bottom: 4px; color: var(--text);">${title}</strong>
                    <div style="font-size: 13px; color: var(--muted);">${message}</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="background: none; border: none; color: var(--muted); cursor: pointer; font-size: 18px; padding: 4px;">
                    ×
                </button>
            </div>
        `;

        return notification;
    }

    removeNotification(notification) {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }

    queueNotification(notificationData) {
        this.notificationQueue.push(notificationData);
    }

    processNotificationQueue() {
        while (this.notificationQueue.length > 0) {
            const { type, title, message, duration } = this.notificationQueue.shift();
            this.showNotification(type, title, message, duration);
        }
    }

    // Offline handling
    setupOfflineHandling() {
        if (!navigator.onLine) {
            this.handleOffline();
        }
    }

    handleOffline() {
        this.isOnline = false;
        this.showNotification('offline', 'Offline Mode', 
            'You are currently offline. Some features may be limited.', 10000);
        
        document.body.classList.add('offline-mode');
    }

    handleOnline() {
        this.isOnline = true;
        this.showNotification('success', 'Back Online', 
            'Connection restored. All features are now available.');
        
        document.body.classList.remove('offline-mode');
        this.processNotificationQueue();
        this.syncOfflineData();
    }

    syncOfflineData() {
        // Sync any offline progress data
        const offlineData = this.getOfflineData();
        if (offlineData.length > 0) {
            this.showNotification('info', 'Syncing Data', 'Synchronizing offline progress...');
            
            // Send offline data to server
            fetch('/api/sync-progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: JSON.stringify({ data: offlineData })
            }).then(response => {
                if (response.ok) {
                    this.clearOfflineData();
                    this.showNotification('success', 'Sync Complete', 'All data synchronized successfully.');
                }
            }).catch(() => {
                this.showNotification('error', 'Sync Failed', 'Could not sync offline data. Will retry later.');
            });
        }
    }

    // Data persistence
    saveSession() {
        const sessionData = {
            timestamp: Date.now(),
            activeTab: document.querySelector('.subject-tab.active')?.dataset.subject,
            scrollPosition: window.scrollY,
            interactionCount: this.interactionCount || 0
        };

        localStorage.setItem('dashboard_session', JSON.stringify(sessionData));
    }

    loadUserPreferences() {
        try {
            const saved = localStorage.getItem('dashboard_preferences');
            if (saved) {
                const preferences = JSON.parse(saved);
                this.applyPreferences(preferences);
            }
        } catch (error) {
            console.warn('Could not load user preferences:', error);
        }
    }

    applyPreferences(preferences) {
        if (preferences.theme) {
            document.body.classList.add(`theme-${preferences.theme}`);
        }
        
        if (preferences.reducedMotion) {
            document.body.classList.add('reduced-motion');
        }
    }

    getOfflineData() {
        try {
            const data = localStorage.getItem('offline_progress');
            return data ? JSON.parse(data) : [];
        } catch {
            return [];
        }
    }

    clearOfflineData() {
        localStorage.removeItem('offline_progress');
    }

    // Performance monitoring
    startPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                const navigation = performance.getEntriesByType('navigation')[0];
                if (navigation) {
                    this.trackEvent('page_performance', {
                        loadTime: Math.round(navigation.loadEventEnd - navigation.loadEventStart),
                        domContentLoaded: Math.round(navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart)
                    });
                }
            }, 0);
        });

        // Monitor memory usage (if available)
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize > memory.jsHeapSizeLimit * 0.9) {
                    console.warn('High memory usage detected');
                }
            }, 30000);
        }
    }

    trackEvent(eventName, data = {}) {
        // Track events for analytics
        const eventData = {
            event: eventName,
            timestamp: Date.now(),
            url: window.location.pathname,
            ...data
        };

        // Send to analytics service or store locally
        console.log('Event tracked:', eventData);
        
        // Store in localStorage for offline tracking
        try {
            const events = JSON.parse(localStorage.getItem('tracked_events') || '[]');
            events.push(eventData);
            
            // Keep only last 100 events
            if (events.length > 100) {
                events.splice(0, events.length - 100);
            }
            
            localStorage.setItem('tracked_events', JSON.stringify(events));
        } catch (error) {
            console.warn('Could not store event:', error);
        }
    }

    // Utility methods
    addEventListenerWithCleanup(element, event, handler, options) {
        element.addEventListener(event, handler, options);
        
        if (!this.eventListeners.has(element)) {
            this.eventListeners.set(element, []);
        }
        
        this.eventListeners.get(element).push({ event, handler, options });
    }

    destroy() {
        // Clean up all event listeners
        this.eventListeners.forEach((listeners, element) => {
            listeners.forEach(({ event, handler, options }) => {
                element.removeEventListener(event, handler, options);
            });
        });
        
        this.eventListeners.clear();
        
        // Clean up other resources
        this.progressData.clear();
        this.notificationQueue.length = 0;
    }
}

// Add CSS for animations and effects
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(10px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }

    .animate-in {
        animation: fadeIn 0.6s ease-out;
    }

    .toast.show {
        opacity: 1 !important;
        transform: translateX(0) !important;
    }

    .offline-mode {
        filter: grayscale(0.3);
    }

    .reduced-motion * {
        animation-duration: 0.01s !important;
        transition-duration: 0.01s !important;
    }

    .subject-content {
        transition: opacity 0.3s ease;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01s !important;
            transition-duration: 0.01s !important;
        }
    }
`;

document.head.appendChild(styleSheet);

// Initialize dashboard when DOM is ready
let dashboardManager;

function initializeDashboard() {
    try {
        dashboardManager = new DashboardManager();
        window.dashboardManager = dashboardManager;
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDashboard);
} else {
    initializeDashboard();
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (dashboardManager) {
        dashboardManager.destroy();
    }
});