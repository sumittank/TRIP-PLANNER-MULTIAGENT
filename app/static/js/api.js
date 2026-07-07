/**
 * Reusable API client for AI Travel Planner
 */
const API = {
    baseUrl: '/api',

    get userId() {
        return localStorage.getItem('userId') || 'default_user';
    },

    set userId(id) {
        localStorage.setItem('userId', id);
    },

    async request(method, path, body = null) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) opts.body = JSON.stringify(body);

        const res = await fetch(`${this.baseUrl}${path}`, opts);
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Request failed (${res.status})`);
        }
        if (res.status === 204) return null;
        const contentType = res.headers.get('content-type') || '';
        if (contentType.includes('application/json')) return res.json();
        return res.text();
    },

    planTrip(query, userId = this.userId, threadId = null) {
        return this.request('POST', '/plan-trip', {
            query,
            user_id: userId,
            thread_id: threadId,
        });
    },

    chat(message, userId = this.userId) {
        return this.request('POST', '/chat', {
            message,
            user_id: userId,
        });
    },

    getHistory(userId = this.userId) {
        return this.request('GET', `/history?user_id=${encodeURIComponent(userId)}`);
    },

    getTrip(tripId) {
        return this.request('GET', `/trip/${tripId}`);
    },

    deleteTrip(tripId) {
        return this.request('DELETE', `/history/${tripId}`);
    },

    getSaved(userId = this.userId) {
        return this.request('GET', `/saved?user_id=${encodeURIComponent(userId)}`);
    },

    toggleFavourite(tripId) {
        return this.request('POST', `/trip/${tripId}/favourite`);
    },

    getPreferences(userId = this.userId) {
        return this.request('GET', `/preferences?user_id=${encodeURIComponent(userId)}`);
    },

    updatePreferences(data, userId = this.userId) {
        return this.request('POST', `/preferences?user_id=${encodeURIComponent(userId)}`, data);
    },

    getAnalytics(userId = this.userId) {
        return this.request('GET', `/analytics?user_id=${encodeURIComponent(userId)}`);
    },

    comparePlans(tripIdA, tripIdB) {
        return this.request('POST', '/compare', {
            trip_id_a: tripIdA,
            trip_id_b: tripIdB,
        });
    },

    exportJsonUrl(tripId) {
        return `${this.baseUrl}/trip/${tripId}/export/json`;
    },

    exportMarkdownUrl(tripId) {
        return `${this.baseUrl}/trip/${tripId}/export/markdown`;
    },

    async healthCheck() {
        const res = await fetch('/health');
        return res.json();
    },
};
