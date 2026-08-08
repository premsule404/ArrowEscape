import { api } from '../api/client.js';
import { cloudSave } from '../services/cloud_save.js';
import { playerState } from '../services/player_state.js';

export class DailyRewardsScreen {
    constructor() {
        this.modal = document.getElementById('daily-modal');
        this.btnClose = document.getElementById('btn-close-daily');
        this.btnClaim = document.getElementById('btn-claim-daily');
        this.gridElem = document.getElementById('daily-grid');
        this.streakElem = document.getElementById('daily-streak');
        this.timerElem = document.getElementById('daily-timer');
        this.monthlyProgressElem = document.getElementById('monthly-progress-bar');
        this.monthlyTextElem = document.getElementById('monthly-progress-text');
        this.celebrationElem = document.getElementById('daily-celebration');
        
        this.timerInterval = null;
        this.bindEvents();
    }

    bindEvents() {
        if (this.btnClose) {
            this.btnClose.onclick = () => this.hide();
        }

        if (this.btnClaim) {
            this.btnClaim.onclick = () => this.claimReward();
        }

        // Hotkey 'D' to open Daily Rewards
        window.addEventListener('keydown', (e) => {
            if ((e.key === 'd' || e.key === 'D') && !e.target.matches('input, textarea')) {
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
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    toggle() {
        if (this.modal && this.modal.classList.contains('active')) {
            this.hide();
        } else {
            this.show();
        }
    }

    async fetchAndRender() {
        if (!this.gridElem) return;
        this.gridElem.innerHTML = `<div class="daily-loading">Loading Daily Rewards...</div>`;

        try {
            let status = null;
            if (localStorage.getItem("access_token")) {
                status = await api.getDailyStatus();
            } else {
                // Local fallback daily status logic
                const local = cloudSave.localSave;
                const lastClaim = local.last_daily_claim ? new Date(local.last_daily_claim) : null;
                const now = new Date();
                
                let canClaim = true;
                let streak = local.daily_streak || 0;
                let nextStreak = streak;

                if (lastClaim) {
                    const diffDays = Math.floor((now - lastClaim) / (1000 * 60 * 60 * 24));
                    if (diffDays === 0) {
                        canClaim = false;
                        nextStreak = streak;
                    } else if (diffDays === 1) {
                        canClaim = true;
                        nextStreak = (streak % 7) + 1;
                    } else {
                        // Missed Day handling
                        canClaim = true;
                        nextStreak = 1;
                    }
                } else {
                    nextStreak = 1;
                }

                status = {
                    can_claim: canClaim,
                    current_streak: streak,
                    next_streak_day: nextStreak,
                    total_claims: local.total_daily_claims || 0,
                    seconds_to_next_reset: canClaim ? 0 : 86400 - Math.floor((now % (1000 * 60 * 60 * 24)) / 1000),
                    rewards: [
                        { day: 1, coins: 50, stars: 0, bonus: false, label: "Day 1" },
                        { day: 2, coins: 100, stars: 0, bonus: false, label: "Day 2" },
                        { day: 3, coins: 150, stars: 0, bonus: false, label: "Day 3" },
                        { day: 4, coins: 200, stars: 0, bonus: false, label: "Day 4" },
                        { day: 5, coins: 250, stars: 0, bonus: false, label: "Day 5" },
                        { day: 6, coins: 300, stars: 0, bonus: false, label: "Day 6" },
                        { day: 7, coins: 500, stars: 5, bonus: true, label: "Weekly Bonus!" }
                    ],
                    monthly_bonus: {
                        requirement: 28,
                        coins: 2000,
                        stars: 10,
                        progress: (local.total_daily_claims || 0) % 28,
                        eligible: false
                    }
                };
            }

            // Streak Counter
            if (this.streakElem) {
                this.streakElem.innerText = `🔥 ${status.current_streak} Day Streak!`;
            }

            // Monthly Bonus progress
            const mPct = Math.min(100, Math.round((status.monthly_bonus.progress / status.monthly_bonus.requirement) * 100));
            if (this.monthlyProgressElem) this.monthlyProgressElem.style.width = `${mPct}%`;
            if (this.monthlyTextElem) this.monthlyTextElem.innerText = `${status.monthly_bonus.progress} / ${status.monthly_bonus.requirement} Claims (${mPct}%)`;

            // Grid rendering
            this.gridElem.innerHTML = status.rewards.map(item => {
                const isClaimed = item.day < status.next_streak_day || (!status.can_claim && item.day <= status.current_streak);
                const isActive = status.can_claim && item.day === status.next_streak_day;
                const isLocked = item.day > status.next_streak_day;

                let cardClass = 'daily-card';
                let badgeHtml = '';
                if (isClaimed) {
                    cardClass += ' claimed';
                    badgeHtml = `<span class="daily-badge claimed">✅ Claimed</span>`;
                } else if (isActive) {
                    cardClass += ' active-day';
                    badgeHtml = `<span class="daily-badge active">🎁 Ready!</span>`;
                } else {
                    cardClass += ' locked';
                    badgeHtml = `<span class="daily-badge locked">🔒 Day ${item.day}</span>`;
                }

                return `
                    <div class="${cardClass}">
                        ${badgeHtml}
                        <div class="daily-icon">${item.bonus ? '👑' : '💰'}</div>
                        <div class="daily-day-label">${item.label}</div>
                        <div class="daily-reward-val">+${item.coins} 💰${item.stars > 0 ? ` +${item.stars} ⭐` : ''}</div>
                    </div>
                `;
            }).join('');

            // Claim button state & countdown timer
            if (this.btnClaim) {
                if (status.can_claim) {
                    this.btnClaim.disabled = false;
                    this.btnClaim.innerText = `CLAIM DAY ${status.next_streak_day} REWARD!`;
                    if (this.timerElem) this.timerElem.innerText = "Available Now!";
                } else {
                    this.btnClaim.disabled = true;
                    this.btnClaim.innerText = "CLAIMED TODAY";
                    this.startTimer(status.seconds_to_next_reset);
                }
            }

        } catch (e) {
            this.gridElem.innerHTML = `<div class="daily-error">Failed to load daily rewards. (${e.message})</div>`;
        }
    }

    startTimer(secondsRemaining) {
        if (this.timerInterval) clearInterval(this.timerInterval);
        let rem = secondsRemaining;

        const updateStr = () => {
            if (rem <= 0) {
                if (this.timerElem) this.timerElem.innerText = "Available Now!";
                if (this.btnClaim) {
                    this.btnClaim.disabled = false;
                    this.btnClaim.innerText = "CLAIM REWARD!";
                }
                clearInterval(this.timerInterval);
                return;
            }

            const hrs = Math.floor(rem / 3600);
            const mins = Math.floor((rem % 3600) / 60);
            const secs = rem % 60;
            const formatted = `Next reward in: ${hrs.toString().padStart(2, '0')}h ${mins.toString().padStart(2, '0')}m ${secs.toString().padStart(2, '0')}s`;
            if (this.timerElem) this.timerElem.innerText = formatted;
            rem--;
        };

        updateStr();
        this.timerInterval = setInterval(updateStr, 1000);
    }

    async claimReward() {
        if (!this.btnClaim || this.btnClaim.disabled) return;
        this.btnClaim.disabled = true;
        this.btnClaim.innerText = "Claiming...";

        try {
            let res = null;
            if (localStorage.getItem("access_token")) {
                res = await api.claimDailyReward();
                cloudSave.localSave.total_coins = res.total_coins;
                cloudSave.localSave.total_stars = res.total_stars;
                cloudSave.saveLocalSave();
                playerState.update({
                    total_coins: res.total_coins,
                    total_stars: res.total_stars
                });
            } else {
                // Local claim fallback
                const local = cloudSave.localSave;
                const streak = (local.daily_streak % 7) + 1;
                const coinsEarned = 50 * streak;
                local.daily_streak = streak;
                local.total_daily_claims = (local.total_daily_claims || 0) + 1;
                local.last_daily_claim = new Date().toISOString();
                await cloudSave.recordPurchaseOrReward(coinsEarned);

                res = {
                    streak_day: streak,
                    earned_coins: coinsEarned,
                    earned_stars: 0,
                    weekly_bonus_applied: streak === 7,
                    monthly_bonus_applied: local.total_daily_claims % 28 === 0
                };
            }

            this.triggerCelebrationAnimation(res.earned_coins, res.earned_stars);
            await this.fetchAndRender();

        } catch (e) {
            alert(e.message || "Failed to claim daily reward.");
            this.btnClaim.disabled = false;
        }
    }

    triggerCelebrationAnimation(coins, stars) {
        if (!this.celebrationElem) return;
        
        const popupText = document.getElementById('daily-popup-text');
        if (popupText) {
            popupText.innerText = `+${coins} 💰${stars > 0 ? ` +${stars} ⭐` : ''}`;
        }

        this.celebrationElem.classList.add('active');
        setTimeout(() => {
            this.celebrationElem.classList.remove('active');
        }, 3000);
    }
}
