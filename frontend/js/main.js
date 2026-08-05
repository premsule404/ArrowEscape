import { loader } from './engine/pyodide_loader.js';
import { GameLoop } from './core/game_loop.js';
import { hideLoading, hideVictory, hidePauseModal, setLevelTitle, updateLoadingProgress } from './ui/screens.js';
import { LevelSelectScreen } from './ui/level_select_screen.js';

let currentLevelIndex = 1;
let gameLoop = null;
let levelSelectScreen = null;

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
        await loader.init((pct, task) => {
            updateLoadingProgress(pct, task);
        });
        
        levelSelectScreen = new LevelSelectScreen((selectedLvl) => {
            loadLevelByIndex(selectedLvl);
        });
        
        updateLoadingProgress(90, "Loading Level 1 Layout...");
        await loadLevelByIndex(1);
        
        updateLoadingProgress(100, "Starting Game...");
        setTimeout(() => hideLoading(), 250);
        
        gameLoop = new GameLoop('game-canvas');
        gameLoop.start();
        
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

// Open Level Select Nav
const btnLevelNav = document.getElementById('btn-level-select-nav');
if (btnLevelNav) {
    btnLevelNav.onclick = () => {
        if (levelSelectScreen) {
            levelSelectScreen.show(50, 50);
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

// Exit Pause Button
const btnExitModal = document.getElementById('btn-exit-modal');
if (btnExitModal) {
    btnExitModal.onclick = () => {
        hidePauseModal();
        if (levelSelectScreen) {
            levelSelectScreen.show(50, 50);
        }
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
            levelSelectScreen.show(50, 50);
        }
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

// Keyboard Accessibility & Hotkeys
window.addEventListener('keydown', (e) => {
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
