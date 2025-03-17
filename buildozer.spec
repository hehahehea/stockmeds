[app]
# Pangalan ng application at package details
title = PharmacyApp
package.name = pharmacyapp
package.domain = org.example

# Main source code directory
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Entry point ng app
entrypoint = main.py

# Target platform
target = android

# Required dependencies
requirements = python3, kivy, sqlite3, pytz, os

# Icon at presplash (siguraduhin na may files na ito sa directory mo)
icon.filename = logo.jpg
presplash.filename = loading.jpg

# Orientation ng screen
orientation = portrait

# Minimum at maximum Android API levels
android.minapi = 21
android.api = 31
android.ndk = 23b

# Permissions na kailangan ng app
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Optimize APK size (tanggalin ang debugging symbols)
android.strip_libs = True

# Gawing release-ready ang APK (baguhin sa True para sa production)
android.release = False

# Tanggalin ang console log sa production
android.logcat_filters = *:S

# Hindi isasama ang mga hindi kailangang files sa build
source.exclude_patterns = .git,__pycache__,*.pyc,*.pyo,*.swp

# Gumamit ng latest na stable version ng Kivy
p4a.fork = kivy
p4a.branch = master

# Suportadong architecture (ARM at 64-bit)
android.archs = arm64-v8a, armeabi-v7a

# Payagan ang auto backup
android.allow_backup = True
