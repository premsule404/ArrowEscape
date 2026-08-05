export class ApiClient {
    constructor(baseURL = window.location.origin.includes('localhost') ? "http://localhost:8000/api/v1" : "/api/v1") {
        this.baseURL = baseURL;
    }

    getHeaders() {
        const token = localStorage.getItem("access_token");
        return {
            "Content-Type": "application/json",
            ...(token ? { "Authorization": `Bearer ${token}` } : {})
        };
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...this.getHeaders(),
                    ...options.headers
                }
            });
            
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                const msg = err.error?.message || err.detail || `API Error: ${response.statusText}`;
                throw new Error(msg);
            }
            
            return response.json();
        } catch (error) {
            console.error(`[ApiClient] Failed to fetch ${endpoint}:`, error);
            throw error;
        }
    }

    // --- Authentication ---
    async login(username, password) {
        const res = await this.request("/auth/login", {
            method: "POST",
            body: JSON.stringify({ username, password })
        });
        this.saveTokens(res);
        return res;
    }

    async register(username, password, email = null) {
        const res = await this.request("/auth/register", {
            method: "POST",
            body: JSON.stringify({ username, password, email })
        });
        this.saveTokens(res);
        return res;
    }

    async guestLogin(displayName = null) {
        const res = await this.request("/auth/guest", {
            method: "POST",
            body: JSON.stringify({ display_name: displayName })
        });
        this.saveTokens(res);
        return res;
    }

    async upgradeGuest(username, password, email = null) {
        const res = await this.request("/auth/upgrade-guest", {
            method: "POST",
            body: JSON.stringify({ username, password, email })
        });
        this.saveTokens(res);
        return res;
    }

    saveTokens(res) {
        if (res.access_token) localStorage.setItem("access_token", res.access_token);
        if (res.refresh_token) localStorage.setItem("refresh_token", res.refresh_token);
    }

    async getMe() {
        return this.request("/auth/me");
    }
    
    async logout() {
        const refToken = localStorage.getItem("refresh_token");
        if (refToken) {
            try {
                await this.request("/auth/logout", {
                    method: "POST",
                    body: JSON.stringify({ refresh_token: refToken })
                });
            } catch (e) {}
        }
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
    }

    // --- Cloud Save & Sync ---
    async syncProgress(levels = [], currentLevel = null) {
        return this.request("/cloud/sync", {
            method: "POST",
            body: JSON.stringify({ levels, current_level: currentLevel })
        });
    }

    async getProgress() {
        return this.request("/progress");
    }

    // --- Leaderboard & Profile ---
    async getLeaderboard(category = "stars") {
        return this.request(`/leaderboard?category=${category}`);
    }

    async updateSettings(settingsData) {
        return this.request("/settings", {
            method: "PATCH",
            body: JSON.stringify(settingsData)
        });
    }

    // --- Admin ---
    async getAdminPlayers() {
        return this.request("/admin/players");
    }

    async setPlayerStatus(userId, status) {
        return this.request(`/admin/players/${userId}/status`, {
            method: "POST",
            body: JSON.stringify({ status })
        });
    }

    async resetPlayerProgress(userId) {
        return this.request(`/admin/players/${userId}/reset`, {
            method: "POST"
        });
    }
}

export const api = new ApiClient();
