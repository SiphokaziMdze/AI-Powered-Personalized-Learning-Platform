// ===============================
// OS2 Learn – Frontend Controller
// ===============================
class OS2LearnApp {
  constructor() {
    this.currentUser = null;
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupScrollEffects();
    this.animateProgressRings();
    this.setupFloatingCards();
  }

  // -------------------------
  // CSRF helpers (for Django)
  // -------------------------
  getCSRFToken() {
    // 1) Try cookie
    const getCookie = (name) => {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
      return null;
    };
    const cookieToken = getCookie('csrftoken');
    if (cookieToken) return cookieToken;

    // 2) Try meta tag <meta name="csrf-token" content="...">
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta?.content) return meta.content;

    // 3) As a last resort, try hidden input in a visible form
    const hidden = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return hidden?.value || '';
  }

  // ---------------
  // Event listeners
  // ---------------
  setupEventListeners() {
    const $ = (s) => document.getElementById(s);

    // Nav buttons
    $('loginBtn')?.addEventListener('click', () => this.openModal('login'));
    $('signupBtn')?.addEventListener('click', () => this.openModal('signup'));

    // Hero buttons
    $('getStartedBtn')?.addEventListener('click', () => this.openModal('signup'));
    $('learnMoreBtn')?.addEventListener('click', () => this.scrollToSection('features'));
    $('startLearningBtn')?.addEventListener('click', () => this.openModal('signup'));

    // Modals
    $('closeLogin')?.addEventListener('click', () => this.closeModal());
    $('closeSignup')?.addEventListener('click', () => this.closeModal());
    const overlay = $('modalOverlay');
    overlay?.addEventListener('click', (e) => {
      if (e.target === overlay) this.closeModal();
    });

    // Switch modals
    $('switchToSignup')?.addEventListener('click', (e) => {
      e.preventDefault(); this.switchModal('signup');
    });
    $('switchToLogin')?.addEventListener('click', (e) => {
      e.preventDefault(); this.switchModal('login');
    });

    // Forms
    $('loginForm')?.addEventListener('submit', (e) => this.handleLogin(e));
    $('signupForm')?.addEventListener('submit', (e) => this.handleSignup(e));

    // ESC closes modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.closeModal();
    });

    // Feature cards preview
    this.setupFeatureCardEffects();

    // CTA micro-animation
    document.querySelectorAll('.btn-hero-primary, .btn-hero-secondary, .btn-cta-primary').forEach((btn) => {
      btn.addEventListener('mouseenter', () => {
        btn.style.transition = 'transform .2s ease';
        btn.style.transform = 'translateY(-2px) scale(1.02)';
      });
      btn.addEventListener('mouseleave', () => {
        btn.style.transform = 'translateY(0) scale(1)';
      });
    });

    console.log('🚀 OS2 Learn initialized');
  }

  setupFeatureCardEffects() {
    document.querySelectorAll('.feature-card, .topic-card').forEach((card) => {
      card.addEventListener('click', () => {
        this.showNotification('info', 'Feature Preview', 'This feature will be available after registration!');
      });
    });
  }

  // -------
  // Modals
  // -------
  openModal(type) {
    const overlay = document.getElementById('modalOverlay');
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');
    if (!overlay || !loginModal || !signupModal) return;

    overlay.classList.add('show');
    overlay.removeAttribute('hidden');
    overlay.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    if (type === 'login') {
      loginModal.style.display = 'block';
      signupModal.style.display = 'none';
      loginModal.setAttribute('aria-hidden', 'false');
      signupModal.setAttribute('aria-hidden', 'true');
      setTimeout(() => document.getElementById('loginEmail')?.focus(), 250);
    } else {
      signupModal.style.display = 'block';
      loginModal.style.display = 'none';
      signupModal.setAttribute('aria-hidden', 'false');
      loginModal.setAttribute('aria-hidden', 'true');
      setTimeout(() => document.getElementById('firstName')?.focus(), 250);
    }
  }

  closeModal() {
    const overlay = document.getElementById('modalOverlay');
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');
    if (!overlay) return;

    overlay.classList.remove('show');
    overlay.setAttribute('hidden', '');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';

    if (loginModal) { loginModal.style.display = 'none'; loginModal.setAttribute('aria-hidden', 'true'); }
    if (signupModal) { signupModal.style.display = 'none'; signupModal.setAttribute('aria-hidden', 'true'); }

    document.getElementById('loginForm')?.reset();
    document.getElementById('signupForm')?.reset();
  }

  switchModal(type) {
    this.closeModal();
    setTimeout(() => this.openModal(type), 200);
  }

  // --------------
  // Form Handlers
  // --------------
  handleLogin(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn?.innerHTML || '';
    if (submitBtn) { submitBtn.innerHTML = '<div class="loading"></div> Signing in...'; submitBtn.disabled = true; }

    const formData = new FormData(form);
    const csrf = this.getCSRFToken();

    fetch('/api/login/', {
      method: 'POST',
      body: formData,               // uses multipart/form-data
      headers: { 'X-CSRFToken': csrf, 'Accept': 'application/json' },
      credentials: 'same-origin',
    })
      .then(r => r.json())
      .then(data => {
        if (data?.success) {
          this.showNotification('success', 'Welcome Back!', `Hello ${data.user?.first_name || ''}! Redirecting...`);
          setTimeout(() => { window.location.href = '/dashboard/'; }, 1200);
        } else {
          this.showNotification('error', 'Login Failed', data?.message || 'Invalid credentials.');
          this.resetSubmitButton(submitBtn, originalText);
        }
      })
      .catch(err => {
        console.error('Login error:', err);
        this.showNotification('error', 'Login Error', 'Something went wrong. Please try again.');
        this.resetSubmitButton(submitBtn, originalText);
      });
  }

  handleSignup(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn?.innerHTML || '';
    if (submitBtn) { submitBtn.innerHTML = '<div class="loading"></div> Creating account...'; submitBtn.disabled = true; }

    const formData = new FormData(form);
    const password = (formData.get('password') || '').toString();
    const confirm = (formData.get('confirmPassword') || '').toString();

    if (password !== confirm) {
      this.showNotification('error', 'Password Mismatch', 'Passwords do not match.');
      return this.resetSubmitButton(submitBtn, originalText);
    }
    if (password.length < 6) {
      this.showNotification('error', 'Weak Password', 'Password must be at least 6 characters.');
      return this.resetSubmitButton(submitBtn, originalText);
    }

    const csrf = this.getCSRFToken();

    fetch('/api/signup/', {
      method: 'POST',
      body: formData,               // uses multipart/form-data
      headers: { 'X-CSRFToken': csrf, 'Accept': 'application/json' },
      credentials: 'same-origin',
    })
      .then(r => r.json())
      .then(data => {
        if (data?.success) {
          this.showNotification('success', 'Account Created!', `Welcome ${data.user?.first_name || ''}! Redirecting...`);
          setTimeout(() => { window.location.href = '/dashboard/'; }, 1200);
        } else {
          this.showNotification('error', 'Registration Failed', data?.message || 'Please try again.');
          this.resetSubmitButton(submitBtn, originalText);
        }
      })
      .catch(err => {
        console.error('Signup error:', err);
        this.showNotification('error', 'Registration Error', 'Something went wrong. Please try again.');
        this.resetSubmitButton(submitBtn, originalText);
      });
  }

  resetSubmitButton(btn, originalText) {
    if (btn) { btn.innerHTML = originalText; btn.disabled = false; }
  }

  // --------------
  // Notifications
  // --------------
  showNotification(type, title, message) {
    const container = document.getElementById('notificationContainer');
    if (!container) return;

    const icons = { success: '✅', error: '❌', info: '💡' };
    const n = document.createElement('div');
    n.className = `toast ${type}`;
    n.innerHTML = `
      <div style="display:flex;align-items:center;gap:8px;">
        <span>${icons[type] || 'ℹ️'}</span>
        <div>
          <strong>${title}</strong><br>
          <small>${message}</small>
        </div>
        <button aria-label="Close" style="margin-left:auto;background:none;border:none;color:var(--muted);cursor:pointer;">&times;</button>
      </div>
    `;
    n.querySelector('button')?.addEventListener('click', () => n.remove());
    container.appendChild(n);
    setTimeout(() => n.remove(), 5000);
  }

  // -----------------
  // Scroll / Animations
  // -----------------
  setupScrollEffects() {
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
      navbar?.classList.toggle('scrolled', window.scrollY > 100);
    });

    // Fade/slide in for cards
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.feature-card, .topic-card').forEach((card) => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(30px)';
      card.style.transition = 'opacity .6s ease, transform .6s ease';
      observer.observe(card);
    });
  }

  scrollToSection(sectionClass) {
    document.querySelector(`.${sectionClass}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  animateProgressRings() {
    const rings = document.querySelectorAll('.progress-ring-circle');
    rings.forEach((ring, i) => {
      setTimeout(() => {
        // trigger CSS transition only if value exists
        const off = ring.style.strokeDashoffset;
        if (typeof off === 'string' && off.length > 0) {
          ring.style.strokeDashoffset = off;
        }
      }, i * 200);
    });
  }

  setupFloatingCards() {
    const cards = document.querySelectorAll('.floating-card');

    // Hover effect
    cards.forEach((card) => {
      card.addEventListener('mouseenter', () => {
        card.style.transition = 'transform .3s ease';
        card.style.transform = 'scale(1.05) translateY(-10px)';
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = 'scale(1) translateY(0)';
      });
      card.addEventListener('click', () => {
        this.showNotification('info', 'Feature Preview', 'This interactive feature will be available in the full version!');
      });
    });

    // Parallax (compute fresh transform; don’t append)
    const onScroll = () => {
      const scrolled = window.pageYOffset;
      cards.forEach((card) => {
        // If hovered, keep the hover transform
        if (card.matches(':hover')) return;
        const offset = scrolled * -0.2;
        card.style.transform = `translateY(${offset}px)`;
      });
    };
    window.addEventListener('scroll', this.debounce(onScroll, 10));
  }

  // Utilities
  debounce(fn, wait) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), wait);
    };
  }
}

// Boot
document.addEventListener('DOMContentLoaded', () => {
  window.os2LearnApp = new OS2LearnApp();
});
