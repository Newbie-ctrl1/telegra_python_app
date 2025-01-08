[app]
title = Telegram Manager
package.name = telegrammanager
package.domain = org.telegram

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_patterns = assets/*,lib/*
source.exclude_dirs = tests, bin, venv, myenv, .buildozer

# Gunakan versi statis saja
version = 0.1.0

requirements = python3,\
    kivy==2.2.1,\
    flet==0.9.0,\
    requests==2.31.0,\
    python-dotenv==1.0.0,\
    telethon==1.29.2,\
    flask==2.3.3,\
    flask-cors==4.0.0,\
    colorama==0.4.6

# Android specific
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 23.1.7779620
android.ndk_api = 21
android.private_storage = True
android.accept_sdk_license = True
android.arch = arm64-v8a

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Orientation
orientation = portrait
fullscreen = 0

# Python for Android
p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin 