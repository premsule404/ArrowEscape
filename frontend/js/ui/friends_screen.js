import { api } from '../api/client.js';

export class FriendsScreen {
    constructor() {
        this.modal = document.getElementById('friends-modal');
        this.btnClose = document.getElementById('btn-close-friends');
        this.btnCopyInvite = document.getElementById('btn-copy-invite');
        this.searchInput = document.getElementById('friends-search-input');
        this.listElem = document.getElementById('friends-list-container');
        this.tabsElem = document.getElementById('friends-tabs');
        this.profileModal = document.getElementById('friend-profile-modal');
        this.profileCloseBtn = document.getElementById('btn-close-friend-profile');
        
        this.currentTab = 'friends';
        this.socialData = null;
        this.searchResults = null;
        this.bindEvents();
    }

    bindEvents() {
        if (this.btnClose) {
            this.btnClose.onclick = () => this.hide();
        }

        if (this.profileCloseBtn) {
            this.profileCloseBtn.onclick = () => {
                if (this.profileModal) this.profileModal.classList.remove('active');
            };
        }

        if (this.btnCopyInvite) {
            this.btnCopyInvite.onclick = () => {
                const link = this.socialData?.invite_link || window.location.href;
                navigator.clipboard.writeText(link);
                alert("Invite link copied to clipboard!\n" + link);
            };
        }

        if (this.tabsElem) {
            this.tabsElem.querySelectorAll('.tab-btn').forEach(btn => {
                btn.onclick = () => {
                    this.tabsElem.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    this.currentTab = btn.getAttribute('data-tab');
                    this.searchResults = null;
                    if (this.searchInput) this.searchInput.value = '';
                    this.renderList();
                };
            });
        }

        if (this.searchInput) {
            let debounceTimer = null;
            this.searchInput.oninput = () => {
                clearTimeout(debounceTimer);
                const query = this.searchInput.value.trim();
                if (query.length === 0) {
                    this.searchResults = null;
                    this.renderList();
                    return;
                }
                debounceTimer = setTimeout(async () => {
                    await this.performSearch(query);
                }, 300);
            };
        }

        // Hotkey 'F' to open Friends
        window.addEventListener('keydown', (e) => {
            if ((e.key === 'f' || e.key === 'F') && !e.target.matches('input, textarea')) {
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
        if (!this.listElem) return;
        this.listElem.innerHTML = `<div class="friends-loading">Loading Friends & Social...</div>`;

        try {
            if (localStorage.getItem("access_token")) {
                this.socialData = await api.getFriendsData();
            } else {
                // Local fallback social data
                this.socialData = {
                    friends: [
                        { id: 101, username: "SpeedyArrow", display_name: "Speedy Arrow", avatar: "🏹", country: "USA", is_online: true, total_stars: 45, completed_levels: 15 },
                        { id: 102, username: "PuzzleMaster", display_name: "Puzzle Master", avatar: "🧠", country: "UK", is_online: false, total_stars: 90, completed_levels: 30 }
                    ],
                    pending_requests: [
                        { request_id: 1, sender: { id: 201, username: "ChallengerX", display_name: "Challenger X", avatar: "⚔️", country: "Canada", is_online: true, total_stars: 20 } }
                    ],
                    recently_played: [
                        { id: 301, username: "FalconRunner", display_name: "Falcon Runner", avatar: "🦅", country: "Germany", is_online: true, total_stars: 60 }
                    ],
                    invite_link: "https://arrowescape.onrender.com/?invite=guest"
                };
            }

            this.renderList();

        } catch (e) {
            this.listElem.innerHTML = `<div class="friends-error">Failed to load friends. (${e.message})</div>`;
        }
    }

    async performSearch(query) {
        try {
            if (localStorage.getItem("access_token")) {
                this.searchResults = await api.searchPlayers(query);
            } else {
                this.searchResults = [
                    { id: 401, username: query, display_name: `${query} Player`, avatar: "🎯", is_online: true, total_stars: 12, is_friend: false, has_pending_request: false }
                ];
            }
            this.renderList();
        } catch (e) {
            console.warn("Search failed:", e);
        }
    }

    renderList() {
        if (!this.listElem || !this.socialData) return;

        if (this.searchResults !== null) {
            this.renderSearchResults();
            return;
        }

        let items = [];
        if (this.currentTab === 'friends') items = this.socialData.friends;
        else if (this.currentTab === 'requests') items = this.socialData.pending_requests;
        else if (this.currentTab === 'recent') items = this.socialData.recently_played;

        if (items.length === 0) {
            this.listElem.innerHTML = `<div class="friends-empty">No ${this.currentTab} found.</div>`;
            return;
        }

        if (this.currentTab === 'requests') {
            this.listElem.innerHTML = items.map(req => `
                <div class="friend-card">
                    <div class="friend-avatar">${req.sender.avatar}</div>
                    <div class="friend-details">
                        <h4 class="friend-name">${req.sender.display_name}</h4>
                        <span class="friend-username">@${req.sender.username}</span>
                    </div>
                    <div class="friend-actions">
                        <button class="primary-btn success-btn accept-req-btn" data-id="${req.request_id}">Accept</button>
                        <button class="danger-btn reject-req-btn" data-id="${req.request_id}">Reject</button>
                    </div>
                </div>
            `).join('');

            this.bindRequestButtons();
            return;
        }

        this.listElem.innerHTML = items.map(p => `
            <div class="friend-card">
                <div class="friend-avatar-wrap">
                    <span class="friend-avatar">${p.avatar}</span>
                    <span class="status-dot ${p.is_online ? 'online' : 'offline'}"></span>
                </div>
                <div class="friend-details">
                    <h4 class="friend-name">${p.display_name} <span class="status-text">${p.is_online ? 'Online' : 'Offline'}</span></h4>
                    <span class="friend-stats">⭐ ${p.total_stars} Stars | 🗺️ ${p.completed_levels || 0} Levels</span>
                </div>
                <div class="friend-actions">
                    <button class="secondary-btn challenge-btn" data-id="${p.id}">⚔️ Challenge</button>
                    <button class="icon-btn profile-btn" data-id="${p.id}" title="View Profile">👤</button>
                    ${this.currentTab === 'friends' ? `<button class="icon-btn danger-icon-btn remove-friend-btn" data-id="${p.id}" title="Remove Friend">🗑️</button>` : ''}
                    ${this.currentTab === 'recent' ? `<button class="primary-btn add-friend-btn" data-id="${p.id}">➕ Add</button>` : ''}
                </div>
            </div>
        `).join('');

        this.bindFriendButtons();
    }

    renderSearchResults() {
        if (this.searchResults.length === 0) {
            this.listElem.innerHTML = `<div class="friends-empty">No players found matching search.</div>`;
            return;
        }

        this.listElem.innerHTML = this.searchResults.map(p => `
            <div class="friend-card">
                <div class="friend-avatar-wrap">
                    <span class="friend-avatar">${p.avatar}</span>
                    <span class="status-dot ${p.is_online ? 'online' : 'offline'}"></span>
                </div>
                <div class="friend-details">
                    <h4 class="friend-name">${p.display_name}</h4>
                    <span class="friend-username">@${p.username} | ⭐ ${p.total_stars}</span>
                </div>
                <div class="friend-actions">
                    ${p.is_friend ? `<span class="friend-badge">Friend</span>` : 
                      (p.has_pending_request ? `<span class="pending-badge">Pending</span>` : 
                      `<button class="primary-btn add-friend-btn" data-id="${p.id}">➕ Add Friend</button>`)}
                </div>
            </div>
        `).join('');

        this.bindFriendButtons();
    }

    bindRequestButtons() {
        this.listElem.querySelectorAll('.accept-req-btn').forEach(btn => {
            btn.onclick = async () => {
                const reqId = parseInt(btn.getAttribute('data-id'));
                try {
                    if (localStorage.getItem("access_token")) {
                        await api.acceptFriendRequest(reqId);
                    }
                    alert("Friend request accepted!");
                    await this.fetchData();
                } catch (e) {
                    alert(e.message || "Failed to accept request.");
                }
            };
        });

        this.listElem.querySelectorAll('.reject-req-btn').forEach(btn => {
            btn.onclick = async () => {
                const reqId = parseInt(btn.getAttribute('data-id'));
                try {
                    if (localStorage.getItem("access_token")) {
                        await api.rejectFriendRequest(reqId);
                    }
                    alert("Friend request rejected.");
                    await this.fetchData();
                } catch (e) {
                    alert(e.message || "Failed to reject request.");
                }
            };
        });
    }

    bindFriendButtons() {
        this.listElem.querySelectorAll('.add-friend-btn').forEach(btn => {
            btn.onclick = async () => {
                const userId = parseInt(btn.getAttribute('data-id'));
                try {
                    if (localStorage.getItem("access_token")) {
                        await api.sendFriendRequest(userId);
                    }
                    alert("Friend request sent!");
                    await this.fetchData();
                } catch (e) {
                    alert(e.message || "Failed to send friend request.");
                }
            };
        });

        this.listElem.querySelectorAll('.challenge-btn').forEach(btn => {
            btn.onclick = async () => {
                const userId = parseInt(btn.getAttribute('data-id'));
                try {
                    if (localStorage.getItem("access_token")) {
                        await api.challengeFriend(userId, 1);
                    }
                    alert("Challenge sent! Your friend will receive your target score alert.");
                } catch (e) {
                    alert(e.message || "Failed to send challenge.");
                }
            };
        });

        this.listElem.querySelectorAll('.profile-btn').forEach(btn => {
            btn.onclick = async () => {
                const userId = parseInt(btn.getAttribute('data-id'));
                await this.showFriendProfile(userId);
            };
        });

        this.listElem.querySelectorAll('.remove-friend-btn').forEach(btn => {
            btn.onclick = async () => {
                const userId = parseInt(btn.getAttribute('data-id'));
                if (!confirm("Are you sure you want to remove this friend?")) return;
                try {
                    if (localStorage.getItem("access_token")) {
                        await api.removeFriend(userId);
                    }
                    await this.fetchData();
                } catch (e) {
                    alert(e.message || "Failed to remove friend.");
                }
            };
        });
    }

    async showFriendProfile(userId) {
        if (!this.profileModal) return;
        try {
            let prof = null;
            if (localStorage.getItem("access_token")) {
                prof = await api.getFriendProfile(userId);
            } else {
                prof = {
                    display_name: "Speedy Arrow",
                    username: "SpeedyArrow",
                    avatar: "🏹",
                    country: "USA",
                    total_stars: 45,
                    total_coins: 1250,
                    completed_levels: 15,
                    highest_level: 16,
                    best_score: 9800,
                    date_joined: "2026-08-01"
                };
            }

            document.getElementById('fp-avatar').innerText = prof.avatar;
            document.getElementById('fp-name').innerText = prof.display_name;
            document.getElementById('fp-username').innerText = `@${prof.username}`;
            document.getElementById('fp-country').innerText = prof.country;
            document.getElementById('fp-stars').innerText = prof.total_stars;
            document.getElementById('fp-coins').innerText = prof.total_coins;
            document.getElementById('fp-completed').innerText = prof.completed_levels;
            document.getElementById('fp-highest').innerText = prof.highest_level;

            this.profileModal.classList.add('active');

        } catch (e) {
            alert(e.message || "Failed to load friend profile.");
        }
    }
}
