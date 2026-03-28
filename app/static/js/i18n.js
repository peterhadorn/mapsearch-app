const I18n = {
    _translations: {},
    _locale: 'en',
    _readyResolve: null,
    _readyPromise: null,

    _ensurePromise() {
        if (!this._readyPromise) {
            this._readyPromise = new Promise(resolve => { this._readyResolve = resolve; });
        }
    },

    async init() {
        this._ensurePromise();

        // Detect browser language, check localStorage override
        const saved = localStorage.getItem('mapsearch-lang');
        const browser = (navigator.language || 'en').split('-')[0];
        this._locale = saved || (['en', 'fr', 'de', 'es'].includes(browser) ? browser : 'en');

        // Set selector to current locale
        const select = document.getElementById('lang-select');
        if (select) {
            select.value = this._locale;
            select.addEventListener('change', () => {
                this._locale = select.value;
                localStorage.setItem('mapsearch-lang', this._locale);
                this.loadAndApply();
            });
        }

        await this.loadAndApply();
        this._readyResolve();
    },

    async ready() {
        this._ensurePromise();
        await this._readyPromise;
    },

    async loadAndApply() {
        try {
            const resp = await fetch(`/static/i18n/${this._locale}.json`);
            if (resp.ok) {
                this._translations = await resp.json();
            }
        } catch (e) {
            console.warn('Failed to load translations for', this._locale);
        }
        this.applyAll();
    },

    applyAll() {
        document.querySelectorAll('[data-i18n]').forEach(el => this.translateElement(el));
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            const val = this.get(key);
            if (val) el.placeholder = val;
        });
    },

    translateElement(el) {
        const key = el.getAttribute('data-i18n');
        const val = this.get(key);
        if (val) el.textContent = val;
    },

    get(key) {
        // Support nested keys with dot notation: "filters.website"
        const keys = key.split('.');
        let val = this._translations;
        for (const k of keys) {
            if (val && typeof val === 'object') val = val[k];
            else return null;
        }
        return typeof val === 'string' ? val : null;
    },

    getLocale() {
        return this._locale;
    },
};

document.addEventListener('DOMContentLoaded', () => I18n.init());
