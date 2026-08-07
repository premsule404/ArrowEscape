import { api } from '../api/client.js';

export class NotificationSystem {
    constructor() {
        this.modal = document.getElementById('notifications-modal');
        this.btnClose = document.getElementById('btn-close-notifications');
        this.btnBell = document.getElementById('btn-notifications');
        this.badgeElem = document.getElementById('notif-badge');
        this.listElem = document.getElementById('notifications-list');
        this.btnMarkAll = document.getElementById('btn-mark-all-read');
        this.btnClearAll = document.getElementById('btn-clear-notifications');
        this.tabsElem = document.getElementById('notifications-tabs');
        this.toastStack = document.getElementById('toast-stack');

        this.currentFilter = 'all';
        this.notifications = [];
        this.unreadCount = 0;
        
        this.bindEvents();
        this.initDefaultNotifications();
    }

    bindEvents() {
        if (this.btnBell) {
            this.btnBell.onclick = () => this.toggle();
        }

        if (this.btnClose) {
            this.btnClose.onclick = () => this.hide();
        }

        if (this.btnMarkAll) {
            this.btnMarkAll.onclick = async () => {
                try {
                    if (localStorage.getItem("access_token")) {
                        await api.markAllNotificationsRead();
                    }
                    this.notifications.forEach(n => n.read = true);
                    this.unreadCount = 0;
                    this.updateBadge();
                    this.renderList();
                } catch (e) {
                    console.warn("Failed to mark all read:", e);
                }
            };
        }

        if (this.btnClearAll) {
            this.btnClearAll.onclick = async () => {
                try {
                    if (localStorage.getItem("access_token")) {
                        await api.clearNotifications();
                    }
                    this.notifications = [];
                    this.unreadCount = 0;
                    this.updateBadge();
                    this.renderList();
                } catch (e) {
                    console.warn("Failed to clear notifications:", e);
                }
            };
        }

        if (this.tabsElem) {
            this.tabsElem.querySelectorAll('.tab-btn').forEach(btn => {
                btn.onclick = () => {
                    this.tabsElem.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    this.currentFilter = btn.getAttribute('data-filter');
                    this.renderList();
                };
            });
        }

        // Hotkey 'N' to open Notification Center
        window.addEventListener('keydown', (e) => {
            if ((e.key === 'n' || e.key === 'N') && !e.target.matches('input, textarea')) {
                this.toggle();
            }
        });
    }

    initDefaultNotifications() {
        // Initial sample notifications
        this.notifications = [
            { id: 1, type: "daily", title: "Daily Reward Available!", content: "Claim your Day 1 reward now to earn 50 Coins!", icon: "🎁", read: false, created_at: "Just now" },
            { id: 2, type: "achievement", title: "Achievement Unlocked!", content: "Unlocked 'First Win' for completing Level 1", icon: "🏆", read: false, created_at: "5m ago" },
            { id: 3, type: "cloud", title: "Cloud Sync Complete", content: "Your local progress has been synchronized to the cloud.", icon: "☁️", read: true, created_at: "10m ago" }
        ];
        this.unreadCount = 2;
        this.updateBadge();
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
        try {
            if (localStorage.getItem("access_token")) {
                const res = await api.getNotifications();
                this.notifications = res.notifications;
                this.unreadCount = res.unread_count;
            }
            this.updateBadge();
            this.renderList();
        } catch (e) {
            console.warn("Failed to fetch notifications:", e);
        }
    }

    updateBadge() {
        if (!this.badgeElem) return;
        if (this.unreadCount > 0) {
            this.badgeElem.innerText = this.unreadCount > 99 ? '99+' : this.unreadCount;
            this.badgeElem.classList.remove('hidden');
        } else {
            this.badgeElem.classList.add('hidden');
        }
    }

    renderList() {
        if (!this.listElem) return;

        let filtered = this.notifications;
        if (this.currentFilter === 'unread') {
            filtered = this.notifications.filter(n => !n.read);
        }

        if (filtered.length === 0) {
            this.listElem.innerHTML = `<div class="notif-empty">No ${this.currentFilter} notifications.</div>`;
            return;
        }

        this.listElem.innerHTML = filtered.map(n => `
            <div class="notif-card ${n.read ? 'read' : 'unread'}">
                <div class="notif-icon">${n.icon}</div>
                <div class="notif-details">
                    <div class="notif-header-row">
                        <h4 class="notif-title">${n.title}</h4>
                        <span class="notif-time">${n.created_at || ''}</span>
                    </div>
                    <p class="notif-content">${n.content}</p>
                </div>
                ${!n.read ? `<button class="icon-btn notif-read-btn" data-id="${n.id}" title="Mark as read">✓</button>` : ''}
            </div>
        `).join('');

        this.listElem.querySelectorAll('.notif-read-btn').forEach(btn => {
            btn.onclick = async () => {
                const id = parseInt(btn.getAttribute('data-id'));
                await this.markRead(id);
            };
        });
    }

    async markRead(id) {
        try {
            if (localStorage.getItem("access_token")) {
                await api.markNotificationRead(id);
            }
            const item = this.notifications.find(n => n.id === id);
            if (item) item.read = true;
            this.unreadCount = Math.max(0, this.unreadCount - 1);
            this.updateBadge();
            this.renderList();
        } catch (e) {
            console.warn("Failed to mark read:", e);
        }
    }

    notify(title, content, type = "system", icon = "🔔") {
        const notifItem = {
            id: Date.now(),
            type,
            title,
            content,
            icon,
            read: false,
            created_at: "Just now"
        };

        this.notifications.unshift(notifItem);
        this.unreadCount++;
        this.updateBadge();

        // Spawn Toast
        this.spawnToast(title, content, icon, type);
    }

    spawnToast(title, content, icon = "🔔", type = "system") {
        if (!this.toastStack) {
            this.toastStack = document.createElement('div');
            this.toastStack.id = 'toast-stack';
            this.toastStack.className = 'toast-stack';
            document.body.appendChild(this.toastStack);
        }

        const toast = document.createElement('div');
        toast.className = `toast-banner toast-${type}`;
        toast.innerHTML = `
            <div class="toast-banner-icon">${icon}</div>
            <div class="toast-banner-content">
                <h4 class="toast-banner-title">${title}</h4>
                <p class="toast-banner-desc">${content}</p>
            </div>
        `;

        this.toastStack.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }
}
