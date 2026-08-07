import { api } from '../api/client.js';
import { cloudSave } from '../services/cloud_save.js';

export class NavigationManager {
    constructor() {
        this.welcomeScreen = document.getElementById('welcome-screen');
        this.mainMenuScreen = document.getElementById('main-menu-screen');
        this.gameplayScreen = document.getElementById('gameplay-screen');
        
        this.bindEvents();
    }

    bindEvents() {
        // Welcome Screen Buttons
        const welcomeLogin = document.getElementById('welcome-btn-login');
        if (welcomeLogin) {
            welcomeLogin.onclick = () => {
                if (window.authScreens) window.authScreens.showLogin();
            };
        }

        const welcomeRegister = document.getElementById('welcome-btn-register');
        if (welcomeRegister) {
            welcomeRegister.onclick = () => {
                if (window.authScreens) window.authScreens.showRegister();
            };
        }

        const welcomeGuest = document.getElementById('welcome-btn-guest');
        if (welcomeGuest) {
            welcomeGuest.onclick = async () => {
                try {
                    const res = await api.guestLogin();
                    await cloudSave.downloadCloudProgress();
                    this.showMainMenu();
                    if (window.notificationSystem) {
                        window.notificationSystem.notify("Guest Mode Active", "Playing as Guest. Progress saved locally.", "system", "🎮");
                    }
                } catch (e) {
                    console.warn("Guest login fallback:", e);
                    this.showMainMenu();
                }
            };
        }

        // Main Menu Grid Buttons
        const mmPlay = document.getElementById('mm-btn-play');
        if (mmPlay) {
            mmPlay.onclick = () => {
                this.showGameplayScreen();
            };
        }

        const mmLevelSelect = document.getElementById('mm-btn-level-select');
        if (mmLevelSelect) {
            mmLevelSelect.onclick = () => {
                if (window.levelSelectScreen) {
                    window.levelSelectScreen.show(50, cloudSave.localSave.current_level || 1, cloudSave.localSave.completed_levels || {});
                }
            };
        }

        const mmLeaderboard = document.getElementById('mm-btn-leaderboard');
        if (mmLeaderboard) {
            mmLeaderboard.onclick = () => {
                if (window.leaderboardScreen) window.leaderboardScreen.show();
            };
        }

        const mmAchievements = document.getElementById('mm-btn-achievements');
        if (mmAchievements) {
            mmAchievements.onclick = () => {
                if (window.achievementsScreen) window.achievementsScreen.show();
            };
        }

        const mmDaily = document.getElementById('mm-btn-daily');
        if (mmDaily) {
            mmDaily.onclick = () => {
                if (window.dailyRewardsScreen) window.dailyRewardsScreen.show();
            };
        }

        const mmShop = document.getElementById('mm-btn-shop');
        if (mmShop) {
            mmShop.onclick = () => {
                if (window.shopScreen) window.shopScreen.show();
            };
        }

        const mmFriends = document.getElementById('mm-btn-friends');
        if (mmFriends) {
            mmFriends.onclick = () => {
                if (window.friendsScreen) window.friendsScreen.show();
            };
        }

        const mmNotifs = document.getElementById('mm-btn-notifs');
        if (mmNotifs) {
            mmNotifs.onclick = () => {
                if (window.notificationSystem) window.notificationSystem.show();
            };
        }

        const mmStats = document.getElementById('mm-btn-stats');
        if (mmStats) {
            mmStats.onclick = () => {
                if (window.statsDashboardScreen) window.statsDashboardScreen.show();
            };
        }

        const mmAccount = document.getElementById('mm-btn-account');
        if (mmAccount) {
            mmAccount.onclick = async () => {
                if (window.authScreens) {
                    try {
                        const userData = await api.getMe();
                        window.authScreens.showProfile(userData);
                    } catch (e) {
                        window.authScreens.showLogin();
                    }
                }
            };
        }

        const mmSettings = document.getElementById('mm-btn-settings');
        if (mmSettings) {
            mmSettings.onclick = () => {
                if (window.settingsScreen) window.settingsScreen.show();
            };
        }

        const mmLogout = document.getElementById('mm-btn-logout');
        if (mmLogout) {
            mmLogout.onclick = async () => {
                await api.logout();
                this.showWelcomeScreen();
                if (window.notificationSystem) {
                    window.notificationSystem.notify("Logged Out", "You have been logged out.", "system", "🚪");
                }
            };
        }

        // Gameplay Home Button
        const btnGameplayHome = document.getElementById('btn-gameplay-home');
        if (btnGameplayHome) {
            btnGameplayHome.onclick = () => {
                this.showMainMenu();
            };
        }
    }

    showWelcomeScreen() {
        if (this.gameplayScreen) this.gameplayScreen.classList.add('hidden');
        if (this.mainMenuScreen) this.mainMenuScreen.classList.add('hidden');
        if (this.welcomeScreen) {
            this.welcomeScreen.classList.remove('hidden');
            this.welcomeScreen.classList.add('active');
        }
    }

    showMainMenu() {
        if (this.welcomeScreen) this.welcomeScreen.classList.add('hidden');
        if (this.gameplayScreen) this.gameplayScreen.classList.add('hidden');
        if (this.mainMenuScreen) {
            this.mainMenuScreen.classList.remove('hidden');
            this.mainMenuScreen.classList.add('active');
            this.updateMainMenuUserData();
        }
    }

    showGameplayScreen() {
        if (this.welcomeScreen) this.welcomeScreen.classList.add('hidden');
        if (this.mainMenuScreen) this.mainMenuScreen.classList.add('hidden');
        if (this.gameplayScreen) {
            this.gameplayScreen.classList.remove('hidden');
            this.gameplayScreen.classList.add('active');
        }
        if (window.gameLoop) {
            window.gameLoop.start();
        }
    }

    updateMainMenuUserData() {
        const local = cloudSave.localSave;
        const curLvl = local.current_level || 1;
        const completedCount = Object.keys(local.completed_levels || {}).length;
        const totalCoins = local.total_coins || 0;
        const totalStars = local.total_stars || 0;

        const mmCoins = document.getElementById('mm-coins');
        const mmStars = document.getElementById('mm-stars');
        const mmCurLevel = document.getElementById('mm-cur-level');
        const mmPlayLevel = document.getElementById('mm-play-level');
        const mmUsername = document.getElementById('mm-username');
        const mmAvatar = document.getElementById('mm-avatar');
        const mmSyncStatus = document.getElementById('mm-sync-status');

        if (mmCoins) mmCoins.innerText = totalCoins.toLocaleString();
        if (mmStars) mmStars.innerText = totalStars;
        if (mmCurLevel) mmCurLevel.innerText = curLvl;
        if (mmPlayLevel) mmPlayLevel.innerText = curLvl;

        if (localStorage.getItem("access_token")) {
            if (mmSyncStatus) {
                mmSyncStatus.innerText = "🟢 Cloud Synced";
                mmSyncStatus.className = "sync-status-badge synced";
            }
            api.getMe().then(user => {
                if (mmUsername) mmUsername.innerText = user.username || "Player";
                if (mmAvatar) mmAvatar.innerText = user.avatar || "🎯";
            }).catch(() => {});
        } else {
            if (mmSyncStatus) {
                mmSyncStatus.innerText = "📶 Offline Guest";
                mmSyncStatus.className = "sync-status-badge offline";
            }
            if (mmUsername) mmUsername.innerText = "Local Guest";
            if (mmAvatar) mmAvatar.innerText = "🎯";
        }
    }
}
