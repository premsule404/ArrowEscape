export const uiVictory = document.getElementById('victory-modal');
export const uiGameOver = document.getElementById('gameover-modal');
export const uiPause = document.getElementById('pause-modal');
export const uiLoading = document.getElementById('loading');
export const levelTitle = document.getElementById('level-title');
export const heartsContainer = document.getElementById('hearts-container');
export const timerDisplay = document.getElementById('timer-display');
export const progressDisplay = document.getElementById('progress-display');
export const moveCountDisplay = document.getElementById('move-count');
export const gameOverTitle = document.getElementById('gameover-title');
export const gameOverMsg = document.getElementById('gameover-msg');

export function showPauseModal() {
    if (uiPause) uiPause.classList.add('active');
}

export function hidePauseModal() {
    if (uiPause) uiPause.classList.remove('active');
}

export function showVictoryCelebration(levelName, stars, coins, elapsed = 0, bestTime = 0, isNewBest = false) {
    const levelNameElem = document.getElementById('victory-level-name');
    const coinsElem = document.getElementById('victory-coins');
    const starsContainer = document.getElementById('victory-stars');
    const timeInfoElem = document.getElementById('victory-time-info');
    
    if (levelNameElem) levelNameElem.innerText = levelName;
    if (coinsElem) coinsElem.innerText = `+0`;
    
    if (timeInfoElem) {
        let text = `Time: ${Math.round(elapsed)}s | Best: ${Math.round(bestTime || elapsed)}s`;
        if (isNewBest) text += ` 🏆 NEW BEST!`;
        timeInfoElem.innerText = text;
    }
    
    if (starsContainer) {
        const slots = starsContainer.querySelectorAll('.star-slot');
        slots.forEach((s, idx) => {
            s.classList.remove('earned');
            if (idx < stars) {
                setTimeout(() => {
                    s.classList.add('earned');
                }, (idx + 1) * 300);
            }
        });
    }
    
    // Count-up Coins Ticker
    let current = 0;
    const target = coins;
    if (target === 0) {
        if (coinsElem) coinsElem.innerText = `+0`;
    } else {
        const step = Math.max(1, Math.floor(target / 15));
        const interval = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(interval);
            }
            if (coinsElem) coinsElem.innerText = `+${current}`;
        }, 40);
    }
    
    if (uiVictory) uiVictory.classList.add('active');
}

export function hideVictory() {
    if (uiVictory) uiVictory.classList.remove('active');
}

export function showGameOver(title, message) {
    if (gameOverTitle) gameOverTitle.innerText = title;
    if (gameOverMsg) gameOverMsg.innerText = message;
    if (uiGameOver) uiGameOver.classList.add('active');
}

export function hideGameOver() {
    if (uiGameOver) uiGameOver.classList.remove('active');
}

export function hideLoading() {
    if (uiLoading) uiLoading.classList.remove('active');
}

export function setLevelTitle(title) {
    if (levelTitle) levelTitle.innerText = title;
}

export function updateHUD(hearts, remainingSecs, remainingArrows, totalArrows, moves) {
    if (heartsContainer) {
        const h = Math.max(0, Math.min(3, Number(hearts) || 0));
        heartsContainer.innerText = "❤️".repeat(h) + "🤍".repeat(3 - h);
    }
    if (timerDisplay) {
        const secs = Math.ceil(Math.max(0, Number(remainingSecs) || 0));
        const mins = Math.floor(secs / 60);
        const remSecs = secs % 60;
        timerDisplay.innerText = `⏱ ${String(mins).padStart(2, '0')}:${String(remSecs).padStart(2, '0')}`;
    }
    if (progressDisplay) {
        const rawTotal = Number(totalArrows);
        const rawRem = Number(remainingArrows);
        
        if (isNaN(rawTotal) || rawTotal <= 0) {
            progressDisplay.innerText = "0/0";
        } else {
            const total = Math.max(0, Math.floor(rawTotal));
            const rem = isNaN(rawRem) ? total : Math.max(0, Math.min(total, Math.floor(rawRem)));
            const completed = Math.max(0, Math.min(total, total - rem));
            progressDisplay.innerText = `${completed}/${total}`;
        }
    }
    if (moveCountDisplay) {
        const m = Math.max(0, Number(moves) || 0);
        moveCountDisplay.innerText = `${m}`;
    }
}
