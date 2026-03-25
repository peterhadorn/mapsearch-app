/**
 * MapSearch — Theme Toggle
 * Cycles through light -> dark -> system themes.
 * Persists choice to localStorage under 'mapsearch-theme'.
 */
const ThemeToggle = {
    STORAGE_KEY: 'mapsearch-theme',
    CYCLE: ['light', 'dark', 'system'],

    init() {
        const toggle = document.getElementById('theme-toggle');
        if (!toggle) return;

        toggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            const idx = this.CYCLE.indexOf(current);
            const next = this.CYCLE[(idx + 1) % this.CYCLE.length];
            this.setTheme(next);
        });
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try { localStorage.setItem(this.STORAGE_KEY, theme); } catch (e) {}

        // Publish theme change for other modules (e.g., map tile switching)
        if (typeof AppState !== 'undefined' && AppState.publish) {
            AppState.publish('theme:changed', theme);
        }
    },

    getTheme() {
        return document.documentElement.getAttribute('data-theme') || 'dark';
    },

    isDark() {
        const theme = this.getTheme();
        if (theme === 'system') {
            return window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
        return theme === 'dark';
    }
};

document.addEventListener('DOMContentLoaded', () => ThemeToggle.init());
