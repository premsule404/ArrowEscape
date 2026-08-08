export class PlayerStateManager {
    constructor() {
        this.listeners = new Set();
        this.state = this.buildInitialState();
    }

    buildInitialState() {
        let local = {};
        try {
            const raw = localStorage.getItem("arrow_escape_local_save_v1");
            if (raw) local = JSON.parse(raw);
        } catch (e) {}

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

        // Keep local storage in 100% sync
        try {
            const raw = localStorage.getItem("arrow_escape_local_save_v1");
            const local = raw ? JSON.parse(raw) : {};
            if (partialState.total_coins !== undefined) local.total_coins = this.state.total_coins;
            if (partialState.total_stars !== undefined) local.total_stars = this.state.total_stars;
            if (partialState.current_level !== undefined) local.current_level = this.state.current_level;
            if (partialState.completed_levels !== undefined) local.completed_levels = this.state.completed_levels;
            localStorage.setItem("arrow_escape_local_save_v1", JSON.stringify(local));
        } catch (e) {}

        this.notify();
    }

    syncFromLocalSave() {
        let local = {};
        try {
            const raw = localStorage.getItem("arrow_escape_local_save_v1");
            if (raw) local = JSON.parse(raw);
        } catch (e) {}

        this.state.total_coins = local.total_coins || 0;
        this.state.total_stars = local.total_stars || 0;
        this.state.current_level = local.current_level || 1;
        this.state.completed_levels = local.completed_levels || {};
        this.state.completed_count = Object.keys(this.state.completed_levels).length;
        this.notify();
    }

    resetToGuest() {
        localStorage.removeItem("username");
        localStorage.removeItem("avatar");
        localStorage.removeItem("email");
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        this.state = {
            username: "Guest Player",
            avatar: "🎯",
            email: "N/A",
            is_guest: true,
            total_coins: 0,
            total_stars: 0,
            current_level: 1,
            highest_level: 1,
            completed_levels: {},
            completed_count: 0,
            boosters: { hints: 3 },
            settings: { theme: 'default', sound_effects: true },
            unlocked_items: [],
            equipped_items: {},
            daily_streak: 1,
            is_online: true,
            last_synced_at: null
        };
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
            this.state.total_coins = apiUser.total_coins ?? 0;
            this.state.total_stars = apiUser.total_stars ?? 0;
            this.state.current_level = apiUser.highest_level ?? apiUser.current_level ?? 1;
            this.state.highest_level = apiUser.highest_level ?? apiUser.current_level ?? 1;
            if (apiUser.unlocked_items) this.state.unlocked_items = apiUser.unlocked_items;
            if (apiUser.equipped_items) this.state.equipped_items = apiUser.equipped_items;
        }
        
        // Save back to local storage
        try {
            const raw = localStorage.getItem("arrow_escape_local_save_v1");
            const local = raw ? JSON.parse(raw) : {};
            local.total_coins = this.state.total_coins;
            local.total_stars = this.state.total_stars;
            local.current_level = this.state.current_level;
            localStorage.setItem("arrow_escape_local_save_v1", JSON.stringify(local));
        } catch (e) {}

        this.notify();
    }
}

export const playerState = new PlayerStateManager();
