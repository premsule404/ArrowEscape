import { cloudSave } from './cloud_save.js';

export class PlayerStateManager {
    constructor() {
        this.listeners = new Set();
        this.state = this.buildInitialState();
    }

    buildInitialState() {
        const local = cloudSave.localSave || {};
        const completedCount = Object.keys(local.completed_levels || {}).length;
        return {
            username: localStorage.getItem("username") || "Player",
            avatar: localStorage.getItem("avatar") || "🎯",
            email: localStorage.getItem("email") || "N/A",
            is_guest: !localStorage.getItem("access_token"),
            total_coins: local.total_coins || 0,
            total_stars: local.total_stars || 0,
            current_level: local.current_level || 1,
            highest_level: local.current_level || 1,
            completed_levels: local.completed_levels || {},
            completed_count: completedCount,
            boosters: local.boosters || { hints: 3 },
            settings: local.settings || { theme: 'default', sound_effects: true },
            unlocked_items: [],
            equipped_items: {},
            daily_streak: 1,
            is_online: true,
            last_synced_at: local.last_synced_at || null
        };
    }

    subscribe(listener) {
        this.listeners.add(listener);
        try {
            listener(this.state);
        } catch (e) {
            console.warn("PlayerState initial subscriber error:", e);
        }
        return () => this.listeners.delete(listener);
    }

    notify() {
        for (const listener of this.listeners) {
            try {
                listener(this.state);
            } catch (e) {
                console.warn("PlayerState subscriber notification error:", e);
            }
        }
    }

    update(partialState) {
        Object.assign(this.state, partialState);
        
        if (this.state.completed_levels) {
            this.state.completed_count = Object.keys(this.state.completed_levels).length;
        }

        // Keep cloudSave.localSave in 100% sync
        if (partialState.total_coins !== undefined) cloudSave.localSave.total_coins = this.state.total_coins;
        if (partialState.total_stars !== undefined) cloudSave.localSave.total_stars = this.state.total_stars;
        if (partialState.current_level !== undefined) cloudSave.localSave.current_level = this.state.current_level;
        if (partialState.completed_levels !== undefined) cloudSave.localSave.completed_levels = this.state.completed_levels;
        cloudSave.saveLocalSave();

        this.notify();
    }

    syncFromLocalSave() {
        const local = cloudSave.localSave;
        this.state.total_coins = local.total_coins || 0;
        this.state.total_stars = local.total_stars || 0;
        this.state.current_level = local.current_level || 1;
        this.state.completed_levels = local.completed_levels || {};
        this.state.completed_count = Object.keys(this.state.completed_levels).length;
        this.notify();
    }

    async syncFromCloudUser(apiUser) {
        if (apiUser) {
            if (apiUser.username) {
                this.state.username = apiUser.username;
                localStorage.setItem("username", apiUser.username);
            }
            if (apiUser.avatar) {
                this.state.avatar = apiUser.avatar;
                localStorage.setItem("avatar", apiUser.avatar);
            }
            if (apiUser.email) {
                this.state.email = apiUser.email;
                localStorage.setItem("email", apiUser.email);
            }
            this.state.is_guest = Boolean(apiUser.is_guest);
            this.state.total_coins = apiUser.total_coins ?? this.state.total_coins;
            this.state.total_stars = apiUser.total_stars ?? this.state.total_stars;
            this.state.current_level = Math.max(this.state.current_level, apiUser.highest_level ?? apiUser.current_level ?? 1);
            this.state.highest_level = Math.max(this.state.highest_level, apiUser.highest_level ?? 1);
            if (apiUser.unlocked_items) this.state.unlocked_items = apiUser.unlocked_items;
            if (apiUser.equipped_items) this.state.equipped_items = apiUser.equipped_items;
        }
        
        // Save back to local storage
        cloudSave.localSave.total_coins = this.state.total_coins;
        cloudSave.localSave.total_stars = this.state.total_stars;
        cloudSave.localSave.current_level = this.state.current_level;
        cloudSave.saveLocalSave();

        this.notify();
    }
}

export const playerState = new PlayerStateManager();
