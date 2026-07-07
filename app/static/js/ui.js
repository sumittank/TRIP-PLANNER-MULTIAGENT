/**
 * Shared UI utilities — toasts, modals, theme, markdown rendering
 */
const UI = {
    init() {
        this.initTheme();
        this.initMobileMenu();
    },

    initTheme() {
        const saved = localStorage.getItem('theme') || 'dark';
        document.documentElement.classList.toggle('light', saved === 'light');
        this.updateThemeIcon(saved);

        const toggle = document.getElementById('theme-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => {
                const isLight = document.documentElement.classList.toggle('light');
                const theme = isLight ? 'light' : 'dark';
                localStorage.setItem('theme', theme);
                this.updateThemeIcon(theme);
            });
        }
    },

    updateThemeIcon(theme) {
        const icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = theme === 'light' ? '☀️' : '🌙';
    },

    initMobileMenu() {
        const btn = document.getElementById('mobile-menu-btn');
        const menu = document.getElementById('mobile-menu');
        if (btn && menu) {
            btn.addEventListener('click', () => menu.classList.toggle('hidden'));
        }
    },

    toast(message, type = 'info', duration = 4000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const el = document.createElement('div');
        el.className = `toast toast-${type}`;
        el.textContent = message;
        container.appendChild(el);

        setTimeout(() => {
            el.style.opacity = '0';
            el.style.transition = 'opacity 0.3s';
            setTimeout(() => el.remove(), 300);
        }, duration);
    },

    showModal(title, content) {
        const overlay = document.getElementById('modal-overlay');
        const modal = document.getElementById('modal-content');
        if (!overlay || !modal) return;

        modal.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-bold text-white">${title}</h2>
                <button id="modal-close" class="text-slate-400 hover:text-white text-2xl leading-none">&times;</button>
            </div>
            <div class="text-slate-300 text-sm leading-relaxed max-h-[60vh] overflow-y-auto">${content}</div>
        `;
        overlay.classList.remove('hidden');

        const close = () => overlay.classList.add('hidden');
        document.getElementById('modal-close')?.addEventListener('click', close);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) close();
        });
    },

    setLoading(btn, loading, text = 'Loading...') {
        if (!btn) return;
        btn.disabled = loading;
        const textEl = btn.querySelector('[id$="-btn-text"]') || btn;
        if (loading) {
            btn.dataset.originalText = textEl.textContent;
            textEl.innerHTML = `<span class="spinner"></span>${text}`;
        } else {
            textEl.textContent = btn.dataset.originalText || 'Submit';
        }
    },

    confidenceBadge(score) {
        const pct = Math.round(score * 100);
        let cls = 'confidence-mid';
        if (score >= 0.75) cls = 'confidence-high';
        else if (score < 0.5) cls = 'confidence-low';
        return `<span class="confidence-badge ${cls}">${pct}% confidence</span>`;
    },

    renderMarkdown(text) {
        if (!text) return '<p class="text-slate-400">No data available.</p>';

        let html = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/^### (.+)$/gm, '<h3>$1</h3>')
            .replace(/^## (.+)$/gm, '<h2>$1</h2>')
            .replace(/^# (.+)$/gm, '<h1>$1</h1>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');

        return `<div class="final-plan-content"><p>${html}</p></div>`;
    },

    formatDate(iso) {
        if (!iso) return '—';
        return new Date(iso).toLocaleString();
    },

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.toast('Copied to clipboard!', 'success');
        } catch {
            this.toast('Failed to copy', 'error');
        }
    },
};

document.addEventListener('DOMContentLoaded', () => UI.init());
