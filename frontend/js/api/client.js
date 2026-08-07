import { API_V1_URL } from '../config.js';

export class ApiClient {
    constructor(baseURL = API_V1_URL) {
        this.baseURL = baseURL;
        this.inFlightRequests = new Map();
    }

    async checkHealth() {
        return this.request("/health", { method: "GET" }, 1);
    }

    getHeaders() {
        const token = localStorage.getItem("access_token");
        return {
            "Content-Type": "application/json",
            ...(token ? { "Authorization": `Bearer ${token}` } : {})
        };
    }

    async refreshTokens() {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
            this.clearTokens();
            throw new Error("No refresh token available");
        }
        
        const response = await fetch(`${this.baseURL}/auth/refresh`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken })
        });
        
        if (!response.ok) {
            this.clearTokens();
            throw new Error("Session expired. Please log in again.");
        }
        
        const data = await response.json();
        this.saveTokens(data);
        return data;
    }

    clearTokens() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
    }

    async request(endpoint, options = {}, retries = 2) {
        const cacheKey = `${options.method || 'GET'}:${endpoint}:${options.body || ''}`;
        
        // Deduplicate GET / read-only in-flight requests
        if ((!options.method || options.method === 'GET') && this.inFlightRequests.has(cacheKey)) {
            return this.inFlightRequests.get(cacheKey);
        }

        const fetchPromise = (async () => {
            let attempt = 0;
            while (attempt <= retries) {
                try {
                    const url = `${this.baseURL}${endpoint}`;
                    const response = await fetch(url, {
                        ...options,
                        headers: {
                            ...this.getHeaders(),
                            ...options.headers
                        }
                    });

                    if (response.status === 401 && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/refresh') && !options._isRetry) {
                        try {
                            await this.refreshTokens();
                            options._isRetry = true;
                            return await this.request(endpoint, options, retries);
                        } catch (refreshErr) {
                            this.clearTokens();
                            throw new Error("Session expired. Please log in again.");
                        }
                    }
                    
                    if (!response.ok) {
                        const err = await response.json().catch(() => ({}));
                        const msg = err.error?.message || err.detail || `API Error: ${response.statusText}`;
                        throw new Error(msg);
                    }
                    
                    return await response.json();
                } catch (error) {
                    attempt++;
                    if (attempt > retries) throw error;
                    await new Promise(r => setTimeout(r, attempt * 300)); // Exponential backoff
                }
            }
        })();

        if (!options.method || options.method === 'GET') {
            this.inFlightRequests.set(cacheKey, fetchPromise);
            fetchPromise.finally(() => this.inFlightRequests.delete(cacheKey));
        }

        return fetchPromise;
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

    async getProfile() {
        return this.request("/profile");
    }

    async updateProfile(profileData) {
        return this.request("/profile", {
            method: "PATCH",
            body: JSON.stringify(profileData)
        });
    }

    async changePassword(oldPassword, newPassword) {
        return this.request("/profile/change-password", {
            method: "POST",
            body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
        });
    }

    async deleteAccount() {
        const res = await this.request("/profile", {
            method: "DELETE"
        });
        this.clearTokens();
        return res;
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

    // --- Achievements ---
    async getAchievements() {
        return this.request("/achievements");
    }

    async claimAchievement(achievementId) {
        return this.request("/achievements/claim", {
            method: "POST",
            body: JSON.stringify({ achievement_id: achievementId })
        });
    }

    async syncAchievements(achievementsList) {
        return this.request("/achievements/sync", {
            method: "POST",
            body: JSON.stringify({ achievements: achievementsList })
        });
    }

    // --- Daily Rewards ---
    async getDailyStatus() {
        return this.request("/daily/status");
    }

    async claimDailyReward() {
        return this.request("/daily/claim", {
            method: "POST"
        });
    }

    // --- Shop & Inventory ---
    async getShopItems() {
        return this.request("/shop/items");
    }

    async purchaseShopItem(itemId) {
        return this.request("/shop/purchase", {
            method: "POST",
            body: JSON.stringify({ item_id: itemId })
        });
    }

    async equipShopItem(itemId, itemType) {
        return this.request("/shop/equip", {
            method: "POST",
            body: JSON.stringify({ item_id: itemId, item_type: itemType })
        });
    }

    // --- Friends & Social ---
    async getFriendsData() {
        return this.request("/friends");
    }

    async searchPlayers(query) {
        return this.request(`/friends/search?query=${encodeURIComponent(query)}`);
    }

    async sendFriendRequest(userId = null, username = null) {
        return this.request("/friends/request", {
            method: "POST",
            body: JSON.stringify({ user_id: userId, username })
        });
    }

    async acceptFriendRequest(requestId) {
        return this.request("/friends/accept", {
            method: "POST",
            body: JSON.stringify({ request_id: requestId })
        });
    }

    async rejectFriendRequest(requestId) {
        return this.request("/friends/reject", {
            method: "POST",
            body: JSON.stringify({ request_id: requestId })
        });
    }

    async removeFriend(friendId) {
        return this.request(`/friends/${friendId}`, {
            method: "DELETE"
        });
    }

    async challengeFriend(friendId, levelNum = 1) {
        return this.request("/friends/challenge", {
            method: "POST",
            body: JSON.stringify({ friend_id: friendId, level_num: levelNum })
        });
    }

    async getFriendProfile(userId) {
        return this.request(`/friends/profile/${userId}`);
    }

    // --- Notifications ---
    async getNotifications(unreadOnly = false) {
        return this.request(`/notifications?unread_only=${unreadOnly}`);
    }

    async markNotificationRead(notificationId) {
        return this.request(`/notifications/read/${notificationId}`, {
            method: "PUT"
        });
    }

    async markAllNotificationsRead() {
        return this.request("/notifications/read-all", {
            method: "PUT"
        });
    }

    async clearNotifications() {
        return this.request("/notifications/clear", {
            method: "DELETE"
        });
    }

    // --- Statistics ---
    async getStatistics() {
        return this.request("/stats");
    }

    // --- Leaderboard & Profile ---
    async getLeaderboard(category = "stars", scope = "global", timeframe = "all_time") {
        return this.request(`/leaderboard?category=${category}&scope=${scope}&timeframe=${timeframe}`);
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
