const Auth = {
    _isLogin: false,
    _pendingSearch: null,  // callback to execute after auth
    _listenersAttached: false,

    init() {
        // Sign in buttons (desktop + mobile)
        document.getElementById('signin-btn').addEventListener('click', () => this.showModal());
        const signinMobile = document.getElementById('signin-btn-mobile');
        if (signinMobile) signinMobile.addEventListener('click', () => {
            this._closeMobileMenu();
            this.showModal();
        });

        // Logout buttons (desktop + mobile)
        document.getElementById('logout-btn').addEventListener('click', () => this.logout());
        const logoutMobile = document.getElementById('logout-btn-mobile');
        if (logoutMobile) logoutMobile.addEventListener('click', () => {
            this._closeMobileMenu();
            this.logout();
        });

        // Nav dropdown logout
        const navLogout = document.getElementById('nav-logout-btn');
        if (navLogout) navLogout.addEventListener('click', () => this.logout());

        // User dropdown toggle
        const menuTrigger = document.getElementById('user-menu-trigger');
        if (menuTrigger) {
            menuTrigger.addEventListener('click', () => this._toggleDropdown());
        }
        // Close dropdown on outside click (only attach once)
        if (!this._listenersAttached) {
            document.addEventListener('click', (e) => {
                const dropdown = document.getElementById('user-menu');
                if (dropdown && !dropdown.contains(e.target)) {
                    this._closeDropdown();
                }
            });
        }

        // Close modal
        document.getElementById('modal-close').addEventListener('click', () => this.hideModal());
        document.getElementById('modal-backdrop').addEventListener('click', () => this.hideModal());

        // Email/password form
        document.getElementById('signup-form').addEventListener('submit', (e) => this.handleSubmit(e));

        // Toggle login/signup (use delegation on footer to survive innerHTML replacement)
        document.querySelector('.modal-footer-text').addEventListener('click', (e) => {
            if (e.target.id === 'login-link') {
                e.preventDefault();
                this.toggleMode();
            }
        });

        // Forgot password link
        const forgotLink = document.getElementById('forgot-password-link');
        if (forgotLink) {
            forgotLink.addEventListener('click', (e) => {
                e.preventDefault();
                this._showForgotPassword();
            });
        }

        // Forgot password submit
        const forgotSubmit = document.getElementById('forgot-submit-btn');
        if (forgotSubmit) {
            forgotSubmit.addEventListener('click', () => this._handleForgotPassword());
        }

        // Back to login link
        const backToLogin = document.getElementById('back-to-login-link');
        if (backToLogin) {
            backToLogin.addEventListener('click', (e) => {
                e.preventDefault();
                this._hideForgotPassword();
            });
        }

        // Escape key closes modal (only attach once)
        if (!this._listenersAttached) {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') this.hideModal();
            });
            this._listenersAttached = true;
        }

        // Hamburger menu
        const hamburger = document.getElementById('hamburger-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        if (hamburger && mobileMenu) {
            hamburger.addEventListener('click', () => {
                const expanded = hamburger.getAttribute('aria-expanded') === 'true';
                hamburger.setAttribute('aria-expanded', !expanded);
                mobileMenu.classList.toggle('is-open');
            });
            // Close menu when clicking nav links
            mobileMenu.querySelectorAll('.mobile-menu__link').forEach(link => {
                link.addEventListener('click', () => this._closeMobileMenu());
            });
            // Sync mobile language selector with desktop
            const langMobile = document.getElementById('lang-select-mobile');
            const langDesktop = document.getElementById('lang-select');
            if (langMobile && langDesktop) {
                langMobile.addEventListener('change', () => {
                    langDesktop.value = langMobile.value;
                    langDesktop.dispatchEvent(new Event('change'));
                });
            }
            // Mobile theme toggle syncs with desktop
            const themeMobile = document.getElementById('theme-toggle-mobile');
            const themeDesktop = document.getElementById('theme-toggle');
            if (themeMobile && themeDesktop) {
                themeMobile.addEventListener('click', () => themeDesktop.click());
            }
        }

        // Check if already logged in
        this.checkSession();
    },

    _closeMobileMenu() {
        const hamburger = document.getElementById('hamburger-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        if (hamburger) hamburger.setAttribute('aria-expanded', 'false');
        if (mobileMenu) mobileMenu.classList.remove('is-open');
    },

    _toggleDropdown() {
        const items = document.getElementById('user-menu-items');
        if (items) {
            items.style.display = items.style.display === 'none' ? 'block' : 'none';
        }
    },

    _closeDropdown() {
        const items = document.getElementById('user-menu-items');
        if (items) items.style.display = 'none';
    },

    _showForgotPassword() {
        document.getElementById('signup-form').style.display = 'none';
        document.querySelector('.modal-footer-text').style.display = 'none';
        const subtitle = document.querySelector('.modal-subtitle');
        if (subtitle) subtitle.style.display = 'none';
        document.querySelector('.modal-title').style.display = 'none';
        document.getElementById('forgot-password-view').style.display = 'block';
        document.getElementById('forgot-message').textContent = '';
        const forgotEmail = document.getElementById('forgot-email');
        if (forgotEmail) forgotEmail.focus();
    },

    _hideForgotPassword() {
        document.getElementById('forgot-password-view').style.display = 'none';
        document.getElementById('signup-form').style.display = '';
        document.querySelector('.modal-footer-text').style.display = '';
        const subtitle = document.querySelector('.modal-subtitle');
        if (subtitle) subtitle.style.display = '';
        document.querySelector('.modal-title').style.display = '';
    },

    async _handleForgotPassword() {
        const email = document.getElementById('forgot-email').value.trim();
        const msgEl = document.getElementById('forgot-message');
        if (!email) {
            msgEl.textContent = I18n.get('forgotPassword.enterEmail') || 'Please enter your email address.';
            msgEl.style.color = 'var(--rose-400)';
            return;
        }
        const btn = document.getElementById('forgot-submit-btn');
        btn.disabled = true;
        btn.textContent = I18n.get('forgotPassword.sending') || 'Sending...';
        try {
            const resp = await fetch('/api/auth/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email }),
            });
            if (resp.ok) {
                msgEl.textContent = I18n.get('forgotPassword.success') || 'If that email exists, a reset link has been sent.';
                msgEl.style.color = 'var(--accent-500)';
            } else {
                msgEl.textContent = I18n.get('forgotPassword.success') || 'If that email exists, a reset link has been sent.';
                msgEl.style.color = 'var(--accent-500)';
            }
        } catch (err) {
            msgEl.textContent = I18n.get('forgotPassword.networkError') || 'Network error. Please try again.';
            msgEl.style.color = 'var(--rose-400)';
        }
        btn.disabled = false;
        btn.textContent = I18n.get('forgotPassword.submitBtn') || 'Send Reset Link';
    },

    async logout() {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
        } catch (e) { /* ignore */ }
        State.set('user', null);
        this.updateUI(null);
    },

    async checkSession() {
        try {
            const resp = await fetch('/api/auth/me');
            if (resp.ok) {
                const user = await resp.json();
                State.set('user', user);
                this.updateUI(user);
            }
        } catch (e) { /* not logged in */ }
    },

    showModal(pendingSearch = null) {
        this._pendingSearch = pendingSearch;
        // Reset to signup form view (hide forgot password if showing)
        this._hideForgotPassword();
        document.getElementById('signup-modal').classList.add('is-open');
        I18n.applyAll();
        document.getElementById('signup-email').focus();
    },

    hideModal() {
        document.getElementById('signup-modal').classList.remove('is-open');
    },

    toggleMode() {
        this._isLogin = !this._isLogin;
        const title = document.querySelector('.modal-title');
        const submit = document.querySelector('.btn--submit');
        const footer = document.querySelector('.modal-footer-text');
        const forgotLink = document.getElementById('forgot-password-link');

        if (this._isLogin) {
            title.textContent = I18n.get('login.title') || 'Welcome back';
            submit.textContent = I18n.get('login.submit') || 'Log in';
            footer.innerHTML = (I18n.get('login.signupLink') || 'Don\'t have an account? <a id="login-link">Sign up</a>');
            if (forgotLink) forgotLink.style.display = 'block';
        } else {
            title.textContent = I18n.get('signup.title') || 'Create free account';
            submit.textContent = I18n.get('signup.submit') || 'Sign up';
            footer.innerHTML = (I18n.get('signup.loginLink') || 'Already have an account? <a id="login-link">Log in</a>');
            if (forgotLink) forgotLink.style.display = 'none';
        }
    },

    async handleSubmit(e) {
        e.preventDefault();
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const endpoint = this._isLogin ? '/api/auth/login' : '/api/auth/signup';

        try {
            const resp = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            if (!resp.ok) {
                const data = await resp.json();
                this.showError(data.detail || I18n.get('errors.serverError') || 'Something went wrong');
                return;
            }

            const user = await resp.json();
            State.set('user', user);
            this.updateUI(user);
            this.hideModal();

            // Execute pending search if any
            if (this._pendingSearch) {
                this._pendingSearch();
                this._pendingSearch = null;
            }
        } catch (err) {
            this.showError(I18n.get('forgotPassword.networkError') || 'Network error. Please try again.');
        }
    },

    showError(msg) {
        // Show error inline in the modal
        let errorEl = document.getElementById('auth-error');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.id = 'auth-error';
            errorEl.className = 'form-error';
            document.getElementById('signup-form').prepend(errorEl);
        }
        errorEl.textContent = msg;
        errorEl.style.display = 'block';
    },

    updateUI(user) {
        const signinBtn = document.getElementById('signin-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const signinMobile = document.getElementById('signin-btn-mobile');
        const logoutMobile = document.getElementById('logout-btn-mobile');
        const creditsPill = document.getElementById('credits-pill');
        const userMenu = document.getElementById('user-menu');
        const mobileAuthLinks = document.getElementById('mobile-auth-links');

        if (user) {
            signinBtn.style.display = 'none';
            logoutBtn.style.display = 'none'; // hide old logout, dropdown has Sign Out
            creditsPill.style.display = 'flex';
            document.getElementById('credits-count').textContent = user.credits_remaining;

            // Show user dropdown with truncated email
            if (userMenu) {
                userMenu.style.display = '';
                const emailDisplay = document.getElementById('user-email-display');
                if (emailDisplay && user.email) {
                    const truncated = user.email.length > 20 ? user.email.substring(0, 18) + '...' : user.email;
                    emailDisplay.textContent = truncated;
                }
            }

            // Mobile: show auth links, hide sign in
            if (signinMobile) signinMobile.style.display = 'none';
            if (logoutMobile) logoutMobile.style.display = '';
            if (mobileAuthLinks) mobileAuthLinks.style.display = '';
        } else {
            signinBtn.style.display = '';
            logoutBtn.style.display = 'none';
            creditsPill.style.display = 'none';

            // Hide user dropdown
            if (userMenu) {
                userMenu.style.display = 'none';
                this._closeDropdown();
            }

            // Mobile: hide auth links, show sign in
            if (signinMobile) signinMobile.style.display = '';
            if (logoutMobile) logoutMobile.style.display = 'none';
            if (mobileAuthLinks) mobileAuthLinks.style.display = 'none';
        }
    },
};

// Listen for user state changes
State.on('user', (user) => Auth.updateUI(user));

document.addEventListener('DOMContentLoaded', () => Auth.init());
