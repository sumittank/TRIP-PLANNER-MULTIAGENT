/**
 * Saved / Favourite trips page logic
 */
(function () {
    const listEl = document.getElementById('saved-list');
    const userIdEl = document.getElementById('saved-user-id');

    function init() {
        const savedUserId = localStorage.getItem('userId');
        if (savedUserId && userIdEl) userIdEl.value = savedUserId;
        userIdEl?.addEventListener('change', loadSaved);
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadSaved);
        } else {
            loadSaved();
        }
    }

    async function loadSaved() {
        const userId = userIdEl?.value?.trim() || 'default_user';
        localStorage.setItem('userId', userId);

        if (!listEl) return;
        listEl.innerHTML = '<div class="text-slate-400 text-center py-12">Loading...</div>';

        try {
            const data = await API.getSaved(userId);
            if (!data.trips?.length) {
                listEl.innerHTML = `
                    <div class="text-center py-16">
                        <div class="text-5xl mb-4">⭐</div>
                        <p class="text-slate-400">No saved trips yet. Favourite a plan from <a href="/history-page" class="text-primary-400 hover:underline">History</a>.</p>
                    </div>`;
                return;
            }

            listEl.innerHTML = data.trips
                .map(
                    (trip) => `
                <div class="history-item">
                    <div class="flex items-start justify-between gap-4">
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-1">
                                <span class="text-yellow-400">⭐</span>
                                <h3 class="text-white font-semibold">${esc(trip.destination || 'Saved Trip')}</h3>
                                ${UI.confidenceBadge(trip.confidence_score)}
                            </div>
                            <p class="text-slate-400 text-sm">${esc(trip.user_query)}</p>
                            <p class="text-xs text-slate-500 mt-1">${UI.formatDate(trip.created_at)}</p>
                        </div>
                        <div class="flex flex-col gap-2 shrink-0">
                            <button class="btn-secondary px-3 py-1 text-xs view-btn" data-id="${trip.trip_id}">View</button>
                            <a href="${API.exportMarkdownUrl(trip.trip_id)}" class="btn-secondary px-3 py-1 text-xs text-center" download>Download</a>
                            <button class="btn-danger unfav-btn" data-id="${trip.trip_id}">Remove</button>
                        </div>
                    </div>
                </div>
            `
                )
                .join('');

            document.querySelectorAll('.view-btn').forEach((btn) => {
                btn.addEventListener('click', async () => {
                    try {
                        const trip = await API.getTrip(btn.dataset.id);
                        UI.showModal(trip.destination || 'Saved Trip', UI.renderMarkdown(trip.final_response || ''));
                    } catch (e) {
                        UI.toast(e.message, 'error');
                    }
                });
            });

            document.querySelectorAll('.unfav-btn').forEach((btn) => {
                btn.addEventListener('click', async () => {
                    try {
                        await API.toggleFavourite(btn.dataset.id);
                        UI.toast('Removed from favourites', 'success');
                        loadSaved();
                    } catch (e) {
                        UI.toast(e.message, 'error');
                    }
                });
            });
        } catch (err) {
            listEl.innerHTML = `<div class="text-red-400 text-center py-12">${esc(err.message)}</div>`;
        }
    }

    function esc(text) {
        const d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    }

    init();
})();
