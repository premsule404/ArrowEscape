import { api } from '../api/client.js';

export class AuthScreens {
    constructor(onAuthSuccessCallback) {
        this.onAuthSuccess = onAuthSuccessCallback;
        
        this.loginModal = document.getElementById('login-modal');
        this.registerModal = document.getElementById('register-modal');
        this.upgradeModal = document.getElementById('upgrade-modal');
        this.profileModal = document.getElementById('profile-modal');
        
        this.loginErrorElem = document.getElementById('login-error');
        this.registerErrorElem = document.getElementById('register-error');
        
        this.bindEvents();
    }

    validateEmail(email) {
        if (!email) return true; // Email is optional
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

    clearErrors() {
        if (this.loginErrorElem) {
            this.loginErrorElem.innerText = '';
            this.loginErrorElem.classList.add('hidden');
        }
        if (this.registerErrorElem) {
            this.registerErrorElem.innerText = '';
            this.registerErrorElem.classList.add('hidden');
        }
    }

    bindEvents() {
        // Open Login Modal
        const btnOpenLogin = document.getElementById('btn-open-login');
        if (btnOpenLogin) btnOpenLogin.onclick = async () => {
            if (localStorage.getItem("access_token")) {
                try {
                    const userData = await api.getMe();
                    this.showProfile(userData);
                } catch (e) {
                    this.showLogin();
                }
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
        
        // Close Buttons
        document.querySelectorAll('.auth-close-btn').forEach(btn => {
            btn.onclick = () => this.hideAll();
        });
        
        // Login Submit
        const formLogin = document.getElementById('form-login');
        if (formLogin) {
            formLogin.onsubmit = async (e) => {
                e.preventDefault();
                this.clearErrors();
                const u = document.getElementById('login-username').value.trim();
                const p = document.getElementById('login-password').value;
                
                if (!u) {
                    this.showLoginError("Username is required.");
                    return;
                }
                if (!p) {
                    this.showLoginError("Password is required.");
                    return;
                }

                try {
                    const res = await api.login(u, p);
                    this.hideAll();
                    if (this.onAuthSuccess) this.onAuthSuccess(res);
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
                
                if (!u) {
                    this.showRegisterError("Username is required.");
                    return;
                }
                if (em && !this.validateEmail(em)) {
                    this.showRegisterError("Please enter a valid email address.");
                    return;
                }
                if (!this.validatePassword(p)) {
                    this.showRegisterError("Password must be at least 6 characters long.");
                    return;
                }

                try {
                    const res = await api.register(u, p, em || null);
                    this.hideAll();
                    if (this.onAuthSuccess) this.onAuthSuccess(res);
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
                    const res = await api.guestLogin();
                    this.hideAll();
                    if (this.onAuthSuccess) this.onAuthSuccess(res);
                } catch (err) {
                    this.showLoginError(err.message || "Guest login failed.");
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

    showProfile(userData) {
        this.hideAll();
        if (this.profileModal) {
            document.getElementById('prof-username').innerText = userData.username || 'Player';
            document.getElementById('prof-type').innerText = userData.is_guest ? 'Guest Account ⚠️' : 'Verified Account ✅';
            this.profileModal.classList.add('active');
        }
    }
}
