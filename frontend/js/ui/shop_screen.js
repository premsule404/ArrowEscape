import { api } from '../api/client.js';
import { cloudSave } from '../services/cloud_save.js';
import { playerState } from '../services/player_state.js';

export class ShopScreen {
    constructor() {
        this.modal = document.getElementById('shop-modal');
        this.btnClose = document.getElementById('btn-close-shop');
        this.coinsElem = document.getElementById('shop-coins-val');
        this.starsElem = document.getElementById('shop-stars-val');
        this.gridElem = document.getElementById('shop-items-grid');
        this.tabsElem = document.getElementById('shop-category-tabs');
        
        this.currentCategory = 'themes';
        this.shopData = null;
        this.bindEvents();

        playerState.subscribe((state) => {
            if (this.coinsElem) this.coinsElem.innerText = (state.total_coins || 0).toLocaleString();
            if (this.starsElem) this.starsElem.innerText = state.total_stars || 0;
            if (this.shopData) {
                this.shopData.coins = state.total_coins || 0;
                this.shopData.stars = state.total_stars || 0;
            }
        });
    }

    bindEvents() {
        if (this.btnClose) {
            this.btnClose.onclick = () => this.hide();
        }

        if (this.tabsElem) {
            this.tabsElem.querySelectorAll('.tab-btn').forEach(btn => {
                btn.onclick = () => {
                    this.tabsElem.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    this.currentCategory = btn.getAttribute('data-category');
                    this.renderGrid();
                };
            });
        }

        // Hotkey 'S' to open Shop
        window.addEventListener('keydown', (e) => {
            if ((e.key === 's' || e.key === 'S') && !e.target.matches('input, textarea')) {
                this.toggle();
            }
        });
    }

    async show() {
        if (this.modal) this.modal.classList.add('active');
        await this.fetchData();
    }

    hide() {
        if (this.modal) this.modal.classList.remove('active');
    }

    toggle() {
        if (this.modal && this.modal.classList.contains('active')) {
            this.hide();
        } else {
            this.show();
        }
    }

