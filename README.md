# Arrow Escape 🏹

A cross-platform 3D directional arrow unblocking puzzle game built for Web (PWA), Mobile (Android & iOS), Desktop (Windows, macOS, Linux), and Cloud.

---

## 🌟 Key Features

- **Directional Unblock Gameplay**: Slide, rotate, and release 3D arrows off the board in 100+ procedural and hand-crafted levels.
- **Cross-Platform Synchronization**: Instant cloud save progress sync across Web PWA, Android APK/AAB, Electron Desktop, and iOS Safari.
- **JWT Authentication & Guest Play**: Support for secure account registration, password validation, guest play, and session token auto-refresh.
- **Cloud Save Engine**: Synchronizes completed levels, stars, coins, boosters, themes, and personal records automatically.
- **Global & Social Leaderboards**: Filter by All-Time, Monthly, Weekly, Country, and Friends scopes with instant user ranking highlights.
- **Achievements System**: 10+ unlockable achievements with animated toasts, star rewards, and progress bars.
- **Daily Rewards & Streaks**: 7-day streak rewards with weekly/monthly bonuses and live countdown timers.
- **In-Game Shop & Inventory**: Purchase and equip arrow skins, board themes (Cyberpunk, Emerald, Sunset), booster undo packs, and hint packs.
- **Friends & Social Network**: Player search, friend request send/accept/reject, online status indicators, shareable invite links, level score challenges, and friend profile lookups.
- **Notification System & Center**: Floating toast banners, top bar unread count badge, and a filterable Notification Center drawer.
- **Statistics Analytics Dashboard**: 12 performance metric cards and responsive Daily (7-day) & Weekly (4-week) activity bar charts.
- **Offline Mode & PWA Support**: Pre-cached Pyodide WASM runtime and level fallback for offline play anywhere.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System, Glassmorphic UI), JavaScript (ES Modules), Pyodide WebAssembly.
- **Mobile**: Capacitor & Kivy (Android 10+ / API 29+ minimum, API 34 target).
- **Desktop**: Electron & Electron-Builder.
- **Backend API**: FastAPI (Python 3.10+), SQLAlchemy, SQLite/PostgreSQL, GZip Compression, Security Headers.
- **Production Server**: Render (`https://arrowescape.onrender.com`).

---

## 🚀 Quick Start

### 1. Web Local Server
```bash
python build.py
python -m http.server 8080 --directory frontend
```
Open `http://127.0.0.1:8080/index.html` in your browser.

### 2. Backend Server
```bash
uvicorn backend.app.main:app --reload --port 8000
```
Interactive OpenAPI docs available at `http://127.0.0.1:8000/docs`.

### 3. Run Automated Tests
```bash
pytest
```

### 4. Cross-Platform Packaging Pipeline
```bash
python package_all.py
python build_android.py
```

---

## 📄 License
MIT License. Developed for Arrow Escape.
