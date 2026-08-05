# Arrow Escape Android Production Build & Installation Guide

Technical build report, sideloading instructions, and Google Play Store submission checklist for **Arrow Escape**.

---

## 📱 1. Production Artifacts & Build Deliverables

All generated Android binaries are located in `android/bin/`:

1. **`ArrowEscape-Debug.apk`**: Unsigned debug package for developer testing and emulator validation.
2. **`ArrowEscape-Release.apk`**: Signed & optimized APK ready to share directly with friends via **WhatsApp, Telegram, Google Drive, or Dropbox**!
3. **`ArrowEscape.aab`**: Signed Android App Bundle (.aab) ready for **Google Play Console** submission.

---

## 🔑 2. Release Signing Fingerprints

- **SHA-1 Fingerprint**:
  `99E84CF7904750983BF2D466B921E3596E6F7711`
- **SHA-256 Fingerprint**:
  `BB1E5A3230CFF6ED36A1D4E21BBB8A134A93DEFFF664DA1E6AFAA8F116BB11AB`

---

## 📤 3. How to Share & Install the APK on Android Phones

### Option A: Upload to Google Drive / Telegram / WhatsApp
1. Copy `android/bin/ArrowEscape-Release.apk` to your Google Drive or send it in Telegram/WhatsApp.
2. Share the file or download link with your friends.

### Option B: Sideloading Installation Steps for Friends
1. On your Android phone, download `ArrowEscape-Release.apk`.
2. Tap the downloaded file.
3. If prompted: **"For your security, your phone is not allowed to install unknown apps from this source"**:
   - Tap **Settings** $\rightarrow$ Enable **"Allow from this source"**.
4. Tap **Install** $\rightarrow$ Open **Arrow Escape** and start playing!

---

## 🏬 4. Google Play Console Submission Checklist

1. **Google Play Console**: Log in to [play.google.com/console](https://play.google.com/console).
2. **Upload App Bundle**: Drag and drop `android/bin/ArrowEscape.aab` into Production or Internal Testing.
3. **Target Android Versions**: Supports Android 5.0 (API 21) through Android 14/15 (API 33/34).
4. **Permissions**: `INTERNET`, `ACCESS_NETWORK_STATE`.
