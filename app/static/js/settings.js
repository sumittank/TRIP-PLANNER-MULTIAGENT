/**
 * Settings page logic
 */
(function () {
    const form = document.getElementById('preferences-form');
    const userIdEl = document.getElementById('settings-user-id');
    const analyticsEl = document.getElementById('analytics-panel');

    function init() {
        const savedUserId = localStorage.getItem('userId');
        if (savedUserId && userIdEl) userIdEl.value = savedUserId;

        userIdEl?.addEventListener('change', () => {
            localStorage.setItem('userId', userIdEl.value);
            loadPreferences();
            loadAnalytics();
        });

        form?.addEventListener('submit', savePreferences);

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                loadPreferences();
                loadAnalytics();
            });
        } else {
            loadPreferences();
            loadAnalytics();
        }
    }

    async function loadPreferences() {
        const userId = userIdEl?.value?.trim() || 'default_user';
        try {
            const prefs = await API.getPreferences(userId);
            setVal('preferred-airline', prefs.preferred_airline);
            setVal('hotel-type', prefs.favourite_hotel_type);
            setVal('travel-style', prefs.travel_style);
            setVal('budget-range', prefs.budget_range);
            setVal('destinations', (prefs.previous_destinations || []).join(', '));
        } catch (e) {
            UI.toast('Could not load preferences', 'error');
        }
    }

    async function loadAnalytics() {
        const userId = userIdEl?.value?.trim() || 'default_user';
        if (!analyticsEl) return;
        try {
            const data = await API.getAnalytics(userId);
            analyticsEl.innerHTML = `
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="metric-box"><div class="metric-val">${data.total_trips}</div><div class="metric-lbl">Total Trips</div></div>
                    <div class="metric-box"><div class="metric-val">${data.favourite_trips}</div><div class="metric-lbl">Favourites</div></div>
                    <div class="metric-box"><div class="metric-val">${data.total_searches}</div><div class="metric-lbl">Searches</div></div>
                    <div class="metric-box"><div class="metric-val">${Math.round(data.average_confidence * 100)}%</div><div class="metric-lbl">Avg Confidence</div></div>
                </div>
                ${data.recent_destinations?.length ? `
                    <div class="mt-4">
                        <p class="text-sm text-slate-400 mb-2">Recent Destinations</p>
                        <div class="flex flex-wrap gap-2">
                            ${data.recent_destinations.map((d) => `<span class="suggestion-chip">${d}</span>`).join('')}
                        </div>
                    </div>` : ''}
            `;
        } catch {
            analyticsEl.innerHTML = '<p class="text-slate-400">Analytics unavailable</p>';
        }
    }

    async function savePreferences(e) {
        e.preventDefault();
        const userId = userIdEl?.value?.trim() || 'default_user';
        localStorage.setItem('userId', userId);

        const data = {
            preferred_airline: getVal('preferred-airline'),
            favourite_hotel_type: getVal('hotel-type'),
            travel_style: getVal('travel-style'),
            budget_range: getVal('budget-range'),
            previous_destinations: getVal('destinations')
                .split(',')
                .map((s) => s.trim())
                .filter(Boolean),
        };

        const btn = document.getElementById('save-prefs-btn');
        UI.setLoading(btn, true, 'Saving...');

        try {
            await API.updatePreferences(data, userId);
            UI.toast('Preferences saved!', 'success');
            loadAnalytics();
        } catch (err) {
            UI.toast(err.message, 'error');
        } finally {
            UI.setLoading(btn, false);
            const textEl = document.getElementById('save-prefs-text');
            if (textEl) textEl.textContent = 'Save Preferences';
        }
    }

    function setVal(id, value) {
        const el = document.getElementById(id);
        if (el) el.value = value || '';
    }

    function getVal(id) {
        return document.getElementById(id)?.value?.trim() || '';
    }

    init();
})();
