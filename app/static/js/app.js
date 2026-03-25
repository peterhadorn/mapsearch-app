const App = {
    init() {
        // Search button
        document.getElementById('search-btn').addEventListener('click', () => this.doSearch());

        // Enter key in inputs
        document.getElementById('keyword-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.doSearch();
        });
        document.getElementById('location-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.doSearch();
        });

        // Back button — return to search view
        document.getElementById('back-btn').addEventListener('click', () => this.showSearchView());

        // Export CSV
        document.getElementById('export-btn').addEventListener('click', () => this.exportCSV());

        // Loading state listener
        State.on('loading', (loading) => this.updateLoadingState(loading));
    },

    async doSearch() {
        const keyword = document.getElementById('keyword-input').value.trim();
        const location = document.getElementById('location-input').value.trim();

        if (!keyword || !location) {
            this.showToast('Please enter both a keyword and location.', 'warning');
            return;
        }

        // Check if logged in
        const user = State.get('user');
        if (!user) {
            Auth.showModal(() => this.doSearch());
            return;
        }

        State.set('loading', true);
        State.set('error', null);

        try {
            const filterState = Filters.getFilterState();
            const resp = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    keyword,
                    location,
                    zoom_level: Filters.getZoomLevel(),
                    near_me: Filters.isNearMe(),
                    filters: filterState,
                }),
            });

            if (!resp.ok) {
                const data = await resp.json();
                throw new Error(data.detail || 'Search failed');
            }

            const data = await resp.json();

            // Handle insufficient credits
            if (data.insufficient_credits) {
                this.showInsufficientCredits(data.needed, data.available);
                State.set('loading', false);
                return;
            }

            // Update state — modules react via pub/sub
            State.set('searchResults', data.results);
            State.set('searchMeta', {
                search_id: data.search_id,
                result_count: data.result_count,
                max_reached: data.max_reached,
                credits_used: data.credits_used,
            });

            // Update credits display
            const currentUser = State.get('user');
            currentUser.credits_remaining = data.credits_remaining;
            State.set('user', currentUser);

            // Update results count text
            document.getElementById('results-count').textContent =
                `${data.result_count} results for "${keyword}" in ${location}`;

            // Populate category dropdown from results
            Filters.populateCategories(data.results);

            // Show results view
            this.showResultsView();

            // Show max reached warning
            if (data.max_reached) {
                this.showToast('Results capped at 700. Try a smaller search area for complete results.', 'warning');
            }

        } catch (err) {
            State.set('error', err.message);
            this.showToast(err.message, 'error');
        } finally {
            State.set('loading', false);
        }
    },

    showResultsView() {
        document.getElementById('results-panel').classList.add('is-visible');
        document.getElementById('search-float').classList.add('is-collapsed');
    },

    showSearchView() {
        document.getElementById('results-panel').classList.remove('is-visible');
        document.getElementById('search-float').classList.remove('is-collapsed');
    },

    showInsufficientCredits(needed, available) {
        this.showToast(
            `This search returns ${needed} results but you only have ${available} credits. Buy more credits to continue.`,
            'warning'
        );
    },

    updateLoadingState(loading) {
        const btn = document.getElementById('search-btn');
        if (loading) {
            btn.disabled = true;
            btn.classList.add('is-loading');
        } else {
            btn.disabled = false;
            btn.classList.remove('is-loading');
        }
    },

    async exportCSV() {
        const meta = State.get('searchMeta');
        if (!meta) return;

        try {
            const resp = await fetch(`/api/export/${meta.search_id}`);
            if (!resp.ok) throw new Error('Export failed');

            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `mapsearch-${meta.search_id}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            this.showToast('Export failed. Please try again.', 'error');
        }
    },

    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.textContent = message;

        // Append to body
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = 'position:fixed;top:80px;right:20px;z-index:10000;display:flex;flex-direction:column;gap:8px;';
            document.body.appendChild(container);
        }
        container.appendChild(toast);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    },
};

document.addEventListener('DOMContentLoaded', () => App.init());
