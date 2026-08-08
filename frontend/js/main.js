import { setLevelTitle, updateLoadingProgress, hideLoading, showOfflineMode, hideOfflineMode, hidePauseModal, hideVictory } from './ui/screens.js';
import { GameLoop } from './core/game_loop.js';
import { loader } from './engine/pyodide_loader.js';
import { LevelSelectScreen } from './ui/level_select_screen.js';
import { AuthScreens } from './ui/auth_screens.js';
import { LeaderboardScreen } from './ui/leaderboard_screen.js';
import { AchievementsScreen } from './ui/achievements_screen.js';
import { DailyRewardsScreen } from './ui/daily_rewards_screen.js';
import { ShopScreen } from './ui/shop_screen.js';
import { FriendsScreen } from './ui/friends_screen.js';
import { NotificationSystem } from './ui/notifications_screen.js';
import { StatsDashboardScreen } from './ui/stats_screen.js';
import { SettingsScreen } from './ui/settings_screen.js';
import { NavigationManager } from './ui/nav_manager.js';
import { api } from './api/client.js';
import { cloudSave } from './services/cloud_save.js';
import { playerState } from './services/player_state.js';

let currentLevelIndex = 1;
export let gameLoop = null;
export let levelSelectScreen = null;
export let authScreens = null;
export let leaderboardScreen = null;
export let achievementsScreen = null;
export let dailyRewardsScreen = null;
export let shopScreen = null;
export let friendsScreen = null;
export let notificationSystem = null;
export let statsDashboardScreen = null;
export let settingsScreen = null;
export let navManager = null;

async function checkBackendStatus() {
    try {
        const health = await api.checkHealth();
        if (health && health.status === "ok") {
            hideOfflineMode();
            console.log("Connected to production backend at:", api.baseURL);
            return true;
        }
    } catch (e) {
        console.warn("Backend API unavailable, using Offline Mode:", e.message);
    }
    showOfflineMode();
    if (notificationSystem) {
        notificationSystem.notify("Offline Mode Active", "Backend unavailable. Progress saved locally.", "offline", "📶");
    }
    return false;
}

async function loadLevelByIndex(idx) {
    currentLevelIndex = idx;
    const meta = await loader.loadLevel(currentLevelIndex);
    setLevelTitle(meta.name);
    if (gameLoop) {
        gameLoop.start();
    }
}

async function init() {
    try {
        notificationSystem = new NotificationSystem();
        window.notificationSystem = notificationSystem;

        updateLoadingProgress(5, "Checking Backend Health...");
        await checkBackendStatus();

        updateLoadingProgress(15, "Downloading Cloud Save...");
        await cloudSave.downloadCloudProgress();

        if (localStorage.getItem("access_token")) {
            try {
                const me = await api.getMe();
                await playerState.syncFromCloudUser(me);
            } catch (e) {
                console.warn("Failed to fetch initial user info:", e);
            }
        }

        authScreens = new AuthScreens(async (res) => {
            console.log("Authenticated successfully:", res);
            await cloudSave.downloadCloudProgress();
            if (res.user) {
                await playerState.syncFromCloudUser(res.user);
            }
            if (navManager) navManager.showMainMenu();
            notificationSystem.notify("Welcome Back!", `Logged in as ${res.user?.username || 'Player'}`, "system", "👤");
        });
        window.authScreens = authScreens;

        leaderboardScreen = new LeaderboardScreen();
        window.leaderboardScreen = leaderboardScreen;

        achievementsScreen = new AchievementsScreen();
        window.achievementsScreen = achievementsScreen;

        dailyRewardsScreen = new DailyRewardsScreen();
        window.dailyRewardsScreen = dailyRewardsScreen;

        shopScreen = new ShopScreen();
        window.shopScreen = shopScreen;

        friendsScreen = new FriendsScreen();
        window.friendsScreen = friendsScreen;

        statsDashboardScreen = new StatsDashboardScreen();
        window.statsDashboardScreen = statsDashboardScreen;

        settingsScreen = new SettingsScreen();
        window.settingsScreen = settingsScreen;

        navManager = new NavigationManager();
        window.navManager = navManager;

        await loader.init((pct, task) => {
            updateLoadingProgress(pct, task);
        });
        
        levelSelectScreen = new LevelSelectScreen(async (selectedLvl) => {
            await loadLevelByIndex(selectedLvl);
            if (navManager) navManager.showGameplayScreen();
        });
        window.levelSelectScreen = levelSelectScreen;
        
        gameLoop = new GameLoop('game-canvas');
        window.gameLoop = gameLoop;

        const startLvl = cloudSave.localSave.current_level || 1;
        updateLoadingProgress(90, `Loading Level ${startLvl} Layout...`);
        await loadLevelByIndex(startLvl);

        updateLoadingProgress(100, "Starting Game...");
        
        // Auto-navigate: Skip welcome screen if user is already logged in
        if (localStorage.getItem("access_token")) {
            navManager.showMainMenu();
        } else {
            navManager.showWelcomeScreen();
        }

        setTimeout(() => hideLoading(), 250);
        
    } catch (e) {
        console.error("Initialization Failed:", e);
        document.querySelector('.loader').style.display = 'none';
        document.querySelector('#loading p').innerText = `Initialization Failed: ${e.message}`;
    }
}

