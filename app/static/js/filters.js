const Filters = {
    init() {
        // Toggle filter panel visibility — open on desktop, closed on mobile
        const toggle = document.getElementById('filter-toggle');
        const panel = document.getElementById('filters-panel');
        const isMobile = window.innerWidth < 768;
        if (!isMobile) {
            panel.classList.add('is-open');
            toggle.setAttribute('aria-expanded', 'true');
        }
        toggle.addEventListener('click', () => {
            const expanded = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', !expanded);
            panel.classList.toggle('is-open');
        });

        // Tri-toggle buttons
        document.querySelectorAll('.tri-toggle').forEach(group => {
            group.querySelectorAll('.tri-toggle__btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    group.querySelectorAll('.tri-toggle__btn').forEach(b => b.classList.remove('is-active'));
                    btn.classList.add('is-active');
                    State.set('filters', this.getFilterState());
                });
            });
        });

        // Checkbox filters (email, phone)
        document.querySelectorAll('.filter-item--checkbox input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', () => {
                State.set('filters', this.getFilterState());
            });
        });

        // Near me toggle
        document.getElementById('nearme-toggle').addEventListener('change', () => {
            State.set('filters', this.getFilterState());
        });

        // Set initial state
        State.set('filters', this.getFilterState());
    },

    getTriToggle(filterName) {
        const group = document.querySelector(`.tri-toggle[data-filter="${filterName}"]`);
        if (!group) return 'any';
        const active = group.querySelector('.tri-toggle__btn.is-active');
        return active ? active.getAttribute('data-value') : 'any';
    },

    getFilterState() {
        const ratingVal = this.getTriToggle('rating');
        return {
            has_website: this.getTriToggle('website'),
            has_email: document.getElementById('email-toggle').checked ? 'yes' : 'any',
            has_phone: document.getElementById('phone-toggle').checked ? 'yes' : 'any',
            min_rating: ratingVal === 'any' ? 0 : parseFloat(ratingVal),
            price_level: this.getTriToggle('price'),
        };
    },

    getZoomLevel() {
        const val = this.getTriToggle('zoom');
        return parseInt(val) || 13;
    },

    isNearMe() {
        return document.getElementById('nearme-toggle').checked;
    },
};

document.addEventListener('DOMContentLoaded', () => Filters.init());
