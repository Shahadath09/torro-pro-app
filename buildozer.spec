[app]
title = Torro Pro
package.name = torropro
package.domain = org.torro

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json

version = 1.0.0
requirements = python3,kivy,yt-dlp,requests,pillow,urllib3,certifi

[buildozer]
log_level = 2

[android]
api = 33
minapi = 21
ndk = 25b
sdk = 33

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

# Bootstrap
android.bootstrap = sdl2

# Architecture
android.arch = arm64-v8a

# Preserve .py files
android.no-compile-pyo = True

# App features
android.allow_backup = True
android.adaptive_icon_foreground = True

# Presplash (comment out if no image)
# presplash.filename = %(source.dir)s/assets/presplash.png

# Icon (comment out if no image)
# icon.filename = %(source.dir)s/assets/icon.png

# Build options
android.accept_sdk_license = True

[buildozer.android]
sdkmanager_path = /home/runner/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager