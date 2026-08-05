export class LevelSelectScreen {
    constructor(onSelectLevelCallback) {
        this.modal = document.getElementById('levelselect-modal');
        this.grid = document.getElementById('level-grid');
        this.btnClose = document.getElementById('btn-close-levelselect');
        this.onSelectLevel = onSelectLevelCallback;
        
        if (this.btnClose) {
            this.btnClose.onclick = () => this.hide();
        }
    }

    show(totalLevels = 50, highestUnlocked = 1, levelProgressMap = {}) {
        if (!this.grid) return;
        this.grid.innerHTML = '';
        
        for (let i = 1; i <= totalLevels; i++) {
            const isUnlocked = i <= highestUnlocked;
            const progress = levelProgressMap[i] || { stars: 0, bestTime: 0 };
            
            const card = document.createElement('div');
            card.className = `level-card ${isUnlocked ? 'unlocked' : 'locked'}`;
            card.setAttribute('role', 'listitem');
            card.setAttribute('tabindex', isUnlocked ? '0' : '-1');
            
            let starsHtml = '';
            if (isUnlocked) {
                const earned = progress.stars || 0;
                starsHtml = `<div class="card-stars">${'★'.repeat(earned)}${'☆'.repeat(3 - earned)}</div>`;
            } else {
                starsHtml = `<div class="card-lock">🔒</div>`;
            }
            
            card.innerHTML = `
                <div class="level-num">${i}</div>
                ${starsHtml}
            `;
            
            if (isUnlocked) {
                card.onclick = () => {
                    this.hide();
                    if (this.onSelectLevel) {
                        this.onSelectLevel(i);
                    }
                };
                card.onkeydown = (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.hide();
                        if (this.onSelectLevel) {
                            this.onSelectLevel(i);
                        }
                    }
                };
            }
            
            this.grid.appendChild(card);
        }
        
        if (this.modal) this.modal.classList.add('active');
    }

    hide() {
        if (this.modal) this.modal.classList.remove('active');
    }
}