    async fetchData() {
        if (!this.gridElem) return;
        this.gridElem.innerHTML = `<div class="shop-loading">Loading Shop Catalog...</div>`;

        try {
            if (localStorage.getItem("access_token")) {
                this.shopData = await api.getShopItems();
            } else {
                // Local fallback shop data
                const local = cloudSave.localSave;
                this.shopData = {
                    coins: local.total_coins || 0,
                    stars: local.total_stars || 0,
                    equipped: {
                        theme: local.equipped_theme || "theme_neon",
                        skin: local.equipped_skin || "skin_classic",
                        board: local.equipped_board || "board_slate"
                    },
                    owned: local.owned_items || ["theme_neon", "skin_classic", "board_slate"],
                    items: [
                        { id: "theme_neon", category: "themes", name: "Default Neon", description: "Sleek glowing cyan & dark slate default theme", price: 0, icon: "🎨", type: "theme" },
                        { id: "theme_cyberpunk", category: "themes", name: "Cyberpunk Purple", description: "Futuristic magenta & neon violet grid aesthetic", price: 500, icon: "👾", type: "theme" },
                        { id: "theme_emerald", category: "themes", name: "Forest Emerald", description: "Relaxing deep forest green & mint glow", price: 750, icon: "🌲", type: "theme" },
                        { id: "theme_sunset", category: "themes", name: "Sunset Glow", description: "Vibrant warm amber & crimson twilight design", price: 1000, icon: "🌅", type: "theme" },
                        { id: "skin_classic", category: "arrow_skins", name: "Classic Arrow", description: "Clean minimal arrow heads", price: 0, icon: "🎯", type: "skin" },
                        { id: "skin_golden", category: "arrow_skins", name: "Golden Arrow", description: "Shining 24k gold arrow vectors", price: 400, icon: "🌟", type: "skin" },
                        { id: "skin_plasma", category: "arrow_skins", name: "Plasma Beam", description: "Electric energy beam arrow heads", price: 800, icon: "⚡", type: "skin" },
                        { id: "skin_wooden", category: "arrow_skins", name: "Wooden Craft", description: "Rustic carved oak arrows", price: 300, icon: "🪵", type: "skin" },
                        { id: "board_slate", category: "board_themes", name: "Dark Slate Grid", description: "Classic dark tile background", price: 0, icon: "🧱", type: "board" },
                        { id: "board_glass", category: "board_themes", name: "Glassmorphism", description: "Frosted glass floating tiles", price: 600, icon: "🧊", type: "board" },
                        { id: "board_hexagon", category: "board_themes", name: "Hexagon Matrix", description: "Sci-fi hexagonal lattice background", price: 900, icon: "🔷", type: "board" },
                        { id: "hints_5", category: "boosters", name: "5x Hints Pack", description: "Instantly adds 5 AI level solution hints", price: 200, icon: "💡", type: "booster", reward_type: "hints", amount: 5 },
                        { id: "undos_10", category: "boosters", name: "10x Undo Pack", description: "Instantly adds 10 move undos", price: 150, icon: "↺", type: "booster", reward_type: "undos", amount: 10 },
                        { id: "hearts_3", category: "boosters", name: "Heart Refill (+3)", description: "Refills 3 extra lives for retries", price: 100, icon: "❤️", type: "booster", reward_type: "hearts", amount: 3 },
                        { id: "coins_500", category: "coin_packs", name: "Coin Sack (+500)", description: "Free welcome daily coin pack", price: 0, icon: "💰", type: "coins", amount: 500 },
                        { id: "coins_2000", category: "coin_packs", name: "Coin Vault (+2000)", description: "Exchange 15 stars for 2000 coins", price: 0, icon: "💎", type: "coins", amount: 2000, star_cost: 15 }
                    ]
                };
            }

            if (this.coinsElem) this.coinsElem.innerText = this.shopData.coins;
            if (this.starsElem) this.starsElem.innerText = this.shopData.stars;

            this.renderGrid();

        } catch (e) {
            this.gridElem.innerHTML = `<div class="shop-error">Failed to load shop catalog. (${e.message})</div>`;
        }
    }

    renderGrid() {
        if (!this.gridElem || !this.shopData) return;

        let filteredItems = [];
        if (this.currentCategory === 'inventory') {
            filteredItems = this.shopData.items.filter(i => this.shopData.owned.includes(i.id));
        } else {
            filteredItems = this.shopData.items.filter(i => i.category === this.currentCategory);
        }

        if (filteredItems.length === 0) {
            this.gridElem.innerHTML = `<div class="shop-empty">No items in this category.</div>`;
            return;
        }

        this.gridElem.innerHTML = filteredItems.map(item => {
            const isOwned = this.shopData.owned.includes(item.id);
            const isEquipped = (
                (item.type === 'theme' && this.shopData.equipped.theme === item.id) ||
                (item.type === 'skin' && this.shopData.equipped.skin === item.id) ||
                (item.type === 'board' && this.shopData.equipped.board === item.id)
            );

            let actionBtnHtml = '';
            if (isEquipped) {
                actionBtnHtml = `<span class="equipped-badge">EQUIPPED</span>`;
            } else if (isOwned && ['theme', 'skin', 'board'].includes(item.type)) {
                actionBtnHtml = `<button class="secondary-btn equip-btn" data-id="${item.id}" data-type="${item.type}">EQUIP</button>`;
            } else {
                const canAfford = item.price === 0 || this.shopData.coins >= item.price;
                const starCost = item.star_cost || 0;
                const canAffordStars = starCost === 0 || this.shopData.stars >= starCost;
                const priceLabel = starCost > 0 ? `${starCost} ⭐` : (item.price > 0 ? `${item.price} 💰` : 'FREE');
                const disabledAttr = (canAfford && canAffordStars) ? '' : 'disabled';

                actionBtnHtml = `<button class="primary-btn success-btn buy-btn" data-id="${item.id}" ${disabledAttr}>BUY ${priceLabel}</button>`;
            }

            return `
                <div class="shop-card ${isEquipped ? 'equipped' : (isOwned ? 'owned' : '')}">
                    <div class="shop-item-icon">${item.icon}</div>
                    <div class="shop-item-details">
                        <h4 class="shop-item-title">${item.name}</h4>
                        <p class="shop-item-desc">${item.description}</p>
                    </div>
                    <div class="shop-item-action">
                        ${actionBtnHtml}
                    </div>
                </div>
            `;
        }).join('');

        // Bind Buy & Equip click listeners
        this.gridElem.querySelectorAll('.buy-btn').forEach(btn => {
            btn.onclick = async () => {
                const itemId = btn.getAttribute('data-id');
                await this.handlePurchase(itemId);
            };
        });

        this.gridElem.querySelectorAll('.equip-btn').forEach(btn => {
            btn.onclick = async () => {
                const itemId = btn.getAttribute('data-id');
                const itemType = btn.getAttribute('data-type');
                await this.handleEquip(itemId, itemType);
            };
        });
    }

