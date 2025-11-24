# rdzwx-go

This was just some simple test code for my first Kotlin code in rdzwx-plugin. Its now a mostly usable app, not not really well-tested. Use at your own risk :)

See https://github.com/dl9rdz/rdzwx-go/wiki for details how to use.

## How to compile and run (Android)

### Prerequisites

Install the following (macOS examples using Homebrew):

```bash
# Java 17
brew install openjdk@17

# Gradle
brew install gradle

# Node.js (via nvm recommended)
brew install nvm
nvm install --lts

# Cordova CLI
npm install -g cordova

# Android Studio (for SDK management)
brew install --cask android-studio
```

### Required Environment Variables

Add these to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Java
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home

# Android SDK (adjust path if installed elsewhere)
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH="$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools"

# Ensure Homebrew binaries are in PATH (for gradle)
export PATH="$PATH:/opt/homebrew/bin"
```

### Android SDK Setup

In Android Studio > Preferences > Appearance & Behaviour > System Settings > Android SDK:

- **SDK Platforms**: Install Android 14 (API 34) or later
- **SDK Tools**: Install:
  - Android SDK Build-Tools 35.0.0
  - Android SDK Command-line Tools
  - Android SDK Platform-Tools

Or via command line:
```bash
sdkmanager "build-tools;35.0.0" "platforms;android-35"
```

### Building

```bash
cd rdzwx-go
cordova platform add android
cordova plugin add ../rdzwx-plugin/
cordova build android              # debug APK
cordova build android --release    # release APK
cordova run android --device       # deploy to connected device
```

## iOS Development (macOS only)

### Prerequisites
- macOS with Xcode installed
- Node.js and Cordova CLI
- Run `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer` to set Xcode path

### Building for iOS

```bash
cd rdzwx-go
cordova platform add ios
cordova plugin add ../rdzwx-plugin/
cordova build ios
```

To run in the simulator:
```bash
cordova run ios --emulator
```

Or manually with simctl:
```bash
xcrun simctl boot "iPhone 16 Plus"
xcrun simctl install "iPhone 16 Plus" platforms/ios/build/Debug-iphonesimulator/rdzSonde.app
xcrun simctl launch "iPhone 16 Plus" de.dl9rdz
open -a Simulator
```

### Viewing Debug Logs

Stream all app logs:
```bash
xcrun simctl spawn "iPhone 16 Plus" log stream \
  --predicate 'processImagePath contains "rdzSonde"' --level debug
```

Stream only custom app logs (less verbose):
```bash
xcrun simctl spawn "iPhone 16 Plus" log stream \
  --predicate 'subsystem contains "de.dl9rdz"' --level info
```

Key log messages to look for:
- `JsonRdzHandler: Attempting to connect to <ip>:<port>` - TCP connection attempts
- `JsonRdzHandler: Connection timeout` - No response from TTGO device
- `callback: { "msgtype": "ttgostatus", ... }` - Status updates to JS layer

