[app]
title = Torro Pro
package.name = torropro
package.domain = org.torro

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json

version = 1.0.0
requirements = python3,kivy==2.3.0,yt-dlp==2023.11.16,requests==2.31.0,pillow==10.0.1,urllib3==2.0.7,certifi==2023.7.22

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

# Skip problematic modules
android.skip_grp_module = True

# Build options
android.accept_sdk_license = True