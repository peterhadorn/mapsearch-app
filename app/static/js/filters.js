const Filters = {
    init() {
        // Toggle filter panel visibility — open by default
        const toggle = document.getElementById('filter-toggle');
        const panel = document.getElementById('filters-panel');
        panel.classList.add('is-open');
        toggle.setAttribute('aria-expanded', 'true');
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

        // Range sliders
        const ratingSlider = document.getElementById('rating-slider');
        const ratingValue = document.getElementById('rating-value');
        ratingSlider.addEventListener('input', () => {
            ratingValue.textContent = parseFloat(ratingSlider.value).toFixed(1);
            State.set('filters', this.getFilterState());
        });

        const reviewsSlider = document.getElementById('reviews-slider');
        const reviewsValue = document.getElementById('reviews-value');
        reviewsSlider.addEventListener('input', () => {
            reviewsValue.textContent = reviewsSlider.value;
            State.set('filters', this.getFilterState());
        });

        // Near me toggle
        document.getElementById('nearme-toggle').addEventListener('change', () => {
            State.set('filters', this.getFilterState());
        });

        // Category select
        document.getElementById('category-select').addEventListener('change', () => {
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
        return {
            has_website: this.getTriToggle('website'),
            has_email: this.getTriToggle('email'),
            has_phone: this.getTriToggle('phone'),
            min_rating: parseFloat(document.getElementById('rating-slider').value),
            min_reviews: parseInt(document.getElementById('reviews-slider').value),
            is_claimed: this.getTriToggle('claimed'),
            has_photos: this.getTriToggle('photos'),
            category: document.getElementById('category-select').value || null,
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

    // Populate category dropdown from search results
    populateCategories(results) {
        const select = document.getElementById('category-select');
        const categories = [...new Set(results.map(r => r.category).filter(Boolean))].sort();

        // Keep first "All categories" option, remove rest
        while (select.options.length > 1) select.remove(1);

        categories.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat;
            opt.textContent = cat;
            select.appendChild(opt);
        });
    },
};

document.addEventListener('DOMContentLoaded', () => Filters.init());
