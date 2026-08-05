# Arrow Escape Cross-Platform Release & Store Submission Guide

Comprehensive release guide for deploying **Arrow Escape** to Google Play, Microsoft Store, Mac App Store, Web PWA, and Desktop installers.

---

## 📱 1. Android Release (Google Play)

1. **Build Production Assets**:
   ```bash
   python package_all.py
   ```
2. **Build Android App Bundle (.aab)**:
   ```bash
   cd android
   ./gradlew bundleRelease
   ```
3. **Upload to Google Play Console**:
   - Upload `.aab` to Production track.
   - Complete Store Listing (Screenshots: 1080x1920 portrait & 1920x1080 landscape, Feature Graphic: 1024x500).
   - Set Content Rating & Privacy Policy URL.

---

## 💻 2. Desktop Release (Windows, Linux, macOS)

1. **Install Electron Builder**:
   ```bash
   cd electron
   npm install
   ```
2. **Build Windows Installer (.exe)**:
   ```bash
   npm run build:win
   ```
3. **Build Linux Installer (.AppImage / .deb)**:
   ```bash
   npm run build:linux
   ```
4. **Build macOS Bundle (.dmg)**:
   ```bash
   npm run build:mac
   ```

---

## 🌐 3. Progressive Web App (PWA) Release

1. **Deploy Frontend Directory**: Deploy `frontend/` to Vercel, Netlify, or AWS CloudFront.
2. **Offline Verification**:
   - Open DevTools $\rightarrow$ Application $\rightarrow$ Service Workers.
   - Verify `sw.js` is active and pre-cached assets are stored.
   - Test "Add to Home Screen" installation on mobile devices.

---

## 🤖 4. CI/CD GitHub Actions Pipeline

The `.github/workflows/build.yml` pipeline automatically triggers on push to `main`:
1. Executes `pytest` test suite (45+ unit/integration/load tests).
2. Executes `python package_all.py` pipeline.
3. Uploads web PWA build artifacts to GitHub Actions release storage.
