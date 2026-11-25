Offline runtime translation experiment
======================================

Standalone arm64 iOS dylib with embedded UTF-8 JSON, no jailbreak framework and no runtime network. Inject MirsaTranslate.dylib into the original unencrypted Drift IPA and re-sign the app plus dylib. Removing the injected library and its load command restores the original UI behavior.

A reviewed per-app JSON named MirsaTranslations.json beside the dylib can override embedded translations, substrings and regex rules. For a single-file injection the embedded table is sufficient. The original IPA is not needed by the runtime.

Hooks UIKit setters, alert/action factories, attributed string construction, NSString drawing, CoreText line/typesetter/framesetter creation. SwiftUI coverage is best effort through those Foundation/CoreText boundaries, not a promise that every SwiftUI rendering path is intercepted. Unmatched text remains unchanged. No executable-code patching or entitlement bypass.

Translation is guarded against recursive entry, bounded by input length and a bounded NSCache. Invalid config/Objective-C exceptions fail open. This does NOT guarantee crash freedom, correct layout, universal SwiftUI coverage or device compatibility. No physical device test yet. Regex must be trusted and bounded, arbitrary regex can be slow. Arabic can require wider UI controls.

fishhook is vendored at upstream aadc161ac3b80db07a9908851839a17ba63a9eb1 under BSD license. The write-protection call is page-aligned and restricted to the pointer's page, and writes are skipped on failure. Fishhook may not cover modern chained-fixup-only images. No symbol-inline hooking. Existing hooks from other libraries may conflict.

Build on macOS with Xcode by running ./build.sh. The CI artifact contains the arm64 dylib, JSON and SHA256SUMS. Ad-hoc code signature must be replaced with the application's signing identity when injecting.
