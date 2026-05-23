# CI/CD Setup Summary

This document describes the automated testing and build infrastructure added to the rdz-claude project.

## 📦 What Was Added

### GitHub Actions Workflows (`.github/workflows/`)

Four comprehensive workflows have been created:

1. **`ci-full.yml`** - Complete CI pipeline
   - Runs security scans first
   - Builds Android APK (Ubuntu)
   - Builds iOS app (macOS)
   - Provides summary report
   - **Produces build artifacts** for both platforms

2. **`android-build.yml`** - Android-specific builds
   - Full Android SDK setup (API 35)
   - Debug and release APK builds
   - Android lint analysis
   - **Produces APK artifacts** (30-day retention)

3. **`ios-build.yml`** - iOS-specific builds
   - Runs on macOS with Xcode 15.2
   - Simulator and device builds
   - Static analysis with Xcode
   - **Produces .app/.ipa artifacts** (30-day retention)

4. **`security-and-quality.yml`** - Security & code quality
   - NPM dependency audits
   - JavaScript syntax validation
   - Security pattern detection (eval, XSS risks)
   - Kotlin code quality checks
   - Objective-C code analysis
   - Weekly automated scans (Mondays 9am UTC)

## 🎯 Key Features

### ✅ Build Testing
- Initializes git submodules automatically
- Tests both Android and iOS platforms
- Verifies all dependencies install correctly
- Confirms Cordova build process works

### ✅ Security Scanning
- NPM audit for vulnerable dependencies
- Pattern detection for unsafe code (eval, innerHTML, etc.)
- Weekly scheduled security scans
- Blocks high-severity vulnerabilities in full CI

### ✅ Code Quality
- JavaScript syntax validation
- XML config validation
- Kotlin and Objective-C code checks
- TODO/FIXME tracking
- Deprecated API detection

### ✅ Build Artifacts
**Android:**
- Debug APK (ready to install)
- Release APK (unsigned)
- Lint reports (HTML)

**iOS:**
- Simulator .app bundle
- Debug IPA (for distribution)
- Device .app bundle (unsigned)

## 🚀 How to Use

### Automatic Triggers

