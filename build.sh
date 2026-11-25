#!/bin/bash
set -euo pipefail
mkdir -p out
python3 - <<'PY'
from pathlib import Path
data=Path('runtime-table.json').read_bytes()
Path('Table.h').write_text('static const unsigned char runtime_table[] = {'+','.join(str(b) for b in data)+'};\nstatic const unsigned long runtime_table_len = sizeof(runtime_table);\n')
PY
SDK=$(xcrun --sdk iphoneos --show-sdk-path)
xcrun --sdk iphoneos clang -arch arm64 -isysroot "$SDK" -miphoneos-version-min=15.0 -fobjc-arc -fblocks -O2 -Wall -Wextra -Werror=implicit-function-declaration -dynamiclib RuntimeTranslate.m fishhook.c -framework UIKit -framework Foundation -framework CoreText -install_name @rpath/MirsaTranslate.dylib -o out/MirsaTranslate.dylib
codesign -s - --force out/MirsaTranslate.dylib
lipo -info out/MirsaTranslate.dylib
otool -L out/MirsaTranslate.dylib
codesign --verify --strict out/MirsaTranslate.dylib
cp runtime-table.json out/MirsaTranslations.json
shasum -a 256 out/* > out/SHA256SUMS
SIMSDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
ARCH=$(uname -m)
xcrun clang -target "$ARCH-apple-ios17.0-simulator" -isysroot "$SIMSDK" -fobjc-arc -fblocks -O1 -dynamiclib RuntimeTranslate.m fishhook.c -framework UIKit -framework Foundation -framework CoreText -o /tmp/MirsaTranslate-sim.dylib
xcrun clang -target "$ARCH-apple-ios17.0-simulator" -isysroot "$SIMSDK" -fobjc-arc -fblocks Smoke.m -framework UIKit -framework Foundation -framework CoreText -o /tmp/MirsaTranslate-smoke
DEVICE=$(xcrun simctl list devices available -j | python3 -c 'import json,sys;d=json.load(sys.stdin);print(next(x["udid"] for group in d["devices"].values() for x in group if "iPhone" in x["name"]))')
xcrun simctl boot "$DEVICE" || true
xcrun simctl bootstatus "$DEVICE" -b
xcrun simctl spawn "$DEVICE" /tmp/MirsaTranslate-smoke /tmp/MirsaTranslate-sim.dylib
