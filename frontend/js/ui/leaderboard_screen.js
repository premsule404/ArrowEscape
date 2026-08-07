import { api } from '../api/client.js';

export class LeaderboardScreen {
    constructor() {
        this.modal = document.getElementById('leaderboard-modal');
        this.listElem = document.getElementById('leaderboard-list');
        this.btnClose = document.getElementById('btn-close-leaderboard');
        
        this.activeCategory = "stars";
        this.activeScope = "global";
        this.activeTimeframe = "all_time";
        
        this.bindEvents();
    }

    bindEvents() {
        if (this.btnClose) {
            this.btnClose.onclick = () => this.hide();
        }

        // Scope Tabs
        document.querySelectorAll('#scope-tabs .tab-btn').forEach(btn => {
            btn.onclick = () => {
                document.querySelectorAll('#scope-tabs .tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.activeScope = btn.getAttribute('data-scope');
                this.fetchAndRender();
            };
        });

        // Timeframe Tabs
        document.querySelectorAll('#timeframe-tabs .tab-btn').forEach(btn => {
            btn.onclick = () => {
                document.querySelectorAll('#timeframe-tabs .tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.activeTimeframe = btn.getAttribute('data-timeframe');
                this.fetchAndRender();
            };
        });

        // Category Tabs
        document.querySelectorAll('#category-tabs .tab-btn').forEach(btn => {
            btn.onclick = () => {
                document.querySelectorAll('#category-tabs .tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.activeCategory = btn.getAttribute('data-category');
                this.fetchAndRender();
            };
        });

        // Hotkey 'L' to open Leaderboard
        window.addEventListener('keydown', (e) => {
            if ((e.key === 'l' || e.key === 'L') && !e.target.matches('input, textarea')) {
                this.toggle();
            }
        });
    }

    async show() {
        if (this.modal) this.modal.classList.add('active');
        await this.fetchAndRender();
    }

    hide() {
        if (this.modal) this.modal.classList.remove('active');
    }

    toggle() {
        if (this.modal && this.modal.classList.contains('active')) {
            this.hide();
        } else {
            this.show();
        }
    }

    getRankBadge(rank) {
        if (rank === 1) return '🥇 1';
        if (rank === 2) return '🥈 2';
        if (rank === 3) return '🥉 3';
        return `#${rank}`;
    }

    async fetchAndRender() {
        if (!this.listElem) return;
        this.listElem.innerHTML = `<tr><td colspan="7" class="lb-loading">Loading Leaderboard...</td></tr>`;

        try {
            const data = await api.getLeaderboard(this.activeCategory, this.activeScope, this.activeTimeframe);
            if (!data || data.length === 0) {
                this.listElem.innerHTML = `<tr><td colspan="7" class="lb-empty">No players found in this category.</td></tr>`;
                return;
            }

            this.listElem.innerHTML = data.map(item => {
                const isYou = item.is_current_user;
                const rowClass = isYou ? 'lb-row-you' : '';
                const rankDisplay = this.getRankBadge(item.rank);
                const avatar = item.avatar || '🎯';
                const displayName = item.display_name || item.username || 'Player';
                const stars = item.total_stars || 0;
                const coins = item.total_coins || 0;
                const levels = item.completed_levels || 0;
                const pct = `${item.completion_pct || 0}%`;
                const bestTime = item.fastest_time > 0 ? `${item.fastest_time}s` : '--';

                return `
                    <tr class="lb-row ${rowClass}">
                        <td class="lb-rank">${rankDisplay}</td>
                        <td class="lb-player">
                            <span class="lb-avatar">${avatar}</span>
                            <span class="lb-name">${this.escapeHtml(displayName)}</span>
                            ${isYou ? '<span class="lb-you-badge">YOU</span>' : ''}
                        </td>
                        <td class="lb-val">⭐ ${stars}</td>
                        <td class="lb-val">💰 ${coins}</td>
                        <td class="lb-val">🗺️ ${levels}</td>
                        <td class="lb-val">${pct}</td>
                        <td class="lb-val">${bestTime}</td>
                    </tr>
                `;
            }).join('');
        } catch (e) {
            this.listElem.innerHTML = `<tr><td colspan="7" class="lb-error">Failed to load leaderboard. (${this.escapeHtml(e.message)})</td></tr>`;
        }
    }

    escapeHtml(str) {
        return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
}
