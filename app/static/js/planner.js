/**
 * Trip Planner page logic
 */
(function () {
    const queryEl = document.getElementById('trip-query');
    const userIdEl = document.getElementById('user-id');
    const planBtn = document.getElementById('plan-btn');
    const progressSection = document.getElementById('progress-section');
    const resultsSection = document.getElementById('results-section');
    const progressBar = document.getElementById('progress-bar');

    let currentTrip = null;

    const AGENT_STEPS = {
        supervisor: { el: '[data-agent="supervisor"]', progress: 20 },
        parallel: { el: '[data-agent="parallel"]', progress: 50 },
        critic: { el: '[data-agent="critic"]', progress: 75 },
        formatter: { el: '[data-agent="formatter"]', progress: 100 },
    };

    function init() {
        const params = new URLSearchParams(window.location.search);
        const dest = params.get('dest');
        if (dest && queryEl) {
            queryEl.value = `Plan a complete trip to ${dest} with flights, hotels, and sightseeing`;
        }

        const savedUserId = localStorage.getItem('userId');
        if (savedUserId && userIdEl) userIdEl.value = savedUserId;

        document.querySelectorAll('.suggestion-chip').forEach((chip) => {
            chip.addEventListener('click', () => {
                if (queryEl) queryEl.value = chip.dataset.query;
            });
        });

        if (userIdEl) {
            userIdEl.addEventListener('change', () => {
                localStorage.setItem('userId', userIdEl.value);
                API.userId = userIdEl.value;
            });
        }

        if (planBtn) planBtn.addEventListener('click', generatePlan);
    }

    function setAgentStatus(agent, status) {
        const step = document.querySelector(AGENT_STEPS[agent]?.el);
        if (!step) return;
        step.classList.remove('active', 'done', 'error');
        const statusEl = step.querySelector('.agent-status');
        if (status === 'running') {
            step.classList.add('active');
            if (statusEl) statusEl.textContent = 'Running...';
        } else if (status === 'done') {
            step.classList.add('done');
            if (statusEl) statusEl.textContent = 'Complete';
        } else if (status === 'error') {
            step.classList.add('error');
            if (statusEl) statusEl.textContent = 'Error';
        } else {
            if (statusEl) statusEl.textContent = 'Waiting';
        }
    }

    function resetPipeline() {
        Object.keys(AGENT_STEPS).forEach((a) => setAgentStatus(a, 'waiting'));
        if (progressBar) progressBar.style.width = '0%';
    }

    function animatePipeline() {
        const steps = ['supervisor', 'parallel', 'critic', 'formatter'];
        let i = 0;

        return new Promise((resolve) => {
            function next() {
                if (i > 0) setAgentStatus(steps[i - 1], 'done');
                if (i < steps.length) {
                    setAgentStatus(steps[i], 'running');
                    if (progressBar) progressBar.style.width = `${AGENT_STEPS[steps[i]].progress}%`;
                    i++;
                    setTimeout(next, 800);
                } else {
                    resolve();
                }
            }
            next();
        });
    }

    function renderMetrics(data) {
        const row = document.getElementById('metrics-row');
        if (!row) return;
        row.innerHTML = `
            <div class="metric-box">
                <div class="metric-val">${(data.agents_run || []).length}</div>
                <div class="metric-lbl">Agents Run</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">${data.llm_calls || 0}</div>
                <div class="metric-lbl">LLM Calls</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">${Math.round((data.confidence_score || 0) * 100)}%</div>
                <div class="metric-lbl">Confidence</div>
            </div>
        `;
    }

    function renderTripCards(data) {
        const container = document.getElementById('trip-cards');
        if (!container) return;

        const sections = [
            { key: 'flight_results', icon: '✈️', title: 'Flights' },
            { key: 'hotel_results', icon: '🏨', title: 'Hotels' },
            { key: 'budget_results', icon: '💰', title: 'Budget Breakdown' },
            { key: 'attraction_results', icon: '🏛️', title: 'Attractions' },
            { key: 'travel_tips_results', icon: '💡', title: 'Travel Tips' },
        ];

        container.innerHTML = sections
            .filter((s) => data[s.key])
            .map(
                (s) => `
            <div class="trip-card">
                <h3>${s.icon} ${s.title}</h3>
                <div class="card-body">${escapeHtml(data[s.key])}</div>
            </div>
        `
            )
            .join('');

        if (data.packing_checklist) {
            container.innerHTML += `
                <div class="trip-card">
                    <h3>🎒 Packing Checklist</h3>
                    <div class="card-body">${escapeHtml(data.packing_checklist)}</div>
                </div>`;
        }
        if (data.travel_checklist) {
            container.innerHTML += `
                <div class="trip-card">
                    <h3>✅ Travel Checklist</h3>
                    <div class="card-body">${escapeHtml(data.travel_checklist)}</div>
                </div>`;
        }
    }

    function renderFinalPlan(data) {
        const el = document.getElementById('final-plan');
        if (!el) return;
        el.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-bold text-white">Final Travel Plan</h2>
                ${UI.confidenceBadge(data.confidence_score || 0)}
            </div>
            ${UI.renderMarkdown(data.final_response || data.itinerary || '')}
        `;
    }

    function renderActions(data) {
        const el = document.getElementById('action-buttons');
        if (!el || !data.trip_id) return;

        el.innerHTML = `
            <a href="${API.exportMarkdownUrl(data.trip_id)}" class="btn-secondary px-4 py-2 text-sm" download>⬇️ Download Markdown</a>
            <a href="${API.exportJsonUrl(data.trip_id)}" class="btn-secondary px-4 py-2 text-sm" download>⬇️ Export JSON</a>
            <button id="copy-plan-btn" class="btn-secondary px-4 py-2 text-sm">📋 Copy to Clipboard</button>
            <button id="fav-plan-btn" class="btn-secondary px-4 py-2 text-sm">⭐ Save to Favourites</button>
            <button id="regen-plan-btn" class="btn-secondary px-4 py-2 text-sm">🔄 Regenerate</button>
        `;

        document.getElementById('copy-plan-btn')?.addEventListener('click', () => {
            UI.copyToClipboard(data.final_response || '');
        });

        document.getElementById('fav-plan-btn')?.addEventListener('click', async () => {
            try {
                await API.toggleFavourite(data.trip_id);
                UI.toast('Added to favourites!', 'success');
            } catch (e) {
                UI.toast(e.message, 'error');
            }
        });

        document.getElementById('regen-plan-btn')?.addEventListener('click', generatePlan);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async function generatePlan() {
        const query = queryEl?.value?.trim();
        const userId = userIdEl?.value?.trim() || 'default_user';

        if (!query) {
            UI.toast('Please describe your trip first.', 'error');
            return;
        }

        localStorage.setItem('userId', userId);
        API.userId = userId;

        resetPipeline();
        progressSection?.classList.remove('hidden');
        resultsSection?.classList.add('hidden');
        UI.setLoading(planBtn, true, 'Planning...');

        const pipelinePromise = animatePipeline();

        try {
            const data = await API.planTrip(query, userId);
            await pipelinePromise;

            setAgentStatus('formatter', 'done');
            if (progressBar) progressBar.style.width = '100%';

            currentTrip = data;
            resultsSection?.classList.remove('hidden');
            renderMetrics(data);
            renderTripCards(data);
            renderFinalPlan(data);
            renderActions(data);

            UI.toast('Travel plan generated successfully!', 'success');
        } catch (err) {
            setAgentStatus('parallel', 'error');
            UI.toast(err.message || 'Failed to generate plan', 'error');
        } finally {
            UI.setLoading(planBtn, false);
            const textEl = document.getElementById('plan-btn-text');
            if (textEl) textEl.textContent = 'Generate Plan';
        }
    }

    document.addEventListener('DOMContentLoaded', init);
})();
