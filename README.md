# Mirsa simulator lab

This repository has no production integration. Only trusted owner dispatches run; no pull-request execution, signing credentials or production secrets. Each run gets an ephemeral GitHub macOS runner and a read-only checkout without persisted credentials. Native source/dylibs are untrusted executable code, not safely contained by an iOS simulator. Do not submit hostile code or introduce runner secrets. Network access is not blocked.

## Submit

On the default host run `/home/kit/bin/mirsa-lab /path/to/job`. The CLI waits, downloads artifacts into `job/lab-output`, and exits nonzero on failed UI tests or build failure. A failed compile is never a pass.

The job directory requires `job.json`, `checks.json`, and either `tweak.m` (plain Objective-C source compiled against UIKit/Foundation) or `tweak.dylib` (already compiled for the runner's iOS simulator architecture). Logos/Theos source and device-only binaries need a simulator-compatible source port first; dependencies are not inferred.

Example job.json is `{"target":"sample","publicUploadApproved":true}`. Job input is committed to a public branch, so review it for credentials, personal data, private app code and redistribution rights BEFORE approving. The 20 MiB job limit is deliberate. Do not include logs, .git, or unrelated files.

For a self-contained sample copy sample/tweak.m and sample/checks.json into a job directory. The bundled UIKit host explicitly dlopens the compiled dylib before showing its controller. The sample dynamically swizzles viewDidAppear to insert an actual button, open/close panel and gesture on a real visible label.

For a different open-source/authorized app use target `source` and provide `app-source/` containing the complete simulator-buildable Objective-C/Swift app sources and resources, with its own entry point. It must load bundled Tweak.dylib with dlopen itself; no bypass of encrypted apps is attempted. Existing Xcode projects, scripts, package dependencies and build hooks are intentionally not executed. Adapt the app first if needed.

checks.json maps five required strings: open, panel, close, gesture (accessibility identifiers), gestureValue (expected accessibility value after double tap). Tests require actual hittability, open, close, reopen/reset, and a visible gesture effect. Unsupported features must be tested on a device separately. Missing selectors/checks fail, not silently skip.

## Evidence

Artifact lab-results includes result.json, compiler/build/UI logs, Lab.xcresult, exported screenshots (where the installed xcresulttool supports attachment export), a final screenshot, simulator console and matching crash reports. Success requires real simulator XCTest completion. Report scope is explicitly simulator-only, not a real-device or real-target guarantee. A sample pass proves the lab, not TikTok compatibility.

Encrypted App Store apps such as TikTok cannot run here. Even unencrypted iPhone IPAs use device binaries and do not run in an iOS simulator. Supply authorized simulator app sources. This lab does not decrypt or download apps.

The report is evidence from potentially untrusted native execution, not a security attestation. Verify against protected workflow logs before relying on it. No production delivery/thread is changed.

## Android APK jobs

The same CLI detects exactly one root-level *.apk and dispatches android.yml on Ubuntu with required KVM and reactivecircus/android-emulator-runner. The iOS path is unchanged. APK jobs need job.json with publicUploadApproved:true; package and launch activity are read from the APK. API 29 x86_64 is currently fixed. ARM-only native APKs, split APK sets and apps requiring a newer API fail rather than silently pass.

The runner installs and launches the APK, checks its process and foreground activity, captures PNG screenshots and UI hierarchy XML, and checks fresh logcat crash/ANR evidence. This is an emulator smoke test, not an instrumentation suite or a complete feature guarantee. Network is not blocked. No production credentials are passed. Public upload approval also covers the APK and its redistribution rights.

Optional job.json steps are a list with actions such as {"action":"tap","x":100,"y":200}, {"action":"tapText","text":"Open menu"}, {"action":"assert","text":"Menu is open"}, {"action":"dump"} or {"action":"wait","seconds":2}. TapText resolves actual visible element bounds from UIAutomator. Exact text/content-description assertions fail when absent. Actions are allowlisted data, never shell commands; at most 40 steps. UI dump is always captured even with no custom steps.

Artifacts retain install/launch logs, complete logcat, crash buffer, foreground diagnostics, screenshots, UI dumps and result.json. Setup failure has a default fail JSON too. The self-contained Java sample under sample/android has no dependencies or permissions. Run build.sh with Android SDK build-tools 35 and platform 36 to make its debug-signed sample APK. Its debug keystore must never be used for real app distribution.
