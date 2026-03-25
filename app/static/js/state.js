/**
 * Minimal pub/sub state management for MapSearch.
 * All modules subscribe to state changes instead of cross-referencing each other.
 */
const State = {
    _state: {
        user: null,           // { id, email, credits }
        searchResults: null,  // array of business objects
        searchMeta: null,     // { search_id, result_count, max_reached }
        filters: {},          // current filter state
        loading: false,
        error: null,
    },
    _listeners: {},

    get(key) { return this._state[key]; },

    set(key, value) {
        this._state[key] = value;
        (this._listeners[key] || []).forEach(fn => fn(value));
    },

    on(key, fn) {
        if (!this._listeners[key]) this._listeners[key] = [];
        this._listeners[key].push(fn);
    },
};
