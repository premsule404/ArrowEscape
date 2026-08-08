import { api } from '../api/client.js';
import { cloudSave } from '../services/cloud_save.js';
import { playerState } from '../services/player_state.js';

export class AchievementsScreen {
    constructor() {
        this.modal = document.getElementById('achievements-modal');
        this.listElem = document.getElementById('achievements-list');
        this.btnClose = document.getElementById('btn-close-achievements');
        this.toastElem = document.getElementById('achievement-toast');
        
        this.unlockedIds = new Set();
        this.bindEvents();

        playerState.subscribe((state) => {
            if (this.modal && this.modal.classList.contains('active')) {
                this.fetchAndRender();
            }
        });
    }

    bindEvents() {
        if (this.btnClose) {
            this.btnClose.onclick = () => this.hide();
        }

        // Hotkey 'A' to open Achievements
        window.addEventListener('keydown', (e) => {
            if ((e.key === 'a' || e.key === 'A') && !e.target.matches('input, textarea')) {
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

    showToast(title, icon = "🏆", description = "") {
        if (!this.toastElem) return;
        const toastIcon = document.getElementById('toast-icon');
        const toastTitle = document.getElementById('toast-title');
        const toastDesc = document.getElementById('toast-desc');

        if (toastIcon) toastIcon.innerText = icon;
        if (toastTitle) toastTitle.innerText = title;
        if (toastDesc) toastDesc.innerText = description || "Achievement Unlocked!";

        this.toastElem.classList.add('show');
        setTimeout(() => {
            this.toastElem.classList.remove('show');
        }, 4000);
    }

    async checkAndTriggerUnlocks(completedLevelNum, starsEarned, movesCount, timeElapsed, heartsLost = false) {
        const local = cloudSave.localSave;
        const completedCount = Object.keys(local.completed_levels || {}).length;
        const totalStars = local.total_stars || 0;
        const totalCoins = local.total_coins || 0;

        const checkList = [
            { id: "first_win", title: "First Win", icon: "🏆", desc: "Complete Level 1", val: completedCount >= 1 },
            { id: "level_10", title: "Complete Level 10", icon: "🏅", desc: "Reach Level 10", val: (local.current_level || 1) >= 10 },
            { id: "level_25", title: "Complete Level 25", icon: "🌟", desc: "Reach Level 25", val: (local.current_level || 1) >= 25 },
            { id: "level_50", title: "Complete Level 50", icon: "👑", desc: "Master Level 50", val: (local.current_level || 1) >= 50 },
            { id: "coins_100", title: "Earn 100 Coins", icon: "💰", desc: "Collect 100 coins", val: totalCoins >= 100 },
            { id: "coins_1000", title: "Earn 1000 Coins", icon: "💎", desc: "Collect 1000 coins", val: totalCoins >= 1000 },
            { id: "three_star_all", title: "3 Star Master", icon: "⭐", desc: "Earn 3 stars on 10 levels", val: Object.values(local.completed_levels || {}).filter(l => l.stars === 3).length >= 10 },
            { id: "no_heart_loss", title: "Finish Without Losing Hearts", icon: "❤️", desc: "Flawless Escape!", val: !heartsLost },
            { id: "speed_runner", title: "Speed Runner", icon: "⚡", desc: "Clear level under 10s", val: timeElapsed > 0 && timeElapsed <= 10.0 },
            { id: "collector", title: "Star Collector", icon: "🎒", desc: "Earn 30 total stars", val: totalStars >= 30 }
        ];

        for (const item of checkList) {
            if (item.val && !this.unlockedIds.has(item.id)) {
                this.unlockedIds.add(item.id);
                this.showToast(item.title, item.icon, item.desc);
            }
        }
    }

    getLocalFallbackData() {
        const local = cloudSave.localSave;
        const completedCount = Object.keys(local.completed_levels || {}).length;
        const totalStars = local.total_stars || 0;
        const totalCoins = local.total_coins || 0;
        const threeStarCount = Object.values(local.completed_levels || {}).filter(l => l.stars === 3).length;

        return [
            { id: "first_win", title: "First Win", description: "Complete Level 1", icon: "🏆", target: 1, progress: Math.min(1, completedCount), reward_coins: 50, unlocked: completedCount >= 1, claimed: false },
            { id: "level_10", title: "Complete Level 10", description: "Reach and clear Level 10", icon: "🏅", target: 10, progress: Math.min(10, local.current_level || 1), reward_coins: 100, unlocked: (local.current_level || 1) >= 10, claimed: false },
            { id: "level_25", title: "Complete Level 25", description: "Reach and clear Level 25", icon: "🌟", target: 25, progress: Math.min(25, local.current_level || 1), reward_coins: 250, unlocked: (local.current_level || 1) >= 25, claimed: false },
            { id: "level_50", title: "Complete Level 50", description: "Master Level 50", icon: "👑", target: 50, progress: Math.min(50, local.current_level || 1), reward_coins: 500, unlocked: (local.current_level || 1) >= 50, claimed: false },
            { id: "coins_100", title: "Earn 100 Coins", description: "Collect 100 coins", icon: "💰", target: 100, progress: Math.min(100, totalCoins), reward_coins: 50, unlocked: totalCoins >= 100, claimed: false },
            { id: "coins_1000", title: "Earn 1000 Coins", description: "Collect 1000 coins", icon: "💎", target: 1000, progress: Math.min(1000, totalCoins), reward_coins: 200, unlocked: totalCoins >= 1000, claimed: false },
            { id: "three_star_all", title: "3 Star Master", description: "Earn 3 stars on 10 levels", icon: "⭐", target: 10, progress: Math.min(10, threeStarCount), reward_coins: 300, unlocked: threeStarCount >= 10, claimed: false },
            { id: "no_heart_loss", title: "Finish Without Losing Hearts", description: "Clear a level with full hearts intact", icon: "❤️", target: 1, progress: completedCount >= 1 ? 1 : 0, reward_coins: 100, unlocked: completedCount >= 1, claimed: false },
            { id: "speed_runner", title: "Speed Runner", description: "Complete a level in under 10s", icon: "⚡", target: 1, progress: 0, reward_coins: 150, unlocked: false, claimed: false },
            { id: "collector", title: "Star Collector", description: "Earn 30 total stars", icon: "🎒", target: 30, progress: Math.min(30, totalStars), reward_coins: 200, unlocked: totalStars >= 30, claimed: false }
        ];
    }

    async fetchAndRender() {
        if (!this.listElem) return;
        this.listElem.innerHTML = `<div class="ach-loading">Loading Achievements...</div>`;

        let data = [];
        try {
            if (localStorage.getItem("access_token")) {
                data = await api.getAchievements();
            } else {
                data = this.getLocalFallbackData();
            }
        } catch (e) {
            console.warn("Backend achievements error, falling back to local:", e.message);
            data = this.getLocalFallbackData();
        }

        const unlockedCount = data.filter(d => d.unlocked).length;
        const counterElem = document.getElementById('achievements-counter');
        if (counterElem) counterElem.innerText = `${unlockedCount} / ${data.length} Unlocked`;

        this.listElem.innerHTML = data.map(item => {
            const pct = Math.min(100, Math.round((item.progress / item.target) * 100));
            let actionBtnHtml = `<button class="ach-btn locked" disabled>🔒 Locked</button>`;
            if (item.claimed) {
                actionBtnHtml = `<span class="ach-claimed-badge">✅ Claimed</span>`;
            } else if (item.unlocked) {
                actionBtnHtml = `<button class="primary-btn success-btn claim-ach-btn" data-id="${item.id}">Claim +${item.reward_coins} 💰</button>`;
            }

            return `
                <div class="ach-card ${item.unlocked ? 'unlocked' : 'locked'}">
                    <div class="ach-icon">${item.icon}</div>
                    <div class="ach-details">
                        <div class="ach-header-row">
                            <h4 class="ach-title">${item.title}</h4>
                            <span class="ach-reward">+${item.reward_coins} 💰</span>
                        </div>
                        <p class="ach-desc">${item.description}</p>
                        <div class="ach-progress-container">
                            <div class="ach-progress-bar" style="width: ${pct}%;"></div>
                            <span class="ach-progress-text">${item.progress} / ${item.target} (${pct}%)</span>
                        </div>
                    </div>
                    <div class="ach-action">
                        ${actionBtnHtml}
                    </div>
                </div>
            `;
        }).join('');

        // Bind Claim Buttons
        this.listElem.querySelectorAll('.claim-ach-btn').forEach(btn => {
            btn.onclick = async () => {
                const achId = btn.getAttribute('data-id');
                try {
                    if (localStorage.getItem("access_token")) {
                        const res = await api.claimAchievement(achId);
                        cloudSave.localSave.total_coins = res.total_coins;
                        cloudSave.saveLocalSave();
                        playerState.update({ total_coins: res.total_coins });
                    } else {
                        const item = data.find(d => d.id === achId);
                        if (item) {
                            item.claimed = true;
                            await cloudSave.recordPurchaseOrReward(item.reward_coins);
                        }
                    }
                    await this.fetchAndRender();
                    alert("Reward claimed successfully!");
                } catch (e) {
                    alert(e.message || "Failed to claim reward.");
                }
            };
        });
    }
}
