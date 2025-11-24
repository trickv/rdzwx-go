# rdzwx-go

This was just some simple test code for my first Kotlin code in rdzwx-plugin. Its now a mostly usable app, not not really well-tested. Use at your own risk :)

See https://github.com/dl9rdz/rdzwx-go/wiki for details how to use.

## How to compile and run

- Install Java (I used openjdk 11, gradle and android on API level 30 do not support later openjdk version) and gradle (I used version 7.4.2) (I installed both on MacOS with brew)

- Install Android Studio (currently tested with Chipmunk 2021.2.1)

     In Preferences: Appearance&Behaviour > System Settings > Android SDK
     
     SDK Platforms:  select some relevant platform (I used API level 32)
      
     SDK Tools: I selected Build-Tools, NDK, SDK command line, emulator, SKK platform tools (maybe not all necessary)
     Specifically, build tools 30.0.3 are needed!!!
      
- `export ANDROID_SDK_ROOT=/Users/me/Library/Android/sdk`

  Use path shown in Android Studio preferences as "Android SDK Location"!
  
- Install node.js (after that you should be able to run "node" and "npm" on your command line)
  (On MacOS I did 'brew install nodejs')
- Install Cordova (used version 9.0.0): `sudo npm install -g cordova`
- clone the git repository (`git clone https://github.com/dl9rdz/rdzwx-go.git`)
- `cd rdzwx-go; cordova platform add android`
- cordova plugin add cordova-plugin-androidx-adapter
- npm i jetifier
- npx jetifier
- `cordova build` to build debug apk
- `cordova build --release` to build releaes apk
- `cordova run android` to upload apk via usb to phone

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

