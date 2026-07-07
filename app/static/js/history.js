/**
 * Trip History page logic
 */
(function () {
    const listEl = document.getElementById('history-list');
    const userIdEl = document.getElementById('history-user-id');
    let selectedForCompare = [];

    function init() {
        const savedUserId = localStorage.getItem('userId');
        if (savedUserId && userIdEl) userIdEl.value = savedUserId;

        userIdEl?.addEventListener('change', loadHistory);
        document.addEventListener('DOMContentLoaded', loadHistory);
        if (document.readyState !== 'loading') loadHistory();
    }

    async function loadHistory() {
        const userId = userIdEl?.value?.trim() || 'default_user';
        localStorage.setItem('userId', userId);

        if (!listEl) return;
        listEl.innerHTML = '<div class="text-slate-400 text-center py-12">Loading...</div>';

        try {
            const data = await API.getHistory(userId);
            if (!data.trips?.length) {
                listEl.innerHTML = `
                    <div class="text-center py-16">
                        <div class="text-5xl mb-4">🗺️</div>
                        <p class="text-slate-400">No trips yet. <a href="/planner" class="text-primary-400 hover:underline">Plan your first trip!</a></p>
                    </div>`;
                return;
            }

            listEl.innerHTML = data.trips
                .map(
                    (trip) => `
                <div class="history-item" data-trip-id="${trip.trip_id}">
                    <div class="flex items-start justify-between gap-4">
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-1">
                                <h3 class="text-white font-semibold">${escapeHtml(trip.destination || 'Trip')}</h3>
                                ${trip.is_favourite ? '<span class="text-yellow-400">⭐</span>' : ''}
                                ${UI.confidenceBadge(trip.confidence_score)}
                            </div>
                            <p class="text-slate-400 text-sm mb-2">${escapeHtml(trip.user_query)}</p>
                            <div class="flex flex-wrap gap-2 text-xs text-slate-500">
                                <span>${UI.formatDate(trip.created_at)}</span>
                                <span>•</span>
                                <span>Agents: ${(trip.agents_run || []).join(', ') || 'N/A'}</span>
                            </div>
                        </div>
                        <div class="flex flex-col gap-2 shrink-0">
                            <button class="btn-secondary px-3 py-1 text-xs view-btn" data-id="${trip.trip_id}">View</button>
                            <button class="btn-secondary px-3 py-1 text-xs fav-btn" data-id="${trip.trip_id}">⭐ Fav</button>
                            <button class="btn-secondary px-3 py-1 text-xs compare-btn" data-id="${trip.trip_id}">Compare</button>
                            <button class="btn-danger delete-btn" data-id="${trip.trip_id}">Delete</button>
                        </div>
                    </div>
                </div>
            `
                )
                .join('');

            bindEvents();
        } catch (err) {
            listEl.innerHTML = `<div class="text-red-400 text-center py-12">${escapeHtml(err.message)}</div>`;
        }
    }

    function bindEvents() {
        document.querySelectorAll('.view-btn').forEach((btn) => {
            btn.addEventListener('click', async () => {
                try {
                    const trip = await API.getTrip(btn.dataset.id);
                    UI.showModal(
                        trip.destination || 'Trip Details',
                        UI.renderMarkdown(trip.final_response || trip.itinerary || 'No content')
                    );
                } catch (e) {
                    UI.toast(e.message, 'error');
                }
            });
        });

        document.querySelectorAll('.fav-btn').forEach((btn) => {
            btn.addEventListener('click', async () => {
                try {
                    await API.toggleFavourite(btn.dataset.id);
                    UI.toast('Favourite updated!', 'success');
                    loadHistory();
                } catch (e) {
                    UI.toast(e.message, 'error');
                }
            });
        });

        document.querySelectorAll('.delete-btn').forEach((btn) => {
            btn.addEventListener('click', async () => {
                if (!confirm('Delete this trip?')) return;
                try {
                    await API.deleteTrip(btn.dataset.id);
                    UI.toast('Trip deleted', 'success');
                    loadHistory();
                } catch (e) {
                    UI.toast(e.message, 'error');
                }
            });
        });

        document.querySelectorAll('.compare-btn').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id;
                if (selectedForCompare.includes(id)) {
                    selectedForCompare = selectedForCompare.filter((x) => x !== id);
                    btn.classList.remove('ring-2', 'ring-primary-500');
                    return;
                }
                selectedForCompare.push(id);
                btn.classList.add('ring-2', 'ring-primary-500');

                if (selectedForCompare.length === 2) {
                    try {
                        const result = await API.comparePlans(selectedForCompare[0], selectedForCompare[1]);
                        const rec = result.recommended === result.trip_a.id ? 'Trip A' : 'Trip B';
                        UI.showModal(
                            'Plan Comparison',
                            `<p><strong>Trip A:</strong> ${result.trip_a.destination} (${Math.round(result.trip_a.confidence * 100)}%)</p>
                             <p><strong>Trip B:</strong> ${result.trip_b.destination} (${Math.round(result.trip_b.confidence * 100)}%)</p>
                             <p class="mt-3"><strong>Recommended:</strong> ${rec}</p>
                             <p>Confidence difference: ${Math.abs(result.comparison.confidence_diff * 100).toFixed(1)}%</p>`
                        );
                    } catch (e) {
                        UI.toast(e.message, 'error');
                    }
                    selectedForCompare = [];
                    document.querySelectorAll('.compare-btn').forEach((b) => b.classList.remove('ring-2', 'ring-primary-500'));
                } else {
                    UI.toast('Select one more trip to compare', 'info');
                }
            });
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    init();
})();
