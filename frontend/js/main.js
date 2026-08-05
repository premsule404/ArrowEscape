import { loader } from './engine/pyodide_loader.js';
import { GameLoop } from './core/game_loop.js';
import { hideLoading, hideVictory, hidePauseModal, setLevelTitle } from './ui/screens.js';

let currentLevelIndex = 1;
let gameLoop = null;

async function init() {
    try {
        await loader.init();
        
        const meta = await loader.loadLevel(1);
        setLevelTitle(meta.name);
        
        hideLoading();
        
        gameLoop = new GameLoop('game-canvas');
        gameLoop.start();
        
    } catch (e) {
        console.error("Initialization Failed:", e);
        document.querySelector('.loader').style.display = 'none';
        document.querySelector('#loading p').innerText = "Failed to load Engine. See console.";
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
        alert("Returning to Level Select...");
    };
}

// Undo Button
document.getElementById('btn-undo').onclick = () => {
    if (loader.engine && loader.engine.undo()) {
        gameLoop.syncArrowsFromEngine();
        gameLoop.syncHUD();
    }
};

// Continue Button (Next Level)
document.getElementById('btn-next').onclick = async () => {
    hideVictory();
    currentLevelIndex++;
    if (currentLevelIndex > 50) currentLevelIndex = 1;
    
    const meta = await loader.loadLevel(currentLevelIndex);
    setLevelTitle(meta.name);
    
    gameLoop.start();
};

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
        alert("Opening Level Select...");
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

// Bootstrap the app
init();
