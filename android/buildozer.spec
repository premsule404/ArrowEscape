[app]

# (str) Title of your application
title = Arrow Escape

# (str) Package name
package.name = arrowescape

# (str) Package domain (needed for android/ios packaging)
package.domain = com.arrowescape

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,md

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,requests,urllib3

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait,landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) List of Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a, x86_64

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) Adaptive icon background/foreground
# android.adaptive_icon.background = %(source.dir)s/assets/icon_bg.png
# android.adaptive_icon.foreground = %(source.dir)s/assets/icon_fg.png

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = error, 1 = warning)
warn_on_root = 1