Workflows run automatically on:
- **Push** to main, master, develop, or claude/* branches
- **Pull requests** targeting main/master/develop
- **Weekly schedule** (security scan only)

### Manual Triggers

1. Go to GitHub Actions tab
2. Select workflow
3. Click "Run workflow"
4. Choose branch and run

### Downloading Builds

After workflow completes:
1. Open the workflow run
2. Scroll to "Artifacts" section
3. Download APK or iOS app
4. Install on device/simulator

## 📋 Workflow Status

Add these badges to your README:

```markdown
![Android Build](https://github.com/trickv/rdz-claude/actions/workflows/android-build.yml/badge.svg)
![iOS Build](https://github.com/trickv/rdz-claude/actions/workflows/ios-build.yml/badge.svg)
![Security](https://github.com/trickv/rdz-claude/actions/workflows/security-and-quality.yml/badge.svg)
![CI](https://github.com/trickv/rdz-claude/actions/workflows/ci-full.yml/badge.svg)
```

## 🔧 Configuration Details

### Submodule Handling

All workflows automatically:
```yaml
- uses: actions/checkout@v4
  with:
    submodules: recursive  # Initializes rdzwx-go and rdzwx-plugin
```

### Platform Versions

**Android Environment:**
- Ubuntu Latest
- JDK 17 (Temurin)
- Node.js 18
- Android SDK API 35
- Build Tools 35.0.0
- Kotlin 1.8.22+

**iOS Environment:**
- macOS 14 (Sonoma)
- Xcode 15.2
- Node.js 18
- CocoaPods (latest)

### Build Commands Used

**Android:**
```bash
cordova platform add android
cordova plugin add plugin-src/rdzwx-plugin/
cordova build android --debug
cordova build android --release
```

**iOS:**
```bash
cordova platform add ios
cordova plugin add plugin-src/rdzwx-plugin/
cordova build ios --emulator
cordova build ios --device --release
```

## 🛡️ Security Features

### Dependency Audits
- Runs `npm audit` on main project and plugin
- Fails CI if high-severity vulnerabilities found
- Generates JSON reports for review

### Code Pattern Detection
- **Blocks:** eval() usage (code injection risk)
- **Warns:** innerHTML usage (XSS risk)
- **Tracks:** console.log (production code cleanup)
- **Detects:** document.write (deprecated practice)

### iOS-Specific Checks
- UIWebView detection (deprecated by Apple)
- Manual memory management (ARC violations)
- Deprecated API usage

## 📊 Expected Results

### First Run
On first workflow execution:
1. ✅ Submodules clone successfully
2. ✅ Dependencies install
3. ✅ Android APK builds (debug)
4. ✅ iOS app builds (simulator)
5. ⚠️ Some quality warnings expected (TODOs, etc.)
6. ✅ Artifacts uploaded successfully

### Artifact Sizes
- **Android Debug APK:** ~10-50 MB
- **Android Release APK:** ~8-40 MB (unsigned)
- **iOS Simulator App:** ~15-60 MB
- **iOS IPA:** ~20-70 MB

## 🐛 Troubleshooting

### Common Issues

**Submodule Access:**
- Workflows use GITHUB_TOKEN for private repos
- Ensure submodules are accessible to Actions

**Build Failures:**
- Check logs in Actions tab
- Verify SDK versions match local setup
- Confirm config.xml is valid

**Artifact Upload:**
- Check file paths after build
- Verify artifacts exist before upload
- Review retention settings

### Testing Locally

Before relying on CI, test locally:

```bash
# Clone with submodules
git clone --recursive <repo-url>

# Or initialize after clone
git submodule update --init --recursive

# Test Android build
cd rdzwx-go
npm install
cordova platform add android
cordova plugin add plugin-src/rdzwx-plugin/
cordova build android

# Test iOS build (macOS only)
cordova platform add ios
cordova build ios
```

## 📚 Documentation

See `.github/workflows/README.md` for:
- Detailed workflow descriptions
- Configuration options
- Advanced usage
- Maintenance schedule

## 🏪 Store Releases (optional, per-fork)

The `release.yml` workflow includes two **optional** jobs that publish to the
App Store (TestFlight) and Google Play (internal track). They are gated on
the presence of fork-specific secrets and **skip silently on any fork that
hasn't configured them** — including upstream. The pre-existing
unsigned-IPA-for-AltStore job always runs and is unaffected.

The jobs are driven by [Fastlane](https://fastlane.tools/). See `fastlane/Fastfile`
for the lane definitions; both lanes consume env vars only — no fork-specific
values are committed to the repo.

### Enabling the iOS App Store job

Set **all** of these repo secrets. Missing any one of them will cause the
job to fail mid-run; the gating secret is `IOS_BUNDLE_ID`.

| Secret | Description |
| --- | --- |
| `IOS_BUNDLE_ID` | Your App Store bundle identifier (e.g. `com.example.rdzwx`). Gates the job. |
| `FASTLANE_APPLE_ID` | Apple ID email associated with your developer account. |
| `APPLE_TEAM_ID` | 10-character Team ID from your Apple Developer account. |
| `APPLE_CODE_SIGN_IDENTITY` | Code signing identity name. Defaults to `Apple Distribution`. |
| `APPLE_PROVISIONING_PROFILE_NAME` | Exact name of the App Store provisioning profile. |
| `BUILD_CERTIFICATE_BASE64` | Distribution `.p12` certificate, base64-encoded. |
| `P12_PASSWORD` | Password for the `.p12` certificate. |
| `KEYCHAIN_PASSWORD` | Arbitrary password for the ephemeral CI keychain. |
| `BUILD_PROVISION_PROFILE_BASE64` | Provisioning profile `.mobileprovision`, base64-encoded. |
| `ASC_API_KEY_BASE64` | App Store Connect API key (`.p8`), base64-encoded. |
| `ASC_API_KEY_ID` | App Store Connect API key ID. |
| `ASC_API_ISSUER_ID` | App Store Connect API issuer ID. |

To base64-encode a file on macOS/Linux: `base64 -i certificate.p12 | tr -d '\n'`.

### Enabling the Android Play Store job

| Secret | Description |
| --- | --- |
| `ANDROID_PACKAGE_NAME` | Your Play Store package name (e.g. `com.example.rdzwx`). Gates the job. |
| `ANDROID_KEYSTORE_BASE64` | Upload keystore (`.jks`), base64-encoded. |
| `ANDROID_KEYSTORE_PASSWORD` | Keystore password. |
| `ANDROID_KEY_ALIAS` | Key alias inside the keystore. |
| `ANDROID_KEY_PASSWORD` | Password for the key (often same as keystore password). |
| `GOOGLE_PLAY_JSON_KEY_BASE64` | Google Play service-account JSON, base64-encoded. |

### One-time setup prerequisites (manual)

- **Apple:** register the App ID, create the App Store Connect app record,
  generate a distribution certificate + App Store provisioning profile, and
  generate an App Store Connect API key.
- **Google:** create the Play Console app record with your chosen package
  name. Manually upload the first AAB via the Play Console UI — the Play
  Developer API rejects the very first upload, so Fastlane can only take
  over from the second release onward. Create a service account in Google
  Cloud, grant it release permissions in Play Console, and download its JSON
  key.
- Both stores require a privacy policy URL; this repo does not currently
  ship one.

### Local Fastlane usage

```bash
bundle install
# Export the same env vars listed above, then:
bundle exec fastlane android beta   # local AAB → Play Store internal
bundle exec fastlane ios beta       # local IPA → TestFlight (macOS only)
```

The legacy local Android release flow (`make release`, using the
GPG-encrypted `my-release-key.jks.gpg`) is unchanged and still works.

## ✨ Future Enhancements

Possible additions:
- [x] Automated release signing (with keystore secrets)
- [x] App Store Connect uploads (iOS)
- [x] Google Play uploads (Android)
- [ ] E2E testing with Appium
- [ ] Code coverage reports
- [ ] Performance benchmarks
- [ ] Automated changelog generation

---

**Created:** November 2025
**Tools Used:** GitHub Actions, Cordova CLI, Android SDK, Xcode
**Platforms:** Android (API 35), iOS (15.2+)
