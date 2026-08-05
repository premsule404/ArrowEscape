import { api } from '../api/client.js';

export class AuthScreens {
    constructor(onAuthSuccessCallback) {
        this.onAuthSuccess = onAuthSuccessCallback;
        
        this.loginModal = document.getElementById('login-modal');
        this.registerModal = document.getElementById('register-modal');
        this.upgradeModal = document.getElementById('upgrade-modal');
        this.profileModal = document.getElementById('profile-modal');
        
        this.bindEvents();
    }

    bindEvents() {
        // Open Login Modal
        const btnOpenLogin = document.getElementById('btn-open-login');
        if (btnOpenLogin) btnOpenLogin.onclick = () => this.showLogin();
        
        // Switch to Register
        const btnSwitchRegister = document.getElementById('btn-switch-register');
        if (btnSwitchRegister) btnSwitchRegister.onclick = () => this.showRegister();
        
        // Switch to Login
        const btnSwitchLogin = document.getElementById('btn-switch-login');
        if (btnSwitchLogin) btnSwitchLogin.onclick = () => this.showLogin();
        
        // Close Buttons
        document.querySelectorAll('.auth-close-btn').forEach(btn => {
            btn.onclick = () => this.hideAll();
        });
        
        // Login Submit
        const formLogin = document.getElementById('form-login');
        if (formLogin) {
            formLogin.onsubmit = async (e) => {
                e.preventDefault();
                const u = document.getElementById('login-username').value;
                const p = document.getElementById('login-password').value;
                try {
                    const res = await api.login(u, p);
                    this.hideAll();
                    if (this.onAuthSuccess) this.onAuthSuccess(res);
                } catch (err) {
                    alert(err.message || "Login failed.");
                }
            };
        }

        // Register Submit
        const formRegister = document.getElementById('form-register');
        if (formRegister) {
            formRegister.onsubmit = async (e) => {
                e.preventDefault();
                const u = document.getElementById('reg-username').value;
                const p = document.getElementById('reg-password').value;
                const em = document.getElementById('reg-email').value;
                try {
                    const res = await api.register(u, p, em);
                    this.hideAll();
                    if (this.onAuthSuccess) this.onAuthSuccess(res);
                } catch (err) {
                    alert(err.message || "Registration failed.");
                }
            };
        }
        
        // Guest Login Submit
        const btnGuestLogin = document.getElementById('btn-guest-login');
        if (btnGuestLogin) {
            btnGuestLogin.onclick = async () => {
                try {
                    const res = await api.guestLogin();
                    this.hideAll();
                    if (this.onAuthSuccess) this.onAuthSuccess(res);
                } catch (err) {
                    alert(err.message || "Guest login failed.");
                }
            };
        }
    }

    hideAll() {
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

    showProfile(userData) {
        this.hideAll();
        if (this.profileModal) {
            document.getElementById('prof-username').innerText = userData.username || 'Player';
            document.getElementById('prof-type').innerText = userData.is_guest ? 'Guest Account ⚠️' : 'Verified Account ✅';
            this.profileModal.classList.add('active');
        }
    }
}
