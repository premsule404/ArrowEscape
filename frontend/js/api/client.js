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
                throw new Error(err.detail || `API Error: ${response.statusText}`);
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
        if (res.access_token) {
            localStorage.setItem("access_token", res.access_token);
        }
        return res;
    }

    async register(username, password, email = null) {
        const res = await this.request("/auth/register", {
            method: "POST",
            body: JSON.stringify({ username, password, email, is_guest: false })
        });
        if (res.access_token) {
            localStorage.setItem("access_token", res.access_token);
        }
        return res;
    }

    async guestLogin(displayName = null) {
        const res = await this.request("/auth/guest", {
            method: "POST",
            body: JSON.stringify({ display_name: displayName })
        });
        if (res.access_token) {
            localStorage.setItem("access_token", res.access_token);
        }
        return res;
    }

    async getMe() {
        return this.request("/auth/me");
    }
    
    async logout() {
        localStorage.removeItem("access_token");
    }

    // --- Cloud Save & Sync ---
    async syncProgress(levels = [], currentLevel = null) {
        return this.request("/progress/sync", {
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
        return this.request("/users/settings", {
            method: "PUT",
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
