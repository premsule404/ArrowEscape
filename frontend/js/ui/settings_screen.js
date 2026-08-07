import { api } from '../api/client.js';
import { cloudSave } from '../services/cloud_save.js';

export class SettingsScreen {
    constructor() {
        this.modal = document.getElementById('settings-modal');
        this.btnClose = document.getElementById('btn-close-settings');
        this.sfxToggle = document.getElementById('setting-sfx');
        this.musicToggle = document.getElementById('setting-music');
        this.vibrateToggle = document.getElementById('setting-vibrate');
        this.themeSelect = document.getElementById('setting-theme');
        this.syncToggle = document.getElementById('setting-auto-sync');
        this.btnSave = document.getElementById('btn-save-settings');

        this.bindEvents();
        this.loadCurrentSettings();
    }

    bindEvents() {
        if (this.btnClose) {
            this.btnClose.onclick = () => this.hide();
        }

        if (this.btnSave) {
            this.btnSave.onclick = async () => {
                await this.saveSettings();
            };
        }

        if (this.themeSelect) {
            this.themeSelect.onchange = () => {
                const selected = this.themeSelect.value;
                document.body.setAttribute('data-theme', selected);
            };
        }
    }

    loadCurrentSettings() {
        const local = cloudSave.localSave.settings || {
            sound_effects: true,
            background_music: true,
            theme: "default",
            haptic_vibration: true,
            auto_cloud_sync: true
        };

        if (this.sfxToggle) this.sfxToggle.checked = local.sound_effects !== false;
        if (this.musicToggle) this.musicToggle.checked = local.background_music !== false;
        if (this.vibrateToggle) this.vibrateToggle.checked = local.haptic_vibration !== false;
        if (this.syncToggle) this.syncToggle.checked = local.auto_cloud_sync !== false;
        if (this.themeSelect) this.themeSelect.value = local.theme || "default";

        if (local.theme) {
            document.body.setAttribute('data-theme', local.theme);
        }
    }

    show() {
        this.loadCurrentSettings();
        if (this.modal) this.modal.classList.add('active');
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

    async saveSettings() {
        const settings = {
            sound_effects: this.sfxToggle ? this.sfxToggle.checked : true,
            background_music: this.musicToggle ? this.musicToggle.checked : true,
            haptic_vibration: this.vibrateToggle ? this.vibrateToggle.checked : true,
            auto_cloud_sync: this.syncToggle ? this.syncToggle.checked : true,
            theme: this.themeSelect ? this.themeSelect.value : "default"
        };

        cloudSave.localSave.settings = settings;
        cloudSave.saveLocalSave();

        if (localStorage.getItem("access_token")) {
            try {
                await api.updateSettings(settings);
                if (window.notificationSystem) {
                    window.notificationSystem.notify("Settings Saved", "Preferences updated and synced to cloud.", "system", "⚙️");
                }
            } catch (e) {
                console.warn("Failed to sync settings online:", e);
            }
        } else {
            if (window.notificationSystem) {
                window.notificationSystem.notify("Settings Saved", "Preferences updated locally.", "system", "⚙️");
            }
        }

        this.hide();
    }
}
