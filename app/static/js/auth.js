const Auth = {
    _isLogin: false,
    _pendingSearch: null,  // callback to execute after auth

    init() {
        // Sign in button opens modal
        document.getElementById('signin-btn').addEventListener('click', () => this.showModal());

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

        // Check if already logged in
        this.checkSession();
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
        document.getElementById('signup-modal').classList.add('is-visible');
        document.getElementById('signup-email').focus();
    },

    hideModal() {
        document.getElementById('signup-modal').classList.remove('is-visible');
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
        if (user) {
            document.getElementById('signin-btn').style.display = 'none';
            document.getElementById('credits-pill').style.display = 'flex';
            document.getElementById('credits-count').textContent = user.credits_remaining;
        } else {
            document.getElementById('signin-btn').style.display = '';
            document.getElementById('credits-pill').style.display = 'none';
        }
    },
};

// Listen for user state changes
State.on('user', (user) => Auth.updateUI(user));

document.addEventListener('DOMContentLoaded', () => Auth.init());
