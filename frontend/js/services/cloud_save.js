import { api } from '../api/client.js';
import { playerState } from './player_state.js';

export class CloudSaveManager {
    constructor() {
        this.STORAGE_KEY = "arrow_escape_local_save_v1";
        this.localSave = this.loadLocalSave();
    }

    loadLocalSave() {
        try {
            const raw = localStorage.getItem(this.STORAGE_KEY);
            if (raw) return JSON.parse(raw);
        } catch (e) {}
        
        return {
            current_level: 1,
            completed_levels: {},
            total_coins: 0,
            total_stars: 0,
            boosters: { hints: 3 },
            hearts: 3,
            settings: { theme: 'default', sound_enabled: true },
            last_synced_at: null
        };
    }

    saveLocalSave() {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.localSave));
        } catch (e) {}
    }

    getLocalLevelsSyncPayload() {
        const levelsList = [];
        for (const [lvlId, data] of Object.entries(this.localSave.completed_levels || {})) {
            levelsList.push({
                level_id: Number(lvlId),
                stars: Number(data.stars) || 0,
                moves: Number(data.best_moves) || 0,
                time: Number(data.best_time) || 0,
                base_coins: Number(data.base_coins) || 100,
                completed: Boolean(data.completed)
            });
        }
        return levelsList;
    }

    async saveLevelCompletion(levelNum, stars, moves, time, coinsEarned) {
        if (!this.localSave.completed_levels) {
            this.localSave.completed_levels = {};
        }

        if (!this.localSave.completed_levels[levelNum]) {
            this.localSave.completed_levels[levelNum] = {
                stars: 0,
                best_moves: 9999,
                best_time: 9999,
                base_coins: coinsEarned,
                completed: true
            };
        }

        const record = this.localSave.completed_levels[levelNum];
        const oldStars = record.stars || 0;
        record.stars = Math.max(oldStars, stars);
        record.best_moves = Math.min(record.best_moves || 9999, moves);
        record.best_time = (record.best_time === 0 || time < record.best_time) ? time : record.best_time;
        record.completed = true;

        const starGain = Math.max(0, record.stars - oldStars);
        this.localSave.total_stars = (this.localSave.total_stars || 0) + starGain;
        this.localSave.total_coins = (this.localSave.total_coins || 0) + coinsEarned;
        this.localSave.current_level = Math.max(this.localSave.current_level || 1, levelNum + 1);

        this.saveLocalSave();

        // Immediately notify centralized playerState subscribers!
        playerState.update({
            total_coins: this.localSave.total_coins,
            total_stars: this.localSave.total_stars,
            current_level: this.localSave.current_level,
            completed_levels: this.localSave.completed_levels
        });

        await this.syncToCloud();
    }

    async recordPurchaseOrReward(coinsChange, boosterType = null, boosterAmount = 0) {
        this.localSave.total_coins = Math.max(0, (this.localSave.total_coins || 0) + coinsChange);
        if (!this.localSave.boosters) this.localSave.boosters = {};
        if (boosterType) {
            this.localSave.boosters[boosterType] = (this.localSave.boosters[boosterType] || 0) + boosterAmount;
        }
        this.saveLocalSave();

        playerState.update({
            total_coins: this.localSave.total_coins,
            boosters: this.localSave.boosters
        });

        await this.syncToCloud();
    }

    async updateSettings(settingsData) {
        if (!this.localSave.settings) this.localSave.settings = {};
        Object.assign(this.localSave.settings, settingsData);
        this.saveLocalSave();

        playerState.update({
            settings: this.localSave.settings
        });

        if (localStorage.getItem("access_token")) {
            try {
                await api.updateSettings(settingsData);
            } catch (e) {}
        }
    }

    async syncToCloud() {
        if (!localStorage.getItem("access_token")) {
            playerState.syncFromLocalSave();
            return this.localSave;
        }

        try {
            const syncPayload = {
                levels: this.getLocalLevelsSyncPayload(),
                total_coins: this.localSave.total_coins,
                total_stars: this.localSave.total_stars,
                current_level: this.localSave.current_level,
                theme: this.localSave.settings?.theme || 'default'
            };

            const cloudRes = await api.syncProgress(syncPayload.levels, syncPayload.current_level);
            if (cloudRes && cloudRes.success) {
                this.localSave.total_coins = cloudRes.total_coins;
                this.localSave.total_stars = cloudRes.total_stars;
                this.localSave.current_level = cloudRes.highest_unlocked_level;
                
                if (cloudRes.levels) {
                    cloudRes.levels.forEach(lvl => {
                        this.localSave.completed_levels[lvl.level_num] = {
                            stars: lvl.stars,
                            best_moves: lvl.best_moves,
                            best_time: lvl.best_time,
                            base_coins: lvl.coins_claimed,
                            completed: lvl.completed
                        };
                    });
                }
                this.localSave.last_synced_at = new Date().toISOString();
                this.saveLocalSave();

                playerState.update({
                    total_coins: this.localSave.total_coins,
                    total_stars: this.localSave.total_stars,
                    current_level: this.localSave.current_level,
                    completed_levels: this.localSave.completed_levels
                });

                if (window.notificationSystem) {
                    window.notificationSystem.notify("Cloud Sync Complete", "Your game progress is backed up.", "cloud", "☁️");
                }
            }
        } catch (e) {
            console.warn("Cloud sync deferred:", e.message);
            playerState.syncFromLocalSave();
            if (window.notificationSystem) {
                window.notificationSystem.notify("Sync Error", e.message || "Failed to sync cloud save.", "error", "⚠️");
            }
        }
        return this.localSave;
    }

    async downloadCloudProgress() {
        if (!localStorage.getItem("access_token")) {
            playerState.syncFromLocalSave();
            return this.localSave;
        }

        try {
            const progress = await api.getProgress();
            if (progress) {
                this.localSave.total_coins = Math.max(this.localSave.total_coins || 0, progress.total_coins || 0);
                this.localSave.total_stars = Math.max(this.localSave.total_stars || 0, progress.total_stars || 0);
                this.localSave.current_level = Math.max(this.localSave.current_level || 1, progress.current_level || 1);

                if (progress.levels) {
                    if (!this.localSave.completed_levels) this.localSave.completed_levels = {};
                    progress.levels.forEach(lvl => {
                        const existing = this.localSave.completed_levels[lvl.level_num] || {};
                        this.localSave.completed_levels[lvl.level_num] = {
                            stars: Math.max(existing.stars || 0, lvl.stars || 0),
                            best_moves: Math.min(existing.best_moves || 9999, lvl.best_moves || 9999),
                            best_time: (existing.best_time === 0 || lvl.best_time < existing.best_time) ? lvl.best_time : existing.best_time,
                            base_coins: Math.max(existing.base_coins || 0, lvl.coins_claimed || 0),
                            completed: existing.completed || lvl.completed
                        };
                    });
                }
                this.saveLocalSave();
                
                playerState.update({
                    total_coins: this.localSave.total_coins,
                    total_stars: this.localSave.total_stars,
                    current_level: this.localSave.current_level,
                    completed_levels: this.localSave.completed_levels
                });

                await this.syncToCloud();
            }
        } catch (e) {
            console.warn("Failed to download cloud progress:", e.message);
            playerState.syncFromLocalSave();
        }
        return this.localSave;
    }
}

export const cloudSave = new CloudSaveManager();
