const Credits = {
    _packs: [],

    init() {
        // Click credits pill → open purchase modal
        document.getElementById('credits-pill').addEventListener('click', () => this.showModal());

        // Listen for user changes to update display
        State.on('user', (user) => {
            if (user) {
                document.getElementById('credits-count').textContent = user.credits_remaining;
            }
        });

        // Check URL for payment result
        const params = new URLSearchParams(window.location.search);
        if (params.get('payment') === 'success') {
            this.showToast('Credits added successfully!', 'success');
            // Refresh user data
            Auth.checkSession();
            // Clean URL
            window.history.replaceState({}, '', '/');
        } else if (params.get('payment') === 'cancelled') {
            window.history.replaceState({}, '', '/');
        }
    },

    async showModal() {
        // Fetch packs if not cached
        if (this._packs.length === 0) {
            try {
                const resp = await fetch('/api/credits/packs');
                const data = await resp.json();
                this._packs = data.packs;
            } catch (e) {
                App.showToast('Failed to load credit packs', 'error');
                return;
            }
        }

        // Create or show modal
        let modal = document.getElementById('credits-modal');
        if (!modal) {
            modal = this.createModal();
            document.body.appendChild(modal);
        }
        modal.classList.add('is-visible');
    },

    hideModal() {
        const modal = document.getElementById('credits-modal');
        if (modal) modal.classList.remove('is-visible');
    },

    createModal() {
        const modal = document.createElement('div');
        modal.id = 'credits-modal';
        modal.className = 'modal-overlay';

        const perThousand = (pack) => ((pack.price_cents / pack.credits) * 1000 / 100).toFixed(2);

        modal.innerHTML = `
            <div class="modal-backdrop" id="credits-backdrop"></div>
            <div class="modal-card" style="max-width:520px;">
                <button class="modal-close" id="credits-close">&times;</button>
                <h2 class="modal-title">Buy Credits</h2>
                <p class="modal-subtitle" style="margin-bottom:1.5rem;opacity:0.7;">1 credit = 1 filtered result. Filters save you money.</p>
                <div class="credit-packs">
                    ${this._packs.map(pack => `
                        <button class="credit-pack" data-pack-id="${pack.id}">
                            <div class="credit-pack__label">${pack.label}</div>
                            <div class="credit-pack__credits">${pack.credits.toLocaleString()} credits</div>
                            <div class="credit-pack__price">$${(pack.price_cents / 100).toFixed(2)}</div>
                            <div class="credit-pack__per">$${perThousand(pack)}/1,000</div>
                        </button>
                    `).join('')}
                </div>
            </div>
        `;

        // Event listeners
        modal.querySelector('#credits-backdrop').addEventListener('click', () => this.hideModal());
        modal.querySelector('#credits-close').addEventListener('click', () => this.hideModal());

        modal.querySelectorAll('.credit-pack').forEach(btn => {
            btn.addEventListener('click', () => this.purchase(btn.dataset.packId));
        });

        return modal;
    },

    async purchase(packId) {
        try {
            const resp = await fetch('/api/credits/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pack_id: packId }),
            });

            if (!resp.ok) {
                const data = await resp.json();
                throw new Error(data.detail || 'Checkout failed');
            }

            const data = await resp.json();
            window.location.href = data.checkout_url;
        } catch (err) {
            App.showToast(err.message, 'error');
        }
    },

    showToast(msg, type) {
        App.showToast(msg, type);
    },
};

document.addEventListener('DOMContentLoaded', () => Credits.init());
