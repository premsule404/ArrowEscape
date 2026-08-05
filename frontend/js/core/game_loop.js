import { loader } from '../engine/pyodide_loader.js';
import { api } from '../api/client.js';
import { showVictoryCelebration, showGameOver, hideGameOver, hideVictory, showPauseModal, hidePauseModal, updateHUD } from '../ui/screens.js';

export class GameLoop {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.arrows = [];
        this.tileSize = 0;
        this.isRunning = false;
        this.lastTime = 0;
        this.hasClaimedReward = false;
        
        window.addEventListener('resize', () => this.resizeCanvas());
        window.addEventListener('blur', () => this.handleWindowBlur());
        this.canvas.addEventListener('pointerdown', (e) => this.handleInput(e));
        
        this.setupEngineEvents();
    }

    handleWindowBlur() {
        if (loader.engine && loader.engine.state && loader.engine.state.name === 'PLAYING') {
            loader.engine.pause();
        }
    }

    setupEngineEvents() {
        if (!loader.engine) return;
        
        loader.engine.events.add_listener("on_wrong_move", (data) => {
            this.syncHUD();
        });
        
        loader.engine.events.add_listener("on_pause", () => {
            showPauseModal();
        });
        
        loader.engine.events.add_listener("on_resume", () => {
            hidePauseModal();
        });
        
        loader.engine.events.add_listener("on_game_over", (data) => {
            this.stop();
            const reason = data && data.get ? data.get("reason") : (data ? data.reason : "out_of_hearts");
            const title = reason === "out_of_hearts" ? "Out of Hearts!" : "Time's Up!";
            const msg = reason === "out_of_hearts" ? "No hearts left!" : "You ran out of time!";
            showGameOver(title, msg);
        });
        
        loader.engine.events.add_listener("on_win", (data) => {
            this.stop();
            const stars = loader.engine.stars_earned;
            const coins = loader.engine.coins_earned;
            const levelName = document.getElementById('level-title') ? document.getElementById('level-title').innerText : "Level 1";
            
            showVictoryCelebration(levelName, stars, coins);
        });
    }

    syncHUD() {
        if (!loader.engine) return;
        const remaining = loader.engine.board ? loader.engine.board.arrows.size : 0;
        updateHUD(
            loader.engine.hearts,
            loader.engine.time_remaining,
            remaining,
            loader.engine.total_arrows_count,
            loader.engine.moves_count
        );
    }

    start() {
        this.isRunning = true;
        this.hasClaimedReward = false;
        this.lastTime = performance.now();
        this.setupEngineEvents();
        this.syncArrowsFromEngine();
        this.resizeCanvas();
        this.syncHUD();
        requestAnimationFrame((time) => this.render(time));
    }

    stop() {
        this.isRunning = false;
    }

    restartLevel() {
        hideGameOver();
        hideVictory();
        hidePauseModal();
        if (loader.engine) {
            loader.engine.restart();
            this.syncHUD();
        }
        this.start();
    }

    syncArrowsFromEngine() {
        this.arrows = [];
        if (!loader.engine) return;
        
        const pyArrows = loader.engine.board.arrows;
        const keys = pyArrows.keys();
        for (const key of keys) {
            const arr = pyArrows.get(key);
            this.arrows.push({
                id: key,
                x: arr.position.x,
                y: arr.position.y,
                direction: arr.direction.name,
                theme: arr.color_theme,
                state: 'idle',
                animOffsetX: 0,
                animOffsetY: 0
            });
        }
    }

    resizeCanvas() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        const size = Math.min(rect.width, rect.height, 500);
        this.canvas.width = size * window.devicePixelRatio;
        this.canvas.height = size * window.devicePixelRatio;
        this.canvas.style.width = size + 'px';
        this.canvas.style.height = size + 'px';
        
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        
        if (loader.engine) {
            this.tileSize = size / loader.engine.board.width;
        }
    }

    handleInput(e) {
        if (!loader.engine || !this.isRunning || loader.engine.is_game_over || loader.engine.is_paused) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const gridX = Math.floor(x / this.tileSize);
        const gridY = Math.floor(y / this.tileSize);
        
        const clickedArrow = this.arrows.find(a => a.x === gridX && a.y === gridY && a.state === 'idle');
        
        if (clickedArrow) {
            const success = loader.engine.tap_arrow(clickedArrow.id);
            if (success) {
                clickedArrow.state = 'sliding';
                this.syncHUD();
            } else {
                clickedArrow.state = 'shaking';
                clickedArrow.shakeTime = performance.now();
                this.syncHUD();
            }
        }
    }

    render(time) {
        if (!this.isRunning) return;
        
        const dt = (time - this.lastTime) / 1000;
        this.lastTime = time;
        
        if (loader.engine && dt > 0 && dt < 1 && !loader.engine.is_paused) {
            loader.engine.tick_timer(dt);
            this.syncHUD();
        }
        
        const rect = this.canvas.getBoundingClientRect();
        this.ctx.clearRect(0, 0, rect.width, rect.height);
        
        if (!loader.engine) {
            requestAnimationFrame((t) => this.render(t));
            return;
        }
        
        // Draw Grid
        this.ctx.strokeStyle = '#334155';
        this.ctx.lineWidth = 1;
        for(let i=0; i<=loader.engine.board.width; i++) {
            this.ctx.beginPath(); this.ctx.moveTo(i * this.tileSize, 0); this.ctx.lineTo(i * this.tileSize, rect.height); this.ctx.stroke();
            this.ctx.beginPath(); this.ctx.moveTo(0, i * this.tileSize); this.ctx.lineTo(rect.width, i * this.tileSize); this.ctx.stroke();
        }
        
        // Draw Arrows
        for (let i = this.arrows.length - 1; i >= 0; i--) {
            let a = this.arrows[i];
            
            let drawX = a.x * this.tileSize;
            let drawY = a.y * this.tileSize;
            
            if (a.state === 'shaking') {
                const elapsed = time - a.shakeTime;
                if (elapsed > 300) {
                    a.state = 'idle';
                } else {
                    const offset = Math.sin(elapsed / 20) * 5;
                    if (a.direction === 'LEFT' || a.direction === 'RIGHT') {
                        drawX += offset;
                    } else {
                        drawY += offset;
                    }
                }
            } else if (a.state === 'sliding') {
                const speed = this.tileSize * 0.15;
                if (a.direction === 'UP') a.animOffsetY -= speed;
                if (a.direction === 'DOWN') a.animOffsetY += speed;
                if (a.direction === 'LEFT') a.animOffsetX -= speed;
                if (a.direction === 'RIGHT') a.animOffsetX += speed;
                
                drawX += a.animOffsetX;
                drawY += a.animOffsetY;
                
                if (drawX < -this.tileSize || drawX > rect.width || drawY < -this.tileSize || drawY > rect.height) {
                    this.arrows.splice(i, 1);
                    continue;
                }
            }
            
            const padding = this.tileSize * 0.1;
            this.ctx.fillStyle = a.state === 'shaking' ? '#ef4444' : '#38bdf8'; 
            
            this.ctx.beginPath();
            this.ctx.roundRect(drawX + padding, drawY + padding, this.tileSize - padding*2, this.tileSize - padding*2, 12);
            this.ctx.fill();
            
            // Draw Triangle Pointer
            this.ctx.fillStyle = '#0f172a';
            this.ctx.save();
            this.ctx.translate(drawX + this.tileSize/2, drawY + this.tileSize/2);
            if (a.direction === 'RIGHT') this.ctx.rotate(Math.PI/2);
            if (a.direction === 'DOWN') this.ctx.rotate(Math.PI);
            if (a.direction === 'LEFT') this.ctx.rotate(-Math.PI/2);
            
            this.ctx.beginPath();
            this.ctx.moveTo(0, -this.tileSize*0.25);
            this.ctx.lineTo(-this.tileSize*0.2, this.tileSize*0.15);
            this.ctx.lineTo(this.tileSize*0.2, this.tileSize*0.15);
            this.ctx.fill();
            this.ctx.restore();
        }
        
        requestAnimationFrame((t) => this.render(t));
    }
}
