[app]
title = NOVA X1 Drone
package.name = novax1
package.domain = org.theagosakai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.3.1
orientation = landscape
fullscreen = 0
android.permissions = INTERNET
android.api = 35
android.minapi = 21
android.sdk = 35
android.accept_sdk_license = True
android.sdk_build_tools_versions = 35.0.0
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
