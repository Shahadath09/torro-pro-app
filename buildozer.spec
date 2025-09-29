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

# Architecture (arm64 is better for modern devices)
android.arch = arm64-v8a

# Presplash
presplash.filename = %(source.dir)s/assets/presplash.png

# Icon
icon.filename = %(source.dir)s/assets/icon.png

# Preserve .py files for debugging
android.no-compile-pyo = True

# Extra build settings
android.allow_backup = True
android.adaptive_icon_foreground = True

# Important: Add these lines for yt-dlp compatibility
android.add_src = include
android.add_resources = include
