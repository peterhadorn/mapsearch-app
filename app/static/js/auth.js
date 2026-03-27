const Auth = {
    _isLogin: false,
    _pendingSearch: null,  // callback to execute after auth

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

        // Close modal
        document.getElementById('modal-close').addEventListener('click', () => this.hideModal());
        document.getElementById('modal-backdrop').addEventListener('click', () => this.hideModal());

        // Email/password form
        document.getElementById('signup-form').addEventListener('submit', (e) => this.handleSubmit(e));

        // Toggle login/signup
        document.getElementById('login-link').addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMode();
        });

        // Escape key closes modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.hideModal();
        });

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
        document.getElementById('signup-modal').classList.add('is-open');
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

        if (this._isLogin) {
            title.textContent = 'Welcome back';
            submit.textContent = 'Log in';
            footer.innerHTML = 'Don\'t have an account? <a id="login-link">Sign up</a>';
        } else {
            title.textContent = 'Create free account';
            submit.textContent = 'Sign up';
            footer.innerHTML = 'Already have an account? <a id="login-link">Log in</a>';
        }
        // Re-bind toggle link
        document.getElementById('login-link').addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMode();
        });
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
                this.showError(data.detail || 'Something went wrong');
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
            this.showError('Network error. Please try again.');
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

        if (user) {
            signinBtn.style.display = 'none';
            logoutBtn.style.display = '';
            creditsPill.style.display = 'flex';
            document.getElementById('credits-count').textContent = user.credits_remaining;
            if (signinMobile) signinMobile.style.display = 'none';
            if (logoutMobile) logoutMobile.style.display = '';
        } else {
            signinBtn.style.display = '';
            logoutBtn.style.display = 'none';
            creditsPill.style.display = 'none';
            if (signinMobile) signinMobile.style.display = '';
            if (logoutMobile) logoutMobile.style.display = 'none';
        }
    },
};

// Listen for user state changes
State.on('user', (user) => Auth.updateUI(user));

document.addEventListener('DOMContentLoaded', () => Auth.init());
