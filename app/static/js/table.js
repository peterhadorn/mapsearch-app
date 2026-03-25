const Table = {
    _results: [],
    _sortCol: null,
    _sortDir: 'asc',
    _page: 1,
    _perPage: 50,
    _visibleColumns: ['business_name', 'category', 'city', 'phone', 'domain', 'email', 'rating', 'reviews_count'],
    _allColumns: [
        { key: 'business_name', label: 'Business' },
        { key: 'category', label: 'Category' },
        { key: 'city', label: 'City' },
        { key: 'phone', label: 'Phone' },
        { key: 'domain', label: 'Website' },
        { key: 'email', label: 'Email' },
        { key: 'rating', label: 'Rating' },
        { key: 'reviews_count', label: 'Reviews' },
        { key: 'is_claimed', label: 'Claimed', hidden: true },
        { key: 'photos_count', label: 'Photos', hidden: true },
        { key: 'price_level', label: 'Price', hidden: true },
        { key: 'latitude', label: 'Lat', hidden: true },
        { key: 'longitude', label: 'Lng', hidden: true },
        { key: 'google_maps_url', label: 'Maps Link', hidden: true },
        { key: 'business_status', label: 'Status', hidden: true },
    ],

    init() {
        // Sort column click
        document.querySelectorAll('#results-table thead th[data-sortable]').forEach((th, index) => {
            th.addEventListener('click', () => this.sort(index));
            th.style.cursor = 'pointer';
        });

        // Column toggle dropdown
        this.initColumnToggle();

        // Listen for results
        State.on('searchResults', (results) => {
            this._results = results || [];
            this._page = 1;
            this.render();
        });

        // Row hover → highlight map pin
        document.getElementById('results-table-body').addEventListener('mouseover', (e) => {
            const row = e.target.closest('tr[data-index]');
            if (row) State.set('highlightedResult', parseInt(row.dataset.index));
        });

        document.getElementById('results-table-body').addEventListener('mouseout', () => {
            State.set('highlightedResult', null);
        });

        // Row click → pan map to pin
        document.getElementById('results-table-body').addEventListener('click', (e) => {
            const row = e.target.closest('tr[data-index]');
            if (row && typeof MapModule !== 'undefined') {
                MapModule.panToPin(parseInt(row.dataset.index));
            }
        });

        // Listen for highlighted result from map
        State.on('highlightedResult', (index) => this.highlightRow(index));
    },

    render() {
        const tbody = document.getElementById('results-table-body');
        const start = (this._page - 1) * this._perPage;
        const end = Math.min(start + this._perPage, this._results.length);
        const pageResults = this._results.slice(start, end);

        tbody.innerHTML = pageResults.map((r, i) => {
            const idx = start + i;
            return `<tr data-index="${idx}">
                <td>${this.escapeHtml(r.business_name || '')}</td>
                <td>${this.escapeHtml(r.category || '')}</td>
                <td>${this.escapeHtml(r.city || '')}</td>
                <td>${r.phone ? `<a href="tel:${this.escapeHtml(r.phone)}">${this.escapeHtml(r.phone)}</a>` : '—'}</td>
                <td>${r.domain ? `<a href="${this.escapeHtml(r.url || 'https://' + r.domain)}" target="_blank" rel="noopener">${this.escapeHtml(r.domain)}</a>` : '—'}</td>
                <td>${r.email ? `<a href="mailto:${this.escapeHtml(r.email)}">${this.escapeHtml(r.email)}</a>` : '—'}</td>
                <td style="text-align:right">${r.rating ? `${'★'.repeat(Math.round(r.rating))} ${r.rating}` : '—'}</td>
                <td style="text-align:right">${r.reviews_count != null ? r.reviews_count.toLocaleString() : '—'}</td>
            </tr>`;
        }).join('');

        // Update footer
        document.getElementById('results-footer-info').textContent =
            `Showing ${start + 1}–${end} of ${this._results.length}`;

        this.renderPagination();
    },

    sort(colIndex) {
        const keys = ['business_name', 'category', 'city', 'phone', 'domain', 'email', 'rating', 'reviews_count'];
        const key = keys[colIndex];
        if (!key) return;

        if (this._sortCol === key) {
            this._sortDir = this._sortDir === 'asc' ? 'desc' : 'asc';
        } else {
            this._sortCol = key;
            this._sortDir = 'asc';
        }

        const numericCols = ['rating', 'reviews_count'];
        const isNumeric = numericCols.includes(key);
        const dir = this._sortDir === 'asc' ? 1 : -1;

        this._results.sort((a, b) => {
            let va = a[key], vb = b[key];
            if (va == null) return 1;
            if (vb == null) return -1;
            if (isNumeric) return (parseFloat(va) - parseFloat(vb)) * dir;
            return String(va).localeCompare(String(vb)) * dir;
        });

        // Update sort indicators
        document.querySelectorAll('#results-table thead th').forEach((th, i) => {
            th.classList.remove('sort-asc', 'sort-desc');
            if (i === colIndex) th.classList.add(`sort-${this._sortDir}`);
        });

        this._page = 1;
        this.render();
        State.set('searchResults', this._results);  // re-render map pins too
    },

    renderPagination() {
        const totalPages = Math.ceil(this._results.length / this._perPage);
        const pagination = document.getElementById('pagination');
        if (totalPages <= 1) { pagination.innerHTML = ''; return; }

        let html = '';
        if (this._page > 1) html += `<button class="pagination__btn" data-page="${this._page - 1}">&laquo;</button>`;

        for (let p = 1; p <= totalPages; p++) {
            if (p === 1 || p === totalPages || Math.abs(p - this._page) <= 2) {
                html += `<button class="pagination__btn ${p === this._page ? 'is-active' : ''}" data-page="${p}">${p}</button>`;
            } else if (Math.abs(p - this._page) === 3) {
                html += '<span class="pagination__dots">…</span>';
            }
        }

        if (this._page < totalPages) html += `<button class="pagination__btn" data-page="${this._page + 1}">&raquo;</button>`;

        pagination.innerHTML = html;
        pagination.querySelectorAll('.pagination__btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this._page = parseInt(btn.dataset.page);
                this.render();
            });
        });
    },

    highlightRow(index) {
        document.querySelectorAll('#results-table-body tr').forEach(tr => {
            tr.classList.toggle('is-highlighted', parseInt(tr.dataset.index) === index);
        });
    },

    initColumnToggle() {
        const trigger = document.getElementById('columns-toggle');
        const dropdown = trigger.closest('.columns-dropdown');

        // Create dropdown content
        const menu = document.createElement('div');
        menu.className = 'columns-dropdown__menu';
        this._allColumns.forEach(col => {
            const label = document.createElement('label');
            label.className = 'columns-dropdown__item';
            const checked = this._visibleColumns.includes(col.key) ? 'checked' : '';
            label.innerHTML = `<input type="checkbox" value="${col.key}" ${checked}> ${col.label}`;
            menu.appendChild(label);
        });
        dropdown.appendChild(menu);

        trigger.addEventListener('click', () => {
            menu.classList.toggle('is-open');
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) menu.classList.remove('is-open');
        });
    },

    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },
};

document.addEventListener('DOMContentLoaded', () => Table.init());