    async handlePurchase(itemId) {
        try {
            if (localStorage.getItem("access_token")) {
                const res = await api.purchaseShopItem(itemId);
                cloudSave.localSave.total_coins = res.total_coins;
                cloudSave.localSave.total_stars = res.total_stars;
                cloudSave.saveLocalSave();
                playerState.update({
                    total_coins: res.total_coins,
                    total_stars: res.total_stars
                });
            } else {
                const item = this.shopData.items.find(i => i.id === itemId);
                if (item) {
                    if (item.price > 0) {
                        cloudSave.localSave.total_coins = Math.max(0, (cloudSave.localSave.total_coins || 0) - item.price);
                    }
                    if (item.star_cost > 0) {
                        cloudSave.localSave.total_stars = Math.max(0, (cloudSave.localSave.total_stars || 0) - item.star_cost);
                    }
                    if (item.amount > 0 && item.type === 'coins') {
                        cloudSave.localSave.total_coins = (cloudSave.localSave.total_coins || 0) + item.amount;
                    }
                    if (!cloudSave.localSave.owned_items) cloudSave.localSave.owned_items = ["theme_neon", "skin_classic", "board_slate"];
                    if (!cloudSave.localSave.owned_items.includes(itemId)) {
                        cloudSave.localSave.owned_items.push(itemId);
                    }
                    cloudSave.saveLocalSave();
                    playerState.update({
                        total_coins: cloudSave.localSave.total_coins,
                        total_stars: cloudSave.localSave.total_stars
                    });
                }
            }
            alert("Purchase successful!");
            await this.fetchData();
        } catch (e) {
            alert(e.message || "Failed to purchase item.");
        }
    }

    async handleEquip(itemId, itemType) {
        try {
            if (localStorage.getItem("access_token")) {
                const res = await api.equipShopItem(itemId, itemType);
                this.shopData.equipped = res.equipped;
            } else {
                if (itemType === 'theme') cloudSave.localSave.equipped_theme = itemId;
                if (itemType === 'skin') cloudSave.localSave.equipped_skin = itemId;
                if (itemType === 'board') cloudSave.localSave.equipped_board = itemId;
                cloudSave.saveLocalSave();
                this.shopData.equipped[itemType] = itemId;
            }

            this.applyThemeToDOM(itemId, itemType);
            this.renderGrid();
        } catch (e) {
            alert(e.message || "Failed to equip item.");
        }
    }

    applyThemeToDOM(itemId, itemType) {
        if (itemType === 'theme') {
            document.body.setAttribute('data-theme', itemId);
        }
    }
}
