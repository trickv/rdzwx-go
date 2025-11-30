# GitHub Actions CI/CD Workflows

This directory contains GitHub Actions workflows for automated testing, building, and quality assurance of the rdzwx-go Cordova application.

## 📋 Available Workflows

### 1. **Full CI Pipeline** (`ci-full.yml`)
**Triggers:** Push to main/master/develop, Pull Requests, Manual

Complete CI pipeline that runs all checks in sequence:
- ✅ Security & dependency scanning
- ✅ Android build test
- ✅ iOS build test (macOS)
- ✅ Summary report

**Use this for:** Production readiness checks, pre-merge validation

**Artifacts:**
- `android-apk-full-ci` - Debug APK (14 days)
- `ios-app-full-ci` - iOS simulator app (14 days)

---

### 2. **Android Build & Test** (`android-build.yml`)
**Triggers:** Push to main/develop/claude branches, Pull Requests, Manual

Comprehensive Android build workflow:
- Initializes git submodules (rdzwx-go, rdzwx-plugin)
- Sets up JDK 17 + Android SDK (API 35)
- Installs Cordova and dependencies
- Builds both debug and release APKs
- Runs Android lint analysis

**Artifacts:**
- `android-debug-apk` - Debug APK (30 days)
- `android-release-apk` - Unsigned release APK (30 days)
- `android-lint-report` - Lint analysis HTML (14 days)

**Environment:**
- JDK: 17 (Temurin)
- Node: 18
- Android SDK: API 35, Build Tools 35.0.0
- Cordova: Latest

---

### 3. **iOS Build & Test** (`ios-build.yml`)
**Triggers:** Push to main/develop/claude branches, Pull Requests, Manual

Complete iOS build workflow (requires macOS):
- Initializes git submodules
- Sets up Node.js + Xcode
- Installs Cordova and CocoaPods
- Builds for simulator (debug) and device (release)
- Runs Xcode static analysis

**Artifacts:**
- `ios-debug-app` - Simulator .app bundle + IPA (30 days)
- `ios-release-app` - Device .app bundle (30 days)

**Environment:**
- macOS: 14 (Sonoma)
- Xcode: 15.2
- Node: 18
- Cordova: Latest

---

### 4. **Security & Code Quality** (`security-and-quality.yml`)
**Triggers:** Push, Pull Requests, Weekly schedule (Mondays 9am UTC), Manual

Multi-job security and quality analysis:

#### **Job: dependency-security**
- NPM audit for main project and plugin
- Outdated dependency checks
- JSON audit reports

#### **Job: code-quality**
- JavaScript syntax validation
- Security pattern detection:
  - Console.log in production
  - eval() usage
  - innerHTML (XSS risk)
  - document.write
- XML syntax validation (config.xml, plugin.xml)

#### **Job: kotlin-quality**
- Kotlin file discovery
- TODO/FIXME comment tracking
- Deprecated code detection

#### **Job: ios-quality** (macOS)
- Objective-C file analysis
- Memory management checks (manual retain/release)
- Deprecated API detection (UIWebView, etc.)
- iOS platform compatibility checks

**Artifacts:**
- `npm-audit-reports` - JSON audit logs (30 days)

---

## 🚀 Usage

### Running Workflows Manually

1. Go to **Actions** tab in GitHub
2. Select desired workflow
3. Click **Run workflow** dropdown
4. Choose branch and click **Run workflow**

### Downloading Build Artifacts

1. Go to **Actions** tab
2. Click on a completed workflow run
3. Scroll to **Artifacts** section
4. Download desired artifact (APK, IPA, reports)

### CI Status Badges

Add to your README.md:

```markdown
![Android Build](https://github.com/trickv/rdz-claude/actions/workflows/android-build.yml/badge.svg)
![iOS Build](https://github.com/trickv/rdz-claude/actions/workflows/ios-build.yml/badge.svg)
![Security](https://github.com/trickv/rdz-claude/actions/workflows/security-and-quality.yml/badge.svg)
```

---

## 🔧 Configuration

### Required Secrets

No secrets required for basic builds. Optional:

- `ANDROID_KEYSTORE` - Base64 encoded keystore for signed releases
- `KEYSTORE_PASSWORD` - Keystore password
- `KEY_ALIAS` - Key alias
- `KEY_PASSWORD` - Key password

### Required Repository Settings

1. **Submodules:** Workflows automatically checkout submodules
2. **GITHUB_TOKEN:** Automatically provided by GitHub Actions
3. **Branch Protection:** Configure branch rules for main/master

### Workflow Permissions

Workflows need:
- **Read** access to repository contents
- **Write** access for uploading artifacts
- **Read** access to pull requests (for PR triggers)

---

## 📊 Understanding Results

### Success Criteria

- ✅ **Green checkmark:** All checks passed
- ⚠️ **Yellow icon:** Some non-critical checks failed
- ❌ **Red X:** Build failed or critical security issues

### Common Failure Scenarios

| Error | Workflow | Solution |
|-------|----------|----------|
| NPM audit fails | Security | Update vulnerable dependencies |
| Cordova build fails | Android/iOS | Check platform requirements |
| Submodule checkout fails | Any | Verify submodule URLs and access |
| SDK not found | Android | Update SDK version in workflow |
| Xcode version mismatch | iOS | Update macOS runner version |

---

## 🛠️ Development Tips

### Testing Workflow Changes

1. Create branch: `git checkout -b test/workflow-update`
2. Modify workflow file
3. Push: `git push origin test/workflow-update`
4. Workflow runs automatically
5. Check Actions tab for results

### Local Testing

Before pushing, test locally:

```bash
# Android build test
cd rdzwx-go
npm install
cordova platform add android
cordova plugin add ../rdzwx-plugin/
cordova build android

# Security checks
npm audit
grep -r "eval(" www/

# Syntax validation
find www -name "*.js" -exec node -c {} \;
```

### Debugging Failed Workflows

1. Check **workflow logs** in Actions tab
2. Look for **red error messages**
3. Verify **environment versions** match local setup
4. Check **submodule initialization** completed
5. Review **dependency installation** logs

---

## 📅 Maintenance Schedule

| Task | Frequency | Workflow |
|------|-----------|----------|
| Security scan | Weekly (Mon 9am) | security-and-quality.yml |
| Dependency updates | Monthly | Manual `npm update` |
| SDK version updates | Quarterly | Update workflow files |
| Workflow syntax check | Per commit | GitHub automatic validation |

---

## 🔗 Related Documentation

- [Cordova CLI Reference](https://cordova.apache.org/docs/en/latest/reference/cordova-cli/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Android SDK Setup](https://developer.android.com/studio)
- [Xcode Release Notes](https://developer.apple.com/documentation/xcode-release-notes)

---

## 🐛 Troubleshooting

### Workflow Not Triggering

**Check:**
1. Branch name matches trigger pattern
2. Workflow file is in `.github/workflows/`
3. YAML syntax is valid
4. Actions enabled in repository settings

### Submodule Issues

**Solutions:**
```yaml
# Ensure recursive checkout
- uses: actions/checkout@v4
  with:
    submodules: recursive
    token: ${{ secrets.GITHUB_TOKEN }}
```

### Build Artifacts Not Uploading

**Check:**
1. File paths exist after build
2. `if-no-files-found` setting
3. Artifact name is unique
4. Retention days within limits (1-90)

---

**Last Updated:** November 2025
**Maintained By:** Claude Code (automated CI/CD setup)
