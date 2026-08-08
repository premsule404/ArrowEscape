import { api } from '../api/client.js';
import { cloudSave } from '../services/cloud_save.js';
import { playerState } from '../services/player_state.js';

export class AuthScreens {
    constructor(onAuthSuccessCallback) {
        this.onAuthSuccess = onAuthSuccessCallback;
        
        this.loginModal = document.getElementById('login-modal');
        this.registerModal = document.getElementById('register-modal');
        this.upgradeModal = document.getElementById('upgrade-modal');
        this.profileModal = document.getElementById('profile-modal');
        
        this.loginErrorElem = document.getElementById('login-error');
        this.registerErrorElem = document.getElementById('register-error');
        this.profileErrorElem = document.getElementById('profile-error');
        
        this.currentAvatar = "🎯";
        this.bindEvents();
    }

    validateEmail(email) {
        if (!email) return true;
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    validatePassword(password) {
        return password && password.length >= 6;
    }

    showLoginError(msg) {
        if (this.loginErrorElem) {
            this.loginErrorElem.innerText = msg;
            this.loginErrorElem.classList.remove('hidden');
        }
    }

    showRegisterError(msg) {
        if (this.registerErrorElem) {
            this.registerErrorElem.innerText = msg;
            this.registerErrorElem.classList.remove('hidden');
        }
    }

    showProfileError(msg) {
        if (this.profileErrorElem) {
            this.profileErrorElem.innerText = msg;
            this.profileErrorElem.classList.remove('hidden');
        }
    }

    clearErrors() {
        if (this.loginErrorElem) {
            this.loginErrorElem.innerText = '';
            this.loginErrorElem.classList.add('hidden');
        }
        if (this.registerErrorElem) {
            this.registerErrorElem.innerText = '';
            this.registerErrorElem.classList.add('hidden');
        }
        if (this.profileErrorElem) {
            this.profileErrorElem.innerText = '';
            this.profileErrorElem.classList.add('hidden');
        }
    }

    bindEvents() {
        // Open Login / Profile Modal
        const btnOpenLogin = document.getElementById('btn-open-login');
        if (btnOpenLogin) btnOpenLogin.onclick = async () => {
            if (localStorage.getItem("access_token")) {
                await this.loadAndShowProfile();
            } else {
                this.showLogin();
            }
        };
        
        // Switch to Register
        const btnSwitchRegister = document.getElementById('btn-switch-register');
        if (btnSwitchRegister) btnSwitchRegister.onclick = (e) => {
            e.preventDefault();
            this.showRegister();
        };
        
        // Switch to Login
        const btnSwitchLogin = document.getElementById('btn-switch-login');
        if (btnSwitchLogin) btnSwitchLogin.onclick = (e) => {
            e.preventDefault();
            this.showLogin();
        };
        
        // Close Buttons for Auth Modals
        if (this.loginModal) {
            const btnClose = this.loginModal.querySelector('.close-btn');
            if (btnClose) btnClose.onclick = () => this.hideAll();
        }
        if (this.registerModal) {
            const btnClose = this.registerModal.querySelector('.close-btn');
            if (btnClose) btnClose.onclick = () => this.hideAll();
        }
        if (this.upgradeModal) {
            const btnClose = this.upgradeModal.querySelector('.close-btn');
            if (btnClose) btnClose.onclick = () => this.hideAll();
        }
        if (this.profileModal) {
            const btnClose = this.profileModal.querySelector('.close-btn');
            if (btnClose) btnClose.onclick = () => this.hideAll();
        }
        
        // Login Submit
        const formLogin = document.getElementById('form-login');
        if (formLogin) {
            formLogin.onsubmit = async (e) => {
                e.preventDefault();
                this.clearErrors();
                const u = document.getElementById('login-username').value.trim();
                const p = document.getElementById('login-password').value;
                
                if (!u) return this.showLoginError("Username is required.");
                if (!p) return this.showLoginError("Password is required.");

                try {
                    cloudSave.resetToDefaults();
                    const res = await api.login(u, p);
                    this.hideAll();
                    if (this.onAuthSuccess) await this.onAuthSuccess(res);
                } catch (err) {
                    this.showLoginError(err.message || "Invalid username or password.");
                }
            };
        }

        // Register Submit
        const formRegister = document.getElementById('form-register');
        if (formRegister) {
            formRegister.onsubmit = async (e) => {
                e.preventDefault();
                this.clearErrors();
                const u = document.getElementById('reg-username').value.trim();
                const em = document.getElementById('reg-email').value.trim();
                const p = document.getElementById('reg-password').value;
                
                if (!u) return this.showRegisterError("Username is required.");
                if (em && !this.validateEmail(em)) return this.showRegisterError("Please enter a valid email address.");
                if (!this.validatePassword(p)) return this.showRegisterError("Password must be at least 6 characters long.");

                try {
                    cloudSave.resetToDefaults();
                    const res = await api.register(u, p, em || null);
                    this.hideAll();
                    if (this.onAuthSuccess) await this.onAuthSuccess(res);
                } catch (err) {
                    this.showRegisterError(err.message || "Registration failed.");
                }
            };
        }
        
        // Guest Login Submit
        const btnGuestLogin = document.getElementById('btn-guest-login');
        if (btnGuestLogin) {
            btnGuestLogin.onclick = async () => {
                this.clearErrors();
                try {
                    cloudSave.resetToDefaults();
                    const res = await api.guestLogin();
                    this.hideAll();
                    if (this.onAuthSuccess) await this.onAuthSuccess(res);
                } catch (err) {
                    this.showLoginError(err.message || "Guest login failed.");
                }
            };
        }

        // Avatar Selection
        document.querySelectorAll('.avatar-opt').forEach(btn => {
            btn.onclick = async () => {
                document.querySelectorAll('.avatar-opt').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const avatar = btn.getAttribute('data-avatar');
                this.currentAvatar = avatar;
                const avatarDisplay = document.getElementById('prof-avatar-display');
                if (avatarDisplay) avatarDisplay.innerText = avatar;

                try {
                    if (localStorage.getItem("access_token")) {
                        await api.updateProfile({ avatar });
                    }
                    playerState.update({ avatar });
                } catch (e) {
                    console.warn("Failed to update avatar:", e);
                }
            };
        });

        // Username Update Submit
        const formUpdateUsername = document.getElementById('form-update-username');
        if (formUpdateUsername) {
            formUpdateUsername.onsubmit = async (e) => {
                e.preventDefault();
                this.clearErrors();
                const newUsername = document.getElementById('edit-username-input').value.trim();
                if (!newUsername) return this.showProfileError("Username cannot be empty.");

                try {
                    const res = await api.updateProfile({ username: newUsername });
                    if (res && res.username) {
                        document.getElementById('prof-username').innerText = res.username;
                        playerState.update({ username: res.username });
                        alert("Username updated successfully!");
                    }
                } catch (err) {
                    this.showProfileError(err.message || "Failed to update username.");
                }
            };
        }

        // Password Change Submit
        const formChangePassword = document.getElementById('form-change-password');
        if (formChangePassword) {
            formChangePassword.onsubmit = async (e) => {
                e.preventDefault();
                this.clearErrors();
                const oldPass = document.getElementById('old-pass-input').value;
                const newPass = document.getElementById('new-pass-input').value;

                if (!oldPass) return this.showProfileError("Current password is required.");
                if (!this.validatePassword(newPass)) return this.showProfileError("New password must be at least 6 characters.");

                try {
                    await api.changePassword(oldPass, newPass);
                    formChangePassword.reset();
                    alert("Password changed successfully!");
                } catch (err) {
                    this.showProfileError(err.message || "Failed to change password.");
                }
            };
        }

        // Logout
        const btnLogout = document.getElementById('btn-logout');
        if (btnLogout) {
            btnLogout.onclick = async () => {
                try {
                    await api.logout();
                } catch (e) {}
                cloudSave.resetToDefaults();
                this.hideAll();
                if (window.navManager) {
                    window.navManager.showWelcomeScreen();
                }
                alert("Logged out successfully.");
            };
        }

        // Delete Account
        const btnDeleteAccount = document.getElementById('btn-delete-account');
        if (btnDeleteAccount) {
            btnDeleteAccount.onclick = async () => {
                if (confirm("⚠️ Are you sure you want to permanently delete your account and all saved progress? This action cannot be undone!")) {
                    try {
                        await api.deleteAccount();
                        this.hideAll();
                        alert("Your account has been deleted.");
                    } catch (err) {
                        this.showProfileError(err.message || "Failed to delete account.");
                    }
                }
            };
        }
    }

    hideAll() {
        this.clearErrors();
        if (this.loginModal) this.loginModal.classList.remove('active');
        if (this.registerModal) this.registerModal.classList.remove('active');
        if (this.upgradeModal) this.upgradeModal.classList.remove('active');
        if (this.profileModal) this.profileModal.classList.remove('active');
    }

    showLogin() {
        this.hideAll();
        if (this.loginModal) this.loginModal.classList.add('active');
    }

    showRegister() {
        this.hideAll();
        if (this.registerModal) this.registerModal.classList.add('active');
    }

    async loadAndShowProfile() {
        this.hideAll();
        try {
            const data = await api.getProfile();
            playerState.syncFromCloudUser(data);
            this.populateProfileData(data);
            if (this.profileModal) this.profileModal.classList.add('active');
        } catch (e) {
            // Fallback to centralized playerState stats if offline / guest
            const state = playerState.state;
            const completedCount = state.completed_count || Object.keys(state.completed_levels || {}).length;
            const pct = Math.round((completedCount / 50) * 100);

            this.populateProfileData({
                username: state.username || "Local Guest",
                email: state.email || "N/A",
                is_guest: state.is_guest,
                avatar: state.avatar || "🎯",
                total_coins: state.total_coins || 0,
                total_stars: state.total_stars || 0,
                current_level: state.current_level || 1,
                highest_level: state.highest_level || state.current_level || 1,
                games_played: completedCount,
                games_won: completedCount,
                completion_pct: pct,
                best_time: 0,
                best_score: 0,
                date_joined: "Offline",
                last_login: "Just Now"
            });
            if (this.profileModal) this.profileModal.classList.add('active');
        }
    }

    populateProfileData(d) {
        document.getElementById('prof-avatar-display').innerText = d.avatar || "🎯";
        document.getElementById('prof-username').innerText = d.username || "Player";
        document.getElementById('prof-email').innerText = d.email || "N/A";
        document.getElementById('prof-type').innerText = d.is_guest ? 'Guest Account ⚠️' : 'Verified Account ✅';
        
        document.getElementById('edit-username-input').value = d.username || "";
        
        document.getElementById('prof-coins').innerText = d.total_coins || 0;
        document.getElementById('prof-stars').innerText = d.total_stars || 0;
        document.getElementById('prof-cur-lvl').innerText = d.current_level || 1;
        document.getElementById('prof-high-lvl').innerText = d.highest_level || 1;
        document.getElementById('prof-played').innerText = d.games_played || 0;
        document.getElementById('prof-won').innerText = d.games_won || 0;
        document.getElementById('prof-pct').innerText = `${d.completion_pct || 0}%`;
        document.getElementById('prof-time').innerText = `${d.best_time || 0}s`;
        document.getElementById('prof-score').innerText = d.best_score || 0;
        document.getElementById('prof-joined').innerText = d.date_joined || "N/A";
        document.getElementById('prof-last-login').innerText = d.last_login || "N/A";

        // Highlight selected avatar button
        document.querySelectorAll('.avatar-opt').forEach(b => {
            if (b.getAttribute('data-avatar') === (d.avatar || "🎯")) {
                b.classList.add('active');
            } else {
                b.classList.remove('active');
            }
        });
    }

    showProfile(userData) {
        this.loadAndShowProfile();
    }
}