// Pause button
const btnPause = document.getElementById('btn-pause');
if (btnPause) {
    btnPause.onclick = () => {
        if (loader.engine) {
            loader.engine.pause();
        }
    };
}

// Restart HUD Button
const btnRestartHud = document.getElementById('btn-restart-hud');
if (btnRestartHud) {
    btnRestartHud.onclick = () => {
        if (gameLoop) {
            gameLoop.restartLevel();
        }
    };
}

// Resume Modal Button
const btnResumeModal = document.getElementById('btn-resume-modal');
if (btnResumeModal) {
    btnResumeModal.onclick = () => {
        if (loader.engine) {
            loader.engine.resume();
        }
    };
}

// Restart Pause Button
const btnRestartPause = document.getElementById('btn-restart-pause');
if (btnRestartPause) {
    btnRestartPause.onclick = () => {
        if (gameLoop) {
            gameLoop.restartLevel();
        }
    };
}

// Exit Pause Button -> Return to Main Menu
const btnExitModal = document.getElementById('btn-exit-modal');
if (btnExitModal) {
    btnExitModal.onclick = () => {
        hidePauseModal();
        if (navManager) navManager.showMainMenu();
    };
}

// Undo Button
const btnUndo = document.getElementById('btn-undo');
if (btnUndo) {
    btnUndo.onclick = () => {
        if (loader.engine && loader.engine.undo()) {
            gameLoop.syncArrowsFromEngine();
            gameLoop.syncHUD();
        }
    };
}

// Continue Button (Next Level)
const btnNext = document.getElementById('btn-next');
if (btnNext) {
    btnNext.onclick = async () => {
        hideVictory();
        currentLevelIndex++;
        if (currentLevelIndex > 50) currentLevelIndex = 1;
        await loadLevelByIndex(currentLevelIndex);
        if (navManager) navManager.showGameplayScreen();
    };
}

// Replay Level Button in Celebration Modal
const btnReplayCelebration = document.getElementById('btn-replay-celebration');
if (btnReplayCelebration) {
    btnReplayCelebration.onclick = () => {
        hideVictory();
        if (gameLoop) {
            gameLoop.restartLevel();
        }
    };
}

// Select Level Button in Celebration Modal
const btnSelectCelebration = document.getElementById('btn-select-celebration');
if (btnSelectCelebration) {
    btnSelectCelebration.onclick = () => {
        hideVictory();
        if (levelSelectScreen) {
            levelSelectScreen.show(50, cloudSave.localSave.current_level || 1, cloudSave.localSave.completed_levels || {});
        }
    };
}

// Main Menu Button in Celebration Modal
const btnMainMenuCelebration = document.getElementById('btn-main-menu-celebration');
if (btnMainMenuCelebration) {
    btnMainMenuCelebration.onclick = () => {
        hideVictory();
        if (navManager) navManager.showMainMenu();
    };
}

const btnRestartModal = document.getElementById('btn-restart-modal');
if (btnRestartModal) {
    btnRestartModal.onclick = () => {
        if (gameLoop) {
            gameLoop.restartLevel();
        }
    };
}

// Global Backdrop Overlay Click Handler
document.addEventListener('click', (e) => {
    if (e.target && e.target.classList && e.target.classList.contains('overlay') && e.target.id !== 'loading') {
        e.target.classList.remove('active');
    }
});

// Keyboard Accessibility & Hotkeys
window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const activeModal = document.querySelector('.overlay.active:not(#loading)');
        if (activeModal) {
            activeModal.classList.remove('active');
            return;
        }
    }

    if (e.key === 'p' || e.key === 'P' || e.key === 'Escape') {
        if (loader.engine) {
            if (loader.engine.is_paused) {
                loader.engine.resume();
            } else {
                loader.engine.pause();
            }
        }
    } else if (e.key === 'u' || e.key === 'U') {
        if (loader.engine && loader.engine.undo()) {
            gameLoop.syncArrowsFromEngine();
            gameLoop.syncHUD();
        }
    } else if (e.key === 'r' || e.key === 'R') {
        if (gameLoop) {
            gameLoop.restartLevel();
        }
    }
});

// Bootstrap the app
init();
