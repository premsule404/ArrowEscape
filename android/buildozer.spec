[app]

# (str) Title of your application
title = Arrow Escape

# (str) Package name
package.name = arrowescape

# (str) Package domain (needed for android/ios packaging)
package.domain = com.arrowescape.app

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,md,html,css,js

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy,requests,urllib3

# (str) Supported orientation: force portrait mode
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (int) Target Android API (Android 14 / API 34)
android.api = 34

# (int) Minimum API your APK will support: Android 10+ (API 29+)
android.minapi = 29

# (str) Android NDK version to use
android.ndk = 25b

# (list) List of Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a, x86_64

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) Preserved icon & splash screen
icon.filename = %(source.dir)s/../frontend/assets/icons/icon-512.png
presplash.filename = %(source.dir)s/../frontend/assets/icons/icon-512.png

# (list) Deep links & intent filters
android.manifest.intent_filters = arrowescape://, https://arrowescape.onrender.com/invite

[buildozer]
log_level = 2
warn_on_root = 1
